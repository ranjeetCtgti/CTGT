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

from db.database import (
    CompanyRecord,
    Database,
    KeywordCompanyResultRecord,
    SignalRecord,
)
from enrichment.identity_verification import CompanyIdentityEvidence, verify_company_identity
from models.schema import ExtractedSignal


RUN_AT = datetime.now(timezone.utc)
LOCK_PATH = Path(
    r"C:\Users\ranjeet.chaudhary\.codex\automations\daily-keyword-company-research\run.lock"
)

PHOTONIC_HOME_URL = "https://photonic.com/"
PHOTONIC_FUNDING_URL = (
    "https://photonic.com/news/"
    "photonic-inc-closes-investment-round-with-over-200m-usd-275m-cad/"
)
PHOTONIC_VANGUARD_URL = (
    "https://photonic.com/news/photonic-inc-unveils-project-vanguard/"
)
BETAKIT_FUNDING_URL = (
    "https://betakit.com/photonic-secures-2-billion-usd-valuation-after-final-"
    "close-of-200-million-financing/"
)
BETAKIT_VANGUARD_URL = (
    "https://betakit.com/the-tech-projects-canada-is-selling-to-global-"
    "investors-at-next-weeks-summit/"
)


PROSPECT = {
    "company_name": "Photonic Inc.",
    "company_domain": "photonic.com",
    "company_url": PHOTONIC_HOME_URL,
    "location": "Vancouver, British Columbia, Canada",
    "industry": "Distributed quantum-computing systems and photonic semiconductor hardware",
    "products": ["Teamcenter", "Polarion", "Simcenter", "Tecnomatix"],
    "identity": CompanyIdentityEvidence(
        official_name="Photonic Inc.",
        official_website_url=PHOTONIC_HOME_URL,
        corroborating_urls=(BETAKIT_FUNDING_URL, BETAKIT_VANGUARD_URL),
    ),
    "signals": [
        {
            "source_url": PHOTONIC_VANGUARD_URL,
            "source_title": (
                "Photonic Inc. unveils Project VANGUARD, a proposal for a $500M "
                "specialized semiconductor manufacturing facility"
            ),
            "source_publisher": "Photonic Inc.",
            "signal_date": datetime(2026, 9, 14, tzinfo=timezone.utc),
            "reason": (
                "On September 14, 2026, Photonic announced Project VANGUARD, an up-to-C$500 "
                "million proposed multi-tenant semiconductor manufacturing facility selected for "
                "the Canada Investment Summit Prospectus. The shared facility is intended to serve "
                "quantum, AI, aerospace, defence, sensing, and semiconductor-packaging customers and "
                "to add Canadian design, fabrication, packaging, and commercialization capacity. "
                "Inference: multi-tenant products, controlled process recipes, packaging variants, "
                "defence requirements, and new factory flows create immediate configuration, change, "
                "requirements-to-test, simulation, and plant-planning pressure. Teamcenter, Polarion, "
                "Simcenter, and Tecnomatix are the smallest defensible set to control product/process "
                "baselines, verification evidence, multiphysics validation, and facility planning; the "
                "current investor summit makes the digital operating model urgent before partners and "
                "capital commitments harden the facility design."
            ),
            "pain": (
                "Must define auditable product, process, packaging, requirements, test, and factory "
                "baselines for a proposed multi-tenant quantum-semiconductor manufacturing facility."
            ),
            "expansion": (
                "Proposed an up-to-C$500 million Canadian semiconductor facility serving quantum, AI, "
                "aerospace, defence, sensing, and advanced-packaging programs."
            ),
        },
        {
            "source_url": BETAKIT_VANGUARD_URL,
            "source_title": (
                "The tech projects Canada is selling to global investors at next week's summit"
            ),
            "source_publisher": "BetaKit",
            "signal_date": datetime(2026, 9, 10, tzinfo=timezone.utc),
            "reason": (
                "On September 10, 2026, BetaKit independently reported that Photonic was seeking "
                "C$500 million for Project VANGUARD, described in Canada's investment pitchbook as "
                "the country's first quantum-semiconductor manufacturing facility in Vancouver. "
                "Inference: moving optically linked silicon-spin-qubit systems from laboratory builds "
                "toward a domestic fab raises BOM, supplier, packaging, process-change, test-evidence, "
                "and capacity-planning complexity. Teamcenter can govern configurations and changes, "
                "Polarion can connect quantum and defence requirements to verification, Simcenter can "
                "support thermal and system validation, and Tecnomatix can test facility and process "
                "concepts; investor solicitation creates urgency before layout and operating decisions "
                "become expensive to reverse."
            ),
            "pain": (
                "Must translate a quantum-system architecture into controlled semiconductor products, "
                "packaging processes, supplier records, verification evidence, and scalable factory plans."
            ),
            "expansion": (
                "Independent reporting corroborated a C$500 million financing objective for a proposed "
                "Vancouver quantum-semiconductor manufacturing facility."
            ),
        },
        {
            "source_url": PHOTONIC_FUNDING_URL,
            "source_title": (
                "Photonic Inc. Closes Investment Round with over $200M USD ($275M CAD)"
            ),
            "source_publisher": "Photonic Inc.",
            "signal_date": datetime(2026, 5, 12, tzinfo=timezone.utc),
            "reason": (
                "On May 12, 2026, Photonic closed more than US$200 million (C$275 million) in "
                "financing at a US$2 billion post-money valuation, bringing total capital raised above "
                "US$350 million (C$475 million). The Vancouver company said the funds would deliver "
                "customer milestones, grow its team, and advance commercial-scale distributed quantum "
                "computers and networks built from optically linked silicon-spin qubits. Inference: the "
                "funded commercialization ramp increases product-baseline, multidisciplinary change, "
                "simulation, requirements, and test-traceability workloads. Teamcenter, Polarion, and "
                "Simcenter can connect hardware configurations, verification, and validation results; "
                "the capital is already closed, so those controls are needed during the current scale-up."
            ),
            "pain": (
                "Must scale a multidisciplinary quantum hardware and networking platform while keeping "
                "system configurations, engineering changes, requirements, and validation evidence aligned."
            ),
            "expansion": (
                "Closed more than US$200 million (C$275 million), taking total capital above US$350 "
                "million, to reach milestones, grow the team, and commercialize distributed quantum systems."
            ),
        },
        {
            "source_url": BETAKIT_FUNDING_URL,
            "source_title": (
                "Photonic secures $2-billion USD valuation after final close of $200-million financing"
            ),
            "source_publisher": "BetaKit",
            "signal_date": datetime(2026, 5, 12, tzinfo=timezone.utc),
            "reason": (
                "On May 12, 2026, BetaKit independently confirmed Photonic's more-than-US$200 "
                "million (C$275 million) round and reported that the latest US$70 million close would "
                "fund quantum-computer development, lab expansion, commercialization, and growth from "
                "roughly 170 employees to more than 200 by 2027. It also reported participation from "
                "BDC's defence-focused StrongNorth Fund, EDC, Bell Ventures, InBC, and other strategic "
                "investors. Inference: expanding laboratories, staff, customer commitments, and defence "
                "programs increases configuration, change, requirements, test, and knowledge-transfer "
                "pressure. Teamcenter, Polarion, and Simcenter can provide one controlled engineering and "
                "verification backbone; hiring and lab build-out make that need current."
            ),
            "pain": (
                "Must absorb a 30-plus-person growth plan and laboratory expansion without fragmenting "
                "hardware configurations, requirements, test evidence, and engineering knowledge."
            ),
            "expansion": (
                "Independent reporting confirmed C$275 million in financing, lab expansion, and a plan "
                "to grow from about 170 employees to more than 200 by 2027."
            ),
        },
    ],
    "keyword_id": 8,
    "keyword_source_url": PHOTONIC_VANGUARD_URL,
    "keyword_source_title": (
        "Photonic Inc. unveils Project VANGUARD, a proposal for a $500M specialized "
        "semiconductor manufacturing facility"
    ),
    "keyword_source_publisher": "Photonic Inc.",
    "signal_label": "C$275M financing precedes proposed C$500M quantum-semiconductor facility",
    "signal_date": datetime(2026, 9, 14, tzinfo=timezone.utc),
    "challenge_summary": (
        "On September 14, 2026, Photonic unveiled Project VANGUARD, an up-to-C$500 million "
        "multi-tenant semiconductor manufacturing facility proposal selected for Canada's Investment "
        "Summit Prospectus; four months earlier, it closed C$275 million in financing and brought "
        "total capital raised to C$475 million. The Vancouver company is commercializing optically "
        "linked silicon-spin-qubit computers and networks, growing its team from roughly 170 toward "
        "more than 200 people, and planning domestic design, fabrication, packaging, and test capacity. "
        "Inference: concurrent product, process, defence, supplier, packaging, validation, and factory "
        "decisions create immediate configuration, requirements-to-test, and industrialization pressure."
    ),
    "why_relevant": (
        "Teamcenter can control quantum-system BOMs, revisions, process baselines, and partner changes; "
        "Polarion can connect demanding quantum and defence requirements to tests and defects. Simcenter "
        "can support thermal and system-level validation, while Tecnomatix can evaluate facility layouts "
        "and process flows before major capital is committed. The practical outcome is a faster scale-up "
        "with fewer configuration escapes and more defensible verification evidence for customers and investors."
    ),
    "qualification_status": "qualified",
    "opportunity_score": 96,
    "manufacturing_fit_score": 98,
    "trigger_score": 98,
    "solution_fit_score": 96,
    "evidence_quality_score": 99,
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
                | (func.lower(CompanyRecord.company_name) == "photonic inc.")
            )
        ).all()
    if prior_identity:
        raise RuntimeError(f"Unexpected existing Photonic identity before first persistence: {prior_identity}")

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
        raise RuntimeError("Photonic persistence returned no company")

    keyword_row = database.record_keyword_company(
        PROSPECT["keyword_id"],
        PROSPECT["company_name"],
        PROSPECT["company_domain"],
        source_url=PROSPECT["keyword_source_url"],
        source_title=PROSPECT["keyword_source_title"],
        source_publisher=PROSPECT["keyword_source_publisher"],
        signal_label=PROSPECT["signal_label"],
        signal_date=PROSPECT["signal_date"],
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
        raise RuntimeError("Could not link Photonic to keyword 8")

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
                    "company_id": company.id,
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
