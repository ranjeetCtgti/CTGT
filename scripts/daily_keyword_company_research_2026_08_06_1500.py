from __future__ import annotations

from datetime import datetime, timezone

from dotenv import load_dotenv

from db.database import Database
from models.schema import ExtractedSignal


SEEN_AT = datetime.now(timezone.utc)
SIGNAL_DATE = datetime(2026, 5, 26, tzinfo=timezone.utc)
SOURCE_URL = "https://betakit.com/sentinel-inks-partnership-to-supply-drones-to-ukraine/"


def main() -> None:
    load_dotenv()
    database = Database()
    database.initialize()
    keywords = {item.id: item for item in database.list_keywords()}

    signal = ExtractedSignal(
        company_name="Sentinel R&D",
        company_domain="sentinelrd.com",
        company_url="https://www.sentinelrd.com/",
        linkedin_url="https://www.linkedin.com/company/sentinel-rd/",
        location="Hamilton, Ontario, Canada",
        industry="Defence aerospace and modular unmanned-aircraft manufacturing",
        company_industry="Modular UAV and automated composite manufacturing",
        software=[],
        signal_type="news",
        signal_source="news",
        pain_signals=[
            "Must control modular mission configurations and supplier-approved components across multiple UAV variants.",
            "Must industrialize robotic fibre placement, resin infusion, post-processing, and airframe assembly in a new Canadian facility.",
            "Defence deployment creates requirements, verification, export-control, and build-traceability obligations.",
        ],
        expansion_signals=[
            "A Canada-Ukraine government-supported joint venture will manufacture drones in Canada for delivery to Ukraine.",
            "Sentinel will manufacture airframes and jointly invest in a new Canadian manufacturing facility, with Ontario and Alberta under consideration.",
        ],
        raw_score=92,
        confidence=0.94,
        reason=(
            "On May 26, 2026, BetaKit reported that Sentinel R&D and Kyiv-based Airlogix formed a 50-50 joint venture to manufacture drones in Canada for Ukraine; Sentinel will also manufacture the airframes. The drones are specified for speeds up to 180 km/h and a 500 km range, and the partners plan a new Canadian manufacturing facility. Sentinel's official site independently confirms that it builds modular UAVs using automated composite manufacturing, robotic fibre placement, intelligent resin infusion, post-process automation, and NATO-aligned sourcing. Inference: moving a configurable defence aircraft from development into a new production site creates immediate pressure on product configuration, requirements and verification, composite-process planning, build genealogy, supplier control, and production quality."
        ),
        source_url=SOURCE_URL,
        source_title="Sentinel inks partnership to supply drones to Ukraine",
        detected_at=SIGNAL_DATE,
    )

    saved = database.save_signal(signal)
    database.upsert_company(signal)
    linked = database.record_keyword_company(
        1,
        "Sentinel R&D",
        "sentinelrd.com",
        source_url=SOURCE_URL,
        source_title="Sentinel inks partnership to supply drones to Ukraine",
        source_publisher="BetaKit",
        signal_label="Canada-Ukraine UAV manufacturing joint venture and new Canadian factory",
        signal_date=SIGNAL_DATE,
        challenge_summary=(
            "On May 26, 2026, BetaKit reported that Hamilton-based Sentinel R&D and Kyiv-based Airlogix formed a 50-50 joint venture to manufacture fixed-wing drones in Canada for Ukraine, with Sentinel also responsible for airframe production. The aircraft are designed for speeds up to 180 km/h and a 500 km range, and the partners intend to invest jointly in a new Canadian manufacturing facility, considering Ontario and Alberta. Sentinel's official site confirms modular UAVs built with robotic fibre placement, intelligent resin infusion, post-process automation, and a NATO-aligned supply chain. Inference: the new plant and defence deployment create immediate configuration, composite-process, supplier, requirements, verification, and build-traceability complexity."
        ),
        why_relevant=(
            "Teamcenter can control modular aircraft configurations, approved suppliers, BOM changes, and the engineering-to-production baseline. Opcenter and Tecnomatix can plan and govern automated composite work cells, airframe assembly, quality records, and production ramp-up; Polarion can connect mission and defence requirements to verification evidence. The government-supported joint venture and planned new factory make this a near-term systems decision rather than a speculative future need."
        ),
        recommended_products=["Teamcenter", "Opcenter", "Tecnomatix", "Polarion"],
        qualification_status="qualified",
        opportunity_score=92,
        manufacturing_fit_score=97,
        trigger_score=95,
        solution_fit_score=94,
        evidence_quality_score=92,
        seen_at=SEEN_AT,
    )
    if linked is None:
        raise RuntimeError("Sentinel R&D could not be linked to the aerospace keyword")

    database.record_keyword_search(1, result_count=1)
    database.record_keyword_search(2, result_count=0)
    database.record_keyword_search(3, result_count=0)
    database.record_keyword_search(4, result_count=0)

    print(
        "Sentinel R&D: "
        f"company_id={linked.company_id} signal_created={saved.created} "
        f"keyword_link_id={linked.id} status={linked.qualification_status}"
    )
    print("Keyword checks recorded: aerospace=1 robotics=0 shipbuilding=0 automotive=0")
    print(f"Loaded persistent keywords: {len(keywords)}")


if __name__ == "__main__":
    main()
