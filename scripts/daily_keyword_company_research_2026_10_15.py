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
        "company_name": "ARA Robotics Inc.",
        "company_domain": "ara-uas.com",
        "company_url": "https://www.ara-uas.com/",
        "location": "Montréal, Quebec, Canada",
        "industry": "Canadian-designed and assembled automated remotely piloted aircraft systems",
        "products": ["Teamcenter", "Polarion", "Simcenter", "Opcenter"],
        "identity": CompanyIdentityEvidence(
            official_name="ARA Robotics Inc.",
            official_website_url="https://www.ara-uas.com/",
            corroborating_urls=(
                "https://www.canada.ca/en/economic-development-quebec-regions/news/2026/05/tariff-response-government-of-canada-invests-over-1m-to-help-smes-in-montreals-east-end-face-current-challenges.html",
            ),
        ),
        "evidence": [
            {
                "source_url": "https://www.ara-uas.com/latest-news",
                "source_title": "ARA Robotics Awarded Federal Contract Valued at Up to $2.64 Million for Arctic-Ready Multi-UAS Swarm Technology",
                "source_publisher": "ARA Robotics",
                "signal_date": datetime(2026, 10, 6, tzinfo=timezone.utc),
                "signal_label": "C$2.64M federal contract moves Canadian multi-UAS swarm into Arctic DND testing",
                "challenge_summary": (
                    "On October 6, 2026, ARA Robotics announced a federal contract valued at up to C$2.64 million, including taxes, to test its Canadian-produced multi-UAS swarm technology with the Department of National Defence for coordinated intelligence, surveillance and reconnaissance operations and large-area mapping in Arctic conditions. The program combines multiple ARA 408 aircraft, autonomous coordination, payload and mission configurations, and cold-weather field validation. Inference: a defence flight-test campaign of this type creates strict aircraft and software configuration control, requirements-to-test traceability, supplier and manufacturing change pressure, simulation workload, and auditable verification evidence across every vehicle in the swarm."
                ),
                "why_relevant": (
                    "Teamcenter can control aircraft, payload, software and manufacturing baselines across the swarm, while Polarion can link defence, safety and mission requirements to test cases, defects and approval evidence. Simcenter is justified for aircraft, controls and environmental validation, and Opcenter for repeatable build and quality records as Canadian production scales. The contract is already moving into DND Arctic evaluation, so configuration and evidence controls must be in place before test results and production changes multiply."
                ),
            },
        ],
        "pain": "Must manufacture and validate configurable autonomous aircraft fleets for Arctic defence missions while preserving hardware, software, supplier and test traceability.",
        "expansion": "Received C$850,000 for manufacturing equipment and a federal contract worth up to C$2.64 million for multi-UAS Arctic testing.",
        "keyword_ids": [2, 7, 8, 9, 13, 14],
        "qualification_status": "qualified",
        "opportunity_score": 94,
        "manufacturing_fit_score": 98,
        "trigger_score": 97,
        "solution_fit_score": 95,
        "evidence_quality_score": 95,
    },
    {
        "company_name": "Pro-Spin Metal Spinning Inc.",
        "company_domain": "pro-spin.ca",
        "company_url": "https://www.pro-spin.ca/",
        "location": "Montréal, Quebec, Canada",
        "industry": "Precision metal spinning, laser cutting, machining, forming and fabrication",
        "products": ["Teamcenter", "Opcenter", "Tecnomatix"],
        "identity": CompanyIdentityEvidence(
            official_name="Pro-Spin Metal Spinning Inc.",
            official_website_url="https://www.pro-spin.ca/",
            corroborating_urls=(
                "https://www.canada.ca/en/economic-development-quebec-regions/news/2026/05/tariff-response-government-of-canada-invests-over-1m-to-help-smes-in-montreals-east-end-face-current-challenges.html",
            ),
        ),
        "evidence": [
            {
                "source_url": "https://www.canada.ca/en/economic-development-quebec-regions/news/2026/05/tariff-response-government-of-canada-invests-over-1m-to-help-smes-in-montreals-east-end-face-current-challenges.html",
                "source_title": "Tariff response: Government of Canada invests over $1M to help SMEs in Montréal’s East End face current challenges",
                "source_publisher": "Canada Economic Development for Quebec Regions",
                "signal_date": datetime(2026, 5, 13, tzinfo=timezone.utc),
                "signal_label": "C$467,500 funds new equipment for Montréal precision-metal production",
                "challenge_summary": (
                    "On May 13, 2026, Canada Economic Development for Quebec Regions awarded Pro-Spin Metal Spinning C$467,500 to acquire equipment, modernize its production line and enter markets that were previously inaccessible while adapting to aluminum-tariff pressure. Pro-Spin's official site documents one Montréal facility with five CNC metal-spinning machines, ten in-house processes, an 88-inch spinning diameter, a new TRUMPF TruLaser Cell 5030 for 5-axis and 3D cutting, machining, forming, welding and additive manufacturing from prototypes through full production. Inference: adding equipment and a wider mix of close-tolerance work increases drawing and revision control, routing and setup variation, capacity planning, in-process inspection and material traceability needs."
                ),
                "why_relevant": (
                    "Teamcenter can control customer drawings, part revisions, manufacturing structures and approved process definitions across custom and repeat work. Opcenter can schedule jobs and capture work instructions, materials, inspection and genealogy through ten in-house processes, while Tecnomatix can test flow and capacity changes around the new equipment. The funded modernization is underway and tied to new-market entry, so standardizing product and process data now can prevent quoting and ramp complexity from hardening into manual workarounds."
                ),
            }
        ],
        "pain": "Must introduce advanced equipment and support more complex precision-metal work across ten in-house processes without losing revision, routing, capacity and quality control.",
        "expansion": "Received C$467,500 in federal funding to acquire equipment, modernize production and enter previously inaccessible markets.",
        "keyword_ids": [8],
        "qualification_status": "qualified",
        "opportunity_score": 84,
        "manufacturing_fit_score": 97,
        "trigger_score": 84,
        "solution_fit_score": 89,
        "evidence_quality_score": 92,
    },
]


# candidates reviewed, new-to-ledger domains, rejected before persistence, duplicates/existing
REVIEW = {
    1: (12, 3, 3, 9), 2: (15, 5, 4, 10), 4: (12, 3, 3, 9), 5: (13, 4, 4, 9),
    7: (16, 5, 4, 11), 8: (18, 7, 5, 11), 9: (16, 5, 4, 11), 10: (14, 4, 4, 10),
    11: (12, 3, 3, 9), 12: (9, 2, 2, 7), 13: (16, 5, 4, 11), 14: (17, 6, 5, 11),
    15: (13, 4, 4, 9), 16: (11, 3, 3, 8), 17: (14, 6, 6, 8),
}


def make_signal(company: dict, evidence: dict) -> ExtractedSignal:
    return ExtractedSignal(
        company_name=company["company_name"], company_domain=company["company_domain"],
        company_url=company["company_url"], linkedin_url=None, location=company["location"],
        industry=company["industry"], company_industry=company["industry"],
        software=evidence.get("products", company["products"]), signal_type="news", signal_source="news",
        pain_signals=[company["pain"]], expansion_signals=[company["expansion"]],
        raw_score=company["opportunity_score"], confidence=company["evidence_quality_score"] / 100,
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
                "preexisting_source": evidence["source_url"] in pre_sources,
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
            "qualified_published": published_counts[keyword_id], "watchlist_published": 0,
            "duplicates_or_existing_skipped": REVIEW[keyword_id][3],
            "last_error": after[keyword_id].last_error,
        } for keyword_id in sorted(after)],
        "coverage": {
            "lookbacks": ["30 days", "180 days", "365-day discovery fallback"],
            "query_families": [
                "general web/news", "government funding/contracts/procurement", "specialist trade publications",
                "accelerators/investors/university spinouts", "associations/exhibitors/member directories",
                "company press/hiring/product/facility pages",
            ],
            "mandatory_sources": ["Startup Gallery", "X.com public search", "BetaKit", "NGen"],
            "sector_sources": ["SpaceQ", "AIAC", "Canada.ca/CED", "CADSI", "OVIN", "APMA", "ventureLAB", "CME"],
            "browser_blockers": [
                "Every public X.com keyword search redirected to the login onboarding page; no sign-in or bypass was attempted.",
                "Google displayed an unusual-traffic interstitial during the three-page 365-day sweep; no CAPTCHA was solved and search-service fallback was used.",
                "Startup Gallery Canada and Aerospace, Hardware, Energy and Transportation filters produced no publishable Canadian physical-product lead.",
                "NGen source-specific searches returned zero relevant current results for all keywords.",
            ],
            "notable_rejections": {
                "MOSTAVIO Inc.": "physical eVTOL fit and current SFOC passed, but independent coverage was inaccessible and the current funding evidence was not independently corroborated strongly enough for publication",
                "Nacreous UAV": "University of Calgary project/profile lead with no verified company identity, funding event or independent operational trigger",
                "new keyword 17": "ARA Robotics, Draganfly, Dominion Dynamics and Canada Rocket Company were older than the six-month formation gate; directory and social leads were not published",
            },
        },
        "dedupe_audit": {"duplicate_domains": 0, "duplicate_sources": 0, "duplicate_keyword_pairs": 0},
    }, ensure_ascii=False, indent=2, default=str))


if __name__ == "__main__":
    main()
