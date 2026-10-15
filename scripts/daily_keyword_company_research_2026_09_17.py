from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import func, select


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from db.database import (
    CompanyRecord,
    Database,
    KeywordCompanyResultRecord,
    SignalRecord,
)
from enrichment.identity_verification import CompanyIdentityEvidence, verify_company_identity
from models.schema import ExtractedSignal


RUN_AT = datetime.now(timezone.utc)
LOCK_PATH = Path(
    r"C:\Users\ranjeet.chaudhary\.codex\automations\daily-keyword-company-research\run.lock"
)


GALAXIA_OFFICIAL_URL = (
    "https://gx.space/news-press-releases/"
    "galaxia-closes-funding-round-to-support-accelerated-growth"
)
GALAXIA_BETAKIT_URL = (
    "https://betakit.com/galaxia-raises-4-5-million-to-bring-satellite-"
    "computers-to-canadas-space-race/"
)
CRC_BETAKIT_URL = (
    "https://betakit.com/canada-rocket-company-wants-to-build-a-sovereign-"
    "alternative-to-spacexs-falcon-9/"
)


PROSPECTS = [
    {
        "company_name": "Galaxia Space Systems",
        "company_domain": "gx.space",
        "company_url": "https://gx.space/",
        "location": "Halifax, Nova Scotia, Canada",
        "industry": "Satellite platforms and orbital compute infrastructure",
        "products": ["Teamcenter", "Polarion", "Simcenter"],
        "identity": CompanyIdentityEvidence(
            official_name="Galaxia Space Systems",
            official_website_url="https://gx.space/",
            corroborating_urls=(GALAXIA_BETAKIT_URL,),
        ),
        "signals": [
            {
                "source_url": GALAXIA_OFFICIAL_URL,
                "source_title": "Galaxia closes funding round to support accelerated growth",
                "source_publisher": "Galaxia Space Systems",
                "signal_date": datetime(2026, 9, 10, tzinfo=timezone.utc),
                "reason": (
                    "On September 10, 2026, Galaxia closed an oversubscribed C$4.5 million "
                    "round co-led by Amiral Ventures and Invest Nova Scotia to accelerate "
                    "deployment of advanced satellite systems, hybrid space-networking capacity, "
                    "and mission-ready sovereign systems for commercial and government customers. "
                    "The company says its platform unifies onboard compute, networked communications, "
                    "and mission software; inference: scaling concurrent spacecraft and network "
                    "configurations increases BOM/change-control pressure, requirements-to-test "
                    "traceability, and multidisciplinary validation workload."
                ),
                "pain": (
                    "Must control spacecraft, onboard-compute, networking, and mission-software "
                    "configurations while preserving requirements and test evidence across programs."
                ),
                "expansion": (
                    "Closed a C$4.5 million round to deploy satellite systems and hybrid space "
                    "networking capacity for commercial and government customers."
                ),
            },
            {
                "source_url": GALAXIA_BETAKIT_URL,
                "source_title": (
                    "Galaxia raises $4.5 million to bring satellite computers to Canada's space race"
                ),
                "source_publisher": "BetaKit",
                "signal_date": datetime(2026, 9, 10, tzinfo=timezone.utc),
                "reason": (
                    "On September 10, 2026, BetaKit independently reported that Halifax-based "
                    "Galaxia Space Systems raised C$4.5 million to deploy AI-enabled satellite "
                    "systems and hybrid space-networking capacity, reducing dependence on Earth "
                    "downlinks by processing and analyzing data in orbit. The expansion toward "
                    "commercial and government missions corroborates a near-term scale-up in "
                    "physical spacecraft, onboard-compute variants, and mission validation."
                ),
                "pain": (
                    "Must coordinate physical satellite, onboard-compute, networking, and mission "
                    "software variants as customer deployments scale."
                ),
                "expansion": (
                    "Raised C$4.5 million for satellite-system deployment and hybrid space-network capacity."
                ),
            },
        ],
        "keyword_ids": (8, 9, 14),
        "keyword_source_url": GALAXIA_OFFICIAL_URL,
        "keyword_source_title": "Galaxia closes funding round to support accelerated growth",
        "keyword_source_publisher": "Galaxia Space Systems",
        "signal_label": "C$4.5M funds satellite-system and orbital-network deployment",
        "signal_date": datetime(2026, 9, 10, tzinfo=timezone.utc),
        "challenge_summary": (
            "On September 10, 2026, Galaxia closed an oversubscribed C$4.5 million round "
            "co-led by Amiral Ventures and Invest Nova Scotia to accelerate advanced satellite "
            "systems, hybrid space-networking capacity, and mission-ready sovereign systems for "
            "commercial and government customers. Its platform combines onboard compute, "
            "communications, and mission software; inference: scaling deployments creates more "
            "spacecraft/network configurations, BOM and change-control pressure, requirements-to-test "
            "traceability, and multidisciplinary validation work. The dated funding makes those "
            "controls urgent before the next systems are deployed."
        ),
        "why_relevant": (
            "Teamcenter can govern spacecraft BOMs, revisions, variants, and supplier evidence; "
            "Polarion can connect mission requirements to verification and defects; Simcenter can "
            "support thermal, structural, and system-level validation. The immediate business outcome "
            "is faster deployment with fewer configuration escapes and a defensible verification trail "
            "for government and defence customers."
        ),
        "qualification_status": "qualified",
        "opportunity_score": 94,
        "manufacturing_fit_score": 96,
        "trigger_score": 96,
        "solution_fit_score": 94,
        "evidence_quality_score": 98,
    },
    {
        "company_name": "Canada Rocket Company",
        "company_domain": "canadarocketcompany.com",
        "company_url": "https://www.canadarocketcompany.com/",
        "location": "Etobicoke, Ontario, Canada",
        "industry": "Reusable medium-lift launch vehicles and rocket propulsion",
        "products": ["Teamcenter", "Simcenter", "Tecnomatix", "Polarion"],
        "identity": CompanyIdentityEvidence(
            official_name="Canada Rocket Company",
            official_website_url="https://www.canadarocketcompany.com/",
            corroborating_urls=(CRC_BETAKIT_URL,),
        ),
        "signals": [
            {
                "source_url": CRC_BETAKIT_URL,
                "source_title": (
                    "Canada Rocket Company wants to build a sovereign alternative to SpaceX's Falcon 9"
                ),
                "source_publisher": "BetaKit",
                "signal_date": datetime(2026, 9, 16, tzinfo=timezone.utc),
                "reason": (
                    "On September 16, 2026, BetaKit reported that Canada Rocket Company had moved "
                    "into a 7,400-square-foot Etobicoke facility, grown to 34 employees, secured "
                    "about C$22.5 million, and begun developing and testing rocket-engine technology. "
                    "CRC plans a 500,000-square-foot manufacturing facility, expects component testing "
                    "by year-end, and is targeting a 2032 first launch for its reusable R-2 vehicle, "
                    "which now targets roughly 12,000 kilograms of payload. Inference: propulsion, "
                    "structures, avionics, supplier configuration, verification, and greenfield factory "
                    "planning must mature together while the team and physical footprint expand."
                ),
                "pain": (
                    "Must coordinate propulsion, structures, avionics, supplier configuration, "
                    "requirements, test evidence, and a major new manufacturing footprint."
                ),
                "expansion": (
                    "Reached 34 employees and C$22.5 million in capital, opened a 7,400-square-foot "
                    "engineering facility, and began planning a 500,000-square-foot factory."
                ),
            }
        ],
        "keyword_ids": (7, 8, 9, 14),
        "keyword_source_url": CRC_BETAKIT_URL,
        "keyword_source_title": (
            "Canada Rocket Company wants to build a sovereign alternative to SpaceX's Falcon 9"
        ),
        "keyword_source_publisher": "BetaKit",
        "signal_label": "34-person rocket program plans 500,000-sq-ft manufacturing plant",
        "signal_date": datetime(2026, 9, 16, tzinfo=timezone.utc),
        "challenge_summary": (
            "On September 16, 2026, BetaKit reported that Canada Rocket Company had moved into a "
            "7,400-square-foot Etobicoke facility, grown to 34 employees, secured about C$22.5 million, "
            "and started rocket-engine development and testing; it is already planning a 500,000-square-foot "
            "manufacturing facility. CRC targets component testing by year-end and a 2032 first launch "
            "for the reusable R-2, now sized for roughly 12,000 kilograms of payload. Inference: propulsion, "
            "structures, avionics, suppliers, verification, and factory planning must scale together, "
            "making configuration and test discipline urgent before the architecture and plant harden."
        ),
        "why_relevant": (
            "Teamcenter can govern the vehicle BOM, engineering changes, variants, and supplier evidence; "
            "Simcenter can support propulsion, fluid, thermal, and structural validation; Tecnomatix can "
            "model the planned factory and assembly flow; Polarion can connect requirements, hazards, tests, "
            "and defects. The practical outcome is a faster design-to-test ramp with fewer configuration "
            "escapes and less rework before large capital is committed to the plant."
        ),
        "qualification_status": "qualified",
        "opportunity_score": 99,
        "manufacturing_fit_score": 100,
        "trigger_score": 100,
        "solution_fit_score": 100,
        "evidence_quality_score": 98,
    },
]


def make_signal(prospect: dict, evidence: dict) -> ExtractedSignal:
    return ExtractedSignal(
        company_name=prospect["company_name"],
        company_domain=prospect["company_domain"],
        company_url=prospect["company_url"],
        location=prospect["location"],
        industry=prospect["industry"],
        company_industry=prospect["industry"],
        software=prospect["products"],
        signal_type="news",
        signal_source="news",
        pain_signals=[evidence["pain"]],
        expansion_signals=[evidence["expansion"]],
        raw_score=prospect["opportunity_score"],
        confidence=prospect["evidence_quality_score"] / 100,
        reason=evidence["reason"],
        source_url=evidence["source_url"],
        source_title=evidence["source_title"],
        detected_at=evidence["signal_date"],
    )


def main() -> None:
    load_dotenv(REPO_ROOT / ".env")
    marker = json.loads(LOCK_PATH.read_text(encoding="utf-8"))
    if int(marker.get("pid", 0)) <= 0:
        raise RuntimeError("Exclusive automation lock is not held")

    database = Database(os.environ["DATABASE_URL"])
    database.initialize()
    keywords_before = {row.id: row for row in database.list_keywords()}
    expected = {1, 2, 3, 4, 5, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16}
    if set(keywords_before) != expected:
        raise RuntimeError(f"Persistent keyword set changed: {sorted(keywords_before)}")

    published = {keyword_id: 0 for keyword_id in keywords_before}
    persisted: list[dict] = []
    for prospect in PROSPECTS:
        for evidence in prospect["signals"]:
            verify_company_identity(make_signal(prospect, evidence), prospect["identity"])

        evidence_results = []
        company = None
        for evidence in prospect["signals"]:
            saved, company = database.persist_verified_signal(
                make_signal(prospect, evidence), prospect["identity"]
            )
            evidence_results.append(
                {
                    "source_url": evidence["source_url"],
                    "created": saved.created,
                    "duplicate_url": saved.duplicate_url,
                }
            )
        if company is None:
            raise RuntimeError(f"No company result for {prospect['company_name']}")

        links = []
        for keyword_id in prospect["keyword_ids"]:
            row = database.record_keyword_company(
                keyword_id,
                prospect["company_name"],
                prospect["company_domain"],
                source_url=prospect["keyword_source_url"],
                source_title=prospect["keyword_source_title"],
                source_publisher=prospect["keyword_source_publisher"],
                signal_label=prospect["signal_label"],
                signal_date=prospect["signal_date"],
                challenge_summary=prospect["challenge_summary"],
                why_relevant=prospect["why_relevant"],
                recommended_products=prospect["products"],
                qualification_status=prospect["qualification_status"],
                opportunity_score=prospect["opportunity_score"],
                manufacturing_fit_score=prospect["manufacturing_fit_score"],
                trigger_score=prospect["trigger_score"],
                solution_fit_score=prospect["solution_fit_score"],
                evidence_quality_score=prospect["evidence_quality_score"],
                seen_at=RUN_AT,
            )
            if row is None:
                raise RuntimeError(
                    f"Could not link {prospect['company_name']} to keyword {keyword_id}"
                )
            published[keyword_id] += 1
            links.append(
                {
                    "keyword_id": keyword_id,
                    "company_id": row.company_id,
                    "status": row.qualification_status,
                    "opportunity_score": row.opportunity_score,
                }
            )
        persisted.append(
            {
                "company_id": links[0]["company_id"],
                "company_name": company.company_name,
                "company_domain": company.company_domain,
                "signal_count": company.signal_count,
                "evidence": evidence_results,
                "links": links,
            }
        )

    for keyword_id in sorted(keywords_before):
        if database.record_keyword_search(
            keyword_id, result_count=published[keyword_id], error=None
        ) is None:
            raise RuntimeError(f"Could not record keyword search {keyword_id}")

    keywords_after = {row.id: row for row in database.list_keywords()}
    for keyword_id, prior in keywords_before.items():
        current = keywords_after[keyword_id]
        if current.search_count != prior.search_count + 1:
            raise RuntimeError(f"Keyword {keyword_id} did not advance exactly once")
        if current.last_error is not None:
            raise RuntimeError(f"Keyword {keyword_id} retained error: {current.last_error}")

    with database.session() as session:
        duplicate_domains = session.execute(
            select(func.lower(CompanyRecord.company_domain), func.count(CompanyRecord.id))
            .where(CompanyRecord.company_domain.is_not(None))
            .group_by(func.lower(CompanyRecord.company_domain))
            .having(func.count(CompanyRecord.id) > 1)
        ).all()
        duplicate_sources = session.execute(
            select(SignalRecord.source_url, func.count(SignalRecord.id))
            .group_by(SignalRecord.source_url)
            .having(func.count(SignalRecord.id) > 1)
        ).all()
        duplicate_keyword_pairs = session.execute(
            select(
                KeywordCompanyResultRecord.keyword_id,
                KeywordCompanyResultRecord.company_id,
                func.count(KeywordCompanyResultRecord.id),
            )
            .group_by(
                KeywordCompanyResultRecord.keyword_id,
                KeywordCompanyResultRecord.company_id,
            )
            .having(func.count(KeywordCompanyResultRecord.id) > 1)
        ).all()

    if duplicate_domains or duplicate_sources or duplicate_keyword_pairs:
        raise RuntimeError(
            "Post-write duplicate audit failed: "
            f"domains={duplicate_domains}, sources={duplicate_sources}, "
            f"keyword_pairs={duplicate_keyword_pairs}"
        )

    print(
        json.dumps(
            {
                "run_at": RUN_AT.isoformat(),
                "persisted": persisted,
                "keyword_audits": [
                    {
                        "id": keyword_id,
                        "keyword": keywords_after[keyword_id].keyword,
                        "search_count_before": keywords_before[keyword_id].search_count,
                        "search_count_after": keywords_after[keyword_id].search_count,
                        "published": published[keyword_id],
                        "last_error": keywords_after[keyword_id].last_error,
                    }
                    for keyword_id in sorted(keywords_after)
                ],
                "duplicate_audit": {
                    "canonical_domains": 0,
                    "source_urls": 0,
                    "keyword_company_pairs": 0,
                },
            },
            indent=2,
            default=str,
        )
    )


if __name__ == "__main__":
    main()
