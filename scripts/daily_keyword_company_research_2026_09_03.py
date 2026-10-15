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
    "Research completed, but publication was blocked: no connected Excel document "
    "session was registered for the already-open canonical Keyword_Companies.xlsx, "
    "so the required workbook identity comparison and append/upsert sync could not run."
)


# Counts are conservative named-company/domain counts from the 2026-09-03
# in-app Browser and focused-source research ledger. Narrow result pools are
# reported as observed and are never padded to the fifteen-domain target.
COVERAGE = {
    1: (10, 6, 4, 4, ["Startup Gallery", "X.com direct", "BetaKit", "NGen", "SpaceQ", "AIAC 2026 Guide", "ventureLAB HCI", "Canada.ca/CSA"], "Startup Gallery yielded no relevant candidate; X.com was certificate-blocked. SpaceQ's recent CUBICS item funded universities, not companies."),
    2: (18, 10, 8, 6, ["Startup Gallery", "X.com direct", "BetaKit", "NGen", "ventureLAB HCI", "Automate Canada", "Canada.ca", "company press/hiring"], "TetraGen, A&K, Avidbots and KONNEXIO were existing identities or replay evidence. Software-led and directory-only robotics leads were rejected."),
    3: (13, 7, 6, 4, ["Startup Gallery", "X.com direct", "BetaKit", "NGen", "Canada.ca shipbuilding", "Ocean Supercluster", "Marine Log/Naval News", "Shipbuilding Association"], "Davie's new C$11.3B six-icebreaker contract passed the evidence gate but was held for the workbook comparison; non-shipyard marine suppliers were rejected."),
    4: (14, 8, 6, 5, ["Startup Gallery", "X.com direct", "BetaKit", "NGen EVMP", "OVIN", "APMA", "Electric Autonomy", "official company sites"], "MesoMat's C$2.2M intelligent-tire R&D project passed identity and physical-product checks but was held. Hanon is a foreign-headquartered supplier, not a Canadian startup/OEM."),
    5: (16, 9, 7, 6, ["Startup Gallery", "X.com direct", "BetaKit", "NGen", "Canada.ca/CED", "BDC", "PLANT", "company facility pages"], "Gilbert Products' C$3M automated-capacity project passed manufacturing and trigger checks but was held. Existing energy-company results were reassessed or deduplicated."),
    7: (15, 8, 7, 6, ["Startup Gallery", "X.com direct", "BetaKit", "NGen", "SpaceQ", "AIAC", "DAIR Aerospace", "Aero Montreal"], "Arcanus' five-year Canadian UAS production agreement passed discovery and source checks but was held; supply-arrangement-only drone results were not treated as contracts."),
    8: (19, 10, 9, 8, ["Startup Gallery", "X.com direct", "BetaKit", "NGen", "ventureLAB HCI", "MaRS/Communitech", "BDC", "Canada.ca/CED"], "Ideal Can, Gilbert Products and MesoMat had credible physical-product triggers but could not complete the workbook comparison. Portfolio-only and tracker-only leads were rejected."),
    9: (14, 8, 6, 5, ["Startup Gallery", "X.com direct", "BetaKit", "NGen", "SpaceQ", "AIAC", "Aero Montreal", "DAIR Aerospace"], "MDA, Telesat, Maritime Launch and NordSpace were existing identities; directory profiles did not independently qualify new rows."),
    10: (14, 9, 5, 5, ["Startup Gallery", "X.com direct", "BetaKit", "NGen", "AIAC members", "CADSI/CANSEC", "Canadian Metalworking", "CanadaBuys"], "AIAC and CADSI profiles were discovery-only. No new Tier 1/Tier 2 supplier had both a current committed trigger and a completed workbook identity comparison."),
    11: (13, 8, 5, 4, ["Startup Gallery", "X.com direct", "BetaKit", "NGen EVMP", "APMA", "OVIN", "Electric Autonomy", "OEM press pages"], "The result pool mainly rediscovered GM and established OEMs. Component suppliers and suspended investment programs did not fit the keyword gate."),
    12: (17, 9, 8, 7, ["Startup Gallery", "X.com direct", "BetaKit", "NGen", "NRC IRAP grants", "PLANT", "Canadian Manufacturing", "vendor customer stories"], "Gastops' live PLM-to-Epicor BOM migration and Calibur Tool & Mold's C$75,000 ERP project passed evidence checks but were held before persistence."),
    13: (17, 10, 7, 6, ["Startup Gallery", "X.com direct", "BetaKit", "NGen", "OVIN", "CanadaBuys DDI", "SpaceQ", "company press pages"], "Arcanus and MesoMat were credible hardware leads but publication was blocked. DDI supply arrangements were not counted as production contracts."),
    14: (19, 10, 9, 8, ["Startup Gallery", "X.com direct", "BetaKit", "NGen", "CanadaBuys DDI", "SpaceQ", "AIAC", "CADSI/CANSEC"], "Arcanus and FeralX had a dated production agreement; Telesat and MDA had major existing-record contract refreshes. All were held because the workbook gate could not run."),
    15: (14, 9, 5, 5, ["Startup Gallery", "X.com direct", "BetaKit", "NGen EVMP", "OVIN", "APMA", "Electric Autonomy", "French Quebec searches"], "No new Canadian EV vehicle startup cleared the exact-fit gate. MesoMat is an automotive sensing supplier rather than a vehicle manufacturer."),
    16: (16, 9, 7, 7, ["Startup Gallery", "X.com direct", "BetaKit", "NGen", "NRC IRAP grants", "PLANT", "manufacturer hiring", "vendor customer stories"], "Gastops, Calibur and existing Multimatic exposed concrete PLM/ERP implementation signals, but the required current workbook comparison was unavailable. Bombardier remains excluded per user direction."),
}


# Zero-publishable gap fill: provincial/federal funding, press wires, hiring,
# trade associations, accelerators, official sites and French-language sources.
GAP_FILL_DOMAINS = {
    "mesomat.com", "gilbert-tech.com", "arcanus.ca", "feralx.ca", "idealcan.ca",
    "gastops.com", "caliburtoolandmold.com", "newfrontierrobotics.com",
    "cyberworksrobotics.com", "coulsonaviation.com", "latecoere.aero", "canarm.com",
    "anchordanly.com", "automationdesign.ca", "motrec.com", "avss.co",
    "openoceanrobotics.com", "nanotess.com", "rutter.ca", "tacteris.com",
    "kardium.com", "longboardproducts.com", "zaber.com", "unilia.com",
    "nikoapparel.com", "fellfab.com", "atlasengineeredproducts.com", "altex.ca",
    "prairiehvacr.com", "sekisui-cms.com", "primepowdersinc.com",
    "uplandtechnologies.com", "velocitybolting.com", "cecmining.com",
    "plasconplastics.com", "hemlock.com", "connorindustries.com", "sediver.com",
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
        for keyword_id, values in COVERAGE.items():
            reviewed, rejected, duplicates, new_domains, sources, note = values
            if after[keyword_id].search_count != before[keyword_id].search_count + 1:
                raise RuntimeError(f"Keyword {keyword_id} did not advance exactly once")
            report[keyword_id] = {
                "keyword": before[keyword_id].keyword,
                "lookback": "rolling 30 days; 180-day evidence and 365-day ongoing discovery fallbacks",
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
                "source_families": [
                    "provincial/federal funding portals", "CanadaBuys awards",
                    "Newswire/press releases", "manufacturer job postings",
                    "trade and exhibitor directories", "accelerator/cohort pages",
                    "French-language Quebec searches", "official company sites",
                ],
            },
            "held_high_confidence": [
                "mesomat.com", "gilbert-tech.com", "arcanus.ca", "feralx.ca",
                "idealcan.ca", "gastops.com", "caliburtoolandmold.com",
                "davie.ca", "telesat.com", "mda.space", "multimatic.com",
            ],
            "database_writes": {
                "companies": 0, "signals": 0, "keyword_company_results": 0,
                "keyword_search_audits": len(COVERAGE),
            },
            "workbook": {
                "canonical": {"inserted": 0, "updated": 0, "unchanged": 135, "failed": 1, "removed": 0},
                "local_staging": {"inserted": 0, "updated": 0, "unchanged": 128, "failed_or_deferred": 13, "removed": 0},
            },
            "blockers": [
                WORKBOOK_BLOCKER,
                "Direct X.com was certificate-blocked for all 15 keywords; no warning was bypassed.",
                "Google imposed a human-verification interstitial after the in-app Browser source checks; it was not solved or bypassed.",
                "Startup Gallery X-ray searches yielded no relevant Canadian prospect for all 15 saved keywords.",
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
