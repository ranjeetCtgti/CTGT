from __future__ import annotations

import argparse
import json
import re

from dotenv import load_dotenv

from db.database import Database


def iso(value):
    return value.isoformat() if value is not None else ""


def normalized_name(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", value.lower())


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ids", default="")
    parser.add_argument("--ids-only", action="store_true")
    args = parser.parse_args()
    selected_ids = {
        int(value)
        for value in args.ids.split(",")
        if value.strip()
    }
    load_dotenv(".env")
    database = Database()
    database.initialize()

    keyword_rows = [
        row
        for row in database.list_keyword_companies(limit=5000)
        if row.qualification_status in {"qualified", "watchlist"}
    ]
    companies_by_domain = {
        company.company_domain: company
        for company in database.get_leads()
        if company.company_domain
    }
    companies_by_name = {
        normalized_name(company.company_name): company
        for company in database.get_leads()
    }

    grouped = {}
    for row in keyword_rows:
        grouped.setdefault(row.company_id, []).append(row)

    output = {}
    for company_id in sorted(grouped):
        if selected_ids and company_id not in selected_ids:
            continue
        rows = grouped[company_id]
        rows.sort(
            key=lambda row: (
                row.qualification_status == "qualified",
                row.opportunity_score,
                row.signal_date or row.last_seen_at,
                row.last_seen_at,
            ),
            reverse=True,
        )
        best = rows[0]
        company = companies_by_domain.get(best.company_domain)
        if company is None:
            company = companies_by_name.get(normalized_name(best.company_name))
        if company is None:
            raise RuntimeError(
                f"Company record missing for id={company_id}, "
                f"domain={best.company_domain}, name={best.company_name}"
            )

        products = sorted(
            {
                product
                for row in rows
                for product in (row.recommended_products or [])
            }
        )
        source_urls = list(dict.fromkeys(row.source_url for row in rows if row.source_url))
        contacts = company.contacts or []
        last_enrichment = company.last_enrichment_at or company.enriched_at
        effective_status = (
            "qualified"
            if any(row.qualification_status == "qualified" for row in rows)
            else "watchlist"
        )
        qualified_at = max(
            (row.qualified_at for row in rows if row.qualified_at is not None),
            default=None,
        )
        latest_discovery = max(row.last_seen_at for row in rows)

        values = [
            company_id,
            company.company_name,
            company.company_domain or "",
            company.company_url or "",
            company.linkedin_url or "",
            company.headquarters_location or company.location or "",
            company.sector or company.company_industry or company.industry or "",
            "; ".join(dict.fromkeys(row.keyword for row in rows)),
            effective_status,
            iso(qualified_at),
            best.opportunity_score,
            best.manufacturing_fit_score,
            best.trigger_score,
            best.solution_fit_score,
            best.evidence_quality_score,
            best.challenge_summary or "",
            best.why_relevant or "",
            "; ".join(products),
            "; ".join(source_urls),
            iso(latest_discovery),
            "enriched" if last_enrichment else "not enriched",
            iso(last_enrichment),
            len(contacts),
            "; ".join(
                f"{contact.full_name} - {contact.title}"
                if contact.title
                else contact.full_name
                for contact in contacts
            ),
            "; ".join(
                contact.linkedin_url
                for contact in contacts
                if contact.linkedin_url
            ),
            "; ".join(company.software or []),
            company.lead_score,
            company.total_score,
            company.signal_count,
            "; ".join(company.signal_sources or []),
        ]
        if len(values) != 30:
            raise RuntimeError(f"Unexpected column count for {company.company_name}")
        output[str(company_id)] = values

    payload = {
        "row_count": len(grouped),
        "expected_ids": sorted(grouped),
        "rows": {} if args.ids_only else output,
    }
    print(json.dumps(payload, ensure_ascii=False))


if __name__ == "__main__":
    main()
