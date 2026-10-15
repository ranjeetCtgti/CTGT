from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from db.database import Database


RUN_AT = datetime.now(timezone.utc)
LOCK_PATH = Path(
    r"C:\Users\ranjeet.chaudhary\.codex\automations\daily-keyword-company-research\run.lock"
)

EXPECTED_SEARCH_COUNTS = {
    1: 51,
    2: 50,
    3: 50,
    4: 46,
    5: 27,
    7: 20,
    8: 20,
    9: 18,
    10: 18,
    11: 18,
    12: 18,
    13: 18,
    14: 13,
    15: 13,
    16: 7,
}

# Conservative counts from the in-app Browser pass. The browser inspected the
# first result page for nine or ten independent query families per keyword.
# Candidate-domain counts are lower because directories, articles, foreign
# companies, and repeated source domains are not counted as candidate identities.
COVERAGE = {
    1: (87, 16, 6, 10, 6, []),
    2: (90, 18, 8, 11, 7, []),
    3: (81, 12, 5, 7, 5, []),
    4: (81, 13, 5, 8, 5, []),
    5: (82, 16, 6, 10, 6, []),
    7: (81, 17, 6, 10, 7, []),
    8: (90, 20, 10, 11, 8, ["Smartrend Manufacturing Group"]),
    9: (91, 18, 7, 11, 7, []),
    10: (82, 20, 8, 10, 8, ["Argus Industries", "FELLFAB"]),
    11: (83, 18, 8, 8, 8, ["Fort Garry Fire Trucks", "International Truck Body"]),
    12: (96, 20, 10, 12, 7, ["Protocase"]),
    13: (91, 19, 7, 11, 8, []),
    14: (79, 20, 8, 12, 8, []),
    15: (92, 14, 5, 9, 5, []),
    16: (89, 18, 8, 12, 6, []),
}

COMMON_SOURCES = ["Startup Gallery", "public X/X-ray", "BetaKit", "NGen"]
ROTATED_SOURCES = {
    1: ["SpaceQ", "AIAC", "Canada.ca", "ventureLAB", "DAIR Aerospace"],
    2: ["Canada.ca", "Canadian Manufacturing", "ventureLAB", "Automate Canada"],
    3: ["Canada.ca", "Naval News", "Ocean Supercluster", "Shipbuilding Association of Canada"],
    4: ["Canada.ca", "Electric Autonomy Canada", "OVIN", "APMA"],
    5: ["Canada.ca", "PLANT", "BDC", "Canadian Manufacturers & Exporters"],
    7: ["SpaceQ", "AIAC", "Canada.ca", "ventureLAB", "DAIR Aerospace"],
    8: ["Canada.ca", "BetaKit", "Communitech", "NGen project portfolio"],
    9: ["SpaceQ", "AIAC", "Canada.ca", "Aero Montreal", "DAIR Aerospace"],
    10: ["CanadaBuys", "Skies Magazine", "CANSEC", "AIAC", "DAIR Aerospace"],
    11: ["Canada.ca", "Automotive News Canada", "OVIN", "APMA", "Electric Autonomy Canada"],
    12: ["NRC IRAP", "PLANT", "NGen", "Canadian Manufacturers & Exporters", "company hiring pages"],
    13: ["Canada.ca", "SpaceQ", "OVIN", "AIAC", "company press pages"],
    14: ["Canada.ca", "SpaceQ", "CANSEC", "AIAC", "CADSI"],
    15: ["Canada.ca", "Electric Autonomy Canada", "OVIN", "APMA", "French Quebec searches"],
    16: ["NRC IRAP", "PLANT", "NGen", "Canadian Manufacturers & Exporters", "French Quebec searches"],
}

WORKBOOK_BLOCKER = (
    "Research completed; publication held because both permitted connected-session "
    "checks found no already-open exact canonical OneDrive Keyword_Companies.xlsx. "
    "The required workbook identity comparison and append/upsert sync could not run. "
    "Direct X.com was certificate-blocked; Google and Bing presented human-verification "
    "challenges, so no barrier was bypassed and DuckDuckGo/direct-source fallback was used."
)


def main() -> None:
    if not LOCK_PATH.exists():
        raise RuntimeError("Exclusive automation run lock is not held")

    load_dotenv(REPO_ROOT / ".env")
    database = Database(os.environ["DATABASE_URL"])
    database.initialize()
    before = {item.id: item for item in database.list_keywords()}

    if set(before) != set(EXPECTED_SEARCH_COUNTS):
        raise RuntimeError(f"Persistent keyword set changed: {sorted(before)}")
    for keyword_id, expected in EXPECTED_SEARCH_COUNTS.items():
        actual = before[keyword_id].search_count
        if actual != expected:
            raise RuntimeError(
                f"Refusing duplicate/partial audit write for keyword {keyword_id}: "
                f"expected {expected}, found {actual}"
            )

    for keyword_id in sorted(before):
        row = database.record_keyword_search(
            keyword_id,
            result_count=0,
            error=WORKBOOK_BLOCKER,
        )
        if row is None:
            raise RuntimeError(f"Keyword {keyword_id} disappeared during audit write")

    after = {item.id: item for item in database.list_keywords()}
    report: dict[int, dict[str, object]] = {}
    for keyword_id, item in before.items():
        if after[keyword_id].search_count != item.search_count + 1:
            raise RuntimeError(f"Keyword {keyword_id} did not advance exactly once")
        (
            raw_results,
            candidate_domains,
            new_domains,
            rejected,
            duplicates,
            held,
        ) = COVERAGE[keyword_id]
        report[keyword_id] = {
            "keyword": item.keyword,
            "lookback": "rolling 30 days, then 180 days, with 365-day ongoing-discovery fallback",
            "query_families": 9 if keyword_id not in {9, 10, 11, 12, 13, 14, 15, 16} else 10,
            "raw_results_inspected": raw_results,
            "unique_candidate_domains_reviewed": candidate_domains,
            "new_to_ledger_domains_reviewed": new_domains,
            "rejected_before_persistence": rejected,
            "qualified_published": 0,
            "watchlist_published": 0,
            "existing_records_upgraded_or_hidden": 0,
            "duplicates_skipped_or_reassessed": duplicates,
            "held_pending_workbook_identity_gate": held,
            "sources_checked": COMMON_SOURCES + ROTATED_SOURCES[keyword_id],
            "startup_gallery_outcome": "checked; no independently qualifying Canadian candidate",
            "x_outcome": "public X-ray checked; direct X.com blocked by ERR_CERT_AUTHORITY_INVALID",
            "search_count_before": item.search_count,
            "search_count_after": after[keyword_id].search_count,
        }

    print(
        json.dumps(
            {
                "status": "completed_with_publication_blocker",
                "run_at": RUN_AT.isoformat(),
                "coverage": report,
                "gap_fill": {
                    "verified_canonical_domains_reviewed": 29,
                    "new_to_database_ledger": 28,
                    "existing_domain_duplicates": ["enginuityinc.ca"],
                    "source_groups": [
                        "PrairiesCan Winnipeg advanced-manufacturing backgrounder",
                        "FedDev Ontario Hamilton tariff-response backgrounder",
                        "ACOA Nova Scotia tariff-response backgrounder",
                        "official company sites and independent identity searches",
                    ],
                },
                "held_candidates": {
                    "qualified_like": [
                        "Fort Garry Fire Trucks",
                        "International Truck Body",
                        "Smartrend Manufacturing Group",
                        "Argus Industries",
                        "FELLFAB",
                    ],
                    "watchlist_like": ["Protocase"],
                    "publication_reason": WORKBOOK_BLOCKER,
                },
                "database_writes": {
                    "companies": 0,
                    "signals": 0,
                    "keyword_company_results": 0,
                    "keyword_search_audits": len(before),
                },
                "workbook": {
                    "canonical": {
                        "inserted": 0,
                        "updated": 0,
                        "unchanged_last_verified": 139,
                        "failed": 1,
                        "removed": 0,
                    },
                    "local_staging": {
                        "inserted": 0,
                        "updated": 0,
                        "unchanged_last_verified": 128,
                        "failed_or_deferred": 11,
                        "removed": 0,
                    },
                },
                "blockers": [
                    WORKBOOK_BLOCKER,
                    "The browser challenges were not solved or bypassed.",
                ],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
