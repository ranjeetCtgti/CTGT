from __future__ import annotations

from datetime import datetime, timezone

from dotenv import load_dotenv

from db.database import Database
from models.schema import ExtractedSignal


def date(value: str | None) -> datetime | None:
    return datetime.fromisoformat(f"{value}T12:00:00+00:00") if value else None


ROWS = [
    dict(
        keyword_id=4, company_name="Raven Connected", company_domain="ravenconnected.com",
        company_url="https://ravenconnected.com/", location="Ottawa, Ontario, Canada",
        industry="Connected-vehicle hardware and AI video telematics",
        source_url="https://ravenconnected.com/news/swift-partnership-announcement/",
        source_title="Raven Connected and Swift Navigation partner on AI-driven spatial intelligence",
        source_publisher="Raven Connected", signal_date="2026-01-05",
        signal_label="New centimeter-accurate AI road-mapping platform launched for CES 2026",
        challenge_summary=(
            "Raven integrated Swift Navigation's precise-positioning service into its AI onboard "
            "units to turn fleet vehicles into live road-mapping sensors. The launch combines "
            "in-vehicle hardware, cameras, GNSS, edge AI, cloud workflows, and digital-twin data "
            "for municipal infrastructure management."
        ),
        why_relevant=(
            "The new hardware-software configuration expands Raven's product and partner matrix "
            "and raises requirements, interface, test, release, and field-support complexity. "
            "Teamcenter, Capital, Polarion, and Simcenter can govern the cross-domain product "
            "definition and validation as the CES-launched platform moves into deployments."
        ),
        recommended_products=["Teamcenter", "Capital", "Polarion", "Simcenter", "Mendix"],
        qualification_status="qualified", opportunity_score=86, manufacturing_fit_score=82,
        trigger_score=86, solution_fit_score=91, evidence_quality_score=98,
        signal_source="official_company_news",
    ),
    dict(
        keyword_id=4, company_name="Aadhya Navik Inc.", company_domain="aadhyanavik.com",
        company_url="https://www.aadhyanavik.com/", location="Canada",
        industry="Autonomous-vehicle ride-control software",
        source_url="https://www.aadhyanavik.com/",
        source_title="Aadhya Navik autonomous-vehicle comfort software",
        source_publisher="Aadhya Navik", signal_date=None,
        signal_label="Software-only autonomous-vehicle startup; no physical product operation",
        challenge_summary=(
            "Aadhya Navik describes a software algorithm that adjusts autonomous-vehicle driving "
            "decisions using passenger comfort, acceleration, deceleration, and jerk thresholds. "
            "No proprietary vehicle, controller, production operation, or current commercialization "
            "trigger was verified."
        ),
        why_relevant=(
            "The company may have ALM needs, but it is a software supplier rather than a physical "
            "vehicle or component manufacturer. It does not meet this manufacturing-prospect gate."
        ),
        recommended_products=["Polarion"],
        qualification_status="disqualified", opportunity_score=22, manufacturing_fit_score=8,
        trigger_score=12, solution_fit_score=38, evidence_quality_score=90,
        signal_source="official_company_site",
    ),
    dict(
        keyword_id=2, company_name="INDROTEK", company_domain="indrotek.com",
        company_url="https://indrotek.com/", location="Canada",
        industry="Autonomous-systems holding company",
        source_url="https://www.ascentafinance.com/indrotek",
        source_title="INDROTEK company profile and InDro Robotics collaboration updates",
        source_publisher="Ascenta Finance", signal_date="2026-06-03",
        signal_label="Holding-company identity overlaps already-qualified InDro Robotics",
        challenge_summary=(
            "INDROTEK is presented as the parent platform for divisions including InDro Robotics, "
            "Bravo Zulu Drone Defence, and Stratocom Solutions. The dated autonomous-ground-mobility "
            "activity is explicitly delivered through InDro Robotics, which is already a separately "
            "qualified manufacturer in the database."
        ),
        why_relevant=(
            "Publishing the parent as another manufacturing prospect would duplicate the same "
            "operating capability and evidence. The actionable product-engineering opportunity "
            "belongs to the existing InDro Robotics account."
        ),
        recommended_products=["Teamcenter", "NX", "Simcenter", "Polarion"],
        qualification_status="disqualified", opportunity_score=32, manufacturing_fit_score=24,
        trigger_score=68, solution_fit_score=55, evidence_quality_score=78,
        signal_source="corporate_profile",
    ),
    dict(
        keyword_id=1, company_name="Voxelis AI", company_domain="voxelis.ai",
        company_url="https://www.voxelis.ai/", location="Richmond, British Columbia, Canada",
        industry="Airborne edge-AI and wildfire sensing systems",
        source_url="https://www.voxelis.ai/",
        source_title="VoxVision airborne AI platform for helicopters",
        source_publisher="Voxelis", signal_date=None,
        signal_label="Physical multi-sensor edge-AI platform confirmed; current urgency unproven",
        challenge_summary=(
            "Voxelis is developing VoxVision, a low-size, weight, and power gimbal and edge-computing "
            "platform that combines visual and infrared sensing, aircraft data, onboard AI, and cloud "
            "delivery for wildfire and geospatial missions. Its public news page shows no deployment, "
            "funding, or production milestone newer than March 2024."
        ),
        why_relevant=(
            "The cross-domain airborne product has credible mechanical, optical, electronics, "
            "embedded-software, and flight-validation complexity suited to Teamcenter, Capital, "
            "Polarion, NX, and Simcenter. It remains a watchlist prospect until a current certification, "
            "fleet deployment, contract, or production-ramp trigger is verified."
        ),
        recommended_products=["Teamcenter", "NX", "Capital", "Polarion", "Simcenter"],
        qualification_status="watchlist", opportunity_score=59, manufacturing_fit_score=79,
        trigger_score=20, solution_fit_score=91, evidence_quality_score=74,
        signal_source="official_company_site",
    ),
    dict(
        keyword_id=3, company_name="Victoria Shipyards Co. Ltd", company_domain="vicship.com",
        company_url="https://www.seaspan.com/seaspan-shipyards/victoria-shipyards/",
        location="Victoria, British Columbia, Canada", industry="Shipbuilding and ship repair",
        source_url="https://www.seaspan.com/press-release/seaspan-celebrates-one-year-of-progress-on-the-heavy-polar-icebreaker/",
        source_title="Seaspan celebrates one year of progress on the heavy polar icebreaker",
        source_publisher="Seaspan", signal_date="2026-05-26",
        signal_label="Significant polar-icebreaker manufacturing work underway at Victoria Shipyards",
        challenge_summary=(
            "Seaspan confirmed significant heavy-polar-icebreaker manufacturing at Victoria "
            "Shipyards while 49 vessel blocks were under construction across the program. Victoria's "
            "work feeds a 26,000-tonne, year-round Arctic vessel with thick-steel structures, specialized "
            "coatings, pre-outfitting, and a supply chain of more than 55 Canadian companies."
        ),
        why_relevant=(
            "Cross-yard block production requires synchronized product structures, work packages, "
            "material and weld traceability, supplier data, quality records, and as-built configuration. "
            "Teamcenter, NX, Opcenter, Tecnomatix, Simcenter, Polarion, and Capital map directly to "
            "the active program's engineering-to-production controls."
        ),
        recommended_products=["Teamcenter", "NX", "Opcenter", "Tecnomatix", "Simcenter", "Polarion", "Capital"],
        qualification_status="qualified", opportunity_score=92, manufacturing_fit_score=100,
        trigger_score=96, solution_fit_score=99, evidence_quality_score=100,
        signal_source="official_company_news",
    ),
    dict(
        keyword_id=3, company_name="Vancouver Shipyards Co Ltd", company_domain=None,
        company_url="https://www.seaspan.com/seaspan-shipyards/vancouver-shipyards/",
        location="North Vancouver, British Columbia, Canada", industry="Complex-vessel shipbuilding",
        source_url="https://www.seaspan.com/press-release/seaspan-celebrates-one-year-of-progress-on-the-heavy-polar-icebreaker/",
        source_title="Seaspan celebrates one year of progress on the heavy polar icebreaker",
        source_publisher="Seaspan", signal_date="2026-05-26",
        signal_label="49 polar-icebreaker blocks in production; first 330-tonne grand block consolidated",
        challenge_summary=(
            "Vancouver Shipyards consolidated the first 330-tonne grand block for Canada's "
            "26,000-tonne heavy polar icebreaker and had more than 49 blocks underway. Production "
            "includes 50-60 mm Arctic steel, early pipe and foundation outfitting, specialized hull "
            "coatings, robotic welding, 230-465 tonne lifts, and coordination with over 55 suppliers."
        ),
        why_relevant=(
            "This is an immediate, configuration-heavy digital-thread opportunity spanning ship "
            "design, requirements, supplier collaboration, block manufacturing, weld and coating "
            "quality, production sequencing, and as-built evidence. The active multi-year build is "
            "a strong fit for the full Teamcenter, NX, Opcenter, Tecnomatix, Simcenter, Polarion, "
            "and Capital stack."
        ),
        recommended_products=["Teamcenter", "NX", "Opcenter", "Tecnomatix", "Simcenter", "Polarion", "Capital"],
        qualification_status="qualified", opportunity_score=98, manufacturing_fit_score=100,
        trigger_score=100, solution_fit_score=100, evidence_quality_score=100,
        signal_source="official_company_news",
    ),
    dict(
        keyword_id=2, company_name="RoboTools Canada", company_domain="robotools.ca",
        company_url="https://robotools.ca/", location="Delta, British Columbia, Canada",
        industry="Robotics distribution and integration",
        source_url="https://robotools.ca/",
        source_title="RoboTools Canada commercial robotics and integration services",
        source_publisher="RoboTools Canada", signal_date=None,
        signal_label="Importer, distributor, and integrator rather than robot manufacturer",
        challenge_summary=(
            "RoboTools sells, leases, integrates, installs, and services cleaning, delivery, welding, "
            "palletizing, and mobile robots sourced from multiple manufacturers. Its own site describes "
            "the company as an importer and distributor with engineering-led integration and support."
        ),
        why_relevant=(
            "This is a robotics channel and systems-integration business, not the target manufacturer "
            "of a proprietary physical product. It is excluded by the reseller and service-provider gate."
        ),
        recommended_products=["Tecnomatix", "Opcenter"],
        qualification_status="disqualified", opportunity_score=25, manufacturing_fit_score=12,
        trigger_score=45, solution_fit_score=42, evidence_quality_score=96,
        signal_source="official_company_site",
    ),
    dict(
        keyword_id=2, company_name="Innventors", company_domain=None,
        company_url="https://www.f6s.com/company/innventors", location="Toronto, Ontario, Canada",
        industry="Robotics and coding education",
        source_url="https://directory.nextcanada.com/directory/ventures/",
        source_title="Innventors robotics and coding education program profile",
        source_publisher="NEXT Canada", signal_date=None,
        signal_label="Education program misclassified as a robotics manufacturer",
        challenge_summary=(
            "Innventors is described as a program that teaches children coding, robotics, design, "
            "and soft skills through workshops. No proprietary robot product, manufacturing operation, "
            "or current commercial trigger was found."
        ),
        why_relevant=(
            "The organization is an education service rather than a physical-product manufacturer "
            "and has no defensible Siemens or Altair manufacturing opportunity."
        ),
        recommended_products=[],
        qualification_status="disqualified", opportunity_score=10, manufacturing_fit_score=2,
        trigger_score=5, solution_fit_score=8, evidence_quality_score=78,
        signal_source="reputable_directory",
    ),
    dict(
        keyword_id=2, company_name="Dartmouth Ocean Technologies",
        company_domain="dartmouthocean.com", company_url="https://www.dartmouthocean.com/",
        location="Dartmouth, Nova Scotia, Canada",
        industry="Underwater sensors and autonomous ocean-sampling systems",
        source_url="https://www.dartmouthocean.com/wp-content/uploads/2026/03/DOT_Alkalinity_Sensor-2026-03A_FINAL.pdf",
        source_title="Dartmouth Ocean Technologies introduces a miniaturized autonomous alkalinity sensor",
        source_publisher="Dartmouth Ocean Technologies", signal_date="2026-03-01",
        signal_label="New configurable autonomous alkalinity sensor introduced in March 2026",
        challenge_summary=(
            "DOT introduced a 5 kg autonomous microfluidic alkalinity sensor with configurable "
            "sampling, reagent housings, mounting arrangements, platform or battery power, Ethernet "
            "and serial outputs, and deployment options for vessels, buoys, gliders, ROVs, and "
            "uncrewed systems. DOT designs and manufactures its sensor and sampler portfolio in Nova Scotia."
        ),
        why_relevant=(
            "Commercializing configurable electro-mechanical and chemical instruments across multiple "
            "ocean platforms creates product-variant, calibration, reagent, test, supplier, and quality "
            "traceability needs. Teamcenter, NX, Capital, Polarion, Simcenter, and Opcenter can connect "
            "the sensor design through controlled manufacturing and field configuration."
        ),
        recommended_products=["Teamcenter", "NX", "Capital", "Polarion", "Simcenter", "Opcenter"],
        qualification_status="qualified", opportunity_score=88, manufacturing_fit_score=96,
        trigger_score=88, solution_fit_score=96, evidence_quality_score=100,
        signal_source="official_product_documentation",
    ),
    dict(
        keyword_id=2, company_name="RenMobi Inc.", company_domain="renmobi.com",
        company_url="https://renmobi.com/", location="Toronto, Ontario, Canada",
        industry="Renewable-energy design and installation services",
        source_url="https://www.yorku.ca/procurement/listing/cred-auto-draft-09f9e1b57f4abf0588d98a7ab950fc19/",
        source_title="RenMobi renewable-energy systems vendor profile",
        source_publisher="York University", signal_date="2025-03-28",
        signal_label="Design-and-installation contractor without a verified proprietary product line",
        challenge_summary=(
            "RenMobi is documented as a designer and installer of solar PV, thermal storage, EV "
            "charging, HVAC, and energy-efficient building systems. The review found no verified "
            "proprietary manufactured product, production facility, or current scale-up trigger."
        ),
        why_relevant=(
            "The business is primarily project design and installation rather than repeatable physical "
            "product manufacturing, so it does not meet the prospect gate."
        ),
        recommended_products=["Solid Edge"],
        qualification_status="disqualified", opportunity_score=30, manufacturing_fit_score=18,
        trigger_score=20, solution_fit_score=42, evidence_quality_score=84,
        signal_source="institutional_vendor_profile",
    ),
    dict(
        keyword_id=2, company_name="Reliable Robots", company_domain="reliablerobots.ca",
        company_url="https://www.reliablerobots.ca/", location="Toronto, Ontario, Canada",
        industry="Service-robot distribution and managed deployment",
        source_url="https://www.reliablerobots.ca/",
        source_title="Reliable Robots service robotics portfolio",
        source_publisher="Reliable Robots", signal_date=None,
        signal_label="Canadian distributor and Robot-as-a-Service provider, not a manufacturer",
        challenge_summary=(
            "Reliable Robots distributes third-party Pudu, Keenon, Sparkoz, FieldBots, and other "
            "service robots and provides financing, installation, maintenance, fleet management, "
            "and Robot-as-a-Service packages. It does not claim to manufacture the robots."
        ),
        why_relevant=(
            "This is a reseller and managed-service provider rather than a proprietary robotics "
            "manufacturer, so it is excluded from the target-client list."
        ),
        recommended_products=["Mendix"],
        qualification_status="disqualified", opportunity_score=18, manufacturing_fit_score=5,
        trigger_score=35, solution_fit_score=28, evidence_quality_score=96,
        signal_source="official_company_site",
    ),
    dict(
        keyword_id=2, company_name="Enginuity Inc.", company_domain="enginuityinc.ca",
        company_url="https://enginuityinc.ca/", location="Halifax, Nova Scotia, Canada",
        industry="Engineering consulting and automation integration",
        source_url="https://enginuityinc.ca/",
        source_title="Enginuity product development and automation engineering services",
        source_publisher="Enginuity", signal_date=None,
        signal_label="Engineering consultancy and integrator rather than target product manufacturer",
        challenge_summary=(
            "Enginuity designs prototypes, custom machines, automation systems, and manufacturing "
            "solutions for clients across aerospace, defence, marine, and industry. Its offering is "
            "project-based engineering, prototyping, integration, and consulting rather than a "
            "scalable proprietary product line."
        ),
        why_relevant=(
            "Enginuity may be an engineering or implementation partner, but it does not match the "
            "end-manufacturer prospect profile required for this keyword workflow."
        ),
        recommended_products=["NX", "Simcenter", "Tecnomatix"],
        qualification_status="disqualified", opportunity_score=40, manufacturing_fit_score=30,
        trigger_score=38, solution_fit_score=70, evidence_quality_score=94,
        signal_source="official_company_site",
    ),
    dict(
        keyword_id=2, company_name="Andaritech", company_domain="andaritech.com",
        company_url="https://andaritech.com/", location="Toronto, Ontario, Canada",
        industry="Robotics, drone, and engineering services",
        source_url="https://andaritech.com/",
        source_title="Andaritech robotics, drone, cybersecurity, and engineering services",
        source_publisher="Andaritech", signal_date=None,
        signal_label="Consulting and custom-project provider without a proprietary manufactured product",
        challenge_summary=(
            "Andaritech offers robotics and drone operations, proof-of-concept development, engineering "
            "consulting, cybersecurity, AI, telecom, automation integration, and 3D-printing services. "
            "No repeatable proprietary robot, drone platform, manufacturing operation, or current product "
            "scale-up trigger was verified."
        ),
        why_relevant=(
            "The company is a broad technology consultancy and systems integrator rather than the "
            "physical-product manufacturing client profile required for publication."
        ),
        recommended_products=["Mendix", "Polarion"],
        qualification_status="disqualified", opportunity_score=25, manufacturing_fit_score=12,
        trigger_score=18, solution_fit_score=48, evidence_quality_score=92,
        signal_source="official_company_site",
    ),
    dict(
        keyword_id=2, company_name="Proax Technologies", company_domain="proax.ca",
        company_url="https://proax.ca/", location="Canada",
        industry="Automation distribution and systems integration",
        source_url="https://proax.ca/strapiv4/uploads/QRG_EN_2026_dadc0312e7.pdf",
        source_title="Proax 2026 automation and robotics quick-reference guide",
        source_publisher="Proax Technologies", signal_date="2026-05-01",
        signal_label="Value-added ABB and Omron automation distributor; excluded reseller profile",
        challenge_summary=(
            "Proax's 2026 guide identifies the company as a value-added automation distributor that "
            "selects, engineers, programs, deploys, services, and repairs ABB and Omron robotics. "
            "Although it also assembles custom conveyors and tooling, its core role is distribution "
            "and systems integration for customer factories."
        ),
        why_relevant=(
            "The explicit reseller and integration role falls outside the target end-manufacturer "
            "gate and may create channel conflict rather than a direct CTGTI client opportunity."
        ),
        recommended_products=["Tecnomatix", "Opcenter"],
        qualification_status="disqualified", opportunity_score=38, manufacturing_fit_score=28,
        trigger_score=55, solution_fit_score=58, evidence_quality_score=96,
        signal_source="official_product_documentation",
    ),
    dict(
        keyword_id=2, company_name="Sanad Labs", company_domain="sanadlabs.com",
        company_url="https://www.sanadlabs.com/", location="Mississauga, Ontario, Canada",
        industry="Early-stage medical robotics",
        source_url="https://www.linkedin.com/company/sanadlabs",
        source_title="Sanad Labs medical-robotics company profile",
        source_publisher="LinkedIn", signal_date=None,
        signal_label="Medical-robot concept claimed; product and current trigger remain unverifiable",
        challenge_summary=(
            "Sanad Labs states that it develops AI-powered medical robots for elderly people and "
            "people with limited mobility, but the review found only a small company profile and no "
            "verifiable product specification, prototype milestone, regulatory work, deployment, "
            "funding, official announcement, or manufacturing operation."
        ),
        why_relevant=(
            "Medical robotics could fit Teamcenter, Polarion, NX, and Simcenter, but the evidence is "
            "too thin to establish product reality or buying urgency. The record remains hidden for "
            "future reassessment rather than being published or permanently rejected."
        ),
        recommended_products=["Teamcenter", "NX", "Polarion", "Simcenter"],
        qualification_status="needs_review", opportunity_score=38, manufacturing_fit_score=55,
        trigger_score=5, solution_fit_score=74, evidence_quality_score=25,
        signal_source="company_profile",
    ),
    dict(
        keyword_id=2, company_name="Copperstone Technologies",
        company_domain="copperstonetech.com", company_url="https://copperstonetech.com/",
        location="Edmonton, Alberta, Canada",
        industry="Autonomous amphibious industrial robots",
        source_url="https://copperstonetech.com/earthday/",
        source_title="Earth Day Spotlight: Arca",
        source_publisher="Copperstone Technologies", signal_date="2026-04-21",
        signal_label="HELIX robots deployed to scale autonomous mine-waste carbon removal",
        challenge_summary=(
            "Copperstone is supporting Arca's scalable mine-waste carbon-removal work with autonomous "
            "rover technology while operating HELIX platforms across Canada, the United States, "
            "Australia, and Brazil. Copperstone designs and manufactures 400 kg and one-ton amphibious "
            "robots with configurable payloads, sensor deployment systems, autonomy, and field software."
        ),
        why_relevant=(
            "Global deployments and application-specific payloads create variant, requirements, "
            "electrical, mechanical, embedded-software, safety, test, and service-configuration pressure. "
            "Teamcenter, NX, Capital, Polarion, Simcenter, and Opcenter can control the product family "
            "and manufacturing evidence as deployments expand."
        ),
        recommended_products=["Teamcenter", "NX", "Capital", "Polarion", "Simcenter", "Opcenter"],
        qualification_status="qualified", opportunity_score=92, manufacturing_fit_score=100,
        trigger_score=91, solution_fit_score=98, evidence_quality_score=94,
        signal_source="official_company_news",
    ),
    dict(
        keyword_id=2, company_name="Roboteurs", company_domain="roboteurs.com",
        company_url="https://roboteurs.com/", location="Canada",
        industry="Educational robotics hardware",
        source_url="https://roboteurs.com/",
        source_title="Roboteurs educational robotics product catalogue",
        source_publisher="Roboteurs", signal_date=None,
        signal_label="Physical education-robotics products confirmed; no recent growth trigger",
        challenge_summary=(
            "Roboteurs sells a six-axis 3D-printed robot-arm kit, stepper-motor drivers, motors, and "
            "education-focused robotics materials and describes additional secondary and post-secondary "
            "products in its pipeline. Several flagship products are sold out and no recent funding, "
            "contract, facility, hiring, or production-ramp announcement was verified."
        ),
        why_relevant=(
            "A configurable electronics and educational-robot product family can benefit from Solid Edge, "
            "Teamcenter, and Capital for design, BOM, revision, and kit configuration. The absence of a "
            "dated commercialization trigger keeps it on the watchlist."
        ),
        recommended_products=["Solid Edge", "Teamcenter", "Capital"],
        qualification_status="watchlist", opportunity_score=49, manufacturing_fit_score=70,
        trigger_score=15, solution_fit_score=70, evidence_quality_score=72,
        signal_source="official_company_site",
    ),
    dict(
        keyword_id=2, company_name="Robot Playtime", company_domain="robotplaytime.com",
        company_url="https://robotplaytime.com/", location="Toronto, Ontario, Canada",
        industry="Robotics education software",
        source_url="https://directory.nextcanada.com/directory/ventures/",
        source_title="Robot Playtime venture profile",
        source_publisher="NEXT Canada", signal_date=None,
        signal_label="Dormant education-app profile without a current manufactured product",
        challenge_summary=(
            "Robot Playtime's documented Pixel platform is an education app that turns a phone or "
            "tablet into a programmable robot controller and can connect to third-party hobby hardware. "
            "The available profile dates to its 2017 cohort, and no current proprietary hardware, "
            "manufacturing activity, or commercial trigger was verified."
        ),
        why_relevant=(
            "This is an education-software profile rather than an active physical-product manufacturer "
            "and does not meet the CTGTI prospect gate."
        ),
        recommended_products=[],
        qualification_status="disqualified", opportunity_score=15, manufacturing_fit_score=5,
        trigger_score=3, solution_fit_score=18, evidence_quality_score=76,
        signal_source="reputable_directory",
    ),
    dict(
        keyword_id=2, company_name="5C Technologies", company_domain="5ctechnologies.com",
        company_url="https://5ctechnologies.com/", location="Canada",
        industry="Unverified robotics directory entry",
        source_url="https://5ctechnologies.com/",
        source_title="5C Technologies digital agency profile",
        source_publisher="5C Technologies", signal_date=None,
        signal_label="Directory false positive; matching company is a software and marketing agency",
        challenge_summary=(
            "The verifiable company operating under the matching name and domain provides web, mobile-app, "
            "UI/UX, and digital-marketing services from Noida, India. No Canadian robotics manufacturer, "
            "physical product, or manufacturing operation could be verified for this directory entry."
        ),
        why_relevant=(
            "The record is a false-positive or identity mismatch and has no defensible manufacturing "
            "or Siemens/Altair product opportunity."
        ),
        recommended_products=[],
        qualification_status="disqualified", opportunity_score=5, manufacturing_fit_score=0,
        trigger_score=0, solution_fit_score=5, evidence_quality_score=82,
        signal_source="official_company_site",
    ),
    dict(
        keyword_id=2, company_name="Able Innovations Inc.",
        company_domain="ableinnovations.com", company_url="https://www.ableinnovations.com/",
        location="Toronto, Ontario, Canada", industry="Medical robotics manufacturing",
        source_url="https://www.ableinnovations.com/deployment-lahey-hospital/",
        source_title="Able Innovations deploys the ALTA Platform at Lahey Hospital & Medical Center",
        source_publisher="Able Innovations", signal_date="2026-03-09",
        signal_label="First U.S. hospital deployment follows multiple Canadian ALTA installations",
        challenge_summary=(
            "Able deployed its ALTA robotic patient-transfer platform at Lahey's 400-bed Level-I "
            "Trauma Center, its first U.S. hospital implementation after multiple Canadian deployments. "
            "The system combines robotics, intelligent motion, sensors, caregiver-centered design, and "
            "hospital workflow integration to move patients safely between beds, stretchers, and tables."
        ),
        why_relevant=(
            "International hospital rollout raises regulated requirements, risk management, design "
            "change, supplier, verification, service configuration, and device-history traceability. "
            "Teamcenter, NX, Polarion, Simcenter, Capital, and Opcenter can support the controlled "
            "medical-device lifecycle as ALTA scales across health systems."
        ),
        recommended_products=["Teamcenter", "NX", "Polarion", "Simcenter", "Capital", "Opcenter"],
        qualification_status="qualified", opportunity_score=96, manufacturing_fit_score=100,
        trigger_score=98, solution_fit_score=100, evidence_quality_score=100,
        signal_source="official_company_news",
    ),
]


def main() -> None:
    load_dotenv()
    db = Database()
    db.initialize()
    results = []
    for row in ROWS:
        signal_date = date(row["signal_date"])
        created = None
        if row["qualification_status"] in {"qualified", "watchlist"}:
            signal = ExtractedSignal(
                company_name=row["company_name"],
                company_domain=row["company_domain"],
                company_url=row["company_url"],
                location=row["location"],
                industry=row["industry"],
                company_industry=row["industry"],
                software=row["recommended_products"],
                signal_type="news",
                signal_source="news",
                pain_signals=[row["challenge_summary"]],
                expansion_signals=[row["signal_label"]],
                raw_score=row["opportunity_score"],
                confidence=row["evidence_quality_score"] / 100,
                reason=row["why_relevant"],
                source_url=row["source_url"],
                source_title=row["source_title"],
                detected_at=signal_date or datetime.now(timezone.utc),
            )
            saved = db.save_signal(signal)
            created = saved.created
            db.upsert_company(signal)

        linked = db.record_keyword_company(
            row["keyword_id"], row["company_name"], row["company_domain"],
            source_url=row["source_url"], source_title=row["source_title"],
            source_publisher=row["source_publisher"], signal_label=row["signal_label"],
            signal_date=signal_date, challenge_summary=row["challenge_summary"],
            why_relevant=row["why_relevant"], recommended_products=row["recommended_products"],
            qualification_status=row["qualification_status"],
            opportunity_score=row["opportunity_score"],
            manufacturing_fit_score=row["manufacturing_fit_score"],
            trigger_score=row["trigger_score"], solution_fit_score=row["solution_fit_score"],
            evidence_quality_score=row["evidence_quality_score"],
        )
        if linked is None:
            raise RuntimeError(f"Unable to update keyword ledger for {row['company_name']}")
        results.append((row["company_name"], row["qualification_status"], created))

    for name, status, created in results:
        print(f"{name}: status={status}, signal_created={created if created is not None else 'skipped'}")


if __name__ == "__main__":
    main()
