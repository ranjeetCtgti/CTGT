from __future__ import annotations

import json
import os
from collections import Counter
from dataclasses import dataclass
from difflib import SequenceMatcher
from json import JSONDecodeError
from typing import Any, Iterable

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


class GeminiClientError(Exception):
    """Raised when Gemini extraction fails irrecoverably."""


@dataclass
class ExtractionCandidate:
    source_url: str
    source_title: str
    source_text: str
    signal_source: SignalSource
    signal_type: SignalType
    company_hint: str | None = None
    location_hint: str | None = None


def _is_retryable_gemini_error(exc: Exception) -> bool:
    if isinstance(exc, (httpx.TimeoutException, httpx.TransportError)):
        return True
    if isinstance(exc, GeminiClientError) and "429" in str(exc):
        return True
    if isinstance(exc, GeminiClientError) and ("status=500" in str(exc) or '"status": "INTERNAL"' in str(exc)):
        return True
    if isinstance(exc, httpx.HTTPStatusError):
        return exc.response.status_code == 429 or 500 <= exc.response.status_code < 600
    return False


class GeminiExtractor:
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

    def close(self) -> None:
        self._http.close()

    def __enter__(self) -> "GeminiExtractor":
        return self

    def __exit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
        self.close()

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
            logger.info("gemini extraction skipped because no candidates survived internal filtering")
        signals: list[ExtractedSignal] = []
        decision_counts: Counter[str] = Counter()
        debug_log_limit = 20
        debug_logged = 0

        for batch in _chunked(deduped_candidates, self.batch_size):
            try:
                payload = self._build_payload(batch)
                response_json = self._call_gemini(payload)
                raw_items = self._extract_response_items(response_json)
                if len(batch) == 1 and len(raw_items) == 0:
                    logger.warning(
                        "gemini returned no usable JSON objects for single-item batch first_try source_url={} raw_preview={!r}",
                        batch[0].source_url,
                        _preview_text(self._extract_response_text(response_json)),
                    )
                    response_json = self._call_gemini(self._build_payload(batch, single_item_retry=True))
                    raw_items = self._extract_response_items(response_json)
                if len(raw_items) != len(batch):
                    logger.warning(
                        "gemini response count mismatch first_try expected={} actual={} retrying_once raw_preview={!r}",
                        len(batch),
                        len(raw_items),
                        _preview_text(self._extract_response_text(response_json)),
                    )
                    response_json = self._call_gemini(payload)
                    raw_items = self._extract_response_items(response_json)
                self._validate_batch_size(batch, raw_items)
            except Exception as exc:
                logger.error("gemini batch failed size={} error={}", len(batch), str(exc))
                continue

            for candidate, raw_item in zip(batch, raw_items):
                signal, decision = self._post_process_item(candidate, raw_item)
                decision_counts[decision] += 1
                if self.debug and debug_logged < debug_log_limit:
                    logger.info(
                        "gemini decision source={} company_hint={!r} detected_company={!r} software_raw={} confidence={} decision={} reasoning={!r}",
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
            logger.info("gemini extraction summary decisions={}", dict(decision_counts))
        return signals

    def from_job_postings(self, postings: list[RawJobPosting]) -> list[ExtractionCandidate]:
        return [candidate_from_job_posting(posting) for posting in postings]

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
            prefilter = keyword_prefilter(candidate.source_text)
            if not prefilter.passed:
                continue
            filtered.append(candidate)
        return filtered

    def _build_payload(
        self,
        batch: list[ExtractionCandidate],
        single_item_retry: bool = False,
    ) -> dict[str, Any]:
        prompt = _build_prompt(batch, single_item_retry=single_item_retry)
        return {
            "contents": [
                {
                    "parts": [
                        {
                            "text": prompt,
                        }
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.1,
                "maxOutputTokens": 2048,
                "responseMimeType": "application/json",
                "responseJsonSchema": _build_response_schema(len(batch)),
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

    def _extract_response_items(self, response_json: dict[str, Any]) -> list[dict[str, Any]]:
        text = self._extract_response_text(response_json)
        if not text:
            candidates = response_json.get("candidates") or []
            if not candidates:
                raise GeminiClientError("Gemini returned no candidates")
            raise GeminiClientError("Gemini returned no content parts")

        cleaned = _strip_json_fences(text)
        if not cleaned.strip():
            raise GeminiClientError("Gemini returned empty content text")
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
                        f"Gemini returned invalid JSON payload preview={preview!r}"
                    ) from exc
            else:
                preview = cleaned[:400].replace("\n", " ")
                raise GeminiClientError(
                    f"Gemini returned invalid JSON payload preview={preview!r}"
                ) from exc
        if isinstance(parsed, dict):
            parsed = [parsed]
        if not isinstance(parsed, list):
            raise GeminiClientError("Gemini response was not a JSON list")
        return [item for item in parsed if isinstance(item, dict)]

    def _extract_response_text(self, response_json: dict[str, Any]) -> str:
        candidates = response_json.get("candidates") or []
        if not candidates:
            return ""
        parts = candidates[0].get("content", {}).get("parts", [])
        if not parts:
            return ""
        return "".join(part.get("text", "") for part in parts)

    def _post_process_item(
        self,
        candidate: ExtractionCandidate,
        raw_item: dict[str, Any],
    ) -> tuple[ExtractedSignal | None, str]:
        company_name = str(raw_item.get("company_name") or candidate.company_hint or "").strip()
        if not company_name or company_name.lower() in EXCLUDED_COMPANIES:
            return None, "excluded_or_missing_company"

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
        if len(raw_items) != len(batch):
            raise GeminiClientError(
                f"Gemini response count mismatch expected={len(batch)} actual={len(raw_items)}"
            )


def candidate_from_job_posting(posting: RawJobPosting) -> ExtractionCandidate:
    source_text = " | ".join(
        value for value in [posting.query, posting.title, posting.company_name, posting.location, posting.snippet] if value
    )
    return ExtractionCandidate(
        source_url=str(posting.job_url),
        source_title=posting.title,
        source_text=source_text,
        signal_source=posting.source,
        signal_type="job_posting",
        company_hint=posting.company_name,
        location_hint=posting.location,
    )


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
) -> str:
    items = []
    for index, candidate in enumerate(batch, start=1):
        items.append(
            {
                "id": index,
                "company_hint": candidate.company_hint,
                "location_hint": candidate.location_hint,
                "signal_source": candidate.signal_source,
                "source_title": candidate.source_title,
                "text": candidate.source_text,
            }
        )

    if single_item_retry and len(batch) == 1:
        return (
            "Return only one JSON array with one object. No prose. No bullets. No markdown. No schema echo.\n"
            f"Allowed industry values: {', '.join(INDUSTRY_CHOICES)}.\n"
            f"Allowed software_detected values: {', '.join(sorted(ALLOWED_SOFTWARE_NAMES))}.\n"
            "If Siemens PLM evidence is weak, return empty software_detected and low confidence instead of explanation text.\n"
            "Required output format:\n"
            '[{"company_name":"string","location":"string or null","industry":"string","software_detected":["allowed values only"],'
            '"migration_detected":true,"migration_from":"string or null","pain_signals":["phrases"],'
            '"expansion_signals":["phrases"],"confidence":0.0,"reasoning":"one sentence"}]\n'
            f"Input item:\n{json.dumps(items[0], ensure_ascii=True)}"
        )

    return (
        "You extract Siemens PLM lead signals for CTGT Innovations.\n"
        "Return only valid JSON as an array with exactly one object per input item in the same order.\n"
        "Do not include markdown, commentary, bullets, prompt restatement, or extra keys.\n"
        f"Allowed industry values: {', '.join(INDUSTRY_CHOICES)}.\n"
        f"Allowed software_detected values: {', '.join(sorted(ALLOWED_SOFTWARE_NAMES))}.\n"
        "Watch for migration signals such as Windchill, Enovia, CATIA, Autodesk Vault, SAP PLM, or legacy PDM replacements.\n"
        "Each output object must use this schema:\n"
        '{"company_name":"string","location":"string or null","industry":"string","software_detected":["allowed values only"],'
        '"migration_detected":true,"migration_from":"string or null","pain_signals":["phrases"],'
        '"expansion_signals":["phrases"],"confidence":0.0,"reasoning":"one sentence"}\n'
        f"Input items:\n{json.dumps(items, ensure_ascii=True)}"
    )


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


def _normalize_industry(value: Any) -> str:
    if not isinstance(value, str):
        return "Unknown"
    cleaned = value.strip()
    if cleaned in INDUSTRY_CHOICES:
        return cleaned
    return "Unknown"


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
