from __future__ import annotations

import json
import os
from datetime import datetime, timezone

from dotenv import load_dotenv

from db.database import Database
from enrichment.identity_verification import CompanyIdentityEvidence
from models.schema import ExtractedSignal


RUN_AT = datetime.now(timezone.utc)


def dt(year: int, month: int, day: int) -> datetime:
    return datetime(year, month, day, tzinfo=timezone.utc)


PROSPECTS = {
    "enerpure": {
        "company_name": "EnerPure Inc.",
        "company_domain": "enerpure.tech",
        "company_url": "https://enerpure.tech/",
        "location": "Alberta, Canada",
        "industry": "Used motor oil recycling technology and modular industrial plants",
        "products": ["Teamcenter", "Tecnomatix", "Opcenter", "Simcenter"],
        "scores": {
            "opportunity": 93,
            "manufacturing": 98,
            "trigger": 98,
            "solution": 94,
            "evidence": 98,
        },
        "pain_signals": [
            "Must move a modular recycling process from pilot scale into commercial plant engineering, commissioning and repeatable multi-site deployment.",
        ],
        "expansion_signals": [
            "Closed US$35 million of commercialization financing for a 32.6-million-litre-per-year Alberta plant and a second-site pipeline.",
        ],
        "challenge_summary": (
            "On August 20, 2026, EnerPure closed US$35 million (about C$48-49 million) of growth equity led by Rice Investment Group, including US$20 million from Canada Growth Fund, to construct its first commercial Alberta used-motor-oil recycling plant; Canadian Mining Journal reports 32.6 million litres per year of capacity and commissioning in the first half of 2028. The program moves a pilot-proven modular process into commercial construction and a repeatable North American deployment model, with capital also supporting a second plant. Inference: detailed engineering, equipment and supplier coordination, modular-plant configuration, commissioning, process-quality traceability and ramp-to-nameplate create immediate engineering-change and production-control pressure."
        ),
        "why_relevant": (
            "Teamcenter can govern modular plant and equipment structures, vendor documents, revisions and second-site reuse; Tecnomatix can validate process and facility layouts, while Opcenter can manage commissioning-to-production execution, quality and batch genealogy. Simcenter is defensible for thermal, flow and process-equipment validation as the pilot design is scaled. The financing is closed and engineering and construction execution are now underway toward first-half 2028 commissioning, creating the implementation window before commercial records proliferate."
        ),
        "identity": CompanyIdentityEvidence(
            official_name="EnerPure Inc.",
            official_website_url="https://enerpure.tech/",
            corroborating_urls=(
                "https://www.cgf-fcc.ca/en/news/rice-investment-group-and-canada-growth-fund-to-invest-us-35-million-in-enerpure-to-accelerate-commercialization-of-used-motor-oil-recycling-technology/",
                "https://www.canadianminingjournal.com/news/enerpure-closes-48m-financing-for-motor-oil-recycling-plant/",
            ),
        ),
        "evidence": (
            {
                "signal_date": dt(2026, 8, 24),
                "source_url": "https://www.canadianminingjournal.com/news/enerpure-closes-48m-financing-for-motor-oil-recycling-plant/",
                "source_title": "EnerPure closes $48M financing for motor oil recycling plant",
                "source_publisher": "Canadian Mining Journal",
                "signal_label": "C$48M financing funds 32.6M-litre Alberta recycling plant",
            },
            {
                "signal_date": dt(2026, 8, 20),
                "source_url": "https://www.cgf-fcc.ca/en/news/rice-investment-group-and-canada-growth-fund-to-invest-us-35-million-in-enerpure-to-accelerate-commercialization-of-used-motor-oil-recycling-technology/",
                "source_title": "Rice Investment Group and Canada Growth Fund to invest US$35 million in EnerPure",
                "source_publisher": "Canada Growth Fund",
                "signal_label": "US$35M equity moves modular recycling process into commercial deployment",
            },
            {
                "signal_date": dt(2026, 8, 20),
                "source_url": "https://enerpure.tech/enerpure-closes-us35-million-commercialization-financing/",
                "source_title": "EnerPure closes US$35 million commercialization financing",
                "source_publisher": "EnerPure",
                "signal_label": "Commercialization financing supports first Alberta plant and second-site pipeline",
            },
        ),
        "keywords": (5, 8),
    },
    "ces_transformers": {
        "company_name": "CES Transformers",
        "company_domain": "cestransformers.com",
        "company_url": "https://www.cestransformers.com/",
        "location": "Markham, Ontario, Canada",
        "industry": "Distribution and power transformer design and manufacturing",
        "products": ["Teamcenter", "Simcenter", "Tecnomatix", "Opcenter"],
        "scores": {
            "opportunity": 91,
            "manufacturing": 100,
            "trigger": 94,
            "solution": 95,
            "evidence": 96,
        },
        "pain_signals": [
            "Must link customized transformer requirements, electrical and mechanical designs, simulation, testing and released production records while capacity more than triples.",
        ],
        "expansion_signals": [
            "Opened a 160,000-square-foot Markham plant, is adding more than 150 jobs and is building an NRC-funded digital-twin design platform through June 2027.",
        ],
        "challenge_summary": (
            "On January 23, 2026, CES Transformers opened a 160,000-square-foot Markham manufacturing facility that is expected to more than triple production capacity and add over 150 advanced-manufacturing jobs by 2030 after nearly C$100 million of company investment. A C$1.4 million NRC IRAP project running from January 2026 through June 2027 is integrating AI-driven electrical and mechanical design, simulation and new Haefely test equipment to cut custom-transformer development cycles from weeks to days. Inference: higher throughput across customized voltage and power configurations increases BOM and change-control, design-to-test traceability, factory-planning, work-in-process quality and release-governance pressure."
        ),
        "why_relevant": (
            "Teamcenter can connect customer specifications, electrical and mechanical product structures, released drawings, revisions and test evidence; Simcenter can support the multi-physics validation central to the funded design platform. Tecnomatix can validate the expanded plant's processes and Opcenter can control execution, inspection and serial-level quality records as output rises. The facility is already open and the funded digital-twin program is active through June 2027, so CES has a current window to establish the digital thread while new equipment, people and processes are still being integrated."
        ),
        "identity": CompanyIdentityEvidence(
            official_name="CES Transformers",
            official_website_url="https://www.cestransformers.com/",
            corroborating_urls=(
                "https://search.open.canada.ca/grants/record/nrc-cnrc%2C172-2025-2026-Q4-1038108%2Ccurrent",
                "https://www.electricity.ca/news/new-corporate-partners-january-2026/",
            ),
        ),
        "evidence": (
            {
                "signal_date": dt(2026, 1, 23),
                "source_url": "https://www.cestransformers.com/announcement/ces-transformers-opens-expanded-markham-facility-creating-150-jobs-and-strengthening-ontarios-energy-supply-chain/",
                "source_title": "CES Transformers opens expanded Markham facility, creating 150+ jobs",
                "source_publisher": "CES Transformers",
                "signal_label": "160,000-square-foot plant more than triples transformer capacity",
            },
            {
                "signal_date": dt(2026, 1, 1),
                "source_url": "https://search.open.canada.ca/grants/record/nrc-cnrc%2C172-2025-2026-Q4-1038108%2Ccurrent",
                "source_title": "Accelerated Digital Twin Enabled Transformer Design Platform",
                "source_publisher": "Government of Canada Open Government Portal",
                "signal_label": "C$1.4M digital-twin project integrates design, simulation and test",
            },
        ),
        "keywords": (5, 8, 16),
    },
    "ocean_pacific": {
        "company_name": "Ocean Pacific Marine",
        "company_domain": "oceanpacificmarine.com",
        "company_url": "https://oceanpacificmarine.com/",
        "location": "Campbell River, British Columbia, Canada",
        "industry": "Aluminum vessel design, shipbuilding and marine sustainment",
        "products": ["NX", "Teamcenter", "Polarion", "Simcenter", "Opcenter"],
        "scores": {
            "opportunity": 94,
            "manufacturing": 100,
            "trigger": 98,
            "solution": 96,
            "evidence": 97,
        },
        "pain_signals": [
            "Must control a regulated three-vessel design/build program across naval architecture, suppliers, requirements, tests and as-built configurations.",
        ],
        "expansion_signals": [
            "Won a C$74.7 million contract to design and build three RCMP coastal patrol vessels with Camarc Design and Bracewell Marine Group.",
        ],
        "challenge_summary": (
            "On July 6, 2026, Marine Log reported that Public Services and Procurement Canada awarded Ocean Pacific Marine C$74.7 million to design and construct three next-generation RCMP Police Coastal Patrol Vessels in Campbell River, British Columbia. The Camarc-designed 26.8-metre aluminum monohulls require 28-knot performance, 450-nautical-mile range, seven-day endurance and integration with fabrication partner Bracewell Marine Group and a wider supplier network. Inference: three concurrent regulated vessels create immediate BOM and change-control, requirements-to-test, supplier, welding-quality and as-built configuration pressure."
        ),
        "why_relevant": (
            "NX can support vessel and mechanical design, Teamcenter can control product structures, supplier deliverables and as-built configurations, and Polarion can trace RCMP requirements through verification and acceptance. Simcenter can support structural and performance validation, while Opcenter can preserve build, inspection and vessel genealogy. The newly awarded program is entering design and construction now, before configuration baselines and production records multiply across the three hulls."
        ),
        "identity": CompanyIdentityEvidence(
            official_name="Ocean Pacific Marine",
            official_website_url="https://oceanpacificmarine.com/",
            corroborating_urls=(
                "https://www.canada.ca/en/public-services-procurement/news/2026/06/government-of-canada-awards-contract-for-new-police-coastal-patrol-vessels-to-strengthen-security-in-british-columbia.html",
                "https://www.marinelog.com/news/ocean-pacific-marine-wins-cad-74-7m-patrol-vessel-contract/",
            ),
        ),
        "evidence": (
            {
                "signal_date": dt(2026, 7, 6),
                "source_url": "https://www.marinelog.com/news/ocean-pacific-marine-wins-cad-74-7m-patrol-vessel-contract/",
                "source_title": "Ocean Pacific Marine wins CAD 74.7M patrol vessel contract",
                "source_publisher": "Marine Log",
                "signal_label": "C$74.7M RCMP award starts three-vessel design and construction program",
            },
        ),
        "keywords": (3,),
    },
    "cota": {
        "company_name": "COTA Aviation Ltd.",
        "company_domain": "cotaaviation.com",
        "company_url": "https://www.cotaaviation.com/",
        "location": "Parksville, British Columbia, Canada",
        "industry": "Aerospace and defence component manufacturing",
        "products": ["Teamcenter", "Tecnomatix", "Opcenter"],
        "scores": {
            "opportunity": 92,
            "manufacturing": 100,
            "trigger": 94,
            "solution": 94,
            "evidence": 97,
        },
        "pain_signals": [
            "Must integrate new gear-production equipment while maintaining AS9100D configuration, process, supplier and inspection traceability.",
        ],
        "expansion_signals": [
            "Received C$1 million to install advanced equipment for aircraft and defence-system gear production in British Columbia.",
        ],
        "challenge_summary": (
            "On August 13, 2026, PacifiCan announced a C$1 million investment for COTA Aviation to purchase and install advanced equipment that will produce gears for aircraft and defence systems in British Columbia; the project was approved in early 2026 and expands domestic aerospace manufacturing capacity. COTA's official site confirms AS9100D manufacturing that includes five-axis machining, welding, finishing, component assembly and quality verification. Inference: introducing gear-production equipment into a controlled aerospace environment raises product-configuration, manufacturing-process, tooling, first-article, supplier and inspection-traceability demands."
        ),
        "why_relevant": (
            "Teamcenter can govern released gear and assembly structures, drawings, revisions and supplier records; Tecnomatix can validate the new machining and inspection process before ramp-up; Opcenter can enforce routings, non-conformance handling and lot or serial genealogy. The funded equipment is being acquired and installed now, so COTA can establish digital controls before the new production flow reaches regulated customer programs."
        ),
        "identity": CompanyIdentityEvidence(
            official_name="COTA Aviation Ltd.",
            official_website_url="https://www.cotaaviation.com/",
            corroborating_urls=(
                "https://www.canada.ca/en/pacific-economic-development/news/2026/08/backgrounder-government-of-canada-invests-over-30-million-to-help-bc-businesses-navigate-trade-disruptions-and-seize-new-opportunities.html",
                "https://www2.gov.bc.ca/gov/content/employment-business/look-west-strategy/diversifying-markets-and-growing-targeted-sectors",
            ),
        ),
        "evidence": (
            {
                "signal_date": dt(2026, 8, 13),
                "source_url": "https://www.canada.ca/en/pacific-economic-development/news/2026/08/backgrounder-government-of-canada-invests-over-30-million-to-help-bc-businesses-navigate-trade-disruptions-and-seize-new-opportunities.html",
                "source_title": "Government of Canada invests over $30 million to help B.C. businesses navigate trade disruptions",
                "source_publisher": "Pacific Economic Development Canada",
                "signal_label": "C$1M funds advanced gear-production equipment for aerospace and defence",
            },
        ),
        "keywords": (9, 10),
    },
}


COVERAGE = {
    1: (7, 5, 2, 5, ["Startup Gallery", "X.com (blocked)", "BetaKit", "NGen", "Canada.ca", "SpaceQ", "Skies", "ventureLAB", "AIAC"], "No newly formed Canadian aerospace company cleared identity and dated-trigger gates."),
    2: (9, 4, 5, 5, ["Startup Gallery", "X.com (blocked)", "BetaKit", "NGen", "Canada.ca", "Canadian Manufacturing", "ventureLAB HCI", "Automate Canada", "company hiring pages"], "TetraGen, Sanctuary AI and other physical-robotics results were existing identities; software and directory-only leads were rejected."),
    3: (7, 4, 3, 4, ["Startup Gallery", "X.com (blocked)", "BetaKit", "NGen", "Canada.ca", "Marine Log", "Ocean Supercluster", "Shipbuilding Association of Canada"], "Ocean Pacific Marine was reassessed with a new independent source; software suppliers and foreign yards were rejected."),
    4: (7, 4, 3, 4, ["Startup Gallery", "X.com (blocked)", "BetaKit", "NGen", "Canada.ca", "Electric Autonomy Canada", "APMA", "OVIN"], "Hanon Systems is an established component supplier rather than a Canadian automotive startup or OEM; no new company passed."),
    5: (11, 7, 2, 7, ["Startup Gallery", "X.com (blocked)", "BetaKit", "NGen", "Canada.ca", "PLANT", "Canadian Mining Journal", "Canada Growth Fund", "BDC"], "EnerPure and CES Transformers passed; other energy and battery results were existing, service-led or lacked a current verified trigger."),
    7: (8, 5, 3, 5, ["Startup Gallery", "X.com (blocked)", "BetaKit", "NGen", "Canada.ca", "SpaceQ", "Skies", "AIAC", "Aero Montreal"], "SpaceQ and AIAC were checked directly; named Canadian aircraft and drone companies were existing identities or lacked a publishable new trigger."),
    8: (10, 5, 3, 6, ["Startup Gallery", "X.com (blocked)", "BetaKit", "NGen", "Canada.ca", "ventureLAB HCI", "MaRS", "Communitech", "BDC Capital"], "EnerPure and CES Transformers passed the funding-plus-hardware gate; software, investor-list and cohort-only leads were rejected."),
    9: (11, 5, 5, 5, ["Startup Gallery", "X.com (blocked)", "BetaKit", "NGen", "Canada.ca", "SpaceQ", "Skies", "AIAC", "DAIR Aerospace", "Aero Montreal"], "COTA Aviation received a current verified manufacturing-capacity refresh; directories were discovery-only."),
    10: (12, 6, 5, 6, ["Startup Gallery", "X.com (blocked)", "BetaKit", "NGen", "Canada.ca", "SpaceQ", "AIAC 2026 Guide", "CADSI/CANSEC", "Canadian Metalworking", "company hiring pages"], "COTA Aviation's new gear-production funding refreshed its existing qualified record; unnamed and service-only results were rejected."),
    11: (7, 5, 2, 4, ["Startup Gallery", "X.com (blocked)", "BetaKit", "NGen", "Canada.ca", "Electric Autonomy Canada", "APMA", "OVIN", "OEM hiring pages"], "Honda and Ford hiring were existing large OEM signals; Hanon is a supplier, not an OEM, and no new manufacturer passed."),
    12: (6, 5, 1, 5, ["Startup Gallery", "X.com (blocked)", "BetaKit", "NGen", "Canadian Manufacturers & Exporters", "PLANT", "company hiring pages", "Oakville Chamber"], "Anonymous recruiter roles, consultants and software vendors were rejected; no identifiable end-client ERP/PLM integration trigger passed."),
    13: (9, 5, 4, 5, ["Startup Gallery", "X.com (blocked)", "BetaKit", "NGen", "Canada.ca", "SpaceQ", "AIAC", "CanadaBuys", "OVIN"], "Calogy, Jaunt, Volatus and North Vector were existing identities; job-only startup leads lacked independent identity and contract evidence."),
    14: (10, 5, 5, 5, ["Startup Gallery", "X.com (blocked)", "BetaKit", "NGen", "Canada.ca", "CanadaBuys", "SpaceQ", "AIAC", "CADSI/CANSEC"], "Sentinel, Dominion Dynamics and North Vector were existing identities; generic procurement notices and directory entries did not qualify a new company."),
    15: (8, 5, 3, 5, ["Startup Gallery", "X.com (blocked)", "BetaKit", "NGen", "Canada.ca", "Electric Autonomy Canada", "APMA", "OVIN", "French Quebec funding searches"], "Mangrove, Calogy and other EV-technology results were existing; Hanon, Grin and Volta did not match the Canadian EV-startup gate."),
    16: (7, 5, 1, 5, ["Startup Gallery", "X.com (blocked)", "BetaKit", "NGen digital-twin reports", "Canada Open Government grants", "manufacturer hiring pages", "French Quebec PLM/MES searches", "CME"], "CES Transformers passed on a funded digital-twin design platform and live factory expansion; Bombardier was an existing identity and anonymous or service-led PLM results were rejected."),
}


def make_signal(prospect: dict[str, object], evidence: dict[str, object]) -> ExtractedSignal:
    scores = prospect["scores"]
    return ExtractedSignal(
        company_name=str(prospect["company_name"]),
        company_domain=str(prospect["company_domain"]),
        company_url=str(prospect["company_url"]),
        location=str(prospect["location"]),
        industry=str(prospect["industry"]),
        company_industry=str(prospect["industry"]),
        software=list(prospect["products"]),
        signal_type="news",
        signal_source="news",
        pain_signals=list(prospect["pain_signals"]),
        expansion_signals=list(prospect["expansion_signals"]),
        raw_score=int(scores["opportunity"]),
        confidence=int(scores["evidence"]) / 100,
        reason=str(prospect["challenge_summary"]),
        source_url=str(evidence["source_url"]),
        source_title=str(evidence["source_title"]),
        detected_at=evidence["signal_date"],
    )


def record_link(database: Database, keyword_id: int, prospect: dict[str, object]):
    evidence = prospect["evidence"][0]
    scores = prospect["scores"]
    row = database.record_keyword_company(
        keyword_id,
        str(prospect["company_name"]),
        str(prospect["company_domain"]),
        source_url=str(evidence["source_url"]),
        source_title=str(evidence["source_title"]),
        source_publisher=str(evidence["source_publisher"]),
        signal_label=str(evidence["signal_label"]),
        signal_date=evidence["signal_date"],
        challenge_summary=str(prospect["challenge_summary"]),
        why_relevant=str(prospect["why_relevant"]),
        recommended_products=list(prospect["products"]),
        qualification_status="qualified",
        opportunity_score=int(scores["opportunity"]),
        manufacturing_fit_score=int(scores["manufacturing"]),
        trigger_score=int(scores["trigger"]),
        solution_fit_score=int(scores["solution"]),
        evidence_quality_score=int(scores["evidence"]),
        seen_at=RUN_AT,
    )
    if row is None:
        raise RuntimeError(f"Could not link {prospect['company_name']} to keyword {keyword_id}")
    return row


def main() -> None:
    load_dotenv(".env")
    database = Database(os.environ["DATABASE_URL"])
    database.initialize()
    before = {row.id: row for row in database.list_keywords()}
    if set(before) != set(COVERAGE):
        raise RuntimeError(f"Persistent keyword set changed: {sorted(before)}")

    prior_domains = {lead.company_domain for lead in database.get_leads(limit=5000)}
    signals = []
    links = []
    published = {keyword_id: 0 for keyword_id in before}
    new_company_domains = set()

    for prospect in PROSPECTS.values():
        is_new_company = prospect["company_domain"] not in prior_domains
        for evidence in prospect["evidence"]:
            saved, company = database.persist_verified_signal(
                make_signal(prospect, evidence), prospect["identity"]
            )
            signals.append(
                {
                    "company_id": company.id if hasattr(company, "id") else None,
                    "company": company.company_name,
                    "domain": company.company_domain,
                    "source_url": str(evidence["source_url"]),
                    "created": saved.created,
                    "duplicate_url": saved.duplicate_url,
                    "signal_count": company.signal_count,
                }
            )
        if is_new_company:
            new_company_domains.add(str(prospect["company_domain"]))
        for keyword_id in prospect["keywords"]:
            row = record_link(database, keyword_id, prospect)
            published[keyword_id] += 1
            links.append(
                {
                    "keyword_id": keyword_id,
                    "company_id": row.company_id,
                    "company": row.company_name,
                    "domain": row.company_domain,
                }
            )

    for keyword_id in sorted(before):
        if database.record_keyword_search(keyword_id, result_count=published[keyword_id]) is None:
            raise RuntimeError(f"Could not record keyword search {keyword_id}")

    after = {row.id: row for row in database.list_keywords()}
    report = {}
    for keyword_id, (reviewed, rejected, duplicates, new_domains, sources, notes) in COVERAGE.items():
        if after[keyword_id].search_count != before[keyword_id].search_count + 1:
            raise RuntimeError(f"Keyword {keyword_id} did not advance exactly once")
        report[keyword_id] = {
            "keyword": before[keyword_id].keyword,
            "lookback": "rolling 30 days, 180-day evidence fallback and 365-day ongoing discovery fallback",
            "query_families": 6,
            "candidate_domains_reviewed": reviewed,
            "new_to_ledger_domains_reviewed": new_domains,
            "rejected_before_persistence": rejected,
            "qualified_published": published[keyword_id],
            "watchlist_published": 0,
            "existing_records_upgraded_or_hidden": 1 if keyword_id in {3, 9, 10} else 0,
            "duplicates_skipped_or_reassessed": duplicates,
            "sources_checked": sources,
            "notes": notes,
        }

    print(
        json.dumps(
            {
                "run_at": RUN_AT.isoformat(),
                "new_company_domains": sorted(new_company_domains),
                "signals": signals,
                "links": links,
                "coverage": report,
                "blockers": [
                    "X.com was inaccessible through the in-app Browser because of ERR_CERT_AUTHORITY_INVALID and URL policy blocking.",
                    "Google presented an unusual-traffic reCAPTCHA during keyword 10; it was not bypassed, and source-specific searches continued through the web research fallback.",
                    "The 15-domain breadth quota was not met for any individual keyword because accessible named-company results were exhausted; exact actual counts are reported without inventing candidates.",
                ],
            },
            indent=2,
            default=str,
        )
    )


if __name__ == "__main__":
    main()
