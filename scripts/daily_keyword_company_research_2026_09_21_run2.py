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

from db.database import CompanyRecord, Database, KeywordCompanyResultRecord, SignalRecord
from enrichment.identity_verification import CompanyIdentityEvidence, verify_company_identity
from models.schema import ExtractedSignal


RUN_AT = datetime.now(timezone.utc)
LOCK_PATH = Path(
    r"C:\Users\ranjeet.chaudhary\.codex\automations\daily-keyword-company-research\run.lock"
)
HOME_URL = "https://www.stathera.com/"
PRIMARY_URL = (
    "https://www.prnewswire.com/news-releases/stathera-announces-us55-million-"
    "series-b-to-scale-silicon-timing-and-accelerate-next-generation-ai-data-"
    "center-solutions-302813712.html"
)
CORROBORATING_URL = (
    "https://www.finsmes.com/2026/06/stathera-raises-us55m-in-series-b-funding.html"
)


PROSPECT = {
    "company_name": "Stathera Inc.",
    "company_domain": "stathera.com",
    "company_url": HOME_URL,
    "location": "Montreal, Quebec, Canada",
    "industry": "MEMS-based silicon timing semiconductors",
    "products": ["Teamcenter", "Polarion", "Simcenter"],
    "identity": CompanyIdentityEvidence(
        official_name="Stathera Inc.",
        official_website_url=HOME_URL,
        corroborating_urls=(CORROBORATING_URL,),
    ),
    "signals": [
        {
            "source_url": PRIMARY_URL,
            "source_title": (
                "Stathera Announces US$55 Million Series B to Scale Silicon Timing "
                "and Accelerate Next-Generation AI Data Center Solutions"
            ),
            "source_publisher": "PR Newswire / Stathera Inc.",
            "signal_date": datetime(2026, 6, 30, tzinfo=timezone.utc),
            "reason": (
                "On June 30, 2026, Stathera closed an oversubscribed US$55 million Series B, "
                "bringing total funding to US$75 million, to move its GEN2 32.768 kHz silicon-"
                "timing portfolio into mass production, expand Tier-1 OEM sampling, grow its "
                "engineering team, and start the GEN3 AI/data-centre platform targeted for first "
                "customer samples in 2028. Inference: simultaneous volume ramp, multiple product "
                "generations, foundry/manufacturing partners, OEM samples, and stringent timing "
                "performance create configuration, change-control, requirements-to-test, and "
                "multiphysics-validation pressure. Teamcenter, Polarion, and Simcenter are the "
                "smallest defensible set to govern product/process baselines, connect requirements "
                "to verification, and manage thermal and system validation; the funded mass-"
                "production program makes those controls urgent now."
            ),
            "pain": (
                "Must control silicon product variants, foundry and partner baselines, OEM sample "
                "configurations, engineering changes, and verification evidence across concurrent "
                "GEN2 production and GEN3 development."
            ),
            "expansion": (
                "Raised US$55 million to scale GEN2 mass production, expand Tier-1 OEM sampling, "
                "grow engineering, and develop a GEN3 AI/data-centre timing platform."
            ),
        },
        {
            "source_url": CORROBORATING_URL,
            "source_title": "Stathera Raises US$55M in Series B Funding",
            "source_publisher": "FinSMEs",
            "signal_date": datetime(2026, 6, 30, tzinfo=timezone.utc),
            "reason": (
                "On June 30, 2026, FinSMEs independently reported Stathera's US$55 million "
                "Series B and US$75 million total funding, naming the GEN2 32.768 kHz mass-"
                "production ramp, GEN3 AI-data-centre development, Tier-1 OEM sampling, team "
                "growth, and a new Silicon Valley presence as uses of proceeds. Inference: moving "
                "MEMS oscillators that are up to 85% smaller than standard quartz packages from "
                "samples to volume while developing a new platform increases BOM, revision, "
                "supplier, requirements, and validation workload. Teamcenter can control product "
                "and partner configurations, Polarion can maintain requirements and test traceability, "
                "and Simcenter can support thermal and system validation; current funding and OEM "
                "sampling create a near-term implementation window."
            ),
            "pain": (
                "Must industrialize compact MEMS timing devices for Tier-1 OEMs while preserving "
                "traceable configurations, supplier changes, performance requirements, and test results."
            ),
            "expansion": (
                "Independent coverage confirmed US$55 million in new capital for volume production, "
                "GEN3 development, team growth, and a Silicon Valley customer presence."
            ),
        },
    ],
    "keyword_id": 8,
    "signal_label": "US$55M Series B funds GEN2 mass production and GEN3 development",
    "challenge_summary": (
        "On June 30, 2026, Montreal-based Stathera closed an oversubscribed US$55 million "
        "Series B, lifting total funding to US$75 million, to take its GEN2 32.768 kHz MEMS "
        "timing portfolio into mass production, expand Tier-1 OEM sampling, grow engineering, "
        "and launch GEN3 development for AI data centres with first samples targeted for 2028. "
        "Inference: concurrent product generations, foundry and manufacturing partners, OEM sample "
        "configurations, and demanding timing-performance targets create immediate BOM, change, "
        "requirements-to-test, supplier, and validation pressure."
    ),
    "why_relevant": (
        "Teamcenter can govern silicon product and process baselines, OEM sample configurations, "
        "and partner changes; Polarion can connect timing and reliability requirements to tests and "
        "defects. Simcenter can support thermal and system-level validation as the devices move from "
        "sampling into volume applications. The practical outcome is a faster production ramp with "
        "fewer configuration escapes and defensible verification evidence for OEM customers."
    ),
    "qualification_status": "qualified",
    "opportunity_score": 91,
    "manufacturing_fit_score": 92,
    "trigger_score": 95,
    "solution_fit_score": 89,
    "evidence_quality_score": 94,
}


def make_signal(evidence: dict) -> ExtractedSignal:
    return ExtractedSignal(
        company_name=PROSPECT["company_name"],
        company_domain=PROSPECT["company_domain"],
        company_url=PROSPECT["company_url"],
        location=PROSPECT["location"],
        industry=PROSPECT["industry"],
        company_industry=PROSPECT["industry"],
        software=PROSPECT["products"],
        signal_type="news",
        signal_source="news",
        pain_signals=[evidence["pain"]],
        expansion_signals=[evidence["expansion"]],
        raw_score=PROSPECT["opportunity_score"],
        confidence=PROSPECT["evidence_quality_score"] / 100,
        reason=evidence["reason"],
        source_url=evidence["source_url"],
        source_title=evidence["source_title"],
        detected_at=evidence["signal_date"],
    )


def main() -> None:
    load_dotenv(REPO_ROOT / ".env")
    marker = json.loads(LOCK_PATH.read_text(encoding="utf-8"))
    if int(marker.get("pid", 0)) <= 0:
        raise RuntimeError("Exclusive automation lock is not held")

    database = Database(os.environ["DATABASE_URL"])
    database.initialize()
    keywords_before = {row.id: row for row in database.list_keywords()}
    expected = {1, 2, 3, 4, 5, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16}
    if set(keywords_before) != expected:
        raise RuntimeError(f"Persistent keyword set changed: {sorted(keywords_before)}")

    with database.session() as session:
        prior_identity = session.execute(
            select(CompanyRecord.id, CompanyRecord.company_name, CompanyRecord.company_domain)
            .where(
                (func.lower(CompanyRecord.company_domain) == PROSPECT["company_domain"])
                | (func.lower(CompanyRecord.company_name).like("%stathera%"))
            )
        ).all()
    if prior_identity:
        raise RuntimeError(f"Existing Stathera identity requires reassessment: {prior_identity}")

    for evidence in PROSPECT["signals"]:
        verify_company_identity(make_signal(evidence), PROSPECT["identity"])

    evidence_results = []
    company = None
    for evidence in PROSPECT["signals"]:
        saved, company = database.persist_verified_signal(
            make_signal(evidence), PROSPECT["identity"]
        )
        evidence_results.append(
            {
                "source_url": evidence["source_url"],
                "created": saved.created,
                "duplicate_url": saved.duplicate_url,
            }
        )
    if company is None:
        raise RuntimeError("Stathera persistence returned no company")

    keyword_row = database.record_keyword_company(
        PROSPECT["keyword_id"],
        PROSPECT["company_name"],
        PROSPECT["company_domain"],
        source_url=PRIMARY_URL,
        source_title=PROSPECT["signals"][0]["source_title"],
        source_publisher=PROSPECT["signals"][0]["source_publisher"],
        signal_label=PROSPECT["signal_label"],
        signal_date=PROSPECT["signals"][0]["signal_date"],
        challenge_summary=PROSPECT["challenge_summary"],
        why_relevant=PROSPECT["why_relevant"],
        recommended_products=PROSPECT["products"],
        qualification_status=PROSPECT["qualification_status"],
        opportunity_score=PROSPECT["opportunity_score"],
        manufacturing_fit_score=PROSPECT["manufacturing_fit_score"],
        trigger_score=PROSPECT["trigger_score"],
        solution_fit_score=PROSPECT["solution_fit_score"],
        evidence_quality_score=PROSPECT["evidence_quality_score"],
        seen_at=RUN_AT,
    )
    if keyword_row is None:
        raise RuntimeError("Could not link Stathera to keyword 8")

    published = {keyword_id: 0 for keyword_id in keywords_before}
    published[PROSPECT["keyword_id"]] = 1
    for keyword_id in sorted(keywords_before):
        if database.record_keyword_search(
            keyword_id, result_count=published[keyword_id], error=None
        ) is None:
            raise RuntimeError(f"Could not record keyword search {keyword_id}")

    keywords_after = {row.id: row for row in database.list_keywords()}
    for keyword_id, prior in keywords_before.items():
        current = keywords_after[keyword_id]
        if current.search_count != prior.search_count + 1:
            raise RuntimeError(f"Keyword {keyword_id} did not advance exactly once")
        if current.last_error is not None:
            raise RuntimeError(f"Keyword {keyword_id} retained error: {current.last_error}")

    with database.session() as session:
        duplicate_domains = session.execute(
            select(func.lower(CompanyRecord.company_domain), func.count(CompanyRecord.id))
            .where(CompanyRecord.company_domain.is_not(None))
            .group_by(func.lower(CompanyRecord.company_domain))
            .having(func.count(CompanyRecord.id) > 1)
        ).all()
        duplicate_sources = session.execute(
            select(SignalRecord.source_url, func.count(SignalRecord.id))
            .group_by(SignalRecord.source_url)
            .having(func.count(SignalRecord.id) > 1)
        ).all()
        duplicate_keyword_pairs = session.execute(
            select(
                KeywordCompanyResultRecord.keyword_id,
                KeywordCompanyResultRecord.company_id,
                func.count(KeywordCompanyResultRecord.id),
            )
            .group_by(
                KeywordCompanyResultRecord.keyword_id,
                KeywordCompanyResultRecord.company_id,
            )
            .having(func.count(KeywordCompanyResultRecord.id) > 1)
        ).all()
        eligible_company_count = session.scalar(
            select(func.count(func.distinct(KeywordCompanyResultRecord.company_id))).where(
                KeywordCompanyResultRecord.qualification_status.in_(("qualified", "watchlist"))
            )
        )

    if duplicate_domains or duplicate_sources or duplicate_keyword_pairs:
        raise RuntimeError(
            "Post-write duplicate audit failed: "
            f"domains={duplicate_domains}, sources={duplicate_sources}, "
            f"keyword_pairs={duplicate_keyword_pairs}"
        )

    print(
        json.dumps(
            {
                "run_at": RUN_AT.isoformat(),
                "persisted": {
                    "company_id": keyword_row.company_id,
                    "company_name": company.company_name,
                    "company_domain": company.company_domain,
                    "signal_count": company.signal_count,
                    "keyword_id": keyword_row.keyword_id,
                    "qualification_status": keyword_row.qualification_status,
                    "opportunity_score": keyword_row.opportunity_score,
                    "evidence": evidence_results,
                },
                "keyword_audits": [
                    {
                        "id": keyword_id,
                        "keyword": keywords_after[keyword_id].keyword,
                        "search_count_before": keywords_before[keyword_id].search_count,
                        "search_count_after": keywords_after[keyword_id].search_count,
                        "published": published[keyword_id],
                        "last_error": keywords_after[keyword_id].last_error,
                    }
                    for keyword_id in sorted(keywords_after)
                ],
                "eligible_company_count": eligible_company_count,
                "duplicate_audit": {
                    "canonical_domains": 0,
                    "source_urls": 0,
                    "keyword_company_pairs": 0,
                },
            },
            indent=2,
            default=str,
        )
    )


if __name__ == "__main__":
    main()
