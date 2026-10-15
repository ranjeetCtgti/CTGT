from __future__ import annotations

from datetime import datetime, timezone

from dotenv import load_dotenv

from db.database import Database, EnrichmentLogEntry
from models.schema import LeadContact


NOW = datetime.now(timezone.utc)


def contact(name: str, title: str, linkedin_url: str | None = None) -> LeadContact:
    parts = name.split()
    return LeadContact(
        full_name=name,
        first_name=parts[0],
        last_name=parts[-1],
        title=title,
        linkedin_url=linkedin_url,
        source_provider="official_company_site_and_public_profile",
        source_stage="same_day_keyword_enrichment",
    )


ITEMS = [
    {
        "name": "Accuenergy Inc.",
        "domain": "accuenergy.com",
        "linkedin_url": "https://www.linkedin.com/company/accuenergy/",
        "sector": "Industrial power and energy measurement hardware",
        "location": "Toronto, Ontario, Canada",
        "contacts": [
            contact(
                "Howard Wang",
                "President",
                "https://ca.linkedin.com/in/howard-wang-42133b51",
            )
        ],
        "evidence": (
            "Accuenergy's official September 4, 2025 supplier-award announcement identifies Howard Wang as President, and the public LinkedIn result matches him to Accuenergy in Toronto. The July 21, 2026 $10 million manufacturing-modernization trigger makes him the relevant executive for production-capacity, new-product, and manufacturing-system discussions."
        ),
    },
    {
        "name": "Mapleview Energy Inc.",
        "domain": "mapleviewenergy.com",
        "linkedin_url": "https://www.linkedin.com/company/mapleview-energy/",
        "sector": "Second-life EV battery energy-storage systems",
        "location": "Toronto, Ontario, Canada",
        "contacts": [
            contact(
                "Nick Nesbitt",
                "Founder and Chief Executive Officer",
                "https://www.linkedin.com/in/nick-nesbitt-8316b8148",
            )
        ],
        "evidence": (
            "Mapleview's August 2026 OVIN project announcement identifies Nick Nesbitt as Founder and CEO and provides him as the media contact. He owns the product and commercialization path for the funded 600 kWh second-life battery pilot."
        ),
    },
    {
        "name": "New Horizon Aircraft Ltd.",
        "domain": "horizonaircraft.com",
        "linkedin_url": "https://www.linkedin.com/company/horizon-aircraft-inc",
        "sector": "Hybrid-electric vertical takeoff and landing aircraft",
        "location": "Lindsay, Ontario, Canada",
        "contacts": [
            contact("Brandon Robinson", "Co-Founder and Chief Executive Officer")
        ],
        "evidence": (
            "Horizon Aircraft's official management page identifies Brandon Robinson as Chief Executive and Founder, and its May 22, 2026 program announcement identifies him as Co-Founder and CEO. He is the executive owner for the Cavorite X7 certification and industrialization path behind the five-aircraft commitment and 95 options."
        ),
    },
    {
        "name": "Serenity Power Inc.",
        "domain": "serenitypower.ca",
        "linkedin_url": "https://www.linkedin.com/company/105534097/",
        "sector": "Compact solid oxide fuel-cell power systems",
        "location": "Calgary, Alberta and Toronto, Ontario, Canada",
        "contacts": [
            contact("Aleisha Reese Cerny", "Chief Executive Officer and Co-Founder"),
            contact("Michael Pastula", "Chief Technology Officer"),
        ],
        "evidence": (
            "Serenity Power's official site identifies Aleisha Reese Cerny as CEO and Michael Pastula as CTO; its May 11, 2026 release says Pastula leads technology and product development toward commercialization. Cerny owns the funded company strategy, while Pastula is the technical buyer for simulation, requirements, configuration, and prototype-validation systems."
        ),
    },
]


def main() -> None:
    load_dotenv(".env")
    database = Database()
    database.initialize()

    for item in ITEMS:
        company = database.save_company_enrichment(
            item["name"],
            item["domain"],
            linkedin_url=item["linkedin_url"],
            sector=item["sector"],
            headquarters_location=item["location"],
            contacts=item["contacts"],
            enrichment_source="same_day_keyword_enrichment",
            mark_enriched_at=NOW,
        )
        if company is None:
            raise RuntimeError(f"Company not found: {item['name']}")

        database.save_enrichment_log(
            EnrichmentLogEntry(
                company_name=item["name"],
                company_domain=item["domain"],
                stage="same_day_keyword_enrichment",
                provider="in_app_browser_official_and_public_profiles",
                status="success",
                message=item["evidence"],
                payload={
                    "contacts_saved": len(item["contacts"]),
                    "verified_software_intent": False,
                },
            )
        )
        print(f"{item['name']}: contacts={len(item['contacts'])}")


if __name__ == "__main__":
    main()
