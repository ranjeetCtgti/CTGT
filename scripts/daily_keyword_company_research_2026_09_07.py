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
WORKBOOK_BLOCKER = (
    "Research completed, but publication was blocked: both permitted connected-"
    "session checks returned no already-open canonical Keyword_Companies.xlsx. "
    "The required workbook identity comparison and append/upsert sync could not run."
)


# Conservative named-company/domain counts from the September 7 in-app Browser
# pass and focused fallback after Google presented a reCAPTCHA. Counts are not
# padded when a source returned a small or noisy result pool.
COVERAGE = {
    1: (17, 12, 5, 10, ["Startup Gallery", "X.com", "BetaKit", "NGen", "SpaceQ", "AIAC", "Canada.ca", "ventureLAB"], "30 distinct named results inspected; NGen and AIAC searches returned zero named project/company pages."),
    2: (20, 14, 4, 16, ["Startup Gallery", "X.com", "BetaKit", "NGen", "Canada.ca", "ventureLAB", "Automate Canada", "Canadian Manufacturing"], "38 named results inspected; NorBot was rejected as an integrator/reseller and Scopia Surgical as software-led."),
    3: (12, 8, 4, 8, ["Startup Gallery", "X.com", "BetaKit", "NGen", "Canada.ca", "Naval News", "Ocean Supercluster", "Shipbuilding Association"], "Only five strong named pages appeared in the source-specific pool; the remainder were service suppliers or undated directories."),
    4: (18, 12, 6, 12, ["Startup Gallery", "X.com", "BetaKit", "NGen", "Canada.ca", "OVIN", "APMA", "Electric Autonomy"], "40 named results inspected; foreign-headquartered suppliers and general directories were rejected."),
    5: (20, 13, 7, 13, ["Startup Gallery", "X.com", "BetaKit", "NGen", "Canada.ca", "BDC", "PLANT", "French Quebec search"], "47 named results inspected; broad energy policy and service-only companies were rejected."),
    7: (18, 11, 7, 12, ["Startup Gallery", "X.com", "BetaKit", "NGen", "SpaceQ", "AIAC", "DAIR Aerospace", "Canada.ca"], "16 Browser results plus gap-fill sources; direct X was certificate-blocked and no safety warning was bypassed."),
    8: (22, 15, 7, 16, ["Startup Gallery", "X.com", "BetaKit", "NGen", "ventureLAB", "BDC", "Canada.ca", "Canadian Manufacturing"], "41 named results inspected; listicles, software startups and investor profiles remained discovery-only."),
    9: (20, 12, 8, 12, ["Startup Gallery", "X.com", "BetaKit", "NGen", "SpaceQ", "AIAC", "Aero Montreal", "Canada.ca"], "47 named results inspected; directories and undated member profiles did not qualify companies."),
    10: (18, 11, 7, 10, ["Startup Gallery", "X.com", "BetaKit", "NGen", "AIAC", "CANSEC", "Skies Magazine", "CanadaBuys"], "34 named results inspected; Bombardier remained excluded and directory-only suppliers were unpublished."),
    11: (22, 15, 7, 15, ["Startup Gallery", "X.com", "BetaKit", "NGen", "Canada.ca", "OVIN", "APMA", "Automotive News Canada"], "After the user resolved Google's CAPTCHA, 67 named results were inspected; no new Canadian-headquartered vehicle OEM cleared the gate."),
    12: (18, 13, 5, 12, ["Startup Gallery", "X.com", "BetaKit", "NGen", "Canada.ca/NRC", "PLANT", "manufacturer job pages", "French Quebec search"], "Searches mainly returned vendors, consultants, anonymous case studies or existing Gastops/Calibur evidence."),
    13: (23, 14, 9, 16, ["Startup Gallery", "X.com", "BetaKit", "NGen", "SpaceQ", "CanadaBuys", "OVIN", "company press pages"], "59 named results were inspected; Robotics Centre and Coulson Aviation cleared research gates but could not complete the workbook comparison."),
    14: (24, 14, 10, 17, ["Startup Gallery", "X.com", "BetaKit", "NGen", "SpaceQ", "AIAC", "Canada.ca", "CANSEC"], "67 named results were inspected; Dominion Dynamics and Volatus were existing identities, and marketplace qualification alone was not treated as a contract."),
    15: (24, 15, 9, 17, ["Startup Gallery", "X.com", "BetaKit", "NGen EVMP", "Canada.ca", "OVIN", "APMA", "French Quebec search"], "After the user resolved Google's second CAPTCHA, 68 named results were inspected across all eight source families; none produced a publishable Canadian-headquartered EV vehicle startup."),
    16: (15, 10, 5, 10, ["Startup Gallery", "X.com", "BetaKit", "NGen", "Canada.ca/NRC", "PLANT", "manufacturer hiring", "French Quebec search"], "Google returned 14 named results across the first six completed families, then raised a third CAPTCHA during the jobs query; direct-source fallback found only vendors, consultants, old articles and Bombardier's excluded Teamcenter hiring."),
}


GAP_FILL_DOMAINS = {
    "robotics-centre.com", "mesomat.com", "gilbert-tech.com", "arcanus.ca",
    "idealcan.ca", "gastops.com", "caliburtoolandmold.com",
    "newfrontierrobotics.com", "cyberworksrobotics.com", "coulsonaviation.com",
    "latecoere.aero", "canarm.com", "anchordanly.com", "automationdesign.ca",
    "motrec.com", "avss.co", "openoceanrobotics.com", "nanotess.com",
    "rutter.ca", "tacteris.com", "kardium.com", "longboardproducts.com",
    "zaber.com", "unilia.com", "nikoapparel.com", "fellfab.com", "altex.ca",
    "prairiehvacr.com", "sekisui-cms.com", "primepowdersinc.com",
}


def acquire_lock() -> int | None:
    LOCK_PATH.parent.mkdir(parents=True, exist_ok=True)
    try:
        fd = os.open(LOCK_PATH, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError:
        return None
    os.write(fd, json.dumps({"pid": os.getpid(), "started_at": RUN_AT.isoformat()}).encode())
    os.fsync(fd)
    return fd


def main() -> None:
    lock_fd = acquire_lock()
    if lock_fd is None:
        print(json.dumps({"status": "skipped", "reason": "active automation run lock"}))
        return

    try:
        load_dotenv(REPO_ROOT / ".env")
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
                keyword_id, result_count=0, error=WORKBOOK_BLOCKER
            ) is None:
                raise RuntimeError(f"Could not record keyword search {keyword_id}")

        after = {row.id: row for row in database.list_keywords()}
        report = {}
        for keyword_id, values in COVERAGE.items():
            reviewed, rejected, duplicates, new_domains, sources, note = values
            if after[keyword_id].search_count != before[keyword_id].search_count + 1:
                raise RuntimeError(f"Keyword {keyword_id} did not advance exactly once")
            report[keyword_id] = {
                "keyword": before[keyword_id].keyword,
                "lookback": "rolling 30 days, then 180 days, with 365-day ongoing-discovery fallback",
                "query_families": 8,
                "candidate_domains_reviewed": reviewed,
                "new_to_ledger_domains_reviewed": new_domains,
                "rejected_before_persistence": rejected,
                "qualified_published": 0,
                "watchlist_published": 0,
                "existing_records_upgraded_or_hidden": 0,
                "duplicates_skipped_or_reassessed": duplicates,
                "sources_checked": sources,
                "blockers_or_zero_results": note,
                "search_count_before": before[keyword_id].search_count,
                "search_count_after": after[keyword_id].search_count,
            }

        print(json.dumps({
            "status": "completed_with_publication_blocker",
            "run_at": RUN_AT.isoformat(),
            "coverage": report,
            "gap_fill": {
                "domains_reviewed": len(GAP_FILL_DOMAINS),
                "new_to_database_ledger": len(gap_fill_new),
                "new_domains": gap_fill_new,
                "inaccessible_or_timeout": [
                    "gilbert-tech.com", "idealcan.ca", "gastops.com",
                    "caliburtoolandmold.com", "newfrontierrobotics.com",
                    "cyberworksrobotics.com", "canarm.com", "anchordanly.com",
                    "automationdesign.ca", "openoceanrobotics.com", "zaber.com",
                    "nikoapparel.com", "fellfab.com", "altex.ca",
                    "primepowdersinc.com",
                ],
            },
            "held_high_confidence": [
                {
                    "company": "Robotics Centre Inc.",
                    "domain": "robotics-centre.com",
                    "status_without_workbook_blocker": "qualified",
                    "scores": {"opportunity": 92, "manufacturing": 97, "trigger": 94, "solution_fit": 95, "evidence": 92},
                    "trigger": "C$5M BDC financing and a new 365 March Road, Kanata manufacturing facility announced 2026-09-03 for Shuriken, Kukri and Longbow uncrewed systems.",
                    "products": ["Teamcenter", "NX", "Simcenter", "Opcenter", "Tecnomatix", "Polarion"],
                },
                {
                    "company": "Coulson Aviation Canada",
                    "domain": "coulsonaviation.com",
                    "status_without_workbook_blocker": "qualified",
                    "scores": {"opportunity": 94, "manufacturing": 99, "trigger": 98, "solution_fit": 96, "evidence": 98},
                    "trigger": "Conditional acquisition of ten former RCAF CC-130H aircraft announced 2026-08-07; government says each conversion needs about 20,000 labour hours at Port Alberni.",
                    "products": ["Teamcenter", "NX", "Simcenter", "Opcenter", "Tecnomatix", "Polarion"],
                },
                {
                    "company": "MesoMat",
                    "domain": "mesomat.com",
                    "status_without_workbook_blocker": "qualified",
                    "scores": {"opportunity": 87, "manufacturing": 91, "trigger": 88, "solution_fit": 91, "evidence": 92},
                    "trigger": "OVIN announced a C$2.2M intelligent-tire R&D project on 2026-08-27, including nearly C$700k public and C$1.5M industry funding.",
                    "products": ["Teamcenter", "Simcenter", "Polarion", "Capital"],
                },
                {
                    "company": "Arcanus Aerial Systems",
                    "domain": "arcanus.ca",
                    "status_without_workbook_blocker": "qualified",
                    "scores": {"opportunity": 91, "manufacturing": 97, "trigger": 92, "solution_fit": 95, "evidence": 91},
                    "trigger": "Five-year Canadian production agreement with FeralX dated 2026-05-12 covers manufacture, assembly, testing and delivery of UAS components and platforms.",
                    "products": ["Teamcenter", "NX", "Simcenter", "Opcenter", "Tecnomatix", "Polarion"],
                },
            ],
            "existing_refreshes_held": [
                "Dominion Dynamics C$139M Series A and 25,000-square-foot Kanata manufacturing facility",
                "Volatus Aerospace Defence Drone Initiative qualification (not a contract)",
            ],
            "database_writes": {"companies": 0, "signals": 0, "keyword_company_results": 0, "keyword_search_audits": len(COVERAGE)},
            "workbook": {
                "canonical": {"inserted": 0, "updated": 0, "unchanged_last_verified": 135, "failed": 1, "removed": 0},
                "local_staging": {"inserted": 0, "updated": 0, "unchanged_last_verified": 128, "failed_or_deferred": 13, "removed": 0},
            },
            "blockers": [
                WORKBOOK_BLOCKER,
                "X.com was certificate-blocked; no warning was bypassed.",
                "The user resolved Google reCAPTCHAs after keywords 10 and 14, allowing research to resume. A third challenge appeared during keyword 16; it was not solved or bypassed, and the remaining gap was covered with direct-source fallback.",
            ],
        }, indent=2, default=str))
    finally:
        os.close(lock_fd)
        try:
            LOCK_PATH.unlink()
        except FileNotFoundError:
            pass


if __name__ == "__main__":
    main()
