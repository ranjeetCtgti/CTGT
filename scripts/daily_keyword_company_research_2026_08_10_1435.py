from __future__ import annotations

from datetime import datetime, timezone

from dotenv import load_dotenv

from db.database import Database
from models.schema import ExtractedSignal


SEEN_AT = datetime.now(timezone.utc)
SIGNAL_DATE = datetime(2026, 8, 5, tzinfo=timezone.utc)


def main() -> None:
    load_dotenv(".env")
    database = Database()
    database.initialize()

    keywords = {item.id: item for item in database.list_keywords()}
    expected_ids = {1, 2, 3, 4, 5}
    if set(keywords) != expected_ids:
        raise RuntimeError(f"Unexpected keyword ids: {sorted(keywords)}")

    challenge_summary = (
        "On August 5, 2026, Volatus Aerospace and Kraus Hamdani Aerospace announced a roadmap to introduce the fully electric K1000ULE autonomous aircraft and ATNE++ communications system in Canada, including progressive licensed domestic manufacturing at Volatus' Mirabel, Quebec aerospace facility. The program also requires Canadian systems integration, operator and maintainer training, lifecycle support, maintenance capability, and deployment for wildfire response, emergency management, critical infrastructure, Arctic operations, and defence; the aircraft already has more than 6,000 operational flight hours on U.S. military and allied missions. Inference: localizing an operational foreign platform for multiple Canadian civil and defence missions creates immediate configuration, requirements, supplier, manufacturing-process, maintenance, and verification complexity."
    )
    why_relevant = (
        "Teamcenter can govern the Canadian K1000ULE product baseline, licensed-manufacturing data, approved suppliers, payload variants, and engineering changes between Volatus and Kraus Hamdani. Polarion can connect wildfire, public-safety, Arctic, and defence mission requirements to integration and acceptance evidence, while Opcenter can provide unit genealogy, inspection, nonconformance, and production visibility as Mirabel manufacturing ramps. The partnership is already engaging governments, regulators, and public-safety agencies on requirements and demonstrations, so establishing the digital thread before Canadian production and deployment is a current priority."
    )

    signal = ExtractedSignal(
        company_name="Volatus Aerospace Inc.",
        company_domain="volatusaerospace.com",
        company_url="https://volatusaerospace.com/",
        linkedin_url="https://www.linkedin.com/company/volatus-aerospace/",
        location="Vaughan, Ontario and Mirabel, Quebec, Canada",
        industry="Autonomous aircraft engineering, manufacturing, and aerial intelligence",
        company_industry="Autonomous UAV engineering and licensed domestic aerospace manufacturing",
        software=[],
        signal_type="news",
        signal_source="news",
        pain_signals=[
            "Must localize and manufacture the K1000ULE and ATNE++ systems in Canada under a licensed-production roadmap.",
            "Must manage civil, wildfire, Arctic, critical-infrastructure, and defence configurations plus their verification evidence.",
            "Must establish Canadian systems integration, maintenance, training, and lifecycle-support capability around an operational platform.",
        ],
        expansion_signals=[
            "Plans progressive Canadian manufacturing at Volatus' Mirabel, Quebec aerospace facility.",
            "Is engaging governments, regulators, emergency-management organizations, and public-safety agencies on demonstrations and deployment pathways.",
        ],
        raw_score=91,
        confidence=0.94,
        reason=challenge_summary,
        source_url="https://www.canadianmanufacturing.com/manufacturing/volatus-and-kraus-hamdani-aerospace-partner-on-canadian-persistent-intelligence-capability-320518/",
        source_title="Volatus and Kraus Hamdani Aerospace partner on Canadian persistent intelligence capability",
        detected_at=SIGNAL_DATE,
    )

    saved = database.save_signal(signal)
    database.upsert_company(signal)
    linked = database.record_keyword_company(
        1,
        signal.company_name,
        signal.company_domain,
        source_url=str(signal.source_url),
        source_title=signal.source_title,
        source_publisher="Canadian Manufacturing",
        signal_label="K1000ULE partnership establishes licensed manufacturing at Mirabel",
        signal_date=SIGNAL_DATE,
        challenge_summary=challenge_summary,
        why_relevant=why_relevant,
        recommended_products=["Teamcenter", "Polarion", "Opcenter"],
        qualification_status="qualified",
        opportunity_score=91,
        manufacturing_fit_score=94,
        trigger_score=93,
        solution_fit_score=92,
        evidence_quality_score=90,
        seen_at=SEEN_AT,
    )
    if linked is None:
        raise RuntimeError("Could not link Volatus Aerospace to the aerospace keyword")

    for keyword_id, result_count in {1: 1, 2: 0, 3: 0, 4: 0, 5: 0}.items():
        database.record_keyword_search(keyword_id, result_count=result_count)

    published = [
        item
        for item in database.list_keyword_companies(limit=5000)
        if item.qualification_status in {"qualified", "watchlist"}
    ]
    unique_company_ids = {item.company_id for item in published}
    qualified_ids = {
        item.company_id for item in published if item.qualification_status == "qualified"
    }
    watchlist_only_ids = unique_company_ids - qualified_ids
    print(
        f"Volatus company_id={linked.company_id} signal_created={saved.created}; "
        f"published_unique={len(unique_company_ids)} qualified={len(qualified_ids)} "
        f"watchlist_only={len(watchlist_only_ids)}"
    )


if __name__ == "__main__":
    main()
