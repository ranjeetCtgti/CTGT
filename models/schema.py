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
    location: str | None = None
    industry: str | None = None
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
    source_url: HttpUrl
    source_title: str | None = None
    detected_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class CompanyLead(BaseModel):
    model_config = ConfigDict(extra="ignore", str_strip_whitespace=True)

    company_name: str
    company_domain: str | None = None
    location: str | None = None
    industry: str | None = None
    software: list[str] = Field(default_factory=list)
    signal_sources: list[str] = Field(default_factory=list)
    signal_count: int = 0
    migration_risk: bool = False
    total_score: int = 0
    lead_score: LeadScore = "cold"
    contacts: list[dict] = Field(default_factory=list)
    first_seen: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_updated: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
