from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import text


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from db.database import Database, KeywordRecord


EXPECTED_SEARCH_COUNTS = {
    1: 50, 2: 49, 3: 49, 4: 45, 5: 26, 7: 19, 8: 19, 9: 17,
    10: 17, 11: 17, 12: 17, 13: 17, 14: 12, 15: 12, 16: 6,
}
RESULT_COUNTS = {
    1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 7: 2, 8: 2, 9: 3,
    10: 0, 11: 0, 12: 0, 13: 2, 14: 2, 15: 0, 16: 0,
}


def main() -> None:
    load_dotenv(REPO_ROOT / ".env")
    database = Database(os.environ["DATABASE_URL"])
    database.initialize()
    now = datetime.now(timezone.utc)
    with database.session() as session, session.begin():
        keywords = {row.id: row for row in session.query(KeywordRecord).all()}
        actual_counts = {
            keyword_id: keywords[keyword_id].search_count
            for keyword_id in EXPECTED_SEARCH_COUNTS
        }
        if actual_counts != EXPECTED_SEARCH_COUNTS:
            raise RuntimeError(
                f"Refusing audit finalization because search counts changed: {actual_counts}"
            )
        for keyword_id, result_count in RESULT_COUNTS.items():
            keywords[keyword_id].last_result_count = result_count
            keywords[keyword_id].last_error = None
            keywords[keyword_id].updated_at = now

    audit_queries = {
        "duplicate_domains": """
            SELECT count(*) FROM (
                SELECT lower(trim(company_domain))
                FROM companies
                WHERE nullif(trim(company_domain), '') IS NOT NULL
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
        audit = {
            name: session.execute(text(sql)).scalar_one()
            for name, sql in audit_queries.items()
        }
    final_keywords = {
        row.id: {
            "search_count": row.search_count,
            "last_result_count": row.last_result_count,
            "last_error": row.last_error,
        }
        for row in database.list_keywords()
    }
    print(json.dumps({"finalized_at": now.isoformat(), "audit": audit, "keywords": final_keywords}, indent=2))


if __name__ == "__main__":
    main()
