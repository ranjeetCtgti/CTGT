from __future__ import annotations

from urllib.parse import urlencode, urljoin

from bs4 import BeautifulSoup, Tag
from loguru import logger

from config import GEO_CODE_BY_COUNTRY, STEPSTONE_GERMAN_QUERIES
from models.schema import RawJobPosting
from scrapers.scrapedo_client import ScrapeDoClient, ScrapeRequest


STEPSTONE_BASE_URL = "https://www.stepstone.de"
STEPSTONE_SEARCH_URL = f"{STEPSTONE_BASE_URL}/jobs"
STEPSTONE_LOCATION = "Germany"
WAIT_SELECTOR = "article[data-at='job-item']"

# scrape.do settings for Stepstone
# - render=True always: Stepstone is Cloudflare-protected, render=False always 400
# - force_render=True: prevents the client ever downgrading to render=False
# - timeout_ms=45_000: Cloudflare JS challenge needs ~10 s extra headroom
# - NO extra_headers: scrape.do already sets optimised browser headers automatically;
#   passing Accept-Language ourselves would override their tuned values and risk
#   causing the 400s we were seeing before
_STEPSTONE_TIMEOUT_MS = 45_000

CARD_SELECTORS = [
    "article[data-at='job-item']",
    "article[aria-label]",
    "div[data-at='job-item']",
]
TITLE_SELECTORS = [
    "[data-at='job-item-title']",
    "h2",
    "a[data-at='job-item-title']",
]
COMPANY_SELECTORS = [
    "[data-at='job-item-company-name']",
    "[data-testid='company-name']",
    "span",
]
LOCATION_SELECTORS = [
    "[data-at='job-item-location']",
    "[data-testid='job-item-location']",
    "span",
]
SNIPPET_SELECTORS = [
    "[data-at='job-item-teaser']",
    "[data-testid='job-item-content']",
    "p",
]
DATE_SELECTORS = [
    "time",
    "[data-at='job-item-date']",
]
LINK_SELECTORS = [
    "a[data-at='job-item-title']",
    "h2 a",
    "a",
]


def build_search_url(query: str) -> str:
    return f"{STEPSTONE_SEARCH_URL}?{urlencode({'q': query})}"


def build_search_plan(max_queries: int | None = None) -> list[str]:
    if max_queries is not None:
        return STEPSTONE_GERMAN_QUERIES[:max_queries]
    return STEPSTONE_GERMAN_QUERIES


def _stepstone_request(query: str, target_url: str) -> ScrapeRequest:
    """Factory for all Stepstone ScrapeRequests.

    Always render=True + force_render=True.
    No extra_headers — scrape.do manages browser headers automatically and
    passing our own Accept-Language was causing the 400 responses.
    """
    return ScrapeRequest(
        source="stepstone",
        query=query,
        target_url=target_url,
        render=True,
        force_render=True,
        super_proxy=False,
        geo_code=GEO_CODE_BY_COUNTRY["germany"],
        wait_selector=WAIT_SELECTOR,
        block_resources=True,
        timeout_ms=_STEPSTONE_TIMEOUT_MS,
        # extra_headers intentionally empty — let scrape.do handle headers
    )


def scrape_stepstone(
    client: ScrapeDoClient,
    max_queries: int | None = None,
) -> list[RawJobPosting]:
    postings: list[RawJobPosting] = []

    for query in build_search_plan(max_queries=max_queries):
        target_url = build_search_url(query)
        response = client.scrape(_stepstone_request(query, target_url))

        if not response.ok or not response.html:
            logger.warning(
                "stepstone scrape failed query={} status={} error={}",
                query,
                response.status_code,
                response.error,
            )
            continue

        parsed_postings = parse_search_results(response.html, query)

        if not parsed_postings:
            logger.warning(
                "stepstone parser found 0 cards query={} html_chars={}",
                query,
                len(response.html),
            )
            continue

        postings.extend(parsed_postings)

    return postings


def parse_search_results(html: str, query: str) -> list[RawJobPosting]:
    soup = BeautifulSoup(html, "lxml")
    cards = _find_cards(soup)
    if not cards:
        logger.warning("stepstone parser found 0 cards for query={}", query)
        return []

    parsed: list[RawJobPosting] = []
    seen_urls: set[str] = set()

    for card in cards:
        posting = _parse_card(card, query)
        if not posting:
            continue
        job_url = str(posting.job_url)
        if job_url in seen_urls:
            continue
        seen_urls.add(job_url)
        parsed.append(posting)

    return parsed


def _find_cards(soup: BeautifulSoup) -> list[Tag]:
    seen: set[int] = set()
    cards: list[Tag] = []
    for selector in CARD_SELECTORS:
        for card in soup.select(selector):
            marker = id(card)
            if marker in seen:
                continue
            seen.add(marker)
            cards.append(card)
    return cards


def _parse_card(card: Tag, query: str) -> RawJobPosting | None:
    title = _extract_text(card, TITLE_SELECTORS)
    company_name = _extract_text(card, COMPANY_SELECTORS)
    location = _extract_text(card, LOCATION_SELECTORS)
    snippet = _extract_text(card, SNIPPET_SELECTORS)
    posted_date = _extract_date(card)
    job_url = _extract_href(card, LINK_SELECTORS)

    if not title or not company_name or not job_url:
        return None

    return RawJobPosting(
        source="stepstone",
        query=query,
        title=title,
        company_name=company_name,
        location=location or STEPSTONE_LOCATION,
        snippet=snippet,
        job_url=urljoin(STEPSTONE_BASE_URL, job_url),
        posted_date=posted_date,
    )


def _extract_text(card: Tag, selectors: list[str]) -> str | None:
    for selector in selectors:
        node = card.select_one(selector)
        if not node:
            continue
        value = " ".join(node.get_text(" ", strip=True).split())
        if value:
            return value
    return None


def _extract_date(card: Tag) -> str | None:
    for selector in DATE_SELECTORS:
        node = card.select_one(selector)
        if not node:
            continue
        datetime_value = node.get("datetime")
        if datetime_value:
            return datetime_value
        value = " ".join(node.get_text(" ", strip=True).split())
        if value:
            return value
    return None


def _extract_href(card: Tag, selectors: list[str]) -> str | None:
    for selector in selectors:
        node = card.select_one(selector)
        if not node:
            continue
        href = node.get("href")
        if href:
            return href
    return None