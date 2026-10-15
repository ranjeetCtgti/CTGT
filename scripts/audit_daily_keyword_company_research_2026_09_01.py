from __future__ import annotations

import json
import os
import re

from dotenv import load_dotenv
from sqlalchemy import func, select

from db.database import (
    CompanyRecord,
    Database,
    KeywordCompanyResultRecord,
    SignalRecord,
)


def normalized_name(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", value.lower())


def duplicate_values(values: list[str]) -> list[str]:
    seen: set[str] = set()
    duplicates: set[str] = set()
    for value in values:
        if value in seen:
            duplicates.add(value)
        seen.add(value)
    return sorted(duplicates)


def main() -> None:
    load_dotenv(".env")
    database = Database(os.environ["DATABASE_URL"])
    database.initialize()
    with database.session() as session:
        companies = session.scalars(select(CompanyRecord)).all()
        signals = session.scalars(select(SignalRecord)).all()
        links = session.scalars(select(KeywordCompanyResultRecord)).all()
        targets = session.scalars(
            select(CompanyRecord).where(CompanyRecord.id.in_([2064, 2221]))
        ).all()
        target_links = session.scalars(
            select(KeywordCompanyResultRecord).where(
                KeywordCompanyResultRecord.company_id.in_([2064, 2221])
            )
        ).all()

    keyword_rows = database.list_keywords()
    eligible_ids = {
        row.company_id
        for row in database.list_keyword_companies(limit=5000)
        if row.qualification_status in {"qualified", "watchlist"}
    }
    domains = [company.company_domain for company in companies if company.company_domain]
    names = [normalized_name(company.company_name) for company in companies]
    source_urls = [signal.source_url for signal in signals]
    pairs = [f"{row.keyword_id}:{row.company_id}" for row in links]

    print(
        json.dumps(
            {
                "keywords": [
                    {
                        "id": row.id,
                        "search_count": row.search_count,
                        "last_result_count": row.last_result_count,
                        "last_error": row.last_error,
                    }
                    for row in keyword_rows
                ],
                "targets": [
                    {
                        "id": row.id,
                        "name": row.company_name,
                        "domain": row.company_domain,
                        "signal_count": row.signal_count,
                        "total_score": row.total_score,
                    }
                    for row in sorted(targets, key=lambda item: item.id)
                ],
                "target_links": [
                    {
                        "keyword_id": row.keyword_id,
                        "company_id": row.company_id,
                        "status": row.qualification_status,
                        "opportunity_score": row.opportunity_score,
                        "source_url": row.source_url,
                    }
                    for row in sorted(target_links, key=lambda item: (item.company_id, item.keyword_id))
                ],
                "eligible_company_ids": len(eligible_ids),
                "keyword_company_rows": len(links),
                "duplicate_domains": duplicate_values(domains),
                "duplicate_normalized_names": duplicate_values(names),
                "duplicate_signal_source_urls": duplicate_values(source_urls),
                "duplicate_keyword_company_pairs": duplicate_values(pairs),
            },
            indent=2,
            default=str,
        )
    )


if __name__ == "__main__":
    main()
