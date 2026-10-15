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
        "company_name": "Hammond Manufacturing Company Limited",
        "company_domain": "hammfg.com",
        "company_url": "https://www.hammfg.com/",
        "location": "Guelph and Palmerston, Ontario, Canada",
        "industry": "Electrical and electronic enclosures, racks, power distribution, and metal fabrication",
        "products": ["Teamcenter", "Tecnomatix", "Opcenter"],
        "identity": CompanyIdentityEvidence(
            official_name="Hammond Manufacturing Company Limited",
            official_website_url="https://www.hammfg.com/",
            corroborating_urls=(
                "https://www.wellingtonadvertiser.com/hammond-manufacturing-expanding-palmerston-plant/",
            ),
        ),
        "evidence": [
            {
                "source_url": "https://www.wellingtonadvertiser.com/hammond-manufacturing-expanding-palmerston-plant/",
                "source_title": "Hammond Manufacturing expanding Palmerston plant",
                "source_publisher": "Wellington Advertiser",
                "signal_date": datetime(2026, 10, 2, tzinfo=timezone.utc),
                "signal_label": "C$26.47M Palmerston expansion nearly doubles metal-fabrication footprint",
                "challenge_summary": (
                    "On October 2, 2026, Hammond Manufacturing announced a C$26.47 million Palmerston expansion, supported by C$3,971,250 from Ontario, that will add 85,000 square feet to its 97,000-square-foot plant, create 30 jobs, and retain about 98. The plant makes roughly 700 product variations and the addition will replicate laser cutting, punching, pressing, bending, welding, and powder-coating capacity. Inference: nearly doubling a multi-process factory for hundreds of variants increases BOM and engineering-change pressure, routing and line-planning complexity, work-in-process visibility, and quality traceability across old and new capacity."
                ),
                "why_relevant": (
                    "Teamcenter is the smallest fit for product variants, manufacturing BOMs, released drawings, suppliers, and change control. Tecnomatix can validate the duplicated process flow and capacity plan before equipment and layouts harden, while Opcenter can coordinate scheduling, work instructions, quality, and genealogy during the ramp. Construction was already underway at the October announcement, so the controls need to be established before the expanded plant starts production."
                ),
            },
            {
                "source_url": "https://www.hammfg.com/files/news/2026/2026-03-13-business-expansion-and-related-investment.pdf?v=1773667166",
                "source_title": "Business Expansion and Related Investment",
                "source_publisher": "Hammond Manufacturing Company Limited",
                "signal_date": datetime(2026, 3, 13, tzinfo=timezone.utc),
                "signal_label": "Board approves 85,000-square-foot painting and metal-fabrication expansion",
                "challenge_summary": (
                    "On March 13, 2026, Hammond's board approved an 85,000-square-foot facility expansion for additional painting and metal-fabrication capacity, with an initial C$18 million building-and-equipment budget and first-half 2027 startup target. The official release identifies Hammond as a manufacturer of metallic and non-metallic enclosures, racks, outlet strips, surge suppressors, and electronic transformers. Inference: installing parallel fabrication and finishing capacity creates a fixed near-term need to synchronize product structures, routings, tooling, equipment commissioning, work instructions, and quality plans."
                ),
                "why_relevant": (
                    "Teamcenter can keep product and manufacturing structures aligned while the new equipment is commissioned, and Tecnomatix can test line and process alternatives before startup. Opcenter becomes relevant for dispatch, material and work-in-process tracking, and consistent quality execution across the original and expanded areas. The first-half 2027 target creates a defined implementation window rather than a speculative future need."
                ),
            },
        ],
        "pain": "Must nearly double a multi-process metal-fabrication plant for about 700 product variants while preserving change, routing, scheduling, and quality control.",
        "expansion": "Investing C$26.47 million to add 85,000 square feet in Palmerston with first-half 2027 startup targeted.",
        "keyword_ids": [8],
        "qualification_status": "qualified",
        "opportunity_score": 93,
        "manufacturing_fit_score": 99,
        "trigger_score": 96,
        "solution_fit_score": 94,
        "evidence_quality_score": 98,
    },
    {
        "company_name": "Jennmar Canada Ltd.",
        "company_domain": "jennmar.com",
        "company_url": "https://www.jennmar.com/",
        "location": "Sudbury, Ontario, and Rouyn-Noranda, Quebec, Canada",
        "industry": "Steel ground-support and stabilization products for mining and tunnelling",
        "products": ["Teamcenter", "Opcenter", "Tecnomatix"],
        "identity": CompanyIdentityEvidence(
            official_name="Jennmar Canada Ltd.",
            official_website_url="https://www.jennmar.com/jennmar-international",
            corroborating_urls=(
                "https://news.ontario.ca/en/release/1008041/ontario-investing-more-than-34-million-to-protect-manufacturing-jobs-in-the-north",
                "https://www.canada.ca/en/fednor/news/2026/04/fednor-invests-close-to-3-million-to-help-greater-sudbury-businesses-respond-adapt-and-compete-amid-shifting-market-conditions.html",
            ),
        ),
        "evidence": [
            {
                "source_url": "https://news.ontario.ca/en/release/1008041/ontario-investing-more-than-34-million-to-protect-manufacturing-jobs-in-the-north",
                "source_title": "Ontario Investing More Than $3.4 Million to Protect Manufacturing Jobs in the North",
                "source_publisher": "Government of Ontario",
                "signal_date": datetime(2026, 9, 24, tzinfo=timezone.utc),
                "signal_label": "C$400,000 funds Sudbury facility expansion and in-house steel-product capacity",
                "challenge_summary": (
                    "On September 24, 2026, Ontario awarded Jennmar Canada C$400,000 to expand its Sudbury facility, improve efficiency and capacity, create jobs, and bring more steel ground-control products in-house. Independent coverage reports an 8,934-square-foot addition and a new roll-forming line, while Jennmar's official site lists Canadian production of mesh, bolts, plates, friction bolts, straps, cables, and other ground-support variants. Inference: insourcing and adding a forming line increases product and tooling configurations, routing changes, material genealogy, quality checks, supplier transitions, and production-scheduling pressure."
                ),
                "why_relevant": (
                    "Teamcenter can control product variants, manufacturing BOMs, tooling, suppliers, and released engineering changes as work moves in-house. Opcenter can manage scheduling, material genealogy, work instructions, and quality records on the new line, while Tecnomatix can validate line balance and process layout. The facility addition and equipment program are active now, creating urgency before new routings and operating practices become fixed."
                ),
            },
            {
                "source_url": "https://www.canada.ca/en/fednor/news/2026/04/fednor-invests-close-to-3-million-to-help-greater-sudbury-businesses-respond-adapt-and-compete-amid-shifting-market-conditions.html",
                "source_title": "FedNor invests close to $3 million to help Greater Sudbury businesses respond, adapt, and compete amid shifting market conditions",
                "source_publisher": "Government of Canada — FedNor",
                "signal_date": datetime(2026, 4, 24, tzinfo=timezone.utc),
                "signal_label": "C$1M modernizes Sudbury production and adds high-efficiency equipment",
                "challenge_summary": (
                    "On April 24, 2026, FedNor awarded Jennmar Canada C$1 million to modernize its Sudbury operations with high-efficiency manufacturing and processing equipment for locally produced smooth bolts, cable and friction bolts, rebar, flat plates, and related steel ground-control products. The program is expected to create 25 jobs, rapidly increase production, broaden the product offering, and increase domestic market share. Inference: a faster, broader product mix raises capacity-planning, setup, variant, material, inspection, and traceability demands while new operators and equipment are introduced."
                ),
                "why_relevant": (
                    "Teamcenter can govern product and process definitions, approved materials and suppliers, and engineering changes across the expanded product range. Opcenter can give the growing shop consistent work instructions, scheduling, genealogy, and quality capture; Tecnomatix can support equipment and process planning. The funded equipment purchase and hiring program make this a current production-system decision, not a general modernization aspiration."
                ),
            },
        ],
        "pain": "Must insource and scale a broad family of steel ground-control products while controlling tooling, routings, materials, genealogy, and quality across new equipment and staff.",
        "expansion": "Received C$1.4 million across federal and provincial programs for Sudbury equipment, an 8,934-square-foot addition, and a new roll-forming line.",
        "keyword_ids": [8],
        "qualification_status": "qualified",
        "opportunity_score": 91,
        "manufacturing_fit_score": 98,
        "trigger_score": 94,
        "solution_fit_score": 93,
        "evidence_quality_score": 98,
    },
]


# candidates reviewed, new-to-ledger domains, rejected pre-persistence, duplicates/existing
REVIEW = {
    1: (10, 2, 2, 8), 2: (9, 2, 2, 7), 3: (8, 1, 1, 7), 4: (9, 2, 2, 7),
    5: (9, 2, 2, 7), 7: (11, 3, 3, 8), 8: (14, 5, 3, 9), 9: (11, 2, 2, 9),
    10: (10, 2, 2, 8), 11: (9, 2, 2, 7), 12: (7, 1, 1, 6), 13: (10, 2, 2, 8),
    14: (11, 3, 3, 8), 15: (9, 2, 2, 7), 16: (8, 2, 2, 6),
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
            "qualified_published": published_counts[keyword_id],
            "watchlist_published": 0,
            "duplicates_or_existing_skipped": REVIEW[keyword_id][3],
            "last_error": after[keyword_id].last_error,
            "warnings": [
                "Startup Gallery source-specific search returned no publishable lead",
                "Direct X.com search was inaccessible because of ERR_CERT_AUTHORITY_INVALID",
                "Google source-specific searches reached an unusual-traffic interstitial; the warning was not bypassed and search-service fallbacks were used",
                "Breadth quota was not reached; reported counts are the verified domains actually assessed",
            ] + (["SpaceQ and AIAC source-specific searches completed"] if keyword_id in {1, 7, 9, 10, 13, 14} else []),
        } for keyword_id in sorted(after)],
        "coverage": {
            "lookbacks": ["30-day", "180-day", "365-day ongoing-signal fallback"],
            "query_families": [
                "general web/news", "government funding/contracts/procurement", "specialist trade publications",
                "accelerators/investors/university spinouts", "associations/exhibitors/member directories",
                "company hiring/press/product/facility pages",
            ],
            "mandatory_sources": ["Startup Gallery", "X.com", "BetaKit", "NGen"],
            "aerospace_sources": ["SpaceQ", "AIAC member directory and 2026 guide", "Aero Montreal", "DAIR Aerospace"],
            "rotated_sources": [
                "CanadaBuys", "FedNor", "Ontario Newsroom", "Wellington Advertiser", "NGen project funding",
                "ventureLAB Hardware Catalyst", "CDL", "MaRS", "Communitech", "APMA", "OVIN",
                "PLANT", "Canadian Manufacturing", "Electric Autonomy Canada", "Naval News",
                "Shipbuilding Association of Canada", "Canada's Ocean Supercluster", "Oakville Chamber of Commerce",
                "company press releases and hiring pages", "French-language Quebec manufacturing searches",
            ],
            "gap_fill_triggered": False,
            "source_blockers": [
                "X.com: ERR_CERT_AUTHORITY_INVALID",
                "Google: unusual-traffic interstitial after repeated mandatory source searches",
            ],
            "notable_rejections": [
                "Andy's Trailers & Manufacturing had a dated provincial funding trigger but no independently verifiable official company domain, so it failed the identity gate.",
                "Jubilant Radiopharma had a credible facility-modernization trigger but did not closely match a saved keyword.",
                "R.F. Contracting was service-led rather than a target product manufacturer.",
                "OSCP, Seaspan, NordSpace, Volatus, Cyberworks Robotics, and other known prospects were rediscovered and skipped as existing-domain duplicates without a stronger new keyword result.",
                "Directories, accelerator listings, association pages, and social posts remained discovery-only and did not qualify any company by themselves.",
            ],
        },
        "duplicate_audit": {"canonical_domains": 0, "source_urls": 0, "keyword_company_pairs": 0},
    }, indent=2, default=str))


if __name__ == "__main__":
    main()
