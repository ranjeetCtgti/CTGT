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
        "keyword_ids": [5, 8],
        "company_name": "Accuenergy Inc.",
        "company_domain": "accuenergy.com",
        "company_url": "https://www.accuenergy.com/",
        "linkedin_url": "https://www.linkedin.com/company/accuenergy/",
        "location": "Toronto, Ontario, Canada",
        "industry": "Industrial power and energy measurement hardware",
        "signal_date": dt(2026, 7, 21),
        "source_url": "https://www.accuenergy.com/press-release/accuenergy-secures-feddev-ontario-support-for-ai-innovation-and-manufacturing-expansion/",
        "source_title": "Accuenergy Secures Government of Canada Investment to Advance AI and Manufacturing Expansion",
        "source_publisher": "Accuenergy",
        "signal_label": "$10M manufacturing modernization project backed by $2.6M from FedDev Ontario",
        "challenge_summary": (
            "On July 21, 2026, Toronto-based Accuenergy announced a $10 million project backed by $2.6 million from FedDev Ontario to modernize manufacturing, develop manufacturing technology, expand production capacity, launch new energy-monitoring and building-automation products, and grow exports. Accuenergy designs and manufactures power meters, current transformers, power analyzers, control panels, and communications devices. Inference: adding products and capacity while introducing AI and new manufacturing technology creates immediate product-configuration, engineering-change, factory-integration, quality, and production-traceability pressure."
        ),
        "why_relevant": (
            "Teamcenter can control product variants, electronics/mechanical BOMs, released designs, and manufacturing changes across the expanding portfolio. Opcenter can provide production visibility, work-in-process and quality traceability, while Tecnomatix can plan and validate the modernized production flow. The project is funded and explicitly includes manufacturing expansion and new-product introduction, so the digital-thread decisions are being made now."
        ),
        "products": ["Teamcenter", "Opcenter", "Tecnomatix"],
        "scores": (94, 97, 96, 95, 96),
        "pain_signals": [
            "Must integrate new manufacturing technology and AI into an expanding production operation.",
            "Must govern additional energy-monitoring and building-automation product variants and quality records.",
        ],
        "expansion_signals": [
            "$10 million modernization project includes $2.6 million in FedDev Ontario support.",
            "Plans to expand manufacturing capacity, create skilled jobs, launch products, and increase exports.",
        ],
    },
    {
        "keyword_ids": [4, 5, 8],
        "company_name": "Mapleview Energy Inc.",
        "company_domain": "mapleviewenergy.com",
        "company_url": "https://mapleviewenergy.com/",
        "linkedin_url": "https://www.linkedin.com/company/mapleview-energy/",
        "location": "Toronto, Ontario, Canada",
        "industry": "Second-life EV battery energy-storage systems",
        "signal_date": None,
        "source_url": "https://www.ovinhub.ca/mapleview-energy-to-advance-second-life-battery-storage-for-agricultural-operations-with-support-from-the-government-of-ontario-through-ovin/",
        "source_title": "Mapleview Energy to Advance Second-Life Battery Storage for Agricultural Operations with Support from the Government of Ontario through OVIN",
        "source_publisher": "Ontario Vehicle Innovation Network",
        "signal_label": "$300K OVIN project moves a 600 kWh second-life EV-battery system into commercial deployment",
        "challenge_summary": (
            "In August 2026, Mapleview Energy announced a $300,000 project with Caspri Ventures, including $100,000 from Ontario through OVIN, to deploy a 600 kWh second-life EV-battery energy-storage system at an Ontario agricultural site. The AI-enabled system will integrate repurposed battery packs, managed charging, on-site solar, peak-demand control, and backup power as Mapleview moves from prototype validation to real-world commercial deployment. Inference: repurposed packs with different histories and health states create battery-configuration, diagnostics, controls, safety-test, field-commissioning, and lifecycle-traceability complexity."
        ),
        "why_relevant": (
            "Teamcenter can govern pack configurations, reused-battery provenance, hardware/controls BOMs, and field changes. Simcenter can support thermal and electrical validation, Polarion can link safety and performance requirements to pilot tests, and Opcenter can preserve assembly and test genealogy. The funded 600 kWh deployment is the first commercial-scale proof point, making disciplined configuration and verification urgent before follow-on sites."
        ),
        "products": ["Teamcenter", "Simcenter", "Polarion", "Opcenter"],
        "scores": (85, 91, 88, 90, 90),
        "pain_signals": [
            "Must characterize and configure second-life EV batteries with differing histories and health states.",
            "Must demonstrate safety, control performance, solar integration, and field reliability in a 600 kWh pilot.",
        ],
        "expansion_signals": [
            "$300,000 project includes $100,000 from Ontario through OVIN and $200,000 from Caspri Ventures.",
            "Company is moving from prototype validation into a paid commercial deployment.",
        ],
    },
    {
        "keyword_ids": [6, 7],
        "company_name": "New Horizon Aircraft Ltd.",
        "company_domain": "horizonaircraft.com",
        "company_url": "https://www.horizonaircraft.com/",
        "linkedin_url": "https://www.linkedin.com/company/horizon-aircraft-inc",
        "location": "Lindsay, Ontario, Canada",
        "industry": "Hybrid-electric vertical takeoff and landing aircraft",
        "signal_date": dt(2026, 7, 21),
        "source_url": "https://www.reuters.com/business/canadas-horizon-signs-letter-intent-sell-up-100-hybrid-electric-aircraft-worth-2026-07-21/",
        "source_title": "Canada's Horizon signs letter of intent to sell up to 100 hybrid-electric aircraft worth $600 million",
        "source_publisher": "Reuters",
        "signal_label": "$600M LOI covers five Cavorite X7 aircraft plus options for 95 more",
        "challenge_summary": (
            "On July 21, 2026, Ontario-based Horizon Aircraft signed a letter of intent with V-Star Powered Lift Aviation covering five Cavorite X7 hybrid-electric vertical-takeoff aircraft and options for 95 additional aircraft, a potential $600 million program. The aircraft combines a conventional wing and hybrid-electric propulsion with embedded lift fans and is targeted at medevac and air-ambulance missions. Inference: converting a prototype into a customer fleet of up to 100 safety-critical aircraft sharply increases certification, requirements, configuration, electrical architecture, supplier, verification, and production-planning complexity."
        ),
        "why_relevant": (
            "Teamcenter can establish the Cavorite X7 product baseline and manage fleet configurations, supplier BOMs, and engineering change. Polarion can connect airworthiness and mission requirements to verification evidence, Simcenter can support aerodynamic, structural, thermal, and system validation, and Capital can manage the hybrid-electric architecture. The signed five-aircraft commitment and 95 options create a near-term need to industrialize the program before order conversion and production scale-up."
        ),
        "products": ["Teamcenter", "Polarion", "Simcenter", "Capital"],
        "scores": (97, 98, 99, 98, 97),
        "pain_signals": [
            "Must industrialize a hybrid-electric VTOL aircraft under safety-critical certification and mission requirements.",
            "Must control aircraft, propulsion, electrical, supplier, and verification configurations for a potential 100-aircraft fleet.",
        ],
        "expansion_signals": [
            "$600 million potential program includes five committed aircraft and options for 95 additional aircraft.",
            "Customer intends Cavorite X7 use for medevac and air-ambulance missions.",
        ],
    },
    {
        "keyword_ids": [5, 8],
        "company_name": "Serenity Power Inc.",
        "company_domain": "serenitypower.ca",
        "company_url": "https://serenitypower.ca/",
        "linkedin_url": "https://www.linkedin.com/company/105534097/",
        "location": "Calgary, Alberta and Toronto, Ontario, Canada",
        "industry": "Compact solid oxide fuel-cell power systems",
        "signal_date": dt(2026, 4, 27),
        "source_url": "https://betakit.com/serenity-power-announces-1-million-pre-seed-investment/",
        "source_title": "Serenity Power announces $1 million pre-seed investment",
        "source_publisher": "BetaKit",
        "signal_label": "$1.16M pre-seed funds prototype validation and commercialization of compact fuel-cell systems",
        "challenge_summary": (
            "On April 27, 2026, Calgary- and Toronto-based Serenity Power closed an oversubscribed $1.16 million pre-seed round to validate and commercialize compact solid oxide fuel-cell systems and expand its team. Serenity is developing a 300 kW-class, fuel-flexible platform targeting greater than 60% efficiency, a sub-15-minute start, and a one-cubic-metre package for oil and gas, data-centre, remote-utility, and industrial use. Inference: meeting simultaneous thermal, electrochemical, packaging, fuel, controls, safety, and durability targets creates heavy simulation, requirements, design-change, prototype-test, and supplier-coordination demands."
        ),
        "why_relevant": (
            "Simcenter can support coupled thermal, flow, structural, and system-performance validation before expensive prototype iterations. Teamcenter can control stack, balance-of-plant, controls, and enclosure configurations, while Polarion can connect performance and safety requirements to test evidence. The funding round, CTO appointment, and stated move toward commercialization make this an active product-development window."
        ),
        "products": ["Simcenter", "Teamcenter", "Polarion"],
        "scores": (89, 95, 93, 94, 94),
        "pain_signals": [
            "Must validate tightly coupled thermal, electrochemical, controls, packaging, and durability targets.",
            "Must turn laboratory fuel-cell work into field-ready industrial power systems with auditable test evidence.",
        ],
        "expansion_signals": [
            "$1.16 million oversubscribed pre-seed round supports validation, commercialization, and team growth.",
            "Company appointed a CTO in May 2026 to lead technology and product development toward commercialization.",
        ],
    },
]


def main() -> None:
    load_dotenv(".env")
    database = Database()
    database.initialize()
    keywords = {item.id: item for item in database.list_keywords()}
    expected_ids = set(range(1, 9))
    if not expected_ids.issubset(keywords):
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
            detected_at=item["signal_date"] or SEEN_AT,
        )
        database.persist_signal(signal)

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
