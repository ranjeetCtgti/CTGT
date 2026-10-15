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
    1: 53,
    2: 52,
    3: 52,
    4: 48,
    5: 29,
    7: 22,
    8: 22,
    9: 20,
    10: 20,
    11: 20,
    12: 20,
    13: 20,
    14: 15,
    15: 15,
    16: 9,
}

# Counts are conservative, based only on named organizations visibly reviewed
# across the ten source-specific query families.  The final tuple entry records
# candidates that appeared repeatedly and were therefore treated as duplicates.
# Format: raw results, candidate domains, new domains, rejected, duplicates.
COVERAGE = {
    1: (96, 16, 7, 9, 9),
    2: (100, 18, 10, 11, 8),
    3: (81, 12, 6, 8, 6),
    4: (92, 16, 7, 10, 9),
    5: (100, 18, 10, 11, 9),
    7: (81, 15, 7, 9, 8),
    8: (100, 18, 11, 12, 8),
    9: (110, 17, 8, 10, 10),
    10: (100, 16, 8, 10, 9),
    11: (80, 15, 8, 9, 8),
    12: (81, 8, 4, 6, 5),
    13: (100, 15, 7, 9, 9),
    14: (110, 16, 9, 9, 10),
    15: (90, 13, 7, 8, 8),
    16: (82, 8, 4, 6, 5),
}

COMMON_SOURCES = [
    "Startup Gallery",
    "public X Google X-ray",
    "direct public X.com",
    "BetaKit",
    "NGen",
]

ROTATED_SOURCES = {
    1: ["Canada.ca", "SpaceQ", "ventureLAB", "AIAC", "company press and hiring pages"],
    2: ["Canada.ca", "PLANT", "ventureLAB", "Automate Canada", "company press and hiring pages"],
    3: ["Canada.ca", "Naval News", "Canada's Ocean Supercluster", "Shipbuilding Association search", "shipyard press pages"],
    4: ["Canada.ca", "Electric Autonomy", "ventureLAB", "APMA", "vehicle-maker press pages"],
    5: ["Canada.ca", "PLANT", "MaRS", "NGen collaboration portfolio", "company facility pages"],
    7: ["Canada.ca", "SpaceQ", "ventureLAB", "AIAC", "UAV/eVTOL press pages"],
    8: ["Canada.ca", "BetaKit hardware", "ventureLAB", "NGen collaborations", "company funding pages"],
    9: ["Canada.ca", "Skies", "Aero Montreal", "AIAC", "SpaceQ", "company manufacturing pages"],
    10: ["CanadaBuys", "Canadian Metalworking", "DAIR Aerospace", "AIAC", "SpaceQ", "supplier press pages"],
    11: ["Canada.ca", "Automotive News Canada search", "OVIN search", "APMA", "vehicle-maker production pages"],
    12: ["Canada.ca/NRC", "PLANT", "NGen", "CME search", "manufacturer PLM/ERP hiring pages"],
    13: ["Canada.ca", "Electric Autonomy", "OVIN search", "AIAC", "SpaceQ", "autonomy press pages"],
    14: ["Canada.ca", "Canadian Defence Review", "ventureLAB", "CADSI", "AIAC", "SpaceQ"],
    15: ["Canada.ca", "Electric Autonomy", "OVIN search", "APMA", "EV-maker production pages"],
    16: ["Canada.ca/NRC", "PLANT", "NGen", "CME search", "manufacturer PLM hiring pages"],
}

WORKBOOK_BLOCKER = (
    "Research completed; publication held because both permitted connected-session "
    "checks found no already-open exact canonical OneDrive Keyword_Companies.xlsx. "
    "The required workbook identity comparison and append/upsert sync could not run. "
    "Direct X.com was certificate-blocked and Google presented a human-verification "
    "challenge near the end of the mandatory-source pass; no barrier was bypassed, "
    "and DuckDuckGo/direct-source fallback completed the remaining coverage."
)

HELD_CANDIDATES = [
    {
        "company": "Magellan Aerospace Corporation",
        "domain": "magellan.aero",
        "trigger": "July 20, 2026 Government of Canada M-72 production-development contract",
        "status": "qualified-like",
    },
    {
        "company": "EnerQuest Technologies Solutions Inc.",
        "domain": "enerquest.ca",
        "trigger": "March 17, 2026 C$15.8M Harrow plant expansion and switchgear reshoring",
        "status": "qualified-like",
    },
    {
        "company": "CIMtech Green Energy Manufacturing Inc.",
        "domain": "cimtechgreenenergy.com",
        "trigger": "June 2, 2026 advanced-manufacturing capacity expansion in Vancouver",
        "status": "qualified-like",
    },
    {
        "company": "CellCore Technologies Inc.",
        "domain": "cellcoretechnologies.com",
        "trigger": "June 15, 2026 partnerships advancing a sovereign nitrocellulose production facility",
        "status": "qualified-like",
    },
    {
        "company": "De Havilland Aircraft of Canada Limited",
        "domain": "dehavilland.com",
        "trigger": "2026 De Havilland Field buildout for a 1,500-acre aircraft-manufacturing campus",
        "status": "qualified-like",
    },
    {
        "company": "Galaxia Mission Systems",
        "domain": "gx.space",
        "trigger": "February 25, 2026 federal support for Halifax satellite-manufacturing expansion",
        "status": "qualified-like-ongoing",
    },
    {
        "company": "Ideal Can Inc.",
        "domain": "idealcan.ca",
        "trigger": "2026 federal expansion support for an additional automated can-manufacturing line",
        "status": "qualified-like",
    },
    {
        "company": "Gastops Ltd.",
        "domain": "gastops.com",
        "trigger": "current PLM-to-Epicor BOM integration plus verified aerospace manufacturing operations",
        "status": "qualified-like",
    },
    {
        "company": "Calibur Tool & Mold Inc.",
        "domain": "caliburtoolandmold.com",
        "trigger": "2026 NRC support for ERP implementation in Windsor mold design and manufacturing",
        "status": "qualified-like",
    },
]

GAP_FILL_DOMAINS = [
    "qscire.com", "onekiwi.com.vn", "sielorobotics.com", "taigarobotics.com",
    "dawnrobotics.com", "synkar.com", "enersion.com", "mosaicmanufacturing.com",
    "vidirsolutions.com", "microgreen.ca", "novasher.tech", "tronmotors.ca",
    "cellcoretechnologies.com", "axibo.com", "enerquest.ca",
    "cimtechgreenenergy.com", "magellan.aero", "krakenrobotics.com",
    "canadagoose.com", "alstom.com", "newflyer.com", "greenpowermotor.com",
    "voltarielectric.com", "gx.space", "arnprioraerospace.com",
    "dehavilland.com", "coltcanada.com", "idealcan.ca", "gastops.com",
    "caliburtoolandmold.com",
]


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
        raw, reviewed, new_domains, rejected, duplicates = COVERAGE[keyword_id]
        report[keyword_id] = {
            "keyword": item.keyword,
            "lookback": "rolling 30 days, then 180 days, with 365-day ongoing-discovery fallback",
            "query_families": 10,
            "raw_results_inspected": raw,
            "unique_candidate_domains_reviewed": reviewed,
            "new_to_ledger_domains_reviewed": new_domains,
            "rejected_before_persistence": rejected,
            "qualified_published": 0,
            "watchlist_published": 0,
            "existing_records_upgraded_or_hidden": 0,
            "duplicates_skipped_or_reassessed": duplicates,
            "sources_checked": COMMON_SOURCES + ROTATED_SOURCES[keyword_id],
            "startup_gallery_outcome": "checked; directory-only or no relevant Canadian candidate",
            "x_outcome": "X-ray checked; direct X.com blocked by ERR_CERT_AUTHORITY_INVALID",
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
                    "canonical_domains_reviewed": len(GAP_FILL_DOMAINS),
                    "new_to_database_ledger_at_review": len(GAP_FILL_DOMAINS),
                    "domains": GAP_FILL_DOMAINS,
                    "sources": [
                        "provincial and federal funding pages",
                        "CanadaBuys award notices",
                        "company press and facility pages",
                        "trade publications",
                        "accelerator and association portfolios",
                    ],
                },
                "held_candidates": HELD_CANDIDATES,
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
                "blockers": [WORKBOOK_BLOCKER],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
