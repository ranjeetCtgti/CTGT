from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import select


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from db.database import Database, KeywordRecord


LOCK_PATH = Path(
    r"C:\Users\ranjeet.chaudhary\.codex\automations\daily-keyword-company-research\run.lock"
)
EXPECTED_COUNTS = {
    1: 50,
    2: 49,
    3: 49,
    4: 45,
    5: 26,
    7: 19,
    8: 19,
    9: 17,
    10: 17,
    11: 17,
    12: 17,
    13: 17,
    14: 12,
    15: 12,
    16: 6,
}
WORKBOOK_BLOCKER = (
    "Research completed; publication held because both permitted checks found no "
    "already-open exact canonical OneDrive Keyword_Companies.xlsx session. The "
    "required workbook identity comparison and read-before-write sync could not run."
)


def main() -> None:
    if not LOCK_PATH.exists():
        raise RuntimeError("Exclusive automation run lock is not held")

    lock_marker = json.loads(LOCK_PATH.read_text(encoding="utf-8"))
    if lock_marker.get("mode") != "manual-broader-rerun":
        raise RuntimeError(f"Unexpected lock marker: {lock_marker}")

    load_dotenv(REPO_ROOT / ".env")
    database = Database(os.environ["DATABASE_URL"])
    database.initialize()
    now = datetime.now(timezone.utc)

    # One transaction makes the per-keyword audit all-or-nothing. The expected-count
    # guard also makes this one-off script fail safely if it is run twice.
    with database.session() as session, session.begin():
        records = {
            record.id: record
            for record in session.scalars(
                select(KeywordRecord)
                .where(KeywordRecord.id.in_(sorted(EXPECTED_COUNTS)))
                .with_for_update()
            ).all()
        }
        actual = {keyword_id: record.search_count for keyword_id, record in records.items()}
        if actual != EXPECTED_COUNTS:
            raise RuntimeError(
                "Keyword search counts changed; refusing a duplicate/partial audit write: "
                f"expected={EXPECTED_COUNTS}, actual={actual}"
            )

        for record in records.values():
            record.search_count += 1
            record.last_result_count = 0
            record.last_error = WORKBOOK_BLOCKER
            record.last_searched_at = now
            record.updated_at = now

    after = {item.id: item.search_count for item in database.list_keywords()}
    expected_after = {keyword_id: count + 1 for keyword_id, count in EXPECTED_COUNTS.items()}
    if {key: after[key] for key in expected_after} != expected_after:
        raise RuntimeError(f"Post-write verification failed: {after}")

    print(
        json.dumps(
            {
                "status": "audit_recorded_publication_blocked",
                "run_at": now.isoformat(),
                "keyword_search_audits": len(EXPECTED_COUNTS),
                "companies_written": 0,
                "signals_written": 0,
                "keyword_company_results_written": 0,
                "search_counts_after": expected_after,
                "last_result_count": 0,
                "last_error": WORKBOOK_BLOCKER,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
