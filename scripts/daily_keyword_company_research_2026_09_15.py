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
from enrichment.identity_verification import CompanyIdentityEvidence
from models.schema import ExtractedSignal


RUN_AT = datetime.now(timezone.utc)
LOCK_PATH = Path(
    r"C:\Users\ranjeet.chaudhary\.codex\automations\daily-keyword-company-research\run.lock"
)


COMPANIES = (
    {
        "company_name": "Kardium Inc.",
        "company_domain": "kardium.com",
        "company_url": "https://kardium.com/",
        "location": "Burnaby, British Columbia, Canada",
        "industry": "Cardiac mapping and ablation medical-device manufacturing",
        "products": ["Teamcenter", "Polarion", "Opcenter"],
        "scores": (98, 100, 100, 98, 100),
        "keywords": (8,),
        "identity": CompanyIdentityEvidence(
            official_name="Kardium Inc.",
            official_website_url="https://kardium.com/",
            corroborating_urls=(
                "https://techcouver.com/2026/08/27/kardium-125-million-burnaby-manufacturing-expansion/",
            ),
        ),
        "signals": (
            {
                "signal_date": datetime(2026, 8, 27, tzinfo=timezone.utc),
                "source_url": "https://kardium.com/news/kardium-receives-funding-from-the-government-of-canada-to-expand-manufacturing-of-the-globe-pulsed-field-system-in-british-columbia/",
                "source_title": "Kardium receives funding from the Government of Canada to Expand Manufacturing of the Globe Pulsed Field System in British Columbia",
                "source_publisher": "Kardium",
                "signal_label": "C$125M cleanroom expansion follows Canadian and U.S. regulatory approvals",
                "pain_signals": [
                    "Must scale a regulated, integrated cardiac mapping and pulsed-field-ablation system while preserving released-device configuration, cleanroom controls, verification evidence, and lot or serial traceability."
                ],
                "expansion_signals": [
                    "Received up to C$31.25 million in federal Strategic Response Fund support toward a C$125 million Vancouver manufacturing expansion."
                ],
                "challenge_summary": (
                    "On August 27, 2026, Kardium announced up to C$31.25 million in federal Strategic Response Fund support toward a C$125 million expansion of its Vancouver cleanroom manufacturing capability for the Globe Pulsed Field System. "
                    "The same announcement states that the integrated cardiac mapping and ablation system received Health Canada approval in July 2026 after U.S. FDA approval in August 2025. "
                    "Inference: moving a newly approved catheter-and-electrode platform into global-scale cleanroom production creates immediate BOM and change-control, regulated requirements and test-evidence, production-quality, and lot or serial traceability pressure."
                ),
                "why_relevant": (
                    "Teamcenter can govern released device structures, revisions, suppliers, and engineering changes; Polarion can connect regulatory requirements, risk controls, tests, and defects; Opcenter can support controlled cleanroom execution and quality genealogy. "
                    "The funded expansion and July 2026 Canadian approval make the operating need current because manufacturing controls must mature before the volume ramp."
                ),
            },
            {
                "signal_date": datetime(2026, 8, 27, tzinfo=timezone.utc),
                "source_url": "https://techcouver.com/2026/08/27/kardium-125-million-burnaby-manufacturing-expansion/",
                "source_title": "Ottawa Backs Kardium's $125 Million Burnaby Manufacturing Expansion",
                "source_publisher": "Techcouver",
                "signal_label": "Annual Globe System capacity targeted to rise 60-fold from 500 to 30,000 units",
                "pain_signals": [
                    "Must industrialize a 122-electrode cardiac catheter platform at roughly 60 times current annual capacity while maintaining cleanroom quality, regulatory evidence, supplier coordination, and production traceability."
                ],
                "expansion_signals": [
                    "Techcouver reports that the cleanroom project is intended to raise annual Globe System capacity from 500 to 30,000 units and create or maintain 1,000 skilled British Columbia jobs."
                ],
                "challenge_summary": (
                    "On August 27, 2026, Techcouver independently reported that Kardium's C$125 million Burnaby expansion is intended to increase annual Globe System capacity from 500 to 30,000 units and create or maintain 1,000 skilled jobs. "
                    "The Globe platform combines real-time high-density cardiac mapping and pulsed-field ablation in a single catheter with a 122-electrode array. "
                    "Inference: a 60-fold ramp of a regulated electromechanical disposable and capital-system platform sharply increases supplier, configuration, cleanroom execution, inspection, nonconformance, and lot or serial genealogy demands."
                ),
                "why_relevant": (
                    "Teamcenter can control the device and system BOMs, released revisions, suppliers, and engineering changes; Polarion can maintain traceability from requirements and risk controls through verification; Opcenter can manage cleanroom work, inspections, and production genealogy. "
                    "The quantified 500-to-30,000 capacity target creates an urgent systems window before the expanded line reaches volume."
                ),
            },
        ),
    },
    {
        "company_name": "Calogy Solutions",
        "company_domain": "calogysolutions.com",
        "company_url": "https://calogysolutions.com/",
        "location": "Sherbrooke, Quebec, Canada",
        "industry": "Battery and thermal-management hardware manufacturing",
        "products": ["Teamcenter", "Simcenter", "Polarion", "Capital"],
        "scores": (93, 95, 93, 95, 98),
        "keywords": (5, 7, 8, 13),
        "identity": CompanyIdentityEvidence(
            official_name="Calogy Solutions",
            official_website_url="https://calogysolutions.com/",
            corroborating_urls=(
                "https://betakit.com/calogy-secures-1-2-million-contract-to-power-jaunts-autonomous-drones/",
            ),
        ),
        "signals": (
            {
                "signal_date": datetime(2026, 8, 4, tzinfo=timezone.utc),
                "source_url": "https://betakit.com/calogy-secures-1-2-million-contract-to-power-jaunts-autonomous-drones/",
                "source_title": "Calogy secures $1.2-million contract to power Jaunt's autonomous drones",
                "source_publisher": "BetaKit",
                "signal_label": "C$1.2M Jaunt contract targets flight-test battery delivery by year-end",
                "pain_signals": [
                    "Must design and validate a lightweight battery and thermal-management system for a large hybrid-electric autonomous aircraft operating across extreme temperatures."
                ],
                "expansion_signals": [
                    "Won a C$1.2 million Jaunt Air Mobility Canada development contract and plans to deliver the flight-test battery by year-end before joint manufacturing and market entry in 2027."
                ],
                "challenge_summary": (
                    "On August 4, 2026, BetaKit reported that Calogy won a C$1.2 million contract to design the battery system for Jaunt Air Mobility Canada's next-generation large autonomous hybrid-electric drone, with a test system due before year-end and joint manufacturing targeted for 2027. "
                    "The aircraft must combine helicopter-like hover with fixed-wing range and speed, while Calogy's battery must control weight, thermal runaway, reliability, and performance from Arctic cold to intense heat. "
                    "Inference: the program creates immediate battery, electronics, aircraft-interface, thermal-simulation, safety-requirement, test-evidence, and released-configuration complexity."
                ),
                "why_relevant": (
                    "Teamcenter can govern the battery, thermal plate, electronics, aircraft interfaces, suppliers, and released revisions; Simcenter can support thermal and multiphysics validation; Polarion can trace flight and safety requirements into tests and defects; Capital can manage electrical architecture. "
                    "The year-end test delivery and planned 2027 manufacturing transition make design governance and verification urgent now."
                ),
            },
        ),
    },
    {
        "company_name": "Dominion Dynamics",
        "company_domain": "defendthedominion.com",
        "company_url": "https://www.defendthedominion.com/",
        "location": "Kanata and Toronto, Ontario, Canada",
        "industry": "Autonomous aircraft, sensing, and multi-domain defence systems",
        "products": ["Teamcenter", "Polarion", "Simcenter", "Opcenter"],
        "scores": (98, 99, 100, 98, 99),
        "keywords": (7, 8, 9, 13, 14),
        "identity": CompanyIdentityEvidence(
            official_name="Dominion Dynamics",
            official_website_url="https://www.defendthedominion.com/",
            corroborating_urls=(
                "https://spaceq.ca/dominion-dynamics-closes-139m-series-a-for-arctic-and-space-defence-systems/",
            ),
        ),
        "signals": (
            {
                "signal_date": datetime(2026, 6, 30, tzinfo=timezone.utc),
                "source_url": "https://spaceq.ca/dominion-dynamics-closes-139m-series-a-for-arctic-and-space-defence-systems/",
                "source_title": "Dominion Dynamics closes $139M Series A for Arctic and space defence systems",
                "source_publisher": "SpaceQ",
                "signal_label": "C$139M Series A funds a 25,000-square-foot Kanata manufacturing ramp",
                "pain_signals": [
                    "Must coordinate autonomous aircraft, sensors, communications, command-and-control software, manufacturing, and extreme-environment verification as programs and engineering headcount scale."
                ],
                "expansion_signals": [
                    "Closed a C$139 million Series A, moved into a 25,000-square-foot Kanata manufacturing facility, opened a Toronto development office, and plans to exceed 100 employees by year-end."
                ],
                "challenge_summary": (
                    "On June 30, 2026, SpaceQ reported that Dominion Dynamics closed a C$139 million Series A, moved into a 25,000-square-foot Kanata manufacturing facility, opened a Toronto development office, and plans to grow beyond 100 employees by year-end. "
                    "The funding supports AuraNet's land-sea-air-space data network and Scout, an autonomous uncrewed aircraft designed to operate alongside crewed fifth-generation fighters. "
                    "Inference: scaling linked aircraft, sensor, communications, software, and factory work creates immediate multidisciplinary configuration, supplier-interface, defence-requirement, simulation, test-evidence, and production-control pressure."
                ),
                "why_relevant": (
                    "Teamcenter can govern Scout hardware, electronics, software, suppliers, and released configurations; Polarion can trace mission and safety requirements through verification; Simcenter can support structural, thermal, flight, and systems validation; Opcenter can establish repeatable production and quality genealogy in the new plant. "
                    "The funded facility and hiring ramp are already under way, so shared engineering and manufacturing controls are needed before program variants and allied deployments multiply."
                ),
            },
        ),
    },
)


def make_signal(company: dict[str, object], evidence: dict[str, object]) -> ExtractedSignal:
    opportunity, _manufacturing, _trigger, _solution, evidence_score = company["scores"]
    return ExtractedSignal(
        company_name=str(company["company_name"]),
        company_domain=str(company["company_domain"]),
        company_url=str(company["company_url"]),
        location=str(company["location"]),
        industry=str(company["industry"]),
        company_industry=str(company["industry"]),
        software=list(company["products"]),
        signal_type="news",
        signal_source="news",
        pain_signals=list(evidence["pain_signals"]),
        expansion_signals=list(evidence["expansion_signals"]),
        raw_score=int(opportunity),
        confidence=int(evidence_score) / 100,
        reason=str(evidence["challenge_summary"]),
        source_url=str(evidence["source_url"]),
        source_title=str(evidence["source_title"]),
        detected_at=evidence["signal_date"],
    )


def record_link(
    database: Database,
    keyword_id: int,
    company: dict[str, object],
    evidence: dict[str, object],
):
    opportunity, manufacturing, trigger, solution, evidence_score = company["scores"]
    row = database.record_keyword_company(
        keyword_id,
        str(company["company_name"]),
        str(company["company_domain"]),
        source_url=str(evidence["source_url"]),
        source_title=str(evidence["source_title"]),
        source_publisher=str(evidence["source_publisher"]),
        signal_label=str(evidence["signal_label"]),
        signal_date=evidence["signal_date"],
        challenge_summary=str(evidence["challenge_summary"]),
        why_relevant=str(evidence["why_relevant"]),
        recommended_products=list(company["products"]),
        qualification_status="qualified",
        opportunity_score=int(opportunity),
        manufacturing_fit_score=int(manufacturing),
        trigger_score=int(trigger),
        solution_fit_score=int(solution),
        evidence_quality_score=int(evidence_score),
        seen_at=RUN_AT,
    )
    if row is None:
        raise RuntimeError(f"Could not link {company['company_name']} to keyword {keyword_id}")
    return row


def main() -> None:
    load_dotenv(REPO_ROOT / ".env")
    marker = json.loads(LOCK_PATH.read_text(encoding="utf-8"))
    if int(marker.get("pid", 0)) <= 0:
        raise RuntimeError("Exclusive automation lock is not held")

    database = Database(os.environ["DATABASE_URL"])
    database.initialize()
    keywords_before = {row.id: row for row in database.list_keywords()}
    expected_ids = {1, 2, 3, 4, 5, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16}
    if set(keywords_before) != expected_ids:
        raise RuntimeError(f"Persistent keyword set changed: {sorted(keywords_before)}")

    prior_domains = {lead.company_domain for lead in database.get_leads(limit=5000)}
    published = {keyword_id: 0 for keyword_id in keywords_before}
    new_domains: set[str] = set()
    signals: list[dict[str, object]] = []
    links: list[dict[str, object]] = []

    for company in COMPANIES:
        domain = str(company["company_domain"])
        if domain not in prior_domains:
            new_domains.add(domain)
        primary_evidence = company["signals"][-1]
        company_record = None
        for evidence in company["signals"]:
            saved, company_record = database.persist_verified_signal(
                make_signal(company, evidence), company["identity"]
            )
            signals.append(
                {
                    "company": company_record.company_name,
                    "company_domain": company_record.company_domain,
                    "source_url": evidence["source_url"],
                    "created": saved.created,
                    "duplicate_url": saved.duplicate_url,
                    "signal_count": company_record.signal_count,
                }
            )
        for keyword_id in company["keywords"]:
            row = record_link(database, keyword_id, company, primary_evidence)
            published[keyword_id] += 1
            links.append(
                {
                    "keyword_id": keyword_id,
                    "company_id": row.company_id,
                    "company_name": row.company_name,
                    "qualification_status": row.qualification_status,
                    "opportunity_score": row.opportunity_score,
                }
            )

    for keyword_id in sorted(keywords_before):
        if database.record_keyword_search(
            keyword_id, result_count=published[keyword_id], error=None
        ) is None:
            raise RuntimeError(f"Could not record keyword search {keyword_id}")

    keywords_after = {row.id: row for row in database.list_keywords()}
    for keyword_id, before in keywords_before.items():
        after = keywords_after[keyword_id]
        if after.search_count != before.search_count + 1:
            raise RuntimeError(f"Keyword {keyword_id} did not advance exactly once")
        if after.last_error is not None:
            raise RuntimeError(f"Keyword {keyword_id} retained error: {after.last_error}")

    print(
        json.dumps(
            {
                "run_at": RUN_AT.isoformat(),
                "new_company_domains": sorted(new_domains),
                "signals": signals,
                "keyword_links": links,
                "keyword_audits": [
                    {
                        "id": keyword_id,
                        "keyword": keywords_after[keyword_id].keyword,
                        "search_count_before": keywords_before[keyword_id].search_count,
                        "search_count_after": keywords_after[keyword_id].search_count,
                        "qualified": published[keyword_id],
                        "watchlist": 0,
                        "last_error": keywords_after[keyword_id].last_error,
                    }
                    for keyword_id in sorted(keywords_after)
                ],
            },
            indent=2,
            default=str,
        )
    )


if __name__ == "__main__":
    main()
