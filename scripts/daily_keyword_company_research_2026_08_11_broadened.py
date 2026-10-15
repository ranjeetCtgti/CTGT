from __future__ import annotations

from datetime import datetime, timezone

from dotenv import load_dotenv

from db.database import Database
from models.schema import ExtractedSignal


SEEN_AT = datetime.now(timezone.utc)


def dt(year: int, month: int, day: int) -> datetime:
    return datetime(year, month, day, tzinfo=timezone.utc)


CANDIDATES = [
    {
        "keyword_ids": [2],
        "company_name": "TetraGen Robotics Inc.",
        "company_domain": "tetragen.ai",
        "company_url": "https://www.tetragen.ai/",
        "linkedin_url": "https://www.linkedin.com/company/tetragen-robotics/",
        "location": "Winnipeg, Manitoba, Canada",
        "industry": "Autonomous robotic welding systems",
        "signal_date": dt(2026, 8, 10),
        "source_url": "https://betakit.com/autonomous-welding-startup-tetragen-robotics-raises-1-8-million/",
        "source_title": "Autonomous welding startup TetraGen Robotics raises $1.8 million",
        "source_publisher": "BetaKit",
        "signal_label": "$1.8M seed round funds commercialization and engineering-team growth",
        "challenge_summary": (
            "On August 10, 2026, Winnipeg-based TetraGen Robotics announced a $1.8 million CAD oversubscribed seed round led by StepChange Capital to commercialize its autonomous welding systems and expand its engineering and commercial teams. Its product combines an industrial welding-robot chassis with proprietary AI and machine vision to generate welding programs automatically and adapt to real production variation; the company plans additional North American customer deployments in heavy equipment, mining, and defence manufacturing. Inference: scaling configurable robotic cells across customers with different parts, welds, fixtures, and acceptance criteria creates immediate engineering-change, cell-planning, commissioning, and production-quality complexity."
        ),
        "why_relevant": (
            "Teamcenter can govern robot-cell configurations, weld recipes, fixtures, released drawings, and customer-specific engineering changes. Tecnomatix can model robotic reach, collision risk, sequencing, and cycle time before installation, while Opcenter can capture deployment genealogy, process results, inspection, and nonconformance. The funded commercialization and engineering expansion make these capabilities relevant before deployment volume grows."
        ),
        "products": ["Teamcenter", "Tecnomatix", "Opcenter"],
        "scores": (91, 97, 92, 95, 93),
        "pain_signals": [
            "Must configure and commission autonomous welding cells for varied customer parts and weld requirements.",
            "Must preserve weld-process and quality evidence as customer deployments increase.",
        ],
        "expansion_signals": [
            "$1.8 million seed round will accelerate commercialization and North American deployments.",
            "Plans to expand engineering and commercial teams.",
        ],
    },
    {
        "keyword_ids": [5],
        "company_name": "Quadrogen Power Systems, Inc.",
        "company_domain": "quadrogen.com",
        "company_url": "https://quadrogen.com/",
        "linkedin_url": "https://www.linkedin.com/company/quadrogen-power-systems/",
        "location": "Burnaby, British Columbia, Canada",
        "industry": "Biogas upgrading and industrial gas-recovery systems",
        "signal_date": dt(2026, 8, 10),
        "source_url": "https://www.canada.ca/en/pacific-economic-development/news/2026/08/government-of-canada-invests-over-30-million-to-help-bc-businesses-navigate-trade-disruptions-and-seize-new-opportunities.html",
        "source_title": "Government of Canada invests over $30 million to help B.C. businesses navigate trade disruptions and seize new opportunities",
        "source_publisher": "Pacific Economic Development Canada",
        "signal_label": "$3.6M investment funds a new lower-cost biogas upgrading system",
        "challenge_summary": (
            "On August 10, 2026, PacifiCan awarded Burnaby-based Quadrogen $3.6 million to design, manufacture, and demonstrate a lower-cost biogas clean-up and upgrading system for deployment in developing markets, including India. Quadrogen develops and fabricates complete biogas, hydrogen, carbon-capture, and industrial gas-recovery systems, so the funded program moves a new process-equipment design through engineering, fabrication, demonstration, and export deployment. Inference: the new cost target and overseas operating environments increase pressure on equipment configuration, process simulation, supplier coordination, fabrication quality, and controlled commissioning documentation."
        ),
        "why_relevant": (
            "NX can support mechanical equipment and skid design, while Teamcenter can control equipment BOMs, vendor data, and changes from design through fabrication. Simcenter can evaluate thermal, flow, and structural behavior before the demonstration system is built, and Opcenter can provide fabrication and test traceability. The funded design-manufacture-demonstrate program is active now and has a defined international deployment objective."
        ),
        "products": ["NX", "Teamcenter", "Simcenter", "Opcenter"],
        "scores": (89, 96, 94, 93, 95),
        "pain_signals": [
            "Must meet a lower cost target while designing and fabricating a new biogas clean-up system.",
            "Must demonstrate and document system performance for deployment in developing markets.",
        ],
        "expansion_signals": [
            "$3.6 million PacifiCan investment supports design, manufacturing, and demonstration.",
            "Program targets deployment in developing markets including India.",
        ],
    },
    {
        "keyword_ids": [1],
        "company_name": "Landing Zones Canada",
        "company_domain": "landingzones.com",
        "company_url": "https://landingzones.com/",
        "linkedin_url": "https://www.linkedin.com/company/landing-zones-canada/",
        "location": "Medicine Hat, Alberta, Canada",
        "industry": "Uncrewed aerial systems and defence training technology",
        "signal_date": dt(2026, 7, 22),
        "source_url": "https://www.airbus.com/en/newsroom/press-releases/2026-07-airbus-and-landing-zones-sign-strategic-partnership-for-advanced-uas-in-canada",
        "source_title": "Airbus and Landing Zones sign strategic partnership for advanced UAS in Canada",
        "source_publisher": "Airbus",
        "signal_label": "Airbus investment accelerates advanced UAS and live-training simulation systems",
        "challenge_summary": (
            "On July 22, 2026, Airbus Defence and Space invested in Medicine Hat-based Landing Zones Canada and took a board seat under a strategic partnership to expand advanced uncrewed-aircraft simulation and training services in Canada. The partners will combine Landing Zones' threat-emulation technology and advanced glide targets with Airbus expertise to deliver large-scale, real-world verification against emerging drone threats; the program also supports Airbus' Canadian industrial-benefits obligations for the A330 MRTT acquisition. Inference: rapid development of safety- and mission-critical UAS targets for complex defence scenarios creates strict requirements, configuration, test-evidence, and multidisciplinary design-control needs."
        ),
        "why_relevant": (
            "Polarion can link threat scenarios and customer requirements to verification results and controlled acceptance evidence. Teamcenter can manage airframe, payload, and training-system configurations and changes, while Simcenter can support aerodynamic, structural, and mission-performance validation. The Airbus capital, board participation, and stated expansion into large-scale Canadian training make the trigger current and concrete."
        ),
        "products": ["Polarion", "Teamcenter", "Simcenter"],
        "scores": (90, 95, 92, 94, 94),
        "pain_signals": [
            "Must manage defence-grade UAS requirements and verification evidence across complex threat scenarios.",
            "Must control advanced glide-target and simulation configurations as Canadian training expands.",
        ],
        "expansion_signals": [
            "Airbus made a strategic investment and obtained board representation.",
            "Partnership will expand large-scale UAS simulation and training services across Canada.",
        ],
    },
    {
        "keyword_ids": [3],
        "company_name": "Miru Smart Technologies",
        "company_domain": "mirucorp.com",
        "company_url": "https://mirucorp.com/",
        "linkedin_url": "https://www.linkedin.com/company/miru-corp/",
        "location": "Vancouver, British Columbia, Canada",
        "industry": "Electrochromic smart-glass systems for vehicles and vessels",
        "signal_date": dt(2026, 7, 28),
        "source_url": "https://oceansupercluster.ca/project/canadas-ocean-supercluster-announces-11-7m-project-oceanshade-dynamic-electrochromic-marine-glass/",
        "source_title": "Canada's Ocean Supercluster Announces $11.7M Project OceanShade – Dynamic Electrochromic Marine Glass",
        "source_publisher": "Canada's Ocean Supercluster",
        "signal_label": "$11.7M OceanShade project funds marine prototypes, certification, and commercialization",
        "challenge_summary": (
            "On July 28, 2026, Canada's Ocean Supercluster announced the $11.7 million Project OceanShade led by Vancouver-based Miru Smart Technologies, including a $4.1 million cluster investment. Miru, Innovative Finishing Solutions, and Maple Advanced Robotics will design marine-adapted dynamic-glass prototypes, conduct durability and certification testing, and assemble a technical package for commercial deployment; the glazing automatically changes tint to manage glare and solar heat. Inference: adapting an electrochromic platform to harsh marine service and AI-enabled manufacturing creates material, control, prototype, supplier, certification, and production-process traceability requirements."
        ),
        "why_relevant": (
            "Teamcenter can control glass, coating, electronics, supplier, and prototype configurations across the three-company consortium. Simcenter can support thermal, optical-environment, structural, and durability validation, while Opcenter can capture manufacturing parameters, inspection, and traceability as the process moves toward commercial deployment. Funding is committed and the project explicitly requires prototypes, certification testing, and a deployment-ready technical package."
        ),
        "products": ["Teamcenter", "Simcenter", "Opcenter"],
        "scores": (90, 94, 93, 93, 96),
        "pain_signals": [
            "Must qualify electrochromic glass for demanding marine durability and certification requirements.",
            "Must coordinate prototypes and AI-enabled manufacturing processes across a three-company consortium.",
        ],
        "expansion_signals": [
            "$11.7 million project includes a $4.1 million Ocean Supercluster investment.",
            "Program targets a complete technical package for commercial marine deployment.",
        ],
    },
    {
        "keyword_ids": [3],
        "company_name": "Celerity Craft Inc.",
        "company_domain": "celeritycraft.com",
        "company_url": "https://celeritycraft.com/",
        "linkedin_url": None,
        "location": "Squamish, British Columbia, Canada",
        "industry": "Zero-emission dynamic air-cushion electric vessels",
        "signal_date": dt(2026, 7, 28),
        "source_url": "https://oceansupercluster.ca/project/canadas-ocean-supercluster-announces-7-6m-dynamic-air-cushion-electric-vehicle-project/",
        "source_title": "Canada's Ocean Supercluster Announces $7.6M Dynamic Air Cushion Electric Vehicle Project",
        "source_publisher": "Canada's Ocean Supercluster",
        "signal_label": "$7.6M DACEV project advances demonstrator, commercial water taxi, and new factory",
        "challenge_summary": (
            "On July 28, 2026, Canada's Ocean Supercluster announced a $7.6 million Dynamic Air Cushion Electric Vehicle project led by Squamish-based Celerity Craft, with a $2.9 million cluster investment. The program will first validate a 5.5-metre air-cushion/electric demonstrator and then develop an 11.9-metre, 12-passenger commercial water taxi, while establishing a new DACEV Manufacturing and Innovation Centre in Squamish. Inference: moving from demonstrator to passenger vessel and factory launch creates immediate multidisciplinary design, electric architecture, hydrodynamic/structural validation, requirements, BOM, supplier, production-planning, and certification complexity."
        ),
        "why_relevant": (
            "NX and Simcenter can support hull, air-cushion, structural, thermal, and propulsion-system design and validation. Teamcenter can control the demonstrator and commercial-vessel baselines and supplier BOMs, while Capital can manage electrical propulsion and controls architecture; Tecnomatix can plan the new manufacturing centre. The funded two-phase program and planned factory create a clear digital-thread decision window before designs and processes harden."
        ),
        "products": ["NX", "Simcenter", "Teamcenter", "Capital", "Tecnomatix"],
        "scores": (94, 99, 96, 97, 97),
        "pain_signals": [
            "Must scale a validated 5.5-metre demonstrator into an 11.9-metre passenger vessel.",
            "Must establish a new vessel manufacturing and innovation centre with controlled processes.",
        ],
        "expansion_signals": [
            "$7.6 million project includes a $2.9 million Ocean Supercluster investment.",
            "Plans a new DACEV Manufacturing and Innovation Centre in Squamish.",
        ],
    },
    {
        "keyword_ids": [1, 2],
        "company_name": "Mahler Machining",
        "company_domain": "mahler-machining.com",
        "company_url": "https://mahler-machining.com/",
        "linkedin_url": "https://www.linkedin.com/company/mahler-machining/",
        "location": "Coquitlam, British Columbia, Canada",
        "industry": "Precision CNC manufacturing for aerospace, defence, robotics, and medical devices",
        "signal_date": dt(2026, 8, 10),
        "source_url": "https://www.canada.ca/en/pacific-economic-development/news/2026/08/government-of-canada-invests-over-30-million-to-help-bc-businesses-navigate-trade-disruptions-and-seize-new-opportunities.html",
        "source_title": "Government of Canada invests over $30 million to help B.C. businesses navigate trade disruptions and seize new opportunities",
        "source_publisher": "Pacific Economic Development Canada",
        "signal_label": "$1M investment adds equipment, automation, and manufacturing software",
        "challenge_summary": (
            "On August 10, 2026, PacifiCan awarded Coquitlam-based Mahler Machining $1 million to modernize its facility with advanced equipment, automation, and new software, improving productivity and supporting entry into new markets. Mahler manufactures complex metal and plastic components for aerospace, defence, medical-device, robotics, clean-technology, and forestry customers from a 20,000-square-foot CNC facility. Inference: adding automated equipment and software across regulated, high-mix customer programs increases NC-program, routing, inspection, machine-data, scheduling, and part-genealogy integration pressure."
        ),
        "why_relevant": (
            "NX can unify part design, manufacturing engineering, and CAM for the expanded machine environment. Teamcenter can govern drawings, revisions, NC programs, routings, and customer-specific change, while Opcenter can schedule work and capture shop-floor quality and genealogy across the automated facility. The grant explicitly funds equipment, automation, and software now, making this a direct modernization trigger."
        ),
        "products": ["NX", "Teamcenter", "Opcenter"],
        "scores": (92, 99, 95, 96, 96),
        "pain_signals": [
            "Must integrate advanced equipment, automation, and new software in a high-mix CNC facility.",
            "Must maintain revision and quality traceability across aerospace, defence, robotics, and medical programs.",
        ],
        "expansion_signals": [
            "$1 million PacifiCan investment funds facility modernization.",
            "Modernization is intended to improve productivity and support expansion into new markets.",
        ],
    },
    {
        "keyword_ids": [1],
        "company_name": "COTA Aviation Ltd.",
        "company_domain": "cotaaviation.com",
        "company_url": "https://www.cotaaviation.com/",
        "linkedin_url": "https://www.linkedin.com/company/cotaaviation/",
        "location": "Parksville, British Columbia, Canada",
        "industry": "Aerospace and defence component manufacturing and MRO",
        "signal_date": dt(2026, 8, 10),
        "source_url": "https://www.canada.ca/en/pacific-economic-development/news/2026/08/government-of-canada-invests-over-30-million-to-help-bc-businesses-navigate-trade-disruptions-and-seize-new-opportunities.html",
        "source_title": "Government of Canada invests over $30 million to help B.C. businesses navigate trade disruptions and seize new opportunities",
        "source_publisher": "Pacific Economic Development Canada",
        "signal_label": "$1M investment establishes domestic aircraft and defence gear production",
        "challenge_summary": (
            "On August 10, 2026, PacifiCan awarded Parksville-based COTA Aviation $1 million to purchase and install advanced equipment for manufacturing gears used in aircraft and defence systems in British Columbia. COTA provides aerospace and defence manufacturing, maintenance, repair and overhaul, and training services. Inference: bringing precision gear production onto new equipment creates controlled design-to-manufacturing, tooling, process-qualification, inspection, nonconformance, serial traceability, and regulated customer-documentation requirements."
        ),
        "why_relevant": (
            "NX can support gear and tooling design plus CAM for the new equipment, while Teamcenter can control drawings, manufacturing plans, revisions, and approved data. Opcenter can capture work instructions, inspection, nonconformance, and serialized genealogy for aerospace and defence customers. The equipment purchase and installation are funded now, so digital process and quality controls can be established alongside the production capability."
        ),
        "products": ["NX", "Teamcenter", "Opcenter"],
        "scores": (92, 99, 96, 96, 96),
        "pain_signals": [
            "Must qualify new advanced equipment and precision processes for aerospace and defence gears.",
            "Must preserve regulated manufacturing and serialized quality traceability.",
        ],
        "expansion_signals": [
            "$1 million PacifiCan investment funds equipment purchase and installation.",
            "Program establishes aircraft and defence gear production in British Columbia.",
        ],
    },
]


def main() -> None:
    load_dotenv(".env")
    database = Database()
    database.initialize()
    keywords = {item.id: item for item in database.list_keywords()}
    if not {1, 2, 3, 4, 5}.issubset(keywords):
        raise RuntimeError(f"Required keyword ids are missing: {sorted(keywords)}")

    published_counts = {keyword_id: 0 for keyword_id in keywords}
    company_ids: dict[str, int] = {}

    for item in CANDIDATES:
        opportunity, manufacturing, trigger, solution, evidence = item["scores"]
        signal = ExtractedSignal(
            company_name=item["company_name"],
            company_domain=item["company_domain"],
            company_url=item["company_url"],
            linkedin_url=item["linkedin_url"],
            location=item["location"],
            industry=item["industry"],
            company_industry=item["industry"],
            software=[],
            signal_type="news",
            signal_source="news",
            pain_signals=item["pain_signals"],
            expansion_signals=item["expansion_signals"],
            raw_score=opportunity,
            confidence=evidence / 100,
            reason=item["challenge_summary"],
            source_url=item["source_url"],
            source_title=item["source_title"],
            detected_at=item["signal_date"],
        )
        database.save_signal(signal)
        database.upsert_company(signal)

        for keyword_id in item["keyword_ids"]:
            linked = database.record_keyword_company(
                keyword_id,
                item["company_name"],
                item["company_domain"],
                source_url=item["source_url"],
                source_title=item["source_title"],
                source_publisher=item["source_publisher"],
                signal_label=item["signal_label"],
                signal_date=item["signal_date"],
                challenge_summary=item["challenge_summary"],
                why_relevant=item["why_relevant"],
                recommended_products=item["products"],
                qualification_status="qualified",
                opportunity_score=opportunity,
                manufacturing_fit_score=manufacturing,
                trigger_score=trigger,
                solution_fit_score=solution,
                evidence_quality_score=evidence,
                seen_at=SEEN_AT,
            )
            if linked is None:
                raise RuntimeError(
                    f"Could not link {item['company_name']} to keyword {keyword_id}"
                )
            published_counts[keyword_id] += 1
            company_ids[item["company_name"]] = linked.company_id

    for keyword_id, result_count in published_counts.items():
        database.record_keyword_search(keyword_id, result_count=result_count)

    published = [
        row
        for row in database.list_keyword_companies(limit=5000)
        if row.qualification_status in {"qualified", "watchlist"}
    ]
    unique_company_ids = {row.company_id for row in published}
    qualified_ids = {
        row.company_id for row in published if row.qualification_status == "qualified"
    }
    print(
        {
            "published_company_ids": company_ids,
            "per_keyword_counts": published_counts,
            "published_unique": len(unique_company_ids),
            "qualified": len(qualified_ids),
            "watchlist_only": len(unique_company_ids - qualified_ids),
        }
    )


if __name__ == "__main__":
    main()
