from __future__ import annotations

from datetime import datetime, timezone

from dotenv import load_dotenv
from sqlalchemy import func, select

from db.database import CompanyRecord, Database
from models.schema import ExtractedSignal


QUALIFIED = [
    {
        "keyword_id": 1,
        "company_name": "Maritime Launch Services",
        "company_domain": "maritimelaunch.com",
        "company_url": "https://www.maritimelaunch.com/",
        "location": "Canso, Nova Scotia, Canada",
        "industry": "Commercial spaceport development and launch operations",
        "evidence": [
            {
                "source_url": (
                    "https://www.maritimelaunch.com/news/"
                    "sovereign-space-access-for-Germany-and-Canada-july-2026"
                ),
                "source_title": (
                    "Maritime Launch Services and Isar Aerospace sign contract to "
                    "advance orbital launch capability from Spaceport Nova Scotia"
                ),
                "source_publisher": "Maritime Launch Services",
                "signal_label": (
                    "Ten-year Spectrum launch-complex contract targets 40 launches a year"
                ),
                "signal_date": datetime(2026, 7, 7, 12, 0, tzinfo=timezone.utc),
                "challenge_summary": (
                    "On July 7, 2026, Maritime Launch Services signed a ten-year contract "
                    "for Isar Aerospace to build a dedicated Spectrum rocket complex at "
                    "Spaceport Nova Scotia, with two optional five-year renewals and a "
                    "target of up to 40 launches annually by 2029. MLS must provide the "
                    "licensed site, launch pad, assembly, integration and test facilities, "
                    "launch-operations centre, and payload-integration capability; build-out "
                    "starts in 2026 for first orbital launches in 2028. Inference: the "
                    "milestone-driven introduction of a new launch vehicle creates immediate "
                    "requirements, facility-interface, configuration, safety-verification, "
                    "and change-control pressure across two companies."
                ),
                "why_relevant": (
                    "Teamcenter can govern facility and launch-system configurations, "
                    "interfaces, documents, and engineering changes; Polarion can trace "
                    "licensed-site, safety, vehicle, and payload requirements into test and "
                    "acceptance evidence. Tecnomatix can support assembly, integration, and "
                    "facility-process planning before operations scale. The opportunity is "
                    "time-sensitive because the statement of work and pad-handover milestones "
                    "fall in 2026, ahead of infrastructure completion in 2027."
                ),
            },
            {
                "source_url": (
                    "https://maritimelaunch.com/news/"
                    "spaceport-nova-scotia-construction-update-july-2026"
                ),
                "source_title": "Spaceport Nova Scotia construction update – July 2026",
                "source_publisher": "Maritime Launch Services",
                "signal_label": (
                    "First civil phase nears completion as integration-facility planning begins"
                ),
                "signal_date": datetime(2026, 7, 2, 12, 0, tzinfo=timezone.utc),
                "challenge_summary": (
                    "Maritime Launch Services reported on July 2, 2026 that construction "
                    "resumed in March, the first civil phase was nearing completion, the "
                    "utility hub was moving to tender, and design work was advancing for the "
                    "site entrance, vehicle-integration facility, and road extensions. "
                    "Inference: concurrent civil, utility, vehicle-integration, and launch-pad "
                    "work creates a fast-changing set of facility requirements and interfaces "
                    "that must remain aligned with launch operations and certification."
                ),
                "why_relevant": (
                    "Teamcenter provides one controlled product-and-facility definition for "
                    "drawings, interfaces, suppliers, and revisions, while Tecnomatix can "
                    "validate integration and material-flow processes before the facility is "
                    "commissioned. Polarion can connect construction and operational "
                    "requirements to verification and acceptance records. The need is current "
                    "because procurement and detailed facility planning are already underway."
                ),
            },
        ],
        "recommended_products": ["Teamcenter", "Polarion", "Tecnomatix"],
        "opportunity_score": 94,
        "manufacturing_fit_score": 92,
        "trigger_score": 98,
        "solution_fit_score": 95,
        "evidence_quality_score": 98,
    },
    {
        "keyword_id": 1,
        "company_name": "MDS Coating Technologies",
        "company_domain": "mdscoating.com",
        "company_url": "https://www.mdscoating.com/",
        "location": "Slemon Park, Prince Edward Island, Canada",
        "industry": "Aerospace engine nanocoatings and advanced manufacturing",
        "evidence": [
            {
                "source_url": (
                    "https://www.canada.ca/en/innovation-science-economic-development/"
                    "news/2026/05/minister-joly-announces-55-million-federal-investment-"
                    "to-advance-sustainable-canadian-dual-use-aerospace-technology-at-"
                    "mds-coating.html"
                ),
                "source_title": (
                    "Minister Joly announces $55 million federal investment to advance "
                    "sustainable Canadian dual-use aerospace technology at MDS Coating"
                ),
                "source_publisher": (
                    "Innovation, Science and Economic Development Canada"
                ),
                "signal_label": (
                    "$212.9M aerospace nanocoating commercialization and factory expansion"
                ),
                "signal_date": datetime(2026, 5, 13, 12, 0, tzinfo=timezone.utc),
                "challenge_summary": (
                    "On May 13, 2026, the federal government announced a $55.7-million "
                    "Strategic Response Fund contribution toward MDS Coating Technologies' "
                    "$212.9-million project to develop and commercialize protective "
                    "nanocoatings for aerospace engines and expand its facility and "
                    "manufacturing capability. The project is expected to create up to 230 "
                    "jobs and 70 co-op placements across its Slemon Park manufacturing centre "
                    "and Montréal research operation. Inference: moving a new dual-use coating "
                    "from R&D into higher-volume aerospace production increases formulation "
                    "and process revision control, qualification-test burden, asset/process "
                    "traceability, and quality-record requirements."
                ),
                "why_relevant": (
                    "Teamcenter can control coating specifications, process definitions, "
                    "customer configurations, and engineering changes; Opcenter can enforce "
                    "manufacturing recipes, genealogy, inspection, and traceability. Polarion "
                    "can link aerospace and dual-use requirements to validation evidence, "
                    "while Simcenter can support performance and durability assessment where "
                    "the engineering team requires it. The funding makes this urgent because "
                    "facility expansion and commercialization are now financed at material scale."
                ),
            }
        ],
        "recommended_products": ["Teamcenter", "Opcenter", "Polarion", "Simcenter"],
        "opportunity_score": 97,
        "manufacturing_fit_score": 100,
        "trigger_score": 100,
        "solution_fit_score": 97,
        "evidence_quality_score": 100,
    },
    {
        "keyword_id": 1,
        "company_name": "Apex Precision Inc.",
        "company_domain": "apexprecision.ca",
        "company_url": "https://apexprecision.ca/",
        "location": "Saint-Lazare and Vaudreuil-Dorion, Quebec, Canada",
        "industry": "Aerospace precision components, machining, and assembly",
        "evidence": [
            {
                "source_url": (
                    "https://www.canada.ca/en/economic-development-quebec-regions/"
                    "news/2026/05/tariff-response-government-of-canada-invests-over-"
                    "950000-in-apex-precision-to-help-it-face-current-challenges.html"
                ),
                "source_title": (
                    "Tariff response: Government of Canada invests over $950,000 in "
                    "Apex Precision to help it face current challenges"
                ),
                "source_publisher": (
                    "Canada Economic Development for Quebec Regions"
                ),
                "signal_label": (
                    "$957,500 equipment investment expands aerospace capacity amid tariffs"
                ),
                "signal_date": datetime(2026, 5, 19, 12, 0, tzinfo=timezone.utc),
                "challenge_summary": (
                    "On May 19, 2026, the Government of Canada awarded Apex Precision a "
                    "$957,500 non-repayable contribution for new production equipment to "
                    "improve productivity, increase capacity, diversify markets, and protect "
                    "nearly 80 jobs while aluminum tariffs pressure the business. Apex "
                    "manufactures and assembles precision aluminum components for aerospace "
                    "and health customers using CNC machining, sheet metal, welding, and "
                    "aerospace assembly. Inference: adding equipment while entering new "
                    "aerospace markets raises NC-program, revision, routing, capacity, "
                    "inspection, and part-traceability complexity at a moment when scrap and "
                    "rework costs are especially sensitive."
                ),
                "why_relevant": (
                    "NX can connect precision design and CAM programming, while Teamcenter "
                    "can govern drawings, BOMs, manufacturing data, customer revisions, and "
                    "release status. Opcenter can provide routing, work-in-process, quality, "
                    "and lot/serial traceability as capacity expands. The opportunity is "
                    "current because funded production equipment and new aerospace-market "
                    "work must be integrated without eroding margins already pressured by tariffs."
                ),
            }
        ],
        "recommended_products": ["NX", "Teamcenter", "Opcenter"],
        "opportunity_score": 91,
        "manufacturing_fit_score": 100,
        "trigger_score": 92,
        "solution_fit_score": 95,
        "evidence_quality_score": 100,
    },
    {
        "keyword_id": 2,
        "company_name": "Atlas Engineered Products",
        "company_domain": "atlasengineeredproducts.com",
        "company_url": "https://www.atlasengineeredproducts.com/",
        "location": "Clinton, Ontario, Canada",
        "industry": "Engineered wood building components and automated manufacturing",
        "evidence": [
            {
                "source_url": (
                    "https://www.atlasengineeredproducts.com/news/"
                    "atlas-engineered-products-reports-first-quarter-2026-"
                    "financial-and-operating-results"
                ),
                "source_title": (
                    "Atlas Engineered Products reports first quarter 2026 financial "
                    "and operating results"
                ),
                "source_publisher": "Atlas Engineered Products",
                "signal_label": (
                    "Robotic truss plant nears July launch as Q1 quotes exceed $80M"
                ),
                "signal_date": datetime(2026, 5, 25, 12, 0, tzinfo=timezone.utc),
                "challenge_summary": (
                    "Atlas Engineered Products reported that its first robotic truss "
                    "manufacturing plant in Clinton, Ontario was nearing completion, equipment "
                    "had shipped, and operations were expected to begin in July 2026; the "
                    "project has access to up to $4 million in non-repayable federal support. "
                    "At the same time, first-quarter customer quotes exceeded $80 million and "
                    "orders surpassed $21 million, up from more than $11 million a year earlier. "
                    "Inference: commissioning a new automated line against a rapidly expanding "
                    "order book creates immediate line-balancing, digital work-instruction, "
                    "production-scheduling, quality, and engineering-to-factory data challenges."
                ),
                "why_relevant": (
                    "Tecnomatix can model and validate the robotic line, material flow, and "
                    "operator processes before and during ramp-up; Opcenter can schedule and "
                    "track production, quality, and throughput. Teamcenter can control truss "
                    "designs, manufacturing definitions, and revisions feeding the automated "
                    "equipment. The fit is urgent because the plant is entering operation now "
                    "while order volume is nearly twice the prior-year level."
                ),
            }
        ],
        "recommended_products": ["Tecnomatix", "Opcenter", "Teamcenter"],
        "opportunity_score": 93,
        "manufacturing_fit_score": 100,
        "trigger_score": 97,
        "solution_fit_score": 96,
        "evidence_quality_score": 97,
    },
]

SEARCH_RESULTS = {1: 3, 2: 1, 3: 0, 4: 0}


def _correct_apex_identity(database: Database) -> None:
    """Correct the previously stored directory-domain mismatch with verified data."""
    with database.session() as session, session.begin():
        company = session.scalar(
            select(CompanyRecord)
            .where(func.lower(CompanyRecord.company_name) == "apex precision inc.")
            .limit(1)
        )
        if company is None:
            return
        company.company_domain = "apexprecision.ca"
        company.company_url = "https://apexprecision.ca/"
        company.location = "Saint-Lazare and Vaudreuil-Dorion, Quebec, Canada"
        company.industry = "Aerospace precision components, machining, and assembly"
        company.company_industry = company.industry


def main() -> None:
    load_dotenv()
    database = Database()
    database.initialize()
    keywords = {keyword.id: keyword for keyword in database.list_keywords()}
    _correct_apex_identity(database)

    for item in QUALIFIED:
        if item["keyword_id"] not in keywords:
            raise RuntimeError(f"Keyword {item['keyword_id']} no longer exists")

        primary = item["evidence"][0]
        for evidence in item["evidence"]:
            signal = ExtractedSignal(
                company_name=item["company_name"],
                company_domain=item["company_domain"],
                company_url=item["company_url"],
                location=item["location"],
                industry=item["industry"],
                company_industry=item["industry"],
                software=item["recommended_products"],
                signal_type="news",
                signal_source="news",
                pain_signals=[evidence["challenge_summary"]],
                expansion_signals=[evidence["signal_label"]],
                raw_score=item["opportunity_score"],
                confidence=item["evidence_quality_score"] / 100,
                reason=evidence["why_relevant"],
                source_url=evidence["source_url"],
                source_title=evidence["source_title"],
                detected_at=evidence["signal_date"],
            )
            saved = database.save_signal(signal)
            database.upsert_company(signal)
            print(
                f"{item['company_name']}: {evidence['signal_label']} "
                f"signal_created={saved.created}"
            )

        ledger = database.record_keyword_company(
            item["keyword_id"],
            item["company_name"],
            item["company_domain"],
            source_url=primary["source_url"],
            source_title=primary["source_title"],
            source_publisher=primary["source_publisher"],
            signal_label=primary["signal_label"],
            signal_date=primary["signal_date"],
            challenge_summary=primary["challenge_summary"],
            why_relevant=primary["why_relevant"],
            recommended_products=item["recommended_products"],
            qualification_status="qualified",
            opportunity_score=item["opportunity_score"],
            manufacturing_fit_score=item["manufacturing_fit_score"],
            trigger_score=item["trigger_score"],
            solution_fit_score=item["solution_fit_score"],
            evidence_quality_score=item["evidence_quality_score"],
        )
        if ledger is None:
            raise RuntimeError(f"Could not link {item['company_name']} to its keyword")
        print(
            f"{item['company_name']}: qualification={ledger.qualification_status} "
            f"opportunity_score={ledger.opportunity_score}"
        )

    for keyword_id, result_count in SEARCH_RESULTS.items():
        database.record_keyword_search(keyword_id, result_count=result_count)
        print(f"{keywords[keyword_id].keyword}: published={result_count}")


if __name__ == "__main__":
    main()
