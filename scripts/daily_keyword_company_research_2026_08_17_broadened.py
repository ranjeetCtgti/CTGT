from __future__ import annotations

import json
from datetime import datetime, timezone

from dotenv import load_dotenv

from db.database import Database
from models.schema import ExtractedSignal


RUN_AT = datetime.now(timezone.utc)


def dt(year: int, month: int, day: int) -> datetime:
    return datetime(year, month, day, tzinfo=timezone.utc)


CANDIDATES = [
    {
        "company_name": "General Fusion",
        "company_domain": "generalfusion.com",
        "company_url": "https://generalfusion.com/",
        "linkedin_url": "https://www.linkedin.com/company/general-fusion/",
        "location": "Richmond, British Columbia, Canada",
        "industry": "Fusion-energy machine development and advanced energy systems",
        "keyword_ids": [5, 8],
        "products": ["Teamcenter", "Simcenter", "Altair tools", "Polarion"],
        "scores": {"opportunity": 92, "manufacturing": 99, "trigger": 94, "solution": 95, "evidence": 99},
        "pain_signals": [
            "Must mature the operating LM26 fusion machine through increasingly demanding plasma-performance milestones while controlling a multidisciplinary hardware and test baseline.",
            "Must deploy US$150 million of new public-company capital against a milestone program extending through 2028.",
        ],
        "expansion_signals": [
            "Began Nasdaq trading with approximately US$150 million in cash for the Lawson Machine 26 program.",
            "LM26 is operating at the Vancouver-area facility and has already supported more than 200,000 plasma experiments across the company's development history.",
        ],
        "evidence": [
            {
                "signal_date": dt(2026, 7, 13),
                "source_url": "https://generalfusion.com/post/general-fusion-becomes-first-publicly-listed-fusion-company/",
                "source_title": "General Fusion Becomes First Publicly Listed Fusion Company",
                "source_publisher": "General Fusion",
                "signal_label": "Nasdaq listing supplies US$150M for LM26 fusion milestones through 2028",
                "challenge_summary": (
                    "On July 13, 2026, General Fusion began trading on Nasdaq with approximately US$150 million in cash earmarked to advance its Lawson Machine 26 program through milestones planned into 2028. The company says the operating LM26 machine at its British Columbia facility is 50% of commercial-machine diameter, recently produced 0.72 keV plasma, and is being advanced toward 1 keV, 10 keV and Lawson-criterion demonstrations after more than 200,000 plasma experiments across its development program. Inference: the funded sequence increases configuration, multidisciplinary simulation, test-instrumentation, engineering-change and verification-evidence pressure as the physical machine is repeatedly modified and validated."
                ),
                "why_relevant": (
                    "Teamcenter can govern the LM26 mechanical, electrical, controls and test configurations while preserving the released baseline for each experiment. Simcenter and Altair tools fit the structural, thermal, electromagnetic and multiphysics validation workload, and Polarion can connect milestone requirements to test procedures, defects and results. The new capital and public 2028 milestone horizon make digital-thread and simulation-scale decisions immediate."
                ),
            },
            {
                "signal_date": dt(2026, 7, 13),
                "source_url": "https://betakit.com/general-fusion-begins-trading-on-nasdaq-becomes-first-nuclear-fusion-company-to-go-public/",
                "source_title": "General Fusion begins trading on Nasdaq, becomes first nuclear fusion company to go public",
                "source_publisher": "BetaKit",
                "signal_label": "Independent report corroborates General Fusion's US$150M public-market capitalization event",
                "challenge_summary": (
                    "On July 13, 2026, BetaKit independently reported that General Fusion completed its Nasdaq transaction and expected approximately US$150 million in cash to advance the LM26 demonstration program. The report places the financing against the company's operating British Columbia fusion machine and its staged plasma-performance roadmap. Inference: investor funding now carries visible milestone and schedule accountability, increasing the cost of uncontrolled design changes, fragmented simulation evidence or slow test-to-engineering feedback."
                ),
                "why_relevant": (
                    "The corroborated financing strengthens the case for Teamcenter-backed configuration and change control rather than relying on the company announcement alone. Polarion can make milestone-to-test status auditable, while Simcenter or Altair tools can shorten analysis cycles before hardware experiments. The transaction has closed, so the engineering program is funded now rather than waiting on a prospective round."
                ),
            },
        ],
    },
    {
        "company_name": "TetraGen Robotics Inc.",
        "company_domain": "tetragen.ai",
        "company_url": "https://www.tetragen.ai/",
        "linkedin_url": "https://www.linkedin.com/company/tetragen-robotics/",
        "location": "Winnipeg, Manitoba, Canada",
        "industry": "Autonomous robotic welding systems",
        "keyword_ids": [2, 8],
        "products": ["Teamcenter", "Tecnomatix", "Polarion"],
        "scores": {"opportunity": 91, "manufacturing": 98, "trigger": 94, "solution": 90, "evidence": 96},
        "pain_signals": [
            "Must configure and commission autonomous welding cells for different customer parts, weld paths, fixtures and acceptance criteria.",
            "Must grow engineering and customer-deployment capacity without losing control of cell variants, software behavior and validation evidence.",
        ],
        "expansion_signals": ["Closed an oversubscribed C$1.8 million seed round to expand engineering, commercial activity and North American deployments."],
        "evidence": [
            {
                "signal_date": dt(2026, 8, 10),
                "source_url": "https://www.tetragen.ai/post/tetragen-robotics-closes-oversubscribed-1-8m-cad-seed-financing-round",
                "source_title": "TetraGen Robotics Closes Oversubscribed $1.8M CAD Seed Financing Round",
                "source_publisher": "TetraGen Robotics",
                "signal_label": "C$1.8M seed funds engineering growth and North American autonomous-welding deployments",
                "challenge_summary": (
                    "On August 10, 2026, Winnipeg-based TetraGen Robotics closed an oversubscribed C$1.8 million seed round led by StepChange Capital, with Emend Vision Fund and Jim Richardson participating, to expand engineering and commercial teams and deploy more autonomous welding systems across North America. Its system combines an industrial robot, proprietary artificial intelligence and 3D vision to generate welding programs without manual robot programming and adapt to production variation. Inference: supporting more heavy-equipment, mining and defence customers creates cell-configuration, fixture, weld-recipe, commissioning, change-control and acceptance-test complexity."
                ),
                "why_relevant": (
                    "Teamcenter can control customer-specific robot-cell configurations, fixtures, released drawings and engineering changes. Tecnomatix can validate reach, collision risk, sequencing and cycle time before installation, while Polarion can trace weld-quality and safety requirements to commissioning evidence. The funded team expansion and planned deployments make these controls urgent before delivery volume increases."
                ),
            }
        ],
    },
    {
        "company_name": "Dominion Dynamics",
        "company_domain": "defendthedominion.com",
        "company_url": "https://www.defendthedominion.com/",
        "linkedin_url": "https://www.linkedin.com/company/dominion-dynamics/",
        "location": "Ottawa, Ontario, Canada",
        "industry": "Uncrewed aircraft and sovereign defence systems",
        "keyword_ids": [7, 8, 9, 13],
        "products": ["Teamcenter", "Polarion", "Simcenter", "Altair tools"],
        "scores": {"opportunity": 97, "manufacturing": 98, "trigger": 98, "solution": 97, "evidence": 99},
        "pain_signals": [
            "Must move a new uncrewed aircraft from requirements and virtual prototypes to first flight while coordinating airframe, propulsion, electronics, autonomy and sovereign suppliers.",
            "Must preserve verification and configuration evidence for a defence aircraft program designed around a non-ITAR Canadian supply chain.",
        ],
        "expansion_signals": ["Committed an initial C$50 million to the Dominion Scout aircraft and targets first flight in 24 to 30 months."],
        "evidence": [
            {
                "signal_date": dt(2026, 8, 14),
                "source_url": "https://www.defendthedominion.com/news/canadas-first-ACP-is-taking-off",
                "source_title": "Canada's First ACP Is Taking Off",
                "source_publisher": "Dominion Dynamics",
                "signal_label": "C$50M Dominion Scout program targets first flight within 24-30 months",
                "challenge_summary": (
                    "On August 14, 2026, Dominion Dynamics said it had committed an initial C$50 million to develop the Dominion Scout autonomous collaborative platform, targeting first flight in 24 to 30 months with a sovereign Canadian supply chain designed to avoid U.S. International Traffic in Arms Regulations dependence. The company is defining aircraft requirements, using its AuraSim physics environment for virtual prototyping, and coordinating a Canadian drone coalition around airframe, autonomy, sensors and manufacturing. Inference: the compressed flight schedule creates immediate requirements, supplier-interface, multidisciplinary configuration, simulation-correlation, test and certification-evidence pressure."
                ),
                "why_relevant": (
                    "Teamcenter can control aircraft and supplier configurations, change status and digital product baselines. Polarion can trace mission, safety and defence requirements into verification, while Simcenter or Altair tools can complement the in-house virtual-prototyping environment for structural, aerodynamic and systems validation. The first-flight clock is already running, so design-governance and evidence practices need to mature before hardware release and test activity accelerate."
                ),
            }
        ],
    },
    {
        "company_name": "Celerity Craft",
        "company_domain": "celeritycraft.com",
        "company_url": "https://celeritycraft.com/",
        "linkedin_url": "https://www.linkedin.com/company/celerity-craft/",
        "location": "Squamish, British Columbia, Canada",
        "industry": "Electric dynamic-air-cushion marine vehicles",
        "keyword_ids": [3, 8],
        "products": ["Teamcenter", "NX", "Simcenter", "Polarion", "Tecnomatix"],
        "scores": {"opportunity": 94, "manufacturing": 99, "trigger": 97, "solution": 96, "evidence": 99},
        "pain_signals": [
            "Must scale from a 5.5-metre demonstrator to an 11.9-metre, 12-passenger commercial electric craft.",
            "Must coordinate hull, propulsion, controls, battery, certification, test and new-facility planning for first commercial production.",
        ],
        "expansion_signals": ["Launched a C$7.6 million project, including C$2.9 million from Canada's Ocean Supercluster, and a new Squamish manufacturing and innovation centre."],
        "evidence": [
            {
                "signal_date": dt(2026, 7, 28),
                "source_url": "https://oceansupercluster.ca/project/canadas-ocean-supercluster-announces-7-6m-dynamic-air-cushion-electric-vehicle-project/",
                "source_title": "Canada's Ocean Supercluster Announces $7.6M Dynamic Air Cushion Electric Vehicle Project",
                "source_publisher": "Canada's Ocean Supercluster",
                "signal_label": "C$7.6M DAC-EV project scales Celerity from demonstrator to 12-passenger commercial craft",
                "challenge_summary": (
                    "On July 28, 2026, Canada's Ocean Supercluster announced a C$7.6 million Dynamic Air Cushion Electric Vehicle project, including C$2.9 million in Supercluster support, to take Celerity Craft from a 5.5-metre demonstrator to an 11.9-metre, 12-passenger commercial water taxi and establish a manufacturing and innovation centre in Squamish. Celerity identifies the 60-knot DACV-12 as its first commercial product. Inference: scaling the platform and opening a production site at the same time creates hull, propulsion, battery, control, certification, supplier, change-control and factory-planning complexity."
                ),
                "why_relevant": (
                    "Teamcenter can govern the craft configuration, supplier data and change process; NX and Simcenter fit marine-structure, hydrodynamic and propulsion design and validation. Polarion can connect passenger-vessel requirements to tests, and Tecnomatix can plan the new assembly flow before equipment and workstations are fixed. Funding and facility work are active now, ahead of the first commercial build."
                ),
            }
        ],
    },
    {
        "company_name": "Volatus Aerospace Inc.",
        "company_domain": "volatusaerospace.com",
        "company_url": "https://volatusaerospace.com/",
        "linkedin_url": "https://www.linkedin.com/company/volatus-aerospace/",
        "location": "Toronto, Ontario, Canada",
        "industry": "Uncrewed aircraft systems and aerospace operations",
        "keyword_ids": [7, 9, 13],
        "products": ["Teamcenter", "Polarion", "Simcenter"],
        "scores": {"opportunity": 86, "manufacturing": 86, "trigger": 91, "solution": 89, "evidence": 90},
        "pain_signals": [
            "Must evaluate Canadian manufacturing, system integration, certification and support for a heavy-lift autonomous aircraft platform.",
            "Must connect wildfire payload, aircraft and operational requirements to evidence before deployment approval.",
        ],
        "expansion_signals": ["Signed an August framework with Singular Aircraft covering the 4,000-kilogram FlyOx I for Canadian wildfire response."],
        "evidence": [
            {
                "signal_date": dt(2026, 8, 4),
                "source_url": "https://www.canadianmanufacturing.com/manufacturing/volatus-aerospace-partners-with-singular-aircraft-for-heavy-lift-autonomous-aircraft-for-canadian-wildfire-response-320487/",
                "source_title": "Volatus Aerospace partners with Singular Aircraft for heavy-lift autonomous aircraft for Canadian wildfire response",
                "source_publisher": "Canadian Manufacturing",
                "signal_label": "FlyOx I framework evaluates Canadian manufacturing and integration for wildfire missions",
                "challenge_summary": (
                    "On August 4, 2026, Canadian Manufacturing reported that Volatus Aerospace and Singular Aircraft signed a framework to introduce the autonomous FlyOx I to Canada and evaluate local manufacturing, system integration, deployment and lifecycle support. The 4,000-kilogram maximum-takeoff-weight aircraft is proposed with a 1,560-litre wildfire payload, subject to certification and regulatory approval. Inference: adapting a heavy-lift platform to Canadian production and wildfire operations creates configuration, supplier, payload-interface, airworthiness, test, maintenance and support-data complexity."
                ),
                "why_relevant": (
                    "Teamcenter can control the Canadian aircraft and payload baseline, supplier data and engineering changes. Polarion can trace regulatory, safety and mission requirements to approval and test evidence, while Simcenter can support structural, loads and flight-performance validation. The parties are evaluating manufacturing and integration now, before certification and deployment decisions lock the operating model."
                ),
            }
        ],
    },
    {
        "company_name": "Tempel Canada",
        "company_domain": "tempel.com",
        "company_url": "https://www.tempel.com/",
        "linkedin_url": "https://www.linkedin.com/company/tempel/",
        "location": "Burlington, Ontario, Canada",
        "industry": "Electrical-steel laminations and transformer-core manufacturing",
        "keyword_ids": [5],
        "products": ["Teamcenter", "Opcenter", "Tecnomatix"],
        "scores": {"opportunity": 91, "manufacturing": 98, "trigger": 96, "solution": 94, "evidence": 97},
        "pain_signals": ["Must industrialize a new 250,000-square-foot electrical-steel manufacturing operation while adding equipment, processes and approximately 100 jobs."],
        "expansion_signals": ["Announced a C$132 million Burlington advanced-manufacturing investment for transformer-core capacity."],
        "evidence": [
            {
                "signal_date": dt(2026, 8, 4),
                "source_url": "https://news.ontario.ca/en/release/1007827/ontario-welcomes-132-million-advanced-manufacturing-investment-in-burlington",
                "source_title": "Ontario Welcomes $132 Million Advanced Manufacturing Investment in Burlington",
                "source_publisher": "Government of Ontario",
                "signal_label": "C$132M Burlington expansion adds 250,000 sq. ft. and roughly 100 manufacturing jobs",
                "challenge_summary": (
                    "On August 4, 2026, Ontario announced that Tempel Canada is investing C$132 million in a 250,000-square-foot Burlington advanced-manufacturing facility for transformer cores and expects to create approximately 100 jobs. The expansion introduces new production equipment, routings, quality processes and workforce at a plant serving power-grid and electrification demand. Inference: the simultaneous capacity and workforce ramp raises product-definition, process-release, factory-layout, scheduling, scrap, quality and material-traceability pressure."
                ),
                "why_relevant": (
                    "Teamcenter can govern lamination and core specifications, revisions and manufacturing definitions; Tecnomatix can validate the new line and material flow. Opcenter can control work execution, inspection, nonconformance and lot genealogy once production starts. Facility and equipment decisions are being made during the current C$132 million buildout, making engagement time-sensitive."
                ),
            }
        ],
    },
    {
        "company_name": "Accuenergy",
        "company_domain": "accuenergy.com",
        "company_url": "https://www.accuenergy.com/",
        "linkedin_url": "https://www.linkedin.com/company/accuenergy/",
        "location": "Toronto, Ontario, Canada",
        "industry": "Electrical energy-metering and monitoring hardware",
        "keyword_ids": [5, 8],
        "products": ["Teamcenter", "Opcenter", "Capital", "Polarion"],
        "scores": {"opportunity": 91, "manufacturing": 98, "trigger": 95, "solution": 94, "evidence": 98},
        "pain_signals": ["Must modernize production, expand capacity and commercialize new AI-enabled meters, panels and sensors within one C$10 million program."],
        "expansion_signals": ["Received C$2.6 million from FedDev Ontario toward a C$10 million manufacturing and product-development project."],
        "evidence": [
            {
                "signal_date": dt(2026, 7, 21),
                "source_url": "https://www.accuenergy.com/press-release/accuenergy-secures-feddev-ontario-support-for-ai-innovation-and-manufacturing-expansion/",
                "source_title": "Accuenergy Secures FedDev Ontario Support for AI Innovation and Manufacturing Expansion",
                "source_publisher": "Accuenergy",
                "signal_label": "C$2.6M federal support advances a C$10M product and factory modernization program",
                "challenge_summary": (
                    "On July 21, 2026, Accuenergy said it received C$2.6 million from FedDev Ontario toward a C$10 million program to modernize manufacturing, increase capacity and develop new AI-enabled energy meters, panels and sensors. The program combines new product variants, electronics, embedded behavior and shop-floor changes in the Toronto operation. Inference: doing product development and factory modernization together increases electrical-BOM, firmware, test, change, supplier, process-release and unit-traceability complexity."
                ),
                "why_relevant": (
                    "Teamcenter can control meter and panel variants, released bills of material and engineering changes, while Capital fits electrical architecture. Polarion can connect product requirements to firmware and hardware tests, and Opcenter can provide manufacturing execution and quality genealogy. The funded C$10 million project is underway now, so platform and process decisions are active."
                ),
            }
        ],
    },
    {
        "company_name": "Huys Industries",
        "company_domain": "huysindustries.com",
        "company_url": "https://www.huysindustries.com/",
        "linkedin_url": "https://www.linkedin.com/company/huys-industries/",
        "location": "Etobicoke, Ontario, Canada",
        "industry": "Welding consumables, electrode systems and surface-engineering equipment",
        "keyword_ids": [8],
        "products": ["Teamcenter", "Simcenter", "Polarion"],
        "scores": {"opportunity": 84, "manufacturing": 96, "trigger": 91, "solution": 87, "evidence": 98},
        "pain_signals": ["Must validate and commercialize an AI-powered electrospark-deposition welding system while controlling process parameters, hardware revisions and qualification evidence."],
        "expansion_signals": ["Received C$660,000 from FedDev Ontario within a C$1.3 million AI welding commercialization project."],
        "evidence": [
            {
                "signal_date": dt(2026, 7, 9),
                "source_url": "https://www.canada.ca/en/economic-development-southern-ontario/news/2026/07/government-of-canada-supports-etobicoke-manufacturing-business-in-adopting-ai.html",
                "source_title": "Government of Canada supports Etobicoke manufacturing business in adopting AI",
                "source_publisher": "Federal Economic Development Agency for Southern Ontario",
                "signal_label": "C$660K supports a C$1.3M AI welding-system validation and commercialization program",
                "challenge_summary": (
                    "On July 9, 2026, FedDev Ontario announced C$660,000 for Huys Industries within a C$1.3 million project to validate and commercialize an AI-powered electrospark-deposition welding system. Huys already manufactures welding consumables and equipment and performs welding-process development and simulation. Inference: moving the new system into commercial use creates hardware, consumable, process-parameter, software, test, customer-application and change-control complexity."
                ),
                "why_relevant": (
                    "Teamcenter can govern equipment, consumable and process revisions across commercialization. Simcenter or Altair tools can support the thermal and process-validation workload, while Polarion can trace application requirements and acceptance tests into validated releases. Federal project funding is committed now, creating a defined validation and commercialization window."
                ),
            }
        ],
    },
    {
        "company_name": "Pratt & Whitney",
        "company_domain": "prattwhitney.com",
        "company_url": "https://www.prattwhitney.com/",
        "linkedin_url": "https://www.linkedin.com/company/pratt-&-whitney-canada/",
        "location": "Longueuil, Quebec, Canada",
        "industry": "Aircraft-engine design and manufacturing",
        "keyword_ids": [9, 10, 12],
        "products": ["Teamcenter", "Opcenter"],
        "scores": {"opportunity": 96, "manufacturing": 100, "trigger": 98, "solution": 100, "evidence": 98},
        "pain_signals": ["Must execute PLM and MES deployments across complex engine-manufacturing programs while preserving traceability, compliance, efficiency and site integration."],
        "expansion_signals": ["Opened a May 27, 2026 Longueuil project-manager requisition dedicated to PLM and MES deployments."],
        "evidence": [
            {
                "signal_date": dt(2026, 5, 27),
                "source_url": "https://globalhr.wd5.myworkdayjobs.com/en-US/REC_RTX_Ext_Gateway/job/Project-Manager_01840761",
                "source_title": "Project Manager - Digital Manufacturing Transformation",
                "source_publisher": "Pratt & Whitney Canada Careers",
                "signal_label": "P&WC is staffing PLM and MES deployments for complex manufacturing programs",
                "challenge_summary": (
                    "On May 27, 2026, Pratt & Whitney Canada posted Longueuil requisition 01840761 for a Project Manager responsible for executing product-lifecycle-management and manufacturing-execution-system deployments across complex manufacturing programs. The official posting explicitly ties the work to traceability, compliance, efficiency, operational planning, execution, site integration and enterprise alignment. This is direct evidence of an active digital-manufacturing deployment rather than an inferred future need."
                ),
                "why_relevant": (
                    "Teamcenter and Opcenter are the smallest defensible solution set because the role explicitly covers PLM and MES delivery. CTGTI can support deployment architecture, product-to-production data handoffs, configuration governance, traceability and site rollout without proposing unrelated products. The company is hiring the delivery owner now, indicating an immediate capacity and implementation window."
                ),
            }
        ],
    },
]


KEYWORD1_HIDE_IDS = {
    2102, 2096, 2104, 1750, 1776, 2053, 2185, 2195, 2107, 2091,
    1828, 2171, 2101, 1874, 2058, 1882, 2191, 2097, 2075, 2194,
    2173, 220, 2174, 2057, 2179, 2077, 2106, 432, 2156, 2169,
    1963, 2184, 2098, 2095, 2157, 2187, 2188, 2155, 2056, 2076,
}

KEYWORD2_HIDE_REASONS = {
    2175: "Atlas Engineered Products manufactures building components and is using automation; it is not a robotics startup selling a robotic product.",
    2176: "Huys Industries is an established welding-products manufacturer commercializing an AI welding system, not a robotics startup.",
    2194: "Mahler Machining is a precision manufacturer adopting automation, not a robotics startup.",
    220: "MDA Space is a mature public aerospace prime with space-robotics products, not a startup.",
    2124: "International Submarine Engineering is a long-established underwater-vehicle manufacturer, not a startup.",
}


COVERAGE = {
    1: (14, 12, 2, ["Startup Gallery", "X.com", "BetaKit", "NGen", "SpaceQ", "AIAC", "ventureLAB", "Velocity", "HAX", "BDC Capital"]),
    2: (18, 12, 5, ["Startup Gallery", "X.com", "BetaKit", "NGen", "Automate Canada", "ventureLAB", "Velocity", "HAX", "BDC Capital"]),
    3: (12, 8, 3, ["Startup Gallery", "X.com", "BetaKit", "NGen", "Canada's Ocean Supercluster", "Naval News", "Marine Log", "Shipbuilding Association of Canada"]),
    4: (14, 10, 4, ["Startup Gallery", "X.com", "BetaKit", "NGen", "OVIN", "APMA", "Electric Autonomy Canada", "BDC Capital"]),
    5: (15, 8, 4, ["Startup Gallery", "X.com", "BetaKit", "NGen", "Government of Canada", "Ontario Newsroom", "BDC Capital", "Canadian Manufacturing"]),
    7: (16, 9, 5, ["Startup Gallery", "X.com", "BetaKit", "NGen", "SpaceQ", "AIAC", "Skies Magazine", "ventureLAB", "Velocity", "Government of Canada"]),
    8: (24, 12, 6, ["Startup Gallery", "X.com", "BetaKit", "NGen", "ventureLAB Hardware Catalyst", "HAX", "Velocity", "Centech", "BDC Capital", "FedDev Ontario"]),
    9: (20, 10, 7, ["Startup Gallery", "X.com", "BetaKit", "NGen", "SpaceQ", "AIAC", "Skies Magazine", "Canadian Manufacturing", "Government of Canada"]),
    10: (15, 8, 6, ["Startup Gallery", "X.com", "BetaKit", "NGen", "SpaceQ", "AIAC", "Skies Magazine", "Canadian Manufacturing", "Government of Canada"]),
    11: (12, 8, 4, ["Startup Gallery", "X.com", "BetaKit", "NGen", "OVIN", "APMA", "Electric Autonomy Canada", "Ontario Newsroom"]),
    12: (12, 8, 3, ["Startup Gallery", "X.com", "BetaKit", "NGen", "Pratt & Whitney Careers", "Canadian Manufacturing", "Government of Canada"]),
    13: (17, 8, 7, ["Startup Gallery", "X.com", "BetaKit", "NGen", "SpaceQ", "AIAC", "OVIN", "Electric Autonomy Canada", "Government of Canada"]),
}


BLOCKERS = (
    "X.com was inaccessible because the public search presented ERR_CERT_AUTHORITY_INVALID. "
    "Bing presented a human-verification challenge, Centech and Marine Log presented browser-security verification, "
    "and the Shipbuilding Association domain did not resolve; none was bypassed."
)


def make_signal(candidate: dict[str, object], evidence: dict[str, object]) -> ExtractedSignal:
    scores = candidate["scores"]
    source = str(evidence["source_publisher"])
    signal_type = "job_posting" if "Careers" in source else "news"
    return ExtractedSignal(
        company_name=str(candidate["company_name"]),
        company_domain=str(candidate["company_domain"]),
        company_url=str(candidate["company_url"]),
        linkedin_url=str(candidate["linkedin_url"]),
        location=str(candidate["location"]),
        industry=str(candidate["industry"]),
        company_industry=str(candidate["industry"]),
        software=[],
        signal_type=signal_type,
        signal_source="career_page" if signal_type == "job_posting" else "news",
        pain_signals=list(candidate["pain_signals"]),
        expansion_signals=list(candidate["expansion_signals"]),
        raw_score=int(scores["opportunity"]),
        confidence=int(scores["evidence"]) / 100,
        reason=str(evidence["challenge_summary"]),
        source_url=str(evidence["source_url"]),
        source_title=str(evidence["source_title"]),
        detected_at=evidence["signal_date"],
    )


def disqualify_row(database: Database, row, reason: str) -> None:
    database.record_keyword_company(
        row.keyword_id,
        row.company_name,
        row.company_domain,
        source_url=row.source_url,
        source_title=row.source_title,
        source_publisher=row.source_publisher,
        signal_label="Existing record hidden after exact keyword-fit reassessment",
        signal_date=row.signal_date,
        challenge_summary=reason,
        why_relevant="The company may remain valid under another saved keyword, but this keyword-company link does not pass the exact saved-keyword gate and must remain hidden.",
        recommended_products=row.recommended_products,
        qualification_status="disqualified",
        opportunity_score=min(row.opportunity_score, 30),
        manufacturing_fit_score=row.manufacturing_fit_score,
        trigger_score=min(row.trigger_score, 20),
        solution_fit_score=row.solution_fit_score,
        evidence_quality_score=row.evidence_quality_score,
        seen_at=RUN_AT,
    )


def main() -> None:
    load_dotenv(".env")
    database = Database()
    database.initialize()
    keywords = {item.id: item for item in database.list_keywords()}
    if set(keywords) != set(COVERAGE):
        raise RuntimeError(f"Persistent keyword set changed: {sorted(keywords)}")

    published_counts = {keyword_id: 0 for keyword_id in keywords}
    signal_results: list[dict[str, object]] = []
    linked_results: list[dict[str, object]] = []

    for candidate in CANDIDATES:
        for evidence in candidate["evidence"]:
            saved, company = database.persist_signal(make_signal(candidate, evidence))
            signal_results.append({
                "company": candidate["company_name"],
                "source_url": evidence["source_url"],
                "created": saved.created,
                "duplicate_url": saved.duplicate_url,
                "company_domain": company.company_domain,
            })

        primary = candidate["evidence"][0]
        scores = candidate["scores"]
        for keyword_id in candidate["keyword_ids"]:
            linked = database.record_keyword_company(
                keyword_id,
                str(candidate["company_name"]),
                str(candidate["company_domain"]),
                source_url=str(primary["source_url"]),
                source_title=str(primary["source_title"]),
                source_publisher=str(primary["source_publisher"]),
                signal_label=str(primary["signal_label"]),
                signal_date=primary["signal_date"],
                challenge_summary=str(primary["challenge_summary"]),
                why_relevant=str(primary["why_relevant"]),
                recommended_products=list(candidate["products"]),
                qualification_status="qualified",
                opportunity_score=int(scores["opportunity"]),
                manufacturing_fit_score=int(scores["manufacturing"]),
                trigger_score=int(scores["trigger"]),
                solution_fit_score=int(scores["solution"]),
                evidence_quality_score=int(scores["evidence"]),
                seen_at=RUN_AT,
            )
            if linked is None:
                raise RuntimeError(f"Could not link {candidate['company_name']} to keyword {keyword_id}")
            published_counts[keyword_id] += 1
            linked_results.append({"keyword_id": keyword_id, "company_id": linked.company_id, "company": linked.company_name})

    hidden: list[dict[str, object]] = []
    rows = database.list_keyword_companies(limit=1000)
    for row in rows:
        if row.keyword_id == 1 and row.company_id in KEYWORD1_HIDE_IDS and row.qualification_status in {"qualified", "watchlist"}:
            reason = (
                f"{row.company_name} was not verified as a Canadian aerospace startup formed during the last month. "
                "Its manufacturing or engineering evidence may qualify it for broader aerospace keywords, but no July/August 2026 company-formation evidence supports this exact keyword."
            )
            disqualify_row(database, row, reason)
            hidden.append({"keyword_id": 1, "company_id": row.company_id, "company": row.company_name})
        elif row.keyword_id == 2 and row.company_id in KEYWORD2_HIDE_REASONS and row.qualification_status in {"qualified", "watchlist"}:
            disqualify_row(database, row, KEYWORD2_HIDE_REASONS[row.company_id])
            hidden.append({"keyword_id": 2, "company_id": row.company_id, "company": row.company_name})

    for keyword_id, result_count in published_counts.items():
        database.record_keyword_search(keyword_id, result_count=result_count)

    per_keyword = {}
    for keyword_id, (reviewed, rejected, duplicates, sources) in COVERAGE.items():
        hidden_count = sum(1 for item in hidden if item["keyword_id"] == keyword_id)
        per_keyword[str(keyword_id)] = {
            "keyword": keywords[keyword_id].keyword,
            "lookback": "rolling 30 days, then 180-day fallback for ongoing evidence",
            "sources_checked": sources,
            "startup_gallery": "checked directly; no relevant qualifying physical-product candidate",
            "x_com": "inaccessible: ERR_CERT_AUTHORITY_INVALID",
            "candidates_reviewed": reviewed,
            "rejected_before_persistence": rejected,
            "qualified_published": published_counts[keyword_id],
            "watchlist_published": 0,
            "existing_records_upgraded_or_hidden": hidden_count,
            "duplicates_skipped": duplicates,
            "blockers": BLOCKERS,
        }

    print(json.dumps({
        "run_at": RUN_AT,
        "persistent_keywords_loaded": len(keywords),
        "signals": signal_results,
        "keyword_links": linked_results,
        "hidden_links": hidden,
        "per_keyword": per_keyword,
    }, default=str, indent=2))


if __name__ == "__main__":
    main()
