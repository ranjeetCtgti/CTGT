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


OSCP = {
    "company_name": "OSCP",
    "company_domain": "oscp.com",
    "company_url": "https://www.oscp.com/",
    "location": "Montreal, Quebec, Canada",
    "industry": "Photonic inertial sensors and navigation hardware manufacturing",
    "products": ["Teamcenter", "Polarion", "Simcenter"],
    "identity": CompanyIdentityEvidence(
        official_name="OSCP",
        official_website_url="https://www.oscp.com/",
        corroborating_urls=(
            "https://betakit.com/oscp-closes-6-million-usd-series-a-round-to-power-navigation-without-gps/",
        ),
    ),
    "signals": [
        {
            "source_url": "https://betakit.com/oscp-closes-6-million-usd-series-a-round-to-power-navigation-without-gps/",
            "source_title": "OSCP closes $6-million USD Series A round to power navigation without GPS",
            "source_publisher": "BetaKit",
            "signal_date": datetime(2026, 10, 2, tzinfo=timezone.utc),
            "reason": (
                "On October 2, 2026, BetaKit reported that Montreal-based OSCP closed a US$6 million "
                "(C$8.6 million) Series A led by New Science Ventures to scale production of its ITAR-free "
                "photonic inertial measurement units and develop additional navigation sensors. OSCP's sensors "
                "are intended to let autonomous aerospace and defence platforms navigate when GPS is unavailable "
                "or jammed. Inference: converting advanced photonics into repeatable tactical-grade production "
                "creates configuration, supplier, calibration, verification, and qualification-evidence pressure. "
                "Teamcenter can govern sensor variants and released BOMs, Polarion can connect requirements and "
                "test evidence, and Simcenter can support multiphysics and system validation; the newly funded "
                "production ramp makes this a current buying window."
            ),
            "pain": (
                "Must scale tactical-grade photonic sensor production while controlling variants, suppliers, "
                "calibration, verification, and defence/aerospace qualification evidence."
            ),
            "expansion": (
                "Closed a US$6 million Series A to expand Montreal production and accelerate next-generation "
                "photonic navigation sensors."
            ),
        },
        {
            "source_url": "https://www.oscp.com/news/oscp-closes-series-financing-led-new-science-ventures",
            "source_title": "OSCP Closes Series A Financing Led by New Science Ventures",
            "source_publisher": "OSCP",
            "signal_date": datetime(2026, 10, 1, tzinfo=timezone.utc),
            "reason": (
                "On October 1, 2026, OSCP announced Series A financing to scale production of ITAR-free photonic "
                "inertial measurement units in Montreal, grow engineering and sales teams, and bring its next "
                "sensor generation to market. The company also identified recent NavigationGate, ArduPilot and "
                "ROS 2 integration work and qualification for Canada's Defence Drone Initiative Marketplace. "
                "Inference: parallel product, interface, production, and defence-market expansion increases "
                "requirements, revision, test, and supplier coordination. Teamcenter, Polarion, and Simcenter "
                "address those controls while the financed scale-up and new integrations are underway."
            ),
            "pain": (
                "Parallel sensor-generation, software-interface, defence-qualification, and production work "
                "requires controlled product structures, requirements, and validation evidence."
            ),
            "expansion": (
                "Financing supports Montreal production scale-up, engineering growth, and commercialization of "
                "the next photonic sensor generation."
            ),
        },
    ],
    "keyword_ids": [8, 9, 10, 13, 14],
    "signal_label": "US$6M Series A funds Montreal photonic-IMU production scale-up",
    "challenge_summary": (
        "On October 1-2, 2026, Montreal-based OSCP closed a US$6 million (C$8.6 million) Series A led by "
        "New Science Ventures to scale production of ITAR-free photonic inertial measurement units and develop "
        "next-generation navigation sensors for GPS-denied autonomous and defence platforms. OSCP also cited "
        "NavigationGate, ArduPilot and ROS 2 integrations plus Defence Drone Initiative Marketplace qualification. "
        "Inference: the funded ramp creates immediate sensor-variant, supplier, calibration, verification, and "
        "qualification-evidence complexity."
    ),
    "why_relevant": (
        "Teamcenter can govern sensor configurations, released BOMs, suppliers, and changes as production grows. "
        "Polarion can trace platform and defence requirements into calibration and verification evidence, while "
        "Simcenter can support sensor and system-level validation. The financing, production expansion, and recent "
        "platform integrations make the need current rather than speculative."
    ),
    "qualification_status": "qualified",
    "opportunity_score": 92,
    "manufacturing_fit_score": 92,
    "trigger_score": 96,
    "solution_fit_score": 93,
    "evidence_quality_score": 97,
}


OBJEXIS = {
    "company_name": "OBJEXIS AI Inc.",
    "company_domain": "objexis.ai",
    "company_url": "https://www.objexis.ai/",
    "location": "Oakville, Ontario, Canada",
    "industry": "Modular uncrewed aircraft, avionics, and counter-UAS manufacturing",
    "products": ["Teamcenter", "Polarion", "Capital"],
    "identity": CompanyIdentityEvidence(
        official_name="OBJEXIS AI Inc.",
        official_website_url="https://www.objexis.ai/",
        corroborating_urls=(
            "https://canadabuys.canada.ca/en/tender-opportunities/contract-history/cw2467923-000",
            "https://www.pm.gc.ca/en/news/news-releases/2026/09/10/canada-and-ukraine-scale-drone-production-build-canadas-defence",
        ),
    ),
    "signals": [
        {
            "source_url": "https://canadabuys.canada.ca/en/tender-opportunities/contract-history/cw2467923-000",
            "source_title": "Contract history CW2467923-000 — Low Cost Uncrewed Aerial System",
            "source_publisher": "CanadaBuys / Government of Canada",
            "signal_date": datetime(2026, 9, 10, tzinfo=timezone.utc),
            "reason": (
                "On September 10, 2026, CanadaBuys recorded a C$612,400 National Defence contract "
                "(W8703-270094/CW2467923) awarded to OBJEXIS AI Inc. for a low-cost uncrewed aerial system, "
                "including spares, support equipment, documentation, training, and sustainment through September "
                "2031. OBJEXIS's official site verifies Oakville development of modular Canadian-built UAS, "
                "interceptors, avionics, and payload systems. Inference: delivery and long-tail sustainment create "
                "airframe/payload configuration, electrical-interface, requirements, documentation, training, and "
                "serialized-support complexity. Teamcenter, Polarion, and Capital fit those controls; the awarded "
                "contract creates an immediate program baseline and delivery clock."
            ),
            "pain": (
                "Must control modular aircraft, payload and avionics configurations together with contract "
                "requirements, documentation, spares, training, and sustainment records through 2031."
            ),
            "expansion": (
                "Won a C$612,400 National Defence contract for a low-cost UAS plus spares, support equipment, "
                "documentation, training, and sustainment."
            ),
        }
    ],
    "keyword_ids": [7, 9, 13, 14],
    "signal_label": "C$612.4K defence UAS contract includes sustainment through 2031",
    "challenge_summary": (
        "On September 10, 2026, National Defence awarded Oakville-based OBJEXIS AI a C$612,400 contract "
        "(W8703-270094/CW2467923) for a low-cost uncrewed aerial system, spares, support equipment, documentation, "
        "training, and sustainment through September 2031. OBJEXIS develops Canadian-built modular aircraft, "
        "interceptors, avionics, and payload systems. Inference: the award creates immediate configuration, "
        "electrical-interface, requirements, documentation, and serialized-sustainment complexity."
    ),
    "why_relevant": (
        "Teamcenter can control aircraft, payload, spares, and support-equipment baselines across delivery and "
        "sustainment. Polarion can connect defence requirements to test evidence, defects, and acceptance records, "
        "while Capital can govern avionics and electrical architectures. The contract award fixes a delivery and "
        "support baseline now, making disciplined product and requirements control urgent."
    ),
    "qualification_status": "qualified",
    "opportunity_score": 94,
    "manufacturing_fit_score": 96,
    "trigger_score": 98,
    "solution_fit_score": 95,
    "evidence_quality_score": 98,
}


DRAGANFLY = {
    "company_name": "Draganfly Inc.",
    "company_domain": "draganfly.com",
    "company_url": "https://draganfly.com/",
    "location": "Saskatoon, Saskatchewan and Burnaby, British Columbia, Canada",
    "industry": "Uncrewed aircraft and autonomous systems manufacturing",
    "products": ["Teamcenter", "Polarion", "Opcenter"],
    "identity": CompanyIdentityEvidence(
        official_name="Draganfly Inc.",
        official_website_url="https://draganfly.com/",
        corroborating_urls=(
            "https://www.pm.gc.ca/en/news/news-releases/2026/09/10/canada-and-ukraine-scale-drone-production-build-canadas-defence",
        ),
    ),
    "signals": [
        {
            "source_url": "https://www.sec.gov/Archives/edgar/data/1786286/000149315226042365/ex99-1.htm",
            "source_title": "Draganfly Awarded Five-Year Canadian Defence Contract for Unmanned Aircraft Systems",
            "source_publisher": "Draganfly / U.S. Securities and Exchange Commission",
            "signal_date": datetime(2026, 9, 11, tzinfo=timezone.utc),
            "reason": (
                "On September 11, 2026, Draganfly disclosed a five-year Canadian defence contract with an initial "
                "firm commitment for 100 uncrewed aircraft systems and options for up to 4,900 more, representing "
                "up to C$24.25 million of optional purchases. The program builds on Draganfly's Canadian engineering "
                "and production footprint and requires configurable aircraft, payloads, support, training, and "
                "sustainment. Inference: an initial delivery plus a potential fiftyfold option ramp increases BOM, "
                "revision, supplier, test, serialized-quality, and capacity-control pressure. Teamcenter, Polarion, "
                "and Opcenter directly address those needs while the five-year procurement window is open."
            ),
            "pain": (
                "Must convert an initial 100-system defence order into a controlled program capable of scaling to "
                "5,000 systems while preserving configuration, test, quality, and sustainment records."
            ),
            "expansion": (
                "Received an initial 100-UAS commitment with options for up to 4,900 additional systems and "
                "C$24.25 million in optional purchases over five years."
            ),
        }
    ],
    "keyword_ids": [7, 9, 13, 14],
    "signal_label": "Five-year defence award starts at 100 UAS with options up to 5,000",
    "challenge_summary": (
        "On September 11, 2026, Draganfly disclosed a five-year Canadian defence contract with an initial firm "
        "commitment for 100 uncrewed aircraft systems and options for up to 4,900 more, representing up to "
        "C$24.25 million of optional purchases. Inference: moving from the first delivery to a potential 5,000-system "
        "program creates immediate platform-variant, BOM/change, supplier, test, serialized-quality, capacity, and "
        "sustainment pressure."
    ),
    "why_relevant": (
        "Teamcenter can govern aircraft and payload configurations, released BOMs, suppliers, and sustainment "
        "structures. Polarion can connect defence requirements to verification and acceptance evidence, while "
        "Opcenter can provide serialized production and quality genealogy. The initial order and large option "
        "ceiling create a near-term need to establish scalable controls before volume expands."
    ),
    "qualification_status": "qualified",
    "opportunity_score": 96,
    "manufacturing_fit_score": 98,
    "trigger_score": 99,
    "solution_fit_score": 96,
    "evidence_quality_score": 99,
}


PROSPECTS = (OSCP, OBJEXIS, DRAGANFLY)
NEW_DOMAINS = {"oscp.com", "objexis.ai"}

RESULT_CARDS = {
    1: 0, 2: 57, 3: 0, 4: 27, 5: 41, 7: 0, 8: 50, 9: 50, 10: 50,
    11: 50, 12: 40, 13: 50, 14: 50, 15: 50, 16: 50,
}

DEEP_REVIEW = {
    1: (0, 0, 0),
    2: (4, 3, 1),
    3: (2, 1, 1),
    4: (3, 1, 2),
    5: (3, 0, 3),
    7: (3, 0, 1),
    8: (2, 0, 1),
    9: (3, 0, 0),
    10: (2, 0, 1),
    11: (2, 0, 2),
    12: (2, 0, 2),
    13: (3, 0, 0),
    14: (5, 1, 1),
    15: (2, 1, 1),
    16: (1, 0, 1),
}


def make_signal(prospect: dict, evidence: dict) -> ExtractedSignal:
    return ExtractedSignal(
        company_name=prospect["company_name"],
        company_domain=prospect["company_domain"],
        company_url=prospect["company_url"],
        location=prospect["location"],
        industry=prospect["industry"],
        company_industry=prospect["industry"],
        software=prospect["products"],
        signal_type="news",
        signal_source="news",
        pain_signals=[evidence["pain"]],
        expansion_signals=[evidence["expansion"]],
        raw_score=prospect["opportunity_score"],
        confidence=prospect["evidence_quality_score"] / 100,
        reason=evidence["reason"],
        source_url=evidence["source_url"],
        source_title=evidence["source_title"],
        detected_at=evidence["signal_date"],
    )


def publish(database: Database, prospect: dict) -> dict:
    saved_evidence = []
    company = None
    for evidence in prospect["signals"]:
        signal = make_signal(prospect, evidence)
        verify_company_identity(signal, prospect["identity"])
        saved, company = database.persist_verified_signal(signal, prospect["identity"])
        saved_evidence.append(
            {
                "source_url": evidence["source_url"],
                "created": saved.created,
                "duplicate_url": saved.duplicate_url,
            }
        )
    if company is None:
        raise RuntimeError(f"Persistence returned no company for {prospect['company_name']}")

    primary = prospect["signals"][0]
    keyword_rows = []
    for keyword_id in prospect["keyword_ids"]:
        row = database.record_keyword_company(
            keyword_id,
            prospect["company_name"],
            prospect["company_domain"],
            source_url=primary["source_url"],
            source_title=primary["source_title"],
            source_publisher=primary["source_publisher"],
            signal_label=prospect["signal_label"],
            signal_date=primary["signal_date"],
            challenge_summary=prospect["challenge_summary"],
            why_relevant=prospect["why_relevant"],
            recommended_products=prospect["products"],
            qualification_status=prospect["qualification_status"],
            opportunity_score=prospect["opportunity_score"],
            manufacturing_fit_score=prospect["manufacturing_fit_score"],
            trigger_score=prospect["trigger_score"],
            solution_fit_score=prospect["solution_fit_score"],
            evidence_quality_score=prospect["evidence_quality_score"],
            seen_at=RUN_AT,
        )
        if row is None:
            raise RuntimeError(f"Could not link {prospect['company_name']} to keyword {keyword_id}")
        keyword_rows.append(
            {
                "keyword_id": keyword_id,
                "result_id": row.id,
                "qualification_status": row.qualification_status,
                "opportunity_score": row.opportunity_score,
            }
        )

    with database.session() as session:
        company_id = session.scalar(
            select(CompanyRecord.id).where(
                func.lower(CompanyRecord.company_domain) == prospect["company_domain"].lower()
            )
        )
    if company_id is None:
        raise RuntimeError(f"Could not resolve company id for {prospect['company_name']}")

    return {
        "company_id": company_id,
        "company_name": company.company_name,
        "company_domain": company.company_domain,
        "signal_count": company.signal_count,
        "evidence": saved_evidence,
        "keywords": keyword_rows,
    }


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
        existing_new_domains = session.execute(
            select(CompanyRecord.id, CompanyRecord.company_name, CompanyRecord.company_domain)
            .where(func.lower(CompanyRecord.company_domain).in_(NEW_DOMAINS))
        ).all()
        draganfly = session.scalar(
            select(CompanyRecord).where(func.lower(CompanyRecord.company_domain) == "draganfly.com")
        )
    if existing_new_domains:
        raise RuntimeError(f"New-candidate domains already exist: {existing_new_domains}")
    if draganfly is None or draganfly.company_name != "Draganfly Inc.":
        raise RuntimeError("Existing Draganfly identity did not match the verified canonical record")

    persisted = [publish(database, prospect) for prospect in PROSPECTS]

    published = {keyword_id: 0 for keyword_id in keywords_before}
    watchlist = {keyword_id: 0 for keyword_id in keywords_before}
    for prospect in PROSPECTS:
        for keyword_id in prospect["keyword_ids"]:
            if prospect["qualification_status"] == "qualified":
                published[keyword_id] += 1
            else:
                watchlist[keyword_id] += 1

    for keyword_id in sorted(keywords_before):
        result_count = published[keyword_id] + watchlist[keyword_id]
        if database.record_keyword_search(keyword_id, result_count=result_count, error=None) is None:
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
            .group_by(KeywordCompanyResultRecord.keyword_id, KeywordCompanyResultRecord.company_id)
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
                "persisted": persisted,
                "new_company_ids": [row["company_id"] for row in persisted if row["company_domain"] in NEW_DOMAINS],
                "updated_company_ids": [row["company_id"] for row in persisted if row["company_domain"] == "draganfly.com"],
                "keyword_audits": [
                    {
                        "id": keyword_id,
                        "keyword": keywords_after[keyword_id].keyword,
                        "search_count_before": keywords_before[keyword_id].search_count,
                        "search_count_after": keywords_after[keyword_id].search_count,
                        "result_cards": RESULT_CARDS[keyword_id],
                        "deep_candidates_reviewed": DEEP_REVIEW[keyword_id][0],
                        "rejected_before_persistence": DEEP_REVIEW[keyword_id][1],
                        "duplicates_or_existing_skipped": DEEP_REVIEW[keyword_id][2],
                        "qualified_published": published[keyword_id],
                        "watchlist_published": watchlist[keyword_id],
                        "last_error": keywords_after[keyword_id].last_error,
                    }
                    for keyword_id in sorted(keywords_after)
                ],
                "coverage": {
                    "result_cards_total": sum(RESULT_CARDS.values()),
                    "lookbacks": ["30-day", "180-day", "365-day ongoing-signal fallback"],
                    "query_families": [
                        "general web/news", "government funding/contracts", "specialist trade publications",
                        "accelerators/investors/university spinouts", "associations/directories",
                        "company press/hiring/product/facility pages",
                    ],
                    "mandatory_direct_startup_gallery": "15/15 checked; query parameter returned the same unfiltered gallery; no publishable lead",
                    "mandatory_direct_x": "15/15 attempted; ERR_CERT_AUTHORITY_INVALID; not bypassed",
                    "mandatory_direct_betakit": "15/15 checked; OSCP lead discovered and independently verified",
                    "mandatory_direct_ngen": "15/15 checked; direct search route returned 404; indexed NGen project/funding searches used",
                    "spaceq_aiac": "Direct checks completed for keywords 1, 7, 9, 10, 13, and 14; AIAC keyword 9 returned two directory results, others zero",
                    "additional_sources": [
                        "CanadaBuys", "Canada.ca/PMO", "SEC filings", "ventureLAB", "BDC Capital",
                        "APMA", "CADSI", "Aero Montreal", "DAIR Aerospace", "OVIN",
                        "Oakville Chamber of Commerce", "Skies Magazine", "Canadian Manufacturing",
                        "PLANT", "Electric Autonomy Canada", "Marine Log", "Naval News",
                    ],
                    "warnings": [
                        "Google degraded to header-only results on some searches; Bing rotation used",
                        "Bing human-verification interstitial appeared on some government searches; not bypassed",
                        "Keywords 1, 3, and 7 returned zero captured cards in the primary family pass; mandatory direct and specialist checks still completed",
                    ],
                },
                "held": [
                    {
                        "company": "Rheinmetall Canada Inc.",
                        "reason": "identity_mismatch: PostgreSQL stores rheinmetall.ca while the verified official canonical domain is rheinmetall.com",
                    }
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
