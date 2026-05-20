from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import date, datetime
from typing import Any

from loguru import logger

from config import ENGLISH_QUERIES, GERMAN_QUERIES, GOOGLE_LOCATIONS, INDEED_LOCATIONS, LINKEDIN_LOCATIONS
from models.schema import RawJobPosting

try:
    import pandas as pd
    from jobspy import scrape_jobs
except ImportError:  # pragma: no cover
    pd = None
    scrape_jobs = None


JOBSPY_SUPPORTED_SOURCES = ("linkedin", "indeed", "google")
JOBSPY_RESULTS_WANTED = 20
JOBSPY_HOURS_OLD = 72

# Maximum characters of full description to store and send to Gemini.
# Full job descriptions average 2,000-5,000 chars. 5,000 gives Gemini enough
# context to distinguish manufacturers from consulting firms, detect migration
# signals, and identify industry — without blowing the token budget per batch.
_DESCRIPTION_MAX_CHARS = 5000


@dataclass(slots=True)
class CollectorResult:
    postings: list[RawJobPosting]
    pages_scraped: int


def build_search_plan(source: str, max_queries: int | None = None) -> list[tuple[str, str]]:
    if source not in JOBSPY_SUPPORTED_SOURCES:
        raise ValueError(f"Unsupported JobSpy source: {source}")

    plan: list[tuple[str, str]] = []
    if source == "linkedin":
        for location in LINKEDIN_LOCATIONS:
            queries = GERMAN_QUERIES if location == "Germany" else ENGLISH_QUERIES
            for query in queries:
                plan.append((query, location))
    else:
        locations = INDEED_LOCATIONS if source == "indeed" else GOOGLE_LOCATIONS
        for location in locations:
            queries = GERMAN_QUERIES if location == "Germany" else ENGLISH_QUERIES
            for query in queries:
                plan.append((query, location))

    if max_queries is not None:
        return plan[:max_queries]
    return plan


def scrape_linkedin(_: Any | None = None, max_queries: int | None = None) -> CollectorResult:
    return collect_jobspy_jobs("linkedin", max_queries=max_queries)


def scrape_indeed(_: Any | None = None, max_queries: int | None = None) -> CollectorResult:
    return collect_jobspy_jobs("indeed", max_queries=max_queries)


def scrape_google(_: Any | None = None, max_queries: int | None = None) -> CollectorResult:
    return collect_jobspy_jobs("google", max_queries=max_queries)


def collect_jobspy_jobs(source: str, max_queries: int | None = None) -> CollectorResult:
    _ensure_jobspy_available()

    postings: list[RawJobPosting] = []
    seen_urls: set[str] = set()
    pages_scraped = 0
    results_wanted = int(os.getenv("JOBSPY_RESULTS_WANTED", JOBSPY_RESULTS_WANTED))
    hours_old = int(os.getenv("JOBSPY_HOURS_OLD", JOBSPY_HOURS_OLD))

    for query, location in build_search_plan(source, max_queries=max_queries):
        logger.info("jobspy request source={} query={} location={}", source, query, location)
        try:
            frame = scrape_jobs(
                site_name=[source],
                search_term=query,
                google_search_term=query,
                location=location,
                results_wanted=results_wanted,
                hours_old=hours_old,
                country_indeed=location,
                # LinkedIn requires an extra page load per job to get the full
                # description. Worth the extra ~30s per query — without it Gemini
                # cannot distinguish manufacturers from consulting firms.
                linkedin_fetch_description=(source == "linkedin"),
            )
        except Exception as exc:
            logger.warning(
                "jobspy request failed source={} query={} location={} error={}",
                source, query, location, exc,
            )
            continue

        pages_scraped += 1
        if frame is None or frame.empty:
            logger.warning(
                "jobspy returned no rows source={} query={} location={}",
                source, query, location,
            )
            continue

        parsed_count = 0
        for _, row in frame.iterrows():
            posting = _normalize_row(row, source=source, query=query, fallback_location=location)
            if posting is None:
                continue
            job_url = str(posting.job_url)
            if job_url in seen_urls:
                continue
            seen_urls.add(job_url)
            postings.append(posting)
            parsed_count += 1

        logger.info(
            "jobspy success source={} query={} location={} rows={} parsed={}",
            source, query, location, len(frame.index), parsed_count,
        )

    return CollectorResult(postings=postings, pages_scraped=pages_scraped)


def _ensure_jobspy_available() -> None:
    if scrape_jobs is None or pd is None:
        raise RuntimeError("python-jobspy is not installed; run `pip install -r requirements.txt`")


def _normalize_row(
    row: Any,
    source: str,
    query: str,
    fallback_location: str,
) -> RawJobPosting | None:
    site = _clean_value(row.get("site"))
    if site and site.lower() != source:
        return None

    title = _clean_value(row.get("title"))
    company_name = _clean_value(row.get("company")) or _clean_value(row.get("company_name"))
    location = _clean_value(row.get("location")) or fallback_location
    job_url = _clean_value(row.get("job_url_direct")) or _clean_value(row.get("job_url"))
    posted_date = _format_posted_date(row.get("date_posted"))

    # JobSpy returns the full job description in the "description" column.
    # We store it in both fields:
    #   description — the full text (up to _DESCRIPTION_MAX_CHARS), used by
    #                 the NLP layer as the primary signal extraction input.
    #   snippet     — a short excerpt for display/logging (first 300 chars).
    raw_description = _clean_value(row.get("description"))
    description = _truncate(raw_description, _DESCRIPTION_MAX_CHARS)
    snippet = _truncate(raw_description, 300)

    if not title or not company_name or not job_url:
        logger.warning(
            "jobspy row skipped source={} query={} missing_fields={}{}{}",
            source, query,
            " title" if not title else "",
            " company" if not company_name else "",
            " job_url" if not job_url else "",
        )
        return None

    try:
        return RawJobPosting(
            source=source,
            query=query,
            title=title,
            company_name=company_name,
            location=location,
            snippet=snippet,
            description=description,
            job_url=job_url,
            posted_date=posted_date,
        )
    except Exception as exc:
        logger.warning(
            "jobspy row validation failed source={} query={} error={}", source, query, exc,
        )
        return None


def _clean_value(value: Any) -> str | None:
    if value is None:
        return None
    if pd.isna(value):
        return None
    cleaned = " ".join(str(value).split()).strip()
    return cleaned or None


def _truncate(value: str | None, max_chars: int) -> str | None:
    if value is None:
        return None
    return value[:max_chars] or None


def _format_posted_date(value: Any) -> str | None:
    if value is None or pd.isna(value):
        return None
    if isinstance(value, datetime):
        return value.date().isoformat()
    if isinstance(value, date):
        return value.isoformat()
    iso_method = getattr(value, "isoformat", None)
    if callable(iso_method):
        try:
            return iso_method()
        except TypeError:
            pass
    return _clean_value(value)
