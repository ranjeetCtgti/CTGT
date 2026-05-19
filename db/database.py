from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from difflib import SequenceMatcher
from typing import Any

from loguru import logger
from sqlalchemy import JSON, Boolean, DateTime, Float, Index, Integer, String, Text, case, create_engine, func, inspect, select, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.engine import Engine, make_url
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker

from config import LEAD_THRESHOLDS, MULTI_SOURCE_BONUS, VOLUME_BONUS_SECOND_SIGNAL, VOLUME_BONUS_THIRD_PLUS_SIGNAL
from models.schema import CompanyLead, ExtractedSignal, LeadScore


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
    location: Mapped[str | None] = mapped_column(Text, nullable=True)
    industry: Mapped[str | None] = mapped_column(Text, nullable=True)
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
    location: Mapped[str | None] = mapped_column(Text, nullable=True)
    industry: Mapped[str | None] = mapped_column(Text, nullable=True)
    employee_count: Mapped[str | None] = mapped_column(Text, nullable=True)
    revenue_range: Mapped[str | None] = mapped_column(Text, nullable=True)
    software: Mapped[list[str]] = mapped_column(_json_type(), nullable=False, default=list)
    signal_sources: Mapped[list[str]] = mapped_column(_json_type(), nullable=False, default=list)
    signal_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    migration_risk: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    total_score: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    lead_score: Mapped[str] = mapped_column(String(16), nullable=False, default="cold")
    contacts: Mapped[list[dict[str, Any]]] = mapped_column(_json_type(), nullable=False, default=list)
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


@dataclass(slots=True)
class SaveSignalResult:
    created: bool
    record_id: int | None = None
    duplicate_url: bool = False


@dataclass(slots=True)
class SignalView:
    company_name: str
    company_domain: str | None
    location: str | None
    industry: str | None
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


class Database:
    def __init__(self, database_url: str | None = None, echo: bool = False) -> None:
        self.database_url = _normalize_database_url(database_url or os.getenv("DATABASE_URL"))
        if not self.database_url:
            raise DatabaseError("DATABASE_URL is missing")

        self.engine: Engine = create_engine(self.database_url, future=True, pool_pre_ping=True, echo=echo)
        self.session_factory = sessionmaker(bind=self.engine, expire_on_commit=False, future=True)

    def initialize(self) -> None:
        Base.metadata.create_all(self.engine)
        self._ensure_compat_columns()

    def session(self) -> Session:
        return self.session_factory()

    def _ensure_compat_columns(self) -> None:
        inspector = inspect(self.engine)
        signal_columns = {column["name"] for column in inspector.get_columns("signals")}
        if "reason" not in signal_columns:
            with self.engine.begin() as connection:
                connection.execute(text("ALTER TABLE signals ADD COLUMN reason TEXT"))

    def save_signal(self, signal: ExtractedSignal) -> SaveSignalResult:
        with self.session() as session:
            existing = session.scalar(
                select(SignalRecord.id).where(SignalRecord.source_url == str(signal.source_url)).limit(1)
            )
            if existing is not None:
                return SaveSignalResult(created=False, record_id=existing, duplicate_url=True)

            record = SignalRecord(
                company_name=signal.company_name,
                company_domain=signal.company_domain,
                location=signal.location,
                industry=signal.industry,
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

    def upsert_company(self, signal: ExtractedSignal) -> CompanyLead:
        with self.session() as session:
            company = self._find_company_record(session, signal)
            now = datetime.now(timezone.utc)
            signal_score = _compute_signal_score(signal)

            if company is None:
                company = CompanyRecord(
                    company_name=signal.company_name,
                    company_domain=signal.company_domain,
                    location=signal.location,
                    industry=signal.industry,
                    software=_merge_unique([], signal.software),
                    signal_sources=[signal.signal_source],
                    signal_count=1,
                    migration_risk=signal.migration,
                    total_score=signal_score,
                    lead_score=_lead_grade(signal_score),
                    contacts=[],
                    first_seen=signal.detected_at,
                    last_updated=now,
                )
                session.add(company)
                session.commit()
                session.refresh(company)
                return _to_company_lead(company)

            if self._is_recent_same_source(session, company, signal):
                return _to_company_lead(company)

            source_count_before = len(company.signal_sources or [])
            company.signal_count += 1
            company.software = _merge_unique(company.software, signal.software)
            company.signal_sources = _merge_unique(company.signal_sources, [signal.signal_source])
            company.migration_risk = company.migration_risk or signal.migration
            company.company_domain = company.company_domain or signal.company_domain
            company.location = signal.location or company.location
            company.industry = signal.industry or company.industry

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

    def _find_company_record(self, session: Session, signal: ExtractedSignal) -> CompanyRecord | None:
        if signal.company_domain:
            company = session.scalar(
                select(CompanyRecord).where(CompanyRecord.company_domain == signal.company_domain).limit(1)
            )
            if company is not None:
                return company

        normalized_name = _normalize_company_name(signal.company_name)
        exact = session.scalar(
            select(CompanyRecord).where(func.lower(CompanyRecord.company_name) == normalized_name).limit(1)
        )
        if exact is not None:
            return exact

        candidates = session.scalars(select(CompanyRecord)).all()
        for candidate in candidates:
            if _names_similar(candidate.company_name, signal.company_name):
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


def _normalize_company_name(value: str) -> str:
    return " ".join(value.strip().lower().split())


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
    return SequenceMatcher(a=left_norm, b=right_norm).ratio() >= 0.88


def _to_company_lead(record: CompanyRecord) -> CompanyLead:
    return CompanyLead(
        company_name=record.company_name,
        company_domain=record.company_domain,
        location=record.location,
        industry=record.industry,
        software=list(record.software or []),
        signal_sources=list(record.signal_sources or []),
        signal_count=record.signal_count,
        migration_risk=record.migration_risk,
        total_score=record.total_score,
        lead_score=record.lead_score,
        contacts=list(record.contacts or []),
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
        location=signal.location,
        industry=signal.industry,
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
