from __future__ import annotations

import argparse
import asyncio
import csv
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import httpx
from loguru import logger
from sqlalchemy import select

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from db import init_database
from db.database import CompanyRecord
from enrichment.domain_resolution import canonicalize_domain

LEGAL_SUFFIXES = {
    "gmbh",
    "ag",
    "kg",
    "se",
    "inc",
    "ltd",
    "llc",
    "plc",
    "sa",
    "srl",
    "bv",
    "corp",
    "corporation",
    "limited",
    "co",
    "company",
    "pty",
}

SOURCE_TLDS = {
    "stepstone": [".de", ".com", ".eu", ".net", ".io", ".co"],
    "indeed": [".com", ".ca", ".com.au", ".au", ".de"],
    "linkedin": [".com", ".de", ".ca", ".com.au", ".au"],
    "google": [".com", ".de", ".ca", ".com.au", ".au"],
    "career_page": [".com", ".de", ".ca", ".com.au", ".au"],
    "news": [".com", ".de", ".ca", ".com.au", ".au"],
}

LOCATION_TLDS = [
    ("germany", [".de"]),
    ("deutschland", [".de"]),
    ("canada", [".ca", ".com"]),
    ("australia", [".com.au", ".au", ".com"]),
    ("united states", [".com"]),
    ("usa", [".com"]),
    ("us", [".com"]),
    ("india", [".in", ".com"]),
]


@dataclass(slots=True)
class GuessRow:
    company_name: str
    location: str | None
    signal_sources: list[str]
    stored_domain: str | None
    guessed_domain: str | None
    matched_stored_domain: bool
    validated_url: str | None
    http_status: int | None
    attempted_candidates: list[str]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Guess company domains from raw names and validate them with simple HTTP requests."
    )
    parser.add_argument("--limit", type=int, default=None, help="Limit how many companies are tested.")
    parser.add_argument("--offset", type=int, default=0, help="Skip the first N companies.")
    parser.add_argument(
        "--only-missing",
        action="store_true",
        help="Only test companies whose stored domain is currently empty.",
    )
    parser.add_argument(
        "--source",
        action="append",
        default=[],
        help="Restrict to companies that contain this signal source. Can be passed multiple times.",
    )
    parser.add_argument(
        "--output",
        default="test_resolver/domain_guess_results.csv",
        help="CSV file to write the raw name/domain guess list to.",
    )
    parser.add_argument("--timeout", type=float, default=5.0, help="HTTP timeout in seconds.")
    parser.add_argument(
        "--concurrency",
        type=int,
        default=12,
        help="Maximum number of concurrent HTTP validations.",
    )
    return parser.parse_args()


def load_dotenv() -> None:
    env_path = PROJECT_ROOT / ".env"
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
    logger.add(sys.stderr, level=os.getenv("LOG_LEVEL", "INFO"))


def main() -> int:
    load_dotenv()
    configure_logging()
    args = parse_args()

    database = init_database()
    rows = _load_company_rows(database)

    if args.source:
        requested_sources = {item.strip().lower() for item in args.source if item.strip()}
        rows = [
            row for row in rows if requested_sources.intersection({source.lower() for source in row.signal_sources})
        ]
    if args.only_missing:
        rows = [row for row in rows if not row.stored_domain]
    if args.offset:
        rows = rows[args.offset :]
    if args.limit is not None:
        rows = rows[: args.limit]

    output_path = (PROJECT_ROOT / args.output).resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    results: list[GuessRow] = []
    results = asyncio.run(_guess_all(rows, timeout=args.timeout, concurrency=args.concurrency))

    _write_csv(output_path, results)
    _print_summary(results, output_path)
    return 0


def _load_company_rows(database: object) -> list[GuessRow]:
    with database.session() as session:
        companies = session.scalars(
            select(CompanyRecord).order_by(CompanyRecord.total_score.desc(), CompanyRecord.last_updated.desc())
        ).all()

    return [
        GuessRow(
            company_name=company.company_name,
            location=company.location,
            signal_sources=list(company.signal_sources or []),
            stored_domain=canonicalize_domain(company.company_domain),
            guessed_domain=None,
            matched_stored_domain=False,
            validated_url=None,
            http_status=None,
            attempted_candidates=[],
        )
        for company in companies
    ]


async def _guess_all(rows: list[GuessRow], *, timeout: float, concurrency: int) -> list[GuessRow]:
    limits = httpx.Limits(max_connections=concurrency, max_keepalive_connections=concurrency)
    semaphore = asyncio.Semaphore(max(1, concurrency))
    async with httpx.AsyncClient(
        timeout=timeout,
        follow_redirects=True,
        limits=limits,
        headers={"User-Agent": "Mozilla/5.0 (compatible; CTGT-DomainGuessTester/1.0)"},
    ) as client:
        tasks = [_guess_for_company(client, semaphore, row) for row in rows]
        return list(await asyncio.gather(*tasks))


async def _guess_for_company(client: httpx.AsyncClient, semaphore: asyncio.Semaphore, row: GuessRow) -> GuessRow:
    candidates = list(_build_candidates(row.company_name, row.location, row.signal_sources))
    guessed_domain: str | None = None
    validated_url: str | None = None
    http_status: int | None = None

    print(
        f"COMPANY\t{row.company_name}\tstored={row.stored_domain or '-'}\t"
        f"sources={','.join(row.signal_sources) or '-'}"
    )

    for candidate in candidates:
        validated = await _validate_candidate(client, semaphore, candidate)
        if validated is None:
            print(f"MISS\t{row.company_name}\t{candidate}")
            continue
        guessed_domain = candidate
        validated_url = validated["url"]
        http_status = validated["status_code"]
        print(f"OK\t{row.company_name}\t{candidate}\tstatus={http_status}\turl={validated_url}")
        break

    if guessed_domain is None:
        print(f"UNRESOLVED\t{row.company_name}")

    return GuessRow(
        company_name=row.company_name,
        location=row.location,
        signal_sources=row.signal_sources,
        stored_domain=row.stored_domain,
        guessed_domain=guessed_domain,
        matched_stored_domain=bool(guessed_domain and row.stored_domain and guessed_domain == row.stored_domain),
        validated_url=validated_url,
        http_status=http_status,
        attempted_candidates=candidates,
    )


def _build_candidates(company_name: str, location: str | None, signal_sources: list[str]) -> Iterable[str]:
    bases = _build_name_bases(company_name)
    if not bases:
        return []

    tlds = _infer_tlds(location, signal_sources)
    candidates: list[str] = []
    seen: set[str] = set()

    for base in bases:
        for tld in tlds:
            candidate = canonicalize_domain(f"{base}{tld}")
            if not candidate or candidate in seen:
                continue
            seen.add(candidate)
            candidates.append(candidate)

    return candidates


def _build_name_bases(company_name: str) -> list[str]:
    cleaned = company_name.strip().lower()
    cleaned = (
        cleaned.replace("ä", "ae")
        .replace("ö", "oe")
        .replace("ü", "ue")
        .replace("ß", "ss")
    )
    cleaned = cleaned.replace("&", " and ")
    cleaned = cleaned.replace("@", " ")
    cleaned = re.sub(r"[^a-z0-9\s-]", " ", cleaned)
    tokens = [token for token in re.findall(r"[a-z0-9]+", cleaned) if token not in LEGAL_SUFFIXES]
    if not tokens:
        return []

    variants: list[str] = []
    seen: set[str] = set()

    joined = "".join(tokens)
    dashed = "-".join(tokens)
    undersized = [joined, dashed, tokens[0]]
    if len(tokens) >= 2:
        undersized.append("".join(tokens[:2]))
        undersized.append("-".join(tokens[:2]))

    for item in undersized:
        normalized = item.strip("-")
        if len(normalized) < 3 or len(normalized) > 30 or normalized in seen:
            continue
        seen.add(normalized)
        variants.append(normalized)

    return variants[:4]


def _infer_tlds(location: str | None, signal_sources: list[str]) -> list[str]:
    ordered: list[str] = []
    seen: set[str] = set()
    matched_location_tlds: list[str] = []

    source_keys = [source.strip().lower() for source in signal_sources if source.strip()]
    for source in source_keys:
        for tld in SOURCE_TLDS.get(source, []):
            if tld not in seen:
                seen.add(tld)
                ordered.append(tld)

    if "stepstone" in source_keys:
        matched_location_tlds = [".de"]

    location_norm = (location or "").strip().lower()
    for marker, tlds in LOCATION_TLDS:
        if marker in location_norm:
            matched_location_tlds = tlds
            for tld in tlds:
                if tld not in seen:
                    seen.add(tld)
                    ordered.append(tld)
            break

    if matched_location_tlds:
        fallback_tlds = [".com", ".net", ".io", ".co"]
    else:
        fallback_tlds = [".com", ".de", ".ca", ".com.au", ".au", ".in", ".net", ".io", ".co"]

    for fallback in fallback_tlds:
        if fallback not in seen:
            seen.add(fallback)
            ordered.append(fallback)

    return ordered[:6]


async def _validate_candidate(
    client: httpx.AsyncClient,
    semaphore: asyncio.Semaphore,
    candidate: str,
) -> dict[str, str | int] | None:
    urls = [f"https://{candidate}"]
    for url in urls:
        response = await _request_candidate(client, semaphore, "HEAD", url)
        if response is not None:
            print(f"REQUEST\tHEAD\t{url}\tstatus={response.status_code}")
        else:
            print(f"REQUEST\tHEAD\t{url}\tstatus=error")
        if response is None or response.status_code >= 400:
            response = await _request_candidate(client, semaphore, "GET", url)
            if response is not None:
                print(f"REQUEST\tGET\t{url}\tstatus={response.status_code}")
            else:
                print(f"REQUEST\tGET\t{url}\tstatus=error")
        if response is None or response.status_code >= 400:
            continue
        return {"url": str(response.url), "status_code": int(response.status_code)}
    return None


async def _request_candidate(
    client: httpx.AsyncClient,
    semaphore: asyncio.Semaphore,
    method: str,
    url: str,
) -> httpx.Response | None:
    try:
        async with semaphore:
            return await client.request(method, url)
    except Exception:
        return None


def _write_csv(output_path: Path, results: list[GuessRow]) -> None:
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "company_name",
                "location",
                "signal_sources",
                "stored_domain",
                "guessed_domain",
                "matched_stored_domain",
                "validated_url",
                "http_status",
                "attempted_candidates",
            ],
        )
        writer.writeheader()
        for row in results:
            writer.writerow(
                {
                    "company_name": row.company_name,
                    "location": row.location or "",
                    "signal_sources": ",".join(row.signal_sources),
                    "stored_domain": row.stored_domain or "",
                    "guessed_domain": row.guessed_domain or "",
                    "matched_stored_domain": str(row.matched_stored_domain).lower(),
                    "validated_url": row.validated_url or "",
                    "http_status": "" if row.http_status is None else row.http_status,
                    "attempted_candidates": ",".join(row.attempted_candidates),
                }
            )


def _print_summary(results: list[GuessRow], output_path: Path) -> None:
    tested = len(results)
    with_guess = sum(1 for row in results if row.guessed_domain)
    with_stored = sum(1 for row in results if row.stored_domain)
    correct = sum(1 for row in results if row.matched_stored_domain)

    print(f"results_file\t{output_path}")
    print(f"tested\t{tested}")
    print(f"guessed\t{with_guess}")
    print(f"stored_domain_available\t{with_stored}")
    print(f"correct_matches\t{correct}")
    if with_stored:
        print(f"match_rate_vs_stored\t{correct / with_stored:.4f}")
    else:
        print("match_rate_vs_stored\tna")


if __name__ == "__main__":
    raise SystemExit(main())
