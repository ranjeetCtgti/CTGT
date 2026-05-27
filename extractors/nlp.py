from __future__ import annotations

import json
import os
import time
from collections import Counter
from dataclasses import dataclass
from difflib import SequenceMatcher
from json import JSONDecodeError
from typing import Any, Iterable, Protocol

import httpx
from loguru import logger
from tenacity import retry, retry_if_exception, stop_after_attempt, wait_exponential

from config import (
    ALLOWED_SOFTWARE_NAMES,
    DEFAULT_BATCH_SIZE,
    DEFAULT_REQUEST_TIMEOUT_SECONDS,
    EXCLUDED_COMPANIES,
    EXPANSION_SIGNAL_BONUS_MAX,
    EXPANSION_SIGNAL_BONUS_PER_MATCH,
    GEMINI_API_URL,
    INDUSTRY_CHOICES,
    MIGRATION_BONUS,
    MIN_CONFIDENCE,
    PAIN_SIGNAL_BONUS_MAX,
    PAIN_SIGNAL_BONUS_PER_MATCH,
    SIGNAL_TYPE_BASE_SCORE,
    SOFTWARE_CANONICAL_TO_DISPLAY,
    SOFTWARE_DISPLAY_TO_CANONICAL,
    SOFTWARE_SCORE,
)
from extractors.prefilter import PrefilterResult, keyword_prefilter
from models.schema import ExtractedSignal, RawJobPosting, SignalSource, SignalType

DEFAULT_LLM_REQUESTS_PER_MINUTE = 25
PLACEHOLDER_COMPANY_NAMES = {"unknown", "n/a", "none", "null"}
CONSULTING_NAME_TERMS = (
    "consulting",
    "consultancy",
    "system integrator",
    "systems integrator",
    "managed services",
    "professional services",
)
CONSULTING_SOURCE_TERMS = (
    "it services and it consulting",
    "business consulting and services",
    "engineering services company",
    "digital transformation consulting",
    "professional services company",
    "managed services provider",
    "global consulting firm",
    "consulting services",
    "technology consulting",
    "staffing and recruiting",
    "outsourcing services",
)


class GeminiClientError(Exception):
    """Raised when Gemini extraction fails irrecoverably."""


class GroqClientError(Exception):
    """Raised when Groq extraction fails irrecoverably."""


@dataclass
class ExtractionCandidate:
    source_url: str
    source_title: str
    source_text: str
    signal_source: SignalSource
    signal_type: SignalType
    query: str
    title: str
    snippet: str | None = None
    description: str | None = None
    company_hint: str | None = None
    location_hint: str | None = None
    prefilter: PrefilterResult | None = None


def _is_retryable_gemini_error(exc: Exception) -> bool:
    if isinstance(exc, (httpx.TimeoutException, httpx.TransportError)):
        return True
    if isinstance(exc, GeminiClientError):
        message = str(exc)
        if "429" in message:
            return True
        if any(f"status={status}" in message for status in (500, 502, 503, 504)):
            return True
        if any(status in message for status in ('"status": "INTERNAL"', '"status": "UNAVAILABLE"')):
            return True
    if isinstance(exc, httpx.HTTPStatusError):
        return exc.response.status_code == 429 or 500 <= exc.response.status_code < 600
    return False


def _is_retryable_groq_error(exc: Exception) -> bool:
    if isinstance(exc, GroqClientError):
        message = str(exc)
        if "429" in message:
            return True
        if any(f"status={status}" in message for status in (500, 502, 503, 504)):
            return True
    if isinstance(exc, (httpx.TimeoutException, httpx.TransportError)):
        return True
    if isinstance(exc, httpx.HTTPStatusError):
        return exc.response.status_code == 429 or 500 <= exc.response.status_code < 600
    return False


class Extractor(Protocol):
    def close(self) -> None: ...
    def __enter__(self) -> "Extractor": ...
    def __exit__(self, exc_type: Any, exc: Any, tb: Any) -> None: ...
    def extract_signals(
        self,
        candidates: list[ExtractionCandidate],
        processed_source_urls: set[str] | None = None,
        recently_processed_companies: set[str] | None = None,
    ) -> list[ExtractedSignal]: ...
    def from_job_postings(self, postings: list[RawJobPosting]) -> list[ExtractionCandidate]: ...


class BaseExtractor:
    def __enter__(self) -> "BaseExtractor":
        return self

    def __exit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
        self.close()

    def from_job_postings(self, postings: list[RawJobPosting]) -> list[ExtractionCandidate]:
        return [candidate_from_job_posting(posting) for posting in postings]

    def extract_signals(
        self,
        candidates: list[ExtractionCandidate],
        processed_source_urls: set[str] | None = None,
        recently_processed_companies: set[str] | None = None,
    ) -> list[ExtractedSignal]:
        deduped_candidates = self._filter_candidates(
            candidates,
            processed_source_urls=processed_source_urls or set(),
            recently_processed_companies=recently_processed_companies or set(),
        )
        if self.debug and not deduped_candidates:
            logger.info("extraction skipped because no candidates survived internal filtering")
        signals: list[ExtractedSignal] = []
        decision_counts: Counter[str] = Counter()
        debug_log_limit = 20
        debug_logged = 0

        for batch in _chunked(deduped_candidates, self.batch_size):
            extracted_pairs = self._extract_batch(batch)
            for candidate, raw_item in extracted_pairs:
                signal, decision = self._post_process_item(candidate, raw_item)
                decision_counts[decision] += 1
                if self.debug and debug_logged < debug_log_limit:
                    logger.info(
                        "model decision source={} company_hint={!r} detected_company={!r} software_raw={} confidence={} decision={} reasoning={!r}",
                        candidate.signal_source,
                        candidate.company_hint,
                        raw_item.get("company_name"),
                        raw_item.get("software_detected"),
                        raw_item.get("confidence"),
                        decision,
                        raw_item.get("reasoning"),
                    )
                    debug_logged += 1
                if signal:
                    signals.append(signal)

        if self.debug:
            logger.info("extraction summary decisions={}", dict(decision_counts))
        return signals

    def _filter_candidates(
        self,
        candidates: list[ExtractionCandidate],
        processed_source_urls: set[str],
        recently_processed_companies: set[str],
    ) -> list[ExtractionCandidate]:
        filtered: list[ExtractionCandidate] = []
        for candidate in candidates:
            if candidate.source_url in processed_source_urls:
                continue
            normalized_company_hint = _normalize_company_hint(candidate.company_hint)
            if normalized_company_hint and _recent_company_match(
                normalized_company_hint, recently_processed_companies
            ):
                continue
            prefilter = candidate.prefilter or keyword_prefilter(candidate.source_text)
            if not prefilter.passed:
                continue
            candidate.prefilter = prefilter
            filtered.append(candidate)
        return filtered

    def _extract_batch(
        self,
        batch: list[ExtractionCandidate],
    ) -> list[tuple[ExtractionCandidate, dict[str, Any]]]:
        try:
            self._throttle_model_request()
            raw_items = self._request_batch_items(batch)
            return self._pair_batch_items(batch, raw_items)
        except Exception as exc:
            logger.error(
                "model batch failed size={} source_urls={} error={}",
                len(batch),
                [candidate.source_url for candidate in batch],
                str(exc),
            )
            return []

    def _throttle_model_request(self) -> None:
        rpm_cap = _load_llm_requests_per_minute()
        min_interval_seconds = 60.0 / rpm_cap
        last_request_started_at = getattr(self, "_last_llm_request_started_at", 0.0)
        elapsed = time.monotonic() - last_request_started_at
        remaining = min_interval_seconds - elapsed
        if remaining > 0:
            logger.info(
                "llm throttle provider={} wait_seconds={:.2f} rpm_cap={}",
                self.__class__.__name__,
                remaining,
                rpm_cap,
            )
            time.sleep(remaining)
        self._last_llm_request_started_at = time.monotonic()

    def _request_batch_items(self, batch: list[ExtractionCandidate]) -> list[dict[str, Any]]:
        response_text = self._generate_batch_text(batch)
        raw_items = self._extract_response_items(response_text)
        if len(batch) == 1 and len(raw_items) == 0:
            logger.warning(
                "model returned no usable JSON objects for single-item batch first_try source_url={} raw_preview={!r}",
                batch[0].source_url,
                _preview_text(response_text),
            )
            response_text = self._generate_batch_text(batch, single_item_retry=True)
            raw_items = self._extract_response_items(response_text)
        if len(raw_items) != len(batch):
            logger.warning(
                "model response count mismatch first_try expected={} actual={} retrying_once raw_preview={!r}",
                len(batch),
                len(raw_items),
                _preview_text(response_text),
            )
            response_text = self._generate_batch_text(batch)
            raw_items = self._extract_response_items(response_text)
        self._validate_batch_size(batch, raw_items)
        return raw_items

    def _pair_batch_items(
        self,
        batch: list[ExtractionCandidate],
        raw_items: list[dict[str, Any]],
    ) -> list[tuple[ExtractionCandidate, dict[str, Any]]]:
        if len(raw_items) == len(batch):
            return list(zip(batch, raw_items))

        indexed_items: dict[int, dict[str, Any]] = {}
        for raw_item in raw_items:
            raw_id = raw_item.get("id")
            if not isinstance(raw_id, int):
                continue
            if 1 <= raw_id <= len(batch) and raw_id not in indexed_items:
                indexed_items[raw_id] = raw_item

        if not indexed_items:
            raise GeminiClientError(
                f"Model response count mismatch expected={len(batch)} actual={len(raw_items)} with no usable item ids"
            )

        missing_ids = [index for index in range(1, len(batch) + 1) if index not in indexed_items]
        if missing_ids:
            logger.warning(
                "model batch returned partial results expected={} actual={} missing_ids={}",
                len(batch),
                len(indexed_items),
                missing_ids,
            )

        return [(batch[index - 1], indexed_items[index]) for index in sorted(indexed_items)]

    def _extract_response_items(self, text: str) -> list[dict[str, Any]]:
        if not text:
            raise GeminiClientError("Model returned empty content text")
        cleaned = _strip_json_fences(text)
        if not cleaned.strip():
            raise GeminiClientError("Model returned empty content text")
        try:
            parsed = json.loads(cleaned)
        except JSONDecodeError as exc:
            if _looks_like_prompt_echo(cleaned):
                return []
            extracted_array = _extract_first_json_array(cleaned)
            if extracted_array:
                try:
                    parsed = json.loads(extracted_array)
                except JSONDecodeError:
                    preview = cleaned[:400].replace("\n", " ")
                    raise GeminiClientError(
                        f"Model returned invalid JSON payload preview={preview!r}"
                    ) from exc
            else:
                preview = cleaned[:400].replace("\n", " ")
                raise GeminiClientError(
                    f"Model returned invalid JSON payload preview={preview!r}"
                ) from exc
        if isinstance(parsed, dict):
            wrapped_items = parsed.get("items")
            if isinstance(wrapped_items, list):
                parsed = wrapped_items
            else:
                parsed = [parsed]
        if not isinstance(parsed, list):
            raise GeminiClientError("Model response was not a JSON list")
        return [item for item in parsed if isinstance(item, dict)]

    def _post_process_item(
        self,
        candidate: ExtractionCandidate,
        raw_item: dict[str, Any],
    ) -> tuple[ExtractedSignal | None, str]:
        company_name = str(raw_item.get("company_name") or candidate.company_hint or "").strip()
        if (
            not company_name
            or company_name.lower() in EXCLUDED_COMPANIES
            or company_name.lower() in PLACEHOLDER_COMPANY_NAMES
        ):
            return None, "excluded_or_missing_company"
        if _is_consulting_company(company_name, candidate.source_text):
            return None, "consulting_company"

        software = _normalize_software(raw_item.get("software_detected", []))
        if not software:
            return None, "no_allowed_software"

        confidence = _coerce_float(raw_item.get("confidence"))
        if confidence < MIN_CONFIDENCE:
            return None, "low_confidence"

        pain_signals = _filter_string_list(raw_item.get("pain_signals"))
        expansion_signals = _filter_string_list(raw_item.get("expansion_signals"))
        migration = bool(raw_item.get("migration_detected"))
        migration_from = _normalize_optional_string(raw_item.get("migration_from"))
        industry = _normalize_industry(raw_item.get("industry"))

        signal = ExtractedSignal(
            company_name=company_name,
            company_domain=None,
            location=_normalize_optional_string(raw_item.get("location")) or candidate.location_hint,
            industry=industry,
            software=software,
            signal_type=candidate.signal_type,
            signal_source=candidate.signal_source,
            migration=migration,
            migration_from=migration_from,
            pain_signals=pain_signals,
            expansion_signals=expansion_signals,
            raw_score=0,
            confidence=confidence,
            reason=_normalize_optional_string(raw_item.get("reasoning")),
            source_url=candidate.source_url,
            source_title=candidate.source_title,
        )
        signal.raw_score = compute_raw_score(signal)
        return signal, "accepted"

    def _validate_batch_size(
        self,
        batch: list[ExtractionCandidate],
        raw_items: list[dict[str, Any]],
    ) -> None:
        if len(raw_items) == len(batch):
            return

        valid_ids = {
            raw_item.get("id")
            for raw_item in raw_items
            if isinstance(raw_item, dict) and isinstance(raw_item.get("id"), int) and 1 <= raw_item["id"] <= len(batch)
        }
        if valid_ids:
            return

        if len(raw_items) != len(batch):
            raise GeminiClientError(
                f"Model response count mismatch expected={len(batch)} actual={len(raw_items)}"
            )


class GeminiExtractor(BaseExtractor):
    def __init__(
        self,
        api_key: str | None = None,
        timeout_seconds: int = DEFAULT_REQUEST_TIMEOUT_SECONDS,
        batch_size: int = DEFAULT_BATCH_SIZE,
        debug: bool = False,
    ) -> None:
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise GeminiClientError("GEMINI_API_KEY is missing")
        self.batch_size = batch_size
        self.debug = debug
        self._http = httpx.Client(timeout=timeout_seconds)
        self.timeout_seconds = timeout_seconds

    def close(self) -> None:
        self._http.close()

    def _build_payload(
        self,
        batch: list[ExtractionCandidate],
        single_item_retry: bool = False,
    ) -> dict[str, Any]:
        prompt = _build_prompt(batch, single_item_retry=single_item_retry)
        return {
            "contents": [
                {
                    "parts": [{"text": prompt}]
                }
            ],
            # FIX: removed "responseJsonSchema" — that field is only supported
            # by the Google Gen AI SDK, not the REST API. Sending it causes
            # 400 INVALID_ARGUMENT on every request.
            # FIX: removed "responseMimeType": "application/json" — this
            # triggers strict structured-output mode which caused 500 INTERNAL
            # errors when Gemini couldn't satisfy the schema constraints on
            # certain job posting content. We instruct JSON output via the
            # prompt instead, which is more robust.
            "generationConfig": {
                "temperature": 0.1,
                "maxOutputTokens": 2048,
            },
        }

    @retry(
        retry=retry_if_exception(_is_retryable_gemini_error),
        wait=wait_exponential(multiplier=1, min=5, max=45),
        stop=stop_after_attempt(3),
        reraise=True,
    )
    def _call_gemini(self, payload: dict[str, Any]) -> dict[str, Any]:
        response = self._http.post(
            GEMINI_API_URL,
            params={"key": self.api_key},
            json=payload,
        )
        if response.status_code == 429:
            raise GeminiClientError("Gemini rate limited (429)")
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            body_preview = response.text[:800].replace("\n", " ")
            raise GeminiClientError(
                f"Gemini HTTP error status={response.status_code} body_preview={body_preview!r}"
            ) from exc
        try:
            return response.json()
        except JSONDecodeError as exc:
            body_preview = response.text[:400].replace("\n", " ")
            raise GeminiClientError(
                f"Gemini returned non-JSON response status={response.status_code} body_preview={body_preview!r}"
            ) from exc

    def _extract_response_text(self, response_json: dict[str, Any]) -> str:
        candidates = response_json.get("candidates") or []
        if not candidates:
            return ""
        parts = candidates[0].get("content", {}).get("parts", [])
        if not parts:
            return ""
        return "".join(part.get("text", "") for part in parts)

    def _generate_batch_text(
        self,
        batch: list[ExtractionCandidate],
        single_item_retry: bool = False,
    ) -> str:
        payload = self._build_payload(batch, single_item_retry=single_item_retry)
        response_json = self._call_gemini(payload)
        text = self._extract_response_text(response_json)
        if not text:
            candidates = response_json.get("candidates") or []
            if not candidates:
                raise GeminiClientError("Gemini returned no candidates")
            raise GeminiClientError("Gemini returned no content parts")
        return text


class GroqExtractor(BaseExtractor):
    def __init__(
        self,
        api_key: str | None = None,
        model_id: str | None = None,
        timeout_seconds: int = DEFAULT_REQUEST_TIMEOUT_SECONDS,
        batch_size: int = DEFAULT_BATCH_SIZE,
        debug: bool = False,
    ) -> None:
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise GroqClientError("GROQ_API_KEY is missing")
        self.model_id = model_id or os.getenv("GROQ_MODEL_ID") or "qwen/qwen3-32b"
        self.batch_size = batch_size
        self.debug = debug
        self.timeout_seconds = timeout_seconds
        self._http = httpx.Client(
            timeout=timeout_seconds,
            base_url="https://api.groq.com/openai/v1",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
        )

    def close(self) -> None:
        self._http.close()

    @retry(
        retry=retry_if_exception(_is_retryable_groq_error),
        wait=wait_exponential(multiplier=1, min=5, max=45),
        stop=stop_after_attempt(3),
        reraise=True,
    )
    def _call_groq_chat(
        self,
        messages: list[dict[str, str]],
    ) -> dict[str, Any]:
        payload = {
            "model": self.model_id,
            "messages": messages,
            "temperature": 0.1,
            "max_completion_tokens": 2048,
            "response_format": {"type": "json_object"},
        }
        if self.model_id.startswith("qwen/"):
            payload["reasoning_format"] = "hidden"
        response = self._http.post("/chat/completions", json=payload)
        if response.status_code == 429:
            raise GroqClientError("Groq rate limited (429)")
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            body_preview = response.text[:800].replace("\n", " ")
            raise GroqClientError(
                f"Groq HTTP error status={response.status_code} body_preview={body_preview!r}"
            ) from exc
        try:
            return response.json()
        except JSONDecodeError as exc:
            body_preview = response.text[:400].replace("\n", " ")
            raise GroqClientError(
                f"Groq returned non-JSON response status={response.status_code} body_preview={body_preview!r}"
            ) from exc

    def _generate_batch_text(
        self,
        batch: list[ExtractionCandidate],
        single_item_retry: bool = False,
    ) -> str:
        prompt = _build_prompt(batch, single_item_retry=single_item_retry, json_object_mode=True)
        try:
            response_json = self._call_groq_chat(
                [
                    {"role": "system", "content": "You are a precise information extraction model."},
                    {"role": "user", "content": prompt},
                ]
            )
        except GroqClientError as exc:
            if "429" not in str(exc) or not os.getenv("GEMINI_API_KEY"):
                raise
            logger.warning(
                "groq rate limited after retries; falling back to Gemini for batch size={}",
                len(batch),
            )
            with GeminiExtractor(
                timeout_seconds=self.timeout_seconds,
                batch_size=self.batch_size,
                debug=self.debug,
            ) as fallback_extractor:
                return fallback_extractor._generate_batch_text(
                    batch,
                    single_item_retry=single_item_retry,
                )
        try:
            content = response_json["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise GroqClientError(f"Unexpected Groq response shape: {response_json!r}") from exc
        if not isinstance(content, str) or not content.strip():
            raise GroqClientError("Groq returned empty content")
        return content


def candidate_from_job_posting(posting: RawJobPosting) -> ExtractionCandidate:
    body = posting.description or posting.snippet or ""
    source_text = " | ".join(
        value for value in [posting.query, posting.title, posting.company_name, posting.location, body] if value
    )
    prefilter = keyword_prefilter(source_text)
    return ExtractionCandidate(
        source_url=str(posting.job_url),
        source_title=posting.title,
        source_text=source_text,
        signal_source=posting.source,
        signal_type=posting.signal_type,
        query=posting.query,
        title=posting.title,
        snippet=posting.snippet,
        description=posting.description,
        company_hint=posting.company_name,
        location_hint=posting.location,
        prefilter=prefilter,
    )


def build_extractor(
    batch_size: int,
    debug: bool = False,
) -> Extractor:
    provider = (os.getenv("LLM_PROVIDER") or "gemini").strip().lower()
    if provider == "groq":
        return GroqExtractor(batch_size=batch_size, debug=debug)
    return GeminiExtractor(batch_size=batch_size, debug=debug)


def compute_raw_score(signal: ExtractedSignal) -> int:
    score = SIGNAL_TYPE_BASE_SCORE[signal.signal_type]
    score += sum(SOFTWARE_SCORE.get(software.lower(), 0) for software in signal.software)
    if signal.migration:
        score += MIGRATION_BONUS
    score += min(PAIN_SIGNAL_BONUS_MAX, len(signal.pain_signals) * PAIN_SIGNAL_BONUS_PER_MATCH)
    score += min(
        EXPANSION_SIGNAL_BONUS_MAX,
        len(signal.expansion_signals) * EXPANSION_SIGNAL_BONUS_PER_MATCH,
    )
    return score


def _build_prompt(
    batch: list[ExtractionCandidate],
    single_item_retry: bool = False,
    json_object_mode: bool = False,
) -> str:
    items = []
    for index, candidate in enumerate(batch, start=1):
        snippet = _sanitise_text(candidate.snippet) if candidate.snippet else None
        description = _sanitise_text(candidate.description) if candidate.description else None
        fallback_text = None
        if not snippet and not description:
            fallback_text = _sanitise_text(candidate.source_text)
        items.append(
            {
                "id": index,
                "signal_type": candidate.signal_type,
                "query": candidate.query,
                "title": candidate.title,
                "company_hint": candidate.company_hint,
                "location_hint": candidate.location_hint,
                "signal_source": candidate.signal_source,
                "source_title": candidate.source_title,
                "prefilter_products": _software_from_prefilter(candidate.prefilter),
                "prefilter_context": _sanitise_text(candidate.prefilter.relevant_context, max_chars=1200)
                if candidate.prefilter and candidate.prefilter.relevant_context
                else None,
                # Avoid sending the same article/job text multiple times.
                "snippet": snippet,
                "description": description,
                "text": fallback_text,
            }
        )

    if single_item_retry and len(batch) == 1:
        output_prefix = '{"items":' if json_object_mode else ""
        output_suffix = "}" if json_object_mode else ""
        return (
            "Return only valid JSON. No prose. No bullets. No markdown. No schema echo.\n"
            f"Allowed industry values: {', '.join(INDUSTRY_CHOICES)}.\n"
            f"Allowed software_detected values: {', '.join(sorted(ALLOWED_SOFTWARE_NAMES))}.\n"
            "Use the structured fields first: query, title, company_hint, location_hint, snippet, and description.\n"
            "Use prefilter_products as deterministic keyword hits and prefilter_context as the most relevant local context.\n"
            "Use text only as a fallback combined view of the same source item.\n"
            "The company_name must refer to the source company in the input item, never CTGT Innovations unless the input explicitly says that.\n"
            "If Siemens PLM evidence is weak, return empty software_detected and low confidence instead of explanation text.\n"
            "Required output format:\n"
            f'{output_prefix}[{{"id":1,"company_name":"string","location":"string or null","industry":"string","software_detected":["allowed values only"],'
            '"migration_detected":true,"migration_from":"string or null","pain_signals":["phrases"],'
            f'"expansion_signals":["phrases"],"confidence":0.0,"reasoning":"one sentence"}}]{output_suffix}\n'
            f"Input item:\n{json.dumps(items[0], ensure_ascii=True)}"
        )

    output_contract = (
        '{"items":[{"id":1,"company_name":"string","location":"string or null","industry":"string",'
        '"software_detected":["allowed values only"],"migration_detected":true,"migration_from":"string or null",'
        '"pain_signals":["phrases"],"expansion_signals":["phrases"],"confidence":0.0,"reasoning":"one sentence"}]}'
        if json_object_mode
        else
        '[{"id":1,"company_name":"string","location":"string or null","industry":"string","software_detected":["allowed values only"],'
        '"migration_detected":true,"migration_from":"string or null","pain_signals":["phrases"],'
        '"expansion_signals":["phrases"],"confidence":0.0,"reasoning":"one sentence"}]'
    )
    output_rule = (
        'Return only valid JSON as one object with a top-level "items" array containing exactly one object per input item in the same order.\n'
        if json_object_mode
        else
        "Return only valid JSON as an array with exactly one object per input item in the same order.\n"
    )

    return (
        "You extract Siemens PLM lead signals from source items.\n"
        f"{output_rule}"
        "Do not include markdown, commentary, bullets, prompt restatement, or extra keys.\n"
        f"Allowed industry values: {', '.join(INDUSTRY_CHOICES)}.\n"
        f"Allowed software_detected values: {', '.join(sorted(ALLOWED_SOFTWARE_NAMES))}.\n"
        "Use the structured fields first: query, title, company_hint, location_hint, snippet, and description.\n"
        "Use prefilter_products as deterministic keyword hits and prefilter_context as the most relevant local context.\n"
        "Use text only as a fallback combined view of the same source item.\n"
        "Each output object must include the matching input id.\n"
        "The company_name must refer to the source company in that input item, never CTGT Innovations unless the input explicitly says that.\n"
        "Watch for migration signals such as Windchill, Enovia, CATIA, Autodesk Vault, SAP PLM, or legacy PDM replacements.\n"
        "Each output object must use this schema:\n"
        f"{output_contract}\n"
        f"Input items:\n{json.dumps(items, ensure_ascii=True)}"
    )


# NOTE: _build_response_schema is kept for reference but no longer called.
# responseJsonSchema is not supported by the Gemini REST API — only by the
# Google Gen AI Python SDK. Sending it via REST causes 400 INVALID_ARGUMENT.
def _build_response_schema(batch_size: int) -> dict[str, Any]:
    return {
        "type": "array",
        "minItems": batch_size,
        "maxItems": batch_size,
        "items": {
            "type": "object",
            "required": [
                "company_name",
                "location",
                "industry",
                "software_detected",
                "migration_detected",
                "migration_from",
                "pain_signals",
                "expansion_signals",
                "confidence",
                "reasoning",
            ],
            "additionalProperties": False,
            "properties": {
                "company_name": {"type": "string"},
                "location": {"type": ["string", "null"]},
                "industry": {"type": "string", "enum": list(INDUSTRY_CHOICES)},
                "software_detected": {
                    "type": "array",
                    "items": {"type": "string", "enum": sorted(ALLOWED_SOFTWARE_NAMES)},
                },
                "migration_detected": {"type": "boolean"},
                "migration_from": {"type": ["string", "null"]},
                "pain_signals": {"type": "array", "items": {"type": "string"}},
                "expansion_signals": {"type": "array", "items": {"type": "string"}},
                "confidence": {"type": "number"},
                "reasoning": {"type": "string"},
            },
        },
    }


def _sanitise_text(text: str, max_chars: int = 5000) -> str:
    """Remove null bytes and control characters that cause Gemini 500 errors.

    Also truncates to max_chars — the source_text is a pipe-joined snippet,
    so 1500 chars is more than enough for signal extraction. Sending full job
    descriptions inflates token usage and increases 500 error rate.
    """
    # Strip null bytes and non-printable control chars (except tab/newline)
    cleaned = "".join(
        ch for ch in text
        if ch == "\t" or ch == "\n" or (ord(ch) >= 32 and ord(ch) != 127)
    )
    # Collapse excessive whitespace
    cleaned = " ".join(cleaned.split())
    return cleaned[:max_chars]


def _normalize_software(values: Any) -> list[str]:
    normalized: list[str] = []
    seen: set[str] = set()
    if not isinstance(values, list):
        return normalized

    for value in values:
        if not isinstance(value, str):
            continue
        cleaned = value.strip()
        canonical = SOFTWARE_DISPLAY_TO_CANONICAL.get(cleaned)
        if canonical is None:
            canonical = SOFTWARE_DISPLAY_TO_CANONICAL.get(cleaned.title())
        if canonical is None and cleaned.lower() in SOFTWARE_CANONICAL_TO_DISPLAY:
            canonical = cleaned.lower()
        if canonical is None:
            continue
        display = SOFTWARE_CANONICAL_TO_DISPLAY[canonical]
        if display in seen:
            continue
        seen.add(display)
        normalized.append(display)
    return normalized


def _software_from_prefilter(prefilter: PrefilterResult | None) -> list[str]:
    if prefilter is None:
        return []

    normalized: list[str] = []
    seen: set[str] = set()
    for product_name in prefilter.matched_products:
        canonical = SOFTWARE_DISPLAY_TO_CANONICAL.get(product_name)
        if canonical is None:
            canonical = SOFTWARE_DISPLAY_TO_CANONICAL.get(product_name.title())
        if canonical is None:
            canonical = product_name.strip().lower()
        display = SOFTWARE_CANONICAL_TO_DISPLAY.get(canonical)
        if not display or display in seen:
            continue
        seen.add(display)
        normalized.append(display)
    return normalized


def _normalize_industry(value: Any) -> str:
    if not isinstance(value, str):
        return "Unknown"
    cleaned = value.strip()
    if cleaned in INDUSTRY_CHOICES:
        return cleaned
    return "Unknown"


def _is_consulting_company(company_name: str, source_text: str) -> bool:
    normalized_name = " ".join(company_name.strip().lower().split())
    if any(term in normalized_name for term in CONSULTING_NAME_TERMS):
        return True

    normalized_text = " ".join(source_text.strip().lower().split())
    if not normalized_text:
        return False

    # Require a text signal that points to services/consulting rather than a single generic word.
    return any(term in normalized_text for term in CONSULTING_SOURCE_TERMS)


def _normalize_optional_string(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    cleaned = value.strip()
    return cleaned or None


def _filter_string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item).strip() for item in value if str(item).strip()]


def _coerce_float(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _normalize_company_hint(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = " ".join(value.strip().lower().split())
    return normalized or None


def _recent_company_match(company_hint: str, recent_companies: set[str]) -> bool:
    if company_hint in recent_companies:
        return True
    return any(_company_names_similar(company_hint, recent_name) for recent_name in recent_companies)


def _company_names_similar(left: str, right: str) -> bool:
    if left == right:
        return True
    left_tokens = set(left.split())
    right_tokens = set(right.split())
    legal_suffixes = {"gmbh", "inc", "ltd", "llc", "ag"}
    if left_tokens and right_tokens and left_tokens.issubset(right_tokens | legal_suffixes):
        return True
    if left_tokens and right_tokens and right_tokens.issubset(left_tokens | legal_suffixes):
        return True
    return SequenceMatcher(a=left, b=right).ratio() >= 0.88


def _strip_json_fences(text: str) -> str:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        lines = cleaned.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        cleaned = "\n".join(lines).strip()
    return cleaned


def _extract_first_json_array(text: str) -> str | None:
    start = text.find("[")
    if start == -1:
        return None

    depth = 0
    in_string = False
    escape = False
    for index in range(start, len(text)):
        ch = text[index]
        if in_string:
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == '"':
                in_string = False
            continue

        if ch == '"':
            in_string = True
            continue
        if ch == "[":
            depth += 1
            continue
        if ch == "]":
            depth -= 1
            if depth == 0:
                return text[start:index + 1]
    return None


def _looks_like_prompt_echo(text: str) -> bool:
    lowered = text.lower()
    return (
        "goal: extract siemens plm lead signals" in lowered
        or "constraints:" in lowered
        or "output: a single parseable json array of objects" in lowered
    )


def _preview_text(text: str, limit: int = 400) -> str:
    return text[:limit].replace("\n", " ")


def _chunked(values: list[ExtractionCandidate], size: int) -> Iterable[list[ExtractionCandidate]]:
    for index in range(0, len(values), size):
        yield values[index:index + size]


def _load_llm_requests_per_minute() -> int:
    raw_value = os.getenv("LLM_REQUESTS_PER_MINUTE")
    if raw_value is None or not raw_value.strip():
        return DEFAULT_LLM_REQUESTS_PER_MINUTE
    try:
        parsed = int(raw_value)
    except ValueError:
        logger.warning(
            "invalid LLM_REQUESTS_PER_MINUTE={!r}; falling back to {}",
            raw_value,
            DEFAULT_LLM_REQUESTS_PER_MINUTE,
        )
        return DEFAULT_LLM_REQUESTS_PER_MINUTE
    if parsed < 1:
        logger.warning(
            "LLM_REQUESTS_PER_MINUTE={} must be at least 1; using {}",
            parsed,
            DEFAULT_LLM_REQUESTS_PER_MINUTE,
        )
        return DEFAULT_LLM_REQUESTS_PER_MINUTE
    return parsed
