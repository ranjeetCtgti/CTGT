from __future__ import annotations

import json
import os
from datetime import datetime, timezone

from dotenv import load_dotenv

from db.database import Database
from enrichment.identity_verification import CompanyIdentityEvidence
from models.schema import ExtractedSignal


RUN_AT = datetime.now(timezone.utc)


def dt(month: int, day: int) -> datetime:
    return datetime(2026, month, day, tzinfo=timezone.utc)


def identity(name: str, website: str, *corroboration: str) -> CompanyIdentityEvidence:
    return CompanyIdentityEvidence(
        official_name=name,
        official_website_url=website,
        corroborating_urls=tuple(corroboration),
    )


PROSPECTS = {
    "landing_zones": {
        "company_name": "Landing Zones Canada",
        "company_domain": "landingzones.com",
        "company_url": "https://landingzones.com/",
        "location": "Medicine Hat, Alberta, Canada",
        "industry": "Defence and space manufacturing; advanced uncrewed aircraft systems",
        "products": ["Teamcenter", "Polarion", "Simcenter", "Capital", "Opcenter"],
        "scores": (94, 98, 95, 96, 98),
        "pain_signals": [
            "Must control UAS configurations, electrical interfaces, mission requirements, simulation evidence and manufacturing scale-up across Alberta and Ontario."
        ],
        "expansion_signals": [
            "Airbus invested and took a board seat after BDC's StrongNorth fund backed commercialization and manufacturing of the Gitpo stratospheric RPAS."
        ],
        "challenge_summary": (
            "On July 22, 2026, Airbus Defence and Space invested in Medicine Hat-based Landing Zones Canada, took a board seat and formed a strategic partnership to expand advanced UAS simulation and training services in Canada; BDC's first StrongNorth investment, announced April 20, is separately funding manufacturing and commercialization of the Gitpo stratospheric remotely piloted aircraft across Alberta and Ontario. The programs combine threat-emulation aircraft, large-scale battlefield scenarios, aerospace engineering and a multi-site scale-up. Inference: more vehicle variants, electrical and mission interfaces, controlled defence requirements, verification evidence and production records create immediate configuration, test-traceability and manufacturing-governance pressure."
        ),
        "why_relevant": (
            "Teamcenter can govern vehicle structures, variants, released configurations and supplier changes; Polarion can trace defence requirements through simulation, flight test and defects. Simcenter is defensible for flight, structural and thermal validation, Capital for electrical architecture, and Opcenter for controlled build and quality genealogy as manufacturing scales. The Airbus partnership and BDC-backed commercialization are active now, before shared baselines and production records multiply."
        ),
        "identity": identity(
            "Landing Zones Canada",
            "https://landingzones.com/",
            "https://www.airbus.com/en/newsroom/press-releases/2026-07-airbus-and-landing-zones-sign-strategic-partnership-for-advanced-uas-in-canada",
            "https://www.bdc.ca/en/about/mediaroom/news-releases/landing-zones-canada-secures-first-investment-from-bdc-new-strongnorth-defence-fund",
        ),
        "evidence": (
            (dt(7, 22), "https://www.airbus.com/en/newsroom/press-releases/2026-07-airbus-and-landing-zones-sign-strategic-partnership-for-advanced-uas-in-canada", "Airbus and Landing Zones sign strategic partnership for advanced UAS in Canada", "Airbus", "Airbus investment and board seat expand Canadian advanced-UAS programs"),
            (dt(4, 20), "https://www.bdc.ca/en/about/mediaroom/news-releases/landing-zones-canada-secures-first-investment-from-bdc-new-strongnorth-defence-fund", "Landing Zones Canada secures first investment from BDC's new StrongNorth Defence fund", "Business Development Bank of Canada", "StrongNorth backs Gitpo manufacturing and commercialization across two provinces"),
        ),
        "keywords": (7, 8, 14),
    },
    "relocalize": {
        "company_name": "Relocalize",
        "company_domain": "relocalize.com",
        "company_url": "https://www.relocalize.com/",
        "location": "Montreal, Quebec, Canada",
        "industry": "Autonomous modular food and cold-chain microfactory manufacturing",
        "products": ["Teamcenter", "Tecnomatix", "Opcenter", "Simcenter"],
        "scores": (92, 98, 96, 96, 97),
        "pain_signals": [
            "Must industrialize a five-robot dark microfactory design and repeat it across a planned multi-site deployment while controlling equipment, process, quality and cold-chain performance."
        ],
        "expansion_signals": [
            "Started construction of Canada's first autonomous dark factory after a C$7 million seed extension and a deployment-capital agreement of up to C$22.5 million."
        ],
        "challenge_summary": (
            "On April 1, 2026, Relocalize began construction of Canada's first autonomous dark factory in Montreal, moving its five-robot cold-pack microfactory from pilot operation to commercial scale under a signed supply agreement. The company closed a C$7-million seed extension and secured deployment capital of up to C$22.5 million for a planned network of commercial microfactories. Inference: repeating a containerized factory across customers creates equipment and recipe configuration, robotic-line validation, change control, commissioning, cold-chain quality and production-visibility pressure."
        ),
        "why_relevant": (
            "Teamcenter can govern the reusable microfactory product structure, equipment revisions and site-specific configurations; Tecnomatix can validate robot cells, flow and throughput before each deployment. Opcenter can manage recipes, execution, quality and genealogy, while Simcenter can validate thermal and process performance for cold-chain products. Construction and commercial deployment are underway now, so the digital baseline should be established before the first factory is cloned into a larger network."
        ),
        "identity": identity(
            "Relocalize",
            "https://www.relocalize.com/",
            "https://betakit.com/relocalize-to-build-fully-autonomous-dark-microfactory-in-montreal/",
            "https://www.cfin-rcia.ca/blogs/community-manager/2026/03/04/program-impact-food-manufacturing-tech",
        ),
        "evidence": (
            (dt(4, 1), "https://www.relocalize.com/blog/montreal-startup-launches-construction-of-canadas-first-autonomous-dark-factory", "Montreal startup launches construction of Canada's first autonomous dark factory", "Relocalize", "Construction starts on commercial five-robot dark microfactory"),
            (dt(4, 1), "https://betakit.com/relocalize-to-build-fully-autonomous-dark-microfactory-in-montreal/", "Relocalize to build fully autonomous dark microfactory in Montreal", "BetaKit", "C$7M seed extension supports autonomous microfactory commercialization"),
        ),
        "keywords": (8,),
    },
    "xanadu": {
        "company_name": "Xanadu Quantum Technologies Inc.",
        "company_domain": "xanadu.ai",
        "company_url": "https://www.xanadu.ai/",
        "location": "Toronto, Ontario, Canada",
        "industry": "Photonic quantum-computing hardware and advanced quantum manufacturing",
        "products": ["Teamcenter", "Polarion", "Simcenter", "Tecnomatix", "HPCWorks"],
        "scores": (97, 99, 100, 98, 99),
        "pain_signals": [
            "Must qualify and scale photonic packaging, heterogeneous integration, wafer-level test and module assembly from chip through complete quantum systems."
        ],
        "expansion_signals": [
            "Secured a C$195 million federal investment within the C$893 million Project OPTIMISM advanced-manufacturing program, expected to create 275 jobs."
        ],
        "challenge_summary": (
            "On August 28, 2026, Canada committed C$195 million through the Strategic Response Fund toward Xanadu's C$893-million Project OPTIMISM, which will establish advanced photonic packaging, heterogeneous integration, wafer-level testing and quantum-module assembly in Canada and create 275 jobs. The program is intended to vertically integrate photonic and semiconductor components from chip through fault-tolerant quantum systems. Inference: qualifying new processes across precision hardware, suppliers, requirements, test data and rapidly changing system configurations creates exceptional product-lifecycle, verification, factory-planning and simulation-compute complexity."
        ),
        "why_relevant": (
            "Teamcenter can control chip-to-system structures, revisions, supplier data and process qualifications; Polarion can trace fault-tolerance and performance requirements through test evidence and defects. Simcenter and HPCWorks can support thermal, electromagnetic and large-scale engineering workloads, while Tecnomatix can validate new assembly and test flows. The federal agreement is signed and the C$893-million manufacturing build-out is beginning now, making the architecture and governance window immediate."
        ),
        "identity": identity(
            "Xanadu Quantum Technologies Inc.",
            "https://www.xanadu.ai/",
            "https://www.canada.ca/en/innovation-science-economic-development/news/2026/08/government-of-canada-invests-in-xanadu-to-build-up-advanced-quantum-manufacturing-in-canada.html",
        ),
        "evidence": (
            (dt(8, 28), "https://www.canada.ca/en/innovation-science-economic-development/news/2026/08/government-of-canada-invests-in-xanadu-to-build-up-advanced-quantum-manufacturing-in-canada.html", "Government of Canada invests in Xanadu to build up advanced quantum manufacturing in Canada", "Innovation, Science and Economic Development Canada", "C$195M federal investment launches C$893M quantum-manufacturing program"),
            (dt(8, 28), "https://investors.xanadu.ai/news-releases/news-release-details/government-canada-invests-cad-195-million-xanadu-build-quantum", "Government of Canada invests C$195 million in Xanadu to build quantum manufacturing", "Xanadu", "Project OPTIMISM vertically integrates photonic quantum hardware production"),
        ),
        "keywords": (8,),
    },
    "nordspace": {
        "company_name": "NordSpace",
        "company_domain": "nordspace.com",
        "company_url": "https://www.nordspace.com/",
        "location": "Markham, Ontario and St. Lawrence, Newfoundland and Labrador, Canada",
        "industry": "Space launch vehicles, rocket propulsion and spaceport manufacturing",
        "products": ["NX", "Teamcenter", "Polarion", "Simcenter", "Tecnomatix", "Capital"],
        "scores": (97, 100, 99, 98, 99),
        "pain_signals": [
            "Must coordinate launch-vehicle, engine, spaceport, supplier, certification and test configurations while commercial and defence programs scale across provinces."
        ],
        "expansion_signals": [
            "Committed C$5 million within a C$10 million Atlantic Spaceport Complex investment and received a conditional C$8.3 million National Defence commitment."
        ],
        "challenge_summary": (
            "On August 27, 2026, federal and Newfoundland and Labrador governments announced a C$10-million Atlantic Spaceport Complex investment in St. Lawrence: C$1 million federal, C$4 million provincial and C$5 million from NordSpace, alongside a conditional C$8.3-million National Defence commitment over three years. The facility supports NordSpace's Tundra orbital launch vehicle, commercial launches and a supply chain expected to create 30 jobs by 2028 and more than 200 by 2035. Inference: integrating launch vehicle, propulsion, ground infrastructure, suppliers and defence requirements creates urgent configuration, simulation, verification and factory/launch-process planning needs."
        ),
        "why_relevant": (
            "NX and Teamcenter can control the multidisciplinary launch-vehicle and ground-system definition, variants, suppliers and released changes; Polarion can connect mission and defence requirements to test evidence. Simcenter and Capital support propulsion, structural, thermal and electrical validation, while Tecnomatix can plan manufacturing and spaceport processes. Construction and funded program execution are active, so a controlled digital thread is needed before hardware, facilities and compliance records expand."
        ),
        "identity": identity(
            "NordSpace",
            "https://www.nordspace.com/",
            "https://www.canada.ca/en/atlantic-canada-opportunities/news/2026/08/10m-investment-advances-canadas-sovereign-space-launch-capacity-in-newfoundland-and-labrador.html",
        ),
        "evidence": (
            (dt(8, 27), "https://www.canada.ca/en/atlantic-canada-opportunities/news/2026/08/10m-investment-advances-canadas-sovereign-space-launch-capacity-in-newfoundland-and-labrador.html", "C$10M investment advances Canada's sovereign space-launch capacity in Newfoundland and Labrador", "Atlantic Canada Opportunities Agency", "C$10M spaceport program and C$8.3M defence commitment expand sovereign launch capacity"),
        ),
        "keywords": (8, 9, 14),
    },
    "volatus": {
        "company_name": "Volatus Aerospace Inc.",
        "company_domain": "volatusaerospace.com",
        "company_url": "https://volatusaerospace.com/",
        "location": "Mirabel, Quebec, Canada",
        "industry": "Uncrewed aircraft manufacturing, systems integration and aerial intelligence",
        "products": ["Teamcenter", "Polarion", "Simcenter", "Capital", "Opcenter"],
        "scores": (96, 99, 98, 98, 98),
        "pain_signals": [
            "Must ramp a 53,000-square-foot manufacturing and integration facility while localizing multiple autonomous aircraft platforms and defence configurations."
        ],
        "expansion_signals": [
            "Opened its Mirabel facility, began production ramp and reported C$59.2 million cash with 49.5% sequential revenue growth in Q2 2026."
        ],
        "challenge_summary": (
            "On August 13, 2026, Volatus reported that its 53,000-square-foot Mirabel manufacturing and systems-integration facility was open and production was ramping, while Q2 revenue rose 49.5% sequentially and cash reached C$59.2 million. The quarter also added Canadian localization programs for Kraus Hamdani's K1000ULE/ATNE++ and Singular's FlyOx heavy-lift autonomous aircraft. Inference: multiple airframes, payloads, defence requirements, suppliers, certifications and locally manufactured configurations increase BOM/change-control, test-traceability, electrical-interface and shop-floor quality pressure."
        ),
        "why_relevant": (
            "Teamcenter can govern localized aircraft structures, payload interfaces, suppliers and released configurations; Polarion can trace mission and certification requirements through test results and defects. Simcenter and Capital support multidisciplinary and electrical validation, while Opcenter can control execution and serial genealogy in Mirabel. Production is ramping now and new platform partnerships are entering the facility, so configuration and manufacturing governance are urgent."
        ),
        "identity": identity(
            "Volatus Aerospace Inc.",
            "https://volatusaerospace.com/",
            "https://www.globenewswire.com/news-release/2026/08/13/3345013/0/en/volatus-aerospace-releases-q2-2026-financial-results.html",
        ),
        "evidence": (
            (dt(8, 13), "https://volatusaerospace.com/insights/releases-q2-2026-financial-results/", "Volatus Aerospace releases Q2 2026 financial results", "Volatus Aerospace", "Mirabel manufacturing facility opens and production ramp begins"),
        ),
        "keywords": (7, 9, 13, 14),
    },
    "general_motors_canada": {
        "company_name": "General Motors Canada",
        "company_domain": "gm.ca",
        "company_url": "https://www.gm.ca/",
        "location": "Oshawa, Ontario, Canada",
        "industry": "Automotive vehicle engineering and manufacturing",
        "products": ["Teamcenter", "Tecnomatix", "Opcenter", "Simcenter", "Capital"],
        "scores": (95, 100, 98, 97, 98),
        "pain_signals": [
            "Must introduce the next-generation GMC Sierra heavy-duty platform into Oshawa while coordinating vehicle variants, suppliers, tooling, quality and electrical systems."
        ],
        "expansion_signals": [
            "Committed an additional C$144 million at Oshawa within a three-year Canadian investment program exceeding C$1 billion."
        ],
        "challenge_summary": (
            "On August 30, 2026, General Motors Canada announced an additional C$144-million investment to add next-generation GMC Sierra heavy-duty production at Oshawa Assembly, on top of a prior C$343-million commitment for next-generation truck manufacturing and wider three-year Canadian investments exceeding C$1 billion. The program is tied to a new labour agreement and preserves large-scale vehicle engineering and manufacturing operations in Ontario. Inference: introducing a new heavy-duty truck generation across variants, tooling, suppliers and an active plant creates immediate product-configuration, line-planning, quality-traceability and production-ramp complexity."
        ),
        "why_relevant": (
            "Teamcenter can govern vehicle structures, options, supplier changes and plant releases; Tecnomatix can validate tooling, stations and throughput before launch. Opcenter can control execution and quality genealogy, while Simcenter and Capital support vehicle and electrical-system validation. The investment and labour agreement were just announced and next-generation production planning is starting now, creating the pre-ramp window for process and configuration controls."
        ),
        "identity": identity(
            "General Motors Canada",
            "https://www.gm.ca/en/home.html",
            "https://www.upi.com/Top_News/World-News/2026/08/30/canada-ontario-general-motors-labor-union/2381788139559/",
        ),
        "evidence": (
            (dt(8, 30), "https://news.gm.ca/en/home.detail.html/Pages/news/ca/en/2026/aug/0830_gm-canada-community-update-investing-people-industry.html", "GM Canada community update: investing in people and industry", "General Motors Canada", "Additional C$144M starts next-generation Sierra HD production program in Oshawa"),
            (dt(8, 30), "https://www.upi.com/Top_News/World-News/2026/08/30/canada-ontario-general-motors-labor-union/2381788139559/", "GM Canada workers ratify three-year agreement with major plant investment", "UPI", "Independent report corroborates billion-dollar Canadian manufacturing program"),
        ),
        "keywords": (11,),
    },
}


COVERAGE = {
    1: (14, 7, 9, 5, ["Startup Gallery", "X public search", "BetaKit", "NGen", "Canada.ca", "SpaceQ", "AIAC", "Skies", "ventureLAB HCI"], "No company formed within the last month had both verified physical-product operations and a publishable dated trigger."),
    2: (15, 8, 7, 6, ["Startup Gallery", "X public search", "BetaKit", "NGen", "Canada.ca", "ventureLAB HCI", "Automate Canada", "company hiring pages"], "TetraGen, Vention, Xaba and other robotics results were existing; software-only and directory-only candidates failed the gate."),
    3: (11, 6, 5, 4, ["Startup Gallery", "X public search", "BetaKit", "NGen", "Canada.ca", "Marine Log", "Ocean Supercluster", "Shipbuilding Association of Canada"], "Confined Space Robotics is not a shipbuilder; SSI-like software suppliers and undated yards were rejected."),
    4: (13, 7, 6, 5, ["Startup Gallery", "X public search", "BetaKit", "NGen", "Canada.ca", "Electric Autonomy Canada", "APMA", "OVIN", "ventureLAB HCI"], "Hanon Systems is an established foreign-headquartered supplier rather than a Canadian automotive startup/OEM; Autonomique is software-led."),
    5: (12, 7, 5, 5, ["Startup Gallery", "X public search", "BetaKit", "NGen", "Canada.ca", "PLANT", "Canadian Manufacturing", "BDC", "federal energy funding"], "Atlas Engineered Products is a building-products manufacturer, not an energy company; other results were existing or lacked a current trigger."),
    7: (16, 7, 9, 6, ["Startup Gallery", "X public search", "BetaKit", "NGen", "Canada.ca", "SpaceQ", "AIAC", "Skies", "Aero Montreal"], "Landing Zones and Volatus passed; directory-only aerospace profiles did not."),
    8: (18, 9, 9, 8, ["Startup Gallery", "X public search", "BetaKit", "NGen", "Canada.ca", "BDC", "ventureLAB HCI", "MaRS", "Communitech", "investor portfolios"], "Relocalize and Xanadu were new; Landing Zones and NordSpace were reassessed with fresh funding/manufacturing evidence."),
    9: (16, 7, 9, 6, ["Startup Gallery", "X public search", "BetaKit", "NGen", "Canada.ca", "SpaceQ", "AIAC", "Skies", "DAIR Aerospace", "Aero Montreal"], "NordSpace and Volatus received new evidence; member-directory entries remained discovery-only."),
    10: (13, 7, 6, 5, ["Startup Gallery", "X public search", "BetaKit", "NGen", "Canada.ca", "AIAC", "CADSI/CANSEC", "Canadian Metalworking"], "No new Tier 1/Tier 2 aerospace manufacturer supplied current identity and trigger evidence; Canadian Metalworking was access-limited."),
    11: (12, 6, 6, 5, ["Startup Gallery", "X public search", "BetaKit", "NGen", "Canada.ca", "Electric Autonomy Canada", "APMA", "OVIN", "OEM press pages"], "General Motors Canada passed on the new Oshawa investment; suppliers and foreign OEM news were rejected."),
    12: (10, 6, 4, 4, ["Startup Gallery", "X public search", "BetaKit", "NGen", "CanadaBuys", "PLANT", "manufacturer hiring pages", "CME"], "Eclipse Automation's existing database identity conflicts with a news-domain value; it was blocked from updates pending independent identity reconciliation."),
    13: (16, 8, 8, 6, ["Startup Gallery", "X public search", "BetaKit", "NGen", "Canada.ca", "SpaceQ", "AIAC", "CanadaBuys", "OVIN"], "Volatus received fresh production-ramp evidence; Calogy and Landing Zones were existing qualified identities."),
    14: (17, 8, 9, 7, ["Startup Gallery", "X public search", "BetaKit", "NGen", "Canada.ca", "CanadaBuys", "SpaceQ", "AIAC", "CADSI/CANSEC"], "Landing Zones, NordSpace and Volatus passed; generic procurement notices and unverified exhibitor entries did not."),
    15: (13, 7, 6, 5, ["Startup Gallery", "X public search", "BetaKit", "NGen", "Canada.ca", "Electric Autonomy Canada", "APMA", "OVIN", "French Quebec searches"], "Calogy was already qualified through relevant hardware keywords; Hanon, Grin and other suppliers did not match the Canadian EV-startup gate."),
    16: (11, 7, 4, 4, ["Startup Gallery", "X public search", "BetaKit", "NGen digital-twin reports", "Canada.ca", "manufacturer hiring pages", "French Quebec PLM/MES searches", "CME"], "Pratt & Whitney and GE Vernova roles confirmed active PLM complexity but were job-only or existing large-company leads; no new named end-client cleared the gate."),
}


def make_signal(prospect: dict[str, object], evidence: tuple[object, ...]) -> ExtractedSignal:
    opportunity, _manufacturing, _trigger, _solution, evidence_score = prospect["scores"]
    signal_date, source_url, source_title, _publisher, _label = evidence
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
        raw_score=int(opportunity),
        confidence=int(evidence_score) / 100,
        reason=str(prospect["challenge_summary"]),
        source_url=str(source_url),
        source_title=str(source_title),
        detected_at=signal_date,
    )


def record_link(database: Database, keyword_id: int, prospect: dict[str, object]):
    signal_date, source_url, source_title, publisher, label = prospect["evidence"][0]
    opportunity, manufacturing, trigger, solution, evidence = prospect["scores"]
    row = database.record_keyword_company(
        keyword_id,
        str(prospect["company_name"]),
        str(prospect["company_domain"]),
        source_url=str(source_url),
        source_title=str(source_title),
        source_publisher=str(publisher),
        signal_label=str(label),
        signal_date=signal_date,
        challenge_summary=str(prospect["challenge_summary"]),
        why_relevant=str(prospect["why_relevant"]),
        recommended_products=list(prospect["products"]),
        qualification_status="qualified",
        opportunity_score=int(opportunity),
        manufacturing_fit_score=int(manufacturing),
        trigger_score=int(trigger),
        solution_fit_score=int(solution),
        evidence_quality_score=int(evidence),
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
    published = {keyword_id: 0 for keyword_id in before}
    new_company_domains: set[str] = set()
    signal_report = []
    link_report = []

    for prospect in PROSPECTS.values():
        domain = str(prospect["company_domain"])
        if domain not in prior_domains:
            new_company_domains.add(domain)
        for evidence in prospect["evidence"]:
            saved, company = database.persist_verified_signal(
                make_signal(prospect, evidence), prospect["identity"]
            )
            signal_report.append(
                {
                    "company": company.company_name,
                    "domain": company.company_domain,
                    "source_url": str(evidence[1]),
                    "created": saved.created,
                    "duplicate_url": saved.duplicate_url,
                    "signal_count": company.signal_count,
                }
            )
        for keyword_id in prospect["keywords"]:
            row = record_link(database, keyword_id, prospect)
            published[keyword_id] += 1
            link_report.append({"keyword_id": keyword_id, "company_id": row.company_id, "company": row.company_name})

    for keyword_id in sorted(before):
        if database.record_keyword_search(keyword_id, result_count=published[keyword_id]) is None:
            raise RuntimeError(f"Could not record keyword search {keyword_id}")

    after = {row.id: row for row in database.list_keywords()}
    coverage_report = {}
    upgraded_keywords = {7, 8, 9, 13, 14}
    for keyword_id, (reviewed, rejected, duplicates, new_domains, sources, notes) in COVERAGE.items():
        if after[keyword_id].search_count != before[keyword_id].search_count + 1:
            raise RuntimeError(f"Keyword {keyword_id} did not advance exactly once")
        coverage_report[keyword_id] = {
            "keyword": before[keyword_id].keyword,
            "lookback": "rolling 30 days, 180-day evidence fallback, 365-day ongoing discovery fallback",
            "query_families": 6,
            "candidate_domains_reviewed": reviewed,
            "new_to_ledger_domains_reviewed": new_domains,
            "rejected_before_persistence": rejected,
            "qualified_published": published[keyword_id],
            "watchlist_published": 0,
            "existing_records_upgraded_or_hidden": 1 if keyword_id in upgraded_keywords else 0,
            "duplicates_skipped_or_reassessed": duplicates,
            "sources_checked": sources,
            "notes": notes,
        }

    print(json.dumps({
        "run_at": RUN_AT.isoformat(),
        "new_company_domains": sorted(new_company_domains),
        "signals": signal_report,
        "links": link_report,
        "coverage": coverage_report,
        "blockers": [
            "Direct X.com navigation failed with ERR_CERT_AUTHORITY_INVALID; public X-ray search was completed for every keyword and produced zero relevant candidates for several narrow terms.",
            "Startup Gallery was accessible, but direct per-keyword checks produced zero relevant candidates for the narrow enterprise/defence terms reported in coverage.",
            "Google presented two unusual-traffic challenges; the user solved both normally, and focused fallback searches covered affected source families without bypassing safeguards.",
            "The 15-domain breadth quota was not met for several narrow keywords after accessible named-company sources were exhausted; actual counts are reported without padding.",
            "Eclipse Automation has an existing canonical-domain mismatch in PostgreSQL and was not modified.",
        ],
    }, indent=2, default=str))


if __name__ == "__main__":
    main()
