from __future__ import annotations

import os
import re
from dataclasses import dataclass
from difflib import SequenceMatcher
from typing import Any, Protocol
from urllib.parse import urlparse

import httpx


GOOGLE_KG_SEARCH_URL = "https://kgsearch.googleapis.com/v1/entities:search"
CLEARBIT_AUTOCOMPLETE_URL = "https://autocomplete.clearbit.com/v1/companies/suggest"
GENERIC_REFERENCE_DOMAINS = {
    "google.com",
    "wikipedia.org",
    "wikidata.org",
    "schema.org",
    "kgsearch.googleapis.com",
    "g.co",
}
THIRD_PARTY_PROFILE_DOMAINS = {
    "linkedin.com",
    "crunchbase.com",
    "bloomberg.com",
    "rocketreach.co",
    "zoominfo.com",
    "owler.com",
    "theorg.com",
    "glassdoor.com",
    "facebook.com",
    "instagram.com",
    "x.com",
    "twitter.com",
    "youtube.com",
    "pitchbook.com",
    "craft.co",
    "cbinsights.com",
}
LEGAL_SUFFIX_PATTERNS = (
    r"\bpty\s+ltd\.?",
    r"\bgmbh\s*&\s*co\.\s*kg",
    r"\bgmbh\.?",
    r"\bag\.?",
    r"\bse\.?",
    r"\binc\.?",
    r"\bltd\.?",
    r"\bllc\.?",
    r"\bplc\.?",
    r"\bsa\.?",
    r"\bsrl\.?",
    r"\bbv\.?",
    r"\bcorp\.?",
    r"\bcorporation\b",
    r"\blimited\b",
)
REGION_NOISE_PATTERNS = (
    r"\baustralia\b",
    r"\bgermany\b",
    r"\bindia\b",
    r"\bcanada\b",
    r"\busa\b",
    r"\bus\b",
    r"\buk\b",
    r"\beurope\b",
    r"\bnorth america\b",
    r"\basia pacific\b",
    r"\bapac\b",
)
COMMON_GUESS_TLDS = (".com", ".de", ".com.au", ".co.uk", ".io")


@dataclass(slots=True)
class DomainResolutionResult:
    company_name: str
    company_domain: str | None = None
    confidence: float = 0.0
    source: str = "none"
    reason: str | None = None
    raw_url: str | None = None


class DomainResolver(Protocol):
    def close(self) -> None: ...
    def __enter__(self) -> "DomainResolver": ...
    def __exit__(self, exc_type: Any, exc: Any, tb: Any) -> None: ...
    def resolve(
        self,
        company_name: str,
        location: str | None = None,
        *,
        source_url: str | None = None,
        signal_source: str | None = None,
    ) -> DomainResolutionResult: ...


class BaseDomainResolver:
    def __enter__(self) -> "BaseDomainResolver":
        return self

    def __exit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
        self.close()


class NoOpDomainResolver(BaseDomainResolver):
    def close(self) -> None:
        return

    def resolve(
        self,
        company_name: str,
        location: str | None = None,
        *,
        source_url: str | None = None,
        signal_source: str | None = None,
    ) -> DomainResolutionResult:
        return DomainResolutionResult(
            company_name=company_name,
            source="noop",
            reason="domain resolution disabled",
        )


class GoogleKnowledgeGraphDomainResolver(BaseDomainResolver):
    def __init__(self, api_key: str, timeout_seconds: int) -> None:
        self.api_key = api_key
        self._http = httpx.Client(timeout=timeout_seconds)

    def close(self) -> None:
        self._http.close()

    def resolve(
        self,
        company_name: str,
        location: str | None = None,
        *,
        source_url: str | None = None,
        signal_source: str | None = None,
    ) -> DomainResolutionResult:
        heuristic = _resolve_from_source_context(
            company_name=company_name,
            source_url=source_url,
            signal_source=signal_source,
        )
        if heuristic is not None:
            return heuristic

        explicit_domain = _explicit_domain_from_company_name(company_name)
        if explicit_domain is not None:
            return DomainResolutionResult(
                company_name=company_name,
                company_domain=explicit_domain,
                confidence=1.0,
                source="company_name_domain",
                reason=f"company name already appears to be a domain `{explicit_domain}`",
                raw_url=f"https://{explicit_domain}",
            )

        query_name = _clean_company_name_for_lookup(company_name)
        if not query_name:
            query_name = company_name.strip()
        query = query_name
        if location:
            query = f"{query} {location.strip()}"

        response = self._http.get(
            GOOGLE_KG_SEARCH_URL,
            params={
                "query": query,
                "types": "Organization",
                "languages": "en",
                "limit": 10,
                "key": self.api_key,
            },
        )
        response.raise_for_status()
        payload = response.json()
        kg_result = _select_best_result(company_name, payload)
        if kg_result.company_domain and _domain_resolution_passes_threshold(kg_result.confidence):
            return kg_result
        clearbit_result = _resolve_via_clearbit_autocomplete(
            self._http,
            company_name=company_name,
            query_name=query_name,
        )
        if clearbit_result is not None:
            return clearbit_result
        fallback = _resolve_by_verified_domain_guess(
            self._http,
            company_name=company_name,
            location=location,
        )
        if fallback is not None:
            return fallback
        return kg_result


def build_domain_resolver() -> DomainResolver:
    if not _env_flag("ENRICHMENT_ENABLED", default=False):
        return NoOpDomainResolver()

    provider = (os.getenv("ENRICHMENT_PROVIDER") or "google_kg").strip().lower()
    timeout_seconds = int(os.getenv("ENRICHMENT_TIMEOUT_SECONDS", "15"))
    if provider == "google_kg":
        api_key = (os.getenv("GOOGLE_KG_API_KEY") or "").strip()
        if not api_key:
            raise ValueError("GOOGLE_KG_API_KEY is missing")
        return GoogleKnowledgeGraphDomainResolver(api_key=api_key, timeout_seconds=timeout_seconds)
    if provider == "noop":
        return NoOpDomainResolver()
    raise ValueError(f"Unsupported ENRICHMENT_PROVIDER: {provider}")


def canonicalize_domain(value: str | None) -> str | None:
    if value is None:
        return None
    cleaned = value.strip().lower()
    if not cleaned:
        return None

    candidate = cleaned
    if "://" not in candidate and "/" not in candidate:
        parsed = urlparse(f"//{candidate}")
    elif "://" not in candidate:
        parsed = urlparse(f"https://{candidate}")
    else:
        parsed = urlparse(candidate)

    host = parsed.netloc or parsed.path.split("/")[0]
    host = host.strip().lower()
    if not host:
        return None
    if "@" in host:
        host = host.rsplit("@", 1)[-1]
    if ":" in host:
        host = host.split(":", 1)[0]
    if host.startswith("www."):
        host = host[4:]
    return host or None


def _explicit_domain_from_company_name(company_name: str) -> str | None:
    raw_value = company_name.strip()
    if not raw_value or " " in raw_value or "@" in raw_value:
        return None
    domain = canonicalize_domain(raw_value)
    if not domain or "." not in domain:
        return None
    tld = domain.rsplit(".", 1)[-1]
    if not tld.isalpha() or len(tld) < 2:
        return None
    return domain


def _resolve_from_source_context(
    *,
    company_name: str,
    source_url: str | None,
    signal_source: str | None,
) -> DomainResolutionResult | None:
    source_domain = canonicalize_domain(source_url)
    if not source_domain:
        return None
    if _is_generic_reference_domain(source_domain) or _is_third_party_profile_domain(source_domain):
        return None

    if signal_source == "career_page":
        return DomainResolutionResult(
            company_name=company_name,
            company_domain=source_domain,
            confidence=0.99,
            source="source_url_career_page",
            reason=f"trusted first-party career page host `{source_domain}`",
            raw_url=source_url,
        )

    if signal_source == "news" and _source_domain_matches_company_name(company_name, source_domain):
        return DomainResolutionResult(
            company_name=company_name,
            company_domain=source_domain,
            confidence=0.88,
            source="source_url_news",
            reason=f"trusted news/article host `{source_domain}` because it strongly matches company name",
            raw_url=source_url,
        )

    return None


def _select_best_result(
    company_name: str,
    payload: dict[str, Any],
    *,
    match_name: str | None = None,
) -> DomainResolutionResult:
    best_domain: str | None = None
    best_url: str | None = None
    best_confidence = 0.0
    best_reason = "no viable organization url in Google Knowledge Graph response"
    name_for_match = match_name or company_name

    for item in payload.get("itemListElement", []) or []:
        if not isinstance(item, dict):
            continue
        result = item.get("result") or {}
        if not isinstance(result, dict):
            continue

        candidate_name = _clean_string(result.get("name")) or company_name
        name_score = _name_similarity(name_for_match, candidate_name)
        result_score = _coerce_float(item.get("resultScore"))
        score_component = min(result_score / 1000.0, 1.0) if result_score > 0 else 0.0

        for raw_url in _extract_candidate_urls(result):
            domain = canonicalize_domain(raw_url)
            if not domain or _is_generic_reference_domain(domain) or _is_third_party_profile_domain(domain):
                continue

            confidence = round((0.75 * name_score) + (0.25 * score_component), 4)
            if domain == _domain_hint_from_company_name(name_for_match):
                confidence = min(1.0, confidence + 0.1)
            if confidence <= best_confidence:
                continue

            best_domain = domain
            best_url = raw_url
            best_confidence = confidence
            best_reason = f"matched KG organization `{candidate_name}` via {raw_url}"

    return DomainResolutionResult(
        company_name=company_name,
        company_domain=best_domain,
        confidence=best_confidence,
        source="google_kg",
        reason=best_reason,
        raw_url=best_url,
    )


def _extract_candidate_urls(result: dict[str, Any]) -> list[str]:
    urls: list[str] = []
    direct_url = _clean_string(result.get("url"))
    if direct_url:
        urls.append(direct_url)

    detailed_description = result.get("detailedDescription")
    if isinstance(detailed_description, dict):
        description_url = _clean_string(detailed_description.get("url"))
        if description_url:
            urls.append(description_url)

    identifiers = result.get("identifier")
    if isinstance(identifiers, list):
        urls.extend(
            identifier.strip()
            for identifier in identifiers
            if isinstance(identifier, str) and identifier.strip().startswith("http")
        )
    elif isinstance(identifiers, str) and identifiers.strip().startswith("http"):
        urls.append(identifiers.strip())

    deduped: list[str] = []
    seen: set[str] = set()
    for url in urls:
        if url in seen:
            continue
        seen.add(url)
        deduped.append(url)
    return deduped


def _is_generic_reference_domain(domain: str) -> bool:
    return any(domain == generic or domain.endswith(f".{generic}") for generic in GENERIC_REFERENCE_DOMAINS)


def _is_third_party_profile_domain(domain: str) -> bool:
    return any(domain == profile or domain.endswith(f".{profile}") for profile in THIRD_PARTY_PROFILE_DOMAINS)


def _source_domain_matches_company_name(company_name: str, domain: str) -> bool:
    normalized_name = _normalize_company_name(company_name)
    if not normalized_name:
        return False

    name_tokens = [
        token
        for token in normalized_name.split()
        if token.isascii() and token not in {"gmbh", "inc", "ltd", "llc", "ag", "corp", "corporation", "limited", "co", "company"}
    ]
    if not name_tokens:
        return False

    host_root = domain.split(".", 1)[0]
    comparable_host = "".join(ch for ch in host_root.lower() if ch.isalnum())
    if not comparable_host:
        return False

    normalized_tokens = ["".join(ch for ch in token.lower() if ch.isalnum()) for token in name_tokens]
    normalized_tokens = [token for token in normalized_tokens if token]
    if not normalized_tokens:
        return False

    if comparable_host in normalized_tokens:
        return True

    joined_name = "".join(normalized_tokens)
    if comparable_host == joined_name:
        return True

    return SequenceMatcher(a=comparable_host, b=joined_name).ratio() >= 0.9


def _name_similarity(left: str, right: str) -> float:
    left_norm = _normalize_company_name(left)
    right_norm = _normalize_company_name(right)
    if not left_norm or not right_norm:
        return 0.0
    if left_norm == right_norm:
        return 1.0

    left_tokens = set(left_norm.split())
    right_tokens = set(right_norm.split())
    legal_suffixes = {"gmbh", "inc", "ltd", "llc", "ag", "corp", "corporation", "limited"}
    if left_tokens and right_tokens and left_tokens.issubset(right_tokens | legal_suffixes):
        return 0.97
    if left_tokens and right_tokens and right_tokens.issubset(left_tokens | legal_suffixes):
        return 0.97
    return SequenceMatcher(a=left_norm, b=right_norm).ratio()


def _normalize_company_name(value: str) -> str:
    cleaned = value.strip().lower()
    cleaned = re.sub(r"^[^\w]+", "", cleaned)
    cleaned = (
        cleaned.replace("ä", "ae")
        .replace("ö", "oe")
        .replace("ü", "ue")
        .replace("ß", "ss")
    )
    tokens = re.findall(r"[a-z0-9]+", cleaned)
    if not tokens:
        return ""
    legal_suffixes = {"gmbh", "inc", "ltd", "llc", "ag", "corp", "corporation", "limited", "co", "kg", "se", "plc", "sa", "bv", "srl", "pty"}
    normalized_tokens = [token for token in tokens if token not in legal_suffixes]
    if not normalized_tokens:
        normalized_tokens = tokens
    return " ".join(normalized_tokens)


def _domain_hint_from_company_name(company_name: str) -> str | None:
    tokens = [token for token in _normalize_company_name(company_name).split() if token.isascii()]
    if not tokens:
        return None
    legal_suffixes = {"gmbh", "inc", "ltd", "llc", "ag", "corp", "corporation", "limited"}
    filtered = [token for token in tokens if token not in legal_suffixes]
    if not filtered:
        return None
    return f"{filtered[0]}.com"


def _clean_company_name_for_lookup(company_name: str) -> str:
    cleaned = _normalize_company_name(company_name)
    cleaned = re.sub(r"^[^\w]+", "", cleaned)
    for pattern in REGION_NOISE_PATTERNS:
        cleaned = re.sub(pattern, " ", cleaned, flags=re.IGNORECASE)
    for pattern in LEGAL_SUFFIX_PATTERNS:
        cleaned = re.sub(pattern, " ", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned or _normalize_company_name(company_name)


def _resolve_via_clearbit_autocomplete(
    client: httpx.Client,
    *,
    company_name: str,
    query_name: str,
) -> DomainResolutionResult | None:
    try:
        response = client.get(
            CLEARBIT_AUTOCOMPLETE_URL,
            params={"query": query_name},
            follow_redirects=True,
        )
        response.raise_for_status()
    except Exception:
        return None

    payload = response.json()
    if not isinstance(payload, list):
        return None

    best_domain: str | None = None
    best_name: str | None = None
    best_score = 0.0

    for item in payload:
        if not isinstance(item, dict):
            continue
        candidate_name = _clean_string(item.get("name")) or ""
        candidate_domain = canonicalize_domain(_clean_string(item.get("domain")))
        if not candidate_domain:
            continue
        score = _name_similarity(query_name, candidate_name)
        if candidate_domain == _domain_hint_from_company_name(query_name):
            score = min(1.0, score + 0.05)
        if score <= best_score:
            continue
        best_domain = candidate_domain
        best_name = candidate_name or company_name
        best_score = score

    if not best_domain or best_score < 0.8:
        return None

    return DomainResolutionResult(
        company_name=company_name,
        company_domain=best_domain,
        confidence=round(max(0.76, min(best_score, 0.9)), 4),
        source="clearbit_autocomplete",
        reason=f"matched Clearbit Autocomplete company `{best_name}` to domain `{best_domain}`",
        raw_url=f"https://{best_domain}",
    )


def _resolve_by_verified_domain_guess(
    client: httpx.Client,
    *,
    company_name: str,
    location: str | None,
) -> DomainResolutionResult | None:
    guess_stems = _candidate_domain_stems(company_name)
    if not guess_stems:
        return None

    tlds = _candidate_tlds(location)
    for stem in guess_stems:
        for tld in tlds:
            domain = f"{stem}{tld}"
            if not _verify_domain(client, domain):
                continue
            return DomainResolutionResult(
                company_name=company_name,
                company_domain=domain,
                confidence=0.76,
                source="heuristic_verified_domain",
                reason=f"verified heuristic domain guess `{domain}` after KG miss/low-confidence result",
                raw_url=f"https://{domain}",
            )
    return None


def _candidate_domain_stems(company_name: str) -> list[str]:
    cleaned = _clean_company_name_for_lookup(company_name)
    if not cleaned:
        return []

    tokens = [
        re.sub(r"[^a-z0-9]", "", token.lower())
        for token in cleaned.split()
    ]
    tokens = [token for token in tokens if token]
    if not tokens:
        return []

    stems: list[str] = []
    seen: set[str] = set()
    for candidate in ("".join(tokens), tokens[0]):
        if len(candidate) < 3 or candidate in seen:
            continue
        seen.add(candidate)
        stems.append(candidate)
    return stems


def _candidate_tlds(location: str | None) -> list[str]:
    location_norm = _normalize_company_name(location or "")
    ordered_tlds: list[str] = []
    if "australia" in location_norm:
        ordered_tlds.append(".com.au")
    if any(token in location_norm for token in {"germany", "deutschland"}):
        ordered_tlds.append(".de")
    if any(token in location_norm for token in {"united kingdom", "uk", "england", "scotland"}):
        ordered_tlds.append(".co.uk")
    for tld in COMMON_GUESS_TLDS:
        if tld not in ordered_tlds:
            ordered_tlds.append(tld)
    return ordered_tlds


def _verify_domain(client: httpx.Client, domain: str) -> bool:
    for method in ("HEAD", "GET"):
        for scheme in ("https", "http"):
            try:
                response = client.request(method, f"{scheme}://{domain}", follow_redirects=True)
            except Exception:
                continue
            if response.status_code < 400:
                return True
    return False


def _domain_resolution_passes_threshold(confidence: float) -> bool:
    threshold = float(os.getenv("ENRICHMENT_MIN_DOMAIN_CONFIDENCE", "0.75"))
    return confidence >= threshold


def _clean_string(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    cleaned = " ".join(value.split()).strip()
    return cleaned or None


def _coerce_float(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _env_flag(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}
