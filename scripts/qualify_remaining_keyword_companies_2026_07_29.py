from __future__ import annotations

from datetime import datetime, timezone

from dotenv import load_dotenv

from db.database import Database
from models.schema import ExtractedSignal


def dt(value: str | None) -> datetime | None:
    return datetime.fromisoformat(f"{value}T12:00:00+00:00") if value else None


def q(
    status: str,
    label: str,
    challenge: str,
    relevance: str,
    products: list[str],
    scores: tuple[int, int, int, int, int],
    *,
    url: str | None = None,
    title: str | None = None,
    publisher: str | None = None,
    date: str | None = None,
) -> dict:
    return {
        "qualification_status": status,
        "signal_label": label,
        "challenge_summary": challenge,
        "why_relevant": relevance,
        "recommended_products": products,
        "opportunity_score": scores[0],
        "manufacturing_fit_score": scores[1],
        "trigger_score": scores[2],
        "solution_fit_score": scores[3],
        "evidence_quality_score": scores[4],
        "source_url": url,
        "source_title": title,
        "source_publisher": publisher,
        "signal_date": date,
    }


P = ["Teamcenter", "NX", "Capital", "Polarion", "Simcenter", "Opcenter"]
R = ["Teamcenter", "NX", "Capital", "Polarion", "Simcenter"]


DECISIONS = {
    "Sanad Labs": q(
        "disqualified", "Medical-robot claim remains unsupported by verifiable product evidence",
        "The company profile claims AI medical robots for mobility support, but no product specification, prototype, regulatory pathway, deployment, funding event, manufacturing operation, or active official product page could be verified after a second review.",
        "A medical robot would be relevant to controlled product development, but this entry does not provide enough evidence that a real manufacturing prospect exists. It is removed from the visible prospect list rather than published on speculation.",
        [], (18, 20, 2, 35, 28),
    ),
    "Nubonetics": q(
        "disqualified", "Enterprise AI automation consultancy, not a robot manufacturer",
        "Nubonetics markets AI agents, cloud-agnostic software, analytics, enterprise integration, and robotic-intelligence consulting. Its site does not show a proprietary physical robot, production operation, or hardware commercialization program.",
        "The offer is software and implementation work rather than a repeatable manufactured product, so it fails the manufacturing gate despite using robotics terminology.",
        ["Mendix", "RapidMiner"], (20, 3, 18, 35, 94),
        url="https://www.nubonetics.com/", title="Nubonetics AI agents and automation services",
        publisher="Nubonetics",
    ),
    "smartARM": q(
        "qualified", "AI-vision prosthetic arm entered Canadian beta",
        "smartARM is onboarding Canadian beta users for a multi-articulating prosthetic hand with an onboard camera, AI vision processor, wireless updates, 365+ recognized objects, and a 12–16 hour battery target. Moving from prototype work into fitted beta use creates regulated hardware, software, test, configuration, and service feedback loops.",
        "Teamcenter can govern device variants and design history; NX and Simcenter support the mechanical hand and load validation; Capital and Polarion connect electronics, embedded behavior, requirements, risk, verification, and beta issues; Opcenter can support controlled assembly as the device approaches launch.",
        P, (93, 98, 95, 99, 99),
        url="https://smartarm.ca/", title="smartARM — AI-vision prosthetic arm beta in Canada",
        publisher="smartARM", date="2026-07-23",
    ),
    "Advanced Intelligent Systems": q(
        "watchlist", "Modular autonomous robot hardware confirmed; no recent scale trigger",
        "AIS develops configurable autonomous robots from reusable mechanical, electrical, sensing, autonomy, and software modules, including mobile material-handling and agricultural platforms. The official news stream is active as a product site but its latest clearly dated commercialization announcements remain from 2021.",
        "Its module library and customized robot variants are a strong Teamcenter, NX, Capital, Polarion, and Simcenter fit. A new order, production expansion, hiring wave, or deployment should trigger direct outreach.",
        R, (61, 88, 22, 94, 91),
        url="https://www.ai-systems.ca/", title="Advanced Intelligent Systems modular autonomous robots",
        publisher="Advanced Intelligent Systems",
    ),
    "Roid": q(
        "disqualified", "Unverifiable directory identity with no defensible manufacturer",
        "Searches for the exact Canadian robotics company identity did not produce an official company site, physical product, team, facility, deployment, or current corporate evidence. The source appears to be a thin directory-only record.",
        "Without a resolvable company identity or product evidence, assigning Siemens products or a buying need would be invented. The record is excluded until rediscovered with primary evidence.",
        [], (5, 0, 0, 0, 25),
    ),
    "Shift Reality": q(
        "disqualified", "XR/software studio rather than a physical-product manufacturer",
        "The verifiable offering centers on virtual, augmented, and mixed-reality experiences and software services. No proprietary manufactured robot, aerospace component, factory operation, or current hardware scale-up program was found.",
        "XR content and project services do not meet the end-manufacturer qualification gate.",
        ["Mendix"], (16, 3, 12, 25, 60),
    ),
    "Domestic Robot Appliances": q(
        "disqualified", "Historical directory entry without an active product operation",
        "The record describes a domestic-robot concept, but the review found no active official product site, supported commercial model, current team, production operation, deployment, or recent trigger.",
        "A concept-level directory entry is not enough to establish a live manufacturer or a PLM buying event.",
        [], (12, 20, 0, 30, 32),
    ),
    "MomCorp Inc.": q(
        "disqualified", "No verifiable Canadian robotics manufacturer identity",
        "The name did not resolve to a credible Canadian robotics company with a proprietary product, official domain, operating team, manufacturing activity, or current commercial evidence.",
        "This is treated as directory noise because the identity cannot be validated without inventing a company match.",
        [], (3, 0, 0, 0, 20),
    ),
    "Loop Parking": q(
        "disqualified", "Parking-intelligence SaaS and marketplace, not a robot maker",
        "Loop Parking operates ParkVue/ParkSense+, an AI parking detection and enforcement platform, plus a parking-space marketplace. A student capstone explored a mobile enforcement robot, but the company itself is documented as a software and computer-vision business rather than a manufacturer.",
        "Its current 30-million-image milestone validates software adoption, not a repeatable physical product operation. The company fails the manufacturing gate.",
        ["Mendix", "RapidMiner"], (30, 5, 70, 45, 94),
        url="https://citm.ca/clients/loop-parking/", title="Loop Parking client profile",
        publisher="Centre for Integrated Transportation and Mobility", date="2026-04-01",
    ),
    "Kobotik Inc.": q(
        "disqualified", "No active proprietary robot or manufacturing evidence",
        "The exact company identity could not be tied to a current official product catalogue, operating facility, deployment, production milestone, or recent commercial activity.",
        "The directory listing alone cannot support a credible PLM opportunity.",
        [], (8, 10, 0, 18, 28),
    ),
    "Neptune Robots": q(
        "disqualified", "Unverified robotics directory record",
        "No current official company, proprietary robot specification, customer deployment, production operation, or commercial trigger could be verified for the exact Canadian identity.",
        "The record lacks the primary evidence required for publication as a potential manufacturing client.",
        [], (8, 10, 0, 18, 25),
    ),
    "YPC Technologies": q(
        "watchlist", "Robotic kitchen platform confirmed; newest public company news is old",
        "YPC has developed compact robotic kitchens combining appliances, robotics, vision, and AI to automate 80–100% of meal preparation with restaurant-scale throughput in under 80 square feet. Its official news page, however, still centers on the 2020 seed round and early pilots.",
        "The mechatronic kitchen and recipe/product variants fit Teamcenter, NX, Capital, Polarion, Simcenter, and Opcenter, but a current deployment, certification, order, hiring, or production-ramp event is needed before prioritizing outreach.",
        P, (62, 91, 18, 96, 93),
        url="https://www.ypc-technologies.com/our-technology", title="YPC robotic kitchen technology",
        publisher="YPC Technologies",
    ),
    "METEOR CRUISER TECHNOLOGIES Inc": q(
        "disqualified", "No verifiable active aerospace product company",
        "The exact identity did not resolve to a current official product site, engineering program, prototype, certification activity, team, facility, or funding and production evidence.",
        "A speculative directory identity cannot be converted into a qualified aerospace manufacturing prospect.",
        [], (6, 8, 0, 15, 24),
    ),
    "Vibraint AI": q(
        "disqualified", "AI/software profile without a physical product operation",
        "Available evidence describes AI capabilities but does not establish a proprietary manufactured robot, aerospace system, industrial hardware line, or production-scale operation.",
        "Software-only companies are outside this manufacturing-focused prospect gate.",
        ["RapidMiner", "Mendix"], (18, 2, 15, 30, 48),
    ),
    "Sami Agtech": q(
        "watchlist", "Agricultural automation concept appears relevant but lacks a current trigger",
        "The company is associated with agricultural automation and robotics, but public evidence does not yet show a recent commercial deployment, production ramp, financing, certification, or detailed product release.",
        "If its physical ag-robot platform is active, Teamcenter, NX, Capital, Polarion, and Simcenter would address multidisciplinary variants and field validation. It remains a lower-confidence watchlist account.",
        R, (47, 66, 8, 76, 42),
    ),
    "teaBOT": q(
        "watchlist", "Connected robotic beverage appliance confirmed; no recent expansion trigger",
        "teaBOT builds automated loose-leaf tea dispensing appliances combining ingredient handling, controls, connectivity, and a customer interface. The review confirmed the physical product but not a recent production, funding, facility, or major fleet expansion announcement.",
        "Solid Edge and Teamcenter could control enclosure, dispenser, electronics, recipe, and service variants; Capital and Polarion could link controls and software requirements. Outreach should wait for a fresh scale trigger.",
        ["Solid Edge", "Teamcenter", "Capital", "Polarion"], (54, 72, 16, 80, 68),
    ),
    "Obruta Space Solutions": q(
        "qualified", "Named a 2026 Top Moonshot Venture amid international demand",
        "Obruta is developing autonomous rendezvous, proximity-operations, and docking systems for spacecraft servicing and orbital logistics. In May 2026 it was named one of NACO's 27 Top Moonshot Ventures while reporting strong U.S. and European demand for its self-driving spacecraft platform.",
        "Space-qualified docking hardware, sensors, guidance software, RF, simulation, and safety-critical verification create an immediate digital-thread need. Teamcenter, NX, Capital, Polarion, and Simcenter can govern requirements, interfaces, test evidence, configuration, and partner data.",
        R, (91, 94, 92, 99, 91),
        url="https://www.cbinsights.com/company/obruta-space-solutions",
        title="Obruta Space Solutions 2026 company and news profile", publisher="CB Insights",
        date="2026-05-06",
    ),
    "Open Ocean Robotics": q(
        "qualified", "2026 U.S. operating permit supports expanding autonomous-vessel deployments",
        "Open Ocean Robotics manufactures solar-powered uncrewed surface vessels with configurable sensors, edge AI, communications, and a command portal. A 2026 commercial-activity permit at Pillar Point Harbor supports ongoing U.S. operations alongside defence, security, research, and offshore deployments.",
        "A multi-mission USV fleet creates hull, propulsion, energy, sensor-payload, software, mission-configuration, test, and service traceability needs suited to Teamcenter, NX, Capital, Polarion, Simcenter, and Opcenter.",
        P, (88, 96, 82, 98, 96),
        url="https://www.openoceanrobotics.com/", title="Open Ocean Robotics autonomous uncrewed surface vehicles",
        publisher="Open Ocean Robotics", date="2026-01-01",
    ),
    "Kraftgene AI Inc.": q(
        "disqualified", "AI company without verified manufactured hardware",
        "The available profile does not demonstrate a proprietary robot, regulated device, aerospace component, production facility, or current physical-product commercialization program.",
        "AI software alone does not satisfy the manufacturing-client requirement.",
        ["RapidMiner", "Mendix"], (16, 2, 10, 28, 42),
    ),
    "Mirsee Robotics Inc.": q(
        "watchlist", "Robotics identity is credible but current commercial evidence is thin",
        "Mirsee is associated with robotics and machine-vision development, but the review did not find a sufficiently detailed 2025–2026 deployment, production, funding, or hiring trigger.",
        "A physical vision-guided robot can fit Teamcenter, NX, Capital, Polarion, and Simcenter, but the account should remain on watch until product and scale evidence improves.",
        R, (46, 63, 8, 74, 44),
    ),
    "Cobionix Corporation": q(
        "qualified", "Codi medical cobot selected as a 2026 SXSW Pitch finalist",
        "Cobionix is developing Codi, an autonomous medical cobot integrating medical-grade mechanics, novel sensors, AI, and application software for clinician-robot collaboration. Its selection for the 2026 SXSW Pitch program is a current commercialization and visibility trigger.",
        "Medical certification, risk management, requirements, sensor and arm interfaces, verification, software releases, and device configuration strongly fit Teamcenter, NX, Capital, Polarion, and Simcenter.",
        R, (89, 95, 87, 99, 96),
        url="https://sxsw.com/wp-content/uploads/2026/03/2026-SXSW-Pitch-Finalists-and-Alternates.pdf",
        title="2026 SXSW Pitch finalists and alternates", publisher="SXSW", date="2026-03-01",
    ),
    "Trexo Robotics": q(
        "qualified", "Actively hiring embedded talent to launch new powered exoskeleton products",
        "Trexo builds powered pediatric gait-training exoskeletons and in 2025 advertised embedded development work spanning the complete robot software stack, hardware collaboration, and launch of new products. Its device is also part of a documented 2026–2027 clinical research project.",
        "Wearable robotics requires strict requirements, risk, mechanical/electrical configuration, embedded release, verification, service, and patient-specific traceability. Teamcenter, NX, Capital, Polarion, and Simcenter map directly to those pressures.",
        R, (87, 97, 84, 99, 91),
        url="https://shared.ontariotechu.ca/shared/faculty/fhs/documents-and-program-maps/research-practicum/2026-2027-research-practicum-projects.pdf",
        title="2026–2027 research project: Trexo robotic gait trainer", publisher="Ontario Tech University",
        date="2026-03-01",
    ),
    "Point.Laz": q(
        "disqualified", "Point-cloud software profile, not a manufacturer",
        "The available evidence indicates a digital point-cloud or geospatial software offering and does not show proprietary manufactured equipment, a production operation, or hardware scale-up.",
        "It may have analytics needs but does not fit the physical-product manufacturer gate.",
        ["Mendix", "RapidMiner"], (15, 2, 10, 28, 40),
    ),
    "Haply Robotics": q(
        "qualified", "NVIDIA physical-AI launch at CES 2026 plus 2026 financing",
        "Haply introduced touch-enabled physical-AI training with NVIDIA Isaac Sim at CES 2026, using its Inverse3 force-feedback hardware for robot demonstration and data collection. The company also launched HARP workflows and reported a May 2026 seed financing.",
        "Rapid expansion across haptic devices, electronics, robotics integrations, firmware, simulation, and application variants creates strong requirements, BOM, test, supplier, and release-control needs for Teamcenter, NX, Capital, Polarion, and Simcenter.",
        R, (96, 98, 98, 99, 99),
        url="https://www.haply.co/blog/haply-robotics-and-nvidia-introduce-touch-enabled-physical-ai-training-at-ces-2026",
        title="Haply Robotics and NVIDIA introduce touch-enabled physical AI at CES 2026",
        publisher="Haply Robotics", date="2025-12-17",
    ),
    "Upside Robotics": q(
        "disqualified", "No current active manufacturer could be verified",
        "The exact Canadian company identity did not yield a current official product, operating team, physical deployment, production activity, or recent corporate trigger.",
        "The source is insufficient to support a real manufacturing opportunity.",
        [], (7, 10, 0, 16, 27),
    ),
    "Swap Robotics": q(
        "qualified", "Dozens of solar-site robots operating after $15M raised",
        "Swap Robotics reports dozens of heavy-duty robots operating on utility-scale solar sites across Canada and the United States for vegetation cutting, module installation, and materials staging, backed by $15M from strategic solar-industry investors.",
        "Scaling multiple robot applications and site configurations creates mechanical, electrical, autonomy, safety, supplier, fleet, and service-configuration complexity suited to Teamcenter, NX, Capital, Polarion, Simcenter, and Opcenter.",
        P, (91, 100, 88, 99, 94),
        url="https://www.swaprobotics.com/about", title="Swap Robotics solar robotics platform and deployments",
        publisher="Swap Robotics", date="2026-07-01",
    ),
    "Human in Motion Robotics": q(
        "watchlist", "Powered exoskeleton manufacturer remains active; urgency not yet specific",
        "Human in Motion Robotics develops wearable lower-limb exoskeleton technology and remains active in the 2026 Canadian science and technology ecosystem. The review did not locate a sufficiently specific new product, regulatory, production, or deployment milestone.",
        "The regulated electromechanical device is a strong Teamcenter, NX, Capital, Polarion, and Simcenter fit, but a current commercialization trigger is needed for priority outreach.",
        R, (60, 94, 18, 98, 63),
        url="https://akcse.ca/download/2026/CKC2026_IndustryForum_v3.pdf",
        title="2026 Canada–Korea Conference industry forum program", publisher="AKCSE", date="2026-07-01",
    ),
    "TABAQ Smart Aerotech Manufacturing Inc.": q(
        "disqualified", "Aerospace NDT and planned service expansion, not a proprietary manufacturer",
        "TABAQ promotes non-destructive testing services, an AMO certification initiative, and plans for heat treatment, coatings, and precision-manufacturing services. The current offering is inspection and contract process support rather than a proprietary repeatable aerospace product.",
        "The company may be an aerospace supplier or service partner, but it does not match the target end-manufacturer profile for this campaign.",
        ["Opcenter", "Teamcenter"], (38, 32, 55, 58, 86),
        url="https://www.linkedin.com/posts/tabaq-sam_welcome-to-tabaqs-official-linkedin-page-activity-7375342544341135360-Fvvd",
        title="TABAQ aerospace NDT services and planned capabilities", publisher="TABAQ", date="2025-10-01",
    ),
    "C3RiOS Systems Inc.": q(
        "disqualified", "Systems/software business without verified manufacturing",
        "The available company evidence centers on systems and technology services and does not establish a proprietary physical aerospace or robotic product, production facility, or current manufacturing ramp.",
        "A service-led systems company does not pass the physical-product gate.",
        ["Polarion", "Mendix"], (22, 8, 15, 40, 44),
    ),
    "Green Aerospace": q(
        "disqualified", "Aerospace sales and service identity, not a product manufacturer",
        "The company is documented as an aerospace parts, equipment, or service business rather than the designer and manufacturer of a proprietary aircraft or component family.",
        "Distribution and service activity is excluded from the target manufacturing prospect list.",
        [], (20, 8, 18, 25, 48),
    ),
    "Evio": q(
        "qualified", "Hybrid-electric regional aircraft launched with 450 conditional orders",
        "EVIO emerged from stealth with the clean-sheet EVIO 810, a 50–100 seat hybrid-electric regional aircraft, 450 conditional purchase agreements and options, Boeing investment and technical support, and Pratt & Whitney Canada propulsion collaboration. Entry into service is targeted for the early 2030s.",
        "A clean-sheet aircraft program creates immediate requirements, configuration, aerodynamic and structural simulation, propulsion and electrical architecture, supplier, certification, manufacturing-planning, and program-data needs across Teamcenter, NX, Capital, Polarion, Simcenter, Tecnomatix, and Opcenter.",
        P + ["Tecnomatix"], (99, 100, 100, 100, 100),
        url="https://evio.aero/evio-launches-hybrid-electric-aircraft-program-with-450-pre-orders/",
        title="EVIO launches hybrid-electric aircraft program with 450 pre-orders",
        publisher="EVIO", date="2025-12-11",
    ),
    "Aviya Aerospace Systems": q(
        "disqualified", "Aerospace engineering and technical-services provider",
        "Aviya provides engineering, certification, project, and technical support services to aerospace clients. The review did not establish a proprietary manufactured aircraft or component line being scaled by Aviya itself.",
        "This is a consultancy/service provider rather than the target end manufacturer.",
        ["NX", "Simcenter", "Polarion"], (36, 20, 35, 62, 80),
    ),
    "Xubin Aerospace": q(
        "qualified", "2026 defence cohort follows investment and field-testing milestones",
        "Xubin is advancing Eagle Vision, a portable edge-AI counter-UAS sensor that detects aerodynamic signatures using EO/IR hardware. It reached TRL 5 and one-kilometre detection with early hardware, secured strategic investment, joined Vimy Forge in February 2026, and is pursuing operational pilots with defence and critical-infrastructure users.",
        "Scaling sensor configurations from prototypes to fieldable defence systems creates optics, enclosure, compute, thermal, electrical, software, requirements, interface, and test traceability needs for Teamcenter, NX, Capital, Polarion, and Simcenter.",
        R, (93, 94, 95, 99, 98),
        url="https://xubinaerospace.com/", title="Xubin Aerospace Eagle Vision and 2026 program milestones",
        publisher="Xubin Aerospace", date="2026-02-10",
    ),
    "LUNR Aerospace": q(
        "watchlist", "Canadian commercial-launch program pursuing federal defence funding",
        "LUNR describes itself as a Canadian commercial launch company and is actively pursuing Canadian IDEaS funding in 2026. Public evidence does not yet provide enough detail on a manufactured launch vehicle, completed subsystem, test campaign, facility, or contracted mission.",
        "Launch systems would be an exceptional Teamcenter, NX, Capital, Polarion, and Simcenter fit, but the program needs a verified hardware and test milestone before qualification.",
        R, (57, 72, 42, 94, 65),
        url="https://lobbycanada.gc.ca/app/secure/ocl/lrs/do/rgstrnSubjctMttrDtls?regId=989339",
        title="LUNR Aerospace federal funding activity", publisher="Office of the Commissioner of Lobbying of Canada",
        date="2026-05-01",
    ),
    "XR Operations": q(
        "disqualified", "Extended-reality software and services, not manufacturing",
        "XR Operations provides digital training or extended-reality capabilities; no proprietary aircraft, robot, industrial hardware family, or manufacturing operation was verified.",
        "A software/service company does not meet the target manufacturing gate.",
        ["Mendix"], (18, 2, 20, 30, 55),
    ),
    "ALUULA Composites": q(
        "qualified", "Record Q2 revenue growth and $14.1M financing support scale-up",
        "ALUULA develops and produces high-performance composite materials. In 2026 it closed an upsized $14.1M financing, announced an advanced-materials collaboration, and reported record Q2 revenue above $3M—up 94%—showing active product and operational scale.",
        "Rapid materials commercialization creates formulation, process, test, certification, customer-variant, supplier, and production traceability needs. Teamcenter, Simcenter, Opcenter, NX, and Polarion can connect material definitions and qualification evidence to controlled production.",
        ["Teamcenter", "Simcenter", "Opcenter", "NX", "Polarion"], (94, 100, 98, 96, 100),
        url="https://aluula.com/press-releases/", title="ALUULA Composites 2026 press releases",
        publisher="ALUULA Composites", date="2026-06-24",
    ),
    "RFQ2GO": q(
        "disqualified", "Digital RFQ/procurement platform, not a manufacturer",
        "The offering is a software workflow for sourcing, quotations, or procurement. It does not operate a proprietary physical-product manufacturing program.",
        "A procurement SaaS tool is outside the end-manufacturer target profile.",
        ["Mendix"], (15, 0, 15, 25, 55),
    ),
    "4pi Lab": q(
        "watchlist", "Space-based wildfire sensor product confirmed; fresh scale trigger not found",
        "4pi Lab is developing space-based early-wildfire-detection technology with onboard processing and a satellite mission concept. Its current site confirms an active physical space product but does not document a recent funding, launch contract, completed spacecraft, or production milestone.",
        "A sensor satellite combines structures, thermal design, optics, electronics, embedded intelligence, communications, and mission requirements—well suited to Teamcenter, NX, Capital, Polarion, and Simcenter once a launch or build milestone appears.",
        R, (60, 84, 18, 97, 72),
        url="https://site.4pilab.com/", title="4pi Lab space-based early wildfire detection",
        publisher="4pi Lab", date="2026-07-01",
    ),
    "HydroGraph": q(
        "qualified", "Plans 40,000-square-foot plant for up to 360 tonnes of graphene",
        "HydroGraph is a commercial producer of 99.8% pure fractal graphene using modular Hyperion reactors. In July 2026 it disclosed a planned 40,000-square-foot Texas manufacturing facility with initial reactor capacity scaling toward roughly 360 tonnes annually, alongside new qualified compounding partners.",
        "The facility and partner ramp create urgent equipment, process recipe, quality, batch, specification, customer-variant, commissioning, and supply-chain controls suited to Teamcenter, Opcenter, Tecnomatix, Simcenter, and Polarion.",
        ["Teamcenter", "Opcenter", "Tecnomatix", "Simcenter", "Polarion"], (98, 100, 100, 98, 100),
        url="https://hydrograph.com/newswire/", title="HydroGraph 2026 manufacturing and partner updates",
        publisher="HydroGraph", date="2026-07-15",
    ),
    "MakerPlane": q(
        "disqualified", "Open aircraft project without a verified commercial manufacturer",
        "MakerPlane is presented as an open-source or community aircraft project. The review did not find a current certified commercial product, production operation, funded scale-up, or active delivery program.",
        "A community design project is not yet a qualified manufacturing client.",
        [], (20, 30, 2, 42, 55),
    ),
    "Metamaterial Technologies Inc.": q(
        "disqualified", "Historical company identity no longer represents an independent prospect",
        "Metamaterial Technologies was absorbed into a later corporate entity; the directory record does not represent a current independent Canadian manufacturer with its own active buying process.",
        "Keeping the obsolete identity would create a duplicate or unreachable account rather than an actionable prospect.",
        [], (15, 25, 0, 35, 74),
    ),
    "Creaform - Ametek": q(
        "qualified", "Active metrology hardware manufacturer within AMETEK",
        "Creaform designs and manufactures portable 3D scanners, automated metrology systems, and inspection equipment used in aerospace and industrial production. Its live product portfolio spans multiple scanner, tracker, software, and automation configurations under AMETEK.",
        "A complex electro-optical product family with calibration, accuracy, firmware, software, supplier, and regulated customer requirements is a strong Teamcenter, NX, Capital, Polarion, Simcenter, and Opcenter opportunity.",
        P, (84, 100, 68, 98, 94),
        url="https://www.creaform3d.com/en", title="Creaform portable and automated 3D metrology systems",
        publisher="Creaform",
    ),
    "Solar Ship": q(
        "watchlist", "Hybrid cargo-aircraft program is credible but lacks a recent milestone",
        "Solar Ship has developed hybrid aircraft concepts combining buoyant lift, aerodynamic lift, solar energy, and electric propulsion for remote cargo. The review did not verify a meaningful 2025–2026 prototype, order, certification, funding, or production update.",
        "The multidisciplinary aircraft would fit Teamcenter, NX, Capital, Polarion, and Simcenter, but its present operating and commercialization status must be refreshed before outreach.",
        R, (48, 82, 3, 96, 58),
        url="https://en.wikipedia.org/wiki/Solar_Ship,_Inc.", title="Solar Ship company and aircraft overview",
        publisher="Wikipedia",
    ),
    "Aeroflux Braking Systems": q(
        "watchlist", "Contactless aircraft brake technology confirmed; no current development trigger",
        "Aeroflux states that it designs, develops, and manufactures magnetic contactless brakes for business and commercial aircraft. The official site still emphasizes its 2020 incubation and does not show a recent prototype test, certification, investment, customer program, or production milestone.",
        "Aircraft braking is safety-critical and strongly suited to Teamcenter, NX, Simcenter, Polarion, and Opcenter, but the lack of a current program trigger prevents qualification.",
        ["Teamcenter", "NX", "Simcenter", "Polarion", "Opcenter"], (56, 94, 8, 98, 78),
        url="https://aerofluxbrakes.com/", title="Aeroflux contactless aircraft brakes",
        publisher="Aeroflux Braking Systems",
    ),
    "SpaceAlpha Insights": q(
        "watchlist", "Dual-band SAR satellite platform confirmed; no dated build milestone",
        "SpaceAlpha is developing SAR-XL Earth-observation satellites combining X- and L-band radar, onboard AI, a 400-kilometre swath, and high-resolution imaging. Its active site confirms the product architecture but not a recent spacecraft build, launch booking, financing, or production milestone.",
        "Radar satellites require tightly managed payload, antenna, power, thermal, structure, software, requirements, and test interfaces. Teamcenter, NX, Capital, Polarion, and Simcenter are a strong fit when a build or launch trigger is verified.",
        R, (61, 88, 20, 99, 78),
        url="https://www.spacealphainsights.com/", title="SpaceAlpha SAR-XL satellite technology",
        publisher="SpaceAlpha",
    ),
    "Paladin AI Inc.": q(
        "disqualified", "AI/software company without a manufactured product line",
        "The company identity and available material point to artificial-intelligence software rather than a proprietary aerospace or robotic hardware platform and production operation.",
        "It falls outside the physical-product manufacturer gate.",
        ["RapidMiner", "Mendix"], (18, 2, 15, 30, 46),
    ),
    "Exchange Income Corporation": q(
        "disqualified", "Holding-company parent; actionable operations belong to PAL Aerospace",
        "Exchange Income Corporation is the parent of aviation and manufacturing subsidiaries. The concrete 2026 mission-aircraft engineering, modification, and delivery evidence belongs to PAL Aerospace, which is separately present in the ledger.",
        "Qualifying the parent would duplicate the same operating opportunity and obscure the team that owns the engineering and manufacturing work.",
        [], (30, 15, 65, 42, 92),
        url="https://www.exchangeincomecorp.ca/wcm-docs/news/2026_05_07_air_greenland_final_20260508063723.pdf",
        title="EIC subsidiary PAL Aerospace missionization update", publisher="Exchange Income Corporation",
        date="2026-05-08",
    ),
    "PAL Aerospace": q(
        "qualified", "Multiple 2026 mission-aircraft awards and $7.5M federal investment",
        "PAL Aerospace is executing aircraft missionization, engineering, modification, certification, C4ISR integration, and sustainment programs. Its 2026 updates include an Air Greenland DHC-8-200 missionization award, a $7.5M federal defence investment, and new RCAF training, missionization, and sustainment work.",
        "Concurrent aircraft configurations, structural and electrical modifications, certification evidence, mission software, supplier kits, test, and in-service baselines create a strong Teamcenter, NX, Capital, Polarion, Simcenter, and Opcenter opportunity.",
        P, (96, 96, 100, 100, 100),
        url="https://palaerospace.com/news/", title="PAL Aerospace 2026 program news",
        publisher="PAL Aerospace", date="2026-07-15",
    ),
    "Nupeak Robotics": q(
        "qualified", "2026 hiring supports Pixa harvesting robot and new industrial systems",
        "Nupeak is building Pixa autonomous strawberry-harvesting robots and an industrial robotic arm/workflow platform. In 2026 it is hiring mechanical and robotics-software developers for multidisciplinary real-world systems and presenting its work at Web Summit Vancouver.",
        "Product-family growth across manipulators, mobile hardware, vision, controls, AI, and field deployments requires CAD/BOM, requirements, electrical, test, variant, and service control suited to Teamcenter, NX, Capital, Polarion, Simcenter, and Opcenter.",
        P, (91, 98, 93, 99, 96),
        url="https://www.linkedin.com/company/nupeak-robotics", title="Nupeak Robotics 2026 product and hiring updates",
        publisher="Nupeak Robotics", date="2026-05-14",
    ),
    "Real Life Robotics": q(
        "qualified", "2026 deployments and platform work follow Canadian sidewalk-delivery approval",
        "Real Life Robotics manufactures configurable delivery robots and develops the PASSENGER automation platform. It completed a municipal sidewalk-delivery pilot with Skip, received IRAP support for fleet optimization, and is showcasing deployment work at the 2026 CFIN FoodTech Next summit.",
        "Scaling customizable robots and fleet software creates mechanical, electrical, autonomy, safety, regulatory, configuration, maintenance, and deployment-data needs suited to Teamcenter, NX, Capital, Polarion, Simcenter, and Opcenter.",
        P, (90, 95, 92, 98, 96),
        url="https://uwaterloo.ca/news/improving-bottom-line-and-impact-environment-one-robot-time",
        title="Real Life Robotics builds Canadian deployment playbook", publisher="University of Waterloo",
        date="2025-07-29",
    ),
    "A&K Robotics": q(
        "qualified", "$8M Series A to expand Cruz mobility-pod production and R&D",
        "A&K Robotics raised an $8M Series A in April 2026 specifically to expand production and R&D for its Canadian-built, all-electric Cruz autonomous airport mobility pods and support global deployments.",
        "The funded production ramp creates immediate needs for product configuration, mechanical and electrical design, autonomy requirements, safety validation, supplier control, manufacturing planning, and field-service baselines across Teamcenter, NX, Capital, Polarion, Simcenter, and Opcenter.",
        P, (98, 100, 100, 100, 100),
        url="https://www.aandkrobotics.com/news", title="A&K Robotics raises $8M to expand production and R&D",
        publisher="A&K Robotics", date="2026-04-21",
    ),
    "MAE Robotics": q(
        "qualified", "2026 international program and active SensuReal product commercialization",
        "MAE Robotics develops and sells SensuReal force sensors alongside custom robots and autonomous systems from Ottawa. It filed its 2026 corporate return, participated in a March–April 2026 Canadian technology mission, and maintains active quote and demonstration workflows for its hardware products.",
        "Force-sensor and robot variants require mechanical, electronics, calibration, firmware, test, customer-configuration, and quality traceability suited to Teamcenter, NX, Capital, Polarion, Simcenter, and Opcenter.",
        P, (82, 92, 78, 97, 91),
        url="https://www.b2match.com/e/mission-of-canada-to-eu/participations/713720",
        title="MAE Robotics in 2026 Canada technology mission", publisher="B2Match",
        date="2026-03-24",
    ),
    "Robotics Design Inc.": q(
        "watchlist", "Active modular robot catalogue; no recent scale event",
        "Robotics Design designs and builds mobile robots, snake arms, manipulators, assisted-handling equipment, HVAC inspection robots, and tactical systems from its modular ANAT architecture. The official catalogue is active, but no recent order, funding, facility, hiring, or production expansion was found.",
        "Its broad configured-to-order hardware portfolio is a strong Teamcenter, NX, Capital, Polarion, and Simcenter fit. A fresh commercial trigger should move it into qualified outreach.",
        R, (63, 98, 12, 97, 90),
        url="https://www.roboticsdesign.qc.ca/company/about-us/", title="Robotics Design modular robotic product portfolio",
        publisher="Robotics Design",
    ),
    "Tactile Robotics": q(
        "qualified", "2026 product launch activity and growing international deployment footprint",
        "Tactile Robotics designs and fabricates haptic, robotic, sensing, dental-training, rehabilitation, and tele-enabled healthcare platforms. Its current site documents real-world deployments and product families, while late-2025/2026 updates include the iManus launch path and continued international growth.",
        "Multiple medical mechatronic products create requirements, risk, mechanical/electrical configuration, calibration, software release, validation, customer deployment, and regulatory evidence needs for Teamcenter, NX, Capital, Polarion, and Simcenter.",
        R, (88, 94, 88, 99, 96),
        url="https://tactilerobotics.ca/news-media/", title="Tactile Robotics product and deployment news",
        publisher="Tactile Robotics", date="2025-12-29",
    ),
    "Optimotive": q(
        "qualified", "Funded robot fleet already deployed with major construction companies",
        "Optimotive raised $2M to fulfill pre-orders and scale its IRIS and BOX autonomous robots for extreme outdoor environments. The fleet has deployed with EllisDon, Pomerleau, and Borea in construction and renewable-energy applications.",
        "Moving rugged robot variants from field pilots into repeatable deliveries creates CAD/BOM, electrical, autonomy, test, environmental validation, supplier, fleet, and service needs for Teamcenter, NX, Capital, Polarion, Simcenter, and Opcenter.",
        P, (86, 98, 81, 99, 94),
        url="https://www.optimotive.io/company", title="Optimotive funding, deployments, and robot fleet",
        publisher="Optimotive", date="2024-09-10",
    ),
    "NIO Robotics": q(
        "qualified", "WALBOT v4 pilots and large-scale industrial projects scheduled for 2026",
        "NIO Robotics is developing WALBOT, a mobile collaborative robot for autonomous painting, sandblasting, and coating. Its published roadmap shows April 2026 lab trials, summer 2026 MVP and first large industrial-partner projects, and a hardened v5 planned for 2027.",
        "The imminent pilot-to-product transition creates mechanical, motion, controls, perception, path-planning, coating-quality, safety, configuration, and validation needs suited to Teamcenter, NX, Capital, Polarion, Simcenter, and Opcenter.",
        P, (95, 98, 100, 99, 100),
        url="https://niorobotics.ca/", title="NIO Robotics WALBOT 2026 product roadmap",
        publisher="NIO Robotics", date="2026-04-01",
    ),
    "GlüxKind Technologies": q(
        "qualified", "Connected smart-stroller platform actively shipping 2026 software updates",
        "Glüxkind manufactures the Ella AI-enabled smart stroller, combining drive assistance, braking, sensors, embedded intelligence, wireless connectivity, an app, and safety functions. Its companion app was updated in June 2026 with owner, family, connectivity, and product-experience features.",
        "A safety-sensitive connected consumer product requires synchronized mechanical, motor, battery, sensor, electronics, firmware, mobile-app, verification, supplier, and model configuration. Teamcenter, NX, Capital, Polarion, and Simcenter fit this lifecycle.",
        R, (88, 98, 88, 99, 98),
        url="https://play.google.com/store/apps/details?id=com.gluxkind.companion",
        title="Glüxkind Companion app update for connected smart stroller", publisher="Google Play",
        date="2026-06-01",
    ),
    "Mission Control Space Services": q(
        "disqualified", "Space software and mission-services provider, not a manufacturer",
        "Mission Control develops spacecraft operations, autonomy, and mission software and delivers space-mission services. The review did not establish a proprietary manufactured spacecraft or production operation.",
        "Although Polarion and Mendix may be relevant to its software lifecycle, it fails this campaign's physical-product manufacturing gate.",
        ["Polarion", "Mendix"], (32, 5, 55, 50, 88),
    ),
}


def main() -> None:
    load_dotenv()
    db = Database()
    db.initialize()
    pending = [
        row for row in db.list_keyword_companies(1000)
        if row.qualification_status == "needs_review"
    ]
    missing = sorted({row.company_name for row in pending} - set(DECISIONS))
    if missing:
        raise RuntimeError(f"Missing qualification decisions: {missing}")

    counts = {"qualified": 0, "watchlist": 0, "disqualified": 0}
    created = 0
    duplicates = 0
    for row in pending:
        decision = DECISIONS[row.company_name]
        source_url = decision["source_url"] or row.source_url or row.company_url
        if not source_url:
            raise RuntimeError(f"No source URL for {row.company_name}")
        source_title = (
            decision["source_title"] or row.source_title
            or f"{row.company_name} qualification evidence"
        )
        source_publisher = decision["source_publisher"] or row.source_publisher or "Company profile"
        signal_date = dt(decision["signal_date"])
        status = decision["qualification_status"]

        if status in {"qualified", "watchlist"}:
            signal = ExtractedSignal(
                company_name=row.company_name,
                company_domain=row.company_domain,
                company_url=row.company_url,
                linkedin_url=row.linkedin_url,
                location=row.location,
                industry=row.industry,
                company_industry=row.industry,
                software=decision["recommended_products"],
                signal_type="news",
                signal_source="news",
                pain_signals=[decision["challenge_summary"]],
                expansion_signals=[decision["signal_label"]],
                raw_score=decision["opportunity_score"],
                confidence=decision["evidence_quality_score"] / 100,
                reason=decision["why_relevant"],
                source_url=source_url,
                source_title=source_title,
                detected_at=signal_date or datetime.now(timezone.utc),
            )
            saved = db.save_signal(signal)
            if saved.created:
                created += 1
            else:
                duplicates += 1
            db.upsert_company(signal)

        linked = db.record_keyword_company(
            row.keyword_id,
            row.company_name,
            row.company_domain,
            source_url=source_url,
            source_title=source_title,
            source_publisher=source_publisher,
            signal_label=decision["signal_label"],
            signal_date=signal_date,
            challenge_summary=decision["challenge_summary"],
            why_relevant=decision["why_relevant"],
            recommended_products=decision["recommended_products"],
            qualification_status=status,
            opportunity_score=decision["opportunity_score"],
            manufacturing_fit_score=decision["manufacturing_fit_score"],
            trigger_score=decision["trigger_score"],
            solution_fit_score=decision["solution_fit_score"],
            evidence_quality_score=decision["evidence_quality_score"],
        )
        if linked is None:
            raise RuntimeError(f"Could not link {row.company_name}")
        counts[status] += 1
        print(f"{row.company_name}: {status} ({decision['opportunity_score']})")

    remaining = sum(
        1 for row in db.list_keyword_companies(1000)
        if row.qualification_status == "needs_review"
    )
    visible = sum(
        1 for row in db.list_keyword_companies(1000)
        if row.qualification_status in {"qualified", "watchlist"}
    )
    print(
        f"SUMMARY processed={len(pending)} qualified={counts['qualified']} "
        f"watchlist={counts['watchlist']} disqualified={counts['disqualified']} "
        f"signals_created={created} signal_duplicates={duplicates} "
        f"remaining={remaining} visible={visible}"
    )


if __name__ == "__main__":
    main()
