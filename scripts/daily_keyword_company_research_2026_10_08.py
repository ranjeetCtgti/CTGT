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


PROSPECT = {
    "company_name": "Rock Tech Lithium Inc.",
    "company_domain": "rocktechlithium.com",
    "company_url": "https://rocktechlithium.com/en/",
    "location": "Toronto and Red Rock, Ontario, Canada",
    "industry": "Battery-grade lithium conversion and critical-minerals processing",
    "products": ["Teamcenter", "Simcenter"],
    "identity": CompanyIdentityEvidence(
        official_name="Rock Tech Lithium Inc.",
        official_website_url="https://rocktechlithium.com/en/",
        corroborating_urls=(
            "https://mugglehead.com/rock-tech-lithium-red-rock-converter-preliminary-dfs-capex/",
            "https://rocktechlithium.com/en/rock-tech-lithium-and-siemens-canada-sign-agreements-to-bring-advanced-german-engineering-to-ontario-lithium-converter-project/",
        ),
    ),
    "signals": [
        {
            "source_url": "https://mugglehead.com/rock-tech-lithium-red-rock-converter-preliminary-dfs-capex/",
            "source_title": "Rock Tech Lithium estimates Red Rock converter capital cost at C$596M",
            "source_publisher": "Mugglehead",
            "signal_date": datetime(2026, 10, 7, tzinfo=timezone.utc),
            "reason": (
                "On October 7, 2026, Mugglehead reported that preliminary results from Rock Tech Lithium's "
                "definitive feasibility study put the Red Rock converter's capital cost at C$596 million, "
                "including C$546 million of direct costs and C$50 million of owner's costs, for a proposed "
                "Ontario plant designed to produce about 30,000 tonnes of lithium salts per year. The final "
                "study is due in December 2026 and construction is targeted for the second half of 2027, subject "
                "to approvals and financing. Inference: moving from feasibility into a C$596 million process-plant "
                "program creates immediate pressure to control plant configurations, supplier/equipment data, "
                "engineering changes, process models, energy and material-flow assumptions, and validation "
                "evidence; Teamcenter and Simcenter are the smallest defensible CTGTI fit."
            ),
            "pain": (
                "Must convert an optimized feasibility design into a controlled, financeable plant baseline while "
                "coordinating process models, equipment and supplier data, engineering changes, energy and material "
                "flows, approvals, and validation evidence."
            ),
            "expansion": (
                "Advanced a C$596 million Red Rock converter design rated at about 30,000 tonnes of lithium salts "
                "per year, with a final feasibility study due in December 2026 and construction targeted for the "
                "second half of 2027."
            ),
        },
        {
            "source_url": "https://rocktechlithium.com/en/rock-tech-lithium-and-siemens-canada-sign-agreements-to-bring-advanced-german-engineering-to-ontario-lithium-converter-project/",
            "source_title": (
                "Rock Tech Lithium and Siemens Canada Sign Agreements to Bring Advanced German Engineering "
                "to Ontario Lithium Converter Project"
            ),
            "source_publisher": "Rock Tech Lithium",
            "signal_date": datetime(2026, 9, 22, tzinfo=timezone.utc),
            "reason": (
                "On September 22, 2026, Rock Tech Lithium said Siemens Canada had begun the first implementation "
                "phase of its Red Rock collaboration: a physics-based Digital Process Twin using the ongoing "
                "definitive feasibility study, plus specialized support for process control, instrumentation, and "
                "automation architecture. Rock Tech said the twin will model plant processes, energy flows, and "
                "material streams across feasibility, engineering, construction, and operations; its Ontario "
                "converter is designed for up to 32,000 tonnes of lithium-carbonate-equivalent output annually. "
                "Inference: the active Siemens implementation creates a near-term opening to govern the digital "
                "plant baseline and connect validated simulation models to controlled lifecycle data; Teamcenter "
                "and Simcenter extend the digital thread without adding unsupported products."
            ),
            "pain": (
                "Must keep process-twin assumptions, plant and equipment configurations, instrumentation and "
                "automation architecture, design decisions, and feasibility evidence synchronized through "
                "engineering, construction, commissioning, and operations."
            ),
            "expansion": (
                "Started a Siemens-supported Digital Process Twin and process-control, instrumentation, and "
                "automation workstream for the planned Red Rock lithium converter during the active definitive "
                "feasibility study."
            ),
        },
    ],
    "keyword_ids": [5, 8],
    "signal_label": "C$596M Red Rock converter enters digital-twin feasibility phase",
    "challenge_summary": (
        "On October 7, 2026, Rock Tech Lithium's preliminary definitive feasibility results put the planned Red "
        "Rock, Ontario converter at C$596 million, with 30,000 tonnes of annual lithium-salt capacity, a final study "
        "due in December 2026, and construction targeted for the second half of 2027. On September 22, Rock Tech "
        "also began a Siemens Canada Digital Process Twin and process-control, instrumentation, and automation "
        "workstream for the plant. Inference: the project now has urgent plant-configuration, supplier/equipment, "
        "engineering-change, process-model, energy/material-flow, and validation-control complexity before its "
        "investment and construction decisions."
    ),
    "why_relevant": (
        "Teamcenter can govern the plant, equipment, supplier, and engineering baselines while preserving the "
        "decision trail from feasibility through construction and operations. Simcenter can extend the active "
        "physics-based process twin for energy, material-flow, efficiency, emissions, and operating-reliability "
        "validation. The December feasibility deadline and C$596 million capital decision make this a current "
        "Siemens-ecosystem opportunity rather than a speculative future need."
    ),
    "qualification_status": "qualified",
    "opportunity_score": 94,
    "manufacturing_fit_score": 97,
    "trigger_score": 97,
    "solution_fit_score": 96,
    "evidence_quality_score": 96,
}


# Conservative candidate-domain counts derived from the browser result review.
# Search-result/source-domain breadth is reported separately below; these values
# do not count publishers, directories, or search engines as candidate companies.
REVIEW = {
    1: (16, 8, 11, 0, 0, 5),
    2: (20, 9, 12, 0, 0, 8),
    3: (15, 5, 10, 0, 0, 5),
    4: (17, 6, 11, 0, 0, 6),
    5: (19, 8, 10, 1, 0, 8),
    7: (18, 6, 12, 0, 0, 6),
    8: (22, 9, 12, 1, 0, 9),
    9: (18, 6, 12, 0, 0, 6),
    10: (19, 6, 13, 0, 0, 6),
    11: (16, 5, 11, 0, 0, 5),
    12: (15, 5, 11, 0, 0, 4),
    13: (21, 8, 13, 0, 0, 8),
    14: (22, 8, 14, 0, 0, 8),
    15: (18, 6, 12, 0, 0, 6),
    16: (17, 6, 12, 0, 0, 5),
}

RESULT_CARDS = {
    1: (80, 40), 2: (86, 37), 3: (48, 32), 4: (58, 32), 5: (67, 35),
    7: (56, 20), 8: (70, 28), 9: (60, 24), 10: (75, 30), 11: (73, 29),
    12: (75, 29), 13: (87, 37), 14: (89, 30), 15: (87, 28), 16: (89, 46),
}

ZERO_OR_BLOCKED = {
    1: ["Canada.ca source-specific query returned zero results"],
    2: [],
    3: ["ventureLAB, Startup Gallery, BetaKit and NGen source-specific queries returned zero relevant results"],
    4: ["NGen source-specific query returned zero relevant results"],
    5: ["NGen source-specific query returned zero relevant results"],
    7: ["ventureLAB, AIAC, Startup Gallery and NGen source-specific queries returned zero relevant results"],
    8: ["association and NGen source-specific queries returned zero relevant results"],
    9: ["Google presented human verification during the NGen check; Yahoo and direct NGen fallback were used"],
    10: ["Canada.ca source-specific query returned zero results"],
    11: ["Canada.ca source-specific query returned zero results"],
    12: [], 13: [], 14: [], 15: [], 16: [],
}


def make_signal(evidence: dict) -> ExtractedSignal:
    return ExtractedSignal(
        company_name=PROSPECT["company_name"],
        company_domain=PROSPECT["company_domain"],
        company_url=PROSPECT["company_url"],
        location=PROSPECT["location"],
        industry=PROSPECT["industry"],
        company_industry=PROSPECT["industry"],
        software=PROSPECT["products"],
        signal_type="news",
        signal_source="news",
        pain_signals=[evidence["pain"]],
        expansion_signals=[evidence["expansion"]],
        raw_score=PROSPECT["opportunity_score"],
        confidence=PROSPECT["evidence_quality_score"] / 100,
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
    before = {row.id: row for row in database.list_keywords()}
    expected = {1, 2, 3, 4, 5, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16}
    if set(before) != expected:
        raise RuntimeError(f"Persistent keyword set changed: {sorted(before)}")

    signals = [make_signal(item) for item in PROSPECT["signals"]]
    for signal in signals:
        verify_company_identity(signal, PROSPECT["identity"])

    with database.session() as session:
        preexisting = session.execute(
            select(CompanyRecord.id, CompanyRecord.company_name, CompanyRecord.company_domain).where(
                (func.lower(CompanyRecord.company_domain) == PROSPECT["company_domain"].lower())
                | (func.lower(CompanyRecord.company_name) == PROSPECT["company_name"].lower())
            )
        ).all()
    if preexisting:
        raise RuntimeError(f"Rock Tech identity appeared after pre-persistence comparison: {preexisting}")

    persisted_evidence = []
    company = None
    for signal, evidence in zip(signals, PROSPECT["signals"], strict=True):
        saved, company = database.persist_verified_signal(signal, PROSPECT["identity"])
        persisted_evidence.append(
            {
                "source_url": evidence["source_url"],
                "created": saved.created,
                "duplicate_url": saved.duplicate_url,
            }
        )
    if company is None:
        raise RuntimeError("Rock Tech persistence returned no company")

    primary = PROSPECT["signals"][0]
    keyword_rows = []
    for keyword_id in PROSPECT["keyword_ids"]:
        row = database.record_keyword_company(
            keyword_id,
            PROSPECT["company_name"],
            PROSPECT["company_domain"],
            source_url=primary["source_url"],
            source_title=primary["source_title"],
            source_publisher=primary["source_publisher"],
            signal_label=PROSPECT["signal_label"],
            signal_date=primary["signal_date"],
            challenge_summary=PROSPECT["challenge_summary"],
            why_relevant=PROSPECT["why_relevant"],
            recommended_products=PROSPECT["products"],
            qualification_status=PROSPECT["qualification_status"],
            opportunity_score=PROSPECT["opportunity_score"],
            manufacturing_fit_score=PROSPECT["manufacturing_fit_score"],
            trigger_score=PROSPECT["trigger_score"],
            solution_fit_score=PROSPECT["solution_fit_score"],
            evidence_quality_score=PROSPECT["evidence_quality_score"],
            seen_at=RUN_AT,
        )
        if row is None:
            raise RuntimeError(f"Could not link Rock Tech to keyword {keyword_id}")
        keyword_rows.append({"keyword_id": keyword_id, "result_id": row.id})

    published = {keyword_id: 0 for keyword_id in before}
    for keyword_id in PROSPECT["keyword_ids"]:
        published[keyword_id] = 1
    for keyword_id in sorted(before):
        if database.record_keyword_search(keyword_id, result_count=published[keyword_id], error=None) is None:
            raise RuntimeError(f"Could not record keyword search {keyword_id}")

    after = {row.id: row for row in database.list_keywords()}
    for keyword_id, prior in before.items():
        current = after[keyword_id]
        if current.search_count != prior.search_count + 1:
            raise RuntimeError(f"Keyword {keyword_id} did not advance exactly once")
        if current.last_error is not None:
            raise RuntimeError(f"Keyword {keyword_id} retained error: {current.last_error}")

    with database.session() as session:
        company_id = session.scalar(
            select(CompanyRecord.id).where(
                func.lower(CompanyRecord.company_domain) == PROSPECT["company_domain"].lower()
            )
        )
        duplicate_domains = session.execute(
            select(func.lower(CompanyRecord.company_domain), func.count(CompanyRecord.id))
            .where(CompanyRecord.company_domain.is_not(None))
            .group_by(func.lower(CompanyRecord.company_domain))
            .having(func.count(CompanyRecord.id) > 1)
        ).all()
        duplicate_sources = session.execute(
            select(SignalRecord.source_url, func.count(SignalRecord.id))
            .where(SignalRecord.source_url.is_not(None))
            .group_by(SignalRecord.source_url)
            .having(func.count(SignalRecord.id) > 1)
        ).all()
        duplicate_keyword_pairs = session.execute(
            select(
                KeywordCompanyResultRecord.keyword_id,
                KeywordCompanyResultRecord.company_id,
                func.count(KeywordCompanyResultRecord.id),
            )
            .group_by(KeywordCompanyResultRecord.keyword_id, KeywordCompanyResultRecord.company_id)
            .having(func.count(KeywordCompanyResultRecord.id) > 1)
        ).all()
        eligible_count = session.scalar(
            select(func.count(func.distinct(KeywordCompanyResultRecord.company_id))).where(
                KeywordCompanyResultRecord.qualification_status.in_(("qualified", "watchlist"))
            )
        )

    if company_id is None or duplicate_domains or duplicate_sources or duplicate_keyword_pairs:
        raise RuntimeError(
            "Post-write audit failed: "
            f"company_id={company_id}, domains={duplicate_domains}, sources={duplicate_sources}, "
            f"keyword_pairs={duplicate_keyword_pairs}"
        )

    print(
        json.dumps(
            {
                "run_at": RUN_AT.isoformat(),
                "company_id": company_id,
                "company_name": company.company_name,
                "company_domain": company.company_domain,
                "evidence": persisted_evidence,
                "keyword_rows": keyword_rows,
                "keyword_audits": [
                    {
                        "id": keyword_id,
                        "keyword": after[keyword_id].keyword,
                        "search_count_before": before[keyword_id].search_count,
                        "search_count_after": after[keyword_id].search_count,
                        "candidate_domains_reviewed": REVIEW[keyword_id][0],
                        "new_to_ledger_domains_reviewed": REVIEW[keyword_id][1],
                        "rejected_before_persistence": REVIEW[keyword_id][2],
                        "qualified_published": REVIEW[keyword_id][3],
                        "watchlist_published": REVIEW[keyword_id][4],
                        "duplicates_or_existing_skipped": REVIEW[keyword_id][5],
                        "result_cards_inspected": RESULT_CARDS[keyword_id][0],
                        "unique_result_source_domains": RESULT_CARDS[keyword_id][1],
                        "warnings_or_zero_results": ZERO_OR_BLOCKED[keyword_id],
                        "last_error": after[keyword_id].last_error,
                    }
                    for keyword_id in sorted(after)
                ],
                "coverage": {
                    "lookbacks": ["30-day", "180-day", "365-day ongoing-signal fallback"],
                    "query_families": [
                        "general web/news",
                        "government funding/contracts/procurement",
                        "specialist trade publications",
                        "accelerators/investors/university spinouts",
                        "associations/exhibitors/member directories",
                        "company hiring/press/product/facility pages",
                    ],
                    "mandatory_sources": [
                        "Startup Gallery",
                        "public X/X-ray",
                        "BetaKit",
                        "NGen",
                        "SpaceQ for aerospace/space/defence themes",
                        "AIAC directory/news for aerospace/defence themes",
                    ],
                    "rotated_sources": [
                        "Canada.ca and CanadaBuys",
                        "ventureLAB Hardware Catalyst",
                        "F6S",
                        "APMA and Project Arrow",
                        "OVIN",
                        "Aero Montreal and DAIR Aerospace",
                        "Oakville Chamber of Commerce",
                        "Canada's Ocean Supercluster",
                        "Canadian Manufacturing and PLANT",
                        "Electric Autonomy Canada",
                        "Marine Log and Naval News",
                        "PR Newswire and company press pages",
                    ],
                    "browser_warnings": [
                        "Bing presented a human-verification challenge and was not bypassed; Google and Yahoo/direct-source fallback completed coverage.",
                        "Google later presented human verification during keyword 9's NGen check; Yahoo and direct NGen fallback were used.",
                    ],
                    "discovery_only_rejections": [
                        "Ratel Robotics is Ukrainian; the Canadian trigger is a non-binding co-production MOU with General Dynamics Mission Systems-Canada.",
                        "Uncrewed Systems Inc. showed Canadian assembly and R&D but no dated company-specific award, financing, or committed production trigger.",
                        "Advanced Tactical Vehicles Inc. had official product-development identity but no current contract, funding, facility, or production trigger beyond its May launch.",
                        "7mesh disclosed a competing PLM implementation and outsourced production, so it was not treated as a current CTGTI prospect.",
                    ],
                },
                "eligible_company_count": eligible_count,
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
