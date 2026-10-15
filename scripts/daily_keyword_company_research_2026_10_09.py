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
    "company_name": "QuantumCore Ltd.",
    "company_domain": "qncor.ca",
    "company_url": "https://www.qncor.ca/",
    "location": "Waterloo, Ontario, Canada",
    "industry": "Cryogenic quantum-computing hardware and signal-amplifier components",
    "products": ["Teamcenter", "Simcenter"],
    "identity": CompanyIdentityEvidence(
        official_name="QuantumCore Ltd.",
        official_website_url="https://www.qncor.ca/",
        corroborating_urls=(
            "https://uwaterloo.ca/news/new-waterloo-quantum-startup-gains-fast-momentum-107-million",
        ),
    ),
    "source_url": "https://uwaterloo.ca/news/new-waterloo-quantum-startup-gains-fast-momentum-107-million",
    "source_title": "New Waterloo quantum startup gains fast momentum with $10.7 million in funding",
    "source_publisher": "University of Waterloo",
    "signal_date": datetime(2026, 4, 24, tzinfo=timezone.utc),
    "signal_label": "$10.7M funding advances cryogenic quantum-amplifier commercialization",
    "challenge_summary": (
        "On April 24, 2026, the University of Waterloo reported that IQC spinout QuantumCore had secured "
        "$10.7 million in dilutive and non-dilutive funding: $9 million from two private rounds and $1.7 "
        "million through an NSERC Alliance Grant. The company is commercializing an amplifier that carries "
        "superconducting-quantum-chip readout signals from near absolute zero to room temperature, and it had "
        "opened a Waterloo office and lab, hired five full-time technical employees, and gained access to the "
        "university's Quantum Nano Fabrication and Characterization Facility. Inference: moving a cryogenic "
        "chipset and amplifier platform toward customer beta and scalable production creates configuration, "
        "supplier, test-data, thermal and signal-integrity validation, and engineering-change pressure."
    ),
    "why_relevant": (
        "Teamcenter can control the evolving amplifier and cryo-optimized chipset product structure, component "
        "revisions, supplier data, and lab-to-production changes. Simcenter can support the coupled thermal, "
        "electromagnetic, and signal-integrity validation needed to prove performance at cryogenic temperatures. "
        "The fresh capital, new lab, technical hiring, and stated beta/commercialization push make the engineering "
        "system decision timely rather than speculative."
    ),
    "pain": (
        "Must convert research prototypes into repeatable quantum-computing hardware while controlling cryogenic "
        "component configurations, suppliers, test results, signal-integrity and thermal models, and engineering changes."
    ),
    "expansion": (
        "Raised $10.7 million, hired five technical employees, opened a Waterloo office and lab, and advanced a "
        "cryogenic amplifier platform toward commercialization."
    ),
    "keyword_ids": [8],
    "qualification_status": "qualified",
    "opportunity_score": 88,
    "manufacturing_fit_score": 93,
    "trigger_score": 89,
    "solution_fit_score": 90,
    "evidence_quality_score": 94,
}

# candidate domains, new-to-ledger domains, pre-persistence rejections,
# qualified, watchlist, and existing-domain duplicates, respectively.
REVIEW = {
    1: (15, 7, 11, 0, 0, 4),
    2: (17, 8, 11, 0, 0, 6),
    3: (15, 5, 11, 0, 0, 4),
    4: (16, 7, 11, 0, 0, 5),
    5: (17, 7, 12, 0, 0, 5),
    7: (16, 7, 10, 0, 0, 6),
    8: (35, 27, 27, 1, 0, 7),
    9: (16, 6, 10, 0, 0, 6),
    10: (15, 5, 10, 0, 0, 5),
    11: (15, 5, 10, 0, 0, 5),
    12: (15, 6, 13, 0, 0, 2),
    13: (17, 8, 11, 0, 0, 6),
    14: (18, 8, 12, 0, 0, 6),
    15: (15, 7, 11, 0, 0, 4),
    16: (15, 8, 13, 0, 0, 2),
}

RESULT_CARDS = {
    1: 50, 2: 50, 3: 47, 4: 50, 5: 50,
    7: 50, 8: 50, 9: 50, 10: 50, 11: 50,
    12: 50, 13: 50, 14: 50, 15: 50, 16: 50,
}


def make_signal() -> ExtractedSignal:
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
        pain_signals=[PROSPECT["pain"]],
        expansion_signals=[PROSPECT["expansion"]],
        raw_score=PROSPECT["opportunity_score"],
        confidence=PROSPECT["evidence_quality_score"] / 100,
        reason=PROSPECT["challenge_summary"] + " " + PROSPECT["why_relevant"],
        source_url=PROSPECT["source_url"],
        source_title=PROSPECT["source_title"],
        detected_at=PROSPECT["signal_date"],
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

    signal = make_signal()
    verify_company_identity(signal, PROSPECT["identity"])

    with database.session() as session:
        preexisting = session.execute(
            select(CompanyRecord.id, CompanyRecord.company_name, CompanyRecord.company_domain).where(
                (func.lower(CompanyRecord.company_domain) == PROSPECT["company_domain"].lower())
                | (func.lower(CompanyRecord.company_name) == PROSPECT["company_name"].lower())
                | (func.lower(CompanyRecord.company_name) == "quantumcore")
            )
        ).all()
    if preexisting:
        raise RuntimeError(f"QuantumCore identity appeared after pre-persistence comparison: {preexisting}")

    saved, company = database.persist_verified_signal(signal, PROSPECT["identity"])
    if company is None or not saved.created or saved.duplicate_url:
        raise RuntimeError(
            f"Unexpected QuantumCore persistence result: company={company}, "
            f"created={saved.created}, duplicate={saved.duplicate_url}"
        )

    keyword_rows = []
    for keyword_id in PROSPECT["keyword_ids"]:
        row = database.record_keyword_company(
            keyword_id,
            PROSPECT["company_name"],
            PROSPECT["company_domain"],
            source_url=PROSPECT["source_url"],
            source_title=PROSPECT["source_title"],
            source_publisher=PROSPECT["source_publisher"],
            signal_label=PROSPECT["signal_label"],
            signal_date=PROSPECT["signal_date"],
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
            raise RuntimeError(f"Could not link QuantumCore to keyword {keyword_id}")
        keyword_rows.append({"keyword_id": keyword_id, "result_id": row.id})

    published = {keyword_id: 0 for keyword_id in before}
    published[8] = 1
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
            select(CompanyRecord.id).where(func.lower(CompanyRecord.company_domain) == "qncor.ca")
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

    print(json.dumps({
        "run_at": RUN_AT.isoformat(),
        "company_id": company_id,
        "company_name": company.company_name,
        "company_domain": company.company_domain,
        "evidence_created": saved.created,
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
                "result_cards_inspected": RESULT_CARDS[keyword_id],
                "warnings_or_zero_results": [
                    "Startup Gallery Canada collection checked; no relevant physical-product candidate",
                    "X.com direct search blocked by ERR_CERT_AUTHORITY_INVALID; indexed X search returned zero",
                    "BetaKit source-specific search returned zero; general search results were inspected",
                    "NGen source-specific search returned zero; indexed project and announcement results were inspected",
                ] + (["SpaceQ source-specific search returned zero; AIAC directory/news results were inspected"]
                     if keyword_id in {1, 7, 9, 10, 13, 14} else []),
                "last_error": after[keyword_id].last_error,
            }
            for keyword_id in sorted(after)
        ],
        "coverage": {
            "lookbacks": ["30-day", "180-day", "365-day ongoing-signal fallback"],
            "query_families": [
                "general web/news", "government funding/contracts/procurement",
                "specialist trade publications", "accelerators/investors/university spinouts",
                "associations/exhibitors/member directories", "company hiring/press/product/facility pages",
            ],
            "rotated_sources": [
                "Canada.ca and CanadaBuys", "FedDev Ontario", "Quebec funding portals",
                "ventureLAB Hardware Catalyst", "CDL, MaRS and Communitech", "F6S",
                "CANSEC exhibitors", "APMA and OVIN", "AIAC, Aero Montreal and DAIR Aerospace",
                "Oakville Chamber of Commerce", "Canada's Ocean Supercluster",
                "Canadian Manufacturing and PLANT", "Newswire and company press pages",
                "University of Waterloo spinouts and engineering news",
            ],
            "gap_fill": {
                "triggered": True,
                "additional_new_to_ledger_domains_reviewed": 35,
                "new_publishable": ["qncor.ca"],
            },
            "notable_rejections": [
                "Atlas Engineered Products had an October 8 robotic-line trigger but is an existing company and does not match a saved startup/PLM-intent keyword.",
                "Aethon Aerial was service-led and lacked verified own-product manufacturing evidence.",
                "Rheinmetall Canada remained excluded because its stored and verified canonical domains conflict.",
                "Vention and Stellantis were existing-domain duplicates with no newer publishable evidence.",
            ],
            "identity_gate": "Official qncor.ca site, University of Waterloo corroboration, PostgreSQL, and the connected workbook were checked before persistence.",
        },
        "eligible_company_count": eligible_count,
        "duplicate_audit": {"canonical_domains": 0, "source_urls": 0, "keyword_company_pairs": 0},
    }, indent=2, default=str))


if __name__ == "__main__":
    main()
