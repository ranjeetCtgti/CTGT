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
        "company_name": "TetraGen Robotics",
        "company_domain": "tetragen.ai",
        "company_url": "https://www.tetragen.ai/",
        "location": "Winnipeg, Manitoba, Canada",
        "industry": "Autonomous industrial welding robotics manufacturing",
        "products": ["Teamcenter", "Polarion", "Simcenter"],
        "identity": CompanyIdentityEvidence(
            official_name="TetraGen Robotics",
            official_website_url="https://www.tetragen.ai/",
            corroborating_urls=(
                "https://betakit.com/autonomous-welding-startup-tetragen-robotics-raises-1-8-million/",
            ),
        ),
        "signals": [
            {
                "source_url": "https://betakit.com/autonomous-welding-startup-tetragen-robotics-raises-1-8-million/",
                "source_title": "Autonomous welding startup TetraGen Robotics raises $1.8 million",
                "source_publisher": "BetaKit",
                "signal_date": datetime(2026, 8, 10, tzinfo=timezone.utc),
                "reason": (
                    "On August 10, 2026, BetaKit reported that Winnipeg-based TetraGen Robotics raised an "
                    "oversubscribed C$1.8 million seed round led by StepChange Capital to commercialize and deploy "
                    "more autonomous welding systems across North America and expand its engineering team. The "
                    "company's official site verifies that its manufactured robot cells combine industrial robots, "
                    "proprietary 3D vision, and AI path generation for high-mix welding in heavy equipment, mining, "
                    "trailers, structural steel, and defence manufacturing. Inference: scaling configurable robotic "
                    "cells into variable customer plants creates mechanical/electrical configuration, weld-process "
                    "validation, software-release, safety, and commissioning evidence pressure. Teamcenter can "
                    "govern cell variants and released BOMs, Polarion can trace deployment requirements and tests, "
                    "and Simcenter can support robot-cell and process validation while the funded rollout is active."
                ),
                "pain": (
                    "Must scale configurable autonomous welding cells across high-variation customer environments "
                    "while controlling hardware, vision, software, weld-process, safety, and commissioning evidence."
                ),
                "expansion": (
                    "Raised C$1.8 million to accelerate commercialization, expand engineering, and deploy more "
                    "autonomous welding systems across North America."
                ),
            }
        ],
        "keyword_ids": [2, 8, 13],
        "signal_label": "C$1.8M seed round funds autonomous-welding commercialization",
        "challenge_summary": (
            "On August 10, 2026, Winnipeg-based TetraGen Robotics disclosed an oversubscribed C$1.8 million seed "
            "round led by StepChange Capital to expand engineering and deploy more autonomous welding systems "
            "across North America. Its robot cells combine industrial robots, proprietary 3D vision, and AI path "
            "generation for high-mix welding. Inference: the rollout creates immediate hardware/software variant, "
            "weld-process validation, safety, commissioning, and field-change complexity."
        ),
        "why_relevant": (
            "Teamcenter can control robot-cell configurations, released BOMs, vision packages, and customer "
            "changes. Polarion can trace application and safety requirements into commissioning tests, while "
            "Simcenter can support cell, motion, and process validation. The funded commercialization push makes "
            "these controls useful before deployment volume and customer-specific variants multiply."
        ),
        "qualification_status": "qualified",
        "opportunity_score": 89,
        "manufacturing_fit_score": 94,
        "trigger_score": 92,
        "solution_fit_score": 90,
        "evidence_quality_score": 91,
    },
    {
        "company_name": "Femtum Inc.",
        "company_domain": "femtum.com",
        "company_url": "https://femtum.com/",
        "location": "Quebec City, Quebec, Canada",
        "industry": "Mid-infrared fiber laser manufacturing for semiconductor production",
        "products": ["Teamcenter", "Polarion", "Opcenter", "Simcenter"],
        "identity": CompanyIdentityEvidence(
            official_name="Femtum Inc.",
            official_website_url="https://femtum.com/",
            corroborating_urls=(
                "https://betakit.com/femtum-opens-new-quebec-city-factory-to-build-more-lasers-for-chipmakers/",
                "https://www.canada.ca/fr/developpement-economique-regions-quebec/nouvelles/2026/08/le-gouvernement-du-canada-investit-pres-de-2-m-dans-le-secteur-quantique-en-soutenant-femtum.html",
            ),
        ),
        "signals": [
            {
                "source_url": "https://betakit.com/femtum-opens-new-quebec-city-factory-to-build-more-lasers-for-chipmakers/",
                "source_title": "Femtum opens new Québec City factory to build more lasers for chipmakers",
                "source_publisher": "BetaKit",
                "signal_date": datetime(2026, 10, 1, tzinfo=timezone.utc),
                "reason": (
                    "On October 1, 2026, BetaKit reported that Femtum opened a C$2.1 million headquarters and "
                    "factory in Quebec City's Metropolitan Technology Park, expanding its footprint sixfold with "
                    "cleanrooms, laboratories, and offices for mid-infrared fiber-laser production. Femtum had about "
                    "40 employees, seven open roles, and a goal of exceeding 50 staff in 2027. Inference: the cleanroom "
                    "ramp and workforce growth increase laser-platform configuration, process-recipe, calibration, "
                    "quality genealogy, test, and engineering-change pressure. Teamcenter, Polarion, Opcenter, and "
                    "Simcenter fit those controls, and the factory has just entered production scale-up."
                ),
                "pain": (
                    "Must transfer advanced laser designs into a six-times-larger cleanroom factory while preserving "
                    "configuration, calibrated process, test, yield, quality, and engineering-change traceability."
                ),
                "expansion": (
                    "Opened a C$2.1 million Quebec City headquarters and factory with cleanrooms and laboratories, "
                    "and is growing from roughly 40 employees toward more than 50 in 2027."
                ),
            },
            {
                "source_url": "https://www.canada.ca/fr/developpement-economique-regions-quebec/nouvelles/2026/08/le-gouvernement-du-canada-investit-pres-de-2-m-dans-le-secteur-quantique-en-soutenant-femtum.html",
                "source_title": "Le gouvernement du Canada investit près de 2 M$ dans le secteur quantique en soutenant Femtum",
                "source_publisher": "Canada Economic Development for Quebec Regions",
                "signal_date": datetime(2026, 8, 14, tzinfo=timezone.utc),
                "reason": (
                    "On August 14, 2026, Canada Economic Development for Quebec Regions announced a C$1.95 million "
                    "repayable contribution to Femtum for new manufacturing laboratories, greater production capacity, "
                    "and more than 20 jobs. The government described Femtum as a Quebec City designer and manufacturer "
                    "of mid-infrared fiber lasers for advanced semiconductor manufacturing. Inference: funded lab and "
                    "capacity expansion raises equipment-validation, controlled-process, product-release, and quality "
                    "traceability demands; Teamcenter, Polarion, Opcenter, and Simcenter provide a focused digital thread "
                    "while facilities and teams are being built."
                ),
                "pain": (
                    "New manufacturing laboratories and capacity require controlled product releases, validated "
                    "equipment and processes, production quality genealogy, and repeatable laser test evidence."
                ),
                "expansion": (
                    "Received a C$1.95 million federal contribution to add manufacturing laboratories, expand "
                    "production capacity, and create more than 20 jobs."
                ),
            },
            {
                "source_url": "https://femtum.com/resources/femtum-closes-16m-oversubscribed-series-a-to-scale-laser-solutions-for-advanced-semiconductor-manufacturing/",
                "source_title": "Femtum closes $16M oversubscribed Series A to scale laser solutions for advanced semiconductor manufacturing",
                "source_publisher": "Femtum",
                "signal_date": datetime(2026, 3, 12, tzinfo=timezone.utc),
                "reason": (
                    "On March 12, 2026, Femtum announced an oversubscribed C$16 million Series A led by BDC Capital, "
                    "including a C$6 million BDC investment, to expand production capacity and move its validated "
                    "mid-infrared fiber lasers into high-volume semiconductor manufacturing. The systems support laser "
                    "cleaning and trimming, wafer-level silicon photonics, and co-packaged optics for Tier-1 customers. "
                    "Inference: high-volume entry into yield-sensitive semiconductor processes increases variant, "
                    "recipe, supplier, calibration, verification, and change-control burden; the financed scale-up "
                    "creates a current Teamcenter, Polarion, Opcenter, and Simcenter opportunity."
                ),
                "pain": (
                    "High-volume, yield-sensitive semiconductor applications require exact product configuration, "
                    "process recipes, supplier control, calibration, validation, and production-quality traceability."
                ),
                "expansion": (
                    "Closed a C$16 million Series A to expand production capacity and commercialize fiber-laser "
                    "systems with Tier-1 semiconductor customers."
                ),
            },
        ],
        "keyword_ids": [8],
        "signal_label": "New C$2.1M cleanroom factory follows C$16M laser scale-up round",
        "challenge_summary": (
            "On October 1, 2026, Femtum opened a C$2.1 million Quebec City factory with cleanrooms and laboratories, "
            "expanding its footprint sixfold after a C$16 million Series A and a C$1.95 million federal contribution. "
            "The mid-infrared fiber-laser manufacturer had about 40 employees, seven open roles, and a goal of more "
            "than 50 staff in 2027. Inference: the cleanroom ramp creates immediate configuration, process-recipe, "
            "calibration, yield, test, and production-quality traceability pressure."
        ),
        "why_relevant": (
            "Teamcenter can govern laser-platform configurations, BOMs, suppliers, and engineering changes. Polarion "
            "can trace semiconductor-customer requirements into calibration and qualification evidence, Opcenter can "
            "provide cleanroom production and quality genealogy, and Simcenter can support laser and thermal validation. "
            "The new facility and funded hiring make this an active implementation window."
        ),
        "qualification_status": "qualified",
        "opportunity_score": 95,
        "manufacturing_fit_score": 97,
        "trigger_score": 99,
        "solution_fit_score": 96,
        "evidence_quality_score": 99,
    },
    {
        "company_name": "Voyis Imaging Inc.",
        "company_domain": "voyis.com",
        "company_url": "https://voyis.com/",
        "location": "Waterloo, Ontario, Canada",
        "industry": "Underwater optical inspection and marine robotics hardware manufacturing",
        "products": ["Teamcenter", "Polarion", "Simcenter"],
        "identity": CompanyIdentityEvidence(
            official_name="Voyis Imaging Inc.",
            official_website_url="https://voyis.com/",
            corroborating_urls=(
                "https://oceansupercluster.ca/project/canadas-ocean-supercluster-announces-4-7m-tech-solution-for-faster-safer-and-more-accurate-vessel-hull-inspections/",
            ),
        ),
        "signals": [
            {
                "source_url": "https://oceansupercluster.ca/project/canadas-ocean-supercluster-announces-4-7m-tech-solution-for-faster-safer-and-more-accurate-vessel-hull-inspections/",
                "source_title": "Canada's Ocean Supercluster announces $4.7M tech solution for faster, safer and more accurate vessel hull inspections",
                "source_publisher": "Canada's Ocean Supercluster",
                "signal_date": datetime(2026, 9, 17, tzinfo=timezone.utc),
                "reason": (
                    "On September 17, 2026, Canada's Ocean Supercluster announced the C$4.7 million SHIP project, "
                    "led by Waterloo-based Voyis Imaging with MarineNAV and C$2 million of Supercluster funding, to "
                    "integrate compact remotely operated vehicles, underwater optical imaging, machine learning, and "
                    "digital twins for vessel-hull inspection. The system is intended to identify cracks, coating "
                    "degradation, corrosion, and fouling and generate class-aware inspection reports. Inference: "
                    "integrating pressure-rated sensors, cameras, vehicles, software, defect models, and classification "
                    "requirements creates configuration, interface, verification, and test-evidence complexity. "
                    "Teamcenter, Polarion, and Simcenter fit that work while the funded multi-partner project is underway."
                ),
                "pain": (
                    "Must control pressure-rated optical hardware, ROV interfaces, software and model releases, "
                    "classification requirements, and validation evidence across a multi-company marine system."
                ),
                "expansion": (
                    "Leads a C$4.7 million vessel-hull inspection project with MarineNAV and C$2 million of Ocean "
                    "Supercluster funding."
                ),
            }
        ],
        "keyword_ids": [8, 13],
        "signal_label": "C$4.7M SHIP project integrates underwater robotics and optical inspection",
        "challenge_summary": (
            "On September 17, 2026, Voyis Imaging was named lead of the C$4.7 million SHIP project with MarineNAV, "
            "including C$2 million from Canada's Ocean Supercluster, to combine compact ROVs, underwater optical "
            "imaging, machine learning, and digital twins for hull inspections. The system must detect cracks, coating "
            "degradation, corrosion, and fouling and produce class-aware reports. Inference: the funded integration "
            "creates immediate hardware/software configuration, interface, verification, and classification-test burden."
        ),
        "why_relevant": (
            "Teamcenter can control sensor, camera, ROV-interface, and released software configurations across the "
            "partner program. Polarion can trace classification and inspection requirements into defects and test "
            "evidence, while Simcenter can support optical, structural, and vehicle-integration validation. The active "
            "funded project creates a defined delivery window for these controls."
        ),
        "qualification_status": "qualified",
        "opportunity_score": 91,
        "manufacturing_fit_score": 95,
        "trigger_score": 94,
        "solution_fit_score": 91,
        "evidence_quality_score": 96,
    },
    {
        "company_name": "Hanon Systems Canada Inc.",
        "company_domain": "hanonsystems.com",
        "company_url": "https://www.hanonsystems.com/En",
        "location": "Vaughan and Belleville, Ontario, Canada",
        "industry": "Automotive thermal-management and electric-compressor manufacturing",
        "products": ["Teamcenter", "Opcenter", "Tecnomatix", "Simcenter"],
        "identity": CompanyIdentityEvidence(
            official_name="Hanon Systems Canada Inc.",
            official_website_url="https://www.hanonsystems.com/En",
            corroborating_urls=(
                "https://www.canada.ca/en/innovation-science-economic-development/news/2026/08/government-of-canada-invests-in-hanon-systems-to-strengthen-canadas-ev-manufacturing-sector.html",
            ),
        ),
        "signals": [
            {
                "source_url": "https://www.canada.ca/en/innovation-science-economic-development/news/2026/08/government-of-canada-invests-in-hanon-systems-to-strengthen-canadas-ev-manufacturing-sector.html",
                "source_title": "Government of Canada invests in Hanon Systems to strengthen Canada's EV manufacturing sector",
                "source_publisher": "Innovation, Science and Economic Development Canada",
                "signal_date": datetime(2026, 8, 6, tzinfo=timezone.utc),
                "reason": (
                    "On August 6, 2026, the Government of Canada announced up to C$10 million for Hanon Systems' "
                    "C$198.75 million Ontario project, including C$155 million of company investment, to establish "
                    "Canada's first electric-compressor plant and an R&D centre in Vaughan. The plant is targeted to "
                    "reach 1.5 million compressors annually by 2034 and create about 300 jobs. Inference: a greenfield "
                    "high-volume EV component line creates product/process industrialization, supplier, tooling, line "
                    "simulation, serialized quality, and production-ramp complexity. Teamcenter, Tecnomatix, Opcenter, "
                    "and Simcenter map directly to those needs while facility and line decisions remain active."
                ),
                "pain": (
                    "Must industrialize a greenfield e-compressor plant and R&D centre for a 1.5-million-unit annual "
                    "target while controlling designs, suppliers, tooling, line plans, launch quality, and traceability."
                ),
                "expansion": (
                    "Launched a C$198.75 million Vaughan e-compressor manufacturing and R&D project supported by up "
                    "to C$10 million federally, targeting about 300 jobs and 1.5 million units a year by 2034."
                ),
            },
            {
                "source_url": "https://www.hanonsystems.com/En/Media/NewsDetails/396",
                "source_title": "Hanon Systems breaks ground on new e-Compressor manufacturing facility in Vaughan, Canada",
                "source_publisher": "Hanon Systems",
                "signal_date": datetime(2026, 8, 7, tzinfo=timezone.utc),
                "reason": (
                    "On August 7, 2026, Hanon Systems confirmed the Vaughan groundbreaking for its first Canadian "
                    "electric-compressor manufacturing facility and associated R&D centre, adding to Canadian operations "
                    "in Belleville and Concord. The company said the investment will increase Canadian production and "
                    "engineering capacity for electrified-vehicle thermal management. Inference: parallel facility, "
                    "product, process, and engineering expansion increases BOM/change, launch-readiness, factory-layout, "
                    "capacity, quality, and validation workload; Teamcenter, Tecnomatix, Opcenter, and Simcenter form the "
                    "smallest defensible set during construction and industrialization."
                ),
                "pain": (
                    "Parallel R&D and first-of-kind Canadian production require coordinated product releases, factory "
                    "and line planning, capacity validation, launch quality, and closed-loop engineering changes."
                ),
                "expansion": (
                    "Broke ground on a Vaughan electric-compressor factory and R&D centre to expand Canadian EV thermal-"
                    "management manufacturing and engineering capacity."
                ),
            },
        ],
        "keyword_ids": [8],
        "signal_label": "C$198.75M Vaughan e-compressor plant targets 1.5M units yearly",
        "challenge_summary": (
            "On August 6-7, 2026, Hanon Systems began a C$198.75 million Vaughan project, including C$155 million of "
            "company investment and up to C$10 million federally, for Canada's first e-compressor factory and an R&D "
            "centre. The facility targets 1.5 million compressors annually by 2034 and about 300 jobs. Inference: the "
            "greenfield ramp creates immediate design/process industrialization, supplier, tooling, line-planning, "
            "capacity, launch-quality, and serialized-traceability complexity."
        ),
        "why_relevant": (
            "Teamcenter can govern compressor configurations, suppliers, released BOMs, and engineering changes. "
            "Tecnomatix can plan and validate the new line, Opcenter can control production quality and genealogy, and "
            "Simcenter can support thermal, mechanical, and manufacturing validation. Groundbreaking and active line "
            "industrialization make this a time-sensitive factory-digitalization window."
        ),
        "qualification_status": "qualified",
        "opportunity_score": 96,
        "manufacturing_fit_score": 99,
        "trigger_score": 99,
        "solution_fit_score": 97,
        "evidence_quality_score": 99,
    },
)


REVIEW = {
    1: (18, 15, 0, 3),
    2: (23, 18, 1, 4),
    3: (19, 15, 0, 4),
    4: (24, 19, 0, 5),
    5: (22, 18, 0, 4),
    7: (26, 21, 0, 5),
    8: (34, 25, 4, 5),
    9: (27, 22, 0, 5),
    10: (21, 17, 0, 4),
    11: (22, 18, 0, 4),
    12: (17, 14, 0, 3),
    13: (29, 22, 2, 5),
    14: (25, 20, 0, 5),
    15: (20, 16, 0, 4),
    16: (16, 13, 0, 3),
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

    domains = {prospect["company_domain"].lower() for prospect in PROSPECTS}
    with database.session() as session:
        before_rows = session.execute(
            select(CompanyRecord.id, CompanyRecord.company_name, CompanyRecord.company_domain)
            .where(func.lower(CompanyRecord.company_domain).in_(domains))
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
                    row["company_id"] for row in persisted if row["company_domain"].lower() not in existing_domains
                ],
                "existing_company_ids_reassessed": [
                    row["company_id"] for row in persisted if row["company_domain"].lower() in existing_domains
                ],
                "keyword_audits": [
                    {
                        "id": keyword_id,
                        "keyword": keywords_after[keyword_id].keyword,
                        "search_count_before": keywords_before[keyword_id].search_count,
                        "search_count_after": keywords_after[keyword_id].search_count,
                        "unique_domains_reviewed": REVIEW[keyword_id][0],
                        "rejected_before_persistence": REVIEW[keyword_id][1],
                        "qualified_published": REVIEW[keyword_id][2],
                        "duplicates_or_existing_skipped": REVIEW[keyword_id][3],
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
                        "Startup Gallery": "all keyword themes checked; unfiltered discovery results yielded no verified publishable lead",
                        "public X": "indexed public results checked for all keyword themes; direct IAB access failed on a certificate error and was not bypassed",
                        "BetaKit": "all keyword themes checked; TetraGen and Femtum qualified after official and independent verification",
                        "NGen": "all keyword themes checked across funding, portfolio, case-study and collaboration pages; discovery-only leads did not add a verified dated candidate",
                        "SpaceQ": "aerospace, space, defence, propulsion, drone and avionics themes checked; no new qualified lead",
                        "AIAC": "member directory, industry guide, reports and news checked for applicable aerospace and defence keywords; directory-only leads were not published",
                    },
                    "rotated_sources": [
                        "Canada's Ocean Supercluster",
                        "CanadaBuys",
                        "ISED Canada",
                        "CED Quebec",
                        "BDC Capital",
                        "ventureLAB",
                        "APMA",
                        "CADSI/CANSEC",
                        "Aero Montreal",
                        "DAIR Aerospace",
                        "OVIN",
                        "Oakville Chamber of Commerce",
                        "Canadian Manufacturing",
                        "PLANT",
                        "Electric Autonomy Canada",
                        "Marine Log",
                        "Naval News",
                    ],
                    "warnings": [
                        "The in-app browser became unstable after the aerospace pass; remaining checks used source-specific web retrieval.",
                        "Direct X.com access failed with a certificate warning; the warning was not bypassed.",
                        "No connected Excel document session was registered, so no workbook edit was attempted.",
                    ],
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
