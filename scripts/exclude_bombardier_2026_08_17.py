from __future__ import annotations

from datetime import datetime, timezone

from dotenv import load_dotenv
from sqlalchemy import text

from db.database import Database


load_dotenv(".env")
database = Database()
database.initialize()
now = datetime.now(timezone.utc)

with database.engine.begin() as connection:
    disposition = connection.execute(
        text(
            """
            UPDATE keyword_company_results
            SET qualification_status = 'disqualified',
                qualified_at = :now
            WHERE keyword_id = 12
              AND company_id = 175
            """
        ),
        {"now": now},
    )
    if disposition.rowcount != 1:
        raise RuntimeError(f"Expected one Bombardier keyword row, updated {disposition.rowcount}")

    connection.execute(
        text(
            """
            UPDATE keywords
            SET last_result_count = 1,
                updated_at = :now
            WHERE id = 12
            """
        ),
        {"now": now},
    )

print("bombardier_keyword_status=disqualified")
