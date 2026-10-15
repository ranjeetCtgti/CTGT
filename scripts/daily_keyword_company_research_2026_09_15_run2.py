from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from db.database import Database
from enrichment.identity_verification import CompanyIdentityEvidence
from models.schema import ExtractedSignal


RUN_AT = datetime.now(timezone.utc)
LOCK_PATH = Path(
    r"C:\Users\ranjeet.chaudhary\.codex\automations\daily-keyword-company-research\run.lock"
)
SOURCE_URL = (
    "https://www.reuters.com/business/stellantis-signs-roshel-memorandum-"
    "potential-factory-sale-bloomberg-news-reports-2026-09-11/"
)
PRODUCTS = ["Teamcenter", "Polarion", "Tecnomatix", "Opcenter"]


def main() -> None:
    load_dotenv(REPO_ROOT / ".env")
    marker = json.loads(LOCK_PATH.read_text(encoding="utf-8"))
    if int(marker.get("pid", 0)) <= 0:
        raise RuntimeError("Exclusive automation lock is not held")

    database = Database(os.environ["DATABASE_URL"])
    database.initialize()
    before = {row.id: row for row in database.list_keywords()}
    expected = {1, 2, 3, 4, 5, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16}
    if set(before) != expected:
        raise RuntimeError(f"Persistent keyword set changed: {sorted(before)}")

    challenge_summary = (
        "On September 11, 2026, Reuters reported that Stellantis signed a memorandum "
        "of understanding with Roshel for the potential sale of the idled Brampton "
        "Assembly plant, and Roshel said it plans to establish a defence-manufacturing "
        "centre there and give laid-off Unifor workers first consideration for jobs as "
        "early as 2026. Stellantis said Roshel represents a path to restoring sustainable "
        "operations at the site; the transaction is still conditional, but it would move "
        "Roshel from its already space-constrained 400,000-square-foot operation toward an "
        "automotive-scale factory. Inference: absorbing a large assembly plant while ramping "
        "configurable armoured vehicles creates immediate factory-layout, variant-BOM, "
        "supplier-transfer, work-instruction, quality-genealogy and production-scheduling pressure."
    )
    why_relevant = (
        "Teamcenter can govern vehicle variants, approved parts, suppliers and engineering "
        "changes as Roshel transfers and expands production. Polarion can connect ballistic, "
        "blast, mobility and customer requirements to verification evidence, while Tecnomatix "
        "can plan the Brampton line and Opcenter can control execution and unit-level quality "
        "genealogy. The memorandum and stated 2026 hiring timeline make the systems decision "
        "urgent before the physical production transfer is finalized."
    )
    identity = CompanyIdentityEvidence(
        official_name="Roshel Smart Armored Vehicles",
        official_website_url="https://roshel.com/",
        corroborating_urls=(SOURCE_URL,),
    )
    signal = ExtractedSignal(
        company_name="Roshel Smart Armored Vehicles",
        company_domain="roshel.com",
        company_url="https://roshel.com/",
        location="Brampton, Ontario, Canada",
        industry="Armoured and special-purpose vehicle manufacturing",
        company_industry="Armoured and special-purpose vehicle manufacturing",
        software=PRODUCTS,
        signal_type="news",
        signal_source="news",
        pain_signals=[
            "Must transfer and scale configurable armoured-vehicle production into an automotive-scale plant while preserving approved configurations, defence verification evidence and unit-level quality genealogy."
        ],
        expansion_signals=[
            "Signed a memorandum with Stellantis for a potential acquisition of the idled Brampton Assembly plant and stated plans for a defence-manufacturing centre with hiring as early as 2026."
        ],
        raw_score=97,
        confidence=0.98,
        reason=challenge_summary,
        source_url=SOURCE_URL,
        source_title="Stellantis signs memorandum of understanding with Roshel for potential Canadian factory sale",
        detected_at=datetime(2026, 9, 11, tzinfo=timezone.utc),
    )

    saved, company = database.persist_verified_signal(signal, identity)
    published = {keyword_id: 0 for keyword_id in before}
    links = []
    for keyword_id in (11, 14):
        row = database.record_keyword_company(
            keyword_id,
            "Roshel Smart Armored Vehicles",
            "roshel.com",
            source_url=SOURCE_URL,
            source_title=signal.source_title,
            source_publisher="Reuters",
            signal_label="Roshel targets idled Brampton Assembly plant for a defence-manufacturing centre",
            signal_date=datetime(2026, 9, 11, tzinfo=timezone.utc),
            challenge_summary=challenge_summary,
            why_relevant=why_relevant,
            recommended_products=PRODUCTS,
            qualification_status="qualified",
            opportunity_score=97,
            manufacturing_fit_score=100,
            trigger_score=97,
            solution_fit_score=98,
            evidence_quality_score=98,
            seen_at=RUN_AT,
        )
        if row is None:
            raise RuntimeError(f"Could not link Roshel to keyword {keyword_id}")
        published[keyword_id] += 1
        links.append(
            {
                "keyword_id": keyword_id,
                "company_id": row.company_id,
                "qualification_status": row.qualification_status,
                "opportunity_score": row.opportunity_score,
            }
        )

    for keyword_id in sorted(before):
        if database.record_keyword_search(
            keyword_id, result_count=published[keyword_id], error=None
        ) is None:
            raise RuntimeError(f"Could not record keyword search {keyword_id}")

    after = {row.id: row for row in database.list_keywords()}
    for keyword_id, prior in before.items():
        current = after[keyword_id]
        if current.search_count != prior.search_count + 1:
            raise RuntimeError(f"Keyword {keyword_id} did not advance exactly once")
        if current.last_error is not None:
            raise RuntimeError(f"Keyword {keyword_id} retained error: {current.last_error}")

    print(
        json.dumps(
            {
                "run_at": RUN_AT.isoformat(),
                "company": {
                    "name": company.company_name,
                    "domain": company.company_domain,
                    "signal_count": company.signal_count,
                    "total_score": company.total_score,
                },
                "signal": {
                    "created": saved.created,
                    "duplicate_url": saved.duplicate_url,
                    "source_url": SOURCE_URL,
                },
                "keyword_links": links,
                "keyword_audits": [
                    {
                        "id": keyword_id,
                        "keyword": after[keyword_id].keyword,
                        "search_count_before": before[keyword_id].search_count,
                        "search_count_after": after[keyword_id].search_count,
                        "qualified": published[keyword_id],
                        "watchlist": 0,
                        "last_error": after[keyword_id].last_error,
                    }
                    for keyword_id in sorted(after)
                ],
            },
            indent=2,
            default=str,
        )
    )


if __name__ == "__main__":
    main()
