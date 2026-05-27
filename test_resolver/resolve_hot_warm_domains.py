from __future__ import annotations

import argparse
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from loguru import logger
from sqlalchemy import func, select
from db import EnrichmentLogEntry, init_database
from db.database import CompanyRecord, SignalRecord
from enrichment.domain_resolution import canonicalize_domain, resolve_company_domain


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Resolve domains for all hot and warm companies already stored in the database."
    )
    parser.add_argument("--limit", type=int, default=None, help="Limit how many hot/warm companies are processed.")
    parser.add_argument("--offset", type=int, default=0, help="Skip the first N hot/warm companies before processing.")
    parser.add_argument(
        "--only-missing",
        action="store_true",
        help="Process only companies whose stored company_domain is currently empty.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Resolve and print results without writing any database updates.",
    )
    return parser.parse_args()


def load_dotenv() -> None:
    env_path = Path(".env")
    if not env_path.exists():
        return

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        if key and key not in os.environ:
            os.environ[key] = value


def configure_logging() -> None:
    logger.remove()
    logger.add(os.sys.stderr, level=os.getenv("LOG_LEVEL", "INFO"))


def main() -> int:
    load_dotenv()
    configure_logging()
    args = parse_args()

    database = init_database()
    leads = database.get_leads(limit=None)
    targets = [lead for lead in leads if lead.lead_score in {"hot", "warm"}]
    if args.only_missing:
        targets = [lead for lead in targets if not canonicalize_domain(lead.company_domain)]
    if args.offset:
        targets = targets[args.offset :]
    if args.limit is not None:
        targets = targets[: args.limit]

    processed = 0
    resolved = 0
    changed = 0
    unchanged = 0
    missed = 0
    errors = 0

    logger.info(
        "domain refresh start targets={} dry_run={} only_missing={}",
        len(targets),
        args.dry_run,
        args.only_missing,
    )

    for lead in targets:
        processed += 1
        old_domain = canonicalize_domain(lead.company_domain)
        try:
            result = resolve_company_domain(lead.company_name, location=lead.location)
            new_domain = canonicalize_domain(result.company_domain)
        except Exception as exc:
            errors += 1
            _save_log(
                database,
                company_name=lead.company_name,
                company_domain=old_domain,
                provider="serper",
                status="error",
                message=str(exc),
                payload={"old_domain": old_domain, "location": lead.location},
                dry_run=args.dry_run,
            )
            logger.warning("domain refresh error company={} error={}", lead.company_name, exc)
            print(f"ERROR\t{lead.lead_score}\t{lead.company_name}\t{type(exc).__name__}: {exc}")
            continue

        if not new_domain:
            missed += 1
            _save_log(
                database,
                company_name=lead.company_name,
                company_domain=old_domain,
                provider=result.source,
                status="miss",
                message=result.reason,
                payload={"old_domain": old_domain, "location": lead.location},
                dry_run=args.dry_run,
            )
            logger.info(
                "domain refresh miss company={} old_domain={} source={} reason={}",
                lead.company_name,
                old_domain or "-",
                result.source,
                result.reason or "-",
            )
            print(f"MISS\t{lead.lead_score}\t{lead.company_name}\t{result.source}\t{result.reason or ''}")
            continue

        resolved += 1
        is_changed = new_domain != old_domain
        if is_changed:
            changed += 1
        else:
            unchanged += 1

        _save_log(
            database,
            company_name=lead.company_name,
            company_domain=new_domain,
            provider=result.source,
            status="success",
            message=result.reason,
            payload={
                "old_domain": old_domain,
                "new_domain": new_domain,
                "confidence": result.confidence,
                "location": lead.location,
            },
            dry_run=args.dry_run,
        )

        if not args.dry_run:
            _persist_domain_update(
                database,
                company_name=lead.company_name,
                old_domain=old_domain,
                new_domain=new_domain,
                source=result.source,
                confidence=result.confidence,
            )

        logger.info(
            "domain refresh success company={} old_domain={} new_domain={} source={} confidence={} changed={}",
            lead.company_name,
            old_domain or "-",
            new_domain,
            result.source,
            result.confidence,
            is_changed,
        )
        print(
            f"OK\t{lead.lead_score}\t{lead.company_name}\t{old_domain or '-'}\t{new_domain}\t"
            f"{result.source}\t{result.confidence:.4f}\tchanged={is_changed}"
        )

    print("")
    print(
        "Summary\t"
        f"processed={processed}\tresolved={resolved}\tchanged={changed}\tunchanged={unchanged}\t"
        f"missed={missed}\terrors={errors}\tdry_run={args.dry_run}"
    )
    return 0


def _persist_domain_update(
    database: object,
    *,
    company_name: str,
    old_domain: str | None,
    new_domain: str,
    source: str,
    confidence: float,
) -> None:
    now = datetime.now(timezone.utc)
    with database.session() as session:
        company = session.scalar(
            select(CompanyRecord).where(func.lower(CompanyRecord.company_name) == company_name.lower()).limit(1)
        )
        if company is None:
            logger.warning("domain refresh persist skipped company={} reason=no_company_record", company_name)
            return

        conflicting = session.scalar(
            select(CompanyRecord)
            .where(CompanyRecord.company_domain == new_domain, CompanyRecord.id != company.id)
            .limit(1)
        )
        if conflicting is not None:
            logger.warning(
                "domain refresh persist skipped company={} new_domain={} conflicting_company={}",
                company_name,
                new_domain,
                conflicting.company_name,
            )
            return

        company.company_domain = new_domain
        company.enrichment_source = source
        company.enrichment_confidence = confidence
        company.last_updated = now

        signal_rows = session.scalars(
            select(SignalRecord).where(func.lower(SignalRecord.company_name) == company_name.lower())
        ).all()
        for signal in signal_rows:
            signal.company_domain = new_domain

        session.commit()


def _save_log(
    database: object,
    *,
    company_name: str,
    company_domain: str | None,
    provider: str,
    status: str,
    message: str | None,
    payload: dict[str, object | None],
    dry_run: bool,
) -> None:
    if dry_run:
        return
    database.save_enrichment_log(
        EnrichmentLogEntry(
            company_name=company_name,
            company_domain=company_domain,
            stage="domain_resolution",
            provider=provider,
            status=status,
            message=message,
            payload=payload,
        )
    )


if __name__ == "__main__":
    raise SystemExit(main())
