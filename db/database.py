from __future__ import annotations

import os
import re
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from difflib import SequenceMatcher
from typing import Any
from uuid import uuid4

from loguru import logger
from sqlalchemy import JSON, Boolean, DateTime, Float, Index, Integer, String, Text, UniqueConstraint, case, create_engine, func, inspect, select, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.engine import Engine, make_url
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker

from config import LEAD_THRESHOLDS, MULTI_SOURCE_BONUS, VOLUME_BONUS_SECOND_SIGNAL, VOLUME_BONUS_THIRD_PLUS_SIGNAL
from enrichment.domain_resolution import canonicalize_domain
from models.schema import CompanyLead, ExtractedSignal, LeadContact, LeadScore


JOBSPY_COMPANY_DOMAIN_SOURCE = "jobspy_company_url_direct"
JOBSPY_COMPANY_URL_DOMAIN_SOURCE = "jobspy_company_url"
TRUSTED_JOBSPY_DOMAIN_SOURCES = {
    JOBSPY_COMPANY_DOMAIN_SOURCE,
    JOBSPY_COMPANY_URL_DOMAIN_SOURCE,
}
LOWER_TRUST_DOMAIN_SOURCES = {
    "clearbit_autocomplete",
    "company_name_domain",
    "existing_company",
    "lead_enrichment",
    "serper",
    "source_url_news",
}


class DatabaseError(Exception):
    """Raised when database configuration or persistence fails."""


def _json_type() -> type[JSON] | type[JSONB]:
    return JSONB if os.getenv("DATABASE_URL", "").startswith("postgresql") else JSON


class Base(DeclarativeBase):
    pass


class SignalRecord(Base):
    __tablename__ = "signals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    company_name: Mapped[str] = mapped_column(Text, nullable=False)
    company_domain: Mapped[str | None] = mapped_column(Text, nullable=True)
    company_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    location: Mapped[str | None] = mapped_column(Text, nullable=True)
    industry: Mapped[str | None] = mapped_column(Text, nullable=True)
    company_industry: Mapped[str | None] = mapped_column(Text, nullable=True)
    software: Mapped[list[str]] = mapped_column(_json_type(), nullable=False, default=list)
    signal_type: Mapped[str] = mapped_column(String(32), nullable=False)
    signal_source: Mapped[str] = mapped_column(String(32), nullable=False)
    migration: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    migration_from: Mapped[str | None] = mapped_column(Text, nullable=True)
    pain_signals: Mapped[list[str]] = mapped_column(_json_type(), nullable=False, default=list)
    expansion_signals: Mapped[list[str]] = mapped_column(_json_type(), nullable=False, default=list)
    raw_score: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    confidence: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_url: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    source_title: Mapped[str | None] = mapped_column(Text, nullable=True)
    detected_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    __table_args__ = (
        Index("idx_signals_company", func.lower(company_name)),
        Index("idx_signals_detected_at", detected_at),
    )


class CompanyRecord(Base):
    __tablename__ = "companies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    company_name: Mapped[str] = mapped_column(Text, nullable=False)
    company_domain: Mapped[str | None] = mapped_column(Text, nullable=True, unique=True)
    company_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    linkedin_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    location: Mapped[str | None] = mapped_column(Text, nullable=True)
    industry: Mapped[str | None] = mapped_column(Text, nullable=True)
    company_industry: Mapped[str | None] = mapped_column(Text, nullable=True)
    sector: Mapped[str | None] = mapped_column(Text, nullable=True)
    headquarters_location: Mapped[str | None] = mapped_column(Text, nullable=True)
    employee_count: Mapped[str | None] = mapped_column(Text, nullable=True)
    revenue_range: Mapped[str | None] = mapped_column(Text, nullable=True)
    software: Mapped[list[str]] = mapped_column(_json_type(), nullable=False, default=list)
    signal_sources: Mapped[list[str]] = mapped_column(_json_type(), nullable=False, default=list)
    signal_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    migration_risk: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    total_score: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    lead_score: Mapped[str] = mapped_column(String(16), nullable=False, default="cold")
    contacts: Mapped[list[dict[str, Any]]] = mapped_column(_json_type(), nullable=False, default=list)
    enrichment_source: Mapped[str | None] = mapped_column(String(64), nullable=True)
    enrichment_confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    enriched_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_enrichment_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    first_seen: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    last_updated: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    __table_args__ = (
        Index("idx_companies_score", total_score.desc()),
        Index("idx_companies_lead_score", lead_score),
        Index("idx_companies_name", func.lower(company_name)),
    )


class ScrapeLogRecord(Base):
    __tablename__ = "scrape_log"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    run_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True, default=lambda: uuid4().hex)
    source: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    query: Mapped[str | None] = mapped_column(Text, nullable=True)
    target_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="success")
    credits_used: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    cards_found: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    signals_found: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    pages_scraped: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    error_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    phase: Mapped[str | None] = mapped_column(String(32), nullable=True)
    dry_run: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    scraped_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        index=True,
    )


class LeadContactRecord(Base):
    __tablename__ = "leads_contacts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    company_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    company_name: Mapped[str] = mapped_column(Text, nullable=False)
    company_domain: Mapped[str | None] = mapped_column(Text, nullable=True)
    full_name: Mapped[str] = mapped_column(Text, nullable=False)
    first_name: Mapped[str | None] = mapped_column(Text, nullable=True)
    last_name: Mapped[str | None] = mapped_column(Text, nullable=True)
    title: Mapped[str | None] = mapped_column(Text, nullable=True)
    email: Mapped[str | None] = mapped_column(Text, nullable=True)
    linkedin_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    phone: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_provider: Mapped[str] = mapped_column(String(64), nullable=False)
    source_stage: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    __table_args__ = (
        Index("idx_leads_contacts_company", company_id),
        Index("idx_leads_contacts_email", email),
    )


class EnrichmentLogRecord(Base):
    __tablename__ = "enrichment_log"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    company_id: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    company_name: Mapped[str] = mapped_column(Text, nullable=False)
    company_domain: Mapped[str | None] = mapped_column(Text, nullable=True)
    stage: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    provider: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    message: Mapped[str | None] = mapped_column(Text, nullable=True)
    payload: Mapped[dict[str, Any] | None] = mapped_column(_json_type(), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        index=True,
    )


class PipelineQueryRecord(Base):
    __tablename__ = "pipeline_queries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    query_text: Mapped[str] = mapped_column(Text, nullable=False)
    locale: Mapped[str] = mapped_column(String(8), nullable=False, default="en")
    sources: Mapped[list[str]] = mapped_column(_json_type(), nullable=False, default=list)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
    )

    __table_args__ = (
        UniqueConstraint("query_text", "locale", name="uq_pipeline_queries_text_locale"),
    )


class PipelineLocationRecord(Base):
    __tablename__ = "pipeline_locations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    location_name: Mapped[str] = mapped_column(Text, nullable=False)
    locale: Mapped[str] = mapped_column(String(8), nullable=False, default="en")
    sources: Mapped[list[str]] = mapped_column(_json_type(), nullable=False, default=list)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
    )

    __table_args__ = (
        UniqueConstraint("location_name", "locale", name="uq_pipeline_locations_name_locale"),
    )


class PipelineConfigMetaRecord(Base):
    __tablename__ = "pipeline_config_meta"

    key: Mapped[str] = mapped_column(String(64), primary_key=True)
    value: Mapped[str] = mapped_column(Text, nullable=False)


class KeywordRecord(Base):
    __tablename__ = "keywords"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    keyword: Mapped[str] = mapped_column(Text, nullable=False)
    google_xray_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    search_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    last_result_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    last_error: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
    last_searched_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        Index("uq_keywords_normalized", func.lower(keyword), unique=True),
        Index("idx_keywords_last_searched", last_searched_at),
    )


class KeywordCompanyResultRecord(Base):
    __tablename__ = "keyword_company_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    keyword_id: Mapped[int] = mapped_column(Integer, nullable=False)
    keyword_text: Mapped[str] = mapped_column(Text, nullable=False)
    company_id: Mapped[int] = mapped_column(Integer, nullable=False)
    source_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    first_discovered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    last_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    times_seen: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    __table_args__ = (
        UniqueConstraint("keyword_id", "company_id", name="uq_keyword_company_result"),
        Index("idx_keyword_company_results_keyword", keyword_id),
        Index("idx_keyword_company_results_company", company_id),
        Index("idx_keyword_company_results_last_seen", last_seen_at),
    )


@dataclass(slots=True)
class ScrapeLogEntry:
    source: str
    status: str
    credits_used: int = 0
    cards_found: int = 0
    signals_found: int = 0
    pages_scraped: int = 0
    error_count: int = 0
    phase: str | None = None
    dry_run: bool = False
    query: str | None = None
    target_url: str | None = None


@dataclass(slots=True)
class SourceHealthAlert:
    source: str
    alert_type: str
    consecutive_runs: int
    message: str


@dataclass(slots=True)
class SaveSignalResult:
    created: bool
    record_id: int | None = None
    duplicate_url: bool = False


@dataclass(slots=True)
class SignalView:
    company_name: str
    company_domain: str | None
    company_url: str | None
    location: str | None
    industry: str | None
    company_industry: str | None
    software: list[str]
    signal_type: str
    signal_source: str
    migration: bool
    migration_from: str | None
    pain_signals: list[str]
    expansion_signals: list[str]
    raw_score: int
    confidence: float
    reason: str | None
    source_url: str
    source_title: str | None
    detected_at: datetime
    lead_score: str = "cold"
    company_total_score: int = 0
    company_signal_count: int = 0


@dataclass(slots=True)
class SourceDashboardStats:
    source: str
    signal_count: int = 0
    company_count: int = 0
    hot_count: int = 0
    warm_count: int = 0
    cold_count: int = 0


@dataclass(slots=True)
class EnrichmentLogEntry:
    company_name: str
    company_domain: str | None
    stage: str
    provider: str
    status: str
    message: str | None = None
    payload: dict[str, Any] | None = None


@dataclass(slots=True)
class KeywordSearchItem:
    id: int
    keyword: str
    google_xray_enabled: bool
    search_count: int
    last_result_count: int
    last_error: str | None
    created_at: datetime
    updated_at: datetime
    last_searched_at: datetime | None


@dataclass(slots=True)
class KeywordCompanySearchItem:
    id: int
    keyword_id: int
    keyword: str
    company_id: int
    company_name: str
    company_domain: str | None
    company_url: str | None
    linkedin_url: str | None
    location: str | None
    industry: str | None
    source_url: str | None
    first_discovered_at: datetime
    last_seen_at: datetime
    times_seen: int


class Database:
    def __init__(self, database_url: str | None = None, echo: bool = False) -> None:
        self.database_url = _normalize_database_url(database_url or os.getenv("DATABASE_URL"))
        if not self.database_url:
            raise DatabaseError("DATABASE_URL is missing")

        self.engine: Engine = create_engine(self.database_url, future=True, pool_pre_ping=True, echo=echo)
        self.session_factory = sessionmaker(bind=self.engine, expire_on_commit=False, future=True)

    def initialize(self) -> None:
        existing_tables = set(inspect(self.engine).get_table_names())
        seed_queries = "pipeline_queries" not in existing_tables
        seed_locations = "pipeline_locations" not in existing_tables
        Base.metadata.create_all(self.engine)
        self._ensure_compat_columns()
        if seed_queries or seed_locations:
            self._seed_pipeline_config(
                seed_queries=seed_queries,
                seed_locations=seed_locations,
            )

    def session(self) -> Session:
        return self.session_factory()

    def list_keywords(self, limit: int = 500) -> list[KeywordSearchItem]:
        safe_limit = max(1, min(limit, 500))
        statement = select(KeywordRecord).order_by(
            KeywordRecord.created_at.asc(),
        ).limit(safe_limit)
        with self.session() as session:
            return [_to_keyword_search_item(record) for record in session.scalars(statement).all()]

    def record_keyword_search(
        self,
        keyword_id: int,
        *,
        result_count: int = 0,
        error: str | None = None,
    ) -> KeywordSearchItem | None:
        with self.session() as session, session.begin():
            record = session.get(KeywordRecord, keyword_id)
            if record is None:
                return None
            now = datetime.now(timezone.utc)
            record.search_count += 1
            record.last_result_count = max(0, result_count)
            record.last_error = error.strip()[:4000] if error else None
            record.last_searched_at = now
            record.updated_at = now
            session.flush()
            return _to_keyword_search_item(record)

    def record_keyword_company(
        self,
        keyword_id: int,
        company_name: str,
        company_domain: str | None = None,
        *,
        source_url: str | None = None,
        seen_at: datetime | None = None,
    ) -> KeywordCompanySearchItem | None:
        normalized_domain = canonicalize_domain(company_domain)
        with self.session() as session, session.begin():
            keyword = session.get(KeywordRecord, keyword_id)
            if keyword is None:
                return None
            company = self._find_company_record(session, company_name, normalized_domain)
            if company is None:
                return None

            record = session.scalar(
                select(KeywordCompanyResultRecord)
                .where(KeywordCompanyResultRecord.keyword_id == keyword_id)
                .where(KeywordCompanyResultRecord.company_id == company.id)
                .limit(1)
            )
            observed_at = _ensure_utc(seen_at) if seen_at is not None else datetime.now(timezone.utc)
            if record is None:
                record = KeywordCompanyResultRecord(
                    keyword_id=keyword.id,
                    keyword_text=keyword.keyword,
                    company_id=company.id,
                    source_url=source_url,
                    first_discovered_at=observed_at,
                    last_seen_at=observed_at,
                    times_seen=1,
                )
                session.add(record)
            else:
                record.keyword_text = keyword.keyword
                record.source_url = source_url or record.source_url
                record.last_seen_at = max(_ensure_utc(record.last_seen_at), observed_at)
                record.times_seen += 1
            session.flush()
            return _to_keyword_company_search_item(record, company)

    def list_keyword_companies(self, limit: int = 500) -> list[KeywordCompanySearchItem]:
        safe_limit = max(1, min(limit, 1000))
        with self.session() as session:
            rows = session.execute(
                select(KeywordCompanyResultRecord, CompanyRecord)
                .join(
                    CompanyRecord,
                    CompanyRecord.id == KeywordCompanyResultRecord.company_id,
                )
                .order_by(KeywordCompanyResultRecord.last_seen_at.desc())
                .limit(safe_limit)
            ).all()
            return [
                _to_keyword_company_search_item(result, company)
                for result, company in rows
            ]

    def _ensure_compat_columns(self) -> None:
        inspector = inspect(self.engine)
        table_names = set(inspector.get_table_names())
        if "signals" in table_names:
            signal_columns = {column["name"] for column in inspector.get_columns("signals")}
            signal_compat_columns = {
                "reason": "ALTER TABLE signals ADD COLUMN reason TEXT",
                "company_url": "ALTER TABLE signals ADD COLUMN company_url TEXT",
                "company_industry": "ALTER TABLE signals ADD COLUMN company_industry TEXT",
            }
            with self.engine.begin() as connection:
                for column_name, ddl in signal_compat_columns.items():
                    if column_name not in signal_columns:
                        connection.execute(text(ddl))
        if "companies" in table_names:
            company_columns = {column["name"] for column in inspector.get_columns("companies")}
            compat_columns = {
                "company_url": "ALTER TABLE companies ADD COLUMN company_url TEXT",
                "linkedin_url": "ALTER TABLE companies ADD COLUMN linkedin_url TEXT",
                "sector": "ALTER TABLE companies ADD COLUMN sector TEXT",
                "headquarters_location": "ALTER TABLE companies ADD COLUMN headquarters_location TEXT",
                "employee_count": "ALTER TABLE companies ADD COLUMN employee_count TEXT",
                "revenue_range": "ALTER TABLE companies ADD COLUMN revenue_range TEXT",
                "company_industry": "ALTER TABLE companies ADD COLUMN company_industry TEXT",
                "enrichment_source": "ALTER TABLE companies ADD COLUMN enrichment_source VARCHAR(64)",
                "enrichment_confidence": "ALTER TABLE companies ADD COLUMN enrichment_confidence FLOAT",
                "enriched_at": "ALTER TABLE companies ADD COLUMN enriched_at TIMESTAMPTZ",
                "last_enrichment_at": "ALTER TABLE companies ADD COLUMN last_enrichment_at TIMESTAMPTZ",
            }
            with self.engine.begin() as connection:
                for column_name, ddl in compat_columns.items():
                    if column_name not in company_columns:
                        connection.execute(text(ddl))
        if "scrape_log" in table_names:
            scrape_columns = {column["name"] for column in inspector.get_columns("scrape_log")}
            compat_columns = {
                "run_id": "ALTER TABLE scrape_log ADD COLUMN run_id VARCHAR(64)",
                "pages_scraped": "ALTER TABLE scrape_log ADD COLUMN pages_scraped INTEGER DEFAULT 0",
                "error_count": "ALTER TABLE scrape_log ADD COLUMN error_count INTEGER DEFAULT 0",
                "phase": "ALTER TABLE scrape_log ADD COLUMN phase VARCHAR(32)",
                "dry_run": "ALTER TABLE scrape_log ADD COLUMN dry_run BOOLEAN DEFAULT FALSE",
            }
            with self.engine.begin() as connection:
                for column_name, ddl in compat_columns.items():
                    if column_name not in scrape_columns:
                        connection.execute(text(ddl))
        if "keywords" in table_names:
            keyword_columns = {column["name"] for column in inspector.get_columns("keywords")}
            if "google_xray_enabled" not in keyword_columns:
                with self.engine.begin() as connection:
                    connection.execute(
                        text(
                            "ALTER TABLE keywords ADD COLUMN "
                            "google_xray_enabled BOOLEAN NOT NULL DEFAULT FALSE"
                        )
                    )
        if "leads_contacts" not in table_names:
            LeadContactRecord.__table__.create(self.engine, checkfirst=True)
        if "enrichment_log" not in table_names:
            EnrichmentLogRecord.__table__.create(self.engine, checkfirst=True)

    def _seed_pipeline_config(self, *, seed_queries: bool, seed_locations: bool) -> None:
        from pipeline_config import default_pipeline_search_config

        defaults = default_pipeline_search_config()
        with self.session() as session:
            if seed_queries:
                session.add_all(
                    PipelineQueryRecord(
                        query_text=item.value,
                        locale=item.locale,
                        sources=list(item.sources),
                    )
                    for item in defaults.queries
                )
            if seed_locations:
                session.add_all(
                    PipelineLocationRecord(
                        location_name=item.value,
                        locale=item.locale,
                        sources=list(item.sources),
                    )
                    for item in defaults.locations
                )
            session.merge(PipelineConfigMetaRecord(key="defaults_seeded", value="true"))
            session.commit()

    def get_pipeline_search_config(self) -> Any:
        from pipeline_config import PipelineLocation, PipelineQuery, PipelineSearchConfig

        with self.session() as session:
            query_rows = session.scalars(
                select(PipelineQueryRecord).order_by(
                    PipelineQueryRecord.locale,
                    PipelineQueryRecord.query_text,
                )
            ).all()
            location_rows = session.scalars(
                select(PipelineLocationRecord).order_by(
                    PipelineLocationRecord.locale,
                    PipelineLocationRecord.location_name,
                )
            ).all()

        return PipelineSearchConfig(
            queries=tuple(
                PipelineQuery(
                    value=row.query_text,
                    locale=row.locale,
                    sources=tuple(row.sources or []),
                )
                for row in query_rows
            ),
            locations=tuple(
                PipelineLocation(
                    value=row.location_name,
                    locale=row.locale,
                    sources=tuple(row.sources or []),
                )
                for row in location_rows
            ),
        )

    def save_signal(self, signal: ExtractedSignal) -> SaveSignalResult:
        signal_domain = canonicalize_domain(signal.company_domain)
        with self.session() as session:
            existing = session.scalar(
                select(SignalRecord).where(SignalRecord.source_url == str(signal.source_url)).limit(1)
            )
            if existing is not None:
                if signal.company_industry and existing.company_industry != signal.company_industry:
                    existing.company_industry = signal.company_industry
                    session.commit()
                return SaveSignalResult(created=False, record_id=existing.id, duplicate_url=True)

            record = SignalRecord(
                company_name=signal.company_name,
                company_domain=signal_domain,
                company_url=signal.company_url,
                location=signal.location,
                industry=signal.industry,
                company_industry=signal.company_industry,
                software=list(signal.software),
                signal_type=signal.signal_type,
                signal_source=signal.signal_source,
                migration=signal.migration,
                migration_from=signal.migration_from,
                pain_signals=list(signal.pain_signals),
                expansion_signals=list(signal.expansion_signals),
                raw_score=signal.raw_score,
                confidence=signal.confidence,
                reason=signal.reason,
                source_url=str(signal.source_url),
                source_title=signal.source_title,
                detected_at=signal.detected_at,
            )
            session.add(record)
            try:
                session.commit()
            except IntegrityError:
                session.rollback()
                duplicate_id = session.scalar(
                    select(SignalRecord.id).where(SignalRecord.source_url == str(signal.source_url)).limit(1)
                )
                return SaveSignalResult(created=False, record_id=duplicate_id, duplicate_url=True)

            session.refresh(record)
            return SaveSignalResult(created=True, record_id=record.id)

    def update_company_industry(self, signal: ExtractedSignal) -> None:
        if not signal.company_industry:
            return

        signal_domain = canonicalize_domain(signal.company_domain)
        with self.session() as session:
            company = self._find_company_record(session, signal.company_name, signal_domain)
            if company is None or company.company_industry == signal.company_industry:
                return
            company.company_industry = signal.company_industry
            company.last_updated = datetime.now(timezone.utc)
            session.commit()

    def upsert_company(self, signal: ExtractedSignal) -> CompanyLead:
        signal_domain = canonicalize_domain(signal.company_domain)
        trusted_jobspy_domain = (
            bool(signal_domain)
            and signal.domain_resolution_source in TRUSTED_JOBSPY_DOMAIN_SOURCES
        )
        with self.session() as session:
            domain_is_available = True
            if trusted_jobspy_domain:
                # Match the employer first. A domain-first lookup could otherwise
                # merge this signal into an unrelated company that already owns
                # a bad/shared domain.
                company = self._find_company_record(session, signal.company_name, None)
                domain_owner = session.scalar(
                    select(CompanyRecord)
                    .where(CompanyRecord.company_domain == signal_domain)
                    .limit(1)
                )
                if company is None and (
                    domain_owner is None
                    or _names_similar(domain_owner.company_name, signal.company_name)
                ):
                    company = domain_owner
                if domain_owner is not None and (
                    company is None or domain_owner.id != company.id
                ):
                    domain_is_available = False
                    logger.warning(
                        "jobspy domain assignment conflict company={} domain={} owner={}",
                        signal.company_name,
                        signal_domain,
                        domain_owner.company_name,
                    )
            else:
                company = self._find_company_record(session, signal.company_name, signal_domain)

            now = datetime.now(timezone.utc)
            signal_score = _compute_signal_score(signal)

            if company is None:
                initial_domain = signal_domain if domain_is_available else None
                company = CompanyRecord(
                    company_name=signal.company_name,
                    company_domain=initial_domain,
                    company_url=signal.company_url,
                    linkedin_url=signal.linkedin_url,
                    location=signal.location,
                    industry=signal.industry,
                    company_industry=signal.company_industry,
                    sector=None,
                    headquarters_location=None,
                    employee_count=None,
                    revenue_range=None,
                    software=_merge_unique([], signal.software),
                    signal_sources=[signal.signal_source],
                    signal_count=1,
                    migration_risk=signal.migration,
                    total_score=signal_score,
                    lead_score=_lead_grade(signal_score),
                    contacts=[],
                    enrichment_source=(
                        signal.domain_resolution_source if initial_domain else None
                    ),
                    enrichment_confidence=(
                        signal.domain_resolution_confidence if initial_domain else None
                    ),
                    enriched_at=(
                        now if initial_domain and signal.domain_resolution_source else None
                    ),
                    last_enrichment_at=None,
                    first_seen=signal.detected_at,
                    last_updated=now,
                )
                session.add(company)
                session.commit()
                session.refresh(company)
                return _to_company_lead(company)

            identity_metadata_changed = False
            existing_domain = canonicalize_domain(company.company_domain)
            should_assign_domain = bool(
                signal_domain
                and domain_is_available
                and (
                    not existing_domain
                    or (
                        trusted_jobspy_domain
                        and existing_domain != signal_domain
                        and _is_lower_trust_domain_source(company.enrichment_source)
                    )
                )
            )
            should_upgrade_jobspy_provenance = bool(
                trusted_jobspy_domain
                and domain_is_available
                and existing_domain == signal_domain
                and company.enrichment_source not in TRUSTED_JOBSPY_DOMAIN_SOURCES
            )
            if should_assign_domain:
                company.company_domain = signal_domain
                identity_metadata_changed = True
            if should_assign_domain or should_upgrade_jobspy_provenance:
                company.enrichment_source = signal.domain_resolution_source
                company.enrichment_confidence = signal.domain_resolution_confidence
                company.enriched_at = now
                identity_metadata_changed = True
            if signal.company_url and not company.company_url:
                company.company_url = signal.company_url
                identity_metadata_changed = True
            if signal.linkedin_url and not company.linkedin_url:
                company.linkedin_url = signal.linkedin_url
                identity_metadata_changed = True
            if signal.company_industry and signal.company_industry != company.company_industry:
                company.company_industry = signal.company_industry
                identity_metadata_changed = True

            if self._is_recent_same_source(session, company, signal):
                if identity_metadata_changed:
                    company.last_updated = now
                    session.commit()
                    session.refresh(company)
                return _to_company_lead(company)

            source_count_before = len(company.signal_sources or [])
            company.signal_count += 1
            company.software = _merge_unique(company.software, signal.software)
            company.signal_sources = _merge_unique(company.signal_sources, [signal.signal_source])
            company.migration_risk = company.migration_risk or signal.migration
            company.location = signal.location or company.location
            company.industry = signal.industry or company.industry
            company.company_industry = signal.company_industry or company.company_industry

            company.total_score += signal_score
            if company.signal_count == 2:
                company.total_score += VOLUME_BONUS_SECOND_SIGNAL
            elif company.signal_count >= 3:
                company.total_score += VOLUME_BONUS_THIRD_PLUS_SIGNAL
            if source_count_before < 2 and len(company.signal_sources) >= 2:
                company.total_score += MULTI_SOURCE_BONUS

            company.lead_score = _lead_grade(company.total_score)
            company.last_updated = now
            session.commit()
            session.refresh(company)
            return _to_company_lead(company)

    def get_leads(self, lead_score: LeadScore | None = None, limit: int | None = None) -> list[CompanyLead]:
        with self.session() as session:
            stmt = select(CompanyRecord).order_by(CompanyRecord.total_score.desc(), CompanyRecord.last_updated.desc())
            if lead_score is not None:
                stmt = stmt.where(CompanyRecord.lead_score == lead_score)
            if limit is not None:
                stmt = stmt.limit(limit)
            companies = session.scalars(stmt).all()
            return [_to_company_lead(company) for company in companies]

    def get_signals(
        self,
        source: str | None = None,
        lead_score: LeadScore | None = None,
        company_query: str | None = None,
        limit: int = 200,
    ) -> list[SignalView]:
        with self.session() as session:
            stmt = (
                select(SignalRecord, CompanyRecord)
                .select_from(SignalRecord)
                .join(
                    CompanyRecord,
                    func.lower(CompanyRecord.company_name) == func.lower(SignalRecord.company_name),
                    isouter=True,
                )
                .order_by(SignalRecord.detected_at.desc(), SignalRecord.id.desc())
            )
            if source:
                stmt = stmt.where(SignalRecord.signal_source == source)
            if lead_score:
                stmt = stmt.where(CompanyRecord.lead_score == lead_score)
            if company_query:
                needle = f"%{company_query.strip().lower()}%"
                stmt = stmt.where(func.lower(SignalRecord.company_name).like(needle))
            stmt = stmt.limit(limit)

            rows = session.execute(stmt).all()
            return [_to_signal_view(signal, company) for signal, company in rows]

    def get_dashboard_source_stats(self) -> list[SourceDashboardStats]:
        with self.session() as session:
            stmt = (
                select(
                    SignalRecord.signal_source,
                    func.count(SignalRecord.id),
                    func.count(func.distinct(func.lower(SignalRecord.company_name))),
                    func.sum(case((CompanyRecord.lead_score == "hot", 1), else_=0)),
                    func.sum(case((CompanyRecord.lead_score == "warm", 1), else_=0)),
                    func.sum(case((CompanyRecord.lead_score == "cold", 1), else_=0)),
                )
                .select_from(SignalRecord)
                .join(
                    CompanyRecord,
                    func.lower(CompanyRecord.company_name) == func.lower(SignalRecord.company_name),
                    isouter=True,
                )
                .group_by(SignalRecord.signal_source)
                .order_by(func.count(SignalRecord.id).desc(), SignalRecord.signal_source.asc())
            )
            rows = session.execute(stmt).all()
            stats: list[SourceDashboardStats] = []
            for row in rows:
                stats.append(
                    SourceDashboardStats(
                        source=str(row[0]),
                        signal_count=int(row[1] or 0),
                        company_count=int(row[2] or 0),
                        hot_count=int(row[3] or 0),
                        warm_count=int(row[4] or 0),
                        cold_count=int(row[5] or 0),
                    )
                )
            return stats

    def get_processed_source_urls(self) -> set[str]:
        with self.session() as session:
            rows = session.scalars(select(SignalRecord.source_url))
            return {str(row) for row in rows}

    def get_recent_company_names(self, within_hours: int = 24 * 7) -> set[str]:
        cutoff = datetime.now(timezone.utc) - timedelta(hours=within_hours)
        with self.session() as session:
            rows = session.scalars(
                select(CompanyRecord.company_name).where(CompanyRecord.last_updated >= cutoff)
            )
            return {_normalize_company_name(str(row)) for row in rows if str(row).strip()}

    def save_company_enrichment(
        self,
        company_name: str,
        company_domain: str | None,
        *,
        linkedin_url: str | None = None,
        sector: str | None = None,
        employee_count: str | None = None,
        revenue_range: str | None = None,
        headquarters_location: str | None = None,
        contacts: list[LeadContact] | None = None,
        enrichment_source: str | None = None,
        mark_enriched_at: datetime | None = None,
    ) -> CompanyLead | None:
        normalized_domain = canonicalize_domain(company_domain)
        with self.session() as session:
            company = self._find_company_record(session, company_name, normalized_domain)
            if company is None:
                return None

            if normalized_domain and not company.company_domain:
                company.company_domain = normalized_domain

            if linkedin_url:
                company.linkedin_url = linkedin_url
            if sector:
                company.sector = sector
            if employee_count:
                company.employee_count = employee_count
            if revenue_range:
                company.revenue_range = revenue_range
            if headquarters_location:
                company.headquarters_location = headquarters_location
            if enrichment_source:
                company.enrichment_source = enrichment_source

            if mark_enriched_at is not None:
                company.last_enrichment_at = _ensure_utc(mark_enriched_at)

            normalized_contacts = _normalize_contacts(contacts or [])
            if normalized_contacts:
                company.contacts = [contact.model_dump() for contact in normalized_contacts]
                session.query(LeadContactRecord).filter(LeadContactRecord.company_id == company.id).delete()
                session.add_all(
                    LeadContactRecord(
                        company_id=company.id,
                        company_name=company.company_name,
                        company_domain=company.company_domain,
                        full_name=contact.full_name,
                        first_name=contact.first_name,
                        last_name=contact.last_name,
                        title=contact.title,
                        email=contact.email,
                        linkedin_url=contact.linkedin_url,
                        phone=contact.phone,
                        source_provider=contact.source_provider,
                        source_stage=contact.source_stage,
                    )
                    for contact in normalized_contacts
                )

            session.commit()
            session.refresh(company)
            return _to_company_lead(company)

    def save_enrichment_log(self, entry: EnrichmentLogEntry) -> None:
        normalized_domain = canonicalize_domain(entry.company_domain)
        with self.session() as session:
            company = self._find_company_record(session, entry.company_name, normalized_domain)
            record = EnrichmentLogRecord(
                company_id=company.id if company is not None else None,
                company_name=entry.company_name,
                company_domain=normalized_domain,
                stage=entry.stage,
                provider=entry.provider,
                status=entry.status,
                message=entry.message,
                payload=entry.payload,
            )
            session.add(record)
            session.commit()

    def save_scrape_logs(self, run_id: str, entries: list[ScrapeLogEntry]) -> None:
        if not entries:
            return
        with self.session() as session:
            records = [
                ScrapeLogRecord(
                    run_id=run_id,
                    source=entry.source,
                    query=entry.query,
                    target_url=entry.target_url,
                    status=entry.status,
                    credits_used=entry.credits_used,
                    cards_found=entry.cards_found,
                    signals_found=entry.signals_found,
                    pages_scraped=entry.pages_scraped,
                    error_count=entry.error_count,
                    phase=entry.phase,
                    dry_run=entry.dry_run,
                )
                for entry in entries
            ]
            session.add_all(records)
            session.commit()

    def get_recent_source_health_alerts(
        self,
        sources: list[str],
        consecutive_runs: int = 3,
        within_days: int = 14,
    ) -> list[SourceHealthAlert]:
        if not sources:
            return []

        cutoff = datetime.now(timezone.utc) - timedelta(days=within_days)
        with self.session() as session:
            rows = session.scalars(
                select(ScrapeLogRecord)
                .where(
                    ScrapeLogRecord.source.in_(sources),
                    ScrapeLogRecord.dry_run.is_(False),
                    ScrapeLogRecord.scraped_at >= cutoff,
                )
                .order_by(ScrapeLogRecord.scraped_at.desc(), ScrapeLogRecord.id.desc())
            ).all()

        grouped: dict[str, list[ScrapeLogRecord]] = defaultdict(list)
        for row in rows:
            grouped[row.source].append(row)

        alerts: list[SourceHealthAlert] = []
        for source in sources:
            recent = grouped.get(source, [])[:consecutive_runs]
            if len(recent) < consecutive_runs:
                continue
            if all(item.status == "failed" or item.error_count > 0 for item in recent):
                alerts.append(
                    SourceHealthAlert(
                        source=source,
                        alert_type="repeated_failures",
                        consecutive_runs=consecutive_runs,
                        message=f"{source} failed in {consecutive_runs} consecutive persisted runs",
                    )
                )
                continue
            if all(item.pages_scraped > 0 and item.cards_found == 0 for item in recent):
                alerts.append(
                    SourceHealthAlert(
                        source=source,
                        alert_type="repeated_zero_cards",
                        consecutive_runs=consecutive_runs,
                        message=f"{source} returned zero cards in {consecutive_runs} consecutive persisted runs",
                    )
                )
        return alerts

    def find_company_by_domain(self, company_domain: str) -> CompanyLead | None:
        normalized_domain = canonicalize_domain(company_domain)
        if not normalized_domain:
            return None
        with self.session() as session:
            company = session.scalar(
                select(CompanyRecord).where(CompanyRecord.company_domain == normalized_domain).limit(1)
            )
            if company is None:
                return None
            return _to_company_lead(company)

    def find_company_by_identity(
        self,
        company_name: str,
        company_domain: str | None = None,
    ) -> CompanyLead | None:
        normalized_domain = canonicalize_domain(company_domain)
        with self.session() as session:
            company = self._find_company_record(session, company_name, normalized_domain)
            if company is None:
                return None
            return _to_company_lead(company)

    def _find_company_record(
        self,
        session: Session,
        company_name: str,
        company_domain: str | None,
    ) -> CompanyRecord | None:
        if company_domain:
            company = session.scalar(
                select(CompanyRecord).where(CompanyRecord.company_domain == company_domain).limit(1)
            )
            if company is not None:
                return company

        normalized_name = _normalize_company_name(company_name)
        exact = session.scalar(
            select(CompanyRecord).where(func.lower(CompanyRecord.company_name) == normalized_name).limit(1)
        )
        if exact is not None:
            return exact

        candidates = session.scalars(select(CompanyRecord)).all()
        for candidate in candidates:
            if _names_similar(candidate.company_name, company_name):
                return candidate
        return None

    def _is_recent_same_source(self, session: Session, company: CompanyRecord, signal: ExtractedSignal) -> bool:
        if signal.signal_source not in (company.signal_sources or []):
            return False

        last_seen = self._get_last_signal_detected_at(session, company, signal)
        if last_seen is None:
            return False
        return _ensure_utc(signal.detected_at) - last_seen < timedelta(hours=24)

    def _get_last_signal_detected_at(
        self,
        session: Session,
        company: CompanyRecord,
        signal: ExtractedSignal,
    ) -> datetime | None:
        if company.company_domain:
            detected_at = session.scalar(
                select(SignalRecord.detected_at)
                .where(
                    SignalRecord.company_domain == company.company_domain,
                    SignalRecord.signal_source == signal.signal_source,
                    SignalRecord.source_url != str(signal.source_url),
                )
                .order_by(SignalRecord.detected_at.desc())
                .limit(1)
            )
            if detected_at is not None:
                return _ensure_utc(detected_at)

        normalized_name = _normalize_company_name(company.company_name)
        detected_at = session.scalar(
            select(SignalRecord.detected_at)
            .where(
                func.lower(SignalRecord.company_name) == normalized_name,
                SignalRecord.signal_source == signal.signal_source,
                SignalRecord.source_url != str(signal.source_url),
            )
            .order_by(SignalRecord.detected_at.desc())
            .limit(1)
        )
        if detected_at is not None:
            return _ensure_utc(detected_at)

        candidate_signals = session.scalars(
            select(SignalRecord)
            .where(
                SignalRecord.signal_source == signal.signal_source,
                SignalRecord.source_url != str(signal.source_url),
            )
            .order_by(SignalRecord.detected_at.desc())
        ).all()
        for candidate in candidate_signals:
            if _names_similar(candidate.company_name, company.company_name):
                return _ensure_utc(candidate.detected_at)
        return None


def init_database(database_url: str | None = None, echo: bool = False) -> Database:
    database = Database(database_url=database_url, echo=echo)
    database.initialize()
    logger.info("database initialized url={}", _redact_database_url(database.database_url))
    return database


def _compute_signal_score(signal: ExtractedSignal) -> int:
    return max(0, int(round(signal.raw_score * signal.confidence)))


def _lead_grade(total_score: int) -> LeadScore:
    if total_score >= LEAD_THRESHOLDS["hot"]:
        return "hot"
    if total_score >= LEAD_THRESHOLDS["warm"]:
        return "warm"
    return "cold"


def _merge_unique(current: list[Any] | None, incoming: list[Any] | None) -> list[Any]:
    merged: list[Any] = []
    seen: set[str] = set()
    for value in (current or []) + (incoming or []):
        key = str(value).strip().lower()
        if not key or key in seen:
            continue
        seen.add(key)
        merged.append(value)
    return merged


def _normalize_contacts(contacts: list[LeadContact]) -> list[LeadContact]:
    normalized: list[LeadContact] = []
    seen: set[str] = set()
    for contact in contacts:
        key = "|".join(
            [
                (contact.email or "").strip().lower(),
                (contact.linkedin_url or "").strip().lower(),
                contact.full_name.strip().lower(),
                (contact.title or "").strip().lower(),
            ]
        )
        if key in seen:
            continue
        seen.add(key)
        normalized.append(contact)
    return normalized


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


def _names_similar(left: str, right: str) -> bool:
    left_norm = _normalize_company_name(left)
    right_norm = _normalize_company_name(right)
    if left_norm == right_norm:
        return True
    left_tokens = set(left_norm.split())
    right_tokens = set(right_norm.split())
    if left_tokens and right_tokens and left_tokens.issubset(right_tokens | {"gmbh", "inc", "ltd", "llc", "ag"}):
        return True
    if left_tokens and right_tokens and right_tokens.issubset(left_tokens | {"gmbh", "inc", "ltd", "llc", "ag"}):
        return True

    # Generic business descriptors can make unrelated short brand names look
    # deceptively similar (for example, "ABCO Industries" and
    # "Ebco Industries"). Compare the distinctive name tokens separately so
    # those records are not merged merely because their descriptors match.
    generic_descriptors = {
        "company",
        "global",
        "group",
        "holdings",
        "industries",
        "industry",
        "international",
        "services",
        "solutions",
        "systems",
        "technologies",
        "technology",
    }
    left_core = " ".join(token for token in left_norm.split() if token not in generic_descriptors)
    right_core = " ".join(token for token in right_norm.split() if token not in generic_descriptors)
    if left_core and right_core and left_core != right_core:
        core_ratio = SequenceMatcher(a=left_core, b=right_core).ratio()
        if min(len(left_core), len(right_core)) <= 4 and core_ratio < 0.9:
            return False

    return SequenceMatcher(a=left_norm, b=right_norm).ratio() >= 0.88


def _is_lower_trust_domain_source(source: str | None) -> bool:
    if not source:
        # Older records predate enrichment provenance. Treat their domains as
        # unverified so an authoritative JobSpy direct URL can correct them.
        return True
    providers = {
        provider.strip().lower()
        for provider in source.split(",")
        if provider.strip()
    }
    return bool(providers & LOWER_TRUST_DOMAIN_SOURCES)


def _to_company_lead(record: CompanyRecord) -> CompanyLead:
    return CompanyLead(
        company_name=record.company_name,
        company_domain=canonicalize_domain(record.company_domain),
        company_url=record.company_url,
        linkedin_url=record.linkedin_url,
        location=record.location,
        industry=record.industry,
        company_industry=record.company_industry,
        sector=record.sector,
        headquarters_location=record.headquarters_location,
        employee_count=record.employee_count,
        revenue_range=record.revenue_range,
        software=list(record.software or []),
        signal_sources=list(record.signal_sources or []),
        signal_count=record.signal_count,
        migration_risk=record.migration_risk,
        total_score=record.total_score,
        lead_score=record.lead_score,
        contacts=[LeadContact.model_validate(item) for item in list(record.contacts or [])],
        enrichment_source=record.enrichment_source,
        enrichment_confidence=record.enrichment_confidence,
        enriched_at=_ensure_utc(record.enriched_at) if record.enriched_at is not None else None,
        last_enrichment_at=_ensure_utc(record.last_enrichment_at) if record.last_enrichment_at is not None else None,
        first_seen=_ensure_utc(record.first_seen),
        last_updated=_ensure_utc(record.last_updated),
    )


def _to_signal_view(signal: SignalRecord, company: CompanyRecord | None) -> SignalView:
    lead_score = company.lead_score if company is not None else "cold"
    company_total_score = company.total_score if company is not None else 0
    company_signal_count = company.signal_count if company is not None else 0
    return SignalView(
        company_name=signal.company_name,
        company_domain=signal.company_domain,
        company_url=signal.company_url,
        location=signal.location,
        industry=signal.industry,
        company_industry=signal.company_industry,
        software=list(signal.software or []),
        signal_type=signal.signal_type,
        signal_source=signal.signal_source,
        migration=signal.migration,
        migration_from=signal.migration_from,
        pain_signals=list(signal.pain_signals or []),
        expansion_signals=list(signal.expansion_signals or []),
        raw_score=signal.raw_score,
        confidence=signal.confidence,
        reason=signal.reason,
        source_url=signal.source_url,
        source_title=signal.source_title,
        detected_at=_ensure_utc(signal.detected_at),
        lead_score=lead_score,
        company_total_score=company_total_score,
        company_signal_count=company_signal_count,
    )


def _to_keyword_search_item(record: KeywordRecord) -> KeywordSearchItem:
    return KeywordSearchItem(
        id=record.id,
        keyword=record.keyword,
        google_xray_enabled=record.google_xray_enabled,
        search_count=record.search_count,
        last_result_count=record.last_result_count,
        last_error=record.last_error,
        created_at=_ensure_utc(record.created_at),
        updated_at=_ensure_utc(record.updated_at),
        last_searched_at=_ensure_utc(record.last_searched_at) if record.last_searched_at is not None else None,
    )


def _to_keyword_company_search_item(
    record: KeywordCompanyResultRecord,
    company: CompanyRecord,
) -> KeywordCompanySearchItem:
    return KeywordCompanySearchItem(
        id=record.id,
        keyword_id=record.keyword_id,
        keyword=record.keyword_text,
        company_id=company.id,
        company_name=company.company_name,
        company_domain=canonicalize_domain(company.company_domain),
        company_url=company.company_url,
        linkedin_url=company.linkedin_url,
        location=company.location,
        industry=company.company_industry or company.industry,
        source_url=record.source_url,
        first_discovered_at=_ensure_utc(record.first_discovered_at),
        last_seen_at=_ensure_utc(record.last_seen_at),
        times_seen=record.times_seen,
    )


def _ensure_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def _redact_database_url(database_url: str) -> str:
    if "@" not in database_url or "://" not in database_url:
        return database_url
    prefix, suffix = database_url.split("://", 1)
    if "@" not in suffix:
        return database_url
    _, host = suffix.rsplit("@", 1)
    return f"{prefix}://***@{host}"


def _normalize_database_url(database_url: str | None) -> str | None:
    if database_url is None:
        return None

    cleaned = database_url.strip()
    if not cleaned:
        return None

    if cleaned.startswith("postgres://"):
        cleaned = "postgresql+psycopg2://" + cleaned[len("postgres://") :]
    elif cleaned.startswith("postgresql://") and not cleaned.startswith("postgresql+psycopg2://"):
        cleaned = "postgresql+psycopg2://" + cleaned[len("postgresql://") :]

    # Common .env mistake: raw "@" in password written as "...:password@@host..."
    # Convert first "@@" into "%40@" so password is URL-safe.
    if "://" in cleaned:
        scheme, rest = cleaned.split("://", 1)
        if "@@" in rest:
            rest = rest.replace("@@", "%40@", 1)
            cleaned = f"{scheme}://{rest}"

    try:
        parsed = make_url(cleaned)
    except Exception as exc:
        raise DatabaseError(f"Invalid DATABASE_URL: {exc}") from exc

    if parsed.host and parsed.host.startswith("@"):
        raise DatabaseError(
            "Invalid DATABASE_URL host. If your password contains '@', encode it as '%40'."
        )

    return parsed.render_as_string(hide_password=False)
