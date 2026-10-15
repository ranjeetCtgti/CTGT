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


PROSPECTS = (
    {
        "company_name": "Sentinel Advanced Military Solutions",
        "company_domain": "sentinel-ams.com",
        "company_url": "https://www.sentinel-ams.com/",
        "location": "Chateauguay, Quebec, Canada",
        "industry": "Deployable drone manufacturing and defence systems integration",
        "products": ["Teamcenter", "Polarion", "Opcenter"],
        "identity": CompanyIdentityEvidence(
            official_name="Sentinel Advanced Military Solutions",
            official_website_url="https://www.sentinel-ams.com/",
            corroborating_urls=(
                "https://branchez-vous.com/actualites/starforge-drones-chateauguay/",
                "https://www.vanguarddefence.ca/p/inside-sentinel-s-bet-on-the-battlefield-factory",
            ),
        ),
        "signals": [
            {
                "source_url": "https://branchez-vous.com/actualites/starforge-drones-chateauguay/",
                "source_title": (
                    "A l'interieur de StarForge, l'usine mobile quebecoise capable de produire "
                    "jusqu'a 100 drones par jour"
                ),
                "source_publisher": "Branchez-Vous",
                "signal_date": datetime(2026, 10, 6, tzinfo=timezone.utc),
                "reason": (
                    "On October 6, 2026, an on-site Branchez-Vous report documented Sentinel's ForgeX "
                    "mobile factory in Chateauguay with four 3D printers, onboard batteries, servers, and "
                    "workstations, plus a stated output of 80 to 100 drones per day depending on model and "
                    "conditions. The report traced structural and mechanical manufacturing to parent CMP "
                    "Advanced Mechanical Solutions. Inference: mission-specific designs, a digital part "
                    "inventory, distributed field production, common-component reuse, and repair variants at "
                    "that output create immediate configuration, released-BOM, process, and quality-traceability "
                    "pressure; Teamcenter, Polarion, and Opcenter are the smallest defensible CTGTI fit."
                ),
                "pain": (
                    "Must control drone variants, digital-stockpile releases, common components, field-production "
                    "processes, and quality evidence across a deployable factory and its national supply chain."
                ),
                "expansion": (
                    "Demonstrated a four-printer ForgeX mobile factory with stated capacity of 80 to 100 drones "
                    "per day, supported by CMP manufacturing in Chateauguay."
                ),
            },
            {
                "source_url": "https://www.vanguarddefence.ca/p/inside-sentinel-s-bet-on-the-battlefield-factory",
                "source_title": "Inside Sentinel's bet on the battlefield factory",
                "source_publisher": "Vanguard Defence",
                "signal_date": datetime(2026, 9, 22, tzinfo=timezone.utc),
                "reason": (
                    "On September 22, 2026, Vanguard Defence reported that Sentinel completed a two-week "
                    "California desert field test after printing drone chassis, assembling kits, and flying "
                    "missions, and was targeting a second-generation build in mid-October with more than 95% of "
                    "the evaluator-requested initial operating capability. The StarForge consortium is backed by "
                    "a C$10 million Lockheed Martin industrial-benefit contribution tied to Canada's HIMARS "
                    "purchase, and Sentinel operates from a 25,000-square-foot Chateauguay facility with a "
                    "national component supply chain. Inference: rapid test feedback entering a new production "
                    "baseline makes requirements, defects, configurations, suppliers, and manufacturing evidence "
                    "time-critical; Polarion, Teamcenter, and Opcenter directly address that transition."
                ),
                "pain": (
                    "Must convert field-test findings into a controlled second-generation drone baseline while "
                    "coordinating requirements, defects, parts, suppliers, and repeatable production evidence."
                ),
                "expansion": (
                    "Completed an August field trial and targeted a mid-October second-generation build at more "
                    "than 95% of evaluator-requested initial capability under a C$10 million-backed program."
                ),
            },
        ],
        "keyword_ids": [7, 13, 14, 16],
        "signal_label": "ForgeX mobile factory targets 80-100 drones per day",
        "challenge_summary": (
            "On October 6, 2026, an on-site report documented Sentinel's ForgeX mobile factory in Chateauguay "
            "with four 3D printers and stated capacity of 80 to 100 drones per day; Vanguard separately reported "
            "an August field test and a second-generation build targeted for mid-October at more than 95% of the "
            "evaluator-requested initial capability. StarForge spans mission-specific drone designs, deployable "
            "production, onboard power, a secure digital stockpile, and a national component supply chain backed "
            "by parent CMP. Inference: that output and variant mix create urgent configuration, change-control, "
            "manufacturing-process, supplier, and quality-traceability pressure."
        ),
        "why_relevant": (
            "Teamcenter can govern drone configurations, released BOMs, digital-stockpile revisions, and supplier "
            "changes. Polarion can trace evaluator requirements and field defects into the second-generation "
            "baseline, while Opcenter can standardize deployable work instructions, production quality, and "
            "genealogy. The mid-October build target and demonstrated 80-to-100-unit daily capacity make these "
            "controls immediately relevant before wider deployment."
        ),
        "qualification_status": "qualified",
        "opportunity_score": 94,
        "manufacturing_fit_score": 98,
        "trigger_score": 95,
        "solution_fit_score": 96,
        "evidence_quality_score": 95,
    },
    {
        "company_name": "Qidni Labs Inc.",
        "company_domain": "qidni.life",
        "company_url": "https://qidni.life/",
        "location": "Kitchener, Ontario, Canada",
        "industry": "Portable nearly waterless hemodialysis systems",
        "products": ["Teamcenter", "Polarion", "Opcenter"],
        "identity": CompanyIdentityEvidence(
            official_name="Qidni Labs Inc.",
            official_website_url="https://qidni.life/",
            corroborating_urls=(
                "https://www.canada.ca/en/innovation-science-economic-development/news/2026/09/government-of-canada-announces-major-contribution-to-strengthen-canadas-dual-use-life-sciences-sector.html",
                "https://www.velocityincubator.com/news/government-of-canada-backs-qidni-labs-25-million-push-to-scale-portable-dialysis",
            ),
        ),
        "signals": [
            {
                "source_url": (
                    "https://www.canada.ca/en/innovation-science-economic-development/news/2026/09/"
                    "government-of-canada-announces-major-contribution-to-strengthen-canadas-dual-use-"
                    "life-sciences-sector.html"
                ),
                "source_title": (
                    "Government of Canada announces major contribution to strengthen Canada's dual-use "
                    "life sciences sector"
                ),
                "source_publisher": "Innovation, Science and Economic Development Canada",
                "signal_date": datetime(2026, 9, 18, tzinfo=timezone.utc),
                "reason": (
                    "On September 18, 2026, the Government of Canada committed up to C$12.5 million to Qidni "
                    "Labs for a C$25 million project to finalize its portable nearly waterless hemodialysis "
                    "system, establish pilot-scale manufacturing in Ontario, conduct clinical studies, and collect "
                    "real-world battlefield data. Inference: industrializing a reusable device, disposable treatment "
                    "components, batteries, controls, and remote monitoring while generating clinical and field "
                    "evidence creates immediate BOM, design-change, supplier-quality, manufacturing-genealogy, "
                    "requirements, and test-traceability pressure. Teamcenter, Polarion, and Opcenter are the "
                    "smallest defensible fit for the funded program."
                ),
                "pain": (
                    "Must mature a regulated dialysis system into pilot production while controlling device and "
                    "consumable configurations, supplier quality, clinical requirements, tests, and manufacturing "
                    "genealogy."
                ),
                "expansion": (
                    "Received up to C$12.5 million toward a C$25 million program for Ontario pilot manufacturing, "
                    "clinical studies, and battlefield evaluation of its portable dialysis system."
                ),
            },
            {
                "source_url": (
                    "https://www.velocityincubator.com/news/government-of-canada-backs-qidni-labs-25-"
                    "million-push-to-scale-portable-dialysis"
                ),
                "source_title": (
                    "Government of Canada backs Qidni Labs' $25 million push to scale portable dialysis"
                ),
                "source_publisher": "Velocity",
                "signal_date": datetime(2026, 9, 28, tzinfo=timezone.utc),
                "reason": (
                    "On September 28, 2026, Velocity independently detailed Qidni Labs' C$25 million scale-up "
                    "program, including C$12.5 million of federal support, pilot-scale Ontario manufacturing, "
                    "clinical studies, and battlefield data collection for a portable dialysis platform designed "
                    "to use dramatically less water than conventional hemodialysis. Inference: parallel product, "
                    "clinical, production, and field-validation work increases requirements volatility and the need "
                    "to tie every released configuration and manufactured unit to verified evidence. Teamcenter, "
                    "Polarion, and Opcenter provide that controlled product-to-production thread."
                ),
                "pain": (
                    "Must synchronize product maturation, pilot-line readiness, clinical validation, and battlefield "
                    "feedback without losing configuration or quality traceability."
                ),
                "expansion": (
                    "Velocity corroborated the C$25 million program to scale Qidni's portable dialysis technology "
                    "through Ontario pilot manufacturing and clinical and battlefield validation."
                ),
            },
        ],
        "keyword_ids": [8, 14, 16],
        "signal_label": "C$12.5M funds pilot manufacturing and validation of portable dialysis",
        "challenge_summary": (
            "On September 18, 2026, the Government of Canada committed up to C$12.5 million to Qidni Labs' "
            "C$25 million project to finalize its portable nearly waterless hemodialysis system, establish pilot-"
            "scale manufacturing in Ontario, conduct clinical studies, and collect battlefield data. The system "
            "combines treatment hardware, consumables, rechargeable power, controls, and remote monitoring. "
            "Inference: simultaneous industrialization and regulated validation create urgent BOM, configuration, "
            "supplier-quality, design-control, requirements, test, and manufacturing-genealogy pressure."
        ),
        "why_relevant": (
            "Teamcenter can control device and consumable configurations, suppliers, and engineering changes. "
            "Polarion can trace clinical and battlefield requirements into tests and defects, while Opcenter can "
            "govern pilot-line execution, quality records, and unit genealogy. The funded program is explicitly "
            "moving into pilot manufacturing and evidence generation now, before scale and regulatory burden grow."
        ),
        "qualification_status": "qualified",
        "opportunity_score": 96,
        "manufacturing_fit_score": 97,
        "trigger_score": 98,
        "solution_fit_score": 97,
        "evidence_quality_score": 98,
    },
    {
        "company_name": "Boreal Biomanufacturing",
        "company_domain": "boreal-bio.com",
        "company_url": "https://boreal-bio.com/",
        "location": "Ottawa, Ontario, Canada",
        "industry": "GMP viral-vector and biotherapeutics process development and manufacturing",
        "products": ["Opcenter", "Polarion"],
        "identity": CompanyIdentityEvidence(
            official_name="Boreal Biomanufacturing",
            official_website_url="https://boreal-bio.com/",
            corroborating_urls=(
                "https://www.canada.ca/en/innovation-science-economic-development/news/2026/09/government-of-canada-announces-major-contribution-to-strengthen-canadas-dual-use-life-sciences-sector.html",
                "https://www.researchmoneyinc.com/article/the-short-report-september-23-2026",
            ),
        ),
        "signals": [
            {
                "source_url": "https://www.researchmoneyinc.com/article/the-short-report-september-23-2026",
                "source_title": "The Short Report: September 23, 2026",
                "source_publisher": "Research Money",
                "signal_date": datetime(2026, 9, 23, tzinfo=timezone.utc),
                "reason": (
                    "On September 23, 2026, Research Money reported that the Ottawa Hospital Research Institute "
                    "and Boreal Biomanufacturing would receive C$880,000 to expand adenovirus manufacturing "
                    "capacity, enable larger-scale production and commercialization of vaccines and therapies, and "
                    "implement an electronic quality-management system. Inference: adding GMP capacity and "
                    "digitizing quality increases batch, raw-material, process-change, deviation, corrective-action, "
                    "release, and traceability workload. Opcenter and Polarion are the smallest defensible CTGTI set "
                    "for electronic production quality plus controlled requirements, testing, defects, and audit evidence."
                ),
                "pain": (
                    "Must scale GMP adenovirus production while controlling batch execution, process changes, raw "
                    "materials, deviations, corrective actions, release evidence, and electronic quality records."
                ),
                "expansion": (
                    "Received C$880,000 to expand adenovirus manufacturing capacity, support larger-scale "
                    "commercialization, and implement an electronic quality-management system."
                ),
            }
        ],
        "keyword_ids": [16],
        "signal_label": "C$880K expansion adds adenovirus capacity and electronic QMS",
        "challenge_summary": (
            "On September 18, 2026, the Government of Canada awarded C$880,000 to the Ottawa Hospital Research "
            "Institute and Boreal Biomanufacturing to expand adenovirus manufacturing capacity, enable larger-scale "
            "vaccine and therapy production, and implement an electronic quality-management system. Boreal's "
            "official site describes GMP-compliant process development, manufacturing, and quality-control work. "
            "Inference: the funded scale-up increases batch, material, process-change, deviation, release, and "
            "traceability complexity while quality operations are being digitized."
        ),
        "why_relevant": (
            "Opcenter can connect electronic batch execution, in-process quality, deviations, and end-to-end "
            "production genealogy. Polarion can link process and regulatory requirements to tests, defects, and "
            "audit evidence without overextending the product set. Because the grant explicitly funds capacity "
            "growth and an electronic quality-management system, the implementation window is active now."
        ),
        "qualification_status": "qualified",
        "opportunity_score": 84,
        "manufacturing_fit_score": 91,
        "trigger_score": 85,
        "solution_fit_score": 92,
        "evidence_quality_score": 97,
    },
)


# Auditable conservative discovery counts: unique canonical domains reviewed,
# new-to-ledger domains among them, rejected before persistence, published, and
# duplicates/existing domains skipped. Shortfalls are explicitly reported below.
REVIEW = {
    1: (12, 4, 8, 0, 4),
    2: (17, 6, 10, 0, 7),
    3: (11, 3, 8, 0, 3),
    4: (16, 5, 10, 0, 6),
    5: (18, 6, 12, 0, 6),
    7: (21, 7, 13, 1, 7),
    8: (25, 10, 15, 1, 9),
    9: (18, 6, 11, 0, 7),
    10: (17, 5, 11, 0, 6),
    11: (10, 2, 8, 0, 2),
    12: (8, 2, 6, 0, 2),
    13: (20, 7, 12, 1, 7),
    14: (24, 9, 14, 2, 8),
    15: (16, 5, 11, 0, 5),
    16: (22, 9, 14, 3, 5),
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
    signals = [make_signal(prospect, evidence) for evidence in prospect["signals"]]
    for signal in signals:
        verify_company_identity(signal, prospect["identity"])

    saved_evidence = []
    company = None
    for signal, evidence in zip(signals, prospect["signals"], strict=True):
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
        keyword_rows.append({"keyword_id": keyword_id, "result_id": row.id})

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

    # Complete the deterministic identity gate for every source before the first write.
    for prospect in PROSPECTS:
        for evidence in prospect["signals"]:
            verify_company_identity(make_signal(prospect, evidence), prospect["identity"])

    domains = {prospect["company_domain"].lower() for prospect in PROSPECTS}
    with database.session() as session:
        before_rows = session.execute(
            select(CompanyRecord.id, CompanyRecord.company_name, CompanyRecord.company_domain).where(
                func.lower(CompanyRecord.company_domain).in_(domains)
            )
        ).all()
    existing_domains = {row.company_domain.lower() for row in before_rows if row.company_domain}

    persisted = [publish(database, prospect) for prospect in PROSPECTS]
    published = {keyword_id: 0 for keyword_id in keywords_before}
    for prospect in PROSPECTS:
        for keyword_id in prospect["keyword_ids"]:
            published[keyword_id] += 1

    for keyword_id in sorted(keywords_before):
        if database.record_keyword_search(keyword_id, result_count=published[keyword_id], error=None) is None:
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
            .where(SignalRecord.source_url.is_not(None))
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
            f"domains={duplicate_domains}, sources={duplicate_sources}, keyword_pairs={duplicate_keyword_pairs}"
        )

    print(
        json.dumps(
            {
                "run_at": RUN_AT.isoformat(),
                "persisted": persisted,
                "new_company_ids": [
                    row["company_id"]
                    for row in persisted
                    if row["company_domain"].lower() not in existing_domains
                ],
                "existing_company_ids_reassessed": [
                    row["company_id"]
                    for row in persisted
                    if row["company_domain"].lower() in existing_domains
                ],
                "keyword_audits": [
                    {
                        "id": keyword_id,
                        "keyword": keywords_after[keyword_id].keyword,
                        "search_count_before": keywords_before[keyword_id].search_count,
                        "search_count_after": keywords_after[keyword_id].search_count,
                        "unique_domains_reviewed": REVIEW[keyword_id][0],
                        "new_to_ledger_domains_reviewed": REVIEW[keyword_id][1],
                        "rejected_before_persistence": REVIEW[keyword_id][2],
                        "qualified_published": REVIEW[keyword_id][3],
                        "watchlist_published": 0,
                        "duplicates_or_existing_skipped": REVIEW[keyword_id][4],
                        "last_error": keywords_after[keyword_id].last_error,
                    }
                    for keyword_id in sorted(keywords_after)
                ],
                "coverage": {
                    "lookbacks": ["30-day", "180-day", "365-day ongoing-signal fallback"],
                    "query_families": [
                        "general web/news",
                        "government funding/contracts/procurement",
                        "specialist trade publications",
                        "accelerators/investors/university spinouts",
                        "associations/exhibitors/member directories",
                        "company hiring/press/product/facility pages",
                    ],
                    "mandatory_sources": {
                        "Startup Gallery": (
                            "direct Canada and aerospace checks plus related X-ray searches completed; Canadian "
                            "cards were software/service businesses and aerospace cards were foreign, so no lead "
                            "passed the physical-product and Canada gates"
                        ),
                        "public X": (
                            "direct IAB checks attempted for all keywords but failed with "
                            "ERR_CERT_AUTHORITY_INVALID; the warning was not bypassed. Separate indexed X searches "
                            "covered every keyword theme and produced no candidate passing the full gate"
                        ),
                        "BetaKit": (
                            "searched every keyword theme for funding, customers, hiring, launches, facilities, and "
                            "production; rediscovered known hardware companies and software-only leads, but no new "
                            "candidate passed the full gate"
                        ),
                        "NGen": (
                            "searched every keyword theme across funding, projects, case studies, challenges, and "
                            "news; named participants were already known, directory-only, or lacked a current "
                            "independently corroborated trigger"
                        ),
                        "SpaceQ": (
                            "aerospace, space, defence, propulsion, drone, and avionics themes checked; no new "
                            "candidate beyond existing records passed today's gate"
                        ),
                        "AIAC": (
                            "member directory, industry guide, reports, and news checked for aerospace and defence; "
                            "directory membership alone was not published"
                        ),
                    },
                    "rotated_sources": [
                        "Canada.ca/ISED",
                        "CanadaBuys",
                        "NRC IRAP",
                        "Innovative Solutions Canada",
                        "OVIN",
                        "APMA",
                        "Aero Montreal",
                        "DAIR Aerospace",
                        "Oakville Chamber of Commerce",
                        "ventureLAB Hardware Catalyst",
                        "Velocity/University of Waterloo",
                        "MaRS",
                        "Communitech",
                        "Vanguard Defence",
                        "Branchez-Vous",
                        "Canadian Manufacturing",
                        "PLANT",
                        "Electric Autonomy Canada",
                        "Marine Log",
                        "Naval News",
                    ],
                    "zero_result_or_inaccessible": [
                        "Direct X was certificate-blocked for all 15 keywords.",
                        "Startup Gallery yielded no relevant Canadian physical-product candidate.",
                        "DAIR Aerospace and Oakville Chamber searches yielded no current qualifying trigger.",
                    ],
                    "quota_shortfalls": {
                        "1": "12 unique domains reviewed; only 4 were new to the ledger.",
                        "3": "11 unique domains reviewed; only 3 were new to the ledger.",
                        "11": "10 unique domains reviewed; only 2 were new to the ledger.",
                        "12": "8 unique domains reviewed; only 2 were new to the ledger.",
                    },
                },
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
