from __future__ import annotations

from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, HttpUrl


SignalType = Literal["job_posting", "career_page", "news"]
SignalSource = Literal["linkedin", "indeed", "google", "stepstone", "career_page", "news"]
LeadScore = Literal["hot", "warm", "cold"]


class RawJobPosting(BaseModel):
    model_config = ConfigDict(extra="ignore", str_strip_whitespace=True)

    source: SignalSource
    signal_type: SignalType = "job_posting"
    query: str
    title: str
    company_name: str | None = None
    # JobSpy exposes both the job-board company profile and, when available,
    # the company's direct website. Keep both so the direct website can be
    # trusted before falling back to external domain resolution.
    company_url: str | None = None
    company_url_direct: str | None = None
    company_industry: str | None = None
    location: str | None = None
    snippet: str | None = None
    # Full job description — populated by JobSpy (linkedin_fetch_description=True
    # for LinkedIn; Indeed/Google return it by default). Used as the primary
    # text input to the NLP extraction layer so Gemini can distinguish
    # manufacturers from consulting firms and detect detailed PLM signals.
    description: str | None = None
    job_url: HttpUrl
    posted_date: str | None = None
    scraped_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class RawSignalDocument(BaseModel):
    model_config = ConfigDict(extra="ignore", str_strip_whitespace=True)

    source: SignalSource
    signal_type: Literal["career_page", "news"]
    query: str
    title: str
    company_name: str | None = None
    company_industry: str | None = None
    location: str | None = None
    snippet: str | None = None
    description: str | None = None
    source_url: HttpUrl
    published_date: str | None = None
    scraped_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ExtractedSignal(BaseModel):
    model_config = ConfigDict(extra="ignore", str_strip_whitespace=True)

    company_name: str
    company_domain: str | None = None
    # Preserve JobSpy's company profile URL exactly as supplied. When no direct
    # employer URL is available, its host is also used as the fallback domain.
    company_url: str | None = None
    linkedin_url: str | None = None
    location: str | None = None
    industry: str | None = None
    company_industry: str | None = None
    software: list[str] = Field(default_factory=list)
    signal_type: SignalType
    signal_source: SignalSource
    migration: bool = False
    migration_from: str | None = None
    pain_signals: list[str] = Field(default_factory=list)
    expansion_signals: list[str] = Field(default_factory=list)
    raw_score: int = 0
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    reason: str | None = None
    domain_resolution_source: str | None = None
    domain_resolution_confidence: float | None = Field(default=None, ge=0.0, le=1.0)
    source_url: HttpUrl
    source_title: str | None = None
    detected_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class LeadContact(BaseModel):
    model_config = ConfigDict(extra="ignore", str_strip_whitespace=True)

    full_name: str
    first_name: str | None = None
    last_name: str | None = None
    title: str | None = None
    email: str | None = None
    linkedin_url: str | None = None
    phone: str | None = None
    source_provider: str
    source_stage: str


class CompanyLead(BaseModel):
    model_config = ConfigDict(extra="ignore", str_strip_whitespace=True)

    company_name: str
    company_domain: str | None = None
    company_url: str | None = None
    linkedin_url: str | None = None
    location: str | None = None
    industry: str | None = None
    company_industry: str | None = None
    sector: str | None = None
    headquarters_location: str | None = None
    employee_count: str | None = None
    revenue_range: str | None = None
    software: list[str] = Field(default_factory=list)
    signal_sources: list[str] = Field(default_factory=list)
    signal_count: int = 0
    migration_risk: bool = False
    total_score: int = 0
    lead_score: LeadScore = "cold"
    contacts: list[LeadContact] = Field(default_factory=list)
    enrichment_source: str | None = None
    enrichment_confidence: float | None = Field(default=None, ge=0.0, le=1.0)
    enriched_at: datetime | None = None
    last_enrichment_at: datetime | None = None
    first_seen: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_updated: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
