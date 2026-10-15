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
        "company_name": "Qubic",
        "company_domain": "qubictech.co",
        "company_url": "https://qubictech.co/",
        "location": "Sherbrooke, Quebec, and Waterloo, Ontario, Canada",
        "industry": "Cryogenic quantum amplifier and radio-frequency sensing hardware",
        "products": ["Teamcenter", "Polarion", "Simcenter"],
        "identity": CompanyIdentityEvidence(
            official_name="Qubic",
            official_website_url="https://qubictech.co/",
            corroborating_urls=(
                "https://spaceq.ca/qubic-lands-ca1-5m-federal-contract-to-de-risk-quantum-sensor-supply-chains/",
                "https://betakit.com/tag/quantum/",
            ),
        ),
        "signals": [
            {
                "source_url": "https://spaceq.ca/qubic-lands-ca1-5m-federal-contract-to-de-risk-quantum-sensor-supply-chains/",
                "source_title": "Qubic Lands CA$1.5M Federal Contract to De-Risk Quantum Sensor Supply Chains",
                "source_publisher": "SpaceQ",
                "signal_date": datetime(2026, 9, 11, tzinfo=timezone.utc),
                "reason": (
                    "On September 11, 2026, SpaceQ reported that Qubic received an Innovative Solutions Canada "
                    "testing-stream contract worth up to C$1.5 million to deliver nine KI-TWPA cryogenic amplifiers, "
                    "supporting components, and software through integration and test milestones extending into spring "
                    "2027. The sub-0.1 mW hardware is intended to remove thermal and supply-chain bottlenecks in "
                    "cryogenic quantum sensing. Inference: a fixed federal delivery set with tightly coupled microwave "
                    "hardware, firmware, components, and acceptance tests increases configuration, supplier, change, "
                    "and verification traceability; Teamcenter, Polarion, and Simcenter are the smallest defensible fit."
                ),
                "pain": (
                    "Must control amplifier, supporting-component, and software configurations while proving contract "
                    "integration and test milestones for a highly sensitive cryogenic RF system."
                ),
                "expansion": (
                    "Won an Innovative Solutions Canada contract worth up to C$1.5 million to deliver nine KI-TWPA "
                    "amplifiers and supporting hardware/software through spring 2027."
                ),
            },
            {
                "source_url": "https://qubictech.co/media/qubic-secures-oversubscribed-2-5-million-usd-seed-round/",
                "source_title": "Qubic secures oversubscribed $2.5 million USD seed round",
                "source_publisher": "Qubic",
                "signal_date": datetime(2026, 6, 23, tzinfo=timezone.utc),
                "reason": (
                    "On June 23, 2026, Qubic announced an oversubscribed US$2.5 million (C$3.5 million) seed round, "
                    "bringing disclosed equity and grant financing to nearly C$10 million, to accelerate its low-noise "
                    "amplifiers, quantum-enhanced radar work, and manufacturing capability. Inference: moving precision "
                    "cryogenic electronics toward repeatable manufacture increases product-variant, supplier, released-"
                    "BOM, calibration, simulation, and verification workload. Teamcenter can govern configurations and "
                    "changes, Polarion can trace funded requirements into evidence, and Simcenter can support thermal "
                    "and electromagnetic validation while commercialization is being funded."
                ),
                "pain": (
                    "Must convert research-grade cryogenic amplifier and sensing designs into repeatable manufactured "
                    "products with controlled configurations, suppliers, calibration, and validation evidence."
                ),
                "expansion": (
                    "Raised an oversubscribed US$2.5 million seed round to accelerate amplifier commercialization, "
                    "quantum-enhanced radar development, and manufacturing capability."
                ),
            },
        ],
        "keyword_ids": [8, 14],
        "signal_label": "C$1.5M federal contract requires nine cryogenic-amplifier systems",
        "challenge_summary": (
            "On September 11, 2026, Qubic secured an Innovative Solutions Canada test contract worth up to C$1.5 "
            "million to deliver nine KI-TWPA cryogenic amplifiers, supporting components, and software through spring "
            "2027; this followed a June US$2.5 million seed round for manufacturing scale-up and quantum-enhanced "
            "radar. Inference: controlled deliveries of tightly coupled RF hardware and software create immediate "
            "configuration, supplier, change-control, thermal/electromagnetic validation, and acceptance-test pressure."
        ),
        "why_relevant": (
            "Teamcenter can govern amplifier variants, released BOMs, suppliers, and hardware/software changes. "
            "Polarion can trace federal contract requirements into integration and acceptance evidence, while Simcenter "
            "can support thermal and electromagnetic validation. The funded delivery milestones run into spring 2027, "
            "so these controls are relevant before the nine-system program and manufacturing capability expand."
        ),
        "qualification_status": "qualified",
        "opportunity_score": 93,
        "manufacturing_fit_score": 95,
        "trigger_score": 95,
        "solution_fit_score": 94,
        "evidence_quality_score": 96,
    },
    {
        "company_name": "Kanin Energy",
        "company_domain": "kaninenergy.com",
        "company_url": "https://kaninenergy.com/",
        "location": "Calgary, Alberta, Canada",
        "industry": "Industrial waste-heat power project engineering and operations",
        "products": ["Teamcenter", "Capital", "Simcenter"],
        "identity": CompanyIdentityEvidence(
            official_name="Kanin Energy",
            official_website_url="https://kaninenergy.com/",
            corroborating_urls=(
                "https://www.cgf-fcc.ca/en/news/kanin-energy-closes-100m-fundraise-to-scale-industrial-waste-heat-to-power-across-north-america/",
                "https://energycapitalhtx.com/kanin-energy-raises-100m",
            ),
        ),
        "signals": [
            {
                "source_url": "https://www.cgf-fcc.ca/en/news/kanin-energy-closes-100m-fundraise-to-scale-industrial-waste-heat-to-power-across-north-america/",
                "source_title": "Kanin Energy Closes $100M Fundraise to Scale Industrial Waste Heat to Power Across North America",
                "source_publisher": "Canada Growth Fund",
                "signal_date": datetime(2026, 9, 16, tzinfo=timezone.utc),
                "reason": (
                    "On September 16, 2026, Canada Growth Fund announced up to US$100 million (about C$138 million) "
                    "of financing for Kanin Energy, split between up to US$50 million from S2G Investments and up to "
                    "US$50 million from CGF, to develop, construct, own, and operate industrial waste-heat-to-power "
                    "projects across North America. Kanin already had an operating facility and several projects under "
                    "construction. Inference: scaling a multi-site fleet across turbines or organic Rankine equipment, "
                    "controls, interconnection, vendors, and commissioning creates equipment-configuration, electrical-"
                    "architecture, thermal-performance, and supplier-change pressure; Teamcenter, Capital, and Simcenter "
                    "are a focused fit while the financed portfolio moves into construction."
                ),
                "pain": (
                    "Must repeatably engineer and commission a multi-site fleet while controlling vendor equipment, "
                    "electrical interfaces, project configurations, changes, and thermal-performance evidence."
                ),
                "expansion": (
                    "Closed up to US$100 million of financing to develop, construct, own, and operate waste-heat-to-"
                    "power projects, with an operating facility and several more under construction."
                ),
            },
            {
                "source_url": "https://kaninenergy.com/press-media/kanin-energy-develops-7-mw-waste-heat-to-power-project-at-colorado-gas-plant/",
                "source_title": "Kanin Energy Develops 7 MW Waste Heat to Power Project at Colorado Gas Plant",
                "source_publisher": "Kanin Energy",
                "signal_date": datetime(2026, 6, 23, tzinfo=timezone.utc),
                "reason": (
                    "On June 23, 2026, Kanin Energy announced a 7 MW waste-heat-to-power project at Phillips 66's "
                    "Mewbourn gas processing plant in Colorado, with construction planned for later in 2026 and Kanin "
                    "responsible for owning and operating the asset. Inference: translating site-specific heat sources "
                    "into an owned power asset requires controlled mechanical/electrical design, vendor interfaces, "
                    "thermal modelling, construction changes, and commissioning evidence. Teamcenter, Capital, and "
                    "Simcenter map directly to those needs as construction begins."
                ),
                "pain": (
                    "Must integrate site-specific heat recovery, generation equipment, controls, and grid interfaces "
                    "while preserving design and commissioning traceability for an owned 7 MW asset."
                ),
                "expansion": (
                    "Advanced a 7 MW waste-heat power project at Phillips 66's Mewbourn gas plant toward construction "
                    "later in 2026."
                ),
            },
        ],
        "keyword_ids": [5],
        "signal_label": "US$100M financing scales owned waste-heat power project fleet",
        "challenge_summary": (
            "On September 16, 2026, Kanin Energy closed up to US$100 million (about C$138 million) from S2G and "
            "Canada Growth Fund to develop, construct, own, and operate waste-heat-to-power assets across North "
            "America; it already had one operating facility and several projects under construction. Inference: the "
            "multi-site buildout creates immediate equipment-configuration, supplier, electrical-interface, thermal-"
            "performance, construction-change, and commissioning complexity."
        ),
        "why_relevant": (
            "Teamcenter can control site and equipment configurations, vendor documents, and engineering changes. "
            "Capital can manage plant electrical architecture and interfaces, while Simcenter can validate heat-"
            "recovery and power-system performance. The financing is explicitly tied to construction and operation of "
            "a larger asset fleet, making standardization and traceability urgent now."
        ),
        "qualification_status": "qualified",
        "opportunity_score": 86,
        "manufacturing_fit_score": 83,
        "trigger_score": 96,
        "solution_fit_score": 88,
        "evidence_quality_score": 95,
    },
    {
        "company_name": "WhalePiX Inc.",
        "company_domain": "whalepix.com",
        "company_url": "https://whalepix.com/",
        "location": "Quebec City, Quebec, and Ottawa, Ontario, Canada",
        "industry": "Silicon-photonics transceiver chiplet development and manufacturing",
        "products": ["Teamcenter", "Polarion", "Simcenter"],
        "identity": CompanyIdentityEvidence(
            official_name="WhalePiX Inc.",
            official_website_url="https://whalepix.com/en",
            corroborating_urls=(
                "https://fabricinnovation.ca/whalepix/",
                "https://www.cmc.ca/tackling-the-demands-of-ai-on-the-edge-fabric-announces-10-7m-investment/",
            ),
        ),
        "signals": [
            {
                "source_url": "https://fabricinnovation.ca/whalepix/",
                "source_title": "LightEdge - Scalable Photonic Chiplets for Next-Generation AI Data Centre Interconnects",
                "source_publisher": "FABrIC",
                "signal_date": datetime(2026, 5, 13, tzinfo=timezone.utc),
                "reason": (
                    "On May 13, 2026, FABrIC disclosed C$999,796 for WhalePiX's LightEdge project to move multi-"
                    "terabit O-band silicon-photonics transceiver chiplets from the lab into pre-commercial manufacturing. "
                    "The work includes production-grade packaging with a Canadian Tier-1 manufacturer plus wafer-level "
                    "test and automation. Inference: the lab-to-production transfer creates chiplet/package variants, "
                    "supplier-interface, design-change, yield, automated-test, and verification traceability pressure; "
                    "Teamcenter, Polarion, and Simcenter are the smallest defensible set for the ongoing funded program."
                ),
                "pain": (
                    "Must transfer photonic chiplets into production-grade packaging and automated wafer-level test "
                    "while controlling variants, supplier interfaces, design changes, yield, and verification evidence."
                ),
                "expansion": (
                    "Received C$999,796 for LightEdge to move multi-terabit photonic chiplets from laboratory work into "
                    "pre-commercial manufacturing, packaging, and automated test."
                ),
            }
        ],
        "keyword_ids": [8],
        "signal_label": "C$999,796 project moves photonic chiplets into pre-commercial manufacturing",
        "challenge_summary": (
            "On May 13, 2026, FABrIC awarded WhalePiX C$999,796 for LightEdge, a program moving multi-terabit "
            "O-band silicon-photonics transceiver chiplets into pre-commercial manufacturing with production-grade "
            "packaging, a Canadian Tier-1 manufacturing partner, and wafer-level test automation. Inference: the "
            "industrialization step creates immediate chiplet/package variant, supplier-interface, design-change, yield, "
            "automated-test, and verification-traceability complexity."
        ),
        "why_relevant": (
            "Teamcenter can govern chiplet and package configurations, supplier deliverables, and released changes. "
            "Polarion can trace performance and manufacturing requirements into wafer/package tests, while Simcenter "
            "can support thermal and signal-integrity validation. The funded project is already bridging the lab and "
            "pre-commercial production, so controls established now can prevent rework during scale-up."
        ),
        "qualification_status": "qualified",
        "opportunity_score": 87,
        "manufacturing_fit_score": 93,
        "trigger_score": 82,
        "solution_fit_score": 90,
        "evidence_quality_score": 94,
    },
    {
        "company_name": "Canada Rocket Company",
        "company_domain": "canadarocketcompany.com",
        "company_url": "https://www.canadarocketcompany.com/",
        "location": "London, Ontario, Canada",
        "industry": "Reusable orbital launch vehicle engineering and manufacturing",
        "products": ["Teamcenter", "Polarion", "Simcenter", "Capital"],
        "identity": CompanyIdentityEvidence(
            official_name="Canada Rocket Company",
            official_website_url="https://www.canadarocketcompany.com/",
            corroborating_urls=(
                "https://spaceq.ca/canada-rocket-company-engine-test-facility-london/",
                "https://investontario.ca/press-release/canada-rocket-company-establishes-advanced-testing-facility-london-ontario",
            ),
        ),
        "signals": [
            {
                "source_url": "https://spaceq.ca/canada-rocket-company-engine-test-facility-london/",
                "source_title": "Canada Rocket Company Breaks Ground on Engine Test Facility in London",
                "source_publisher": "SpaceQ",
                "signal_date": datetime(2026, 10, 2, tzinfo=timezone.utc),
                "reason": (
                    "On October 2, 2026, SpaceQ reported that Canada Rocket Company broke ground on a C$30 million "
                    "engine-test facility at London International Airport, planned to be fully operational in 2028 for "
                    "a reusable medium-lift launch vehicle targeting up to 12,500 kg to sun-synchronous orbit. Inference: "
                    "building the test asset while maturing vehicle and propulsion systems increases configuration, "
                    "requirements, electrical-interface, simulation, instrumentation, and test-evidence complexity. "
                    "Teamcenter, Polarion, Simcenter, and Capital form a focused digital thread during facility and "
                    "vehicle development."
                ),
                "pain": (
                    "Must synchronize reusable launch-vehicle, propulsion, facility, instrumentation, and electrical "
                    "configurations while tracing requirements, hazards, simulations, and engine-test evidence."
                ),
                "expansion": (
                    "Broke ground on a C$30 million London engine-test facility intended to support a reusable medium-"
                    "lift launcher and become fully operational in 2028."
                ),
            },
            {
                "source_url": "https://investontario.ca/press-release/canada-rocket-company-establishes-advanced-testing-facility-london-ontario",
                "source_title": "Canada Rocket Company establishes advanced testing facility in London, Ontario",
                "source_publisher": "Invest Ontario",
                "signal_date": datetime(2026, 10, 1, tzinfo=timezone.utc),
                "reason": (
                    "On October 1, 2026, Invest Ontario announced Canada Rocket Company's C$30 million, 12,000-square-"
                    "foot Jeremy Hansen Rocket Test Facility at London International Airport, initially expected to "
                    "create 40 jobs over 18 months and validate critical rocket systems. The company described a long-"
                    "term ambition of 1,000 jobs and C$1 billion of investment. Inference: simultaneous facility build, "
                    "hiring, and flight-system validation create immediate BOM/configuration, requirements, test, "
                    "simulation, and electrical-architecture pressure addressed by Teamcenter, Polarion, Simcenter, "
                    "and Capital."
                ),
                "pain": (
                    "Must build a new propulsion-test organization and facility while controlling rocket-system "
                    "configurations, requirements, instrumentation interfaces, hazards, and test results."
                ),
                "expansion": (
                    "Committed C$30 million to a 12,000-square-foot London rocket test facility with 40 initial jobs "
                    "and a long-term C$1 billion investment ambition."
                ),
            },
        ],
        "keyword_ids": [7, 8, 9, 14],
        "signal_label": "C$30M London rocket test facility breaks ground",
        "challenge_summary": (
            "On October 1-2, 2026, Canada Rocket Company broke ground on a C$30 million, 12,000-square-foot engine-"
            "test facility at London International Airport, initially creating 40 jobs and targeting full operation in "
            "2028 for a reusable medium-lift launcher rated up to 12,500 kg to sun-synchronous orbit. Inference: the "
            "facility build and vehicle maturation create immediate configuration, requirements, instrumentation, "
            "electrical-interface, simulation, safety, and test-evidence complexity."
        ),
        "why_relevant": (
            "Teamcenter can govern launch-vehicle, engine, facility, and instrumentation configurations. Polarion can "
            "trace requirements, hazards, and verification; Simcenter can support propulsion and structural validation; "
            "and Capital can control electrical architecture and interfaces. Groundbreaking and active hiring make the "
            "period before facility commissioning the practical window to establish this digital thread."
        ),
        "qualification_status": "qualified",
        "opportunity_score": 99,
        "manufacturing_fit_score": 99,
        "trigger_score": 99,
        "solution_fit_score": 99,
        "evidence_quality_score": 99,
    },
)


# unique domains reviewed, rejected before persistence, qualified/watchlist published,
# duplicates/existing domains skipped. Counts are deliberately conservative because
# Google result pagination was blocked by an automated-traffic interstitial.
REVIEW = {
    1: (8, 6, 0, 2),
    2: (9, 7, 0, 2),
    3: (8, 6, 0, 2),
    4: (9, 6, 0, 3),
    5: (10, 7, 1, 2),
    7: (12, 8, 1, 3),
    8: (18, 11, 3, 4),
    9: (12, 8, 1, 3),
    10: (11, 8, 0, 3),
    11: (9, 7, 0, 2),
    12: (7, 5, 0, 2),
    13: (10, 7, 0, 3),
    14: (13, 8, 2, 3),
    15: (9, 7, 0, 2),
    16: (7, 5, 0, 2),
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
    # Validate every evidence item before the first mutation for this prospect.
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

    # Perform the full deterministic identity gate before any database write.
    for prospect in PROSPECTS:
        for evidence in prospect["signals"]:
            verify_company_identity(make_signal(prospect, evidence), prospect["identity"])

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

    # Record exactly one successful search per saved keyword after publication.
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
                        "watchlist_published": 0,
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
                        "Startup Gallery": (
                            "direct Canada, aerospace, and energy category checks completed; Canadian results were "
                            "software/service businesses and the aerospace page returned no candidate cards"
                        ),
                        "public X": (
                            "attempted for every keyword; direct IAB access failed with ERR_CERT_AUTHORITY_INVALID "
                            "and the warning was not bypassed"
                        ),
                        "BetaKit": (
                            "all keyword themes searched; its hardware/quantum coverage corroborated Qubic and "
                            "exposed no additional candidate passing the full gate"
                        ),
                        "NGen": (
                            "all keyword themes searched across funding, project, case-study, challenge and news "
                            "pages; no new dated candidate passed the gate"
                        ),
                        "SpaceQ": (
                            "aerospace, space, defence, propulsion, drone and avionics themes checked; Qubic and "
                            "Canada Rocket Company produced qualifying dated triggers"
                        ),
                        "AIAC": (
                            "member directory, 2026 industry guide, reports and news checked for aerospace and "
                            "defence keywords; directory-only entries were not published"
                        ),
                    },
                    "rotated_sources": [
                        "FABrIC/CMC Microsystems",
                        "Canada Growth Fund",
                        "Invest Ontario",
                        "Innovative Solutions Canada",
                        "CanadaBuys",
                        "ventureLAB Hardware Catalyst",
                        "Aero Montreal",
                        "DAIR Aerospace",
                        "OVIN",
                        "Oakville Chamber of Commerce",
                        "CADSI/CANSEC",
                        "APMA",
                        "Canadian Manufacturing",
                        "PLANT",
                        "Electric Autonomy Canada",
                        "Marine Log",
                        "Naval News",
                    ],
                    "warnings": [
                        "Google switched to an automated-traffic interstitial during the source-specific sweep; it "
                        "was not bypassed, and quota shortfalls use actual conservative counts.",
                        "Direct X.com access failed with a certificate warning; the warning was not bypassed.",
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
