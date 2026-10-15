from __future__ import annotations

import json

from dotenv import load_dotenv
from sqlalchemy import text

from db.database import Database


load_dotenv()
database = Database()
database.initialize()

with database.engine.connect() as connection:
    keywords = [
        dict(row._mapping)
        for row in connection.execute(
            text(
                """
                SELECT id, keyword, search_count, last_result_count, last_error,
                       last_searched_at
                FROM keywords
                ORDER BY id
                """
            )
        )
    ]
    touched = [
        dict(row._mapping)
        for row in connection.execute(
            text(
                """
                SELECT c.id AS company_id, c.company_name, c.company_domain,
                       k.id AS keyword_id,
                       kcr.qualification_status, kcr.opportunity_score,
                       kcr.last_seen_at, kcr.times_seen
                FROM keyword_company_results kcr
                JOIN companies c ON c.id = kcr.company_id
                JOIN keywords k ON k.id = kcr.keyword_id
                WHERE c.company_domain IN ('roshel.com', 'bombardier.com', 'celestica.com')
                   OR (
                       k.id IN (5, 8, 9, 10, 13)
                       AND kcr.last_seen_at >= date_trunc('day', now())
                   )
                ORDER BY k.id, c.id
                """
            )
        )
    ]
    eligible_unique = connection.execute(
        text(
            """
            SELECT count(DISTINCT company_id)
            FROM keyword_company_results
            WHERE qualification_status IN ('qualified', 'watchlist')
            """
        )
    ).scalar_one()
    new_signals = [
        dict(row._mapping)
        for row in connection.execute(
            text(
                """
                SELECT s.id, s.company_name, s.source_url, s.detected_at
                FROM signals s
                WHERE s.company_domain IN ('roshel.com', 'bombardier.com', 'celestica.com')
                ORDER BY s.company_name, s.detected_at DESC
                """
            )
        )
    ]

print(
    json.dumps(
        {
            "keywords": keywords,
            "touched": touched,
            "eligible_unique": eligible_unique,
            "new_signals": new_signals,
        },
        default=str,
        indent=2,
    )
)
