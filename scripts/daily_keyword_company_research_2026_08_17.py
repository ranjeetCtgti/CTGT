from __future__ import annotations

import json
from datetime import datetime, timezone

from dotenv import load_dotenv

from db.database import Database
from models.schema import ExtractedSignal


RUN_AT = datetime.now(timezone.utc)


def dt(year: int, month: int, day: int) -> datetime:
    return datetime(year, month, day, tzinfo=timezone.utc)


NEW_CANDIDATES = [
    {
        "keyword_ids": [11],
        "company_name": "Roshel Smart Armored Vehicles",
        "company_domain": "roshel.com",
        "company_url": "https://roshel.com/",
        "linkedin_url": "https://ca.linkedin.com/company/roshel",
        "location": "Brampton, Ontario, Canada",
        "industry": "Armoured and special-purpose vehicle manufacturing",
        "products": ["Teamcenter", "Polarion", "Tecnomatix", "Opcenter"],
        "scores": {
            "opportunity": 91,
            "manufacturing": 99,
            "trigger": 91,
            "solution": 94,
            "evidence": 94,
        },
        "pain_signals": [
            "Must industrialize multiple modular armoured-vehicle variants while preserving ballistic, blast, mobility and customer-specific configuration evidence.",
            "Has outgrown 400,000 square feet of manufacturing and R&D space while pursuing a Canadian defence program reported at up to $6 billion.",
        ],
        "expansion_signals": [
            "Unveiled five new Canadian-developed defence vehicle platforms and variants at CANSEC 2026.",
            "Reportedly needs additional capacity beyond its existing 400,000-square-foot Brampton operation and could add thousands of jobs if the pending program is awarded.",
        ],
        "evidence": [
            {
                "signal_date": dt(2026, 7, 23),
                "source_url": "https://toronto.citynews.ca/2026/07/23/thousands-of-jobs-billions-of-dollars-on-the-line-in-brampton-defence-companys-bid-to-expand/",
                "source_title": "Thousands of jobs, billions of dollars on the line in Brampton defence company's bid to expand",
                "source_publisher": "CityNews Toronto",
                "signal_label": "Roshel has outgrown 400,000 sq. ft. while pursuing a defence program worth up to $6B",
                "challenge_summary": (
                    "On July 23, 2026, CityNews reported that Brampton armoured-vehicle manufacturer Roshel had already outgrown 400,000 square feet of manufacturing and R&D space while preparing a bid for a Canadian defence program expected to be worth up to $6 billion; its CEO said a win could support thousands of jobs and a much larger domestic industrial footprint. Roshel's official site confirms that it designs and manufactures vehicles in-house at a vertically integrated Ontario operation with capacity stated at 140 units per month. Inference: a capacity expansion tied to configurable, certified military vehicles would sharply increase product-variant, supplier, engineering-change, factory-planning, quality-genealogy and production-scheduling pressure."
                ),
                "why_relevant": (
                    "Teamcenter can govern customer-specific vehicle configurations, approved parts, engineering changes and supplier data across Roshel's modular platforms. Polarion can connect ballistic, blast, mobility and mission requirements to verification evidence, while Tecnomatix and Opcenter can plan the expanded flow and preserve unit-level build and quality genealogy. The existing operation is already space-constrained and the bid decision would require rapid scale, so the digital manufacturing architecture must be established before physical expansion and workforce growth accelerate."
                ),
            },
            {
                "signal_date": dt(2026, 5, 26),
                "source_url": "https://roshel.com/roshel-to-unveil-new-generation-of-canadian-defence-vehicles-at-cansec-2026/",
                "source_title": "Roshel to Unveil New Generation of Canadian Defence Vehicles at CANSEC 2026",
                "source_publisher": "Roshel",
                "signal_label": "CANSEC launch adds LUV, ExtremV, medical, emergency and counter-UAS vehicle variants",
                "challenge_summary": (
                    "On May 26, 2026, Roshel announced the CANSEC debut of a new Canadian-developed Light Utility Vehicle platform, the Canadian-manufactured ExtremV, a Senator medical-evacuation vehicle, and updated emergency-response and counter-UAS variants; the company said it was prepared to begin large-scale Canadian production and assembly. The platforms combine modular armour, mobility, medical, sensor and counter-drone configurations for different defence missions. Inference: introducing several regulated vehicle families at once creates immediate requirements, variant-BOM, interface, test, supplier and manufacturing-release complexity."
                ),
                "why_relevant": (
                    "Teamcenter is the smallest defensible backbone for controlling platform commonality, customer variants, bills of material and released manufacturing definitions. Polarion can trace mission, protection and interoperability requirements to qualification results, while Tecnomatix can validate assembly alternatives before capacity is committed. The product family entered the market at CANSEC and Roshel says it is production-ready, making configuration discipline urgent before large orders arrive."
                ),
            },
        ],
    },
    {
        "keyword_ids": [12],
        "company_name": "Bombardier",
        "company_domain": "bombardier.com",
        "company_url": "https://bombardier.com/",
        "linkedin_url": "https://www.linkedin.com/company/bombardier/",
        "location": "Dorval, Quebec, Canada",
        "industry": "Business aircraft design, manufacturing and service",
        "products": ["Teamcenter"],
        "scores": {
            "opportunity": 94,
            "manufacturing": 100,
            "trigger": 95,
            "solution": 100,
            "evidence": 100,
        },
        "pain_signals": [
            "Must evolve Teamcenter as the enterprise PLM platform and integrate it with CAD, product-change, CAM, ERP and supplier-collaboration systems.",
            "Must preserve BOM, change and configuration control while scaling secure enterprise-grade digital engineering architecture.",
        ],
        "expansion_signals": [
            "Opened a June 10, 2026 Solution Architect requisition to lead Teamcenter architecture and integrations for Aerospace Canada.",
        ],
        "evidence": [
            {
                "signal_date": dt(2026, 6, 10),
                "source_url": "https://jobs.bombardier.com/job/Solution-Architect-PLM-%28Teamcenter%29/13751-en_US/",
                "source_title": "Solution Architect - PLM (Teamcenter)",
                "source_publisher": "Bombardier Careers",
                "signal_label": "Bombardier is hiring an architect to evolve Teamcenter and connect PLM with CAD, ERP and suppliers",
                "challenge_summary": (
                    "On June 10, 2026, Bombardier posted a Dorval-based Solution Architect role to define and evolve enterprise Teamcenter PLM solutions supporting engineering and product development. The role explicitly covers Teamcenter architecture, extensions and integrations with CATIA/NX, product-change and CAM tools, ERP and supplier-collaboration platforms, together with BOM, change and configuration control. This is direct evidence of an active enterprise integration program where scale, cybersecurity, product data continuity and cross-system ownership are current delivery requirements rather than inferred future needs."
                ),
                "why_relevant": (
                    "Teamcenter is already the selected platform, so the defensible opportunity is focused Teamcenter architecture, integration, migration and adoption support rather than a broad software replacement. CTGTI can help stabilize CAD/PLM/ERP and supplier interfaces, govern configuration patterns and reduce release or change latency across the aircraft lifecycle. The dated architect requisition shows Bombardier is staffing the program now, making partner capacity and specialist delivery support timely."
                ),
            }
        ],
    },
    {
        "keyword_ids": [12],
        "company_name": "Celestica Inc.",
        "company_domain": "celestica.com",
        "company_url": "https://www.celestica.com/",
        "linkedin_url": "https://www.linkedin.com/company/celestica/",
        "location": "Toronto, Ontario, Canada",
        "industry": "Electronics design, manufacturing, hardware-platform and supply-chain solutions",
        "products": ["Teamcenter", "Opcenter"],
        "scores": {
            "opportunity": 86,
            "manufacturing": 98,
            "trigger": 91,
            "solution": 89,
            "evidence": 96,
        },
        "pain_signals": [
            "Must integrate SAP S/4HANA with PLM, MES and data-warehouse systems across a global design and manufacturing operation.",
            "Must govern enterprise architecture and migration while maintaining scalable, secure product and production data flows.",
        ],
        "expansion_signals": [
            "Opened a July 27, 2026 SAP Enterprise Architect and Delivery Lead role to drive S/4HANA transformation and integrated enterprise systems.",
        ],
        "evidence": [
            {
                "signal_date": dt(2026, 7, 27),
                "source_url": "https://careers.celestica.com/job/Toronto-SAP-Senior-Architect-%26-Delivery-Lead-ON/1380620833/",
                "source_title": "SAP Senior Architect & Delivery Lead",
                "source_publisher": "Celestica Careers",
                "signal_label": "Celestica is staffing an S/4HANA transformation spanning ERP, PLM, MES and data systems",
                "challenge_summary": (
                    "On July 27, 2026, Celestica posted a Toronto-based SAP Enterprise Architect and Delivery Lead role to define the S/4HANA transformation roadmap and lead architecture across ERP, integration platforms and connected PLM, MES and data-warehouse systems. Celestica's posting describes a global business that provides product design, manufacturing, hardware-platform and supply-chain services from advanced medical devices to engineered aviation and cloud hardware. Inference: coordinating enterprise migration with engineering and shop-floor systems creates immediate item/BOM, routing, change, master-data, interface, cutover and production-continuity risk."
                ),
                "why_relevant": (
                    "Teamcenter and Opcenter are the smallest defensible Siemens set where Celestica needs governed product-definition and production-execution integration around SAP S/4HANA. CTGTI can help assess BOM and routing ownership, integration boundaries and traceable handoffs without assuming that Celestica has selected Siemens for every layer. The July requisition is direct evidence that architecture and delivery decisions are active now."
                ),
            }
        ],
    },
]


# Reuse already qualified evidence for newly created persistent keywords and for
# strongly matching existing keywords. Replaying persist_signal is intentional:
# source_url idempotency prevents counter inflation while allowing identity updates.
EXISTING_LINKS = {
    5: [2183],
    8: [2183],
    9: [220, 432, 2194, 2195, 2191, 2184, 2188],
    10: [432, 2194, 2195, 1750, 2174],
    13: [2188, 2191, 2184, 2091],
}


COVERAGE = {
    1: {
        "reviewed": 6,
        "rejected": 2,
        "duplicates": 4,
        "sources": ["Startup Gallery", "X.com", "BetaKit", "NGen", "SpaceQ", "AIAC", "ventureLAB", "BDC StrongNorth"],
        "notes": "Startup Gallery, NGen, SpaceQ and AIAC returned zero relevant new results. BetaKit and BDC surfaced Landing Zones and Sentinel as already-qualified domains. X.com was inaccessible because its certificate could not be verified; later Google X-ray requests were blocked by an automated-traffic challenge.",
    },
    2: {
        "reviewed": 6,
        "rejected": 4,
        "duplicates": 2,
        "sources": ["Startup Gallery", "X.com", "BetaKit", "NGen", "Automate Canada", "ventureLAB", "BDC Capital"],
        "notes": "Startup Gallery returned global directory leads without verified Canadian identity; BetaKit and NGen returned zero recent matches. Automate Canada listings were discovery-only. X.com was inaccessible because its certificate could not be verified.",
    },
    3: {
        "reviewed": 5,
        "rejected": 4,
        "duplicates": 1,
        "sources": ["Startup Gallery", "X.com", "BetaKit", "NGen", "Canada's Ocean Supercluster", "Shipbuilding Association of Canada", "Marine Log", "EDC"],
        "notes": "Mandatory sources returned zero recent shipyard results. Ocean Supercluster surfaced Oneka and digital-ship projects; GIT Coatings was rejected before persistence because it is a coatings manufacturer, not a shipbuilder. Shipbuilding Association search yielded no accessible result and Marine Log returned no Canadian match. X.com was inaccessible.",
    },
    4: {
        "reviewed": 5,
        "rejected": 3,
        "duplicates": 2,
        "sources": ["Startup Gallery", "X.com", "BetaKit", "NGen", "OVIN", "APMA", "Electric Autonomy Canada", "BDC"],
        "notes": "Startup Gallery surfaced non-Canadian directory leads; BetaKit and NGen returned zero recent matches. APMA and OVIN confirmed the ecosystem and Project Arrow but did not provide a new company-specific buying trigger. Electric Autonomy returned zero relevant results. X.com was inaccessible.",
    },
    5: {
        "reviewed": 5,
        "rejected": 2,
        "duplicates": 2,
        "sources": ["Startup Gallery", "X.com", "BetaKit", "NGen", "Creative Destruction Lab", "PLANT", "FedDev Ontario", "BDC Climate Tech"],
        "notes": "BetaKit surfaced Civic Grid, but the available evidence described an installation rather than a sufficiently detailed manufacturing or funding trigger, so it was not published. Volta Energy Solutions was reassessed and newly linked. CDL and NGen returned zero relevant company results. X.com was inaccessible.",
    },
    7: {
        "reviewed": 5,
        "rejected": 3,
        "duplicates": 2,
        "sources": ["Startup Gallery", "X.com", "BetaKit", "NGen", "SpaceQ", "AIAC", "ventureLAB", "BDC StrongNorth"],
        "notes": "Startup Gallery, BetaKit, NGen and SpaceQ returned zero recent matches. AIAC returned Jaunt as a directory-only duplicate. BDC surfaced already-qualified Landing Zones. X.com was inaccessible.",
    },
    8: {
        "reviewed": 7,
        "rejected": 4,
        "duplicates": 2,
        "sources": ["Startup Gallery", "X.com", "BetaKit", "NGen", "ventureLAB Hardware Catalyst", "Automate Canada", "BDC Capital", "ACOA", "FedDev Ontario"],
        "notes": "Startup Gallery and ventureLAB generated discovery leads only. GIT Coatings passed manufacturing fit but did not cleanly match the saved hardware-funding keyword, so it was not persisted. Volta Energy Solutions was reassessed and newly linked. X.com was inaccessible.",
    },
    9: {
        "reviewed": 9,
        "rejected": 2,
        "duplicates": 7,
        "sources": ["Startup Gallery", "X.com", "BetaKit", "NGen", "SpaceQ", "AIAC 2026 Industry Guide", "PacifiCan", "FedDev Ontario", "BDC"],
        "notes": "Seven already-qualified aerospace manufacturers were reassessed and linked using their dated official or government evidence. AIAC's new 2026 guide was discovery-only. SpaceQ returned no exact company result. X.com was inaccessible and Google later presented an automated-traffic challenge.",
    },
    10: {
        "reviewed": 7,
        "rejected": 2,
        "duplicates": 5,
        "sources": ["Startup Gallery", "X.com", "BetaKit", "NGen", "SpaceQ", "AIAC 2026 Industry Guide", "PacifiCan", "CED Quebec", "Canadian Metalworking", "BDC"],
        "notes": "Five already-qualified aerospace suppliers and engine/component manufacturers were reassessed and linked. AIAC's dated guide generated directory leads only; SpaceQ returned zero exact results. X.com was inaccessible.",
    },
    11: {
        "reviewed": 5,
        "rejected": 4,
        "duplicates": 0,
        "sources": ["Startup Gallery", "X.com", "BetaKit", "NGen", "OVIN", "APMA", "Electric Autonomy Canada", "CityNews", "Roshel", "BDC"],
        "notes": "Roshel passed the gate on official product evidence plus a dated independent capacity report. APMA and OVIN profiles were discovery-only; Startup Gallery, BetaKit, NGen and Electric Autonomy returned no qualifying recent OEM. X.com was inaccessible.",
    },
    12: {
        "reviewed": 6,
        "rejected": 4,
        "duplicates": 0,
        "sources": ["Startup Gallery", "X.com", "BetaKit", "NGen", "Bombardier Careers", "Celestica Careers", "CME", "PLANT", "BDC LIFT"],
        "notes": "Bombardier and Celestica passed with dated official career evidence for active ERP-PLM/MES integration programs. Pure Life Machinery was rejected because PLM in its name was not Product Lifecycle Management and its posting showed ERP-only work. Anonymous consulting engagements and software vendors were not published. X.com was inaccessible.",
    },
    13: {
        "reviewed": 7,
        "rejected": 3,
        "duplicates": 4,
        "sources": ["Startup Gallery", "X.com", "BetaKit", "NGen", "SpaceQ", "AIAC", "CanadaBuys", "ventureLAB", "BDC StrongNorth", "National Defence"],
        "notes": "Four already-qualified autonomous-aircraft and drone manufacturers were reassessed and linked. CanadaBuys' Volatus award concerned DJI-equivalent procurement and was not used as manufacturing proof. Tactiql/Most Ambitious and the Defence Drone Initiative were discovery context only. X.com was inaccessible.",
    },
}


def make_signal(candidate: dict[str, object], evidence: dict[str, object]) -> ExtractedSignal:
    scores = candidate["scores"]
    return ExtractedSignal(
        company_name=str(candidate["company_name"]),
        company_domain=str(candidate["company_domain"]),
        company_url=str(candidate["company_url"]),
        linkedin_url=str(candidate["linkedin_url"]),
        location=str(candidate["location"]),
        industry=str(candidate["industry"]),
        company_industry=str(candidate["industry"]),
        software=[],
        signal_type="career_page" if "Careers" in str(evidence["source_publisher"]) else "news",
        signal_source="career_page" if "Careers" in str(evidence["source_publisher"]) else "news",
        pain_signals=list(candidate["pain_signals"]),
        expansion_signals=list(candidate["expansion_signals"]),
        raw_score=int(scores["opportunity"]),
        confidence=int(scores["evidence"]) / 100,
        reason=str(evidence["challenge_summary"]),
        source_url=str(evidence["source_url"]),
        source_title=str(evidence["source_title"]),
        detected_at=evidence["signal_date"],
    )


def replay_existing_signal(database: Database, row, company) -> None:
    signal_type = "job_posting" if row.source_url and "/job" in row.source_url else "news"
    signal_source = "google" if signal_type == "job_posting" else "news"
    database.persist_signal(
        ExtractedSignal(
            company_name=company.company_name,
            company_domain=company.company_domain,
            company_url=company.company_url,
            linkedin_url=company.linkedin_url,
            location=company.location,
            industry=company.industry,
            company_industry=company.company_industry,
            software=list(company.software or []),
            signal_type=signal_type,
            signal_source=signal_source,
            pain_signals=[row.challenge_summary] if row.challenge_summary else [],
            expansion_signals=[row.signal_label] if row.signal_label else [],
            raw_score=row.opportunity_score,
            confidence=row.evidence_quality_score / 100,
            reason=row.challenge_summary,
            source_url=row.source_url,
            source_title=row.source_title,
            detected_at=row.signal_date or row.last_seen_at,
        )
    )


def main() -> None:
    load_dotenv(".env")
    database = Database()
    database.initialize()
    keywords = {item.id: item for item in database.list_keywords()}
    expected_ids = set(COVERAGE)
    if set(keywords) != expected_ids:
        raise RuntimeError(f"Persistent keyword set changed: {sorted(keywords)}")

    published_counts = {keyword_id: 0 for keyword_id in keywords}
    signal_results = []
    linked_companies = []

    for candidate in NEW_CANDIDATES:
        for evidence in candidate["evidence"]:
            saved, company = database.persist_signal(make_signal(candidate, evidence))
            signal_results.append(
                {
                    "company": candidate["company_name"],
                    "source_url": evidence["source_url"],
                    "created": saved.created,
                    "duplicate_url": saved.duplicate_url,
                    "company_domain": company.company_domain,
                }
            )

        primary = candidate["evidence"][0]
        scores = candidate["scores"]
        for keyword_id in candidate["keyword_ids"]:
            linked = database.record_keyword_company(
                keyword_id,
                candidate["company_name"],
                candidate["company_domain"],
                source_url=primary["source_url"],
                source_title=primary["source_title"],
                source_publisher=primary["source_publisher"],
                signal_label=primary["signal_label"],
                signal_date=primary["signal_date"],
                challenge_summary=primary["challenge_summary"],
                why_relevant=primary["why_relevant"],
                recommended_products=candidate["products"],
                qualification_status="qualified",
                opportunity_score=scores["opportunity"],
                manufacturing_fit_score=scores["manufacturing"],
                trigger_score=scores["trigger"],
                solution_fit_score=scores["solution"],
                evidence_quality_score=scores["evidence"],
                seen_at=RUN_AT,
            )
            if linked is None:
                raise RuntimeError(f"Could not link {candidate['company_name']} to keyword {keyword_id}")
            published_counts[keyword_id] += 1
            linked_companies.append(
                {"keyword_id": keyword_id, "company_id": linked.company_id, "company": linked.company_name}
            )

    existing_rows = database.list_keyword_companies(limit=5000)
    row_by_company_id = {}
    for row in existing_rows:
        if row.qualification_status not in {"qualified", "watchlist"} or not row.source_url:
            continue
        current = row_by_company_id.get(row.company_id)
        if current is None or (row.signal_date or row.last_seen_at) > (current.signal_date or current.last_seen_at):
            row_by_company_id[row.company_id] = row

    leads_by_domain = {
        company.company_domain: company
        for company in database.get_leads()
        if company.company_domain
    }

    for keyword_id, company_ids in EXISTING_LINKS.items():
        for company_id in company_ids:
            row = row_by_company_id[company_id]
            company = leads_by_domain[row.company_domain]
            replay_existing_signal(database, row, company)
            linked = database.record_keyword_company(
                keyword_id,
                row.company_name,
                row.company_domain,
                source_url=row.source_url,
                source_title=row.source_title,
                source_publisher=row.source_publisher,
                signal_label=row.signal_label,
                signal_date=row.signal_date,
                challenge_summary=row.challenge_summary,
                why_relevant=row.why_relevant,
                recommended_products=row.recommended_products,
                qualification_status=row.qualification_status,
                opportunity_score=row.opportunity_score,
                manufacturing_fit_score=row.manufacturing_fit_score,
                trigger_score=row.trigger_score,
                solution_fit_score=row.solution_fit_score,
                evidence_quality_score=row.evidence_quality_score,
                seen_at=RUN_AT,
            )
            if linked is None:
                raise RuntimeError(f"Could not link existing company {row.company_name} to keyword {keyword_id}")
            published_counts[keyword_id] += 1
            linked_companies.append(
                {"keyword_id": keyword_id, "company_id": linked.company_id, "company": linked.company_name}
            )

    for keyword_id, result_count in published_counts.items():
        database.record_keyword_search(keyword_id, result_count=result_count)

    per_keyword = {}
    for keyword_id, item in COVERAGE.items():
        per_keyword[keyword_id] = {
            "keyword": keywords[keyword_id].keyword,
            "lookback": "rolling 30 days first, then 180-day fallback",
            "candidates_reviewed": item["reviewed"],
            "rejected_before_persistence": item["rejected"],
            "qualified_published": published_counts[keyword_id],
            "watchlist_published": 0,
            "existing_records_upgraded_or_hidden": 0,
            "duplicates_skipped": item["duplicates"],
            "sources_checked": item["sources"],
            "blockers_or_zero_results": item["notes"],
        }

    print(
        json.dumps(
            {
                "run_at": RUN_AT.isoformat(),
                "signals": signal_results,
                "keyword_links": linked_companies,
                "published_counts": published_counts,
                "per_keyword": per_keyword,
            },
            indent=2,
            default=str,
        )
    )


if __name__ == "__main__":
    main()
