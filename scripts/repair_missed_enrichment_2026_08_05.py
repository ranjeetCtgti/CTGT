from __future__ import annotations

from datetime import datetime, timezone

from dotenv import load_dotenv

from db.database import Database, EnrichmentLogEntry
from models.schema import LeadContact


NOW = datetime.now(timezone.utc)


def contact(name: str, title: str, linkedin_url: str) -> LeadContact:
    parts = name.split()
    return LeadContact(
        full_name=name,
        first_name=parts[0],
        last_name=parts[-1],
        title=title,
        linkedin_url=linkedin_url,
        source_provider="linkedin",
        source_stage="linkedin_connector_and_public_profile_verified",
    )


ITEMS = [
    {
        "name": "Calogy Solutions",
        "domain": "calogysolutions.com",
        "linkedin_url": "https://www.linkedin.com/company/calogysolutions/",
        "sector": "Battery systems and thermal-management hardware for aerospace and e-mobility",
        "location": "Sherbrooke, Quebec, Canada",
        "contacts": [
            contact(
                "Mahmood Shirazy",
                "Co-Founder and Chief Executive Officer",
                "https://ca.linkedin.com/in/mahmood-shirazy-4477998",
            )
        ],
        "evidence": (
            "LinkedIn verifies Mahmood Shirazy as Calogy Solutions' co-founder and CEO. "
            "The August 4, 2026 qualification evidence records a C$1.2 million battery-system "
            "contract for Jaunt's autonomous hybrid-electric drone, with testing planned before "
            "year-end 2026 and joint manufacturing targeted for 2027. This makes Shirazy the "
            "appropriate executive contact for battery configuration, test traceability, "
            "supplier coordination, and manufacturing-ramp discussions."
        ),
    },
    {
        "name": "Jaunt Air Mobility Canada",
        "domain": "jauntairmobility.com",
        "linkedin_url": "https://ca.linkedin.com/company/jauntair",
        "sector": "Autonomous hybrid-electric aircraft and dual-use drones",
        "location": "Montreal, Quebec, Canada",
        "contacts": [
            contact(
                "Eric Cote",
                "President, Jaunt Air Mobility Canada",
                "https://ca.linkedin.com/in/ericcote2020",
            ),
            contact(
                "Martin Peryea",
                "Chief Executive Officer, Jaunt Air Mobility",
                "https://www.linkedin.com/in/martin-peryea-57058880",
            ),
        ],
        "evidence": (
            "Jaunt's official leadership page and LinkedIn identify Eric Cote as president of "
            "Jaunt Air Mobility Canada, while LinkedIn identifies Martin Peryea as Jaunt's CEO. "
            "The August 4, 2026 qualification evidence records a C$1.2 million Calogy battery-system "
            "contract supporting drone testing before year-end 2026 and a 2027 market-entry target. "
            "Cote is the primary Canadian design/manufacturing contact; Peryea owns the wider "
            "aircraft-program and technology decision path."
        ),
    },
]


def main() -> None:
    load_dotenv()
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
            enrichment_source="scheduled_keyword_enrichment_repair",
            mark_enriched_at=NOW,
        )
        if company is None:
            raise RuntimeError(f"Company not found: {item['name']}")

        database.save_enrichment_log(
            EnrichmentLogEntry(
                company_name=item["name"],
                company_domain=item["domain"],
                stage="scheduled_keyword_enrichment_repair",
                provider="in_app_browser_linkedin",
                status="success",
                message=item["evidence"],
                payload={
                    "contacts_saved": len(item["contacts"]),
                    "qualification_reassessment_triggered": True,
                    "verified_software_intent": False,
                    "source_urls": [
                        contact.linkedin_url for contact in item["contacts"]
                    ],
                },
            )
        )
        print(f"{item['name']}: contacts={len(item['contacts'])} enriched_at={NOW.isoformat()}")


if __name__ == "__main__":
    main()
