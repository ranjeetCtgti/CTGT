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
        source_stage="linkedin_connector_and_public_source_verified",
    )


ITEMS = [
    {
        "name": "North Vector Dynamics",
        "domain": "northvectordynamics.com",
        "sector": "Hypersonic propulsion and autonomous defence systems",
        "headquarters": "Calgary, Alberta, Canada",
        "contacts": [
            contact(
                "Paul Ziade",
                "Chief Executive Officer",
                "https://ca.linkedin.com/in/paul-ziade",
            )
        ],
        "summary": (
            "CEO Paul Ziade is the primary executive contact for the July 31 strategic "
            "investment and NordSpace technical partnership. The immediate sales conversation "
            "should focus on controlling propulsion configurations, defence requirements, "
            "simulation evidence, and supplier changes while the $4.2-million DND program and "
            "the overlapping hypersonic roadmaps accelerate."
        ),
    },
    {
        "name": "Allied Marine & Industrial",
        "domain": "allmind.com",
        "sector": "Commercial vessel repair, refit, fabrication, and marine industrial services",
        "headquarters": "Port Colborne, Ontario, Canada",
        "contacts": [
            contact(
                "Rob Gair",
                "Vice President Operations and General Manager",
                "https://ca.linkedin.com/in/robgair",
            )
        ],
        "summary": (
            "Rob Gair is the operating executive best positioned to discuss how Allied will "
            "absorb more than $8 million of new infrastructure, machinery, equipment, and skills "
            "investment. The practical pain point is integrating the expanded yard into controlled "
            "vessel work packages, drawings, materials, inspections, welding quality, and repair "
            "genealogy without losing delivery visibility."
        ),
    },
    {
        "name": "Kiwi Charge",
        "domain": "kiwicharge.com",
        "sector": "Autonomous mobile electric-vehicle charging robots",
        "headquarters": "Toronto, Ontario, Canada",
        "contacts": [
            contact(
                "Abdel Ali",
                "Co-founder and Chief Executive Officer",
                "https://ca.linkedin.com/in/abdelali1",
            )
        ],
        "summary": (
            "Co-founder and CEO Abdel Ali is the accountable product and commercialization "
            "decision maker for the $1.7-million GM Canada and Pfaff pilot. The immediate need "
            "is to replace prototype-era change handling with traceable mechanical, electrical, "
            "battery, controls-software, safety, and verification management before unattended "
            "robots operate across customer sites."
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
            sector=item["sector"],
            headquarters_location=item["headquarters"],
            contacts=item["contacts"],
            enrichment_source="scheduled_keyword_enrichment",
            mark_enriched_at=NOW,
        )
        if company is None:
            raise RuntimeError(f"Company disappeared: {item['name']}")
        database.save_enrichment_log(
            EnrichmentLogEntry(
                company_name=item["name"],
                company_domain=item["domain"],
                stage="scheduled_keyword_enrichment",
                provider="in_app_browser_linkedin",
                status="success",
                message=item["summary"],
                payload={
                    "contacts_saved": len(item["contacts"]),
                    "contact_urls": [c.linkedin_url for c in item["contacts"]],
                    "enriched_at": NOW.isoformat(),
                },
            )
        )
        print(f"{item['name']}: contacts={len(item['contacts'])} enriched=True")


if __name__ == "__main__":
    main()
