from __future__ import annotations

from datetime import datetime, timezone

from dotenv import load_dotenv

from db.database import Database
from models.schema import ExtractedSignal


SOURCE_DATE = datetime(2026, 7, 27, 12, 0, tzinfo=timezone.utc)
HIKE_SOURCE_DATE = datetime(2026, 7, 28, 12, 0, tzinfo=timezone.utc)


QUALIFIED = [
    {
        "keyword_id": 1,
        "company_name": "PV Labs",
        "company_domain": "pv-labs.com",
        "company_url": "https://www.pv-labs.com/",
        "location": "Burlington, Ontario, Canada",
        "industry": "Aerospace and defence electro-optical/infrared imaging systems",
        "source_url": (
            "https://www.canada.ca/en/economic-development-southern-ontario/news/2026/07/"
            "government-of-canada-supports-growth-and-competitiveness-of-three-burlington-businesses.html"
        ),
        "source_title": (
            "Government of Canada supports growth and competitiveness of three "
            "Burlington businesses"
        ),
        "source_publisher": "Federal Economic Development Agency for Southern Ontario",
        "signal_label": "$14M domestic manufacturing expansion for next-generation EO/IR systems",
        "signal_date": SOURCE_DATE,
        "challenge_summary": (
            "On July 27, 2026, FedDev Ontario announced $5 million toward PV Labs' "
            "$14-million project to expand Canadian manufacturing of advanced aerial "
            "stabilization and electro-optical/infrared imaging systems and accelerate "
            "next-generation technology development. PV Labs' official product ecosystem "
            "contains multiple modular airborne imaging platforms built around a common, "
            "upgradeable architecture. Inference: expanding a regulated, variant-rich "
            "mechatronic product family increases pressure on BOM and configuration control, "
            "electrical/mechanical integration, verification evidence, and production "
            "traceability precisely as funded capacity comes online."
        ),
        "why_relevant": (
            "Teamcenter can govern the common platform architecture, product variants, "
            "engineering changes, and manufacturing BOMs; NX and Simcenter support the "
            "mechanical and stabilization engineering workload. Polarion and Capital fit "
            "traceable mission requirements, verification, and electrical/electronic "
            "architecture, while Opcenter can provide production and quality traceability. "
            "The July funding decision makes the need timely because PV Labs is now moving "
            "from product-platform development into expanded domestic production."
        ),
        "recommended_products": [
            "Teamcenter",
            "NX",
            "Simcenter",
            "Polarion",
            "Capital",
            "Opcenter",
        ],
        "opportunity_score": 94,
        "manufacturing_fit_score": 98,
        "trigger_score": 98,
        "solution_fit_score": 98,
        "evidence_quality_score": 96,
    },
    {
        "keyword_id": 3,
        "company_name": "Hike Metal Products",
        "company_domain": "hikemetal.com",
        "company_url": "https://hikemetal.com/",
        "location": "Wheatley, Ontario, Canada",
        "industry": "Custom workboat, patrol-vessel, and autonomous-vessel manufacturing",
        "source_url": (
            "https://navaltoday.com/2026/07/28/"
            "canada-and-uk-firms-join-forces-to-expand-autonomous-vessel-operations-in-north-america"
        ),
        "source_title": (
            "Canada and UK firms join forces to expand autonomous vessel operations "
            "in North America"
        ),
        "source_publisher": "Naval Today",
        "signal_label": "Production started for three licensed autonomous-vessel variants",
        "signal_date": HIKE_SOURCE_DATE,
        "challenge_summary": (
            "On July 28, 2026, Hike Metal Products and HydroSurv announced a technology "
            "licensing agreement under which Hike will manufacture, market, and support "
            "three uncrewed surface-vessel variants ranging from 2.5 to 6 metres in Canada "
            "and the United States; manufacturing of the first North American units has "
            "already begun. The lineup spans battery-electric and battery-hybrid propulsion, "
            "multi-day missions, heavier payloads, remotely operated vehicles, and towed "
            "arrays. Inference: transferring a UK design into local serial production while "
            "managing propulsion, payload, and mission variants creates immediate "
            "configuration, supplier, requirements, validation, and shop-floor traceability "
            "complexity."
        ),
        "why_relevant": (
            "Teamcenter can control the licensed product definition, vessel variants, BOMs, "
            "and engineering changes across Hike and HydroSurv; NX and Capital fit hull, "
            "mechanical, battery, controls, and payload integration. Polarion can trace "
            "government and commercial mission requirements into verification, while "
            "Opcenter can govern build and quality records for the newly started production "
            "run. The opportunity is current because manufacturing has already started and "
            "initial Canadian and U.S. deployments are planned."
        ),
        "recommended_products": ["Teamcenter", "NX", "Capital", "Polarion", "Opcenter"],
        "opportunity_score": 93,
        "manufacturing_fit_score": 100,
        "trigger_score": 98,
        "solution_fit_score": 97,
        "evidence_quality_score": 92,
    },
]


SEARCH_RESULTS = {
    1: 1,
    2: 0,
    3: 1,
    4: 0,
}


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
        database.upsert_company(signal)
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
        if ledger is None:
            raise RuntimeError(f"Could not link {item['company_name']} to its keyword")
        print(
            f"{item['company_name']}: signal_created={saved.created} "
            f"qualification={ledger.qualification_status}"
        )

    for keyword_id, result_count in SEARCH_RESULTS.items():
        database.record_keyword_search(keyword_id, result_count=result_count)
        print(
            f"{keywords[keyword_id].keyword}: "
            f"published={result_count}"
        )


if __name__ == "__main__":
    main()
