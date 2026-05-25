from __future__ import annotations

import argparse
import os
import sys

try:
    from dotenv import load_dotenv
except ImportError:
    def load_dotenv() -> bool:
        return False

try:
    from loguru import logger
except ImportError:
    import logging

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("ctgt_lead_enrichment")
    logger.remove = lambda: None  # type: ignore[attr-defined]
    logger.add = lambda *args, **kwargs: None  # type: ignore[attr-defined]

from db import DatabaseError, init_database
from enrichment import lead_enrichment_enabled, run_lead_enrichment_pass


PLACEHOLDER_ENV_VALUES = {
    "your_google_kg_api_key",
    "postgresql+psycopg2://username:password@localhost:5432/ctgt_leads",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="CTGT lead enrichment pass")
    parser.add_argument("--limit", type=int, default=None, help="Limit how many leads are loaded from the database.")
    parser.add_argument(
        "--freshness-days",
        type=int,
        default=None,
        help="Override the default freshness window before a lead is re-enriched.",
    )
    return parser.parse_args()


def configure_logging() -> None:
    logger.remove()
    logger.add(sys.stderr, level=os.getenv("LOG_LEVEL", "INFO"))


def main() -> int:
    load_dotenv()
    configure_logging()
    args = parse_args()

    try:
        validate_runtime_config(args)
        database = init_database()
    except (ValueError, DatabaseError) as exc:
        logger.error(str(exc))
        return 1

    summary = run_lead_enrichment_pass(
        database,
        freshness_days=args.freshness_days,
        limit=args.limit,
    )

    print("Lead enrichment pass complete.")
    print(
        f"candidates={summary.candidates} | attempted={summary.attempted} | "
        f"completed={summary.completed} | skipped={summary.skipped} | "
        f"errors={summary.errors} | contacts_found={summary.contacts_found}"
    )
    return 0


def validate_runtime_config(args: argparse.Namespace) -> None:
    _validate_positive_int(args.limit, "limit")
    _validate_positive_int(args.freshness_days, "freshness-days")
    _validate_positive_int(os.getenv("LEAD_ENRICHMENT_TIMEOUT_SECONDS"), "LEAD_ENRICHMENT_TIMEOUT_SECONDS")
    _validate_positive_int(os.getenv("LEAD_ENRICHMENT_FRESHNESS_DAYS"), "LEAD_ENRICHMENT_FRESHNESS_DAYS")

    if _is_missing_or_placeholder(os.getenv("DATABASE_URL")):
        raise ValueError("Missing or placeholder environment values: DATABASE_URL")

    if not lead_enrichment_enabled():
        raise ValueError("LEAD_ENRICHMENT_ENABLED must be true to run the enrichment pass")

    required_if_enabled = []
    if _is_missing_or_placeholder(os.getenv("GOOGLE_SEARCH_API_KEY")) or _is_missing_or_placeholder(os.getenv("GOOGLE_SEARCH_ENGINE_ID")):
        logger.warning("Google LinkedIn lookup is not configured; Stage 2 will be skipped")
    if _is_missing_or_placeholder(os.getenv("APOLLO_API_KEY")):
        logger.warning("Apollo is not configured; Stage 3 and Stage 4a will be skipped")
    if _is_missing_or_placeholder(os.getenv("HUNTER_API_KEY")):
        logger.warning("Hunter is not configured; Stage 4b fallback will be skipped")

    if os.getenv("ENRICHMENT_ENABLED", "").strip().lower() in {"1", "true", "yes", "on"}:
        required_if_enabled.append("GOOGLE_KG_API_KEY")

    missing = [name for name in required_if_enabled if _is_missing_or_placeholder(os.getenv(name))]
    if missing:
        raise ValueError(f"Missing or placeholder environment values: {', '.join(missing)}")


def _validate_positive_int(value: int | str | None, name: str) -> None:
    if value is None:
        return
    try:
        parsed = int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must be an integer") from exc
    if parsed <= 0:
        raise ValueError(f"{name} must be greater than 0")


def _is_missing_or_placeholder(value: str | None) -> bool:
    if value is None:
        return True
    cleaned = value.strip()
    return not cleaned or cleaned in PLACEHOLDER_ENV_VALUES


if __name__ == "__main__":
    raise SystemExit(main())
