from __future__ import annotations

import html
import os
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from email.utils import parsedate_to_datetime
from urllib.parse import parse_qs, urlparse

import httpx
from bs4 import BeautifulSoup
from loguru import logger

from config import DEFAULT_REQUEST_TIMEOUT_SECONDS, NEWS_RSS_DESCRIPTION_MAX_CHARS, NEWS_RSS_FEEDS
from models.schema import RawSignalDocument


@dataclass(slots=True)
class CollectorResult:
    postings: list[RawSignalDocument]
    pages_scraped: int


def scrape_news(_: object | None = None, max_queries: int | None = None) -> CollectorResult:
    feed_urls = NEWS_RSS_FEEDS[:max_queries] if max_queries is not None else NEWS_RSS_FEEDS
    timeout_seconds = int(os.getenv("REQUEST_TIMEOUT_SECONDS", DEFAULT_REQUEST_TIMEOUT_SECONDS))
    postings: list[RawSignalDocument] = []
    seen_urls: set[str] = set()
    pages_scraped = 0

    with httpx.Client(timeout=timeout_seconds, follow_redirects=True) as client:
        for feed_url in feed_urls:
            try:
                response = client.get(feed_url, headers={"User-Agent": "CTGT-NewsBot/1.0"})
                response.raise_for_status()
            except Exception as exc:
                logger.warning("news rss fetch failed feed={} error={}", feed_url, exc)
                continue

            pages_scraped += 1
            for document in parse_rss_feed(response.text, feed_url=feed_url):
                key = str(document.source_url)
                if key in seen_urls:
                    continue
                seen_urls.add(key)
                postings.append(document)

    return CollectorResult(postings=postings, pages_scraped=pages_scraped)


def parse_rss_feed(xml_text: str, feed_url: str) -> list[RawSignalDocument]:
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError as exc:
        logger.warning("news rss parse failed feed={} error={}", feed_url, exc)
        return []

    documents: list[RawSignalDocument] = []
    for item in root.findall(".//item"):
        title = _text(item.find("title"))
        link = _text(item.find("link"))
        description = _clean_html(_text(item.find("description")))
        pub_date = _normalize_pub_date(_text(item.find("pubDate")))
        source_name = _text(item.find("source")) or _feed_label(feed_url)

        if not title or not link:
            continue

        text_parts = [title, description, source_name]
        full_text = " | ".join(part for part in text_parts if part)
        try:
            documents.append(
                RawSignalDocument(
                    source="news",
                    signal_type="news",
                    query=_feed_label(feed_url),
                    title=title,
                    company_name=None,
                    location=None,
                    snippet=description[:500] if description else None,
                    description=full_text[:NEWS_RSS_DESCRIPTION_MAX_CHARS],
                    source_url=link,
                    published_date=pub_date,
                )
            )
        except Exception as exc:
            logger.warning("news item validation failed link={} error={}", link, exc)

    return documents


def _feed_label(feed_url: str) -> str:
    parsed = urlparse(feed_url)
    query = parse_qs(parsed.query).get("q", [""])[0]
    return query.replace("+", " ").strip() or feed_url


def _clean_html(value: str | None) -> str | None:
    if value is None:
        return None
    text = BeautifulSoup(html.unescape(value), "lxml").get_text(" ", strip=True)
    cleaned = " ".join(text.split()).strip()
    return cleaned or None


def _normalize_pub_date(value: str | None) -> str | None:
    if not value:
        return None
    try:
        return parsedate_to_datetime(value).isoformat()
    except Exception:
        return value


def _text(node: ET.Element | None) -> str | None:
    if node is None or node.text is None:
        return None
    cleaned = " ".join(node.text.split()).strip()
    return cleaned or None
