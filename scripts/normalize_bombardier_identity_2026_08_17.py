from __future__ import annotations

from datetime import datetime, timezone

from dotenv import load_dotenv
from sqlalchemy import text

from db.database import Database


load_dotenv(".env")
database = Database()
database.initialize()

with database.engine.begin() as connection:
    result = connection.execute(
        text(
            """
            UPDATE companies
            SET company_url = :company_url,
                linkedin_url = :linkedin_url,
                location = :location,
                headquarters_location = :location,
                industry = :industry,
                company_industry = :industry,
                sector = :industry,
                last_updated = :updated_at
            WHERE id = 175
              AND company_domain = 'bombardier.com'
            """
        ),
        {
            "company_url": "https://bombardier.com/",
            "linkedin_url": "https://www.linkedin.com/company/bombardier/",
            "location": "Dorval, Quebec, Canada",
            "industry": "Business aircraft design, manufacturing and service",
            "updated_at": datetime.now(timezone.utc),
        },
    )
    if result.rowcount != 1:
        raise RuntimeError(f"Expected one Bombardier row, updated {result.rowcount}")

print("normalized_company_id=175")
