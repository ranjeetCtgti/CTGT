from __future__ import annotations

import json
from datetime import datetime, timezone

from dotenv import load_dotenv

from db.database import Database


RUN_AT = datetime.now(timezone.utc)


COVERAGE = {
    1: (5, 2, 2, ["Startup Gallery", "X.com public/X-ray", "BetaKit", "NGen", "SpaceQ", "AIAC", "ventureLAB HCI", "CanadaBuys"], "Startup Gallery returned foreign or unrelated companies; Horizon Aircraft and Sentinel R&D were existing identities. NGen had zero named 30-day results."),
    2: (5, 3, 2, ["Startup Gallery", "X.com public/X-ray", "BetaKit", "NGen", "ventureLAB HCI", "MaRS", "Communitech", "CanadaBuys"], "Upside Robotics was profile-only and Veeda AI was software-led; NGen had zero named 30-day results."),
    3: (5, 2, 3, ["Startup Gallery", "X.com public/X-ray", "BetaKit", "NGen", "Ocean Supercluster", "Shipbuilding Association of Canada", "Marine Log", "Naval News"], "Startup Gallery and BetaKit returned zero relevant candidates. Marine results were foreign or existing Canadian shipyard identities."),
    4: (4, 3, 1, ["Startup Gallery", "X.com public/X-ray", "BetaKit", "NGen EVMP", "APMA", "OVIN", "Electric Autonomy Canada", "BDC"], "Directory/social results were foreign or software-led. Hanon Systems remained an established foreign-owned supplier, not a Canadian automotive startup."),
    5: (6, 3, 2, ["Startup Gallery", "X.com public/X-ray", "BetaKit", "NGen", "Canada.ca", "BDC Climate Tech", "PLANT", "Emissions Reduction Alberta"], "Power Wood's C$84M announcement remained unpublished because current financing was not independently corroborated beyond its release and identity spans a new parent and operating subsidiary. NGen had zero named 30-day results."),
    7: (7, 2, 5, ["Startup Gallery", "X.com public/X-ray", "BetaKit", "NGen", "SpaceQ", "AIAC Member Directory", "Aero Montreal", "Canadian Space Agency"], "SpaceQ's current named manufacturers were existing identities; Startup Gallery, BetaKit and NGen had zero relevant 30-day results."),
    8: (8, 3, 5, ["Startup Gallery", "X.com public/X-ray", "BetaKit", "NGen", "BDC Capital", "MaRS", "Communitech", "PacifiCan"], "Blueprint was an electronics-design software lead. COTA Aviation, Mahler Machining and Calogy were existing qualified identities with duplicate evidence URLs; Power Wood did not clear the identity/evidence gate."),
    9: (6, 2, 4, ["Startup Gallery", "X.com public/X-ray", "BetaKit", "NGen", "SpaceQ", "AIAC Industry Guide", "DAIR Aerospace", "Aero Montreal"], "COTA Aviation and Mahler Machining were existing qualified records. AIAC and Aero Montreal entries were discovery-only; DAIR yielded no named current trigger."),
    10: (6, 2, 4, ["Startup Gallery", "X.com public/X-ray", "BetaKit", "NGen", "SpaceQ", "AIAC Member Directory", "PacifiCan", "Canadian Metalworking"], "COTA Aviation and Mahler Machining were existing qualified records with the August 10 PacifiCan URL already stored. Directory-only suppliers were not republished."),
    11: (5, 4, 1, ["Startup Gallery", "X.com public/X-ray", "BetaKit", "NGen", "APMA", "OVIN", "Electric Autonomy Canada", "Canadian Manufacturing"], "GM and Honda are established OEMs, not startups; Hanon Systems is a foreign-owned component supplier rather than a Canadian vehicle OEM. No new OEM passed the gate."),
    12: (5, 3, 2, ["Startup Gallery", "X.com public/X-ray", "BetaKit", "NGen AI4M", "CME", "PLANT", "manufacturer hiring pages", "CanadaBuys"], "Google presented an automated-traffic checkpoint during this keyword; the barrier was not bypassed and direct/source-search fallback was used. Software vendors, consultants and undated integration profiles were rejected."),
    13: (7, 2, 5, ["Startup Gallery", "X.com public/X-ray", "BetaKit", "NGen", "SpaceQ", "AIAC", "CanadaBuys", "Defence Drone Initiative"], "Google remained blocked, so source-specific fallback covered the 180-day window. Calogy's C$1.2M Jaunt contract and other named autonomous-system makers were existing qualified records."),
    14: (7, 2, 5, ["Startup Gallery", "X.com public/X-ray", "BetaKit", "NGen", "SpaceQ", "AIAC", "CADSI", "CanadaBuys"], "Google remained blocked, so source-specific fallback covered the 180-day window. COTA, Mahler, Dominion and GIT were existing identities; directories and general defence programs did not independently qualify a new company."),
    15: (6, 2, 4, ["Startup Gallery", "X.com public/X-ray", "BetaKit", "NGen EVMP", "APMA Project Arrow", "OVIN", "Electric Autonomy Canada", "Canada.ca"], "Google remained blocked, so source-specific fallback covered the 180-day window. Calogy was reassessed from existing evidence; other EV results were program pages, established suppliers or foreign companies."),
}


def main() -> None:
    load_dotenv(".env")
    database = Database()
    database.initialize()

    before = {item.id: item for item in database.list_keywords()}
    if set(before) != set(COVERAGE):
        raise RuntimeError(f"Persistent keyword set changed: {sorted(before)}")

    for keyword_id in sorted(before):
        if database.record_keyword_search(keyword_id, result_count=0) is None:
            raise RuntimeError(f"Could not record keyword {keyword_id}")

    after = {item.id: item for item in database.list_keywords()}
    report = {}
    for keyword_id, (reviewed, rejected, duplicates, sources, notes) in COVERAGE.items():
        if after[keyword_id].search_count != before[keyword_id].search_count + 1:
            raise RuntimeError(f"Keyword {keyword_id} did not advance exactly once")
        report[keyword_id] = {
            "keyword": before[keyword_id].keyword,
            "lookback": "rolling 30 days, then 180-day fallback",
            "candidates_reviewed": reviewed,
            "rejected_before_persistence": rejected,
            "qualified_published": 0,
            "watchlist_published": 0,
            "existing_records_upgraded_or_hidden": 0,
            "duplicates_skipped_or_reassessed": duplicates,
            "sources_checked": sources,
            "blockers_or_zero_results": notes,
            "search_count_before": before[keyword_id].search_count,
            "search_count_after": after[keyword_id].search_count,
            "last_result_count": after[keyword_id].last_result_count,
            "last_error": after[keyword_id].last_error,
        }

    keyword_rows = database.list_keyword_companies(limit=5000)
    eligible_ids = {
        row.company_id
        for row in keyword_rows
        if row.qualification_status in {"qualified", "watchlist"}
    }
    processed_urls = database.get_processed_source_urls()
    duplicate_urls = {
        "cota": "https://www.canada.ca/en/pacific-economic-development/news/2026/08/government-of-canada-invests-over-30-million-to-help-bc-businesses-navigate-trade-disruptions-and-seize-new-opportunities.html" in processed_urls,
        "mahler": "https://www.canada.ca/en/pacific-economic-development/news/2026/08/government-of-canada-invests-over-30-million-to-help-bc-businesses-navigate-trade-disruptions-and-seize-new-opportunities.html" in processed_urls,
        "calogy": "https://betakit.com/calogy-secures-1-2-million-contract-to-power-jaunts-autonomous-drones/" in processed_urls,
    }
    if not all(duplicate_urls.values()):
        raise RuntimeError(f"Expected existing evidence URL was missing: {duplicate_urls}")

    print(json.dumps({
        "run_at": RUN_AT.isoformat(),
        "eligible_company_count": len(eligible_ids),
        "duplicate_evidence_confirmed": duplicate_urls,
        "published_company_ids": [],
        "per_keyword": report,
    }, indent=2, default=str))


if __name__ == "__main__":
    main()
