from __future__ import annotations

from datetime import datetime, timezone

from dotenv import load_dotenv

from db.database import Database, EnrichmentLogEntry
from models.schema import ExtractedSignal, LeadContact


NOW = datetime.now(timezone.utc)


def make_contact(
    name: str,
    title: str,
    linkedin_url: str | None,
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


ITEMS = [
    {
        "name": "Atlas Engineered Products",
        "domain": "atlasengineeredproducts.com",
        "linkedin_url": None,
        "sector": "Engineered wood building-component manufacturing",
        "headquarters": "Nanaimo, British Columbia, Canada",
        "employee_count": None,
        "contacts": [
            make_contact(
                "Hadi Abassi",
                "Founder, President and CEO",
                None,
                "official_company_team_page_verified",
            )
        ],
        "source_url": "https://www.atlasengineeredproducts.com/",
        "source_title": "Atlas Engineered Products",
        "industry": "Engineered wood building-component manufacturing",
        "software": [],
        "pain": [
            "Coordinating engineering and production across an acquisition-led network of component plants"
        ],
        "expansion": [
            "Commissioning its first robotic truss manufacturing facility in Clinton, Ontario"
        ],
        "reason": (
            "Atlas' official site verifies Hadi Abassi as founder, president and CEO and "
            "identifies a multi-location engineered-products business. Together with the "
            "current robotic-plant commissioning evidence already stored, this confirms a "
            "senior owner and a material engineering-to-production scale-up; no named PLM "
            "or MES platform was found."
        ),
        "score": 62,
        "confidence": 0.96,
    },
    {
        "name": "MDS Coating Technologies",
        "domain": "mdscoating.com",
        "linkedin_url": None,
        "sector": "Aerospace protective-coating development and manufacturing",
        "headquarters": "Slemon Park, Prince Edward Island, Canada",
        "employee_count": None,
        "contacts": [
            make_contact(
                "Lee Martin",
                "Advanced Research and Development specialist",
                "https://ca.linkedin.com/in/lee-martin-7258b214",
                "linkedin_connector_and_public_profile_verified",
            )
        ],
        "source_url": "https://www.mdscoating.com/company/",
        "source_title": "About Us | MDS Coating Technologies Corp.",
        "industry": "Aerospace protective-coating development and manufacturing",
        "software": [],
        "pain": [
            "Maintaining aerospace quality, precision, and repeatability across proprietary coating and surface-treatment processes"
        ],
        "expansion": [
            "More than five million aerospace airfoils coated",
            "Commercializing additional protective coating technology through a funded facility expansion",
        ],
        "reason": (
            "MDS Coating's official company page confirms that it designs and manufactures "
            "protective gas-turbine coatings, has coated more than five million airfoils, "
            "and operates under a quality policy focused on safety, precision, and engine "
            "life. This provides strong product, process, and traceability context for its "
            "funded expansion; no named PLM or MES platform was found."
        ),
        "score": 68,
        "confidence": 0.98,
    },
    {
        "name": "Maritime Launch Services",
        "domain": "maritimelaunch.com",
        "linkedin_url": "https://www.linkedin.com/company/maritimelaunch/",
        "sector": "Commercial spaceport development and launch operations",
        "headquarters": "Halifax, Nova Scotia, Canada",
        "employee_count": "2-10",
        "contacts": [
            make_contact(
                "Stephen Matier",
                "President and CEO",
                "https://ca.linkedin.com/in/stephen-matier-502a0924",
                "linkedin_connector_and_company_post_verified",
            )
        ],
        "source_url": "https://www.linkedin.com/company/maritimelaunch/",
        "source_title": "Maritime Launch Services | LinkedIn",
        "industry": "Commercial spaceport development and launch operations",
        "software": [],
        "pain": [
            "Managing a multi-user dual-use launch site across commercial, civil, and defence requirements"
        ],
        "expansion": [
            "Ten-year Isar Aerospace agreement for a dedicated Spectrum launch complex",
            "Construction begins in 2026 with first orbital launches targeted for 2028",
        ],
        "reason": (
            "The live Maritime Launch LinkedIn page identifies Stephen Matier as president "
            "and CEO and confirms the ten-year Isar Aerospace agreement, 2026 construction, "
            "and 2028 first-launch target. The page also describes Spaceport Nova Scotia as "
            "a multi-user civil, commercial, and defence facility, verifying immediate "
            "requirements and configuration complexity; no named PLM platform was found."
        ),
        "score": 72,
        "confidence": 0.99,
    },
    {
        "name": "Ocean Pacific Marine",
        "domain": "oceanpacificmarine.com",
        "linkedin_url": (
            "https://ca.linkedin.com/company/ocean-pacific-marine-store-boatyard"
        ),
        "sector": "Vessel repair, refit, life extension, and small-vessel construction",
        "headquarters": "Campbell River, British Columbia, Canada",
        "employee_count": None,
        "contacts": [
            make_contact(
                "Govinda Advani",
                "Chief Executive Officer",
                "https://ca.linkedin.com/in/govindaadvani",
                "linkedin_connector_and_company_post_verified",
            ),
            make_contact(
                "Graham George",
                "Program Manager and Senior Management Team member",
                "https://ca.linkedin.com/in/grahamgeorge1",
                "linkedin_connector_and_company_post_verified",
            ),
        ],
        "source_url": (
            "https://ca.linkedin.com/company/ocean-pacific-marine-store-boatyard"
        ),
        "source_title": "Ocean Pacific Marine Store & Boatyard | LinkedIn",
        "industry": "Vessel repair, refit, life extension, and small-vessel construction",
        "software": [],
        "pain": [
            "Coordinating complex vessel refit, life-extension, and federal-program work while the business scales"
        ],
        "expansion": [
            "New CEO following acquisition by Regenerative Capital Group",
            "New program manager added to the senior management team during significant growth",
            "Current RCMP coastal-patrol-vessel contract",
        ],
        "reason": (
            "Ocean Pacific's live LinkedIn page verifies Govinda Advani as CEO and Graham "
            "George as program manager and a member of the senior management team. It states "
            "that the Campbell River operation is experiencing significant growth and "
            "performs commercial refit, vessel life-extension, and federal Coast Guard and "
            "defence work, providing direct management and operational-complexity evidence; "
            "no named PLM system was found."
        ),
        "score": 70,
        "confidence": 0.99,
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
            company_url=f"https://{item['domain']}/",
            linkedin_url=item["linkedin_url"],
            location=item["headquarters"],
            industry=item["industry"],
            company_industry=item["industry"],
            software=item["software"],
            signal_type="news",
            signal_source="linkedin" if "linkedin.com" in item["source_url"] else "news",
            pain_signals=item["pain"],
            expansion_signals=item["expansion"],
            raw_score=item["score"],
            confidence=item["confidence"],
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
            employee_count=item["employee_count"],
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
                message=(
                    f"Rerun saved {len(item['contacts'])} verified contacts; "
                    f"signal_created={saved.created}"
                ),
                payload={
                    "source_url": item["source_url"],
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
