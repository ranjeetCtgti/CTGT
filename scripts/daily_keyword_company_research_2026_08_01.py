from __future__ import annotations

from datetime import datetime, timezone

from dotenv import load_dotenv

from db.database import Database
from models.schema import ExtractedSignal


QUALIFIED = [
    {
        "keyword_id": 1,
        "company_name": "North Vector Dynamics",
        "company_domain": "northvectordynamics.com",
        "company_url": "https://www.northvectordynamics.com/",
        "location": "Calgary, Alberta, Canada",
        "industry": "Hypersonic propulsion and autonomous defence systems",
        "source_url": "https://betakit.com/nordspaces-venture-arm-makes-undisclosed-strategic-investment-in-north-vector-dynamics/",
        "source_title": "NordSpace's venture arm makes undisclosed strategic investment in North Vector Dynamics",
        "source_publisher": "BetaKit",
        "signal_label": "Strategic investment accelerates sovereign hypersonic-propulsion partnership",
        "signal_date": datetime(2026, 7, 31, 12, 0, tzinfo=timezone.utc),
        "challenge_summary": (
            "On July 31, 2026, BetaKit reported that NordSpace Ventures made an undisclosed "
            "strategic investment in Calgary-based North Vector Dynamics (NVD), deepening an "
            "active technical partnership around rocket propulsion, sovereign missile capability, "
            "and hypersonic technologies. NVD already holds a $4.2-million National Defence "
            "contract for high-speed and hypersonic aeropropulsion and participates in a DND-backed "
            "hypersonic innovation network. Inference: moving propulsion research toward integrated "
            "missile and space-launch hardware creates strict requirements, configuration, simulation, "
            "interface, test-evidence, safety, and supplier-control demands across two engineering teams."
        ),
        "why_relevant": (
            "Teamcenter can control propulsion product structures, configurations, suppliers, and "
            "engineering changes; NX and Simcenter can support detailed aeropropulsion design and "
            "multiphysics validation. Polarion can trace defence requirements into verification and "
            "test evidence. The July 31 investment creates urgency because NVD and NordSpace are "
            "accelerating overlapping roadmaps from contracted R&D toward sovereign fieldable capability."
        ),
        "recommended_products": ["Teamcenter", "NX", "Simcenter", "Polarion"],
        "opportunity_score": 96,
        "manufacturing_fit_score": 98,
        "trigger_score": 96,
        "solution_fit_score": 98,
        "evidence_quality_score": 97,
    },
    {
        "keyword_id": 2,
        "company_name": "Mecademic",
        "company_domain": "mecademic.com",
        "company_url": "https://mecademic.com/",
        "location": "Montreal, Quebec, Canada",
        "industry": "Compact precision industrial robot manufacturing",
        "source_url": "https://betakit.com/mecademic-secures-21-million-to-bring-its-tiny-industrial-robots-to-the-world/",
        "source_title": "Mecademic secures $21 million to bring its tiny industrial robots to the world",
        "source_publisher": "BetaKit",
        "signal_label": "$21M funding for headquarters expansion and global industrial-robot scale-up",
        "signal_date": datetime(2026, 2, 19, 12, 0, tzinfo=timezone.utc),
        "challenge_summary": (
            "On February 19, 2026, Mecademic announced a $21-million strategic round led by "
            "Investissement Quebec with EDC and BDC participation to expand its Montreal headquarters, "
            "hire in the United States, Europe, and Asia, and scale compact precision robots used in "
            "electronics, medical-device, component, and biopharmaceutical manufacturing. Inference: "
            "scaling a safety-critical mechatronic product family across regulated customer segments "
            "increases mechanical, electrical, controls-software, variant, supplier, calibration, and "
            "quality-traceability complexity."
        ),
        "why_relevant": (
            "Teamcenter can govern robot configurations, electronics, firmware, suppliers, and changes; "
            "NX and Capital can support mechanical and electrical development. Polarion can trace "
            "requirements, defects, and validation evidence, while Opcenter can preserve assembly and "
            "calibration genealogy. The funded headquarters expansion makes the opportunity timely as "
            "Mecademic prepares its product and production systems for international volume."
        ),
        "recommended_products": ["Teamcenter", "NX", "Capital", "Polarion", "Opcenter"],
        "opportunity_score": 92,
        "manufacturing_fit_score": 100,
        "trigger_score": 91,
        "solution_fit_score": 97,
        "evidence_quality_score": 94,
    },
    {
        "keyword_id": 3,
        "company_name": "Allied Marine & Industrial",
        "company_domain": "allmind.com",
        "company_url": "https://allmind.com/",
        "location": "Port Colborne, Ontario, Canada",
        "industry": "Commercial vessel repair, refit, fabrication, and marine industrial services",
        "source_url": "https://canada.constructconnect.com/dcn/news/infrastructure/2026/07/90m-flowing-to-ontarios-shipbuilding-industry",
        "source_title": "$90M flowing to Ontario's shipbuilding industry",
        "source_publisher": "Daily Commercial News / ConstructConnect",
        "signal_label": "$8M-plus grant for shipyard infrastructure, machinery, equipment, and skills",
        "signal_date": datetime(2026, 7, 14, 10, 15, tzinfo=timezone.utc),
        "challenge_summary": (
            "On July 14, 2026, Daily Commercial News reported that Ontario is investing more than "
            "$8 million in Allied Marine & Industrial at Port Colborne through the Ontario "
            "Shipbuilding Grant Program. The funding is specifically allocated to skills training, "
            "infrastructure improvements, and new machinery and equipment as the province expands "
            "capacity for vessel construction, repair, refit, and maintenance. Inference: adding yard "
            "capacity and equipment while executing customer-specific vessel work increases planning, "
            "configuration, drawing, supplier, work-package, welding-quality, and as-maintained-record pressure."
        ),
        "why_relevant": (
            "Teamcenter can control vessel configurations, drawings, materials, work packages, and "
            "engineering changes; Tecnomatix can help plan revised yard and fabrication processes. "
            "Opcenter can provide execution, inspection, and repair genealogy for refit and fabrication "
            "work. The grant is a current buying trigger because Allied must now integrate new machinery, "
            "infrastructure, and trained staff into a repeatable delivery system."
        ),
        "recommended_products": ["Teamcenter", "Tecnomatix", "Opcenter"],
        "opportunity_score": 88,
        "manufacturing_fit_score": 94,
        "trigger_score": 93,
        "solution_fit_score": 91,
        "evidence_quality_score": 92,
    },
    {
        "keyword_id": 4,
        "company_name": "Kiwi Charge",
        "company_domain": "kiwicharge.com",
        "company_url": "https://kiwicharge.com/",
        "location": "Toronto, Ontario, Canada",
        "industry": "Autonomous mobile electric-vehicle charging robots",
        "source_url": "https://betakit.com/kiwi-charge-takes-ev-charging-robot-to-showroom-floor-with-1-7-million-pilot-project/",
        "source_title": "Kiwi Charge takes EV-charging robot to showroom floor with $1.7-million pilot project",
        "source_publisher": "BetaKit",
        "signal_label": "$1.7M GM Canada and Pfaff pilot moves charging robot into continuous operation",
        "signal_date": datetime(2026, 2, 9, 13, 0, tzinfo=timezone.utc),
        "challenge_summary": (
            "On February 9, 2026, Kiwi Charge unveiled a $1.7-million pilot with General Motors "
            "Canada and Pfaff Automotive to rapidly prototype and run its autonomous EV-charging "
            "robot continuously at Pfaff's Porsche dealership in Vaughan. The pilot includes a "
            "$500,000 OVIN grant, $250,000 in-kind support from GM and Pfaff, and company capital, "
            "while Kiwi was also working to close a $1-million seed round. Inference: moving from a "
            "duct-taped prototype to unattended customer operation creates urgent battery, mobility, "
            "safety, controls-software, charging-interface, reliability, and field-change complexity."
        ),
        "why_relevant": (
            "Teamcenter can govern the robot's mechanical, electrical, battery, and software "
            "configurations; Polarion can trace unattended-operation and charging-safety requirements "
            "into tests and defects. NX and Capital can support mechanical and electrical design, while "
            "Simcenter can support thermal, structural, and motion validation. The customer pilot makes "
            "the need immediate because failures and uncontrolled revisions now affect live dealership operations."
        ),
        "recommended_products": ["Teamcenter", "Polarion", "NX", "Capital", "Simcenter"],
        "opportunity_score": 91,
        "manufacturing_fit_score": 96,
        "trigger_score": 94,
        "solution_fit_score": 97,
        "evidence_quality_score": 95,
    },
]


SEARCH_RESULTS = {1: 1, 2: 1, 3: 4, 4: 1}


def main() -> None:
    load_dotenv()
    database = Database()
    database.initialize()
    keywords = {keyword.id: keyword for keyword in database.list_keywords()}

    for item in QUALIFIED:
        if item["keyword_id"] not in keywords:
            raise RuntimeError(f"Keyword {item['keyword_id']} no longer exists")
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
            pain_signals=[item["challenge_summary"]],
            expansion_signals=[item["signal_label"]],
            raw_score=item["opportunity_score"],
            confidence=item["evidence_quality_score"] / 100,
            reason=item["why_relevant"],
            source_url=item["source_url"],
            source_title=item["source_title"],
            detected_at=item["signal_date"],
        )
        saved = database.save_signal(signal)
        company = database.upsert_company(signal)
        ledger = database.record_keyword_company(
            item["keyword_id"],
            item["company_name"],
            item["company_domain"],
            source_url=item["source_url"],
            source_title=item["source_title"],
            source_publisher=item["source_publisher"],
            signal_label=item["signal_label"],
            signal_date=item["signal_date"],
            challenge_summary=item["challenge_summary"],
            why_relevant=item["why_relevant"],
            recommended_products=item["recommended_products"],
            qualification_status="qualified",
            opportunity_score=item["opportunity_score"],
            manufacturing_fit_score=item["manufacturing_fit_score"],
            trigger_score=item["trigger_score"],
            solution_fit_score=item["solution_fit_score"],
            evidence_quality_score=item["evidence_quality_score"],
        )
        if company is None or ledger is None:
            raise RuntimeError(f"Could not persist {item['company_name']}")
        print(
            f"{item['company_name']}: signal_created={saved.created} "
            f"qualification={ledger.qualification_status}"
        )

    for keyword_id, result_count in SEARCH_RESULTS.items():
        database.record_keyword_search(keyword_id, result_count=result_count)
        print(f"{keywords[keyword_id].keyword}: verified_relevant={result_count}")


if __name__ == "__main__":
    main()
