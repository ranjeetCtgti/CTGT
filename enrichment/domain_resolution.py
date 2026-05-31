from __future__ import annotations

import os
import re
import time
from dataclasses import dataclass
from difflib import SequenceMatcher
from typing import Any, Protocol
from urllib.parse import parse_qs, urlparse

import httpx
from bs4 import BeautifulSoup
from loguru import logger

SERPER_GOOGLE_SEARCH_API_URL = "https://google.serper.dev/search"
CLEARBIT_AUTOCOMPLETE_URL = "https://autocomplete.clearbit.com/v1/companies/suggest"
GOOGLE_SEARCH_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)
GENERIC_REFERENCE_DOMAINS = {
    "google.com",
    "wikipedia.org",
    "wikidata.org",
    "schema.org",
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


def resolve_company_domain(
    company_name: str,
    *,
    location: str | None = None,
    source_url: str | None = None,
    signal_source: str | None = None,
) -> DomainResolutionResult:
    with build_domain_resolver() as resolver:
        return resolver.resolve(
            company_name,
            location=location,
            source_url=source_url,
            signal_source=signal_source,
        )


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


class SerperDomainResolver(BaseDomainResolver):
    def __init__(self, timeout_seconds: int) -> None:
        self.serper_api_key = (os.getenv("SERPER_API_KEY") or "").strip()
        if not self.serper_api_key:
            raise ValueError("SERPER_API_KEY is missing")
        self._http = httpx.Client(
            timeout=timeout_seconds,
            headers={
                "User-Agent": GOOGLE_SEARCH_USER_AGENT,
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9",
                "Cache-Control": "no-cache",
            },
            follow_redirects=True,
        )

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

        candidates: dict[str, dict[str, Any]] = {}
        search_name = _expand_search_characters_unicode(company_name).strip()
        query_name = _clean_company_name_for_lookup(company_name) or search_name
        search_queries = _serper_search_queries(search_name=search_name, location=location)
        logger.info(
            "domain resolver start company={} search_name={} query_name={} location={} provider=serper",
            company_name,
            search_name,
            query_name,
            location or "-",
        )
        for index, query in enumerate(search_queries):
            if index > 0:
                time.sleep(_serper_request_delay_seconds())
            try:
                html = self._fetch_serper_search_html(query, location=location)
            except Exception as exc:
                logger.warning(
                    "domain resolver serper_request_failed company={} query={} error={}",
                    company_name,
                    query,
                    exc,
                )
                continue

            for result in _extract_serper_result_candidates(html):
                domain = canonicalize_domain(result.get("url"))
                if not domain or _is_generic_reference_domain(domain) or _is_third_party_profile_domain(domain):
                    continue
                candidate = candidates.setdefault(
                    domain,
                    {
                        "query_hits": 0,
                        "best_url": result.get("url"),
                        "best_title": result.get("title"),
                        "best_snippet": result.get("snippet"),
                    },
                )
                candidate["query_hits"] += 1
                if _candidate_result_score(company_name, domain, result) > _candidate_result_score(
                    company_name,
                    domain,
                    {
                        "title": candidate.get("best_title"),
                        "snippet": candidate.get("best_snippet"),
                        "url": candidate.get("best_url"),
                    },
                ):
                    candidate["best_url"] = result.get("url")
                    candidate["best_title"] = result.get("title")
                    candidate["best_snippet"] = result.get("snippet")

        best_result = DomainResolutionResult(
            company_name=company_name,
            source="serper",
            reason="no validated first-party domain found from Serper Google search results",
        )
        for domain, candidate in sorted(
            candidates.items(),
            key=lambda item: (
                item[1]["query_hits"],
                _candidate_result_score(company_name, item[0], item[1]),
            ),
            reverse=True,
        ):
            page_validation = _validate_candidate_domain(
                self._http,
                company_name=company_name,
                domain=domain,
                preferred_url=candidate.get("best_url"),
            )
            if page_validation is None:
                continue
            confidence = round(
                min(
                    0.99,
                    0.45
                    + (0.2 * min(candidate["query_hits"], len(search_queries)) / max(len(search_queries), 1))
                    + (0.35 * page_validation["name_score"]),
                ),
                4,
            )
            if confidence <= best_result.confidence:
                continue
            best_result = DomainResolutionResult(
                company_name=company_name,
                company_domain=domain,
                confidence=confidence,
                source="serper",
                reason=(
                    f"validated first-party domain `{domain}` from Serper Google search "
                    f"using page title/text match score {page_validation['name_score']:.2f}"
                ),
                raw_url=page_validation["validated_url"],
            )

        if best_result.company_domain:
            logger.info(
                "domain resolver serper_hit company={} domain={} confidence={} url={}",
                company_name,
                best_result.company_domain,
                best_result.confidence,
                best_result.raw_url or "-",
            )
            return best_result

        logger.info(
            "domain resolver serper_miss company={} reason={} fallback=clearbit",
            company_name,
            best_result.reason or "-",
        )
        clearbit_result = _resolve_via_clearbit_autocomplete(
            self._http,
            company_name=company_name,
            query_name=query_name,
        )
        if clearbit_result is not None:
            logger.info(
                "domain resolver clearbit_fallback company={} domain={} confidence={}",
                company_name,
                clearbit_result.company_domain or "-",
                clearbit_result.confidence,
            )
            return clearbit_result
        logger.info("domain resolver unresolved company={} provider=serper_clearbit", company_name)
        return best_result

    def _fetch_serper_search_html(self, query: str, *, location: str | None) -> str:
        response = self._http.post(
            SERPER_GOOGLE_SEARCH_API_URL,
            headers={
                "X-API-KEY": self.serper_api_key,
                "Content-Type": "application/json",
            },
            json={
                "q": query,
                "gl": _serper_gl_from_location(location),
                "hl": "en",
                "type": "search",
                "engine": "google",
            },
        )
        response.raise_for_status()
        payload = response.json()
        organic_results = payload.get("organic") or []
        return _serper_results_to_html_stub(organic_results)


def build_domain_resolver() -> DomainResolver:
    if not _env_flag("ENRICHMENT_ENABLED", default=False):
        return NoOpDomainResolver()

    provider = (os.getenv("ENRICHMENT_PROVIDER") or "serper").strip().lower()
    timeout_seconds = int(os.getenv("ENRICHMENT_TIMEOUT_SECONDS", "15"))
    if provider == "serper":
        return SerperDomainResolver(timeout_seconds=timeout_seconds)
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


def _expand_search_characters_unicode(value: str) -> str:
    replacements = {
        "\u00c4": "Ae",
        "\u00d6": "Oe",
        "\u00dc": "Ue",
        "\u00e4": "ae",
        "\u00f6": "oe",
        "\u00fc": "ue",
        "\u00df": "ss",
        "\u00c3\u00a4": "ae",
        "\u00c3\u00b6": "oe",
        "\u00c3\u00bc": "ue",
        "\u00c3\u009f": "ss",
        "\u00c3\u201e": "Ae",
        "\u00c3\u2013": "Oe",
        "\u00c3\u0153": "Ue",
        "\u00c3\u0178": "ss",
    }
    expanded = value
    for source, target in replacements.items():
        expanded = expanded.replace(source, target)
    return expanded


def _normalize_company_name(value: str) -> str:
    cleaned = _expand_search_characters_unicode(value).strip().lower()
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


def _serper_search_queries(*, search_name: str, location: str | None) -> list[str]:
    queries = [f'"{search_name}" official site']
    if location:
        queries.append(f'"{search_name}" official site {location.strip()}')
    else:
        queries.append(f'"{search_name}" company')
    queries.append(f'"{search_name}" about')

    deduped: list[str] = []
    seen: set[str] = set()
    for query in queries:
        normalized = " ".join(query.split()).strip()
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        deduped.append(normalized)
    return deduped[:3]


def _serper_request_delay_seconds() -> float:
    return 1.0


def _serper_gl_from_location(location: str | None) -> str:
    location_norm = _normalize_company_name(location or "")
    if "australia" in location_norm:
        return "au"
    if any(token in location_norm for token in {"germany", "deutschland"}):
        return "de"
    if any(token in location_norm for token in {"united kingdom", "uk", "england", "scotland"}):
        return "uk"
    if "india" in location_norm:
        return "in"
    if "canada" in location_norm:
        return "ca"
    return "us"


def _serper_results_to_html_stub(organic_results: list[Any]) -> str:
    links: list[str] = []
    for item in organic_results:
        if not isinstance(item, dict):
            continue
        link = _clean_string(item.get("link") or item.get("url"))
        title = _clean_string(item.get("title")) or ""
        snippet = _clean_string(item.get("snippet") or item.get("description")) or ""
        if not link:
            continue
        links.append(
            f'<a href="{link}"><span>{title}</span></a><div>{snippet}</div>'
        )
    return "<html><body>" + "".join(links) + "</body></html>"


def _extract_serper_result_candidates(html: str) -> list[dict[str, str]]:
    soup = BeautifulSoup(html, "lxml")
    candidates: list[dict[str, str]] = []
    seen_urls: set[str] = set()

    for anchor in soup.select("a[href]"):
        href = (anchor.get("href") or "").strip()
        resolved_url = _serper_result_target_url(href)
        if not resolved_url or resolved_url in seen_urls:
            continue
        title = " ".join(anchor.get_text(" ", strip=True).split())
        snippet = ""
        parent = anchor.find_parent(["div", "article"])
        if parent is not None:
            snippet = " ".join(parent.get_text(" ", strip=True).split())
        seen_urls.add(resolved_url)
        candidates.append(
            {
                "url": resolved_url,
                "title": title,
                "snippet": snippet,
            }
        )
    return candidates


def _serper_result_target_url(href: str) -> str | None:
    if not href:
        return None
    if href.startswith("/url?"):
        parsed = urlparse(href)
        q = parse_qs(parsed.query).get("q", [])
        if q:
            return q[0]
        return None
    if href.startswith("http://") or href.startswith("https://"):
        return href
    return None


def _candidate_result_score(company_name: str, domain: str, result: dict[str, Any]) -> float:
    title = _clean_string(result.get("title")) or ""
    snippet = _clean_string(result.get("snippet")) or ""
    title_score = _name_similarity(company_name, title)
    snippet_score = _name_similarity(company_name, snippet)
    domain_score = _domain_name_similarity(company_name, domain)
    return round((0.5 * domain_score) + (0.3 * title_score) + (0.2 * snippet_score), 4)


def _validate_candidate_domain(
    client: httpx.Client,
    *,
    company_name: str,
    domain: str,
    preferred_url: str | None,
) -> dict[str, Any] | None:
    candidate_urls = []
    preferred_domain = canonicalize_domain(preferred_url)
    if preferred_url and preferred_domain == domain:
        candidate_urls.append(preferred_url)
    candidate_urls.extend(
        [
            f"https://{domain}",
            f"https://{domain}/about",
            f"https://{domain}/company",
            f"https://{domain}/careers",
            f"https://{domain}/contact",
        ]
    )

    seen: set[str] = set()
    best_match: dict[str, Any] | None = None
    for url in candidate_urls:
        if url in seen:
            continue
        seen.add(url)
        try:
            response = client.get(url)
        except Exception:
            continue
        if response.status_code >= 400 or not response.text:
            continue
        soup = BeautifulSoup(response.text, "lxml")
        title = " ".join(soup.title.get_text(" ", strip=True).split()) if soup.title else ""
        body_text = " ".join(soup.get_text(" ", strip=True).split())
        if not body_text and not title:
            continue
        sampled_text = body_text[:4000]
        title_score = _name_similarity(company_name, title)
        text_score = _name_similarity(company_name, sampled_text)
        domain_score = _domain_name_similarity(company_name, domain)
        name_score = max(title_score, text_score, domain_score)
        if name_score < 0.78:
            continue
        current = {
            "validated_url": str(response.url),
            "name_score": round(name_score, 4),
        }
        if best_match is None or current["name_score"] > best_match["name_score"]:
            best_match = current
    return best_match


def _domain_name_similarity(company_name: str, domain: str) -> float:
    root = domain.split(".", 1)[0]
    normalized_root = " ".join(re.findall(r"[a-z0-9]+", root.lower()))
    if not normalized_root:
        return 0.0
    return _name_similarity(company_name, normalized_root)
def _clean_string(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    cleaned = " ".join(value.split()).strip()
    return cleaned or None


def _env_flag(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}
