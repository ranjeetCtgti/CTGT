from __future__ import annotations

import json
import os
from datetime import datetime, timezone

from dotenv import load_dotenv

from db.database import Database


RUN_AT = datetime.now(timezone.utc)
WORKBOOK_BLOCKER = (
    "Research completed, but publication was blocked: no connected Excel document "
    "session was registered for the already-open canonical workbook, so the required "
    "pre-persistence workbook identity comparison and append/upsert sync could not run."
)


# Conservative result-level counts from the browser research ledger. They count
# named Canadian company candidates, not noisy raw search-result URLs.
COVERAGE = {
    1: (11, 7, 4, 5, "No August-formed aerospace startup had verifiable formation-date plus operating evidence."),
    2: (16, 9, 5, 7, "TetraGen was an existing duplicate; Cyberworks was software-led; New Frontier lacked a committed trigger."),
    3: (12, 7, 4, 6, "Davie's icebreaker contract was an existing qualified-company event and duplicate of the stored program."),
    4: (13, 8, 4, 5, "Hanon was an established foreign-headquartered supplier, not a Canadian automotive startup."),
    5: (18, 9, 8, 7, "Irving Oil, Sediver and other operating leads were held for workbook identity comparison."),
    7: (15, 9, 5, 6, "SpaceQ and AIAC were checked; new programs were calls or supply arrangements, not committed company work."),
    8: (20, 10, 9, 7, "Ideal Can passed source and product-fit checks but was held before persistence."),
    9: (15, 9, 5, 7, "Coulson and supplier-directory leads lacked a new publishable event after deduplication."),
    10: (18, 10, 7, 7, "AIAC and trade directories were discovery-only; Latecoere evidence was hiring-led and foreign-owned."),
    11: (13, 8, 4, 6, "GM's Oshawa program was already published on the previous run; no distinct OEM event cleared the gate."),
    12: (16, 8, 8, 5, "Gastops and Calibur Tool & Mold passed identity and ERP/PLM evidence checks but were held."),
    13: (17, 10, 6, 7, "DDI supply arrangements were not committed contracts; Volatus and Davie Autonomous were existing."),
    14: (19, 11, 8, 7, "Defence supplier pools and exhibitor listings were discovery-only without committed work."),
    15: (14, 9, 5, 5, "No new Canadian EV startup had both a dated trigger and verified physical-product operations."),
    16: (15, 8, 7, 5, "Canada Goose, Bombardier and Pratt & Whitney exposed PLM implementation signals, but no row could be identity-compared to the workbook."),
}


# Second-pass domains reviewed after the zero-publishable first pass. The audit
# reports how many were absent from the database ledger at run time.
GAP_FILL_DOMAINS = {
    "idealcan.ca",
    "gastops.com",
    "caliburtoolandmold.com",
    "gilbert-tech.com",
    "kardium.com",
    "longboardproducts.com",
    "gmiwheels.com",
    "zaber.com",
    "unilia.com",
    "nikoapparel.com",
    "fellfab.com",
    "atlasengineeredproducts.com",
    "altex.ca",
    "prairiehvacr.com",
    "sekisui-cms.com",
    "primepowdersinc.com",
    "uplandtechnologies.com",
    "velocitybolting.com",
    "cecmining.com",
    "plasconplastics.com",
    "hemlock.com",
    "connorindustries.com",
    "sediver.com",
    "newfrontierrobotics.com",
    "cyberworksrobotics.com",
    "coulsonaviation.com",
    "latecoere.aero",
    "canarm.com",
    "anchordanly.com",
    "automationdesign.ca",
    "motrec.com",
    "avss.co",
    "openoceanrobotics.com",
    "nanotess.com",
    "rutter.ca",
    "tacteris.com",
}


def main() -> None:
    load_dotenv(".env")
    database = Database(os.environ["DATABASE_URL"])
    database.initialize()

    before = {row.id: row for row in database.list_keywords()}
    if set(before) != set(COVERAGE):
        raise RuntimeError(f"Persistent keyword set changed: {sorted(before)}")

    known_domains = {
        (lead.company_domain or "").strip().lower()
        for lead in database.get_leads(limit=5000)
        if lead.company_domain
    }
    gap_fill_new = sorted(GAP_FILL_DOMAINS - known_domains)

    for keyword_id in sorted(COVERAGE):
        if database.record_keyword_search(
            keyword_id,
            result_count=0,
            error=WORKBOOK_BLOCKER,
        ) is None:
            raise RuntimeError(f"Could not record keyword search {keyword_id}")

    after = {row.id: row for row in database.list_keywords()}
    report = {}
    for keyword_id, (reviewed, rejected, new_domains, duplicates, note) in COVERAGE.items():
        if after[keyword_id].search_count != before[keyword_id].search_count + 1:
            raise RuntimeError(f"Keyword {keyword_id} did not advance exactly once")
        report[keyword_id] = {
            "keyword": before[keyword_id].keyword,
            "search_count_before": before[keyword_id].search_count,
            "search_count_after": after[keyword_id].search_count,
            "lookback": "rolling 30 days; 180-day evidence and 365-day ongoing discovery fallbacks",
            "query_families": 8,
            "candidate_domains_reviewed": reviewed,
            "new_to_ledger_domains_reviewed": new_domains,
            "rejected_before_persistence": rejected,
            "duplicates_skipped_or_reassessed": duplicates,
            "qualified_published": 0,
            "watchlist_published": 0,
            "note": note,
        }

    print(
        json.dumps(
            {
                "run_at": RUN_AT.isoformat(),
                "coverage": report,
                "gap_fill_domains_reviewed": len(GAP_FILL_DOMAINS),
                "gap_fill_new_to_database": len(gap_fill_new),
                "gap_fill_new_domains": gap_fill_new,
                "held_high_confidence": [
                    "idealcan.ca",
                    "gastops.com",
                    "caliburtoolandmold.com",
                ],
                "database_writes": {
                    "new_companies": 0,
                    "new_signals": 0,
                    "new_keyword_company_results": 0,
                    "keyword_search_audits": len(COVERAGE),
                },
                "blockers": [
                    WORKBOOK_BLOCKER,
                    "Direct X.com searches failed certificate validation for all 15 keywords; no warning was bypassed.",
                    "Search-engine human-verification interstitials were not solved or bypassed; accessible sources were used instead.",
                ],
            },
            indent=2,
            default=str,
        )
    )


if __name__ == "__main__":
    main()
