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


MANGROVE = {
    "company_name": "Mangrove Lithium",
    "company_domain": "mangrovelithium.com",
    "company_url": "https://www.mangrovelithium.com/",
    "location": "Delta, British Columbia, Canada",
    "industry": "Battery-grade lithium refining technology and materials manufacturing",
    "products": ["Teamcenter", "Opcenter", "Tecnomatix"],
    "identity": CompanyIdentityEvidence(
        official_name="Mangrove Lithium",
        official_website_url="https://www.mangrovelithium.com/",
        corroborating_urls=(
            "https://betakit.com/mangrove-lithium-announces-85-million-usd-financing-to-power-critical-mineral-refinement-for-evs/",
            "https://www.canada.ca/en/department-finance/news/2026/01/government-welcomes-canada-growth-fund-investment-in-canadian-cleantech-company-mangrove-lithium.html",
        ),
    ),
    "signals": [
        {
            "source_url": "https://betakit.com/mangrove-lithium-announces-85-million-usd-financing-to-power-critical-mineral-refinement-for-evs/",
            "source_title": "Mangrove Lithium announces $85-million USD financing to power critical mineral refinement for EVs",
            "source_publisher": "BetaKit",
            "signal_date": datetime(2026, 4, 16, tzinfo=timezone.utc),
            "reason": (
                "BetaKit updated its January 16, 2026 financing report on April 16, when Mangrove Lithium "
                "opened its first commercial lithium-refining plant in Delta, British Columbia; the facility "
                "is designed to make enough battery-grade material for 25,000 electric vehicles per year, and "
                "the company is using up to US$85 million of structured financing plus a C$9 million tax-credit-"
                "backed loan to advance a second plant expected to support 500,000 vehicles annually. Inference: "
                "moving a patented electrochemical process from a first commercial line toward a plant twenty "
                "times larger creates equipment-configuration, process-release, supplier, batch-quality, and "
                "production-genealogy pressure. Teamcenter can govern approved product/process structures and "
                "engineering changes, Tecnomatix can support the larger plant and line plan, and Opcenter can "
                "control execution, quality, and material genealogy; the opened plant and funded scale-up make "
                "the systems window active now."
            ),
            "pain": (
                "Must scale a patented lithium-refining process while controlling equipment configurations, "
                "process releases, raw-material variability, batch quality, and end-to-end genealogy."
            ),
            "expansion": (
                "Opened a Delta commercial plant sized for 25,000 EVs per year and is advancing a second plant "
                "expected to support 500,000 EVs annually."
            ),
        },
        {
            "source_url": "https://www.mangrovelithium.com/canada-growth-fund-leads-us85usd-investment/",
            "source_title": "Canada Growth Fund Leads US$85 Million Financing in BC-based Mangrove Lithium alongside existing investors",
            "source_publisher": "Mangrove Lithium / Canada Growth Fund",
            "signal_date": datetime(2026, 1, 15, tzinfo=timezone.utc),
            "reason": (
                "On January 15, 2026, Mangrove Lithium and Canada Growth Fund announced up to US$85 million in "
                "structured financing, closed alongside a C$9 million Clean Technology Manufacturing investment-"
                "tax-credit-backed loan, to commercialize and deploy Mangrove's lithium-refining technology in "
                "Canada and abroad. The investment explicitly supports commercial development, Canadian IP, "
                "skilled jobs, and an integrated mining-to-refining supply chain. Inference: funded domestic and "
                "international deployment increases the number of plant, customer-feedstock, and process variants "
                "that engineering and operations must release and trace. Teamcenter, Tecnomatix, and Opcenter are "
                "the smallest defensible set for configuration/change control, industrialization planning, and "
                "quality genealogy while capital is being converted into commercial capacity."
            ),
            "pain": (
                "Commercial deployment across plants and feedstocks requires disciplined process configuration, "
                "supplier coordination, controlled engineering release, and auditable quality records."
            ),
            "expansion": (
                "Closed up to US$85 million of structured financing plus a C$9 million manufacturing-tax-credit-"
                "backed loan for commercial deployment."
            ),
        },
    ],
    "keyword_ids": [5, 8],
    "signal_label": "US$85M-funded Delta lithium plant opened; 20x larger capacity stage planned",
    "challenge_summary": (
        "On April 16, 2026, Mangrove Lithium opened its first commercial Delta, B.C. refinery, sized to produce "
        "battery-grade material for 25,000 electric vehicles per year, after closing up to US$85 million in "
        "structured financing and a C$9 million manufacturing-tax-credit-backed loan. BetaKit reported that "
        "Mangrove is also advancing a second plant expected to support 500,000 vehicles annually. Inference: "
        "scaling a patented electrochemical process across much larger equipment, feedstock, supplier, and batch "
        "volumes creates immediate configuration, industrialization, quality, and genealogy complexity."
    ),
    "why_relevant": (
        "Teamcenter can control approved process/equipment structures, suppliers, and engineering changes across "
        "the first and second plants. Tecnomatix can support factory and line planning, while Opcenter can enforce "
        "released work, batch quality, and material genealogy. The practical outcome is a repeatable scale-up with "
        "fewer commissioning and quality escapes; the first plant is operating and the next stage is funded now."
    ),
    "qualification_status": "qualified",
    "opportunity_score": 91,
    "manufacturing_fit_score": 96,
    "trigger_score": 93,
    "solution_fit_score": 92,
    "evidence_quality_score": 97,
}


IDEAL_CAN = {
    "company_name": "Ideal Can",
    "company_domain": "idealcan.ca",
    "company_url": "https://idealcan.ca/",
    "location": "Saint-Apollinaire, Quebec, Canada",
    "industry": "Steel food-can manufacturing",
    "products": ["Opcenter", "Tecnomatix"],
    "identity": CompanyIdentityEvidence(
        official_name="Ideal Can",
        official_website_url="https://idealcan.ca/",
        corroborating_urls=(
            "https://metalpackager.com/2026/08/4th-line-at-saint-apollinaire-for-ideal-can/",
            "https://www.foodincanada.com/food-business/federal-govt-s-1-5-m-repayable-grant-to-help-ideal-can-expand-capacity-164334/",
        ),
    ),
    "signals": [
        {
            "source_url": "https://metalpackager.com/2026/08/4th-line-at-saint-apollinaire-for-ideal-can/",
            "source_title": "4th line at Saint-Apollinaire for Ideal Can",
            "source_publisher": "The Metal Packager",
            "signal_date": datetime(2026, 8, 18, tzinfo=timezone.utc),
            "reason": (
                "On August 18, 2026, The Metal Packager independently reported that Ideal Can commissioned a "
                "fourth production line at Saint-Apollinaire with a C$1.5 million contribution from Canada "
                "Economic Development for Quebec Regions, raising annual capacity from 350 million to 470 million "
                "food cans. The company also plans further Quebec investment and a second plant in Chatham-Kent, "
                "Ontario. Inference: an active high-speed line ramp plus a future second site increases line-"
                "balancing, tooling/changeover, work-instruction, quality, and cross-site production-visibility "
                "pressure. Tecnomatix can validate the new and future line plans, while Opcenter can standardize "
                "execution, quality, and lot genealogy; the fourth line is already commissioned, so ramp controls "
                "are needed now."
            ),
            "pain": (
                "Must stabilize a new high-speed can line while controlling changeovers, quality checks, lot "
                "genealogy, throughput, and future cross-site production standards."
            ),
            "expansion": (
                "Commissioned a fourth Saint-Apollinaire line, increasing annual capacity from 350 million to "
                "470 million cans, with a second Ontario plant planned."
            ),
        },
        {
            "source_url": "https://idealcan.ca/news/government-of-canada-announces-usd1-5-million-financial-contribution-for-new-production-line",
            "source_title": "Government of Canada Announces CAD $1.5 Million Financial Contribution for New Production Line",
            "source_publisher": "Ideal Can",
            "signal_date": datetime(2026, 8, 15, tzinfo=timezone.utc),
            "reason": (
                "On August 15, 2026, Ideal Can confirmed commissioning its fourth Saint-Apollinaire production "
                "line with C$1.5 million of federal support, increasing rated capacity from 350 million to 470 "
                "million food cans per year in response to demand that accelerated after early-2025 U.S. tariffs. "
                "It also disclosed additional Quebec investment and a planned Chatham-Kent plant. Inference: "
                "rapid capacity growth and a coming multi-site footprint require consistent process plans, "
                "changeover control, quality inspection, lot traceability, and real-time production visibility. "
                "Tecnomatix and Opcenter fit those needs and can reduce ramp losses and quality escapes while the "
                "new line is being brought to sustained output."
            ),
            "pain": (
                "A newly commissioned line and planned second plant require repeatable process planning, "
                "changeover control, production quality, traceability, and throughput visibility."
            ),
            "expansion": (
                "Added a fourth line with C$1.5 million of federal support and disclosed a planned Ontario plant."
            ),
        },
    ],
    "keyword_ids": [8],
    "signal_label": "Fourth can line lifts capacity to 470M/year; Ontario plant planned",
    "challenge_summary": (
        "On August 15-18, 2026, Ideal Can commissioned a fourth production line at Saint-Apollinaire with a "
        "C$1.5 million federal contribution, lifting annual capacity from 350 million to 470 million food cans. "
        "The company said demand accelerated after early-2025 U.S. tariffs and disclosed further Quebec investment "
        "plus a planned second plant in Chatham-Kent, Ontario. Inference: a live high-speed line ramp and emerging "
        "multi-site footprint create immediate line-planning, changeover, quality, traceability, and visibility needs."
    ),
    "why_relevant": (
        "Tecnomatix can model and validate the fourth line and future Ontario layout before more capital is committed. "
        "Opcenter can standardize released operations, quality checks, lot genealogy, and real-time production "
        "visibility across the expanding footprint. The business outcome is faster stabilization at the new "
        "470-million-can capacity with fewer quality losses; the commissioned line makes the timing immediate."
    ),
    "qualification_status": "qualified",
    "opportunity_score": 89,
    "manufacturing_fit_score": 99,
    "trigger_score": 94,
    "solution_fit_score": 92,
    "evidence_quality_score": 96,
}


CALIBUR = {
    "company_name": "Calibur Tool & Mold Inc.",
    "company_domain": "caliburtoolandmold.com",
    "company_url": "https://caliburtoolandmold.com/",
    "location": "Windsor, Ontario, Canada",
    "industry": "Plastic injection and compression mold design and manufacturing",
    "products": ["Teamcenter", "Mendix"],
    "identity": CompanyIdentityEvidence(
        official_name="Calibur Tool & Mold Inc.",
        official_website_url="https://caliburtoolandmold.com/",
        corroborating_urls=(
            "https://search.open.canada.ca/grants/record/nrc-cnrc%2C172-2026-2027-Q1-1040619%2Ccurrent",
        ),
    ),
    "signals": [
        {
            "source_url": "https://search.open.canada.ca/grants/record/nrc-cnrc%2C172-2026-2027-Q1-1040619%2Ccurrent",
            "source_title": "Productivity Improvement ERP Implementation — Calibur Tool & Mold Inc.",
            "source_publisher": "Government of Canada / National Research Council Canada",
            "signal_date": datetime(2026, 4, 1, tzinfo=timezone.utc),
            "reason": (
                "On April 1, 2026, the National Research Council of Canada began a C$75,000 IRAP contribution "
                "agreement with Calibur Tool & Mold for a 'Productivity Improvement ERP Implementation' running "
                "through March 17, 2027; the disclosed objective is to improve manufacturing efficiency through "
                "ERP implementation. Calibur's official site verifies a Windsor operation that engineers and "
                "manufactures injection and compression molds, handles engineering changes and repairs, and "
                "operates under ISO 9001:2015. Inference: the active ERP project creates a near-term integration "
                "point for governed CAD/mold structures, revisions, and released manufacturing data rather than "
                "allowing ERP records to diverge from engineering. Teamcenter can own the mold BOM, revisions, "
                "documents, and changes, while Mendix can support targeted ERP-connected workflows; the funded "
                "implementation is underway now."
            ),
            "pain": (
                "Must keep mold designs, tooling structures, engineering changes, and released manufacturing data "
                "aligned with an ERP implementation without duplicate entry or revision errors."
            ),
            "expansion": (
                "Received a C$75,000 NRC IRAP contribution for an ERP implementation running from April 2026 "
                "through March 2027 to improve manufacturing efficiency."
            ),
        },
    ],
    "keyword_ids": [12],
    "signal_label": "C$75K NRC-backed ERP implementation is active through March 2027",
    "challenge_summary": (
        "On April 1, 2026, NRC IRAP began a C$75,000 contribution agreement with Calibur Tool & Mold for an ERP "
        "implementation intended to improve manufacturing efficiency, with the project running through March 17, "
        "2027. Calibur's Windsor operation designs and manufactures injection and compression molds, manages "
        "engineering changes and repairs, and holds ISO 9001:2015 certification. Inference: the live ERP project "
        "creates immediate CAD/BOM/revision and released-data integration pressure across engineer-to-order tooling."
    ),
    "why_relevant": (
        "Teamcenter can govern each mold's design files, tooling structure, revision, approval, and engineering "
        "change before released data reaches ERP. Mendix can support focused ERP-connected approval and exception "
        "workflows without replacing the funded ERP. The practical outcome is less duplicate entry and fewer "
        "revision errors; the funded implementation window is open through March 2027."
    ),
    "qualification_status": "qualified",
    "opportunity_score": 88,
    "manufacturing_fit_score": 98,
    "trigger_score": 93,
    "solution_fit_score": 95,
    "evidence_quality_score": 94,
}


PROSPECTS = (MANGROVE, IDEAL_CAN, CALIBUR)


RESULT_CARDS = {
    1: 30,
    2: 89,
    3: 67,
    4: 64,
    5: 63,
    7: 80,
    8: 50,
    9: 30,
    10: 75,
    11: 75,
    12: 55,
    13: 77,
    14: 86,
    15: 84,
    16: 77,
}


DEEP_REVIEW = {
    1: (0, 0, 0),
    2: (1, 0, 1),
    3: (1, 0, 1),
    4: (0, 0, 0),
    5: (2, 1, 0),
    7: (1, 0, 1),
    8: (4, 2, 0),
    9: (1, 0, 1),
    10: (2, 1, 1),
    11: (2, 0, 2),
    12: (3, 2, 0),
    13: (2, 0, 2),
    14: (3, 1, 2),
    15: (2, 2, 0),
    16: (2, 2, 0),
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
    saved_evidence = []
    company = None
    for evidence in prospect["signals"]:
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

    primary = prospect["signals"][0]
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

    candidate_domains = {p["company_domain"] for p in PROSPECTS}
    with database.session() as session:
        existing = session.execute(
            select(CompanyRecord.id, CompanyRecord.company_name, CompanyRecord.company_domain)
            .where(func.lower(CompanyRecord.company_domain).in_(candidate_domains))
        ).all()
    if existing:
        raise RuntimeError(f"New-candidate domains already exist: {existing}")

    persisted = [publish(database, prospect) for prospect in PROSPECTS]

    published = {keyword_id: 0 for keyword_id in keywords_before}
    watchlist = {keyword_id: 0 for keyword_id in keywords_before}
    for prospect in PROSPECTS:
        for keyword_id in prospect["keyword_ids"]:
            if prospect["qualification_status"] == "qualified":
                published[keyword_id] += 1
            else:
                watchlist[keyword_id] += 1

    for keyword_id in sorted(keywords_before):
        result_count = published[keyword_id] + watchlist[keyword_id]
        if database.record_keyword_search(keyword_id, result_count=result_count, error=None) is None:
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
                "persisted": persisted,
                "keyword_audits": [
                    {
                        "id": keyword_id,
                        "keyword": keywords_after[keyword_id].keyword,
                        "search_count_before": keywords_before[keyword_id].search_count,
                        "search_count_after": keywords_after[keyword_id].search_count,
                        "result_cards": RESULT_CARDS[keyword_id],
                        "deep_candidates_reviewed": DEEP_REVIEW[keyword_id][0],
                        "rejected_before_persistence": DEEP_REVIEW[keyword_id][1],
                        "duplicates_or_existing_skipped": DEEP_REVIEW[keyword_id][2],
                        "qualified_published": published[keyword_id],
                        "watchlist_published": watchlist[keyword_id],
                        "last_error": keywords_after[keyword_id].last_error,
                    }
                    for keyword_id in sorted(keywords_after)
                ],
                "coverage": {
                    "result_cards_total": sum(RESULT_CARDS.values()),
                    "lookbacks": ["30-day", "180-day", "365-day ongoing-signal fallback"],
                    "mandatory_direct_startup_gallery": "15/15 accessible; query parameter returned the same unfiltered gallery and no relevant candidate",
                    "mandatory_direct_x": "15/15 attempted; certificate/URL-policy inaccessible; public X-ray results used",
                    "mandatory_direct_betakit": "15/15 checked; exact zero-result searches for keywords 1, 7, 12, and 16",
                    "mandatory_direct_ngen": "15/15 direct search endpoints returned 404/timeout; site-specific indexed project/funding searches completed",
                    "spaceq_aiac": "direct checks completed for keywords 1, 7, 9, 10, 13, and 14",
                    "engines": ["Google", "Bing", "Yahoo"],
                    "google_warning": "Automated-traffic interstitial encountered; not solved or bypassed",
                },
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
