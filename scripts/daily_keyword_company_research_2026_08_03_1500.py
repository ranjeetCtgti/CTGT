from __future__ import annotations

from datetime import datetime, timezone

from dotenv import load_dotenv

from db.database import Database
from models.schema import ExtractedSignal


SOURCE_URL = (
    "https://www.canada.ca/en/innovation-science-economic-development/news/2026/07/"
    "government-of-canada-invests-70-million-to-strengthen-the-ev-battery-supply-chain-in-quebec.html"
)


def main() -> None:
    load_dotenv()
    database = Database()
    database.initialize()
    keywords = {keyword.id: keyword for keyword in database.list_keywords()}
    expected = {1, 2, 3, 4}
    if not expected.issubset(keywords):
        raise RuntimeError(f"Missing keyword ids: {sorted(expected - set(keywords))}")

    signal_date = datetime(2026, 7, 30, 12, 0, tzinfo=timezone.utc)
    challenge_summary = (
        "On July 30, 2026, the Government of Canada announced up to $70 million for Volta "
        "Energy Solutions Canada Inc.'s $760.9 million project to upgrade and expand an acquired "
        "Granby, Quebec facility into a battery-grade copper-foil plant. The project targets 25,000 "
        "tonnes of annual output beginning in 2027, later scaling to 63,000 tonnes, and is expected "
        "to create 260 jobs. Inference: commissioning a high-volume materials plant at that scale "
        "creates immediate equipment, process, recipe, quality, traceability, maintenance, supplier, "
        "and production-ramp control requirements."
    )
    why_relevant = (
        "Opcenter is the most direct fit for production execution, quality genealogy, and copper-foil "
        "process traceability; Tecnomatix can support line and process planning as the acquired site is "
        "reconfigured. Teamcenter can govern equipment, product, process, and supplier configurations, "
        "while Simcenter can support process-equipment and thermal validation where required. The "
        "July 30 funding decision makes the opportunity time-sensitive because the facility must be "
        "upgraded, commissioned, staffed, and stabilized before the stated 2027 production start."
    )
    recommended_products = ["Opcenter", "Tecnomatix", "Teamcenter", "Simcenter"]
    signal = ExtractedSignal(
        company_name="Volta Energy Solutions Canada Inc.",
        company_domain="volta-energysolutions.com",
        company_url="https://www.volta-energysolutions.com/en",
        location="Granby, Quebec, Canada",
        industry="Battery-grade copper foil manufacturing for EV and energy-storage cells",
        company_industry="Battery materials manufacturing",
        software=recommended_products,
        signal_type="news",
        signal_source="news",
        pain_signals=[challenge_summary],
        expansion_signals=[
            "$760.9M Granby copper-foil facility expansion backed by up to $70M in federal funding"
        ],
        raw_score=95,
        confidence=0.99,
        reason=why_relevant,
        source_url=SOURCE_URL,
        source_title=(
            "Government of Canada invests $70 million to strengthen the EV battery supply chain in Quebec"
        ),
        detected_at=signal_date,
    )
    saved = database.save_signal(signal)
    company = database.upsert_company(signal)
    ledger = database.record_keyword_company(
        4,
        "Volta Energy Solutions Canada Inc.",
        "volta-energysolutions.com",
        source_url=SOURCE_URL,
        source_title=(
            "Government of Canada invests $70 million to strengthen the EV battery supply chain in Quebec"
        ),
        source_publisher="Innovation, Science and Economic Development Canada",
        signal_label=(
            "$760.9M Granby copper-foil plant expansion targets 25,000 tonnes/year from 2027"
        ),
        signal_date=signal_date,
        challenge_summary=challenge_summary,
        why_relevant=why_relevant,
        recommended_products=recommended_products,
        qualification_status="qualified",
        opportunity_score=95,
        manufacturing_fit_score=100,
        trigger_score=98,
        solution_fit_score=96,
        evidence_quality_score=99,
    )
    if company is None or ledger is None:
        raise RuntimeError("Could not persist Volta Energy Solutions Canada Inc.")

    results = {1: 0, 2: 0, 3: 0, 4: 1}
    for keyword_id, result_count in results.items():
        database.record_keyword_search(keyword_id, result_count=result_count)
        print(f"keyword={keyword_id}|published={result_count}")
    print(
        "Volta Energy Solutions Canada Inc."
        f"|signal_created={saved.created}|qualification={ledger.qualification_status}"
    )


if __name__ == "__main__":
    main()
