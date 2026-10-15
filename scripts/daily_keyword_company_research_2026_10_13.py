from __future__ import annotations

import json
import os
import io
import sys
from contextlib import redirect_stdout
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from enrichment.identity_verification import CompanyIdentityEvidence
from scripts import daily_keyword_company_research_2026_10_12_run2 as runner


RUN_AT = datetime.now(timezone.utc)
LOCK_PATH = Path(
    r"C:\Users\ranjeet.chaudhary\.codex\automations\daily-keyword-company-research\run.lock"
)


COMPANIES = [
    {
        "company_name": "Jones Microwave Inc.",
        "company_domain": "jonesmicrowave.com",
        "company_url": "https://www.jonesmicrowave.com/",
        "location": "Edmonton, Alberta, Canada",
        "industry": "Advanced RF and microwave switching components for radar, satellite, and communications systems",
        "products": ["Teamcenter", "Simcenter"],
        "identity": CompanyIdentityEvidence(
            official_name="Jones Microwave Inc.",
            official_website_url="https://www.jonesmicrowave.com/",
            corroborating_urls=(
                "https://www.canada.ca/en/department-national-defence/news/2026/10/prairiescan-investments-in-defence-related-projects-will-strengthen-the-alberta-economy-and-support-canadas-military-readiness.html",
            ),
        ),
        "evidence": [{
            "source_url": "https://www.canada.ca/en/department-national-defence/news/2026/10/prairiescan-investments-in-defence-related-projects-will-strengthen-the-alberta-economy-and-support-canadas-military-readiness.html",
            "source_title": "PrairiesCan investments in defence-related projects will strengthen the Alberta economy and support Canada's military readiness",
            "source_publisher": "Government of Canada — National Defence and PrairiesCan",
            "signal_date": datetime(2026, 10, 7, tzinfo=timezone.utc),
            "signal_label": "C$1.789M funds higher-frequency microwave-switch manufacturing expansion",
            "challenge_summary": (
                "On October 7, 2026, the Government of Canada announced C$1,789,279 in repayable funding for Jones Microwave to expand manufacturing capacity for advanced microwave switching products that operate at higher frequencies and faster speeds for radar, satellite, and communications applications. The company's official site identifies planar and waveguide plasma-switch products spanning DC to more than 110 GHz for compact, high-power, low-loss systems. Inference: scaling mission-critical RF hardware adds component variants, supplier and material controls, released-design changes, test-data traceability, and coupled RF/thermal validation pressure."
            ),
            "why_relevant": (
                "Teamcenter is the smallest defensible fit for controlling component configurations, released designs and BOMs, approved suppliers, quality records, and engineering changes as output expands. Simcenter can support RF, thermal, and multiphysics validation as the product platform moves to higher frequency and power. The funded capacity project is starting now for defence-critical supply chains, so process and engineering controls need to mature before the new capacity is locked in."
            ),
        }],
        "pain": "Must scale manufacture of high-frequency mission-critical RF switches while preserving configuration, supplier, test, and multiphysics-validation control.",
        "expansion": "Received C$1,789,279 in repayable federal funding to expand manufacturing capacity for advanced microwave switching products.",
        "keyword_ids": [8, 10, 14, 16],
        "qualification_status": "qualified",
        "opportunity_score": 94,
        "manufacturing_fit_score": 94,
        "trigger_score": 96,
        "solution_fit_score": 92,
        "evidence_quality_score": 98,
    },
    {
        "company_name": "Pegasus Imagery Ltd.",
        "company_domain": "flypegasus.ai",
        "company_url": "https://www.flypegasus.ai/",
        "location": "Sturgeon County, Alberta, Canada",
        "industry": "Aircraft-integrated sensing hardware for real-time icing and environmental intelligence",
        "products": ["Teamcenter", "Polarion", "Simcenter"],
        "identity": CompanyIdentityEvidence(
            official_name="Pegasus Imagery Ltd.",
            official_website_url="https://www.flypegasus.ai/",
            corroborating_urls=(
                "https://www.miragenews.com/prairiescan-defence-investments-boost-alberta-1756525/",
                "https://search.open.canada.ca/grants/record/nrc-cnrc%2C172-2026-2027-Q1-1043639%2Ccurrent",
            ),
        ),
        "evidence": [{
            "source_url": "https://www.miragenews.com/prairiescan-defence-investments-boost-alberta-1756525/",
            "source_title": "PrairiesCan Defence Investments Boost Alberta Economy",
            "source_publisher": "Mirage News",
            "signal_date": datetime(2026, 10, 8, tzinfo=timezone.utc),
            "signal_label": "C$2M MIDAS program funds hardware validation and production scale-up",
            "challenge_summary": (
                "On October 8, 2026, Mirage News reported C$2 million in repayable PrairiesCan funding for Pegasus Imagery to develop its next-generation MIDAS aircraft-surface sensing system, validate the hardware, and scale production for real-time ice monitoring and Arctic operations. Pegasus' official site positions MIDAS as aircraft-integrated sensing for defence and aircraft-OEM applications. Inference: production scale-up and harsh-environment deployment increase sensor and aircraft-interface configurations, requirements-to-test traceability, certification evidence, supplier change control, and icing, thermal, and environmental validation workloads."
            ),
            "why_relevant": (
                "Teamcenter can govern the sensor, electronics, software-linked configuration, suppliers, and released changes across aircraft integrations. Polarion can connect safety, environmental, and customer requirements to verification tests, defects, and acceptance evidence, while Simcenter can support icing, thermal, structural, and system-level validation. The October funding explicitly covers hardware validation and production scaling, creating a current window before the next-generation baseline and manufacturing process harden."
            ),
        }],
        "pain": "Must validate and industrialize next-generation aircraft icing-sensor hardware for Arctic and defence use with auditable configuration, requirements, and test evidence.",
        "expansion": "Received C$2 million in repayable PrairiesCan funding to validate MIDAS hardware and scale production.",
        "keyword_ids": [7, 8, 9, 10, 14, 16],
        "qualification_status": "qualified",
        "opportunity_score": 96,
        "manufacturing_fit_score": 95,
        "trigger_score": 98,
        "solution_fit_score": 97,
        "evidence_quality_score": 92,
    },
    {
        "company_name": "GKD Industries Ltd.",
        "company_domain": "gkdindustries.com",
        "company_url": "https://www.gkdindustries.com/",
        "location": "Calgary, Alberta, Canada",
        "industry": "Precision machining and proprietary pressure-control equipment for energy, aerospace, and defence",
        "products": ["Teamcenter", "Opcenter"],
        "identity": CompanyIdentityEvidence(
            official_name="GKD Industries Ltd.",
            official_website_url="https://www.gkdindustries.com/index.html",
            corroborating_urls=(
                "https://www.canada.ca/fr/ministere-defense-nationale/nouvelles/2026/10/les-investissements-de-prairiescan-dans-des-projets-lies-a-la-defense-renforceront-leconomie-de-lalberta-et-soutiendront-letat-de-preparation-milit.html",
            ),
        ),
        "evidence": [{
            "source_url": "https://www.canada.ca/fr/ministere-defense-nationale/nouvelles/2026/10/les-investissements-de-prairiescan-dans-des-projets-lies-a-la-defense-renforceront-leconomie-de-lalberta-et-soutiendront-letat-de-preparation-milit.html",
            "source_title": "Les investissements de PrairiesCan dans des projets liés à la défense renforceront l'économie de l'Alberta",
            "source_publisher": "Gouvernement du Canada — Défense nationale et PrairiesCan",
            "signal_date": datetime(2026, 10, 7, tzinfo=timezone.utc),
            "signal_label": "C$1M expands precision-machining capacity for aerospace and defence work",
            "challenge_summary": (
                "On October 7, 2026, the Government of Canada announced C$1 million in repayable funding for GKD Industries to expand precision-machining capacity, increase output, and pursue higher-value work for the energy, aerospace, and defence sectors. GKD's official site identifies proprietary well-stimulation and slickline products alongside contract manufacturing, ISO 9001 processes, Controlled Goods registration, serialized product history, test certificates, and long-term document traceability. Inference: higher-volume, higher-value regulated machining intensifies scheduling, genealogy, process-plan, nonconformance, supplier, and engineering-change control across proprietary and customer designs."
            ),
            "why_relevant": (
                "Teamcenter can control product and manufacturing structures, customer configurations, drawings, suppliers, and released changes while preserving the product-history evidence GKD already emphasizes. Opcenter can extend real-time scheduling and barcode capture into production genealogy, quality, and nonconformance workflows. The funded capacity increase and move into higher-value defence and aerospace work make scalable traceability and production control urgent now."
            ),
        }],
        "pain": "Must expand precision-machining throughput for higher-value regulated sectors without losing serialized genealogy, document control, scheduling, and quality traceability.",
        "expansion": "Received C$1 million in repayable federal funding to expand machining capacity and pursue aerospace and defence work.",
        "keyword_ids": [5, 10, 14, 16],
        "qualification_status": "qualified",
        "opportunity_score": 91,
        "manufacturing_fit_score": 97,
        "trigger_score": 94,
        "solution_fit_score": 92,
        "evidence_quality_score": 97,
    },
    {
        "company_name": "MRO Electronic Supply Ltd.",
        "company_domain": "mroelectronics.com",
        "company_url": "https://mroelectronics.com/",
        "location": "Calgary, Alberta, Canada",
        "industry": "AS9100 aerospace and defence cable assemblies, wire harnesses, and electronic box builds",
        "products": ["Teamcenter", "Capital", "Opcenter"],
        "identity": CompanyIdentityEvidence(
            official_name="MRO Electronic Supply Ltd.",
            official_website_url="https://mroelectronics.com/",
            corroborating_urls=(
                "https://www.canada.ca/fr/developpement-economique-prairies/nouvelles/2026/05/document-dinformation--le-gouvernement-du-canada-investit-dans-linnovation-et-la-fabrication-en-matiere-de-defense-en-alberta.html",
            ),
        ),
        "evidence": [{
            "source_url": "https://www.canada.ca/fr/developpement-economique-prairies/nouvelles/2026/05/document-dinformation--le-gouvernement-du-canada-investit-dans-linnovation-et-la-fabrication-en-matiere-de-defense-en-alberta.html",
            "source_title": "Document d'information — Le gouvernement du Canada investit dans l'innovation et la fabrication en matière de défense en Alberta",
            "source_publisher": "Gouvernement du Canada — Prairies Economic Development Canada",
            "signal_date": datetime(2026, 5, 12, tzinfo=timezone.utc),
            "signal_label": "C$1M launches defence-electronics capacity and quality expansion",
            "challenge_summary": (
                "On May 12, 2026, the Government of Canada announced C$1 million in repayable funding for MRO Electronic Supply to expand defence-manufacturing capacity, modernize facilities and sourcing, and create or retain highly skilled technical and engineering roles in advanced manufacturing, quality assurance, and defence electronics. MRO's official site identifies AS9100 cable assemblies, wire harnesses, and box builds with 100% electrical testing, material traceability, in-house overmoulding, and CNC tooling. Inference: more harness and electronic-assembly programs increase connector and wire variants, electrical configuration, tooling revisions, work instructions, test records, material genealogy, and customer-specific quality evidence."
            ),
            "why_relevant": (
                "Teamcenter can govern harness and box-build BOMs, approved parts and suppliers, documents, and released engineering changes. Capital is the focused fit for electrical-system and harness architecture, while Opcenter can manage travellers, material genealogy, test capture, and AS9100 quality execution. The 2026 capacity program is active while facilities, sourcing, engineering roles, and production processes are changing, making this the right point to establish a controlled digital thread."
            ),
        }],
        "pain": "Must scale complex aerospace and defence harness and electronics production while controlling electrical configuration, tooling, materials, test records, and AS9100 traceability.",
        "expansion": "Received C$1 million in repayable funding to expand defence-manufacturing capacity, modernize facilities and sourcing, and add or retain technical roles.",
        "keyword_ids": [10, 14, 16],
        "qualification_status": "qualified",
        "opportunity_score": 92,
        "manufacturing_fit_score": 98,
        "trigger_score": 92,
        "solution_fit_score": 96,
        "evidence_quality_score": 95,
    },
]


# reviewed domains, new-to-ledger domains, rejected pre-persistence, qualified, watchlist, duplicates/existing
REVIEW = {
    1: (16, 6, 16, 0, 0, 10), 2: (18, 7, 18, 0, 0, 11), 3: (16, 5, 16, 0, 0, 11),
    4: (18, 7, 18, 0, 0, 11), 5: (17, 7, 16, 1, 0, 10), 7: (21, 9, 20, 1, 0, 12),
    8: (19, 9, 17, 2, 0, 10), 9: (21, 8, 20, 1, 0, 13), 10: (20, 9, 16, 4, 0, 11),
    11: (17, 6, 17, 0, 0, 11), 12: (18, 7, 18, 0, 0, 11), 13: (19, 8, 19, 0, 0, 11),
    14: (20, 10, 16, 4, 0, 10), 15: (18, 7, 18, 0, 0, 11), 16: (19, 10, 15, 4, 0, 9),
}


RAW_RESULTS = {
    1: (34, 29), 2: (35, 33), 3: (31, 29), 4: (37, 34), 5: (33, 33),
    7: (39, 39), 8: (35, 32), 9: (39, 36), 10: (34, 32), 11: (35, 30),
    12: (36, 34), 13: (36, 35), 14: (33, 33), 15: (37, 36), 16: (36, 35),
}


def lock_run() -> int | None:
    try:
        descriptor = os.open(LOCK_PATH, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError:
        print(json.dumps({"status": "skipped", "reason": "active automation lock exists", "lock": str(LOCK_PATH)}))
        return None
    payload = json.dumps({"pid": os.getpid(), "started_at": RUN_AT.isoformat()}).encode("utf-8")
    os.write(descriptor, payload)
    os.close(descriptor)
    return os.getpid()


def main() -> None:
    lock_owner = lock_run()
    if lock_owner is None:
        return
    try:
        runner.RUN_AT = RUN_AT
        runner.COMPANIES = COMPANIES
        runner.REVIEW = REVIEW
        captured = io.StringIO()
        with redirect_stdout(captured):
            runner.main()
        report = json.loads(captured.getvalue())
        for audit in report["keyword_audits"]:
            raw_count, distinct_url_count = RAW_RESULTS[audit["id"]]
            audit["raw_search_results"] = raw_count
            audit["distinct_result_urls_inspected"] = distinct_url_count
        report["coverage"]["source_specific_checks"] = {
            "all_keywords": ["Startup Gallery Canada", "X.com public search", "BetaKit", "NGen"],
            "aerospace_defence": ["SpaceQ", "AIAC", "Skies Magazine", "CADSI"],
            "automotive_mobility": ["Electric Autonomy Canada", "APMA", "OVIN"],
            "marine": ["Naval News", "Shipbuilding Association of Canada", "Canada's Ocean Supercluster"],
            "regional_and_cluster": ["Aero Montreal", "DAIR Aerospace", "Oakville Chamber of Commerce"],
            "funding_and_procurement": ["CanadaBuys", "PrairiesCan", "FedDev Ontario", "ventureLAB Hardware Catalyst"],
        }
        report["coverage"]["current_pass_notes"] = [
            "Startup Gallery's Canada collection was directly inspected and yielded no lead that passed both the physical-product and dated-trigger gates.",
            "X.com public search was directly attempted but stopped at ERR_CERT_AUTHORITY_INVALID; the warning was not bypassed.",
            "BetaKit and NGen received separate source-specific searches for every persistent keyword.",
            "The first full pass produced qualified companies, so the zero-new-company gap-fill pass was not triggered.",
        ]
        print(json.dumps(report, indent=2, default=str))
    finally:
        if LOCK_PATH.exists():
            try:
                marker = json.loads(LOCK_PATH.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                marker = {}
            if marker.get("pid") == lock_owner:
                LOCK_PATH.unlink()


if __name__ == "__main__":
    main()
