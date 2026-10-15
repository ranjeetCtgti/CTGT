from __future__ import annotations

import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import func, select


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from db.database import (
    CompanyRecord,
    Database,
    KeywordCompanyResultRecord,
    SignalRecord,
)


def main() -> None:
    load_dotenv(REPO_ROOT / ".env")
    database = Database(os.environ["DATABASE_URL"])
    database.initialize()
    target_domains = {
        "stanleyboats.ca",
        "avss.co",
        "beonyx.ca",
        "draganfly.com",
        "volatusaerospace.com",
    }
    with database.session() as session:
        target_companies = session.scalars(
            select(CompanyRecord)
            .where(CompanyRecord.company_domain.in_(target_domains))
            .order_by(CompanyRecord.id)
        ).all()
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
        duplicate_keyword_pairs = session.execute(
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
        target_links = session.execute(
            select(
                KeywordCompanyResultRecord.keyword_id,
                KeywordCompanyResultRecord.company_id,
                CompanyRecord.company_name,
                KeywordCompanyResultRecord.qualification_status,
                KeywordCompanyResultRecord.opportunity_score,
                KeywordCompanyResultRecord.source_url,
            )
            .join(
                CompanyRecord,
                CompanyRecord.id == KeywordCompanyResultRecord.company_id,
            )
            .where(
                KeywordCompanyResultRecord.company_id.in_(
                    [company.id for company in target_companies]
                )
            )
            .order_by(
                KeywordCompanyResultRecord.keyword_id,
                KeywordCompanyResultRecord.company_id,
            )
        ).all()
        eligible_ids = session.scalars(
            select(KeywordCompanyResultRecord.company_id)
            .where(
                KeywordCompanyResultRecord.qualification_status.in_(
                    ("qualified", "watchlist")
                )
            )
            .distinct()
        ).all()

    print(
        json.dumps(
            {
                "target_companies": [
                    {
                        "id": row.id,
                        "company_name": row.company_name,
                        "company_domain": row.company_domain,
                        "signal_count": row.signal_count,
                        "total_score": row.total_score,
                    }
                    for row in target_companies
                ],
                "target_keyword_links": [
                    {
                        "keyword_id": row[0],
                        "company_id": row[1],
                        "company_name": row[2],
                        "status": row[3],
                        "opportunity_score": row[4],
                    }
                    for row in target_links
                ],
                "eligible_company_ids": len(set(eligible_ids)),
                "duplicate_domain_count": len(duplicate_domains),
                "duplicate_source_url_count": len(duplicate_sources),
                "duplicate_keyword_company_pair_count": len(duplicate_keyword_pairs),
            },
            indent=2,
            default=str,
        )
    )


if __name__ == "__main__":
    main()
