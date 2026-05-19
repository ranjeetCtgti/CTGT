from __future__ import annotations

from urllib.parse import urlencode, urljoin

from bs4 import BeautifulSoup, Tag
from loguru import logger

from config import ENGLISH_QUERIES, GEO_CODE_BY_COUNTRY, GERMAN_QUERIES, INDEED_LOCATIONS
from models.schema import RawJobPosting
from scrapers.scrapedo_client import ScrapeDoClient, ScrapeRequest


INDEED_HOST_BY_LOCATION = {
    "India": "https://in.indeed.com",
    "Germany": "https://de.indeed.com",
    "Canada": "https://ca.indeed.com",
    "United States": "https://www.indeed.com",
}

CARD_SELECTORS = [
    "div.job_seen_beacon",
    "div.slider_container div[data-testid='slider_item']",
    "td.resultContent",
]
TITLE_SELECTORS = [
    "h2.jobTitle a span",
    "[data-testid='job-title']",
    "h2 a",
]
COMPANY_SELECTORS = [
    "[data-testid='company-name']",
    "span.companyName",
    "div.company_location span",
]
LOCATION_SELECTORS = [
    "[data-testid='text-location']",
    "div.company_location div",
    "div.company_location span",
]
SNIPPET_SELECTORS = [
    "[data-testid='job-snippet']",
    "div.job-snippet",
    "ul",
]
DATE_SELECTORS = [
    "span.date",
    "span[data-testid='myJobsStateDate']",
]
LINK_SELECTORS = [
    "h2.jobTitle a",
    "a.jcs-JobTitle",
    "a",
]
WAIT_SELECTOR = "div.job_seen_beacon"


def build_search_url(query: str, location: str) -> str:
    base_url = INDEED_HOST_BY_LOCATION[location]
    params = {
        "q": query,
        "fromage": "7",
    }
    if location != "Germany":
        params["l"] = location
    return f"{base_url}/jobs?{urlencode(params)}"


def build_search_plan(max_queries: int | None = None) -> list[tuple[str, str]]:
    plan: list[tuple[str, str]] = []
    for location in INDEED_LOCATIONS:
        queries = GERMAN_QUERIES if location == "Germany" else ENGLISH_QUERIES
        for query in queries:
            plan.append((query, location))
    if max_queries is not None:
        return plan[:max_queries]
    return plan


def scrape_indeed(
    client: ScrapeDoClient,
    max_queries: int | None = None,
) -> list[RawJobPosting]:
    postings: list[RawJobPosting] = []

    for query, location in build_search_plan(max_queries=max_queries):
        target_url = build_search_url(query, location)
        geo_code = GEO_CODE_BY_COUNTRY.get(location.lower())
        response = client.scrape(
            ScrapeRequest(
                source="indeed",
                query=query,
                target_url=target_url,
                render=False,
                geo_code=geo_code,
                wait_selector=WAIT_SELECTOR,
            )
        )
        if not response.ok or not response.html:
            response = client.scrape(
                ScrapeRequest(
                    source="indeed",
                    query=query,
                    target_url=target_url,
                    render=True,
                    geo_code=geo_code,
                    wait_selector=WAIT_SELECTOR,
                )
            )
        if not response.ok or not response.html:
            continue
        parsed_postings = parse_search_results(response.html, query, location)
        if parsed_postings:
            postings.extend(parsed_postings)
            continue

        logger.warning(
            "indeed render=false returned 0 cards, retrying with render=true query={} location={}",
            query,
            location,
        )
        response = client.scrape(
            ScrapeRequest(
                source="indeed",
                query=query,
                target_url=target_url,
                render=True,
                geo_code=geo_code,
                wait_selector=WAIT_SELECTOR,
            )
        )
        if not response.ok or not response.html:
            continue
        postings.extend(parse_search_results(response.html, query, location))

    return postings


def parse_search_results(html: str, query: str, location: str) -> list[RawJobPosting]:
    soup = BeautifulSoup(html, "lxml")
    cards = _find_cards(soup)
    if not cards:
        logger.warning("indeed parser found 0 cards for query={} location={}", query, location)
        return []

    parsed: list[RawJobPosting] = []
    seen_urls: set[str] = set()

    for card in cards:
        posting = _parse_card(card, query, location)
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


def _parse_card(card: Tag, query: str, location: str) -> RawJobPosting | None:
    title = _extract_text(card, TITLE_SELECTORS)
    company_name = _extract_text(card, COMPANY_SELECTORS)
    card_location = _extract_text(card, LOCATION_SELECTORS)
    snippet = _extract_text(card, SNIPPET_SELECTORS)
    posted_date = _extract_text(card, DATE_SELECTORS)
    job_url = _extract_href(card, LINK_SELECTORS)

    if not title or not company_name or not job_url:
        return None

    return RawJobPosting(
        source="indeed",
        query=query,
        title=title,
        company_name=company_name,
        location=card_location or location,
        snippet=snippet,
        job_url=urljoin(INDEED_HOST_BY_LOCATION[location], job_url),
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


def _extract_href(card: Tag, selectors: list[str]) -> str | None:
    for selector in selectors:
        node = card.select_one(selector)
        if not node:
            continue
        href = node.get("href")
        if href:
            return href
    return None
