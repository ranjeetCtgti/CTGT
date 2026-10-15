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

from db.database import CompanyRecord, Database, KeywordCompanyResultRecord, SignalRecord
from enrichment.identity_verification import CompanyIdentityEvidence, verify_company_identity
from models.schema import ExtractedSignal


RUN_AT = datetime.now(timezone.utc)
LOCK_PATH = Path(
    r"C:\Users\ranjeet.chaudhary\.codex\automations\daily-keyword-company-research\run.lock"
)


CANADIAN_ENERGIES = {
    "company_name": "Canadian Sustainable Energies Ltd.",
    "company_domain": "canadianenergies.com",
    "company_url": "https://www.canadianenergies.com/",
    "location": "Toronto, Ontario, Canada; proposed manufacturing campus in Chatham-Kent, Ontario",
    "industry": "Solar-module and battery-energy-storage-system manufacturing",
    "products": ["Teamcenter", "Opcenter", "Tecnomatix"],
    "identity": CompanyIdentityEvidence(
        official_name="Canadian Sustainable Energies Ltd.",
        official_website_url="https://www.canadianenergies.com/",
        corroborating_urls=(
            "https://www.ctvnews.ca/windsor/article/proposed-2b-clean-energy-manufacturing-project-could-bring-more-than-1000-direct-jobs-to-chatham-kent/",
        ),
    ),
    "signals": [
        {
            "source_url": "https://www.canadianenergies.com/news/chatham-kent-facility-media-clarification",
            "source_title": "Media Clarification: Canadian Sustainable Energies Ltd. Chatham-Kent Facility",
            "source_publisher": "Canadian Sustainable Energies Ltd.",
            "signal_date": datetime(2026, 9, 17, tzinfo=timezone.utc),
            "reason": (
                "On September 17, 2026, Canadian Sustainable Energies Ltd. confirmed that its proposed "
                "Chatham-Kent project is a 10-GW integrated clean-energy manufacturing campus for battery "
                "energy storage systems, solar modules, and other clean-energy components, rather than a "
                "data centre. Inference: a campus spanning solar-module and battery-system production would "
                "create extensive product-configuration, supplier, factory-layout, production-quality, and "
                "traceability pressure across multiple phased lines. Teamcenter, Tecnomatix, and Opcenter "
                "are the smallest defensible set to control product and process structures, plan the campus "
                "and lines, and establish production genealogy and quality visibility; the newly public site "
                "proposal makes early manufacturing-systems planning relevant now, but the project remains "
                "proposed and therefore stays watchlist."
            ),
            "pain": (
                "Would need to coordinate product variants, suppliers, line design, work instructions, "
                "quality records, and end-to-end traceability across proposed solar-module and BESS production."
            ),
            "expansion": (
                "Confirmed a proposed 10-GW Chatham-Kent manufacturing campus for BESS, solar modules, "
                "and other clean-energy components."
            ),
        },
        {
            "source_url": "https://www.ctvnews.ca/windsor/article/proposed-2b-clean-energy-manufacturing-project-could-bring-more-than-1000-direct-jobs-to-chatham-kent/",
            "source_title": "Proposed $2B clean-energy manufacturing project could bring more than 1,000 direct jobs to Chatham-Kent",
            "source_publisher": "CTV News Windsor",
            "signal_date": datetime(2026, 9, 15, tzinfo=timezone.utc),
            "reason": (
                "On September 15, 2026, CTV News independently reported that Canadian Sustainable Energies "
                "selected Chatham-Kent for a proposed nearly C$2-billion, 10-GW campus expected to produce "
                "bifacial TOPCon solar modules and grid-scale and behind-the-meter battery energy storage "
                "systems and to create more than 1,000 direct jobs. Municipal officials cautioned that the "
                "project is not yet a done deal; the company described phased expansion, several possible "
                "financing structures, and discussions for long-term customer agreements. Inference: if the "
                "project advances, concurrent solar and storage product families, phased factory build-out, "
                "local sourcing, and large workforce ramp would require disciplined BOM/change control, line "
                "planning, quality genealogy, and production visibility. Teamcenter, Tecnomatix, and Opcenter "
                "map directly to those needs, while the public site selection creates a current planning window "
                "but incomplete financing and approvals cap the result at watchlist."
            ),
            "pain": (
                "A phased C$2-billion, 10-GW multi-product campus would require coordinated factory planning, "
                "supplier and product configuration control, workforce-ready processes, and auditable quality "
                "and production traceability."
            ),
            "expansion": (
                "Independent coverage described a proposed C$2-billion Chatham-Kent campus, more than 1,000 "
                "direct jobs, and phased solar-module and BESS manufacturing, while confirming financing and "
                "final agreements are not complete."
            ),
        },
    ],
    "keyword_ids": [5],
    "signal_label": "Proposed C$2B, 10-GW Chatham-Kent solar and BESS manufacturing campus",
    "challenge_summary": (
        "On September 15-17, 2026, Canadian Sustainable Energies identified Chatham-Kent for a proposed "
        "nearly C$2-billion, 10-GW integrated campus to manufacture bifacial TOPCon solar modules and grid-scale "
        "and behind-the-meter battery energy storage systems, with more than 1,000 direct jobs. CTV News reported "
        "that the project is not yet a done deal and still depends on phased financing and customer agreements. "
        "Inference: simultaneous solar and storage lines, local sourcing, a large workforce ramp, and phased "
        "factory build-out would create substantial BOM, supplier, line-planning, quality, and traceability pressure."
    ),
    "why_relevant": (
        "Teamcenter can govern solar-module and BESS product structures, approved suppliers, and engineering "
        "changes across the proposed campus. Tecnomatix can support phased factory and line planning, while "
        "Opcenter can provide production execution, genealogy, and quality visibility as lines are commissioned. "
        "The practical outcome would be a controlled ramp with fewer configuration and quality escapes; the public "
        "site announcement creates an early design window, but incomplete financing keeps timing at watchlist."
    ),
    "qualification_status": "watchlist",
    "opportunity_score": 63,
    "manufacturing_fit_score": 94,
    "trigger_score": 68,
    "solution_fit_score": 93,
    "evidence_quality_score": 92,
}


AIRMETAL = {
    "company_name": "AirMetal Robotics Corporation",
    "company_domain": "airmetal.com",
    "company_url": "https://airmetal.com/",
    "location": "Kanata, Ontario, Canada",
    "industry": "Drone, mesh-radio and counter-UAS hardware manufacturing",
    "products": ["Teamcenter", "Polarion", "Opcenter", "Tecnomatix"],
    "identity": CompanyIdentityEvidence(
        official_name="AirMetal Robotics Corporation",
        official_website_url="https://airmetal.com/",
        corroborating_urls=(
            "https://www.prnewswire.com/news-releases/orqa-and-remote-robotic-systems-launch-150m-partnership-to-build-canadian-sovereign-capability-in-drones-ai-and-counter-uas-systems-302813660.html",
            "https://federalcorporation.ca/corporation/17687117",
        ),
    ),
    "signal": {
        "source_url": "https://www.prnewswire.com/news-releases/orqa-and-remote-robotic-systems-launch-150m-partnership-to-build-canadian-sovereign-capability-in-drones-ai-and-counter-uas-systems-302813660.html",
        "source_title": "Orqa and Remote Robotic Systems Launch $150M Partnership to Build Canadian Sovereign Capability in Drones, AI, and Counter-UAS Systems",
        "source_publisher": "PR Newswire / Orqa d.o.o.",
        "signal_date": datetime(2026, 6, 30, tzinfo=timezone.utc),
        "reason": (
            "On June 30, 2026, Orqa and AirMetal parent Remote Robotic Systems announced a five-year "
            "partnership estimated at C$150 million, beginning with C$20 million to expand Canadian production "
            "facilities and targeting 1,000 uncrewed systems per month by mid-2027 and 10,000 per month over the "
            "agreement, with up to 100 technology jobs by Q4 2027. AirMetal's official site now identifies it as "
            "the Canadian manufacturing division and exclusive licensed Orqa producer in Kanata. Inference: "
            "licensed platform variants, joint development, defence requirements, rapid capacity growth, and a "
            "domestic supply chain create immediate configuration, requirements-to-test, line-planning, and "
            "production-traceability pressure. Teamcenter, Polarion, Tecnomatix, and Opcenter fit those needs, but "
            "the source describes an MOU and future targets rather than funded orders, so the opportunity remains watchlist."
        ),
        "pain": (
            "Must control licensed and Canadian-designed UAV variants, defence requirements and verification, "
            "supplier changes, production-line scale-up, and serial quality genealogy."
        ),
        "expansion": (
            "Five-year C$150-million partnership with an initial C$20-million facility expansion and targets of "
            "1,000 systems per month by mid-2027 and 10,000 per month over the agreement."
        ),
    },
    "keyword_ids": [2, 7, 9, 13, 14],
    "signal_label": "C$150M licensed-drone partnership targets 1,000 systems monthly by mid-2027",
    "challenge_summary": (
        "On June 30, 2026, Orqa and AirMetal parent Remote Robotic Systems announced a five-year partnership "
        "estimated at C$150 million, starting with C$20 million for Canadian production expansion and targeting "
        "1,000 systems per month by mid-2027 plus up to 100 technology jobs by Q4 2027. AirMetal's official site "
        "identifies its Kanata facility as the Canadian production location for licensed Orqa MRM platforms and "
        "AirMetal TacMesh systems. Inference: licensed variants, joint defence development, rapid line scale-up, "
        "and sovereign sourcing increase configuration, requirements-to-test, production-planning, and genealogy pressure."
    ),
    "why_relevant": (
        "Teamcenter can govern licensed and Canadian-designed product structures and supplier changes; Polarion "
        "can trace defence requirements to verification evidence. Tecnomatix and Opcenter can plan and execute the "
        "capacity ramp with controlled work instructions, quality records, and serial genealogy. The practical "
        "outcome is a faster, auditable Canadian production ramp, but an MOU and forward capacity targets keep the "
        "timing at watchlist until funded orders or completed production milestones are verified."
    ),
    "qualification_status": "watchlist",
    "opportunity_score": 64,
    "manufacturing_fit_score": 97,
    "trigger_score": 64,
    "solution_fit_score": 94,
    "evidence_quality_score": 90,
}


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


def publish(database: Database, prospect: dict) -> dict:
    evidence_rows = prospect["signals"] if "signals" in prospect else [prospect["signal"]]
    saved_evidence = []
    company = None
    for evidence in evidence_rows:
        signal = make_signal(prospect, evidence)
        verify_company_identity(signal, prospect["identity"])
        saved, company = database.persist_verified_signal(signal, prospect["identity"])
        saved_evidence.append(
            {
                "source_url": evidence["source_url"],
                "created": saved.created,
                "duplicate_url": saved.duplicate_url,
            }
        )
    if company is None:
        raise RuntimeError(f"Persistence returned no company for {prospect['company_name']}")

    primary = evidence_rows[0]
    keyword_rows = []
    for keyword_id in prospect["keyword_ids"]:
        row = database.record_keyword_company(
            keyword_id,
            prospect["company_name"],
            prospect["company_domain"],
            source_url=primary["source_url"],
            source_title=primary["source_title"],
            source_publisher=primary["source_publisher"],
            signal_label=prospect["signal_label"],
            signal_date=primary["signal_date"],
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
        keyword_rows.append(
            {
                "keyword_id": keyword_id,
                "result_id": row.id,
                "qualification_status": row.qualification_status,
                "opportunity_score": row.opportunity_score,
            }
        )

    with database.session() as session:
        company_id = session.scalar(
            select(CompanyRecord.id).where(
                func.lower(CompanyRecord.company_domain) == prospect["company_domain"].lower()
            )
        )
    if company_id is None:
        raise RuntimeError(f"Could not resolve company id for {prospect['company_name']}")

    return {
        "company_id": company_id,
        "company_name": company.company_name,
        "company_domain": company.company_domain,
        "signal_count": company.signal_count,
        "evidence": saved_evidence,
        "keywords": keyword_rows,
    }


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

    with database.session() as session:
        canadian_energies_before = session.execute(
            select(CompanyRecord.id, CompanyRecord.company_name, CompanyRecord.company_domain)
            .where(
                (func.lower(CompanyRecord.company_domain) == "canadianenergies.com")
                | (func.lower(CompanyRecord.company_name).like("%canadian sustainable energies%"))
            )
        ).all()
        airmetal_before = session.execute(
            select(CompanyRecord.id, CompanyRecord.company_name, CompanyRecord.company_domain)
            .where(func.lower(CompanyRecord.company_domain) == "airmetal.com")
        ).all()
    if canadian_energies_before:
        # Safe reruns are idempotent by canonical domain and evidence URL.
        new_company_expected = False
    else:
        new_company_expected = True
    if len(airmetal_before) != 1 or airmetal_before[0].id != 2238:
        raise RuntimeError(f"AirMetal identity changed: {airmetal_before}")

    results = [
        publish(database, CANADIAN_ENERGIES),
        publish(database, AIRMETAL),
    ]

    published = {keyword_id: 0 for keyword_id in keywords_before}
    for prospect in (CANADIAN_ENERGIES, AIRMETAL):
        for keyword_id in prospect["keyword_ids"]:
            published[keyword_id] += 1

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
        eligible_company_count = session.scalar(
            select(func.count(func.distinct(KeywordCompanyResultRecord.company_id))).where(
                KeywordCompanyResultRecord.qualification_status.in_(("qualified", "watchlist"))
            )
        )

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
                "new_company_expected": new_company_expected,
                "persisted": results,
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
                "eligible_company_count": eligible_company_count,
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
