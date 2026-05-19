from __future__ import annotations

import argparse
import os
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Callable, Iterable

try:
    from dotenv import load_dotenv
except ImportError:
    def load_dotenv() -> bool:
        return False

try:
    from loguru import logger
except ImportError:
    import logging

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("ctgt_pipeline")
    logger.remove = lambda: None  # type: ignore[attr-defined]
    logger.add = lambda *args, **kwargs: None  # type: ignore[attr-defined]

if TYPE_CHECKING:
    from db import Database
    from models.schema import CompanyLead, ExtractedSignal, RawJobPosting
    from scrapers.scrapedo_client import ScrapeDoClient


ScraperFn = Callable[[Any, int | None], list[Any]]
SOURCE_NAMES = ("linkedin", "indeed", "stepstone")
REQUESTS_PER_QUERY_BY_SOURCE = {
    "linkedin": 1,
    "indeed": 3,
    "stepstone": 3,
}
TESTING_MAX_REQUESTS_BY_SOURCE = {
    "linkedin": 3,
    "indeed": 3,
    "stepstone": 3,
}
DEFAULT_PIPELINE_PHASE = "testing"
PLACEHOLDER_ENV_VALUES = {
    "your_scrapedo_api_key",
    "your_gemini_api_key",
    "postgresql+psycopg2://username:password@localhost:5432/ctgt_leads",
}
DEFAULT_SMOKE_TEST_QUERIES = 3


@dataclass(slots=True)
class SourceRunStats:
    pages_scraped: int = 0
    job_cards: int = 0
    prefilter_hits: int = 0
    signals: int = 0
    persisted_signals: int = 0
    duplicate_signals: int = 0
    errors: list[str] = field(default_factory=list)


@dataclass(slots=True)
class PipelineSummary:
    source_stats: dict[str, SourceRunStats] = field(default_factory=dict)
    persisted_companies: dict[str, "CompanyLead"] = field(default_factory=dict)
    total_candidates: int = 0
    dry_run: bool = False
    smoke_test: bool = False
    phase: str = DEFAULT_PIPELINE_PHASE

    def ensure_source(self, source: str) -> SourceRunStats:
        if source not in self.source_stats:
            self.source_stats[source] = SourceRunStats()
        return self.source_stats[source]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="CTGT lead engine Phase 1 pipeline")
    parser.add_argument(
        "--source",
        choices=["all", *SOURCE_NAMES],
        default="all",
        help="Run one source or all sources.",
    )
    parser.add_argument("--dry-run", action="store_true", help="Run extraction without database writes.")
    parser.add_argument("--max-queries", type=int, default=None, help="Limit the number of queries per source.")
    parser.add_argument("--leads", action="store_true", help="Print the current leads table from the database.")
    parser.add_argument(
        "--debug-extraction",
        action="store_true",
        help="Log Gemini extraction decisions for verification during testing.",
    )
    parser.add_argument(
        "--smoke-test",
        action="store_true",
        help="Run a minimal validation pass with dry-run enabled and max-queries defaulting to 1.",
    )
    return parser.parse_args()


def configure_logging() -> None:
    logger.remove()
    logger.add(sys.stderr, level=os.getenv("LOG_LEVEL", "INFO"))


def main() -> int:
    load_dotenv()
    configure_logging()
    args = parse_args()
    normalize_args(args)

    if args.leads:
        try:
            validate_runtime_config(args)
        except ValueError as exc:
            logger.error(str(exc))
            return 1
        return print_leads()

    try:
        validate_runtime_config(args)
        return run_pipeline(args)
    except ValueError as exc:
        logger.error(str(exc))
        return 1
    except Exception as exc:
        logger.error(str(exc))
        return 1


def print_leads(limit: int = 25) -> int:
    try:
        from db import DatabaseError, init_database

        database = init_database()
    except DatabaseError as exc:
        logger.error(str(exc))
        return 1

    leads = database.get_leads(limit=limit)
    if not leads:
        print("No leads found.")
        return 0

    print("Current leads:")
    for lead in leads:
        software = ", ".join(lead.software) or "-"
        sources = ", ".join(lead.signal_sources) or "-"
        print(
            f"- {lead.company_name} | {lead.lead_score.upper()} | score={lead.total_score} | "
            f"signals={lead.signal_count} | software={software} | sources={sources}"
        )
    return 0


def run_pipeline(args: argparse.Namespace) -> int:
    from config import DEFAULT_BATCH_SIZE, DEFAULT_REQUEST_TIMEOUT_SECONDS
    from db import init_database
    from scrapers.scrapedo_client import ScrapeDoClient

    database: Database | None = None
    if not args.dry_run:
        database = init_database()

    timeout_seconds = int(os.getenv("REQUEST_TIMEOUT_SECONDS", DEFAULT_REQUEST_TIMEOUT_SECONDS))
    batch_size = int(os.getenv("BATCH_SIZE", DEFAULT_BATCH_SIZE))
    selected_sources = list(SOURCE_NAMES) if args.source == "all" else [args.source]
    phase = _pipeline_phase()
    max_requests_by_source = build_max_requests_by_source(selected_sources, args.max_queries, phase=phase)
    summary = PipelineSummary(dry_run=args.dry_run, smoke_test=args.smoke_test, phase=phase)

    if args.smoke_test:
        logger.info(
            "running smoke test phase={} source={} max_queries={} dry_run={}",
            phase,
            args.source,
            args.max_queries,
            args.dry_run,
        )
    logger.info(
        "pipeline phase={} source={} max_requests_by_source={} production={}",
        phase,
        args.source,
        max_requests_by_source,
        phase == "production",
    )

    with ScrapeDoClient(
        timeout_seconds=timeout_seconds,
        max_requests_by_source=max_requests_by_source,
    ) as scrape_client:
        postings = collect_postings(scrape_client, selected_sources, args.max_queries, summary)
        filtered_postings = filter_postings(postings, summary)
        signals = extract_signals(
            filtered_postings,
            batch_size=batch_size,
            debug=args.debug_extraction,
            database=database,
        )
        process_signals(signals, summary, database=database)
        print_run_summary(summary, scrape_client.stats())

    return evaluate_run(summary, selected_sources)


def collect_postings(
    scrape_client: "ScrapeDoClient",
    selected_sources: list[str],
    max_queries: int | None,
    summary: PipelineSummary,
) -> list["RawJobPosting"]:
    source_scrapers = get_source_scrapers()
    postings: list[RawJobPosting] = []

    for source in selected_sources:
        stats = summary.ensure_source(source)
        scraper = source_scrapers[source]
        request_count_before = scrape_client.request_count
        try:
            source_postings = scraper(scrape_client, max_queries=max_queries)
        except Exception as exc:
            message = f"{source} scrape failed: {exc}"
            logger.exception(message)
            stats.errors.append(message)
            continue

        stats.pages_scraped += scrape_client.request_count - request_count_before
        stats.job_cards += len(source_postings)
        postings.extend(source_postings)

    return postings


def build_max_requests_by_source(
    selected_sources: list[str],
    max_queries: int | None,
    phase: str,
) -> dict[str, int]:
    from scrapers.indeed import build_search_plan as build_indeed_search_plan
    from scrapers.linkedin import build_search_plan as build_linkedin_search_plan
    from scrapers.stepstone import build_search_plan as build_stepstone_search_plan

    search_plan_builders: dict[str, Callable[[int | None], list[Any]]] = {
        "linkedin": build_linkedin_search_plan,
        "indeed": build_indeed_search_plan,
        "stepstone": build_stepstone_search_plan,
    }
    max_requests_by_source: dict[str, int] = {}

    for source in selected_sources:
        plan_size = len(search_plan_builders[source](max_queries=max_queries))
        planned_requests = plan_size * REQUESTS_PER_QUERY_BY_SOURCE[source]
        if phase != "production":
            planned_requests = min(planned_requests, TESTING_MAX_REQUESTS_BY_SOURCE[source])
        max_requests_by_source[source] = planned_requests

    return max_requests_by_source


def filter_postings(postings: list["RawJobPosting"], summary: PipelineSummary) -> list["RawJobPosting"]:
    from extractors.prefilter import keyword_prefilter

    filtered: list[RawJobPosting] = []
    for posting in postings:
        stats = summary.ensure_source(posting.source)
        if keyword_prefilter(_posting_text(posting)).passed:
            filtered.append(posting)
            stats.prefilter_hits += 1

    summary.total_candidates = len(filtered)
    return filtered


def extract_signals(
    postings: list["RawJobPosting"],
    batch_size: int,
    debug: bool = False,
    database: "Database" | None = None,
) -> list["ExtractedSignal"]:
    from extractors.nlp import GeminiExtractor

    if not postings:
        return []

    processed_source_urls: set[str] = set()
    recently_processed_companies: set[str] = set()
    if database is not None:
        processed_source_urls = database.get_processed_source_urls()
        recently_processed_companies = database.get_recent_company_names(within_hours=24 * 7)

    with GeminiExtractor(batch_size=batch_size, debug=debug) as extractor:
        candidates = extractor.from_job_postings(postings)
        return extractor.extract_signals(
            candidates,
            processed_source_urls=processed_source_urls,
            recently_processed_companies=recently_processed_companies,
        )


def process_signals(
    signals: list["ExtractedSignal"],
    summary: PipelineSummary,
    database: "Database" | None,
) -> None:
    for signal in signals:
        stats = summary.ensure_source(signal.signal_source)
        stats.signals += 1

        if database is None:
            upsert_local_company(summary.persisted_companies, signal)
            continue

        save_result = database.save_signal(signal)
        if not save_result.created:
            stats.duplicate_signals += 1
            continue

        stats.persisted_signals += 1
        lead = database.upsert_company(signal)
        summary.persisted_companies[f"{lead.company_name.lower()}|{lead.company_domain or ''}"] = lead


def print_run_summary(summary: PipelineSummary, scrape_stats: dict[str, int]) -> None:
    lead_counts = Counter(lead.lead_score for lead in summary.persisted_companies.values())

    print("Run complete.")
    print("")
    print(
        f"Mode: {summary.phase.upper()} "
        f"({'production' if summary.phase == 'production' else 'testing / non-production'})"
    )
    if summary.phase != "production":
        print(f"Scrape.do request caps: {TESTING_MAX_REQUESTS_BY_SOURCE}")
        print("")
    print("By source:")
    for source in SOURCE_NAMES:
        if source not in summary.source_stats:
            continue
        stats = summary.source_stats[source]
        print(
            f"  {source.title():<10} pages={stats.pages_scraped} | cards={stats.job_cards} | "
            f"prefilter={stats.prefilter_hits} | signals={stats.signals} | persisted={stats.persisted_signals} | "
            f"duplicates={stats.duplicate_signals}"
        )
        for error in stats.errors:
            print(f"    error: {error}")

    print("")
    print(
        f"NLP extraction: {sum(stat.signals for stat in summary.source_stats.values())} signals "
        f"from {summary.total_candidates} candidates"
    )
    print(
        f"Credits used: {scrape_stats.get('credits_used_total', 0)} "
        f"across {scrape_stats.get('request_count', 0)} scrape.do requests"
    )
    print("")
    print("Lead bands:")
    print(f"  HOT: {lead_counts.get('hot', 0)}")
    print(f"  WARM: {lead_counts.get('warm', 0)}")
    print(f"  COLD: {lead_counts.get('cold', 0)}")

    grouped = _group_leads(summary.persisted_companies.values())
    for band in ["hot", "warm", "cold"]:
        leads = grouped.get(band, [])
        if not leads:
            continue
        print("")
        print(f"{band.upper()} leads:")
        for lead in leads[:10]:
            software = ", ".join(lead.software) or "-"
            sources = ", ".join(lead.signal_sources) or "-"
            print(
                f"  {lead.company_name} | score={lead.total_score} | signals={lead.signal_count} | "
                f"software={software} | sources={sources}"
            )


def evaluate_run(summary: PipelineSummary, selected_sources: list[str]) -> int:
    if not summary.smoke_test:
        return 0

    for source in selected_sources:
        stats = summary.ensure_source(source)
        if stats.errors:
            logger.error("smoke test failed due to source errors source={}", source)
            return 1

    total_pages = sum(summary.ensure_source(source).pages_scraped for source in selected_sources)
    total_cards = sum(summary.ensure_source(source).job_cards for source in selected_sources)
    if total_pages == 0:
        logger.error("smoke test failed because no pages were scraped")
        return 1
    if total_cards == 0:
        logger.error("smoke test failed because no job cards were parsed")
        return 1
    return 0


def company_lead_from_signal(signal: "ExtractedSignal") -> "CompanyLead":
    from models.schema import CompanyLead

    total_score = max(0, int(round(signal.raw_score * signal.confidence)))
    lead_score = "cold"
    if total_score >= 70:
        lead_score = "hot"
    elif total_score >= 35:
        lead_score = "warm"

    return CompanyLead(
        company_name=signal.company_name,
        company_domain=signal.company_domain,
        location=signal.location,
        industry=signal.industry,
        software=list(signal.software),
        signal_sources=[signal.signal_source],
        signal_count=1,
        migration_risk=signal.migration,
        total_score=total_score,
        lead_score=lead_score,
        contacts=[],
        first_seen=signal.detected_at,
        last_updated=signal.detected_at,
    )


def upsert_local_company(
    companies: dict[str, "CompanyLead"],
    signal: "ExtractedSignal",
) -> "CompanyLead":
    key = f"{signal.company_name.lower()}|{signal.company_domain or ''}"
    signal_score = max(0, int(round(signal.raw_score * signal.confidence)))
    existing = companies.get(key)

    if existing is None:
        lead = company_lead_from_signal(signal)
        companies[key] = lead
        return lead

    source_count_before = len(existing.signal_sources)
    existing.signal_count += 1
    existing.software = _merge_unique(existing.software, signal.software)
    existing.signal_sources = _merge_unique(existing.signal_sources, [signal.signal_source])
    existing.migration_risk = existing.migration_risk or signal.migration
    existing.company_domain = existing.company_domain or signal.company_domain
    existing.location = signal.location or existing.location
    existing.industry = signal.industry or existing.industry
    existing.total_score += signal_score
    if existing.signal_count == 2:
        existing.total_score += 15
    elif existing.signal_count >= 3:
        existing.total_score += 20
    if source_count_before < 2 and len(existing.signal_sources) >= 2:
        existing.total_score += 25
    existing.lead_score = _lead_grade(existing.total_score)
    existing.last_updated = signal.detected_at
    companies[key] = existing
    return existing


def _group_leads(leads: Iterable["CompanyLead"]) -> dict[str, list["CompanyLead"]]:
    grouped: dict[str, list[CompanyLead]] = defaultdict(list)
    for lead in leads:
        grouped[lead.lead_score].append(lead)
    for band in grouped:
        grouped[band].sort(key=lambda item: item.total_score, reverse=True)
    return grouped


def _posting_text(posting: "RawJobPosting") -> str:
    return " | ".join(
        value
        for value in [posting.query, posting.title, posting.company_name, posting.location, posting.snippet]
        if value
    )


def _merge_unique(current: list[str], incoming: list[str]) -> list[str]:
    merged: list[str] = []
    seen: set[str] = set()
    for value in current + incoming:
        key = value.strip().lower()
        if not key or key in seen:
            continue
        seen.add(key)
        merged.append(value)
    return merged


def _lead_grade(total_score: int) -> str:
    if total_score >= 70:
        return "hot"
    if total_score >= 35:
        return "warm"
    return "cold"


def normalize_args(args: argparse.Namespace) -> None:
    if args.smoke_test:
        args.dry_run = True
        if args.max_queries is None:
            args.max_queries = DEFAULT_SMOKE_TEST_QUERIES


def _pipeline_phase() -> str:
    raw_value = (os.getenv("PIPELINE_PHASE") or DEFAULT_PIPELINE_PHASE).strip().lower()
    if raw_value in {"prod", "production"}:
        return "production"
    return "testing"


def validate_runtime_config(args: argparse.Namespace) -> None:
    _validate_positive_int(args.max_queries, "max-queries")
    _validate_positive_int(os.getenv("REQUEST_TIMEOUT_SECONDS"), "REQUEST_TIMEOUT_SECONDS")
    _validate_positive_int(os.getenv("BATCH_SIZE"), "BATCH_SIZE")

    required_env = []
    if args.leads:
        required_env = ["DATABASE_URL"]
    else:
        required_env = ["SCRAPEDO_API_KEY", "GEMINI_API_KEY"]
        if not args.dry_run:
            required_env.append("DATABASE_URL")

    missing_or_placeholder = [
        name for name in required_env if _is_missing_or_placeholder(os.getenv(name))
    ]
    if missing_or_placeholder:
        joined = ", ".join(missing_or_placeholder)
        raise ValueError(f"Missing or placeholder environment values: {joined}")


def _validate_positive_int(value: str | int | None, name: str) -> None:
    if value is None:
        return
    try:
        parsed = int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must be an integer") from exc
    if parsed <= 0:
        raise ValueError(f"{name} must be greater than 0")


def _is_missing_or_placeholder(value: str | None) -> bool:
    if value is None:
        return True
    cleaned = value.strip()
    return not cleaned or cleaned in PLACEHOLDER_ENV_VALUES


def get_source_scrapers() -> dict[str, ScraperFn]:
    from scrapers.indeed import scrape_indeed
    from scrapers.linkedin import scrape_linkedin
    from scrapers.stepstone import scrape_stepstone

    return {
        "linkedin": scrape_linkedin,
        "indeed": scrape_indeed,
        "stepstone": scrape_stepstone,
    }


if __name__ == "__main__":
    raise SystemExit(main())
