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


COMPANIES = [
    {
        "company_name": "SenseHuman AI",
        "company_domain": "sensehuman.ai",
        "company_url": "https://sensehuman.ai/",
        "location": "Edmonton, Alberta, Canada",
        "industry": "AI-enabled industrial safety wearables and smart hardhats",
        "products": ["Teamcenter", "Polarion"],
        "identity": CompanyIdentityEvidence(
            official_name="SenseHuman AI",
            official_website_url="https://sensehuman.ai/",
            corroborating_urls=(
                "https://betakit.com/sensehuman-ai-is-building-an-ai-powered-hardhat-that-watches-your-back/",
            ),
        ),
        "evidence": [
            {
                "source_url": "https://betakit.com/sensehuman-ai-is-building-an-ai-powered-hardhat-that-watches-your-back/",
                "source_title": "SenseHuman AI is building an AI-powered hardhat that watches your back",
                "source_publisher": "BetaKit",
                "signal_date": datetime(2026, 10, 9, tzinfo=timezone.utc),
                "signal_label": "Twelve smart-hardhat field units expose a manufacturing-capacity constraint",
                "challenge_summary": (
                    "On October 9, 2026, BetaKit reported that Edmonton-based SenseHuman AI had 12 camera-equipped smart hardhats operating in the field after pilots including Edmonton Unlimited's Built World Venture Pilot with The Bartlett Group; OpenCircle Contractors Association bought the first five units after contributing to a C$250,000 January 2026 pre-seed round. CEO Ryker Telford said demand already exceeds the company's ability to build the four-camera, machine-vision helmets and that the next step is scaling manufacturing. Inference: moving from hand-built pilot units to a repeatable safety product increases hardware/software configuration, component-revision, requirements, field-defect, test, and supplier-control pressure."
                ),
                "why_relevant": (
                    "Teamcenter is the smallest fit for controlling helmet variants, camera and compute components, firmware-linked configurations, supplier data, and released changes. Polarion can connect safety requirements, pilot findings, verification tests, and defects as the product moves from trials to a manufactured offering. The current field deployments and stated inability to meet demand create urgency, although the absence of a disclosed production plan keeps this prospect on the watchlist."
                ),
            }
        ],
        "pain": "Must turn pilot smart hardhats into a repeatable manufactured product while controlling camera, compute, firmware, safety-requirement, test, and supplier changes.",
        "expansion": "Has 12 smart hardhats in field use and says demand exceeds current build capacity after a C$250,000 pre-seed round.",
        "keyword_ids": [8],
        "qualification_status": "watchlist",
        "opportunity_score": 63,
        "manufacturing_fit_score": 82,
        "trigger_score": 72,
        "solution_fit_score": 78,
        "evidence_quality_score": 92,
    },
    {
        "company_name": "Intellijoint Surgical Inc.",
        "company_domain": "intellijointsurgical.com",
        "company_url": "https://intellijointsurgical.com/",
        "location": "Kitchener-Waterloo, Ontario, Canada",
        "industry": "Regulated orthopaedic surgical-navigation medical devices",
        "products": ["Teamcenter", "Polarion"],
        "identity": CompanyIdentityEvidence(
            official_name="Intellijoint Surgical Inc.",
            official_website_url="https://intellijointsurgical.com/about/",
            corroborating_urls=(
                "https://betakit.com/intellijoint-surgical-wants-to-prove-canadian-medtech-companies-can-grow-on-their-own-terms/",
                "https://uwaterloo.ca/news/intellijoint-surgical-inc-and-vena-medical-awarded-19",
            ),
        ),
        "evidence": [
            {
                "source_url": "https://betakit.com/intellijoint-surgical-wants-to-prove-canadian-medtech-companies-can-grow-on-their-own-terms/",
                "source_title": "Intellijoint Surgical wants to prove Canadian medtech companies can grow on their own terms",
                "source_publisher": "BetaKit",
                "signal_date": datetime(2026, 10, 8, tzinfo=timezone.utc),
                "signal_label": "IJX OEM platform and global expansion extend a 90,000-case surgical-device base",
                "challenge_summary": (
                    "On October 8, 2026, BetaKit reported that Intellijoint Surgical's navigation technology had supported more than 90,000 surgical cases and that its new IJX business unit would let other medical-device manufacturers integrate Intellijoint technology into their own systems while the company expands in Latin America and Asia. The same article describes Intellijoint HIP and Intellijoint KNEE as regulated surgical-navigation devices sold through a capital-and-consumables model. Inference: OEM integrations and additional markets multiply device configurations, interface requirements, regional submissions, design-history evidence, supplier changes, and verification workloads."
                ),
                "why_relevant": (
                    "Teamcenter can govern device and consumable BOMs, OEM configurations, supplier records, and released engineering changes. Polarion can maintain traceability from partner and regulatory requirements through risk controls, verification tests, defects, and approval evidence. IJX is being commercialized now against a large installed clinical evidence base, so a common product-development backbone is timely before integrations and jurisdictions proliferate."
                ),
            },
            {
                "source_url": "https://uwaterloo.ca/news/intellijoint-surgical-inc-and-vena-medical-awarded-19",
                "source_title": "Intellijoint Surgical Inc. and Vena Medical awarded $1.9 million in government funding",
                "source_publisher": "University of Waterloo",
                "signal_date": datetime(2026, 3, 3, tzinfo=timezone.utc),
                "signal_label": "C$450,000 production-automation project supports 34 roles and adds three jobs",
                "challenge_summary": (
                    "On March 3, 2026, the University of Waterloo reported that Intellijoint Surgical received C$450,000 to integrate artificial intelligence and automation into its production and distribution workflows, supporting 34 existing roles and creating three skilled jobs. The funded work applies directly to delivery of the company's regulated orthopaedic navigation systems. Inference: automating production and distribution while preserving medical-device quality records raises work-instruction, genealogy, nonconformance, change-control, validation, and audit-traceability demands."
                ),
                "why_relevant": (
                    "Teamcenter can keep production structures, approved suppliers, device revisions, and change approvals synchronized with engineering. Polarion can connect process and product requirements to validation evidence, deviations, and regulated test records. The funded automation program is active in 2026, creating a near-term window to establish controlled data and validation practices before new workflows become entrenched."
                ),
            },
        ],
        "pain": "Must scale regulated surgical-navigation products, OEM integrations, global variants, and automated production while maintaining configuration and requirements-to-test traceability.",
        "expansion": "Launched the IJX OEM-integration business after more than 90,000 surgical cases and received C$450,000 for AI and automation in production and distribution.",
        "keyword_ids": [8],
        "qualification_status": "qualified",
        "opportunity_score": 88,
        "manufacturing_fit_score": 94,
        "trigger_score": 88,
        "solution_fit_score": 93,
        "evidence_quality_score": 95,
    },
    {
        "company_name": "Cyberworks Robotics Inc.",
        "company_domain": "cyberworksrobotics.com",
        "company_url": "https://www.cyberworksrobotics.com/",
        "location": "Markham, Ontario, Canada",
        "industry": "Autonomous mobile robots and multi-role defence vehicles",
        "products": ["Teamcenter", "Polarion", "Simcenter"],
        "identity": CompanyIdentityEvidence(
            official_name="Cyberworks Robotics Inc.",
            official_website_url="https://www.cyberworksrobotics.com/",
            corroborating_urls=(
                "https://betakit.com/cyberworks-lands-1-million-canadian-armed-forces-contract/",
                "https://canadabuys.canada.ca/en/tender-opportunities/contract-history/cw2465735-000",
            ),
        ),
        "evidence": [
            {
                "source_url": "https://betakit.com/cyberworks-lands-1-million-canadian-armed-forces-contract/",
                "source_title": "Cyberworks lands $1-million Canadian Armed Forces contract",
                "source_publisher": "BetaKit",
                "signal_date": datetime(2026, 10, 6, tzinfo=timezone.utc),
                "signal_label": "C$1.02M defence contract advances next-generation multi-role autonomous vehicles",
                "challenge_summary": (
                    "On October 6, 2026, BetaKit reported that Cyberworks Robotics' Department of National Defence contract had been amended to more than C$1 million for delivery of next-generation multi-role autonomous vehicles, with the work scheduled through February 2027 and a potential path to as much as C$7 million in additional sales. Cyberworks' official product portfolio spans autonomous wheelchairs, transport tugs, material-handling robots, and military transport vehicles built on its OmniSuite navigation platform. Inference: a defence vehicle program adds customer-specific vehicle configurations, sensor and control interfaces, ruggedization, verification scenarios, supplier coordination, and formal requirements/change evidence."
                ),
                "why_relevant": (
                    "Teamcenter can control vehicle variants, mechanical/electrical/software configuration baselines, suppliers, and released changes. Polarion can trace defence requirements through test cases, defects, and acceptance evidence, while Simcenter can support structural, thermal, motion, and controls validation for multi-role platforms. Delivery is due by February 2027 and the initial contract can unlock follow-on sales, making disciplined engineering execution urgent now."
                ),
            },
            {
                "source_url": "https://canadabuys.canada.ca/en/tender-opportunities/contract-history/cw2465735-000",
                "source_title": "Cyberworks TS11-021833 - Contract History",
                "source_publisher": "CanadaBuys",
                "signal_date": datetime(2026, 9, 22, tzinfo=timezone.utc),
                "signal_label": "CanadaBuys confirms competitive DND contract CW2465735 at C$1,023,653.14",
                "challenge_summary": (
                    "CanadaBuys records contract CW2465735 to Cyberworks Robotics Inc. at C$1,023,653.14 after the September 22, 2026 amendment, for a five-month Department of National Defence product-research-and-development term ending February 8, 2027. The award was made through competitive open bidding and names an Ontario delivery address. Inference: the short execution window for a defence R&D vehicle program concentrates configuration, requirements, verification, supplier, and acceptance-data pressure."
                ),
                "why_relevant": (
                    "Teamcenter and Polarion together can establish an auditable baseline for the vehicle BOM, interfaces, requirements, changes, tests, and delivery evidence; Simcenter is relevant where physical vehicle performance must be validated before acceptance. The government record confirms the contract value, buyer, and deadline independently of the trade article, making the buying trigger current and verifiable."
                ),
            },
        ],
        "pain": "Must execute a time-bounded defence autonomous-vehicle program while coordinating multi-domain configurations, suppliers, ruggedization, verification, and acceptance evidence.",
        "expansion": "Won a C$1,023,653.14 DND contract for next-generation multi-role autonomous vehicles, with possible follow-on sales up to C$7 million.",
        "keyword_ids": [2, 13, 14],
        "qualification_status": "qualified",
        "opportunity_score": 95,
        "manufacturing_fit_score": 93,
        "trigger_score": 98,
        "solution_fit_score": 95,
        "evidence_quality_score": 97,
    },
]


# reviewed, new-to-ledger, rejected, qualified, watchlist, duplicates/existing
REVIEW = {
    1: (18, 7, 14, 0, 0, 4), 2: (22, 9, 16, 1, 0, 5), 3: (19, 6, 15, 0, 0, 4),
    4: (18, 7, 14, 0, 0, 4), 5: (21, 8, 16, 0, 0, 5), 7: (24, 10, 18, 0, 0, 6),
    8: (27, 14, 19, 1, 1, 6), 9: (22, 8, 17, 0, 0, 5), 10: (20, 7, 16, 0, 0, 4),
    11: (18, 6, 14, 0, 0, 4), 12: (19, 8, 16, 0, 0, 3), 13: (23, 10, 17, 1, 0, 5),
    14: (25, 11, 18, 1, 0, 6), 15: (18, 7, 14, 0, 0, 4), 16: (20, 9, 16, 0, 0, 4),
}


def make_signal(company: dict, evidence: dict) -> ExtractedSignal:
    return ExtractedSignal(
        company_name=company["company_name"], company_domain=company["company_domain"],
        company_url=company["company_url"], linkedin_url=None, location=company["location"],
        industry=company["industry"], company_industry=company["industry"], software=company["products"],
        signal_type="news", signal_source="news", pain_signals=[company["pain"]],
        expansion_signals=[company["expansion"]], raw_score=company["opportunity_score"],
        confidence=company["evidence_quality_score"] / 100,
        reason=evidence["challenge_summary"] + " " + evidence["why_relevant"],
        source_url=evidence["source_url"], source_title=evidence["source_title"],
        detected_at=evidence["signal_date"],
    )


def main() -> None:
    load_dotenv(REPO_ROOT / ".env")
    marker = json.loads(LOCK_PATH.read_text(encoding="utf-8"))
    if int(marker.get("pid", 0)) <= 0:
        raise RuntimeError("Exclusive automation lock is not held")

    database = Database(os.environ["DATABASE_URL"])
    database.initialize()
    before = {row.id: row for row in database.list_keywords()}
    if set(before) != set(REVIEW):
        raise RuntimeError(f"Persistent keyword set changed during run: {sorted(before)}")

    candidate_domains = [company["company_domain"] for company in COMPANIES]
    evidence_urls = [e["source_url"] for company in COMPANIES for e in company["evidence"]]
    with database.session() as session:
        pre_by_domain = {
            row.company_domain.lower(): row for row in session.scalars(
                select(CompanyRecord).where(func.lower(CompanyRecord.company_domain).in_(candidate_domains))
            ).all()
        }
        pre_sources = set(session.scalars(
            select(SignalRecord.source_url).where(SignalRecord.source_url.in_(evidence_urls))
        ).all())

    for company in COMPANIES:
        for evidence in company["evidence"]:
            verify_company_identity(make_signal(company, evidence), company["identity"])

    published_counts = {keyword_id: 0 for keyword_id in before}
    persisted_evidence = []
    company_rows = []
    for company in COMPANIES:
        for evidence in company["evidence"]:
            saved, _ = database.persist_verified_signal(make_signal(company, evidence), company["identity"])
            persisted_evidence.append({
                "company_domain": company["company_domain"], "source_url": evidence["source_url"],
                "created": saved.created, "duplicate_url": saved.duplicate_url,
            })

        with database.session() as session:
            company_record = session.scalar(select(CompanyRecord).where(
                func.lower(CompanyRecord.company_domain) == company["company_domain"]
            ))
        if company_record is None:
            raise RuntimeError(f"Persisted company missing: {company['company_domain']}")

        primary = company["evidence"][0]
        links = []
        for keyword_id in company["keyword_ids"]:
            row = database.record_keyword_company(
                keyword_id, company["company_name"], company["company_domain"],
                source_url=primary["source_url"], source_title=primary["source_title"],
                source_publisher=primary["source_publisher"], signal_label=primary["signal_label"],
                signal_date=primary["signal_date"], challenge_summary=primary["challenge_summary"],
                why_relevant=primary["why_relevant"], recommended_products=company["products"],
                qualification_status=company["qualification_status"], opportunity_score=company["opportunity_score"],
                manufacturing_fit_score=company["manufacturing_fit_score"], trigger_score=company["trigger_score"],
                solution_fit_score=company["solution_fit_score"], evidence_quality_score=company["evidence_quality_score"],
                seen_at=RUN_AT,
            )
            if row is None:
                raise RuntimeError(f"Could not link {company['company_name']} to keyword {keyword_id}")
            links.append({"keyword_id": keyword_id, "result_id": row.id})
            published_counts[keyword_id] += 1

        company_rows.append({
            "company_id": company_record.id, "company_name": company_record.company_name,
            "company_domain": company_record.company_domain, "company_url": company_record.company_url,
            "location": company_record.location, "industry": company_record.industry,
            "software": company_record.software, "signal_count": company_record.signal_count,
            "total_score": company_record.total_score, "lead_score": company_record.lead_score,
            "qualification_status": company["qualification_status"], "opportunity_score": company["opportunity_score"],
            "manufacturing_fit_score": company["manufacturing_fit_score"], "trigger_score": company["trigger_score"],
            "solution_fit_score": company["solution_fit_score"], "evidence_quality_score": company["evidence_quality_score"],
            "keyword_links": links, "new_company": company["company_domain"] not in pre_by_domain,
        })

    for keyword_id in sorted(before):
        if database.record_keyword_search(keyword_id, result_count=published_counts[keyword_id], error=None) is None:
            raise RuntimeError(f"Could not record keyword search {keyword_id}")

    after = {row.id: row for row in database.list_keywords()}
    for keyword_id, prior in before.items():
        current = after[keyword_id]
        if current.search_count != prior.search_count + 1 or current.last_error is not None:
            raise RuntimeError(f"Keyword audit failed for {keyword_id}")

    with database.session() as session:
        duplicate_domains = session.execute(
            select(func.lower(CompanyRecord.company_domain), func.count(CompanyRecord.id))
            .where(CompanyRecord.company_domain.is_not(None)).group_by(func.lower(CompanyRecord.company_domain))
            .having(func.count(CompanyRecord.id) > 1)
        ).all()
        duplicate_sources = session.execute(
            select(SignalRecord.source_url, func.count(SignalRecord.id)).where(SignalRecord.source_url.is_not(None))
            .group_by(SignalRecord.source_url).having(func.count(SignalRecord.id) > 1)
        ).all()
        duplicate_keyword_pairs = session.execute(
            select(KeywordCompanyResultRecord.keyword_id, KeywordCompanyResultRecord.company_id, func.count(KeywordCompanyResultRecord.id))
            .group_by(KeywordCompanyResultRecord.keyword_id, KeywordCompanyResultRecord.company_id)
            .having(func.count(KeywordCompanyResultRecord.id) > 1)
        ).all()
        eligible_count = session.scalar(select(func.count(func.distinct(KeywordCompanyResultRecord.company_id))).where(
            KeywordCompanyResultRecord.qualification_status.in_(("qualified", "watchlist"))
        ))
    if duplicate_domains or duplicate_sources or duplicate_keyword_pairs:
        raise RuntimeError(f"Post-write dedupe audit failed: {duplicate_domains}, {duplicate_sources}, {duplicate_keyword_pairs}")

    print(json.dumps({
        "run_at": RUN_AT.isoformat(), "companies": company_rows, "evidence": persisted_evidence,
        "published_counts": published_counts, "eligible_company_count": eligible_count,
        "keyword_audits": [{
            "id": keyword_id, "keyword": after[keyword_id].keyword,
            "search_count_before": before[keyword_id].search_count,
            "search_count_after": after[keyword_id].search_count,
            "candidate_domains_reviewed": REVIEW[keyword_id][0],
            "new_to_ledger_domains_reviewed": REVIEW[keyword_id][1],
            "rejected_before_persistence": REVIEW[keyword_id][2],
            "qualified_published": REVIEW[keyword_id][3],
            "watchlist_published": REVIEW[keyword_id][4],
            "duplicates_or_existing_skipped": REVIEW[keyword_id][5],
            "last_error": after[keyword_id].last_error,
            "warnings": [
                "Startup Gallery directly checked; no discovery lead passed official-site and dated-trigger verification",
                "X.com direct search was inaccessible because of ERR_CERT_AUTHORITY_INVALID; no warning was bypassed",
                "BetaKit source-specific search completed",
                "NGen project, funding, case-study, challenge, and news search completed",
            ] + (["SpaceQ and AIAC news, guide, and member searches completed"] if keyword_id in {1, 7, 9, 10, 13, 14} else []),
        } for keyword_id in sorted(after)],
        "coverage": {
            "lookbacks": ["30-day", "180-day", "365-day ongoing-signal fallback"],
            "query_families": [
                "general web/news", "government funding/contracts/procurement", "specialist trade publications",
                "accelerators/investors/university spinouts", "associations/exhibitors/member directories",
                "company hiring/press/product/facility pages",
            ],
            "mandatory_sources": ["Startup Gallery", "X.com", "BetaKit", "NGen"],
            "aerospace_sources": ["SpaceQ", "AIAC", "Aero Montreal", "DAIR Aerospace"],
            "rotated_sources": [
                "CanadaBuys", "Natural Resources Canada", "ISED Strategic Response Fund", "FedDev Ontario",
                "Canada's Ocean Supercluster", "Shipbuilding Association of Canada", "Marine Log", "Naval News",
                "ventureLAB Hardware Catalyst", "CDL", "MaRS", "Communitech", "APMA Project Arrow", "OVIN",
                "PLANT", "Canadian Manufacturing", "Electric Autonomy Canada", "Oakville Chamber of Commerce",
                "company press releases and hiring pages", "French-language Quebec manufacturing searches",
            ],
            "gap_fill_triggered": False,
            "notable_rejections": [
                "AirMatrix was confirmed as an airspace-management software provider rather than a physical-product manufacturer.",
                "Adaptive Marine Solutions was a vessel-design participant, not a verified shipbuilder or physical-product manufacturer.",
                "Axya was an industrial procurement software vendor and outside the physical-product gate.",
                "Jubilant Radiopharma and Northern RNA had credible facility signals but did not match a saved keyword closely enough for publication.",
                "Startup Gallery's Canada-category leads were software, fintech, AI, or service businesses; related hardware categories were outside Canada.",
                "Known companies including Volatus, TetraGen, NordSpace, Reaction Dynamics, InDro, Sentinel, Nano One, NanoXplore, Davie, Irving, and Seaspan were rediscovered and skipped or lacked a newer qualifying keyword result.",
            ],
        },
        "duplicate_audit": {"canonical_domains": 0, "source_urls": 0, "keyword_company_pairs": 0},
    }, indent=2, default=str))


if __name__ == "__main__":
    main()
