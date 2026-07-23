from __future__ import annotations

import argparse
from dataclasses import dataclass

from dotenv import load_dotenv
from sqlalchemy import func, or_, select

from db.database import (
    CompanyRecord,
    Database,
    EnrichmentLogRecord,
    LeadContactRecord,
    SignalRecord,
)
from industry_filter import matching_excluded_industry


EXCLUDED_NAME_TERMS = (
    "consulting",
    "consultancy",
    "staffing",
    "recruiting",
    "recruitment",
    "talent solutions",
    "professional services",
    "managed services",
    "system integrator",
    "systems integrator",
)

# Manual review of the current cleanup set confirmed these are target-sector
# manufacturers whose enrichment metadata was attached to the wrong entity or
# source website. Never delete them solely from that conflicting sector value.
REVIEWED_TARGET_COMPANY_NAMES = {
    "enercon",
    "hager & meisinger gmbh",
    "mermec deutschland gmbh",
    "minth north america, inc.",
    "pressure dynamics international",
    "tatra trucks",
    "tesla",
    "think surgical",
}


@dataclass(frozen=True, slots=True)
class CleanupCandidate:
    company_id: int
    company_name: str
    company_domain: str | None
    industry: str | None
    sector: str | None
    reason: str


def find_cleanup_candidates(database: Database) -> list[CleanupCandidate]:
    with database.session() as session:
        records = session.scalars(select(CompanyRecord).order_by(CompanyRecord.id)).all()

    candidates: list[CleanupCandidate] = []
    for record in records:
        normalized_name = " ".join(record.company_name.casefold().split())
        if normalized_name in REVIEWED_TARGET_COMPANY_NAMES:
            continue

        excluded_sector = matching_excluded_industry(record.sector)
        excluded_name_term = next(
            (term for term in EXCLUDED_NAME_TERMS if term in normalized_name),
            None,
        )
        if not excluded_sector and not excluded_name_term:
            continue

        reason = (
            f"excluded sector: {record.sector} (matched {excluded_sector})"
            if excluded_sector
            else f"excluded company-name term: {excluded_name_term}"
        )
        candidates.append(
            CleanupCandidate(
                company_id=record.id,
                company_name=record.company_name,
                company_domain=record.company_domain,
                industry=record.industry,
                sector=record.sector,
                reason=reason,
            )
        )
    return candidates


def _company_signal_condition(candidate: CleanupCandidate):
    # Company domains can be polluted with shared job-board or publisher hosts.
    # The extracted company name is the safe key for destructive cleanup.
    return func.lower(SignalRecord.company_name) == candidate.company_name.casefold()


def related_counts(database: Database, candidates: list[CleanupCandidate]) -> dict[str, int]:
    company_ids = [candidate.company_id for candidate in candidates]
    if not company_ids:
        return {"companies": 0, "signals": 0, "contacts": 0, "enrichment_logs": 0}

    signal_conditions = [_company_signal_condition(candidate) for candidate in candidates]
    with database.session() as session:
        return {
            "companies": len(candidates),
            "signals": int(
                session.scalar(
                    select(func.count()).select_from(SignalRecord).where(or_(*signal_conditions))
                )
                or 0
            ),
            "contacts": int(
                session.scalar(
                    select(func.count())
                    .select_from(LeadContactRecord)
                    .where(LeadContactRecord.company_id.in_(company_ids))
                )
                or 0
            ),
            "enrichment_logs": int(
                session.scalar(
                    select(func.count())
                    .select_from(EnrichmentLogRecord)
                    .where(EnrichmentLogRecord.company_id.in_(company_ids))
                )
                or 0
            ),
        }


def delete_candidates(database: Database, candidates: list[CleanupCandidate]) -> dict[str, int]:
    company_ids = [candidate.company_id for candidate in candidates]
    if not company_ids:
        return {"companies": 0, "signals": 0, "contacts": 0, "enrichment_logs": 0}

    signal_conditions = [_company_signal_condition(candidate) for candidate in candidates]
    with database.session() as session:
        counts = {
            "signals": session.query(SignalRecord)
            .filter(or_(*signal_conditions))
            .delete(synchronize_session=False),
            "contacts": session.query(LeadContactRecord)
            .filter(LeadContactRecord.company_id.in_(company_ids))
            .delete(synchronize_session=False),
            "enrichment_logs": session.query(EnrichmentLogRecord)
            .filter(EnrichmentLogRecord.company_id.in_(company_ids))
            .delete(synchronize_session=False),
            "companies": session.query(CompanyRecord)
            .filter(CompanyRecord.id.in_(company_ids))
            .delete(synchronize_session=False),
        }
        session.commit()
    return {key: int(value) for key, value in counts.items()}


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Audit or remove companies matching configured excluded industries."
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Commit deletion. Without this option, only print the audit.",
    )
    args = parser.parse_args()

    load_dotenv()
    database = Database()
    candidates = find_cleanup_candidates(database)
    counts = related_counts(database, candidates)

    print(
        "cleanup candidates: "
        + ", ".join(f"{key}={value}" for key, value in counts.items())
    )
    for candidate in candidates:
        print(
            f"{candidate.company_id}\t{candidate.company_name}\t"
            f"domain={candidate.company_domain or 'NULL'}\t"
            f"industry={candidate.industry or 'NULL'}\tsector={candidate.sector or 'NULL'}\t"
            f"{candidate.reason}"
        )

    if not args.apply:
        print("dry run only; use --apply to commit this exact rule-based cleanup")
        return 0

    deleted = delete_candidates(database, candidates)
    print("deleted: " + ", ".join(f"{key}={value}" for key, value in deleted.items()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
