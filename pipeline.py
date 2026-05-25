from __future__ import annotations

import argparse
import os
import re
import sys
from collections import Counter, defaultdict
from contextlib import nullcontext
from dataclasses import dataclass, field
from difflib import SequenceMatcher
from typing import TYPE_CHECKING, Any, Callable, Iterable
from uuid import uuid4

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
    from models.schema import CompanyLead, ExtractedSignal, RawJobPosting, RawSignalDocument
    from scrapers.scrapedo_client import ScrapeDoClient


ScraperFn = Callable[[Any | None, int | None], Any]
SOURCE_NAMES = ("linkedin", "indeed", "google", "stepstone", "career_page", "news")
PHASE1_SOURCE_NAMES = ("linkedin", "indeed", "google", "stepstone")
REQUESTS_PER_QUERY_BY_SOURCE = {
    "stepstone": 3,
}
TESTING_MAX_REQUESTS_BY_SOURCE = {
    "stepstone": 3,
}
DEFAULT_PIPELINE_PHASE = "testing"
PLACEHOLDER_ENV_VALUES = {
    "your_scrapedo_api_key",
    "your_gemini_api_key",
    "your_groq_api_key",
    "your_google_kg_api_key",
    "postgresql+psycopg2://username:password@localhost:5432/ctgt_leads",
}
DEFAULT_SMOKE_TEST_QUERIES = 3
DOMAIN_RESOLUTION_OUTCOME_RESOLVED = "resolved"
DOMAIN_RESOLUTION_OUTCOME_UNRESOLVED = "unresolved"
DOMAIN_RESOLUTION_OUTCOME_ERROR = "error"


@dataclass(slots=True)
class SourceRunStats:
    pages_scraped: int = 0
    job_cards: int = 0
    prefilter_hits: int = 0
    signals: int = 0
    persisted_signals: int = 0
    duplicate_signals: int = 0
    credits_used: int = 0
    errors: list[str] = field(default_factory=list)


@dataclass(slots=True)
class DomainResolutionStats:
    companies_considered: int = 0
    reused_existing: int = 0
    attempted: int = 0
    resolved: int = 0
    retry_attempted: int = 0
    retry_resolved: int = 0
    unresolved: int = 0
    conflicts: int = 0
    errors: int = 0


@dataclass(slots=True)
class PipelineSummary:
    run_id: str = field(default_factory=lambda: uuid4().hex)
    source_stats: dict[str, SourceRunStats] = field(default_factory=dict)
    persisted_companies: dict[str, "CompanyLead"] = field(default_factory=dict)
    total_candidates: int = 0
    domain_resolution: DomainResolutionStats = field(default_factory=DomainResolutionStats)
    dry_run: bool = False
    smoke_test: bool = False
    phase: str = DEFAULT_PIPELINE_PHASE

    def ensure_source(self, source: str) -> SourceRunStats:
        if source not in self.source_stats:
            self.source_stats[source] = SourceRunStats()
        return self.source_stats[source]

    def persisted_signal_count(self) -> int:
        return sum(stats.persisted_signals for stats in self.source_stats.values())

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
        "--validate-phase1",
        action="store_true",
        help="Run Phase 1 readiness checks and a Phase 1-only smoke validation pass.",
    )
    parser.add_argument(
        "--debug-extraction",
        action="store_true",
        help="Log extraction decisions for verification during testing.",
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

    if args.validate_phase1:
        return validate_phase1_readiness(args)

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
    selected_sources = list(SOURCE_NAMES) if args.source == "all" else [args.source]
    return run_pipeline_for_sources(args, selected_sources)


def run_pipeline_for_sources(
    args: argparse.Namespace,
    selected_sources: list[str],
) -> int:
    from config import DEFAULT_BATCH_SIZE, DEFAULT_REQUEST_TIMEOUT_SECONDS
    from db import init_database
    from scrapers.scrapedo_client import ScrapeDoClient

    database: Database | None = None
    if not args.dry_run:
        database = init_database()

    timeout_seconds = int(os.getenv("REQUEST_TIMEOUT_SECONDS", DEFAULT_REQUEST_TIMEOUT_SECONDS))
    batch_size = int(os.getenv("BATCH_SIZE", DEFAULT_BATCH_SIZE))
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
    logger.info(
        "nlp runtime config batch_size={} batch_size_env={!r} default_batch_size={} request_timeout_seconds={}",
        batch_size,
        os.getenv("BATCH_SIZE"),
        DEFAULT_BATCH_SIZE,
        timeout_seconds,
    )

    scrape_context = (
        ScrapeDoClient(
            timeout_seconds=timeout_seconds,
            max_requests_by_source=max_requests_by_source,
        )
        if "stepstone" in selected_sources
        else nullcontext(None)
    )

    with scrape_context as scrape_client:
        postings = collect_postings(scrape_client, selected_sources, args.max_queries, summary)
        filtered_postings = filter_postings(postings, summary)
        signals = extract_signals(
            filtered_postings,
            batch_size=batch_size,
            debug=args.debug_extraction,
            database=database,
        )
        signals = resolve_signal_domains(signals, summary, database=database)
        process_signals(signals, summary, database=database)
        run_automatic_lead_enrichment(database=database, args=args, summary=summary)
        scrape_stats = scrape_client.stats() if scrape_client is not None else {
            "credits_used_total": 0,
            "request_count": 0,
            "credits_used_by_source": {},
            "request_count_by_source": {},
        }
        apply_scrape_stats_to_summary(summary, scrape_stats)
        health_alerts = persist_operational_logs(
            database=database,
            summary=summary,
            selected_sources=selected_sources,
        )
        print_run_summary(summary, scrape_stats, health_alerts)

    return evaluate_run(summary, selected_sources)


def validate_phase1_readiness(args: argparse.Namespace) -> int:
    validation_args = argparse.Namespace(**vars(args))
    validation_args.source = "all"
    validation_args.dry_run = True
    validation_args.smoke_test = True
    if validation_args.max_queries is None:
        validation_args.max_queries = DEFAULT_SMOKE_TEST_QUERIES

    checks = _phase1_static_checks()
    _print_phase1_checklist(checks)
    if not all(item["ok"] for item in checks):
        return 1

    try:
        validate_runtime_config_for_sources(validation_args, list(PHASE1_SOURCE_NAMES))
    except ValueError as exc:
        print("")
        print(f"Phase 1 runtime validation failed: {exc}")
        return 1

    print("")
    print(
        f"Running Phase 1 validation smoke pass for {', '.join(PHASE1_SOURCE_NAMES)} "
        f"with max_queries={validation_args.max_queries}"
    )
    return run_pipeline_for_sources(validation_args, list(PHASE1_SOURCE_NAMES))


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
        request_count_before = scrape_client.request_count if scrape_client is not None else 0
        try:
            result = scraper(scrape_client, max_queries=max_queries)
        except Exception as exc:
            message = f"{source} scrape failed: {exc}"
            logger.exception(message)
            stats.errors.append(message)
            continue

        source_postings, pages_scraped = _unpack_collector_result(result)
        collector_errors = getattr(result, "errors", None)
        if isinstance(collector_errors, list):
            stats.errors.extend(str(error) for error in collector_errors if str(error).strip())
        if pages_scraped is None:
            pages_scraped = (
                scrape_client.request_count - request_count_before
                if scrape_client is not None
                else 0
            )
        normalized_postings = [_normalize_raw_posting(posting) for posting in source_postings]
        stats.pages_scraped += pages_scraped
        stats.job_cards += len(normalized_postings)
        postings.extend(normalized_postings)

    return postings


def build_max_requests_by_source(
    selected_sources: list[str],
    max_queries: int | None,
    phase: str,
) -> dict[str, int]:
    from scrapers.stepstone import build_search_plan as build_stepstone_search_plan

    search_plan_builders: dict[str, Callable[[int | None], list[Any]]] = {
        "stepstone": build_stepstone_search_plan,
    }
    max_requests_by_source: dict[str, int] = {}

    for source in selected_sources:
        if source not in search_plan_builders:
            continue
        plan_size = len(search_plan_builders[source](max_queries=max_queries))
        planned_requests = plan_size * REQUESTS_PER_QUERY_BY_SOURCE[source]
        if phase != "production":
            planned_requests = min(planned_requests, TESTING_MAX_REQUESTS_BY_SOURCE[source])
        max_requests_by_source[source] = planned_requests

    return max_requests_by_source


def filter_postings(
    postings: list["RawJobPosting"],
    summary: PipelineSummary,
) -> list["RawJobPosting"]:
    from extractors.prefilter import keyword_prefilter

    filtered: list[RawJobPosting] = []
    for posting in postings:
        stats = summary.ensure_source(posting.source)
        if keyword_prefilter(_document_text(posting)).passed:
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
    from extractors.nlp import build_extractor

    if not postings:
        return []

    processed_source_urls: set[str] = set()
    recently_processed_companies: set[str] = set()
    if database is not None:
        processed_source_urls = database.get_processed_source_urls()
        recently_processed_companies = database.get_recent_company_names(within_hours=24 * 7)

    with build_extractor(batch_size=batch_size, debug=debug) as extractor:
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


def run_automatic_lead_enrichment(
    *,
    database: "Database" | None,
    args: argparse.Namespace,
    summary: PipelineSummary,
) -> None:
    if database is None or args.dry_run:
        return
    if not _lead_enrichment_enabled():
        return
    if summary.persisted_signal_count() == 0:
        logger.info("skipping lead enrichment because no new signals were persisted in this run")
        return

    from enrichment import run_lead_enrichment_pass

    enrichment_summary = run_lead_enrichment_pass(database)
    logger.info(
        "lead enrichment auto-run complete candidates={} attempted={} completed={} skipped={} errors={} contacts_found={}",
        enrichment_summary.candidates,
        enrichment_summary.attempted,
        enrichment_summary.completed,
        enrichment_summary.skipped,
        enrichment_summary.errors,
        enrichment_summary.contacts_found,
    )


def resolve_signal_domains(
    signals: list["ExtractedSignal"],
    summary: PipelineSummary,
    database: "Database" | None,
) -> list["ExtractedSignal"]:
    if not signals:
        return signals

    from enrichment import build_domain_resolver, canonicalize_domain

    grouped_signals: dict[str, list[ExtractedSignal]] = defaultdict(list)
    for signal in signals:
        if canonicalize_domain(signal.company_domain):
            continue
        company_key = _normalize_company_name(signal.company_name)
        if company_key:
            grouped_signals[company_key].append(signal)

    summary.domain_resolution.companies_considered = len(grouped_signals)
    if not grouped_signals:
        return signals

    if not _enrichment_enabled():
        for unresolved_signals in grouped_signals.values():
            exemplar = unresolved_signals[0]
            existing_lead = (
                database.find_company_by_identity(exemplar.company_name)
                if database is not None
                else None
            )
            existing_domain = canonicalize_domain(existing_lead.company_domain) if existing_lead else None
            if not existing_domain:
                continue
            for signal in unresolved_signals:
                _apply_domain_resolution(signal, existing_domain, "existing_company", 1.0)
            summary.domain_resolution.reused_existing += 1
        return signals

    first_pass_unresolved: list[list[ExtractedSignal]] = []
    with build_domain_resolver() as resolver:
        for unresolved_signals in grouped_signals.values():
            exemplar = unresolved_signals[0]
            existing_lead = (
                database.find_company_by_identity(exemplar.company_name)
                if database is not None
                else None
            )
            existing_domain = canonicalize_domain(existing_lead.company_domain) if existing_lead else None
            if existing_domain:
                for signal in unresolved_signals:
                    _apply_domain_resolution(signal, existing_domain, "existing_company", 1.0)
                summary.domain_resolution.reused_existing += 1
                continue

            outcome = _resolve_domain_for_company_group(
                unresolved_signals,
                summary,
                database=database,
                resolver=resolver,
                is_retry=False,
            )
            if outcome == DOMAIN_RESOLUTION_OUTCOME_RESOLVED:
                continue
            if outcome == DOMAIN_RESOLUTION_OUTCOME_ERROR:
                first_pass_unresolved.append(unresolved_signals)

        for unresolved_signals in first_pass_unresolved:
            _resolve_domain_for_company_group(
                unresolved_signals,
                summary,
                database=database,
                resolver=resolver,
                is_retry=True,
            )

    summary.domain_resolution.unresolved = len(
        [
            grouped
            for grouped in grouped_signals.values()
            if not canonicalize_domain(grouped[0].company_domain)
        ]
    )

    return signals


def print_run_summary(
    summary: PipelineSummary,
    scrape_stats: dict[str, Any],
    health_alerts: list[Any] | None = None,
) -> None:
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
            f"duplicates={stats.duplicate_signals} | credits={stats.credits_used}"
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
    print(
        "Domain resolution: "
        f"companies={summary.domain_resolution.companies_considered} | "
        f"reused={summary.domain_resolution.reused_existing} | "
        f"attempted={summary.domain_resolution.attempted} | "
        f"resolved={summary.domain_resolution.resolved} | "
        f"retry_attempted={summary.domain_resolution.retry_attempted} | "
        f"retry_resolved={summary.domain_resolution.retry_resolved} | "
        f"unresolved={summary.domain_resolution.unresolved} | "
        f"conflicts={summary.domain_resolution.conflicts} | "
        f"errors={summary.domain_resolution.errors}"
    )
    print("")
    print("Lead bands:")
    print(f"  HOT: {lead_counts.get('hot', 0)}")
    print(f"  WARM: {lead_counts.get('warm', 0)}")
    print(f"  COLD: {lead_counts.get('cold', 0)}")

    if health_alerts:
        print("")
        print("Health alerts:")
        for alert in health_alerts:
            print(f"  {alert.source}: {alert.message}")

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
    from enrichment import canonicalize_domain

    total_score = max(0, int(round(signal.raw_score * signal.confidence)))
    lead_score = "cold"
    if total_score >= 70:
        lead_score = "hot"
    elif total_score >= 35:
        lead_score = "warm"

    return CompanyLead(
        company_name=signal.company_name,
        company_domain=canonicalize_domain(signal.company_domain),
        linkedin_url=None,
        location=signal.location,
        industry=signal.industry,
        sector=None,
        headquarters_location=None,
        employee_count=None,
        revenue_range=None,
        software=list(signal.software),
        signal_sources=[signal.signal_source],
        signal_count=1,
        migration_risk=signal.migration,
        total_score=total_score,
        lead_score=lead_score,
        contacts=[],
        enrichment_source=signal.domain_resolution_source,
        enrichment_confidence=signal.domain_resolution_confidence,
        enriched_at=signal.detected_at if signal.company_domain and signal.domain_resolution_source else None,
        last_enrichment_at=None,
        first_seen=signal.detected_at,
        last_updated=signal.detected_at,
    )


def upsert_local_company(
    companies: dict[str, "CompanyLead"],
    signal: "ExtractedSignal",
) -> "CompanyLead":
    from enrichment import canonicalize_domain

    signal_domain = canonicalize_domain(signal.company_domain)
    key = f"{signal.company_name.lower()}|{signal_domain or ''}"
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
    existing.company_domain = existing.company_domain or signal_domain
    existing.location = signal.location or existing.location
    existing.industry = signal.industry or existing.industry
    if signal_domain and signal.domain_resolution_source:
        existing.enrichment_source = signal.domain_resolution_source
        existing.enrichment_confidence = signal.domain_resolution_confidence
        existing.enriched_at = signal.detected_at
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


def _document_text(posting: "RawJobPosting") -> str:
    return " | ".join(
        value
        for value in [
            posting.query,
            posting.title,
            posting.company_name,
            posting.location,
            posting.snippet,
            getattr(posting, "description", None),
        ]
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


def _apply_domain_resolution(
    signal: "ExtractedSignal",
    company_domain: str,
    source: str,
    confidence: float,
) -> None:
    signal.company_domain = company_domain
    signal.domain_resolution_source = source
    signal.domain_resolution_confidence = confidence


def _resolve_domain_for_company_group(
    unresolved_signals: list["ExtractedSignal"],
    summary: PipelineSummary,
    database: "Database" | None,
    resolver: Any,
    is_retry: bool,
) -> str:
    from enrichment import canonicalize_domain

    exemplar = unresolved_signals[0]
    if is_retry:
        summary.domain_resolution.retry_attempted += 1
    else:
        summary.domain_resolution.attempted += 1

    try:
        result = resolver.resolve(
            exemplar.company_name,
            location=exemplar.location,
            source_url=str(exemplar.source_url),
            signal_source=exemplar.signal_source,
        )
    except Exception as exc:
        logger.warning(
            "domain resolution {}failed company={} error={}",
            "retry " if is_retry else "",
            exemplar.company_name,
            exc,
        )
        summary.domain_resolution.errors += 1
        return DOMAIN_RESOLUTION_OUTCOME_ERROR

    resolved_domain = canonicalize_domain(result.company_domain)
    if not resolved_domain or not _domain_resolution_passes_threshold(result.confidence):
        logger.info(
            "domain resolution {}unresolved company={} source={} confidence={} reason={}",
            "retry " if is_retry else "",
            exemplar.company_name,
            result.source,
            result.confidence,
            result.reason,
        )
        return DOMAIN_RESOLUTION_OUTCOME_UNRESOLVED

    conflicting_lead = database.find_company_by_domain(resolved_domain) if database is not None else None
    if conflicting_lead and not _company_names_similar(conflicting_lead.company_name, exemplar.company_name):
        logger.warning(
            "domain resolution {}conflict company={} resolved_domain={} existing_company={}",
            "retry " if is_retry else "",
            exemplar.company_name,
            resolved_domain,
            conflicting_lead.company_name,
        )
        summary.domain_resolution.conflicts += 1
        return DOMAIN_RESOLUTION_OUTCOME_UNRESOLVED

    for signal in unresolved_signals:
        _apply_domain_resolution(signal, resolved_domain, result.source, result.confidence)
    if is_retry:
        summary.domain_resolution.retry_resolved += 1
    else:
        summary.domain_resolution.resolved += 1
    return DOMAIN_RESOLUTION_OUTCOME_RESOLVED


def _domain_resolution_passes_threshold(confidence: float) -> bool:
    threshold = float(os.getenv("ENRICHMENT_MIN_DOMAIN_CONFIDENCE", "0.75"))
    return confidence >= threshold


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


def _company_names_similar(left: str, right: str) -> bool:
    left_norm = _normalize_company_name(left)
    right_norm = _normalize_company_name(right)
    if left_norm == right_norm:
        return True
    left_tokens = set(left_norm.split())
    right_tokens = set(right_norm.split())
    legal_suffixes = {"gmbh", "inc", "ltd", "llc", "ag"}
    if left_tokens and right_tokens and left_tokens.issubset(right_tokens | legal_suffixes):
        return True
    if left_tokens and right_tokens and right_tokens.issubset(left_tokens | legal_suffixes):
        return True
    return SequenceMatcher(a=left_norm, b=right_norm).ratio() >= 0.88


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
    _validate_positive_int(os.getenv("ENRICHMENT_TIMEOUT_SECONDS"), "ENRICHMENT_TIMEOUT_SECONDS")
    _validate_probability(os.getenv("ENRICHMENT_MIN_DOMAIN_CONFIDENCE"), "ENRICHMENT_MIN_DOMAIN_CONFIDENCE")
    _validate_positive_int(os.getenv("LEAD_ENRICHMENT_TIMEOUT_SECONDS"), "LEAD_ENRICHMENT_TIMEOUT_SECONDS")
    _validate_positive_int(os.getenv("LEAD_ENRICHMENT_FRESHNESS_DAYS"), "LEAD_ENRICHMENT_FRESHNESS_DAYS")

    selected_sources = list(SOURCE_NAMES) if args.source == "all" else [args.source]
    validate_runtime_config_for_sources(args, selected_sources)


def validate_runtime_config_for_sources(
    args: argparse.Namespace,
    selected_sources: list[str],
) -> None:
    _validate_positive_int(args.max_queries, "max-queries")
    _validate_positive_int(os.getenv("REQUEST_TIMEOUT_SECONDS"), "REQUEST_TIMEOUT_SECONDS")
    _validate_positive_int(os.getenv("BATCH_SIZE"), "BATCH_SIZE")
    _validate_positive_int(os.getenv("ENRICHMENT_TIMEOUT_SECONDS"), "ENRICHMENT_TIMEOUT_SECONDS")
    _validate_probability(os.getenv("ENRICHMENT_MIN_DOMAIN_CONFIDENCE"), "ENRICHMENT_MIN_DOMAIN_CONFIDENCE")
    _validate_positive_int(os.getenv("LEAD_ENRICHMENT_TIMEOUT_SECONDS"), "LEAD_ENRICHMENT_TIMEOUT_SECONDS")
    _validate_positive_int(os.getenv("LEAD_ENRICHMENT_FRESHNESS_DAYS"), "LEAD_ENRICHMENT_FRESHNESS_DAYS")

    llm_provider = _llm_provider()
    required_env = []
    if args.leads:
        required_env = ["DATABASE_URL"]
    else:
        if llm_provider == "groq":
            required_env = ["GROQ_API_KEY"]
        else:
            required_env = ["GEMINI_API_KEY"]
        if "stepstone" in selected_sources:
            required_env.append("SCRAPEDO_API_KEY")
        if not args.dry_run:
            required_env.append("DATABASE_URL")

    if _enrichment_enabled() and not args.leads:
        provider = (os.getenv("ENRICHMENT_PROVIDER") or "google_kg").strip().lower()
        if provider not in {"google_kg", "noop"}:
            raise ValueError("ENRICHMENT_PROVIDER must be either 'google_kg' or 'noop'")
        if provider == "google_kg":
            required_env.append("GOOGLE_KG_API_KEY")

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


def _validate_probability(value: str | None, name: str) -> None:
    if value is None or not value.strip():
        return
    try:
        parsed = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must be a number") from exc
    if parsed < 0.0 or parsed > 1.0:
        raise ValueError(f"{name} must be between 0 and 1")


def _is_missing_or_placeholder(value: str | None) -> bool:
    if value is None:
        return True
    cleaned = value.strip()
    return not cleaned or cleaned in PLACEHOLDER_ENV_VALUES


def _llm_provider() -> str:
    provider = (os.getenv("LLM_PROVIDER") or "gemini").strip().lower()
    if provider not in {"gemini", "groq"}:
        raise ValueError("LLM_PROVIDER must be either 'gemini' or 'groq'")
    return provider


def _enrichment_enabled() -> bool:
    raw_value = (os.getenv("ENRICHMENT_ENABLED") or "").strip().lower()
    return raw_value in {"1", "true", "yes", "on"}


def _lead_enrichment_enabled() -> bool:
    raw_value = (os.getenv("LEAD_ENRICHMENT_ENABLED") or "").strip().lower()
    return raw_value in {"1", "true", "yes", "on"}


def _unpack_collector_result(result: Any) -> tuple[list["RawJobPosting | RawSignalDocument"], int | None]:
    postings = getattr(result, "postings", None)
    pages_scraped = getattr(result, "pages_scraped", None)
    if isinstance(postings, list):
        return postings, pages_scraped
    return result, None


def _normalize_raw_posting(posting: "RawJobPosting | RawSignalDocument") -> "RawJobPosting":
    from models.schema import RawJobPosting, RawSignalDocument

    if isinstance(posting, RawJobPosting):
        return posting
    if isinstance(posting, RawSignalDocument):
        return RawJobPosting(
            source=posting.source,
            signal_type=posting.signal_type,
            query=posting.query,
            title=posting.title,
            company_name=posting.company_name,
            location=posting.location,
            snippet=posting.snippet,
            description=posting.description,
            job_url=posting.source_url,
            posted_date=posting.published_date,
            scraped_at=posting.scraped_at,
        )
    raise TypeError(f"Unsupported raw posting type: {type(posting)!r}")


def get_source_scrapers() -> dict[str, ScraperFn]:
    from scrapers.career_pages import scrape_career_pages
    from scrapers.jobspy_adapter import scrape_google, scrape_indeed, scrape_linkedin
    from scrapers.news_rss import scrape_news
    from scrapers.stepstone import scrape_stepstone

    return {
        "linkedin": scrape_linkedin,
        "indeed": scrape_indeed,
        "google": scrape_google,
        "stepstone": scrape_stepstone,
        "career_page": scrape_career_pages,
        "news": scrape_news,
    }


def apply_scrape_stats_to_summary(summary: PipelineSummary, scrape_stats: dict[str, Any]) -> None:
    credits_by_source = scrape_stats.get("credits_used_by_source", {}) or {}
    for source, credits_used in credits_by_source.items():
        summary.ensure_source(str(source)).credits_used += int(credits_used or 0)


def persist_operational_logs(
    database: "Database" | None,
    summary: PipelineSummary,
    selected_sources: list[str],
) -> list[Any]:
    if database is None:
        return []

    from db import ScrapeLogEntry

    entries: list[ScrapeLogEntry] = []
    for source in selected_sources:
        stats = summary.ensure_source(source)
        status = _source_run_status(stats)
        entries.append(
            ScrapeLogEntry(
                source=source,
                status=status,
                credits_used=stats.credits_used,
                cards_found=stats.job_cards,
                signals_found=stats.persisted_signals or stats.signals,
                pages_scraped=stats.pages_scraped,
                error_count=len(stats.errors),
                phase=summary.phase,
                dry_run=summary.dry_run,
            )
        )

    database.save_scrape_logs(summary.run_id, entries)
    return database.get_recent_source_health_alerts(selected_sources)


def _source_run_status(stats: SourceRunStats) -> str:
    if stats.errors:
        return "failed"
    if stats.pages_scraped > 0 and stats.job_cards == 0:
        return "zero_cards"
    if stats.pages_scraped == 0 and stats.job_cards == 0:
        return "skipped"
    return "success"


def _phase1_static_checks() -> list[dict[str, str | bool]]:
    from models.schema import SignalSource
    from scrapers.jobspy_adapter import JOBSPY_SUPPORTED_SOURCES, build_search_plan as build_jobspy_search_plan
    from scrapers.stepstone import build_search_plan as build_stepstone_search_plan

    source_scrapers = get_source_scrapers()
    signal_sources = set(getattr(SignalSource, "__args__", ()))
    jobspy_sources = set(JOBSPY_SUPPORTED_SOURCES)
    checks: list[dict[str, str | bool]] = []

    for source in PHASE1_SOURCE_NAMES:
        checks.append(
            {
                "label": f"pipeline source registry includes `{source}`",
                "ok": source in source_scrapers,
            }
        )
        checks.append(
            {
                "label": f"schema supports `{source}` as SignalSource",
                "ok": source in signal_sources,
            }
        )

    for source in ("linkedin", "indeed", "google"):
        checks.append(
            {
                "label": f"JobSpy supports `{source}`",
                "ok": source in jobspy_sources,
            }
        )
        checks.append(
            {
                "label": f"`{source}` search plan is non-empty",
                "ok": len(build_jobspy_search_plan(source, max_queries=1)) > 0,
            }
        )

    checks.append(
        {
            "label": "`stepstone` search plan is non-empty",
            "ok": len(build_stepstone_search_plan(max_queries=1)) > 0,
        }
    )

    return checks


def _print_phase1_checklist(checks: list[dict[str, str | bool]]) -> None:
    print("Phase 1 readiness checklist:")
    for item in checks:
        status = "PASS" if item["ok"] else "FAIL"
        print(f"- [{status}] {item['label']}")


if __name__ == "__main__":
    raise SystemExit(main())
