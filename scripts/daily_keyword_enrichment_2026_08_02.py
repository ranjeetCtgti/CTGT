from __future__ import annotations

from datetime import datetime, timezone

from dotenv import load_dotenv

from db.database import Database, EnrichmentLogEntry
from models.schema import ExtractedSignal, LeadContact


NOW = datetime.now(timezone.utc)


def contact(name: str, title: str, linkedin_url: str, stage: str) -> LeadContact:
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


ITEMS = [
    {
        "name": "GlüxKind Technologies",
        "domain": "gluxkind.com",
        "company_url": "https://gluxkind.com/",
        "linkedin_url": "https://ca.linkedin.com/company/gluxkind",
        "location": "Vancouver, British Columbia, Canada",
        "sector": "AI-powered family robotics and adaptive-mobility products",
        "source_url": "https://ca.linkedin.com/company/gluxkind",
        "source_title": "GlüxKind | LinkedIn",
        "contacts": [
            contact(
                "Kevin Huang",
                "Co-founder and Chief Executive Officer",
                "https://ca.linkedin.com/in/kevinzwhuang",
                "linkedin_connector_and_public_profile_verified",
            ),
            contact(
                "Anne Hunger",
                "Co-founder and Chief Product Officer",
                "https://ca.linkedin.com/in/anne-hunger/en",
                "public_linkedin_profile_verified",
            ),
        ],
        "reason": (
            "Current public LinkedIn evidence identifies Kevin Huang as GlüxKind's co-founder "
            "and CEO and Anne Hunger as co-founder and chief product officer. Their ownership of "
            "commercial strategy and product development makes them the relevant contacts for "
            "discussing configuration, safety, embedded controls, verification, and production "
            "readiness for the company's AI-powered adaptive mobility products. No named PLM, CAD, "
            "MES, or competing engineering platform was found."
        ),
    },
    {
        "name": "Obruta Space Solutions",
        "domain": "obruta.com",
        "company_url": "https://www.obruta.com/",
        "linkedin_url": "https://ca.linkedin.com/company/obruta",
        "location": "Ottawa, Ontario, Canada",
        "sector": "Autonomous spacecraft rendezvous, docking, and on-orbit servicing systems",
        "source_url": "https://www.obruta.com/about",
        "source_title": "About | Obruta",
        "contacts": [
            contact(
                "Kevin Stadnyk",
                "Co-founder and Chief Executive Officer",
                "https://ca.linkedin.com/in/kevinstadnyk",
                "official_team_page_and_linkedin_connector_verified",
            ),
            contact(
                "Kirk Hovell",
                "Co-founder and Chief Technology Officer",
                "https://ca.linkedin.com/in/kirkhovell",
                "official_team_page_and_linkedin_connector_verified",
            ),
        ],
        "reason": (
            "Obruta's official team page identifies Kevin Stadnyk as co-founder and CEO and "
            "Dr. Kirk Hovell as co-founder and CTO; both identities and current employer links "
            "were validated with LinkedIn. They are the appropriate executive and technical "
            "contacts for spacecraft docking, guidance/navigation/control, AI vision, test "
            "evidence, and configuration-management discussions. No named PLM or engineering "
            "platform was found."
        ),
    },
    {
        "name": "NIO Robotics",
        "domain": None,
        "company_url": None,
        "linkedin_url": None,
        "location": "Canada",
        "sector": "AI-powered polymorphic robots for industrial inspection and maintenance",
        "source_url": "https://ca.linkedin.com/in/ali-chokre",
        "source_title": "Ali Chokre - Founder & CEO of NIO Robotics Inc. | LinkedIn",
        "contacts": [
            contact(
                "Ali Chokre",
                "Founder and Chief Executive Officer",
                "https://ca.linkedin.com/in/ali-chokre",
                "linkedin_connector_and_public_profile_verified",
            )
        ],
        "reason": (
            "Current public LinkedIn evidence identifies Ali Chokre as founder and CEO of NIO "
            "Robotics, and Dealroom describes the company as developing AI-powered polymorphic "
            "robots for industrial inspection and maintenance. Chokre is the relevant commercial "
            "and product-ownership contact for discussing multidisciplinary robot configuration, "
            "field reliability, and verification. An authoritative canonical company domain and "
            "named PLM or MES platform were not found."
        ),
    },
    {
        "name": "Optimotive",
        "domain": "optimotive.io",
        "company_url": "https://www.optimotive.io/",
        "linkedin_url": "https://www.linkedin.com/company/optimotive-technologies",
        "location": "Windsor, Ontario, Canada",
        "sector": "Autonomous robots for construction and other extreme environments",
        "source_url": "https://www.linkedin.com/company/optimotive-technologies",
        "source_title": "Optimotive | LinkedIn",
        "contacts": [
            contact(
                "Scott M. Fairley",
                "Founder and Chief Executive Officer",
                "https://ca.linkedin.com/in/scott-m-fairley-92940011b",
                "linkedin_connector_and_public_profile_verified",
            ),
            contact(
                "Stephen Vaidyan",
                "Head of Production and Robot Operations",
                "https://ca.linkedin.com/in/stephenvaidyan",
                "linkedin_connector_and_public_profile_verified",
            ),
        ],
        "reason": (
            "Optimotive's current public LinkedIn presence verifies Scott M. Fairley as founder "
            "and CEO and Stephen Vaidyan as head of production and robot operations. Their roles "
            "directly cover product strategy and the manufacturing/field-operation handoff for "
            "autonomous robots used in extreme environments, making them relevant for digital-thread, "
            "change-control, build genealogy, and reliability discussions. No named PLM or MES "
            "platform was found."
        ),
    },
    {
        "name": "Tactile Robotics",
        "domain": None,
        "company_url": None,
        "linkedin_url": "https://ca.linkedin.com/company/tactilerobotics",
        "location": "Canada",
        "sector": "Robotics, AI, tactile sensing, and tele-enabled healthcare platforms",
        "source_url": "https://ca.linkedin.com/company/tactilerobotics",
        "source_title": "Tactile Robotics | LinkedIn",
        "contacts": [
            contact(
                "Yaser Maddahi",
                "Founder and Chief Executive Officer",
                "https://ca.linkedin.com/in/ymaddahi",
                "public_linkedin_profile_verified",
            ),
            contact(
                "Ali Maddahi",
                "Chief Technology Officer",
                "https://ca.linkedin.com/in/amaddahi",
                "linkedin_connector_and_public_profile_verified",
            ),
        ],
        "reason": (
            "Tactile Robotics' current public LinkedIn evidence identifies Dr. Yaser Maddahi as "
            "founder and CEO and Ali Maddahi as CTO. These contacts own the business and technical "
            "decisions around robotics, AI, tactile sensing, and tele-enabled healthcare development; "
            "the company also publicly indicated a growth funding round. No named PLM, CAD, MES, or "
            "competing engineering platform was found."
        ),
    },
]


def main() -> None:
    load_dotenv()
    database = Database()
    database.initialize()

    for item in ITEMS:
        signal = ExtractedSignal(
            company_name=item["name"],
            company_domain=item["domain"],
            company_url=item["company_url"],
            linkedin_url=item["linkedin_url"],
            location=item["location"],
            industry=item["sector"],
            company_industry=item["sector"],
            software=[],
            signal_type="news",
            signal_source="linkedin",
            pain_signals=[],
            expansion_signals=[],
            raw_score=65,
            confidence=0.95,
            reason=item["reason"],
            source_url=item["source_url"],
            source_title=item["source_title"],
            detected_at=NOW,
        )
        saved = database.save_signal(signal)
        database.upsert_company(signal)
        company = database.save_company_enrichment(
            item["name"],
            item["domain"],
            linkedin_url=item["linkedin_url"],
            sector=item["sector"],
            headquarters_location=item["location"],
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
                message=(
                    f"Saved {len(item['contacts'])} verified decision-makers; "
                    f"signal_created={saved.created}; no verified PLM/software intent found"
                ),
                payload={
                    "source_url": item["source_url"],
                    "contacts_saved": len(item["contacts"]),
                    "signal_created": saved.created,
                    "verified_software_intent": False,
                },
            )
        )
        print(
            f"{item['name']}: contacts={len(item['contacts'])} "
            f"signal_created={saved.created} enriched=True"
        )


if __name__ == "__main__":
    main()
