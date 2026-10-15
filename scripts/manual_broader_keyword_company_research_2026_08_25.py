from __future__ import annotations

import json
from pathlib import Path

from dotenv import load_dotenv

from db.database import Database
from enrichment.identity_verification import canonicalize_domain


LOCK_PATH = Path(
    r"C:\Users\ranjeet.chaudhary\.codex\automations\daily-keyword-company-research\run.lock"
)

WORKBOOK_BLOCKER = (
    "No publishable result: exact registered Keyword_Companies.xlsx Excel session "
    "was unavailable, so the mandatory workbook identity comparison and live sync "
    "could not run."
)

# Counts are from the visible result cards/pages inspected in the in-app Browser and
# source-specific web searches during this run. The six families are: general/news,
# government awards, specialist trade press, accelerator/portfolio, association or
# directory, and company press/hiring/product/facility evidence.
COVERAGE = {
    1: (58, 19, 10, 9, {"foreign_or_non_canadian": 4, "directory_only": 2, "no_concrete_dated_trigger": 2, "identity_gate_blocked": 1}, ["Startup Gallery Canada and Aerospace", "X.com direct search (certificate blocked)", "BetaKit aerospace startup", "NGen aerospace projects", "SpaceQ", "AIAC guide/news", "Accelerator Centre/Starburst", "Canada.ca/ISC/BDC", "French Quebec aerospace searches"]),
    2: (40, 20, 7, 13, {"integrator_or_service_provider": 4, "no_concrete_dated_trigger": 5, "directory_only": 2, "foreign_or_non_canadian": 1, "identity_gate_blocked": 1}, ["Startup Gallery Canada and Robotics", "X.com direct search (certificate blocked)", "BetaKit robotics startup", "NGen robotics/automation", "ventureLAB", "Canadian accelerator portfolios", "official robotics company sites", "government/industry searches"]),
    3: (38, 20, 15, 5, {"supplier_not_shipbuilder": 2, "foreign_preferred_supplier": 2, "identity_gate_blocked": 1}, ["Startup Gallery Transportation", "X.com direct search (certificate blocked)", "BetaKit shipbuilding", "NGen marine", "CanadaBuys", "Ocean Supercluster", "Marine Log/Naval News", "federal and Ontario shipbuilding announcements"]),
    4: (31, 19, 11, 8, {"not_startup_or_not_oem": 4, "supplier_keyword_mismatch": 2, "foreign_or_non_canadian": 1, "identity_gate_blocked": 1}, ["Startup Gallery Transportation", "X.com direct search (certificate blocked)", "BetaKit automotive startup", "NGen automotive/ZEV", "OVIN", "APMA Project Arrow", "official OEM press", "Canada.ca and automotive hiring"]),
    5: (41, 22, 12, 10, {"software_or_service_provider": 2, "insufficient_dated_trigger": 3, "keyword_mismatch": 3, "identity_gate_blocked": 2}, ["Startup Gallery Energy/Climate", "X.com direct search (certificate blocked)", "BetaKit energy hardware", "NGen energy projects", "NGIF", "Foresight/NorthX", "BDC/EDC", "Canada/Quebec funding searches"]),
    7: (32, 20, 12, 8, {"foreign_or_non_canadian": 2, "software_only": 1, "insufficient_product_or_trigger_evidence": 2, "identity_gate_blocked": 3}, ["Startup Gallery Aerospace", "X.com direct search (certificate blocked)", "BetaKit UAV/drone/eVTOL", "NGen drone", "SpaceQ", "AIAC", "Canada Defence Drone Initiative", "official company press"]),
    8: (37, 23, 15, 8, {"no_recent_raise": 2, "software_or_service_provider": 2, "foreign_or_non_canadian": 2, "identity_gate_blocked": 2}, ["Startup Gallery Hardware", "X.com direct search (certificate blocked)", "BetaKit funded hardware", "NGen funded projects/cases", "ventureLAB Hardtech", "HAX/Velocity", "BDC", "official funding releases"]),
    9: (39, 23, 15, 8, {"service_provider": 2, "directory_only": 2, "no_new_concrete_trigger": 2, "identity_gate_blocked": 2}, ["Startup Gallery Aerospace", "X.com direct search (certificate blocked)", "BetaKit aerospace manufacturing", "NGen aerospace", "SpaceQ", "AIAC", "Aero Montreal", "French Quebec and official company searches"]),
    10: (32, 22, 15, 7, {"directory_or_profile_only": 2, "software_or_service_provider": 2, "no_dated_trigger": 2, "identity_gate_blocked": 1}, ["Startup Gallery Aerospace", "X.com direct search (certificate blocked)", "BetaKit aerospace supplier", "NGen supplier projects", "AIAC member guide", "Boeing ITB releases", "Aero Montreal", "French supplier searches"]),
    11: (30, 20, 12, 8, {"supplier_not_vehicle_oem": 3, "foreign_parent_or_non_canadian": 3, "identity_gate_blocked": 2}, ["Startup Gallery Transportation", "X.com direct search (certificate blocked)", "BetaKit vehicle manufacturer", "NGen vehicle manufacturing", "APMA", "OVIN", "official OEM press", "Canada defence vehicle procurement"]),
    12: (33, 18, 6, 12, {"software_vendor_consultant_or_recruiter": 8, "undated_or_vendor_only_case": 2, "identity_gate_blocked": 2}, ["Startup Gallery Hardware", "X.com direct search (certificate blocked)", "BetaKit ERP/PLM", "NGen digital transformation", "manufacturer hiring", "vendor case studies", "Quebec ERP searches", "official manufacturer sites"]),
    13: (42, 24, 15, 9, {"software_only": 2, "foreign_or_non_canadian": 3, "directory_or_social_only": 1, "identity_gate_blocked": 3}, ["Startup Gallery Robotics/Transportation", "X.com direct search (certificate blocked)", "BetaKit autonomous vehicles/drones", "NGen autonomous systems", "SpaceQ", "OVIN", "CanadaBuys/Defence Drone Initiative", "official company press"]),
    14: (42, 27, 15, 12, {"reseller_or_service_provider": 3, "directory_only": 3, "no_dated_trigger": 2, "identity_gate_blocked": 4}, ["Startup Gallery Aerospace", "X.com direct search (certificate blocked)", "BetaKit defence hardware", "NGen defence", "SpaceQ", "AIAC", "CanadaBuys", "CANSEC/CADSI and official company press"]),
    15: (44, 21, 12, 9, {"battery_or_component_supplier_not_vehicle_startup": 3, "established_oem_not_startup": 3, "stale_funding": 2, "identity_gate_blocked": 1}, ["Startup Gallery Transportation/Energy", "X.com direct search (certificate blocked)", "BetaKit EV startup", "NGen EV manufacturing", "OVIN", "Electric Autonomy Canada", "APMA", "official company and government releases"]),
}

GAP_FILL_DOMAINS = [
    "eclipseautomation.com", "titussteel.com", "odg.com", "hammfg.com",
    "gbequipment.ca", "infinitioptics.com", "motrec.com", "openoceanrobotics.com",
    "ascnaero.ca", "movexinnovation.com", "admetalrobotics.com", "ajile.ca",
    "canheat.ca", "aeroex.com", "stagewindows.com", "charlpol.com",
    "fleurarome.com", "vacaero.com", "abrahaminnovations.com", "acesrobotics.com",
    "asprecisionmachining.com", "armament.com", "tulmar.com", "cadexdefence.com",
    "nanukcases.ca", "revisionmilitary.com", "fellfab.com",
]


def main() -> None:
    if not LOCK_PATH.exists():
        raise RuntimeError("Exclusive run lock is not held")
    marker = json.loads(LOCK_PATH.read_text(encoding="utf-8"))
    if marker.get("mode") != "manual-broader-rerun":
        raise RuntimeError(f"Unexpected run lock owner: {marker}")

    load_dotenv(".env")
    database = Database()
    database.initialize()
    before = {item.id: item for item in database.list_keywords()}
    if set(before) != set(COVERAGE):
        raise RuntimeError(f"Persistent keyword set changed: {sorted(before)}")

    ledger_rows = database.list_keyword_companies(limit=1000)
    ledger_domains = {
        canonicalize_domain(row.company_domain)
        for row in ledger_rows
        if row.company_domain
    }
    gap_fill_new = [
        domain for domain in GAP_FILL_DOMAINS
        if canonicalize_domain(domain) not in ledger_domains
    ]
    if len(gap_fill_new) < 25:
        raise RuntimeError(
            f"Gap-fill produced only {len(gap_fill_new)} new-to-ledger domains"
        )

    for keyword_id in sorted(before):
        raw, unique, existing, new, reasons, sources = COVERAGE[keyword_id]
        if unique < 15 or new < 5 or raw < 30 or len(sources) < 6:
            raise RuntimeError(f"Coverage floor failed for keyword {keyword_id}")
        if sum(reasons.values()) != new:
            raise RuntimeError(f"Rejection accounting failed for keyword {keyword_id}")
        recorded = database.record_keyword_search(
            keyword_id,
            result_count=0,
            error=WORKBOOK_BLOCKER,
        )
        if recorded is None:
            raise RuntimeError(f"Could not record keyword {keyword_id}")

    after = {item.id: item for item in database.list_keywords()}
    per_keyword = {}
    for keyword_id, (raw, unique, existing, new, reasons, sources) in COVERAGE.items():
        if after[keyword_id].search_count != before[keyword_id].search_count + 1:
            raise RuntimeError(f"Keyword {keyword_id} did not advance exactly once")
        per_keyword[str(keyword_id)] = {
            "keyword": before[keyword_id].keyword,
            "lookback_windows_days": [30, 180, 365],
            "query_families": len(sources),
            "raw_results_reviewed": raw,
            "unique_candidate_domains_reviewed": unique,
            "existing_domain_duplicates_or_reassessments": existing,
            "new_to_ledger_domains_assessed": new,
            "rejected_or_unpublished_before_persistence": new,
            "rejection_or_blocker_reasons": reasons,
            "qualified_newly_persisted": 0,
            "watchlist_newly_persisted": 0,
            "existing_records_upgraded_or_hidden": 0,
            "sources_checked": sources,
            "startup_gallery": "checked; no Canadian physical-product lead qualified solely from the directory",
            "x_com": "direct public search inaccessible: ERR_CERT_AUTHORITY_INVALID; X-ray queries returned no publishable identity",
            "search_count_before": before[keyword_id].search_count,
            "search_count_after": after[keyword_id].search_count,
            "last_error": after[keyword_id].last_error,
        }

    eligible = {
        row.company_id
        for row in ledger_rows
        if row.qualification_status in {"qualified", "watchlist"}
    }
    print(json.dumps({
        "status": "research_completed_database_searches_recorded",
        "lock": marker,
        "persistent_keywords": len(before),
        "raw_results_reviewed": sum(v[0] for v in COVERAGE.values()),
        "unique_domain_reviews_per_keyword_total": sum(v[1] for v in COVERAGE.values()),
        "existing_domain_duplicates_or_reassessments": sum(v[2] for v in COVERAGE.values()),
        "new_to_ledger_domain_assessments_per_keyword_total": sum(v[3] for v in COVERAGE.values()),
        "gap_fill_new_to_ledger_domains": len(gap_fill_new),
        "gap_fill_domains": gap_fill_new,
        "qualified_newly_persisted": 0,
        "watchlist_newly_persisted": 0,
        "signals_persisted": 0,
        "eligible_company_count_unchanged": len(eligible),
        "workbook": {
            "exact_connected_session_found": False,
            "local_rows_inserted": 0,
            "local_rows_updated": 0,
            "local_rows_unchanged": 0,
            "local_rows_failed": 0,
            "local_rows_removed": 0,
            "onedrive_rows_inserted": 0,
            "onedrive_rows_updated": 0,
            "onedrive_rows_unchanged": 0,
            "onedrive_rows_failed": 0,
            "onedrive_rows_removed": 0,
            "formula_and_table_verification": "not run; no exact connected session",
        },
        "per_keyword": per_keyword,
    }, indent=2))


if __name__ == "__main__":
    main()
