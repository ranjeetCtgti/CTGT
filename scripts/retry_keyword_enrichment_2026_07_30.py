from __future__ import annotations

from datetime import datetime, timezone

from dotenv import load_dotenv

from db.database import Database, EnrichmentLogEntry
from models.schema import ExtractedSignal, LeadContact


NOW = datetime.now(timezone.utc)


def contact(
    name: str,
    title: str,
    linkedin_url: str | None = None,
    *,
    stage: str,
) -> LeadContact:
    parts = name.split()
    return LeadContact(
        full_name=name,
        first_name=parts[0],
        last_name=parts[-1] if len(parts) > 1 else None,
        title=title,
        linkedin_url=linkedin_url,
        source_provider="linkedin",
        source_stage=stage,
    )


ENRICHMENTS = [
    {
        "name": "PowerCo Canada Inc.",
        "domain": "powerco.de",
        "linkedin_url": "https://www.linkedin.com/company/powerco-se",
        "sector": "Electric-vehicle battery-cell manufacturing",
        "headquarters": "St. Thomas, Ontario, Canada",
        "employee_count": "1,001-5,000 globally",
        "contacts": [
            contact(
                "Mustafa Bulut",
                "COO and Interim CEO, PowerCo Canada Inc.",
                stage="public_linkedin_company_post_verified",
            )
        ],
        "signal": {
            "source_url": "https://in.linkedin.com/company/powerco-se",
            "source_title": "PowerCo | LinkedIn",
            "industry": "Electric-vehicle battery-cell manufacturing",
            "software": [],
            "pain": [
                "Coordinating the ramp-up of three battery-cell factories and a new regional supply chain"
            ],
            "expansion": [
                "Ramping three cell factories in Germany, Spain, and Canada with combined capacity up to 200 GWh per year"
            ],
            "reason": (
                "PowerCo's public company profile states that it is ramping three battery-cell "
                "factories with combined capacity of up to 200 GWh per year, including St. "
                "Thomas. This verifies a live multi-site production and supply-chain scale-up; "
                "no named PLM or MES platform was found in the reviewed source."
            ),
            "score": 70,
            "confidence": 0.96,
        },
    },
    {
        "name": "MetalCraft Marine",
        "domain": "metalcraftmarine.com",
        "linkedin_url": "https://www.linkedin.com/company/metalcraft-marine-inc-",
        "sector": "Custom aluminum patrol, fire, rescue, and workboat manufacturing",
        "headquarters": "Kingston, Ontario, Canada",
        "employee_count": "51-200",
        "contacts": [
            contact(
                "Michael Reed",
                "General Manager",
                stage="government_release_verified",
            ),
            contact(
                "Ryan Hunter",
                "Project Manager",
                "https://ca.linkedin.com/in/ryan-d-hunter",
                stage="public_linkedin_profile_verified",
            ),
        ],
        "signal": {
            "source_url": "https://www.linkedin.com/company/metalcraft-marine-inc-",
            "source_title": "MetalCraft Marine Inc. | LinkedIn",
            "industry": "Custom aluminum patrol, fire, rescue, and workboat manufacturing",
            "software": [],
            "pain": [
                "ABS-compliant welding, electrical integration, and material compatibility across custom vessels"
            ],
            "expansion": [
                "More than 120 designers, craftspeople, and support staff across Canadian and U.S. facilities",
                "More than 800 custom aluminum workboats delivered",
            ],
            "reason": (
                "MetalCraft Marine's public company page confirms a 120-plus-person team, "
                "more than 800 custom vessels, Canadian and U.S. facilities, ABS-compliant "
                "welding, and substantial electrical and corrosion-control requirements. "
                "These facts verify configuration, quality, and multi-site engineering "
                "complexity; no named PLM platform was found in the reviewed source."
            ),
            "score": 65,
            "confidence": 0.97,
        },
    },
    {
        "name": "Connor Industries Ltd.",
        "domain": "stanleyboats.ca",
        "linkedin_url": "https://ca.linkedin.com/company/connor-industries",
        "sector": "Welded aluminum boat manufacturing",
        "headquarters": "Parry Sound, Ontario, Canada",
        "employee_count": "51-200",
        "contacts": [
            contact(
                "Gerry Ramsay",
                "Executive Vice President",
                stage="government_release_verified",
            )
        ],
        "signal": {
            "source_url": "https://ca.linkedin.com/company/connor-industries",
            "source_title": "Connor Industries | LinkedIn",
            "industry": "Welded aluminum boat manufacturing",
            "software": [],
            "pain": [
                "Managing two configurable aluminum-boat product brands from one Parry Sound manufacturing operation"
            ],
            "expansion": [
                "Manufactures Stanley and Lighthouse aluminum boats",
                "Public company profile reports 51-200 employees",
            ],
            "reason": (
                "Connor Industries' public company profile verifies that its Parry Sound "
                "operation designs and manufactures both Stanley and Lighthouse aluminum "
                "boats with 51-200 employees. Combined with its current equipment grant, this "
                "is meaningful profile and product-complexity evidence; no named PLM, CAD, "
                "or MES platform was found in the reviewed source."
            ),
            "score": 58,
            "confidence": 0.94,
        },
    },
    {
        "name": "Huys Industries",
        "domain": "huysindustries.com",
        "linkedin_url": "https://www.linkedin.com/company/huys-industries-limited",
        "sector": "Resistance-welding equipment, consumables, coatings, and simulation",
        "headquarters": "Etobicoke, Ontario, Canada",
        "employee_count": "51-200",
        "contacts": [
            contact(
                "Hugh Scotchmer",
                "President",
                "https://ca.linkedin.com/in/hugh-scotchmer-48a88266",
                stage="linkedin_connector_and_government_release_verified",
            ),
            contact(
                "Kevin Chan",
                "Vice President of Engineering",
                "https://ca.linkedin.com/in/kevin-chan-4703719",
                stage="linkedin_connector_and_company_post_verified",
            ),
        ],
        "signal": {
            "source_url": "https://www.linkedin.com/company/huys-industries-limited",
            "source_title": "Huys Industries | LinkedIn",
            "industry": "Resistance-welding equipment, consumables, coatings, and simulation",
            "software": ["SORPAS"],
            "pain": [
                "Integrating welding simulation, optimization, AI surrogate models, and digital twins with physical equipment and consumables"
            ],
            "expansion": [
                "Commercializing AI-enabled SORPAS digital-twin capabilities for spot welding",
                "Supplying aerospace, rail, automotive, and industrial manufacturers",
            ],
            "reason": (
                "Huys Industries' public company page identifies SORPAS welding-simulation "
                "software, AI-enabled digital twins, physical welding equipment, coatings, "
                "and consumables serving multiple regulated manufacturing sectors. This is "
                "direct evidence of mixed software/hardware product configuration and "
                "validation complexity, although no PLM platform was named."
            ),
            "score": 72,
            "confidence": 0.98,
        },
    },
]


def main() -> None:
    load_dotenv()
    database = Database()
    database.initialize()

    for item in ENRICHMENTS:
        signal_data = item["signal"]
        signal = ExtractedSignal(
            company_name=item["name"],
            company_domain=item["domain"],
            company_url=f"https://{item['domain']}/",
            linkedin_url=item["linkedin_url"],
            location=item["headquarters"],
            industry=signal_data["industry"],
            company_industry=signal_data["industry"],
            software=signal_data["software"],
            signal_type="news",
            signal_source="linkedin",
            pain_signals=signal_data["pain"],
            expansion_signals=signal_data["expansion"],
            raw_score=signal_data["score"],
            confidence=signal_data["confidence"],
            reason=signal_data["reason"],
            source_url=signal_data["source_url"],
            source_title=signal_data["source_title"],
            detected_at=NOW,
        )
        saved = database.save_signal(signal)
        database.upsert_company(signal)
        company = database.save_company_enrichment(
            item["name"],
            item["domain"],
            linkedin_url=item["linkedin_url"],
            sector=item["sector"],
            employee_count=item["employee_count"],
            headquarters_location=item["headquarters"],
            contacts=item["contacts"],
            enrichment_source="scheduled_keyword_enrichment",
            mark_enriched_at=NOW,
        )
        if company is None:
            raise RuntimeError(f"Company disappeared during enrichment: {item['name']}")
        database.save_enrichment_log(
            EnrichmentLogEntry(
                company_name=item["name"],
                company_domain=item["domain"],
                stage="scheduled_keyword_enrichment",
                provider="browser_linkedin",
                status="success",
                message=(
                    f"Meaningful public enrichment saved: {len(item['contacts'])} "
                    f"verified contacts; signal_created={saved.created}"
                ),
                payload={
                    "source_url": signal_data["source_url"],
                    "contacts_saved": len(item["contacts"]),
                    "signal_created": saved.created,
                },
            )
        )
        print(
            f"{item['name']}: contacts={len(item['contacts'])} "
            f"signal_created={saved.created} enriched=True"
        )


if __name__ == "__main__":
    main()
