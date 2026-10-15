from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import func, select


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from db.database import CompanyRecord, Database, SignalRecord
from enrichment.identity_verification import CompanyIdentityEvidence, verify_company_identity
from models.schema import ExtractedSignal


SOURCE_URL = "https://www.researchmoneyinc.com/article/the-short-report-september-23-2026"


def main() -> None:
    load_dotenv(REPO_ROOT / ".env")
    database = Database(os.environ["DATABASE_URL"])
    database.initialize()
    evidence = CompanyIdentityEvidence(
        official_name="Boreal Biomanufacturing",
        official_website_url="https://boreal-bio.com/",
        corroborating_urls=(
            "https://www.canada.ca/en/innovation-science-economic-development/news/2026/09/"
            "government-of-canada-announces-major-contribution-to-strengthen-canadas-dual-use-life-sciences-sector.html",
            SOURCE_URL,
        ),
    )
    signal = ExtractedSignal(
        company_name="Boreal Biomanufacturing",
        company_domain="boreal-bio.com",
        company_url="https://boreal-bio.com/",
        location="Ottawa, Ontario, Canada",
        industry="GMP viral-vector and biotherapeutics process development and manufacturing",
        company_industry="GMP viral-vector and biotherapeutics process development and manufacturing",
        software=["Opcenter", "Polarion"],
        signal_type="news",
        signal_source="news",
        pain_signals=[
            "Must scale GMP adenovirus production while controlling batch execution, process changes, raw "
            "materials, deviations, corrective actions, release evidence, and electronic quality records."
        ],
        expansion_signals=[
            "Received C$880,000 to expand adenovirus manufacturing capacity, support larger-scale "
            "commercialization, and implement an electronic quality-management system."
        ],
        raw_score=84,
        confidence=0.97,
        reason=(
            "On September 23, 2026, Research Money reported that the Ottawa Hospital Research Institute and "
            "Boreal Biomanufacturing would receive C$880,000 to expand adenovirus manufacturing capacity, enable "
            "larger-scale production and commercialization of vaccines and therapies, and implement an electronic "
            "quality-management system. Inference: adding GMP capacity and digitizing quality increases batch, "
            "raw-material, process-change, deviation, corrective-action, release, and traceability workload. "
            "Opcenter and Polarion are the smallest defensible CTGTI set for electronic production quality plus "
            "controlled requirements, testing, defects, and audit evidence."
        ),
        source_url=SOURCE_URL,
        source_title="The Short Report: September 23, 2026",
        detected_at=datetime(2026, 9, 23, tzinfo=timezone.utc),
    )
    verify_company_identity(signal, evidence)
    saved, _ = database.persist_verified_signal(signal, evidence)
    row = database.record_keyword_company(
        16,
        "Boreal Biomanufacturing",
        "boreal-bio.com",
        source_url=SOURCE_URL,
        source_title="The Short Report: September 23, 2026",
        source_publisher="Research Money",
        signal_label="C$880K expansion adds adenovirus capacity and electronic QMS",
        signal_date=datetime(2026, 9, 23, tzinfo=timezone.utc),
        challenge_summary=(
            "On September 23, 2026, Research Money reported C$880,000 for the Ottawa Hospital Research Institute "
            "and Boreal Biomanufacturing to expand adenovirus manufacturing capacity, enable larger-scale vaccine "
            "and therapy production, and implement an electronic quality-management system. Boreal's official site "
            "describes GMP-compliant process development, manufacturing, and quality-control work. Inference: the "
            "funded scale-up increases batch, material, process-change, deviation, release, and traceability "
            "complexity while quality operations are being digitized."
        ),
        why_relevant=(
            "Opcenter can connect electronic batch execution, in-process quality, deviations, and end-to-end "
            "production genealogy. Polarion can link process and regulatory requirements to tests, defects, and "
            "audit evidence without overextending the product set. Because the grant explicitly funds capacity "
            "growth and an electronic quality-management system, the implementation window is active now."
        ),
        recommended_products=["Opcenter", "Polarion"],
        qualification_status="qualified",
        opportunity_score=84,
        manufacturing_fit_score=91,
        trigger_score=85,
        solution_fit_score=92,
        evidence_quality_score=97,
        seen_at=datetime.now(timezone.utc),
    )
    if row is None:
        raise RuntimeError("Could not update Boreal keyword result")

    # The original federal URL had already been used by Qidni. The initial
    # verified-company insert therefore initialized Boreal's aggregate without
    # creating a second global source row. Normalize the aggregate to the one
    # independently sourced Boreal evidence row created above.
    with database.session() as session:
        company = session.scalar(
            select(CompanyRecord).where(func.lower(CompanyRecord.company_domain) == "boreal-bio.com")
        )
        if company is None:
            raise RuntimeError("Boreal company record is missing")
        actual_signals = session.scalars(
            select(SignalRecord).where(func.lower(SignalRecord.company_domain) == "boreal-bio.com")
        ).all()
        if len(actual_signals) != 1 or actual_signals[0].source_url != SOURCE_URL:
            raise RuntimeError(f"Unexpected Boreal evidence rows: {len(actual_signals)}")
        company.signal_count = 1
        company.total_score = 81
        company.lead_score = "hot"
        company.signal_sources = ["news"]
        company.last_updated = datetime.now(timezone.utc)
        session.commit()
        company_id = company.id

    print(
        json.dumps(
            {
                "company_id": company_id,
                "source_created": saved.created,
                "source_url": SOURCE_URL,
                "signal_count": 1,
                "total_score": 81,
                "keyword_result_id": row.id,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
