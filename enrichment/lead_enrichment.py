from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from difflib import SequenceMatcher
from typing import Any
from urllib.parse import urlparse

import httpx
from loguru import logger

from enrichment.domain_resolution import canonicalize_domain, resolve_company_domain
from models.schema import CompanyLead, LeadContact


GOOGLE_CUSTOM_SEARCH_URL = "https://customsearch.googleapis.com/customsearch/v1"
APOLLO_ORGANIZATION_ENRICH_URL = "https://api.apollo.io/api/v1/organizations/enrich"
APOLLO_PEOPLE_SEARCH_URL = "https://api.apollo.io/api/v1/mixed_people/api_search"
APOLLO_BULK_PEOPLE_MATCH_URL = "https://api.apollo.io/api/v1/people/bulk_match"
HUNTER_DOMAIN_SEARCH_URL = "https://api.hunter.io/v2/domain-search"
GOOGLE_LINKEDIN_HOST = "linkedin.com"
APOLLO_MAX_CONTACTS = 5
APOLLO_BASE_TARGET_TITLES = [
    "PLM Manager",
    "PLM Lead",
    "PLM Product Owner",
    "PLM Architect",
    "Director, PLM",
    "Head of PLM",
    "Engineering Systems Manager",
    "Engineering Applications Manager",
    "Engineering IT Manager",
    "CAD Manager",
    "Director of Engineering Systems",
    "Director of Engineering Applications",
    "Head of Engineering Systems",
    "Head of Engineering Applications",
    "Digital Engineering Manager",
]
APOLLO_EXEC_TARGET_TITLES = [
    "Chief Technology Officer",
    "Chief Information Officer",
    "Chief Digital Officer",
    "VP Engineering",
    "VP Product Development",
    "VP IT",
    "VP Digital Transformation",
    "Head of Engineering",
    "Head of Product Development",
    "Head of IT",
    "Head of Digital Transformation",
    "Director of Engineering",
    "Director of Product Development",
    "Director of IT",
    "Director of Digital Transformation",
    "IT Director",
    "Applications Director",
]
APOLLO_BUSINESS_TARGET_TITLES = [
    "VP Operations",
    "Director of Operations",
    "Head of Operations",
    "Manufacturing Director",
    "Director of Manufacturing Engineering",
    "Plant Director",
]
APOLLO_COMMERCIAL_TARGET_TITLES = [
    "Chief Revenue Officer",
    "VP Sales",
    "Director of Sales",
    "Head of Sales",
    "VP Marketing",
    "Director of Marketing",
    "Head of Marketing",
    "Business Development Director",
]
APOLLO_PEOPLE_TARGET_TITLES = [
    "Chief Human Resources Officer",
    "VP Human Resources",
    "HR Director",
    "Head of Talent Acquisition",
    "Director of Talent Acquisition",
    "People Director",
]
APOLLO_SOFTWARE_TARGET_TITLES = {
    "Teamcenter": [
        "Teamcenter Administrator",
        "Teamcenter Lead",
        "Teamcenter Manager",
        "Teamcenter Architect",
        "Teamcenter Product Owner",
    ],
    "NX": [
        "NX Administrator",
        "NX Manager",
        "NX Architect",
        "CAD Systems Manager",
    ],
    "Solid Edge": [
        "Solid Edge Administrator",
        "Solid Edge Manager",
        "CAD Applications Manager",
    ],
    "Polarion": [
        "Polarion Administrator",
        "Polarion Manager",
        "ALM Manager",
        "ALM Product Owner",
    ],
    "Mendix": [
        "Mendix Product Owner",
        "Mendix Platform Owner",
        "Mendix Manager",
    ],
}
APOLLO_RELEVANT_TITLE_HINTS = (
    "plm",
    "product lifecycle",
    "teamcenter",
    "polarion",
    "mendix",
    "technology officer",
    "information officer",
    "digital officer",
    "engineering systems",
    "engineering applications",
    "engineering it",
    "digital engineering",
    "digital thread",
    "digital transformation",
    "cad manager",
    "cad systems",
    "cad applications",
    "nx ",
    "solid edge",
    "alm",
    "product development",
    "operations",
    "manufacturing",
    "sales",
    "marketing",
    "human resources",
    "talent acquisition",
    "people director",
    "business development",
)
APOLLO_TARGET_SENIORITIES = (
    "c_suite",
    "vp",
    "head",
    "director",
    "manager",
)
APOLLO_TITLE_EXCLUSIONS = (
    "software engineer",
    "software developer",
    "full stack",
    "frontend",
    "front end",
    "backend",
    "back end",
    "data engineer",
    "devops",
    "site reliability",
    "qa ",
    "quality assurance",
    "recruit",
    "customer success",
    "support engineer",
    "sales development representative",
    "business development representative",
    "account executive",
    "account manager",
    "content marketing",
    "field marketing",
    "recruiting coordinator",
    "recruiting specialist",
    "hr business partner",
    "people partner",
)


@dataclass(slots=True)
class CompanyProfile:
    canonical_name: str | None = None
    domain: str | None = None
    linkedin_url: str | None = None
    sector: str | None = None
    employee_count: str | None = None
    revenue_range: str | None = None
    headquarters_location: str | None = None


@dataclass(slots=True)
class EnrichmentStageResult:
    stage: str
    provider: str
    status: str
    message: str | None = None
    payload: dict[str, Any] | None = None


@dataclass(slots=True)
class CompanyEnrichmentOutcome:
    company_name: str
    company_domain: str | None
    profile: CompanyProfile = field(default_factory=CompanyProfile)
    contacts: list[LeadContact] = field(default_factory=list)
    stages: list[EnrichmentStageResult] = field(default_factory=list)


@dataclass(slots=True)
class LeadEnrichmentPassSummary:
    candidates: int = 0
    attempted: int = 0
    completed: int = 0
    skipped: int = 0
    errors: int = 0
    contacts_found: int = 0


class GoogleSearchLinkedInResolver:
    def __init__(self, api_key: str, search_engine_id: str, timeout_seconds: int) -> None:
        self._http = httpx.Client(timeout=timeout_seconds)
        self.api_key = api_key
        self.search_engine_id = search_engine_id

    def close(self) -> None:
        self._http.close()

    def resolve(self, company_name: str) -> str | None:
        response = self._http.get(
            GOOGLE_CUSTOM_SEARCH_URL,
            params={
                "key": self.api_key,
                "cx": self.search_engine_id,
                "q": f'site:linkedin.com/company "{company_name}"',
                "num": 5,
            },
        )
        response.raise_for_status()
        payload = response.json()
        for item in payload.get("items", []) or []:
            if not isinstance(item, dict):
                continue
            link = _clean_string(item.get("link"))
            if _is_linkedin_company_url(link):
                return link
        return None


class ApolloClient:
    def __init__(self, api_key: str, timeout_seconds: int) -> None:
        self._http = httpx.Client(
            timeout=timeout_seconds,
            headers={
                "x-api-key": api_key,
                "accept": "application/json",
                "content-type": "application/json",
                "cache-control": "no-cache",
            },
        )

    def close(self) -> None:
        self._http.close()

    def enrich_company(self, domain: str) -> CompanyProfile:
        response = self._http.get(APOLLO_ORGANIZATION_ENRICH_URL, params={"domain": domain})
        response.raise_for_status()
        payload = response.json()
        organization = _apollo_organization_object(payload)
        return CompanyProfile(
            canonical_name=_clean_string(organization.get("name")) or _clean_string(payload.get("name")),
            domain=canonicalize_domain(
                organization.get("primary_domain")
                or organization.get("domain")
                or payload.get("primary_domain")
                or payload.get("domain")
                or domain
            ),
            linkedin_url=_coalesce_strings(
                organization,
                ["linkedin_url", "linkedin", "linkedin_profile_url", "linkedin_company_url"],
            )
            or _coalesce_strings(
                payload,
                ["linkedin_url", "linkedin", "linkedin_profile_url", "linkedin_company_url"],
            ),
            sector=_coalesce_strings(organization, ["industry", "sector", "industry_tag"]),
            employee_count=_format_employee_count(organization),
            revenue_range=_format_revenue_range(organization),
            headquarters_location=_format_headquarters_location(organization),
        )

    def find_contacts(self, domain: str, software: list[str] | None = None, limit: int = APOLLO_MAX_CONTACTS) -> list[LeadContact]:
        target_titles = _apollo_target_titles(software)
        candidate_page_size = max(limit * 8, 40)
        params: list[tuple[str, str | int | bool]] = [("per_page", candidate_page_size), ("include_similar_titles", "true")]
        params.append(("q_organization_domains_list[]", domain))
        for title in target_titles:
            params.append(("person_titles[]", title))
        for seniority in APOLLO_TARGET_SENIORITIES:
            params.append(("person_seniorities[]", seniority))

        response = self._http.post(APOLLO_PEOPLE_SEARCH_URL, params=params, json={})
        response.raise_for_status()
        payload = response.json()
        ranked_people = sorted(
            [
            item for item in payload.get("people", [])
            if isinstance(item, dict) and _is_relevant_apollo_person(item, target_titles)
            ],
            key=lambda item: _apollo_person_rank(item, target_titles),
            reverse=True,
        )
        people = _select_mixed_apollo_people(ranked_people, limit=limit)
        if not people:
            return []

        details = [{"id": person["id"]} for person in people if _clean_string(person.get("id"))]
        enriched_by_id: dict[str, dict[str, Any]] = {}
        if details:
            enrich_response = self._http.post(
                APOLLO_BULK_PEOPLE_MATCH_URL,
                params={"reveal_personal_emails": "false", "reveal_phone_number": "false"},
                json={"details": details[:10]},
            )
            enrich_response.raise_for_status()
            enrich_payload = enrich_response.json()
            matches = enrich_payload.get("matches", []) or []
            enriched_by_id = {
                str(match.get("id")): match
                for match in matches
                if isinstance(match, dict) and _clean_string(match.get("id"))
            }

        contacts: list[LeadContact] = []
        for person in people:
            enriched = enriched_by_id.get(str(person.get("id")), person)
            name = _clean_string(enriched.get("name")) or _build_full_name(enriched)
            if not name:
                continue
            contacts.append(
                LeadContact(
                    full_name=name,
                    first_name=_clean_string(enriched.get("first_name")),
                    last_name=_clean_string(enriched.get("last_name")),
                    title=_clean_string(enriched.get("title")),
                    email=_clean_string(enriched.get("email")),
                    linkedin_url=_clean_string(enriched.get("linkedin_url")),
                    phone=_extract_apollo_phone(enriched),
                    source_provider="apollo",
                    source_stage="people_search",
                )
            )
        return contacts


class HunterClient:
    def __init__(self, api_key: str, timeout_seconds: int) -> None:
        self._http = httpx.Client(timeout=timeout_seconds)
        self.api_key = api_key

    def close(self) -> None:
        self._http.close()

    def find_contacts(self, domain: str, limit: int = 5) -> list[LeadContact]:
        response = self._http.get(
            HUNTER_DOMAIN_SEARCH_URL,
            params={"domain": domain, "api_key": self.api_key, "limit": limit},
        )
        response.raise_for_status()
        payload = response.json()
        data = payload.get("data") or {}
        emails = data.get("emails", []) or []
        contacts: list[LeadContact] = []
        for item in emails:
            if not isinstance(item, dict):
                continue
            name = _build_full_name(item)
            email = _clean_string(item.get("value"))
            if not name and not email:
                continue
            contacts.append(
                LeadContact(
                    full_name=name or email or domain,
                    first_name=_clean_string(item.get("first_name")),
                    last_name=_clean_string(item.get("last_name")),
                    title=_clean_string(item.get("position")),
                    email=email,
                    linkedin_url=_clean_string(item.get("linkedin")),
                    phone=None,
                    source_provider="hunter",
                    source_stage="domain_search",
                )
            )
        return contacts


def lead_enrichment_enabled() -> bool:
    return _env_flag("LEAD_ENRICHMENT_ENABLED", default=False)


def apollo_enrichment_enabled() -> bool:
    """Require an explicit opt-in; an API key alone must not activate Apollo."""
    return _env_flag("APOLLO_ENRICHMENT_ENABLED", default=False)


def should_enrich_lead(lead: CompanyLead, freshness_days: int) -> bool:
    if lead.lead_score not in {"hot", "warm"}:
        return False
    if lead.last_enrichment_at is None:
        return True
    freshness_cutoff = datetime.now(timezone.utc) - timedelta(days=freshness_days)
    if lead.last_enrichment_at <= freshness_cutoff:
        return True
    if lead.last_updated > lead.last_enrichment_at:
        return True
    return False


def enrich_company_lead(lead: CompanyLead) -> CompanyEnrichmentOutcome:
    return enrich_company_lead_with_options(lead, force_domain_refresh=False)


def enrich_company_lead_with_options(
    lead: CompanyLead,
    *,
    force_domain_refresh: bool = False,
) -> CompanyEnrichmentOutcome:
    timeout_seconds = int(os.getenv("LEAD_ENRICHMENT_TIMEOUT_SECONDS", os.getenv("ENRICHMENT_TIMEOUT_SECONDS", "10")))
    outcome = CompanyEnrichmentOutcome(
        company_name=lead.company_name,
        company_domain=None if force_domain_refresh else canonicalize_domain(lead.company_domain),
    )

    domain = outcome.company_domain
    apollo_client = _build_apollo_client(timeout_seconds=timeout_seconds)

    if not domain:
        try:
            resolved = resolve_company_domain(
                lead.company_name,
                location=lead.location,
            )
            domain = canonicalize_domain(resolved.company_domain)
            if domain:
                outcome.profile.domain = domain
                outcome.stages.append(
                    EnrichmentStageResult(
                        stage="domain_resolution",
                        provider=resolved.source,
                        status="success",
                        message=resolved.reason,
                        payload={"domain": domain, "confidence": resolved.confidence},
                    )
                )
            else:
                outcome.stages.append(
                    EnrichmentStageResult(
                        stage="domain_resolution",
                        provider=resolved.source,
                        status="miss",
                        message=resolved.reason,
                    )
                )
        except Exception as exc:
            logger.warning("domain resolution failed company={} provider=serper error={}", lead.company_name, exc)
            outcome.stages.append(
                EnrichmentStageResult(
                    stage="domain_resolution",
                    provider=(os.getenv("ENRICHMENT_PROVIDER") or "serper").strip().lower(),
                    status="error",
                    message=str(exc),
                )
            )

    if not domain:
        logger.info("lead enrichment stopped_no_domain company={}", lead.company_name)
        if apollo_client is not None:
            apollo_client.close()
        return outcome

    outcome.company_domain = domain
    outcome.profile.domain = domain

    if apollo_client is None:
        outcome.stages.append(
            EnrichmentStageResult(
                stage="company_profile",
                provider="apollo",
                status="skipped",
                message=(
                    "Apollo enrichment disabled"
                    if not apollo_enrichment_enabled()
                    else "Apollo API key not configured"
                ),
            )
        )
    else:
        try:
            logger.info("apollo domain_enrich_start company={} domain={}", lead.company_name, domain)
            profile = apollo_client.enrich_company(domain)
            outcome.profile.canonical_name = profile.canonical_name or lead.company_name
            outcome.profile.linkedin_url = profile.linkedin_url or outcome.profile.linkedin_url
            outcome.profile.sector = profile.sector
            outcome.profile.employee_count = profile.employee_count
            outcome.profile.revenue_range = profile.revenue_range
            outcome.profile.headquarters_location = profile.headquarters_location
            outcome.stages.append(
                EnrichmentStageResult(
                    stage="company_profile",
                    provider="apollo",
                    status="success",
                    payload={
                        "linkedin_url": profile.linkedin_url,
                        "sector": profile.sector,
                        "employee_count": profile.employee_count,
                        "revenue_range": profile.revenue_range,
                        "headquarters_location": profile.headquarters_location,
                    },
                )
            )
        except Exception as exc:
            logger.warning("apollo domain_enrich_failed company={} domain={} error={}", lead.company_name, domain, exc)
            outcome.stages.append(
                EnrichmentStageResult(
                    stage="company_profile",
                    provider="apollo",
                    status="error",
                    message=str(exc),
                )
            )

        try:
            logger.info("apollo contact_lookup_start company={} domain={} target_titles={}", lead.company_name, domain, _apollo_target_titles(lead.software))
            contacts = apollo_client.find_contacts(domain, software=lead.software)
            outcome.contacts = contacts
            outcome.stages.append(
                EnrichmentStageResult(
                    stage="contacts_primary",
                    provider="apollo",
                    status="success" if contacts else "miss",
                    payload={
                        "contacts_found": len(contacts),
                        "target_titles": _apollo_target_titles(lead.software),
                    },
                )
            )
        except Exception as exc:
            logger.warning("apollo contact_lookup_failed company={} domain={} error={}", lead.company_name, domain, exc)
            outcome.stages.append(
                EnrichmentStageResult(
                    stage="contacts_primary",
                    provider="apollo",
                    status="error",
                    message=str(exc),
                )
            )
        finally:
            apollo_client.close()

    if outcome.profile.linkedin_url:
        outcome.stages.append(
            EnrichmentStageResult(
                stage="linkedin_lookup",
                provider="apollo",
                status="success",
                payload={"linkedin_url": outcome.profile.linkedin_url},
            )
        )
    else:
        google_client = _build_google_search_client(timeout_seconds=timeout_seconds)
        if google_client is None:
            outcome.stages.append(
                EnrichmentStageResult(
                    stage="linkedin_lookup",
                    provider="google_search",
                    status="skipped",
                    message="Google search provider not configured",
                )
            )
        else:
            try:
                linkedin_url = google_client.resolve(lead.company_name)
                if linkedin_url:
                    outcome.profile.linkedin_url = linkedin_url
                    outcome.stages.append(
                        EnrichmentStageResult(
                            stage="linkedin_lookup",
                            provider="google_search",
                            status="success",
                            payload={"linkedin_url": linkedin_url},
                        )
                    )
                else:
                    outcome.stages.append(
                        EnrichmentStageResult(
                            stage="linkedin_lookup",
                            provider="google_search",
                            status="miss",
                            message="No LinkedIn company URL found",
                        )
                    )
            except Exception as exc:
                outcome.stages.append(
                    EnrichmentStageResult(
                        stage="linkedin_lookup",
                        provider="google_search",
                        status="error",
                        message=str(exc),
                    )
                )
            finally:
                google_client.close()

    if outcome.contacts:
        return outcome

    hunter_client = _build_hunter_client(timeout_seconds=timeout_seconds)
    if hunter_client is None:
        outcome.stages.append(
            EnrichmentStageResult(
                stage="contacts_fallback",
                provider="hunter",
                status="skipped",
                message="Hunter API key not configured",
            )
        )
        return outcome

    try:
        contacts = hunter_client.find_contacts(domain)
        outcome.contacts = contacts
        outcome.stages.append(
            EnrichmentStageResult(
                stage="contacts_fallback",
                provider="hunter",
                status="success" if contacts else "miss",
                payload={"contacts_found": len(contacts)},
            )
        )
    except Exception as exc:
        outcome.stages.append(
            EnrichmentStageResult(
                stage="contacts_fallback",
                provider="hunter",
                status="error",
                message=str(exc),
            )
        )
    finally:
        hunter_client.close()

    return outcome


def persist_enrichment_outcome(database: Any, lead: CompanyLead, outcome: CompanyEnrichmentOutcome) -> CompanyLead | None:
    for stage in outcome.stages:
        database.save_enrichment_log(
            entry=_build_log_entry(outcome, stage)
        )

    mark_enriched_at = None
    if any(stage.status == "success" for stage in outcome.stages):
        mark_enriched_at = datetime.now(timezone.utc)

    updated_lead = database.save_company_enrichment(
        company_name=lead.company_name,
        company_domain=outcome.company_domain or lead.company_domain,
        linkedin_url=outcome.profile.linkedin_url,
        sector=outcome.profile.sector,
        employee_count=outcome.profile.employee_count,
        revenue_range=outcome.profile.revenue_range,
        headquarters_location=outcome.profile.headquarters_location,
        contacts=outcome.contacts,
        enrichment_source=_build_source_summary(outcome.stages),
        mark_enriched_at=mark_enriched_at,
    )
    return updated_lead


def run_lead_enrichment_pass(
    database: Any,
    *,
    freshness_days: int | None = None,
    limit: int | None = None,
    company_names: list[str] | None = None,
    force: bool = False,
    force_domain_refresh: bool = False,
) -> LeadEnrichmentPassSummary:
    summary = LeadEnrichmentPassSummary()
    if not lead_enrichment_enabled():
        return summary

    # Qualification is the hard gate for enrichment. Normal runs also select only
    # companies that have never been enriched; --force remains an explicit manual
    # override for re-enriching an already-qualified company.
    leads = database.get_qualified_keyword_leads(
        limit=None if company_names else limit,
        only_unenriched=not force,
    )
    if company_names:
        requested = {_normalize_company_name(name) for name in company_names if _normalize_company_name(name)}
        leads = [lead for lead in leads if _normalize_company_name(lead.company_name) in requested]
        if limit is not None:
            leads = leads[:limit]
    candidates = leads
    summary.candidates = len(candidates)

    for lead in candidates:
        summary.attempted += 1
        try:
            outcome = enrich_company_lead_with_options(
                lead,
                force_domain_refresh=force_domain_refresh,
            )
            persist_enrichment_outcome(database, lead, outcome)
            _log_enrichment_outcome(outcome)
            summary.completed += 1
            summary.contacts_found += len(outcome.contacts)
        except Exception as exc:
            logger.warning("lead enrichment failed company={} error={}", lead.company_name, exc)
            summary.errors += 1

    return summary


def _build_log_entry(outcome: CompanyEnrichmentOutcome, stage: EnrichmentStageResult) -> Any:
    from db import EnrichmentLogEntry

    return EnrichmentLogEntry(
        company_name=outcome.company_name,
        company_domain=outcome.company_domain,
        stage=stage.stage,
        provider=stage.provider,
        status=stage.status,
        message=stage.message,
        payload=stage.payload,
    )


def _log_enrichment_outcome(outcome: CompanyEnrichmentOutcome) -> None:
    profile = outcome.profile
    resolution_stage = next((stage for stage in reversed(outcome.stages) if stage.stage == "domain_resolution"), None)
    resolution_provider = resolution_stage.provider if resolution_stage is not None else "-"
    resolution_status = resolution_stage.status if resolution_stage is not None else "-"
    logger.info(
        (
            "enrichment result company={} domain={} domain_provider={} domain_status={} linkedin_url={} sector={} "
            "employee_count={} revenue_range={} headquarters_location={} contacts_found={}"
        ),
        outcome.company_name,
        outcome.company_domain or "-",
        resolution_provider,
        resolution_status,
        profile.linkedin_url or "-",
        profile.sector or "-",
        profile.employee_count or "-",
        profile.revenue_range or "-",
        profile.headquarters_location or "-",
        len(outcome.contacts),
    )

    for contact in outcome.contacts:
        logger.info(
            "contact company={} name={} title={} email={} linkedin_url={} phone={} provider={} stage={}",
            outcome.company_name,
            contact.full_name,
            contact.title or "-",
            contact.email or "-",
            contact.linkedin_url or "-",
            contact.phone or "-",
            contact.source_provider,
            contact.source_stage,
        )


def _build_google_search_client(timeout_seconds: int) -> GoogleSearchLinkedInResolver | None:
    api_key = (os.getenv("GOOGLE_SEARCH_API_KEY") or "").strip()
    search_engine_id = (os.getenv("GOOGLE_SEARCH_ENGINE_ID") or "").strip()
    if not api_key or not search_engine_id:
        return None
    return GoogleSearchLinkedInResolver(api_key=api_key, search_engine_id=search_engine_id, timeout_seconds=timeout_seconds)


def _build_apollo_client(timeout_seconds: int) -> ApolloClient | None:
    if not apollo_enrichment_enabled():
        return None
    api_key = (os.getenv("APOLLO_API_KEY") or "").strip()
    if not api_key:
        return None
    return ApolloClient(api_key=api_key, timeout_seconds=timeout_seconds)


def _build_hunter_client(timeout_seconds: int) -> HunterClient | None:
    api_key = (os.getenv("HUNTER_API_KEY") or "").strip()
    if not api_key:
        return None
    return HunterClient(api_key=api_key, timeout_seconds=timeout_seconds)


def _apollo_organization_object(payload: dict[str, Any]) -> dict[str, Any]:
    for key in ("organization", "account", "company"):
        value = payload.get(key)
        if isinstance(value, dict):
            return value
    return payload


def _format_employee_count(payload: dict[str, Any]) -> str | None:
    for key in ("estimated_num_employees", "employee_count", "employees_count", "organization_num_employees"):
        value = payload.get(key)
        if isinstance(value, int):
            return str(value)
        cleaned = _clean_string(value)
        if cleaned:
            return cleaned
    return None


def _format_revenue_range(payload: dict[str, Any]) -> str | None:
    for key in ("estimated_annual_revenue", "annual_revenue", "revenue_range", "organization_revenue_printed"):
        cleaned = _clean_string(payload.get(key))
        if cleaned:
            return cleaned
    min_value = payload.get("revenue_range", {}).get("min") if isinstance(payload.get("revenue_range"), dict) else None
    max_value = payload.get("revenue_range", {}).get("max") if isinstance(payload.get("revenue_range"), dict) else None
    if min_value is not None or max_value is not None:
        return f"{min_value or 0}-{max_value or 0}"
    return None


def _format_headquarters_location(payload: dict[str, Any]) -> str | None:
    fields = [
        _clean_string(payload.get("raw_address")),
        _clean_string(payload.get("city")),
        _clean_string(payload.get("state")),
        _clean_string(payload.get("country")),
    ]
    values = [field for field in fields if field]
    if values:
        return ", ".join(dict.fromkeys(values))
    return _clean_string(payload.get("headquarters_location"))


def _extract_apollo_phone(payload: dict[str, Any]) -> str | None:
    direct = _clean_string(payload.get("phone_number"))
    if direct:
        return direct
    organization = payload.get("organization")
    if isinstance(organization, dict):
        phone = _clean_string(organization.get("phone"))
        if phone:
            return phone
    contact = payload.get("contact")
    if isinstance(contact, dict):
        phone = _clean_string(contact.get("sanitized_phone"))
        if phone:
            return phone
        phone_numbers = contact.get("phone_numbers") or []
        for item in phone_numbers:
            if isinstance(item, dict):
                phone = _clean_string(item.get("sanitized_number") or item.get("raw_number"))
                if phone:
                    return phone
    return None


def _build_source_summary(stages: list[EnrichmentStageResult]) -> str:
    providers = [stage.provider for stage in stages if stage.status == "success"]
    if not providers:
        return "lead_enrichment"
    ordered = list(dict.fromkeys(providers))
    return ",".join(ordered)


def _is_linkedin_company_url(value: str | None) -> bool:
    if not value:
        return False
    parsed = urlparse(value)
    host = parsed.netloc.lower()
    path = parsed.path.lower()
    return GOOGLE_LINKEDIN_HOST in host and "/company/" in path


def _coalesce_strings(payload: dict[str, Any], keys: list[str]) -> str | None:
    for key in keys:
        cleaned = _clean_string(payload.get(key))
        if cleaned:
            return cleaned
    return None


def _build_full_name(payload: dict[str, Any]) -> str | None:
    first_name = _clean_string(payload.get("first_name"))
    last_name = _clean_string(payload.get("last_name"))
    name = " ".join(part for part in [first_name, last_name] if part)
    return name or _clean_string(payload.get("name"))


def _clean_string(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    cleaned = " ".join(value.split()).strip()
    return cleaned or None


def _normalize_company_name(value: str) -> str:
    cleaned = value.strip().lower()
    tokens = re.findall(r"[a-z0-9]+", cleaned)
    if not tokens:
        return ""
    legal_suffixes = {"gmbh", "inc", "ltd", "llc", "ag", "corp", "corporation", "limited", "co", "kg", "se", "plc", "sa", "bv", "srl", "pty"}
    normalized_tokens = [token for token in tokens if token not in legal_suffixes]
    if not normalized_tokens:
        normalized_tokens = tokens
    return " ".join(normalized_tokens)


def _name_similarity(left: str, right: str) -> float:
    left_norm = _normalize_company_name(left)
    right_norm = _normalize_company_name(right)
    if not left_norm or not right_norm:
        return 0.0
    if left_norm == right_norm:
        return 1.0
    return SequenceMatcher(a=left_norm, b=right_norm).ratio()


def _apollo_target_titles(software: list[str] | None) -> list[str]:
    ordered_titles = list(APOLLO_BASE_TARGET_TITLES)
    ordered_titles.extend(APOLLO_EXEC_TARGET_TITLES)
    ordered_titles.extend(APOLLO_BUSINESS_TARGET_TITLES)
    ordered_titles.extend(APOLLO_COMMERCIAL_TARGET_TITLES)
    ordered_titles.extend(APOLLO_PEOPLE_TARGET_TITLES)
    for product in software or []:
        ordered_titles.extend(APOLLO_SOFTWARE_TARGET_TITLES.get(product, []))

    deduped: list[str] = []
    seen: set[str] = set()
    for title in ordered_titles:
        key = title.strip().lower()
        if not key or key in seen:
            continue
        seen.add(key)
        deduped.append(title)
    return deduped


def _is_relevant_apollo_person(person: dict[str, Any], target_titles: list[str]) -> bool:
    title = (_clean_string(person.get("title")) or "").lower()
    if not title:
        return False
    if any(excluded in title for excluded in APOLLO_TITLE_EXCLUSIONS):
        return False

    normalized_targets = {item.lower() for item in target_titles}
    if title in normalized_targets:
        return True

    return any(hint in title for hint in APOLLO_RELEVANT_TITLE_HINTS)


def _apollo_person_rank(person: dict[str, Any], target_titles: list[str]) -> tuple[int, int, int]:
    title = (_clean_string(person.get("title")) or "").lower()
    normalized_targets = {item.lower() for item in target_titles}
    seniority = (_clean_string(person.get("seniority")) or "").lower()

    exact_match = 1 if title in normalized_targets else 0
    hint_match = 1 if any(hint in title for hint in APOLLO_RELEVANT_TITLE_HINTS) else 0
    seniority_score = _apollo_seniority_rank(seniority)
    return (exact_match, seniority_score, hint_match)


def _select_mixed_apollo_people(people: list[dict[str, Any]], limit: int) -> list[dict[str, Any]]:
    if len(people) <= limit:
        return people

    buckets = {
        "technical": [],
        "business": [],
        "commercial": [],
        "people": [],
        "other": [],
    }
    for person in people:
        buckets[_apollo_person_bucket(person)].append(person)

    selected: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    bucket_targets = (
        ("technical", 2),
        ("business", 1),
        ("commercial", 1),
        ("people", 1),
    )

    for bucket_name, target_count in bucket_targets:
        for _ in range(target_count):
            if len(selected) >= limit:
                return selected
            person = _pop_first_unseen_person(buckets[bucket_name], seen_ids)
            if person is None:
                break
            selected.append(person)
            person_id = _clean_string(person.get("id"))
            if person_id:
                seen_ids.add(person_id)

    refill_order = ("technical", "business", "commercial", "people", "other")
    while len(selected) < limit:
        added = False
        for bucket_name in refill_order:
            person = _pop_first_unseen_person(buckets[bucket_name], seen_ids)
            if person is None:
                continue
            selected.append(person)
            person_id = _clean_string(person.get("id"))
            if person_id:
                seen_ids.add(person_id)
            added = True
            if len(selected) >= limit:
                break
        if not added:
            break

    return selected


def _pop_first_unseen_person(people: list[dict[str, Any]], seen_ids: set[str]) -> dict[str, Any] | None:
    while people:
        person = people.pop(0)
        person_id = _clean_string(person.get("id"))
        if person_id and person_id in seen_ids:
            continue
        return person
    return None


def _apollo_person_bucket(person: dict[str, Any]) -> str:
    title = (_clean_string(person.get("title")) or "").lower()
    if any(token in title for token in ("sales", "marketing", "revenue", "business development")):
        return "commercial"
    if any(token in title for token in ("human resources", "talent", "people ", "people director", "hr ")):
        return "people"
    if any(token in title for token in ("operations", "manufacturing", "plant", "product development")):
        return "business"
    if any(
        token in title
        for token in (
            "plm",
            "teamcenter",
            "polarion",
            "mendix",
            "engineering",
            "technology",
            "information",
            "digital",
            "cad",
            "nx ",
            "solid edge",
            "alm",
            "it ",
            "cto",
            "cio",
        )
    ):
        return "technical"
    return "other"


def _apollo_seniority_rank(seniority: str) -> int:
    order = {
        "owner": 7,
        "founder": 6,
        "c_suite": 5,
        "vp": 4,
        "head": 3,
        "director": 2,
        "manager": 1,
    }
    return order.get(seniority, 0)


def _env_flag(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}
