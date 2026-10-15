from __future__ import annotations

from datetime import datetime, timezone

from dotenv import load_dotenv

from db.database import Database
from models.schema import ExtractedSignal


QUALIFIED = [
    {
        "keyword_id": 1,
        "company_name": "Pratt & Whitney",
        "company_domain": "prattwhitney.com",
        "company_url": "https://www.prattwhitney.com/",
        "location": "Longueuil, Quebec, Canada",
        "industry": "Aircraft engine design and manufacturing",
        "source_url": (
            "https://www.canada.ca/en/innovation-science-economic-development/news/"
            "2026/07/minister-joly-announces-engagement-with-pratt--whitney-canada-"
            "to-strengthen-canadas-aerospace-sector.html"
        ),
        "source_title": (
            "Minister Joly announces engagement with Pratt & Whitney Canada to "
            "strengthen Canada’s aerospace sector"
        ),
        "source_publisher": "Innovation, Science and Economic Development Canada",
        "signal_label": "$275M Longueuil aircraft-engine manufacturing modernization",
        "signal_date": datetime(2026, 7, 21, 12, 0, tzinfo=timezone.utc),
        "challenge_summary": (
            "On July 21, 2026, Canada announced up to $34 million toward Pratt & "
            "Whitney Canada's $275-million modernization of its aircraft-engine "
            "manufacturing centre of excellence in Longueuil, Quebec, supporting 650 "
            "jobs. The site designs, develops, manufactures, and maintains gas-turbine "
            "engines and auxiliary power units. Inference: modernizing advanced engine "
            "production creates a live need to coordinate product and process revisions, "
            "validate new manufacturing methods, qualify equipment, and preserve "
            "regulated quality and genealogy records during the transition."
        ),
        "why_relevant": (
            "Teamcenter can govern engine configurations, manufacturing BOMs, tooling, "
            "and changes; Tecnomatix can validate revised factory processes and equipment "
            "layouts before deployment. Opcenter can manage production execution, quality, "
            "and traceability, while Simcenter supports engine and process validation where "
            "required. The opportunity is current because a funded modernization program "
            "must now move from investment approval into plant implementation."
        ),
        "recommended_products": ["Teamcenter", "Tecnomatix", "Opcenter", "Simcenter"],
        "opportunity_score": 94,
        "manufacturing_fit_score": 100,
        "trigger_score": 98,
        "solution_fit_score": 98,
        "evidence_quality_score": 100,
    },
    {
        "keyword_id": 2,
        "company_name": "Huys Industries",
        "company_domain": "huysindustries.com",
        "company_url": "https://huysindustries.com/",
        "location": "Etobicoke, Ontario, Canada",
        "industry": "Resistance-welding consumables and electrospark-deposition equipment",
        "source_url": (
            "https://www.canada.ca/en/economic-development-southern-ontario/news/"
            "2026/07/government-of-canada-supports-etobicoke-manufacturing-business-"
            "in-adopting-ai.html"
        ),
        "source_title": (
            "Government of Canada supports Etobicoke manufacturing business in adopting AI"
        ),
        "source_publisher": (
            "Federal Economic Development Agency for Southern Ontario"
        ),
        "signal_label": "$1.3M AI-powered welding-system development and commercialization",
        "signal_date": datetime(2026, 7, 9, 12, 0, tzinfo=timezone.utc),
        "challenge_summary": (
            "On July 9, 2026, FedDev Ontario announced approximately $660,000 toward "
            "Huys Industries' project of more than $1.3 million to integrate and validate "
            "AI in its electrospark-deposition welding system and commercialize the new "
            "product. Huys also manufactures millions of resistance-welding consumables "
            "and is ISO 9001 certified. Inference: adding AI, validation data, software "
            "versions, and new product configurations to an established equipment line "
            "increases multidisciplinary requirements, design-change, test-evidence, and "
            "manufacturing-quality complexity."
        ),
        "why_relevant": (
            "Teamcenter can control mechanical, electrical, software, and manufacturing "
            "configurations for the new system; Polarion can trace AI and welding "
            "requirements into validation results and defects. NX can support equipment "
            "design, while Opcenter can maintain production and quality traceability for "
            "machines and consumables. The timing is immediate because integration, "
            "validation, and commercialization are the funded work now underway."
        ),
        "recommended_products": ["Teamcenter", "Polarion", "NX", "Opcenter"],
        "opportunity_score": 91,
        "manufacturing_fit_score": 98,
        "trigger_score": 94,
        "solution_fit_score": 96,
        "evidence_quality_score": 100,
    },
    {
        "keyword_id": 3,
        "company_name": "Connor Industries Ltd.",
        "company_domain": "stanleyboats.ca",
        "company_url": "https://stanleyboats.ca/",
        "location": "Parry Sound, Ontario, Canada",
        "industry": "Welded aluminum boat manufacturing",
        "source_url": (
            "https://news.ontario.ca/en/release/1007712/"
            "ontario-investing-more-than-90-million-to-support-expanded-"
            "provincial-shipbuilding-capacity"
        ),
        "source_title": (
            "Ontario Investing More than $90 Million to Support Expanded Provincial "
            "Shipbuilding Capacity"
        ),
        "source_publisher": "Government of Ontario",
        "signal_label": "$1.1M grant for new boatbuilding equipment and capacity growth",
        "signal_date": datetime(2026, 7, 8, 12, 0, tzinfo=timezone.utc),
        "challenge_summary": (
            "On July 8, 2026, Ontario awarded Connor Industries $1.1 million through "
            "the Ontario Shipbuilding Grant Program for equipment, infrastructure, and "
            "workforce growth at its Parry Sound operation, where it manufactures Stanley "
            "welded-aluminum boats. The company said the funding creates an immediate "
            "ability to add equipment and jobs for long-term growth. Inference: expanding "
            "custom boat production increases control needs across hull and outfitting "
            "variants, customer options, drawings, purchasing, build sequences, welding "
            "quality, and as-built records."
        ),
        "why_relevant": (
            "Solid Edge can support configurable aluminum-vessel design for a small-to-"
            "mid-sized manufacturer, and Teamcenter can govern drawings, BOMs, options, "
            "supplier data, and engineering changes. Opcenter can provide work-order, "
            "welding-quality, and as-built traceability as equipment and headcount expand. "
            "The grant creates a near-term opening because the company is deciding how new "
            "equipment and processes will fit into its production system."
        ),
        "recommended_products": ["Solid Edge", "Teamcenter", "Opcenter"],
        "opportunity_score": 86,
        "manufacturing_fit_score": 100,
        "trigger_score": 89,
        "solution_fit_score": 92,
        "evidence_quality_score": 96,
    },
    {
        "keyword_id": 3,
        "company_name": "MetalCraft Marine",
        "company_domain": "metalcraftmarine.com",
        "company_url": "https://www.metalcraftmarine.com/",
        "location": "Kingston, Ontario, Canada",
        "industry": "High-speed aluminum patrol, fire, rescue, and workboat manufacturing",
        "source_url": (
            "https://news.ontario.ca/en/release/1007712/"
            "ontario-investing-more-than-90-million-to-support-expanded-"
            "provincial-shipbuilding-capacity"
        ),
        "source_title": (
            "Ontario Investing More than $90 Million to Support Expanded Provincial "
            "Shipbuilding Capacity"
        ),
        "source_publisher": "Government of Ontario",
        "signal_label": "$6M-plus capacity and equipment modernization for mission-ready boats",
        "signal_date": datetime(2026, 7, 8, 12, 0, tzinfo=timezone.utc),
        "challenge_summary": (
            "On July 8, 2026, Ontario committed more than $6 million to MetalCraft Marine "
            "for skills, infrastructure, machinery, and equipment supporting its Kingston "
            "production of purpose-built fire, police, border-security, and military boats. "
            "Its portfolio includes numerous patrol, fire, rescue, workboat, and uncrewed "
            "variants with propulsion, electronics, cabin, and mission-system options. "
            "Inference: funded capacity expansion across a highly configurable vessel family "
            "increases BOM, requirements, supplier, change-control, commissioning, and "
            "as-built traceability pressure."
        ),
        "why_relevant": (
            "Teamcenter can manage vessel families, customer configurations, engineering "
            "changes, and supplier BOMs; NX and Capital can support hull, mechanical, "
            "electrical, and mission-system integration. Polarion can trace government "
            "requirements into verification, and Opcenter can preserve build and quality "
            "genealogy. The opportunity is current because public funding is now tied to "
            "equipment and infrastructure modernization for expanding defence-sector demand."
        ),
        "recommended_products": ["Teamcenter", "NX", "Capital", "Polarion", "Opcenter"],
        "opportunity_score": 93,
        "manufacturing_fit_score": 100,
        "trigger_score": 96,
        "solution_fit_score": 98,
        "evidence_quality_score": 98,
    },
    {
        "keyword_id": 4,
        "company_name": "PowerCo Canada Inc.",
        "company_domain": "powerco.de",
        "company_url": "https://www.powerco.de/",
        "location": "St. Thomas, Ontario, Canada",
        "industry": "Electric-vehicle battery-cell manufacturing",
        "source_url": (
            "https://careers.powerco.de/PowerCo_Canada_Inc/job/St_-Thomas-"
            "Senior-Analyst%2C-IT-Energy-%26-HSE-Applications-ON/1386602533/"
        ),
        "source_title": "Senior Analyst, IT Energy & HSE Applications",
        "source_publisher": "PowerCo Canada Inc.",
        "signal_label": (
            "St. Thomas gigafactory ramp creates facility-application ownership role"
        ),
        "signal_date": datetime(2026, 7, 21, 12, 0, tzinfo=timezone.utc),
        "challenge_summary": (
            "On July 21, 2026, PowerCo Canada advertised a new application-owner role "
            "for energy management, health and safety, building automation, and facility "
            "monitoring as it ramps Volkswagen Group's largest battery-cell factory in "
            "St. Thomas. The role must translate requirements across IT, facilities, "
            "engineering, sustainability, and safety teams, providing direct evidence of "
            "cross-system integration pressure during factory launch. Inference: ramping a "
            "high-volume battery plant requires controlled facility requirements, equipment "
            "interfaces, process versions, quality genealogy, and real-time production and "
            "energy visibility."
        ),
        "why_relevant": (
            "Opcenter can provide production execution, quality, and cell genealogy; "
            "Tecnomatix can validate factory and material-flow processes as equipment is "
            "commissioned. Teamcenter can govern product, process, equipment, and change "
            "definitions, while Polarion can trace safety, environmental, and facility "
            "requirements into validation. The newly posted ownership role makes the need "
            "timely because PowerCo is establishing its operational application landscape now."
        ),
        "recommended_products": ["Opcenter", "Tecnomatix", "Teamcenter", "Polarion"],
        "opportunity_score": 95,
        "manufacturing_fit_score": 100,
        "trigger_score": 96,
        "solution_fit_score": 99,
        "evidence_quality_score": 94,
    },
]

SEARCH_RESULTS = {1: 1, 2: 1, 3: 2, 4: 1}


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
        print(f"{keywords[keyword_id].keyword}: published={result_count}")


if __name__ == "__main__":
    main()
