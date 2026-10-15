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


SOURCE_URL = (
    "https://www.reuters.com/business/stellantis-signs-roshel-memorandum-"
    "potential-factory-sale-bloomberg-news-reports-2026-09-11/"
)


def main() -> None:
    load_dotenv(REPO_ROOT / ".env")
    database = Database(os.environ["DATABASE_URL"])
    database.initialize()
    with database.session() as session:
        duplicate_domains = session.execute(
            select(func.lower(CompanyRecord.company_domain), func.count())
            .where(CompanyRecord.company_domain.is_not(None))
            .group_by(func.lower(CompanyRecord.company_domain))
            .having(func.count() > 1)
        ).all()
        duplicate_sources = session.execute(
            select(SignalRecord.source_url, func.count())
            .group_by(SignalRecord.source_url)
            .having(func.count() > 1)
        ).all()
        duplicate_pairs = session.execute(
            select(
                KeywordCompanyResultRecord.keyword_id,
                KeywordCompanyResultRecord.company_id,
                func.count(),
            )
            .group_by(
                KeywordCompanyResultRecord.keyword_id,
                KeywordCompanyResultRecord.company_id,
            )
            .having(func.count() > 1)
        ).all()
        eligible = session.scalar(
            select(func.count(func.distinct(KeywordCompanyResultRecord.company_id))).where(
                KeywordCompanyResultRecord.qualification_status.in_(("qualified", "watchlist"))
            )
        )
        source_count = session.scalar(
            select(func.count()).select_from(SignalRecord).where(SignalRecord.source_url == SOURCE_URL)
        )
        roshel = session.scalar(
            select(CompanyRecord).where(CompanyRecord.company_domain == "roshel.com")
        )
        links = session.scalars(
            select(KeywordCompanyResultRecord)
            .where(KeywordCompanyResultRecord.company_id == roshel.id)
            .order_by(KeywordCompanyResultRecord.keyword_id)
        ).all()

    print(
        json.dumps(
            {
                "eligible_company_ids": eligible,
                "duplicate_domains": duplicate_domains,
                "duplicate_source_urls": duplicate_sources,
                "duplicate_keyword_company_pairs": duplicate_pairs,
                "reuters_source_count": source_count,
                "roshel": {
                    "company_id": roshel.id,
                    "company_name": roshel.company_name,
                    "company_domain": roshel.company_domain,
                    "company_url": roshel.company_url,
                    "signal_count": roshel.signal_count,
                    "total_score": roshel.total_score,
                    "keyword_links": [
                        {
                            "keyword_id": row.keyword_id,
                            "status": row.qualification_status,
                            "opportunity_score": row.opportunity_score,
                            "source_url": row.source_url,
                        }
                        for row in links
                    ],
                },
            },
            indent=2,
            default=str,
        )
    )


if __name__ == "__main__":
    main()
