from __future__ import annotations

from urllib.parse import urlencode, urljoin

from bs4 import BeautifulSoup, Tag
from loguru import logger

from config import ENGLISH_QUERIES, GEO_CODE_BY_COUNTRY, GERMAN_QUERIES, LINKEDIN_LOCATIONS
from models.schema import RawJobPosting
from scrapers.scrapedo_client import ScrapeDoClient, ScrapeRequest


LINKEDIN_BASE_URL = "https://www.linkedin.com"
LINKEDIN_SEARCH_URL = f"{LINKEDIN_BASE_URL}/jobs/search/"
LINKEDIN_WAIT_SELECTOR = ".base-card"
LINKEDIN_GERMANY_LOCATION = "Germany"

CARD_SELECTORS = [
    "li:has(.base-card)",
    "div.base-card",
    "li .base-search-card",
]
TITLE_SELECTORS = [
    "h3.base-search-card__title",
    "a.base-card__full-link span[aria-hidden='true']",
    "h3",
]
COMPANY_SELECTORS = [
    "h4.base-search-card__subtitle",
    "a.hidden-nested-link",
    "h4",
]
LOCATION_SELECTORS = [
    "span.job-search-card__location",
    "span.base-search-card__metadata",
    "span",
]
SNIPPET_SELECTORS = [
    "div.base-search-card__metadata",
    "p.job-search-card__snippet",
    ".job-search-card__snippet",
]
DATE_SELECTORS = [
    "time",
    "time.job-search-card__listdate",
]
LINK_SELECTORS = [
    "a.base-card__full-link",
    "a.hidden-nested-link",
    "a",
]


def build_search_url(query: str, location: str) -> str:
    params = {
        "keywords": query,
        "location": location,
        "f_TPR": "r86400",
    }
    return f"{LINKEDIN_SEARCH_URL}?{urlencode(params)}"


def build_search_plan(max_queries: int | None = None) -> list[tuple[str, str]]:
    english_pairs = [(query, location) for query in ENGLISH_QUERIES for location in LINKEDIN_LOCATIONS]
    german_pairs = [(query, LINKEDIN_GERMANY_LOCATION) for query in GERMAN_QUERIES]
    pairs = english_pairs + german_pairs
    if max_queries is not None:
        return pairs[:max_queries]
    return pairs


def scrape_linkedin(
    client: ScrapeDoClient,
    max_queries: int | None = None,
) -> list[RawJobPosting]:
    postings: list[RawJobPosting] = []

    for query, location in build_search_plan(max_queries=max_queries):
        target_url = build_search_url(query, location)
        geo_code = GEO_CODE_BY_COUNTRY.get(location.lower())
        response = client.scrape(
            ScrapeRequest(
                source="linkedin",
                query=query,
                target_url=target_url,
                render=True,
                super_proxy=True,
                geo_code=geo_code,
                wait_selector=LINKEDIN_WAIT_SELECTOR,
            )
        )
        if not response.ok or not response.html:
            continue
        postings.extend(parse_search_results(response.html, query))

    return postings


def parse_search_results(html: str, query: str) -> list[RawJobPosting]:
    soup = BeautifulSoup(html, "lxml")
    cards = _find_cards(soup)
    if not cards:
        logger.warning("linkedin parser found 0 cards for query={}", query)
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
        source="linkedin",
        query=query,
        title=title,
        company_name=company_name,
        location=location,
        snippet=snippet,
        job_url=urljoin(LINKEDIN_BASE_URL, job_url),
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
        text_value = " ".join(node.get_text(" ", strip=True).split())
        if text_value:
            return text_value
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
