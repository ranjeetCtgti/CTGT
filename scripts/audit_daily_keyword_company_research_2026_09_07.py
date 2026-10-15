from __future__ import annotations

import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import text


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from db.database import Database


def main() -> None:
    load_dotenv(REPO_ROOT / ".env")
    database = Database(os.environ["DATABASE_URL"])
    database.initialize()
    queries = {
        "duplicate_domains": """
            SELECT count(*) FROM (
                SELECT lower(trim(company_domain))
                FROM companies
                WHERE nullif(trim(company_domain), '') IS NOT NULL
                GROUP BY 1 HAVING count(*) > 1
            ) duplicates
        """,
        "duplicate_normalized_names": """
            SELECT count(*) FROM (
                SELECT lower(regexp_replace(trim(company_name), '[^a-z0-9]+', '', 'g'))
                FROM companies
                GROUP BY 1 HAVING count(*) > 1
            ) duplicates
        """,
        "duplicate_source_urls": """
            SELECT count(*) FROM (
                SELECT source_url FROM signals
                GROUP BY 1 HAVING count(*) > 1
            ) duplicates
        """,
        "duplicate_keyword_company_pairs": """
            SELECT count(*) FROM (
                SELECT keyword_id, company_id FROM keyword_company_results
                GROUP BY 1, 2 HAVING count(*) > 1
            ) duplicates
        """,
    }
    with database.session() as session:
        print({name: session.execute(text(sql)).scalar_one() for name, sql in queries.items()})


if __name__ == "__main__":
    main()
