from __future__ import annotations

import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from db.database import Database, KeywordRecord


EXPECTED_AFTER_ACCIDENTAL_REPLAY = {
    1: 51, 2: 50, 3: 50, 4: 46, 5: 27, 7: 20, 8: 20, 9: 18,
    10: 18, 11: 18, 12: 18, 13: 18, 14: 13, 15: 13, 16: 7,
}


def main() -> None:
    load_dotenv(REPO_ROOT / ".env")
    database = Database(os.environ["DATABASE_URL"])
    database.initialize()
    now = datetime.now(timezone.utc)
    with database.session() as session, session.begin():
        rows = {row.id: row for row in session.query(KeywordRecord).all()}
        actual = {keyword_id: rows[keyword_id].search_count for keyword_id in EXPECTED_AFTER_ACCIDENTAL_REPLAY}
        if actual != EXPECTED_AFTER_ACCIDENTAL_REPLAY:
            raise RuntimeError(f"Refusing correction because counts changed: {actual}")
        for keyword_id in EXPECTED_AFTER_ACCIDENTAL_REPLAY:
            rows[keyword_id].search_count -= 1
            rows[keyword_id].updated_at = now
    print("Corrected one accidental keyword-audit replay for all 15 persistent keywords.")


if __name__ == "__main__":
    main()
