from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv

from db.database import Database


RUN_AT = datetime.now(timezone.utc)
LOCK_PATH = Path(
    r"C:\Users\ranjeet.chaudhary\.codex\automations\daily-keyword-company-research\run.lock"
)


COVERAGE = {
    1: (11, 7, 4, 0, ["Startup Gallery Aerospace and Canada pages", "X.com direct search (certificate blocked)", "Google public X-ray search", "BetaKit aerospace startup search", "NGen aerospace 30-day and 180-day searches", "SpaceQ latest news/search", "AIAC 2026 guide and site search", "ventureLAB search (Google CAPTCHA blocked)"], "Startup Gallery and public-X results were foreign, undated, or directory/social leads. SpaceQ's August 21 FAST grants went to universities rather than companies; AIAC yielded guide/member discovery only."),
    2: (13, 7, 6, 0, ["Startup Gallery Robotics and Canada pages", "X.com direct search (certificate blocked)", "Google public X-ray search", "BetaKit robotics manufacturing search", "NGen robotics 30-day and 180-day searches", "MaRS robotics/hardware jobs", "ventureLAB and Communitech searches"], "Haply, Promise, TetraGen and A&K were existing identities or replay evidence. M2M Tech was software/digital-twin services, and directory-only robotics leads were rejected."),
    3: (9, 7, 2, 1, ["Startup Gallery Transportation and Canada pages", "X.com direct search (certificate blocked)", "Google public X-ray search", "BetaKit shipbuilding search", "NGen marine searches", "Canada's Ocean Supercluster portfolio", "Marine Log and Naval News searches", "Canada.ca/PacifiCan manufacturing awards"], "Jastram is a marine steering supplier rather than a shipbuilder, and Oneka is a desalination-hardware company rather than a shipyard. No new shipbuilder cleared the exact-keyword gate."),
    4: (9, 7, 2, 0, ["Startup Gallery Transportation and Canada pages", "X.com direct search (certificate blocked)", "Google public X-ray search", "BetaKit automotive startup search", "NGen automotive searches", "OVIN", "APMA Project Arrow"], "Project Arrow is a non-commercial demonstrator; Hanon and parts makers are not Canadian automotive startups. No new OEM/startup passed."),
    5: (14, 10, 4, 4, ["Startup Gallery Energy and Canada pages", "X.com direct search (certificate blocked)", "Google public X-ray search", "BetaKit energy hardware search", "NGen energy searches", "Canada.ca/PacifiCan August funding backgrounder", "BDC", "PLANT"], "OSENSA, Accelovant, GMI Wheels and PowerWood were assessed. Scope, parent/subsidiary identity, or workbook-comparison gates remained incomplete, so none was published."),
    7: (8, 5, 3, 0, ["Startup Gallery Aerospace and Canada pages", "X.com direct search (certificate blocked)", "Google public X-ray search", "BetaKit drone/UAV/eVTOL search", "NGen drone searches", "SpaceQ latest news/search", "AIAC drone search and 2026 guide", "Aero Montreal"], "X-ray results were foreign or social-only. SpaceQ's current items did not identify a new Canadian aircraft/UAV startup with a qualifying production trigger."),
    8: (14, 8, 6, 3, ["Startup Gallery Hardware and Canada pages", "X.com direct search (certificate blocked)", "Google public X-ray search", "BetaKit funded-hardware search", "NGen hardware searches", "MaRS and Communitech", "BDC", "Canada.ca/PacifiCan funding awards"], "OSENSA and Accelovant have verified physical products and government-backed expansion signals, while Scandium/Scalium has a July acquisition. New-company persistence was withheld because the mandatory workbook identity comparison could not run; the acquisition also did not meet the exact recently-raised-funding wording."),
    9: (15, 7, 8, 1, ["Startup Gallery Aerospace and Canada pages", "X.com direct search (certificate blocked)", "Google public X-ray search", "BetaKit aerospace manufacturing search", "NGen aerospace searches", "SpaceQ latest news/search", "AIAC manufacturing search and 2026 guide", "Aero Montreal and DAIR searches"], "MDA, North Vector, NordSpace, Calogy and COTA were existing or duplicate identities. Scandium/Scalium's aircraft-material ambition remains pre-commercial and did not clear the operating-aerospace-company gate."),
    10: (12, 6, 6, 0, ["Startup Gallery Aerospace and Canada pages", "X.com direct search (certificate blocked)", "Google public X-ray search", "BetaKit aerospace supplier search", "NGen supplier searches", "AIAC supplier search and 2026 guide", "CanadaBuys", "Canada.ca/PacifiCan"], "COTA and Magellan were existing identities or older contract evidence; AIAC results were directory/guide entries. No new supplier trigger passed."),
    11: (10, 7, 3, 0, ["Startup Gallery Transportation and Canada pages", "X.com direct search (certificate blocked)", "Google public X-ray search", "BetaKit automotive OEM search", "NGen vehicle searches", "APMA", "OVIN", "Canadian Manufacturing"], "Hanon is a foreign-headquartered parts supplier, Roshel was already present, and Project Arrow is not a commercial OEM. No new Canadian vehicle manufacturer passed."),
    12: (6, 5, 1, 0, ["Startup Gallery Hardware and Canada pages", "X.com direct search (certificate blocked)", "Google public X-ray search", "BetaKit ERP/PLM search", "NGen digital-transformation searches", "PLANT and Canadian Manufacturing", "Oakville Chamber of Commerce search"], "BetaKit produced an irrelevant language-model result; NGen and PLANT produced generic transformation material rather than a named manufacturer implementing ERP/PLM."),
    13: (13, 7, 6, 1, ["Startup Gallery Robotics/Transportation and Canada pages", "X.com direct search (certificate blocked)", "Google public X-ray search", "BetaKit autonomous vehicle/drone search", "NGen autonomous searches", "SpaceQ latest news/search", "AIAC autonomous-drone search", "CanadaBuys and Defence Drone Initiative"], "Pelagos Frontier appeared only in social/directory discovery and lacked independent dated funding corroboration. Calogy, Dominion, Sentinel and other credible identities were existing or already assessed."),
    14: (16, 10, 6, 2, ["Startup Gallery Aerospace and Canada pages", "X.com direct search (certificate blocked)", "Google public X-ray search", "BetaKit defence-hardware search", "NGen defence searches", "SpaceQ latest news/search", "AIAC defence search", "CADSI OEM/capabilities pages", "CanadaBuys", "Canada.ca/PacifiCan"], "Jastram and INKAS were new-domain leads, but the unavailable workbook comparison blocked new identity persistence. CADSI membership and directories were discovery-only; North Vector, Dominion and COTA were existing identities."),
    15: (11, 9, 2, 1, ["Startup Gallery Transportation and Canada pages", "X.com direct search (certificate blocked)", "Google public X-ray search", "BetaKit electric-vehicle startup search", "NGen zero-emission-vehicle searches", "APMA Project Arrow", "OVIN", "Electric Autonomy supplier directory", "Canada.ca/PacifiCan"], "Grin Technologies is an established light-EV component maker rather than a startup; Hanon is a foreign-headquartered supplier. Electric Autonomy results were directory-only, so no Canadian EV startup passed."),
}


def acquire_lock() -> int | None:
    LOCK_PATH.parent.mkdir(parents=True, exist_ok=True)
    try:
        fd = os.open(LOCK_PATH, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError:
        print(json.dumps({"status": "skipped", "reason": "active run marker exists"}))
        return None
    os.write(fd, json.dumps({"pid": os.getpid(), "started_at": RUN_AT.isoformat()}).encode("utf-8"))
    return fd


def main() -> None:
    lock_fd = acquire_lock()
    if lock_fd is None:
        return
    try:
        load_dotenv(".env")
        database = Database()
        database.initialize()
        before = {row.id: row for row in database.list_keywords()}
        if set(before) != set(COVERAGE):
            raise RuntimeError(f"Persistent keyword set changed: {sorted(before)}")

        for keyword_id in sorted(before):
            if database.record_keyword_search(keyword_id, result_count=0) is None:
                raise RuntimeError(f"Could not record keyword {keyword_id}")

        after = {row.id: row for row in database.list_keywords()}
        report = {}
        for keyword_id, (reviewed, rejected, duplicates, new_domains, sources, notes) in COVERAGE.items():
            if after[keyword_id].search_count != before[keyword_id].search_count + 1:
                raise RuntimeError(f"Keyword {keyword_id} did not advance exactly once")
            report[keyword_id] = {
                "keyword": before[keyword_id].keyword,
                "lookback": "rolling 30 days, then 180-day fallback; older evidence only where ongoing",
                "candidates_reviewed": reviewed,
                "new_domains_reviewed": new_domains,
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

        rows = database.list_keyword_companies(limit=5000)
        eligible_ids = {
            row.company_id
            for row in rows
            if row.qualification_status in {"qualified", "watchlist"}
        }
        print(json.dumps({
            "status": "completed",
            "run_at": RUN_AT.isoformat(),
            "signals_persisted": 0,
            "keyword_links_published": 0,
            "eligible_company_count": len(eligible_ids),
            "per_keyword": report,
            "research_blockers": [
                "Direct X.com was inaccessible for every keyword with ERR_CERT_AUTHORITY_INVALID; no warning was bypassed.",
                "Google presented an automated-traffic CAPTCHA during rotated-source coverage; it was not solved or bypassed, and direct-source/read-only lookup continued.",
                "No exact connected Keyword_Companies.xlsx Excel session was registered, so new-company persistence was withheld where workbook identity comparison was required.",
            ],
        }, indent=2, default=str))
    finally:
        os.close(lock_fd)
        LOCK_PATH.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
