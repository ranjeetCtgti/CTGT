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
    CAREER_PAGE_MAX_TEXT_CHARS,
    CAREER_PAGE_TARGETS_CSV,
    CAREER_PAGE_USER_AGENTS,
    DEFAULT_REQUEST_TIMEOUT_SECONDS,
)
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
    postings: list[RawSignalDocument] = []
    pages_scraped = 0

    with httpx.Client(timeout=timeout_seconds, follow_redirects=True) as client:
        robots_cache: dict[str, RobotFileParser | None] = {}
        for target in targets:
            if not _allowed_by_robots(client, target.careers_url, robots_cache):
                logger.info("career_page skipped by robots company={} url={}", target.company_name, target.careers_url)
                continue

            headers = {"User-Agent": random.choice(CAREER_PAGE_USER_AGENTS)}
            try:
                response = client.get(target.careers_url, headers=headers)
                response.raise_for_status()
            except Exception as exc:
                logger.warning(
                    "career_page fetch failed company={} url={} error={}",
                    target.company_name,
                    target.careers_url,
                    exc,
                )
                continue

            pages_scraped += 1
            document = parse_career_page(
                html=response.text,
                target=target,
                final_url=str(response.url),
            )
            if document is None:
                continue
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

    return RawSignalDocument(
        source="career_page",
        signal_type="career_page",
        query=f"{target.company_name} career page",
        title=page_title or f"{target.company_name} careers",
        company_name=target.company_name,
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


def _clean(value: str | None) -> str | None:
    if value is None:
        return None
    cleaned = " ".join(str(value).split()).strip()
    return cleaned or None
