from __future__ import annotations

import json

from dotenv import load_dotenv

from db.database import Database


TARGET_IDS = {2196, 2197, 2198, 2199}


def iso(value):
    return value.isoformat() if value is not None else ""


def main() -> None:
    load_dotenv(".env")
    database = Database()
    database.initialize()

    keyword_rows = [
        row
        for row in database.list_keyword_companies(limit=5000)
        if row.company_id in TARGET_IDS
        and row.qualification_status in {"qualified", "watchlist"}
    ]
    companies = {
        company.company_domain: company
        for company in database.get_leads()
        if company.company_domain
    }

    grouped = {}
    for row in keyword_rows:
        grouped.setdefault(row.company_id, []).append(row)

    output = []
    for company_id in sorted(grouped):
        rows = grouped[company_id]
        rows.sort(
            key=lambda row: (
                row.qualification_status == "qualified",
                row.opportunity_score,
                row.last_seen_at,
            ),
            reverse=True,
        )
        best = rows[0]
        company = companies.get(best.company_domain)
        if company is None:
            raise RuntimeError(f"Company record missing for {best.company_domain}")

        products = sorted(
            {
                product
                for row in rows
                for product in (row.recommended_products or [])
            }
        )
        source_urls = list(
            dict.fromkeys(row.source_url for row in rows if row.source_url)
        )
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
        output.append(values)

    if set(grouped) != TARGET_IDS:
        raise RuntimeError(f"Missing target rows: {sorted(TARGET_IDS - set(grouped))}")
    print(json.dumps(output, ensure_ascii=False))


if __name__ == "__main__":
    main()
