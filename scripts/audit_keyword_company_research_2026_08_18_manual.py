from __future__ import annotations

import json
import re

from dotenv import load_dotenv
from sqlalchemy import func, select

from db.database import (
    CompanyRecord,
    Database,
    KeywordCompanyResultRecord,
    SignalRecord,
)


EXPECTED_SEARCH_COUNTS = {
    1: 39,
    2: 38,
    3: 38,
    4: 34,
    5: 15,
    7: 8,
    8: 8,
    9: 6,
    10: 6,
    11: 6,
    12: 6,
    13: 6,
    14: 1,
    15: 1,
}

CANDIDATE_DOMAINS = {
    "velocitymachining.ca",
    "forcen.tech",
    "northvectordynamics.com",
    "enedym.com",
}


def normalized_identity(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", value.lower())


def main() -> None:
    load_dotenv(".env")
    database = Database()
    database.initialize()
    keywords = database.list_keywords()
    actual_counts = {row.id: row.search_count for row in keywords}
    if actual_counts != EXPECTED_SEARCH_COUNTS:
        raise RuntimeError(f"Unexpected keyword counts: {actual_counts}")
    if any(row.last_error for row in keywords):
        raise RuntimeError("At least one keyword has a search error")

    with database.session() as session:
        duplicate_domains = session.execute(
            select(func.lower(CompanyRecord.company_domain), func.count(CompanyRecord.id))
            .where(CompanyRecord.company_domain.is_not(None))
            .group_by(func.lower(CompanyRecord.company_domain))
            .having(func.count(CompanyRecord.id) > 1)
        ).all()
        duplicate_sources = session.execute(
            select(SignalRecord.source_url, func.count(SignalRecord.id))
            .group_by(SignalRecord.source_url)
            .having(func.count(SignalRecord.id) > 1)
        ).all()
        duplicate_keyword_companies = session.execute(
            select(
                KeywordCompanyResultRecord.keyword_id,
                KeywordCompanyResultRecord.company_id,
                func.count(KeywordCompanyResultRecord.id),
            )
            .group_by(
                KeywordCompanyResultRecord.keyword_id,
                KeywordCompanyResultRecord.company_id,
            )
            .having(func.count(KeywordCompanyResultRecord.id) > 1)
        ).all()
        companies = session.scalars(select(CompanyRecord)).all()
        signals = session.scalars(
            select(SignalRecord).where(SignalRecord.company_domain.in_(CANDIDATE_DOMAINS))
        ).all()
        results = session.scalars(
            select(KeywordCompanyResultRecord).where(
                KeywordCompanyResultRecord.company_id.in_(
                    select(CompanyRecord.id).where(CompanyRecord.company_domain.in_(CANDIDATE_DOMAINS))
                )
            )
        ).all()

    identity_groups: dict[str, list[dict[str, object]]] = {}
    for company in companies:
        identity_groups.setdefault(normalized_identity(company.company_name), []).append(
            {"id": company.id, "name": company.company_name, "domain": company.company_domain}
        )
    duplicate_identities = {
        key: rows
        for key, rows in identity_groups.items()
        if len(rows) > 1 and len({row["domain"] for row in rows}) > 1
    }
    candidate_companies = [
        {
            "id": company.id,
            "name": company.company_name,
            "domain": company.company_domain,
            "signal_count": company.signal_count,
            "total_score": company.total_score,
        }
        for company in companies
        if company.company_domain in CANDIDATE_DOMAINS
    ]
    candidate_results = [
        {
            "keyword_id": row.keyword_id,
            "company_id": row.company_id,
            "status": row.qualification_status,
            "opportunity_score": row.opportunity_score,
            "source_url": row.source_url,
        }
        for row in results
        if row.keyword_id in {2, 10, 14, 15}
    ]
    candidate_signals = [
        {"id": row.id, "domain": row.company_domain, "source_url": row.source_url}
        for row in signals
    ]

    if duplicate_domains or duplicate_sources or duplicate_keyword_companies:
        raise RuntimeError("Database uniqueness audit failed")

    eligible_ids = {
        row.company_id
        for row in database.list_keyword_companies(limit=5000)
        if row.qualification_status in {"qualified", "watchlist"}
    }
    print(json.dumps({
        "keyword_search_counts": actual_counts,
        "last_result_counts": {row.id: row.last_result_count for row in keywords},
        "duplicate_domains": duplicate_domains,
        "duplicate_normalized_identities": duplicate_identities,
        "duplicate_source_urls": duplicate_sources,
        "duplicate_keyword_company_pairs": duplicate_keyword_companies,
        "candidate_companies": candidate_companies,
        "candidate_results": candidate_results,
        "candidate_signals": candidate_signals,
        "eligible_company_count": len(eligible_ids),
    }, indent=2, default=str))


if __name__ == "__main__":
    main()
