from __future__ import annotations

import csv
import os
import random
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser

import httpx
from bs4 import BeautifulSoup
from loguru import logger

from config import (
    CAREER_PAGE_MAX_PAGES_PER_TARGET,
    CAREER_PAGE_MAX_TEXT_CHARS,
    CAREER_PAGE_TARGETS_CSV,
    CAREER_PAGE_USER_AGENTS,
    DEFAULT_REQUEST_TIMEOUT_SECONDS,
)
from industry_filter import matching_excluded_industry
from models.schema import RawSignalDocument


TEXT_SELECTORS = [
    "h1",
    "h2",
    "h3",
    "h4",
    "p",
    "li",
    "div",
]


@dataclass(slots=True)
class CareerPageTarget:
    company_name: str
    domain: str
    careers_url: str
    country: str
    industry: str


@dataclass(slots=True)
class CollectorResult:
    postings: list[RawSignalDocument]
    pages_scraped: int


def scrape_career_pages(_: object | None = None, max_queries: int | None = None) -> CollectorResult:
    targets = load_targets()
    if max_queries is not None:
        targets = targets[:max_queries]

    timeout_seconds = int(os.getenv("REQUEST_TIMEOUT_SECONDS", DEFAULT_REQUEST_TIMEOUT_SECONDS))
    max_pages_per_target = int(
        os.getenv("CAREER_PAGE_MAX_PAGES_PER_TARGET", CAREER_PAGE_MAX_PAGES_PER_TARGET)
    )
    postings: list[RawSignalDocument] = []
    pages_scraped = 0
    seen_urls: set[str] = set()

    with httpx.Client(timeout=timeout_seconds, follow_redirects=True) as client:
        robots_cache: dict[str, RobotFileParser | None] = {}
        for target in targets:
            target_pages_scraped, target_postings = _crawl_target(
                client,
                target,
                robots_cache,
                max_pages=max_pages_per_target,
            )
            pages_scraped += target_pages_scraped
            for document in target_postings:
                key = str(document.source_url)
                if key in seen_urls:
                    continue
                seen_urls.add(key)
                postings.append(document)

    return CollectorResult(postings=postings, pages_scraped=pages_scraped)


def load_targets(path: Path | None = None) -> list[CareerPageTarget]:
    configured_path = os.getenv("CAREER_PAGE_TARGETS_CSV")
    if path is not None:
        csv_path = path
    elif configured_path:
        csv_path = Path(configured_path)
    else:
        csv_path = CAREER_PAGE_TARGETS_CSV
    if not csv_path.exists():
        logger.warning("career page target csv not found path={}", csv_path)
        return []

    targets: list[CareerPageTarget] = []
    with csv_path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            company_name = _clean(row.get("company_name"))
            domain = _clean(row.get("domain"))
            careers_url = _clean(row.get("careers_url"))
            country = _clean(row.get("country"))
            industry = _clean(row.get("industry"))
            if not all([company_name, domain, careers_url, country, industry]):
                continue
            excluded_industry = matching_excluded_industry(industry)
            if excluded_industry:
                logger.info(
                    "career_page target excluded company={} industry={} matched={}",
                    company_name,
                    industry,
                    excluded_industry,
                )
                continue
            targets.append(
                CareerPageTarget(
                    company_name=company_name,
                    domain=domain,
                    careers_url=careers_url,
                    country=country,
                    industry=industry,
                )
            )
    return targets


def parse_career_page(html: str, target: CareerPageTarget, final_url: str) -> RawSignalDocument | None:
    soup = BeautifulSoup(html, "lxml")
    page_title = _clean(soup.title.get_text(" ", strip=True) if soup.title else None)
    full_text = _extract_page_text(soup)
    if not full_text:
        logger.warning("career_page parser found no text company={} url={}", target.company_name, final_url)
        return None

    parsed_url = urlparse(final_url)
    path_hint = parsed_url.path.rstrip("/").split("/")[-1].replace("-", " ").replace("_", " ").strip()
    title = page_title or f"{target.company_name} careers"
    if path_hint and path_hint.lower() not in {"careers", "career"}:
        title = f"{title} - {path_hint.title()}"

    return RawSignalDocument(
        source="career_page",
        signal_type="career_page",
        query=f"{target.company_name} career page",
        title=title,
        company_name=target.company_name,
        company_industry=target.industry,
        location=target.country,
        snippet=full_text[:500],
        description=full_text,
        source_url=final_url,
    )


def _extract_page_text(soup: BeautifulSoup) -> str:
    seen: set[str] = set()
    parts: list[str] = []

    for selector in TEXT_SELECTORS:
        for node in soup.select(selector):
            text = _clean(node.get_text(" ", strip=True))
            if not text or text in seen:
                continue
            seen.add(text)
            parts.append(text)

    return " | ".join(parts)[:CAREER_PAGE_MAX_TEXT_CHARS]


def _crawl_target(
    client: httpx.Client,
    target: CareerPageTarget,
    robots_cache: dict[str, RobotFileParser | None],
    max_pages: int,
) -> tuple[int, list[RawSignalDocument]]:
    pages_scraped = 0
    postings: list[RawSignalDocument] = []
    headers = {"User-Agent": random.choice(CAREER_PAGE_USER_AGENTS)}
    queue: list[str] = [target.careers_url]
    seen_urls: set[str] = set()

    while queue and pages_scraped < max_pages:
        url = queue.pop(0)
        normalized_url = _normalize_url(url)
        if normalized_url in seen_urls:
            continue
        seen_urls.add(normalized_url)

        if not _allowed_by_robots(client, url, robots_cache):
            logger.info("career_page skipped by robots company={} url={}", target.company_name, url)
            continue

        try:
            response = client.get(url, headers=headers)
            response.raise_for_status()
        except Exception as exc:
            logger.warning(
                "career_page fetch failed company={} url={} error={}",
                target.company_name,
                url,
                exc,
            )
            continue

        pages_scraped += 1
        final_url = str(response.url)
        normalized_final_url = _normalize_url(final_url)
        seen_urls.add(normalized_final_url)
        soup = BeautifulSoup(response.text, "lxml")

        document = parse_career_page(
            html=response.text,
            target=target,
            final_url=final_url,
        )
        if document is not None:
            postings.append(document)

        for next_url in _extract_candidate_links(soup, final_url, target):
            normalized_next_url = _normalize_url(next_url)
            if normalized_next_url in seen_urls:
                continue
            if next_url in queue:
                continue
            queue.append(next_url)

    return pages_scraped, postings


def _extract_candidate_links(soup: BeautifulSoup, base_url: str, target: CareerPageTarget) -> list[str]:
    candidates: list[str] = []
    seen: set[str] = set()

    for link in soup.select("a[href]"):
        href = _clean(link.get("href"))
        if not href:
            continue
        absolute = urljoin(base_url, href)
        if not _url_matches_target_domain(absolute, target.domain):
            continue
        if not _looks_like_pagination_link(absolute, base_url, link.get_text(" ", strip=True)):
            continue

        normalized = _normalize_url(absolute)
        if normalized in seen:
            continue
        seen.add(normalized)
        candidates.append(absolute)

    return candidates


def _allowed_by_robots(
    client: httpx.Client,
    url: str,
    cache: dict[str, RobotFileParser | None],
) -> bool:
    parsed = urlparse(url)
    base = f"{parsed.scheme}://{parsed.netloc}"
    parser = cache.get(base)
    if parser is None and base not in cache:
        robots_url = urljoin(base, "/robots.txt")
        parser = RobotFileParser()
        try:
            response = client.get(robots_url, headers={"User-Agent": CAREER_PAGE_USER_AGENTS[0]})
            if response.status_code >= 400 or not response.text.strip():
                cache[base] = None
                return True
            parser.parse(response.text.splitlines())
            cache[base] = parser
        except Exception:
            cache[base] = None
            return True

    parser = cache.get(base)
    if parser is None:
        return True
    return parser.can_fetch("*", url)


def _looks_like_pagination_link(url: str, base_url: str, anchor_text: str) -> bool:
    parsed = urlparse(url)
    base_parsed = urlparse(base_url)
    anchor = anchor_text.strip().lower()
    query = parsed.query.lower()
    path = parsed.path.lower()

    if "/page/" in path:
        return True
    if parsed.path.rstrip("/") != base_parsed.path.rstrip("/") and not query:
        return False

    if anchor in {"next", "next page", "older", "more", ">>", ">", "2", "3", "4", "5"}:
        return True
    if "page=" in query or "paged=" in query or "start=" in query or "offset=" in query:
        return True
    return False


def _url_matches_target_domain(url: str, target_domain: str) -> bool:
    hostname = (urlparse(url).hostname or "").lower()
    domain = target_domain.lower().removeprefix("www.")
    host = hostname.removeprefix("www.")
    return host == domain or host.endswith(f".{domain}")


def _normalize_url(url: str) -> str:
    parsed = urlparse(url)
    path = parsed.path.rstrip("/") or "/"
    normalized = f"{parsed.scheme}://{parsed.netloc}{path}"
    if parsed.query:
        normalized = f"{normalized}?{parsed.query}"
    return normalized


def _clean(value: str | None) -> str | None:
    if value is None:
        return None
    cleaned = " ".join(str(value).split()).strip()
    return cleaned or None
