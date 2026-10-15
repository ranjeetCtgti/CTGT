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

ENERQUEST_GOV_URL = (
    "https://news.ontario.ca/en/release/1007173/"
    "ontario_welcomes_158_million_manufacturing_investment_in_southwestern_ontario"
)
ENERQUEST_PLANT_URL = (
    "https://www.plant.ca/plant-industry/"
    "enerquest-to-expand-ontario-facility-reshore-switchgear-manufacturing/"
)
POWER_WOOD_GNW_URL = (
    "https://www.globenewswire.com/news-release/2026/08/04/3338535/0/en/"
    "power-wood-holdings-agrees-ca-84m-investment-into-black-pellet-production-plants.html"
)
POWER_WOOD_PAPER_ADVANCE_URL = (
    "https://www.paperadvance.com/bioeconomy/biomass/"
    "power-wood-agrees-c-84m-black-pellet-financing.html"
)
IMT_GOV_URL = (
    "https://www.canada.ca/en/department-national-defence/news/2026/03/"
    "minister-mcguinty-announces-investment-of-1-4-billion-into-domestic-ammunition-production.html"
)
IMT_HEART_FM_URL = (
    "https://www.heartfm.ca/news/local-news/ottawa-funding-new-facility-for-imt-precision/"
)
NORTHERN_OFFICIAL_URL = (
    "https://www.northerntransformer.com/post/"
    "northern-transformer-breaks-ground-on-large-power-transformer-facility"
)
NORTHERN_PLANT_URL = (
    "https://www.plant.ca/operations/"
    "northern-transformer-invests-207m-to-build-new-facility-in-innisfil/"
)


PROSPECTS = [
    {
        "company_name": "EnerQuest Technologies Solutions Inc.",
        "company_domain": "enerquestservices.com",
        "company_url": "https://enerquestservices.com/",
        "location": "Harrow, Ontario, Canada",
        "industry": "Custom prefabricated electrical equipment and switchgear manufacturing",
        "products": ["Teamcenter", "Tecnomatix", "Opcenter"],
        "identity": CompanyIdentityEvidence(
            official_name="EnerQuest Technologies Solutions Inc.",
            official_website_url="https://enerquestservices.com/",
            corroborating_urls=(ENERQUEST_GOV_URL, ENERQUEST_PLANT_URL),
        ),
        "signals": [
            {
                "source_url": ENERQUEST_GOV_URL,
                "source_title": "Ontario Welcomes $15.8 Million Manufacturing Investment in Southwestern Ontario",
                "source_publisher": "Ontario Newsroom",
                "signal_date": datetime(2026, 3, 17, tzinfo=timezone.utc),
                "reason": (
                    "On March 17, 2026, Ontario announced EnerQuest Technologies Solutions Inc.'s "
                    "$15.8 million expansion of its Harrow manufacturing facility, supported by "
                    "$1.5 million in provincial funding, to bring switchgear sub-assembly production "
                    "in-house from a U.S. sister facility. The project will create 125 jobs, protect "
                    "154 existing jobs, increase capacity, and serve confirmed contracts for data-centre "
                    "infrastructure, modular housing, and medical units. Inference: reshoring an engineered "
                    "sub-assembly while scaling custom production creates immediate product-configuration, "
                    "supplier-change, line-planning, quality, and production-visibility pressure."
                ),
                "pain": (
                    "Must industrialize an in-house switchgear sub-assembly flow while controlling custom "
                    "equipment configurations, engineering changes, supplier transitions, and production quality."
                ),
                "expansion": (
                    "Investing $15.8 million in Harrow to reshore switchgear sub-assembly, add 125 jobs, "
                    "protect 154 jobs, and meet confirmed customer contracts."
                ),
            }
        ],
        "keyword_ids": (5,),
        "keyword_source_url": ENERQUEST_GOV_URL,
        "keyword_source_title": "Ontario Welcomes $15.8 Million Manufacturing Investment in Southwestern Ontario",
        "keyword_source_publisher": "Ontario Newsroom",
        "signal_label": "$15.8M switchgear expansion reshores sub-assembly to Harrow",
        "signal_date": datetime(2026, 3, 17, tzinfo=timezone.utc),
        "challenge_summary": (
            "On March 17, 2026, EnerQuest committed $15.8 million to expand its Harrow plant and bring "
            "switchgear sub-assembly production in-house from a U.S. sister facility, with $1.5 million "
            "from Ontario, 125 new jobs, and 154 protected positions. The expansion is intended to meet "
            "confirmed contracts for data-centre infrastructure, modular housing, and medical units; "
            "inference: custom product variants, supplier changes, factory-flow design, and quality traceability "
            "must be controlled as production is reshored. Those commitments make process definition and "
            "configuration discipline urgent during the active expansion."
        ),
        "why_relevant": (
            "Teamcenter can govern engineered switchgear BOMs, revisions, and supplier changes; Tecnomatix can "
            "validate the reshored assembly flow before equipment and labour are committed; Opcenter can provide "
            "production visibility and quality traceability. The practical outcome is a faster ramp with fewer "
            "configuration errors and less rework while EnerQuest delivers confirmed contracts."
        ),
        "qualification_status": "qualified",
        "opportunity_score": 91,
        "manufacturing_fit_score": 99,
        "trigger_score": 93,
        "solution_fit_score": 92,
        "evidence_quality_score": 98,
    },
    {
        "company_name": "Power Wood Canada Corp.",
        "company_domain": "powerwoodcanadacorp.com",
        "company_url": "https://www.powerwoodcanadacorp.com/",
        "location": "Calgary, Alberta, Canada",
        "industry": "Advanced black-pellet biofuel manufacturing",
        "products": ["Tecnomatix", "Opcenter"],
        "identity": CompanyIdentityEvidence(
            official_name="Power Wood Canada Corp.",
            official_website_url="https://www.powerwoodcanadacorp.com/",
            corroborating_urls=(POWER_WOOD_PAPER_ADVANCE_URL,),
        ),
        "signals": [
            {
                "source_url": POWER_WOOD_GNW_URL,
                "source_title": "Power Wood Holdings Agrees CA$84M Investment into Black Pellet Production Plants",
                "source_publisher": "Power Wood Canada Corp. / GlobeNewswire",
                "signal_date": datetime(2026, 8, 4, tzinfo=timezone.utc),
                "reason": (
                    "On August 4, 2026, Power Wood Canada Corp. announced that parent Power Wood Holdings "
                    "agreed terms for up to C$84 million from Chair Capital to advance two Northern Alberta "
                    "black-pellet plants and a rail spur. C$42 million is intended for the Peace River plant "
                    "near La Crete and rail infrastructure, with up to C$42 million released by milestones for "
                    "the Hay Meadow plant near High Level; the two facilities target 700,000 tonnes of combined "
                    "annual output under 10-year take-or-pay agreements with Japanese energy companies. "
                    "Inference: two greenfield plants, milestone-based financing, export logistics, and a high-volume "
                    "production ramp create urgent factory-planning, throughput, maintenance, and quality-control needs."
                ),
                "pain": (
                    "Must plan and ramp two greenfield pellet plants plus rail logistics while controlling "
                    "throughput, process quality, maintenance, and milestone delivery."
                ),
                "expansion": (
                    "Agreed terms for up to C$84 million to build two Northern Alberta plants targeting "
                    "700,000 tonnes of annual black-pellet capacity and supporting export rail infrastructure."
                ),
            },
            {
                "source_url": POWER_WOOD_PAPER_ADVANCE_URL,
                "source_title": "Power Wood Agrees C$84M Black Pellet Financing",
                "source_publisher": "Paper Advance",
                "signal_date": datetime(2026, 8, 19, tzinfo=timezone.utc),
                "reason": (
                    "On August 19, 2026, Paper Advance independently reported the proposed C$84 million "
                    "financing for Power Wood's Peace River plant near La Crete, its rail connection, and the "
                    "Hay Meadow plant near High Level. The report states the first C$42 million is expected at "
                    "financial close and the second commitment will be released as construction milestones are "
                    "met; inference: schedule, factory-layout, production-readiness, and milestone reporting must "
                    "stay synchronized before capital tranches and customer offtake obligations come due."
                ),
                "pain": (
                    "Must synchronize construction milestones, factory readiness, process capacity, and export "
                    "logistics across two sites before milestone financing and offtake obligations mature."
                ),
                "expansion": (
                    "Independent trade coverage corroborated the C$84 million staged financing for two Alberta "
                    "black-pellet plants and related rail infrastructure."
                ),
            },
        ],
        "keyword_ids": (5,),
        "keyword_source_url": POWER_WOOD_GNW_URL,
        "keyword_source_title": "Power Wood Holdings Agrees CA$84M Investment into Black Pellet Production Plants",
        "keyword_source_publisher": "Power Wood Canada Corp. / GlobeNewswire",
        "signal_label": "C$84M staged financing advances two 700,000-tonne pellet plants",
        "signal_date": datetime(2026, 8, 4, tzinfo=timezone.utc),
        "challenge_summary": (
            "On August 4, 2026, Power Wood announced terms for up to C$84 million to advance the Peace River "
            "black-pellet plant near La Crete, a rail spur, and the Hay Meadow plant near High Level; combined "
            "target capacity is 700,000 tonnes per year under 10-year take-or-pay agreements with Japanese buyers. "
            "Funding is staged as an initial C$42 million plus up to C$42 million tied to construction milestones; "
            "inference: two-site factory planning, production ramp, quality control, maintenance, and export logistics "
            "must remain synchronized. The milestone structure and customer commitments make production-readiness "
            "controls urgent now."
        ),
        "why_relevant": (
            "Tecnomatix can model plant layout, material flow, rail interfaces, and commissioning scenarios before "
            "capital is locked in; Opcenter can provide production visibility, process-quality records, and traceability "
            "once the lines ramp. The practical outcome is lower commissioning risk and a clearer path to meeting "
            "capacity, financing, and offtake milestones across both facilities."
        ),
        "qualification_status": "qualified",
        "opportunity_score": 92,
        "manufacturing_fit_score": 98,
        "trigger_score": 98,
        "solution_fit_score": 90,
        "evidence_quality_score": 95,
    },
    {
        "company_name": "IMT Precision",
        "company_domain": "imtprecision.com",
        "company_url": "https://imtprecision.com/",
        "location": "Ingersoll, Ontario, Canada",
        "industry": "Precision projectile-body, defence, aerospace, and heavy-equipment manufacturing",
        "products": ["Teamcenter", "Tecnomatix", "Opcenter"],
        "identity": CompanyIdentityEvidence(
            official_name="IMT Precision",
            official_website_url="https://imtprecision.com/",
            corroborating_urls=(IMT_GOV_URL, IMT_HEART_FM_URL),
        ),
        "signals": [
            {
                "source_url": IMT_GOV_URL,
                "source_title": "Minister McGuinty announces investment of $1.4 billion into Domestic Ammunition Production",
                "source_publisher": "National Defence / Government of Canada",
                "signal_date": datetime(2026, 3, 18, tzinfo=timezone.utc),
                "reason": (
                    "On March 18, 2026, National Defence announced up to C$305.4 million for IMT Precision "
                    "to establish an Ingersoll facility producing empty metal shells for modern 155 mm artillery "
                    "projectiles. The government expects at least 75 full-time jobs and up to 400 jobs at full "
                    "production; IMT's existing operation includes forging, CNC machining, heat treatment, coating, "
                    "inspection, and complete M795 and M1128 production lines. Inference: the new facility must scale "
                    "regulated configurations, tooling and process plans, inspection evidence, lot genealogy, and "
                    "capacity without compromising Controlled Goods and ISO 9001 requirements."
                ),
                "pain": (
                    "Must industrialize a new 155 mm shell-body facility while controlling product configuration, "
                    "tooling, routings, inspection evidence, quality genealogy, and a large production ramp."
                ),
                "expansion": (
                    "Awarded up to C$305.4 million for a new Ingersoll 155 mm shell-body facility expected to "
                    "support at least 75 and up to 400 jobs at full production."
                ),
            },
            {
                "source_url": IMT_HEART_FM_URL,
                "source_title": "Ottawa Funding New Facility for IMT Precision",
                "source_publisher": "104.7 Heart FM",
                "signal_date": datetime(2026, 3, 19, tzinfo=timezone.utc),
                "reason": (
                    "On March 19, 2026, 104.7 Heart FM independently reported more than C$305 million in federal "
                    "support for IMT Precision's new Ingersoll facility focused on 155 mm projectile shell cases, "
                    "with roughly 300 new jobs cited locally. This corroborates a material greenfield production "
                    "ramp; inference: program configuration, manufacturing planning, inspection, and traceability "
                    "must mature before staffing and equipment reach full scale."
                ),
                "pain": (
                    "Must make program configuration, process planning, inspection, and traceability repeatable "
                    "before hundreds of new staff and new production equipment reach full scale."
                ),
                "expansion": (
                    "Independent local reporting corroborated more than C$305 million for a new 155 mm shell-case "
                    "facility and a roughly 300-job expansion."
                ),
            },
        ],
        "keyword_ids": (14,),
        "keyword_source_url": IMT_GOV_URL,
        "keyword_source_title": "Minister McGuinty announces investment of $1.4 billion into Domestic Ammunition Production",
        "keyword_source_publisher": "National Defence / Government of Canada",
        "signal_label": "C$305.4M builds new 155 mm projectile-shell facility",
        "signal_date": datetime(2026, 3, 18, tzinfo=timezone.utc),
        "challenge_summary": (
            "On March 18, 2026, National Defence committed up to C$305.4 million for IMT Precision to establish "
            "a new Ingersoll facility for empty metal shells used in modern 155 mm artillery projectiles, with at "
            "least 75 jobs and up to 400 jobs at full production. IMT already operates forging, CNC machining, heat "
            "treatment, coating, inspection, and complete M795/M1128 lines; inference: the expansion sharply increases "
            "configuration, tooling, routing, quality-genealogy, and Controlled Goods traceability pressure. The new "
            "facility and sovereign-capacity mandate make those controls urgent during industrialization."
        ),
        "why_relevant": (
            "Teamcenter can govern projectile variants, BOMs, drawings, tooling, routings, and approved changes; "
            "Tecnomatix can validate the new line and material flow; Opcenter can enforce execution, inspection, lot "
            "genealogy, and non-conformance control. The business outcome is a faster compliant ramp with fewer "
            "configuration escapes and more defensible delivery evidence for National Defence."
        ),
        "qualification_status": "qualified",
        "opportunity_score": 98,
        "manufacturing_fit_score": 100,
        "trigger_score": 100,
        "solution_fit_score": 99,
        "evidence_quality_score": 100,
    },
    {
        "company_name": "Northern Transformer Corporation",
        "company_domain": "northerntransformer.com",
        "company_url": "https://www.northerntransformer.com/",
        "location": "Maple and Innisfil, Ontario, Canada",
        "industry": "High-voltage large power transformer design, manufacturing, and testing",
        "products": ["Teamcenter", "Tecnomatix", "Opcenter"],
        "identity": CompanyIdentityEvidence(
            official_name="Northern Transformer Corporation",
            official_website_url="https://www.northerntransformer.com/",
            corroborating_urls=(NORTHERN_PLANT_URL,),
        ),
        "signals": [
            {
                "source_url": NORTHERN_OFFICIAL_URL,
                "source_title": "Northern Transformer Breaks Ground on Large Power Transformer Facility",
                "source_publisher": "Northern Transformer Corporation",
                "signal_date": datetime(2025, 9, 18, tzinfo=timezone.utc),
                "reason": (
                    "On September 18, 2025, Northern Transformer broke ground on a C$207 million, 183,000-square-foot "
                    "Innisfil facility for designing, manufacturing, and testing 230-500 kV large power transformers "
                    "up to 750 MVA, supported by C$6 million from FedDev Ontario and C$10.5 million from Ontario. "
                    "The company's current site states construction is underway and contrasts the new capability with "
                    "its Maple plant's current 100 MVA/240 kV range. Inference: the sevenfold MVA step-up and new test "
                    "facility create sustained engineering-change, supplier, factory-flow, inspection, and test-record "
                    "complexity while construction and production planning continue."
                ),
                "pain": (
                    "Must scale from 100 MVA/240 kV products to 750 MVA/500 kV transformers while coordinating "
                    "engineering configurations, suppliers, new factory flow, inspection, and high-voltage testing."
                ),
                "expansion": (
                    "Building a C$207 million, 183,000-square-foot Innisfil factory for 230-500 kV transformers "
                    "up to 750 MVA; construction remains underway."
                ),
            },
            {
                "source_url": NORTHERN_PLANT_URL,
                "source_title": "Northern Transformer invests $207M to build new facility in Innisfil",
                "source_publisher": "Plant Magazine",
                "signal_date": datetime(2025, 9, 19, tzinfo=timezone.utc),
                "reason": (
                    "On September 19, 2025, Plant Magazine independently reported Northern Transformer's C$207 million "
                    "Innisfil factory investment for large high-voltage transformers. The expansion adds a new product "
                    "and test envelope rather than merely more floor space; inference: product configuration, line "
                    "planning, quality evidence, and production visibility must be established while the active "
                    "construction project moves toward commissioning."
                ),
                "pain": (
                    "Must establish repeatable configuration, factory-planning, quality, and test-data controls for "
                    "a much larger transformer class before the new facility commissions."
                ),
                "expansion": (
                    "Independent manufacturing coverage corroborated the C$207 million Innisfil large-transformer facility."
                ),
            },
        ],
        "keyword_ids": (5,),
        "keyword_source_url": NORTHERN_OFFICIAL_URL,
        "keyword_source_title": "Northern Transformer Breaks Ground on Large Power Transformer Facility",
        "keyword_source_publisher": "Northern Transformer Corporation",
        "signal_label": "C$207M plant expands transformer capability to 750 MVA and 500 kV",
        "signal_date": datetime(2025, 9, 18, tzinfo=timezone.utc),
        "challenge_summary": (
            "Northern Transformer is actively building a C$207 million, 183,000-square-foot Innisfil facility to "
            "manufacture and test 230-500 kV transformers up to 750 MVA, compared with the Maple plant's current "
            "100 MVA/240 kV range. The September 18, 2025 groundbreaking is older than the preferred 180-day window, "
            "but the official site confirms construction remains underway; inference: the larger product envelope "
            "creates sustained configuration, supplier, factory-flow, inspection, and test-record pressure. The live "
            "construction phase makes digital production and engineering controls timely before commissioning."
        ),
        "why_relevant": (
            "Teamcenter can govern transformer variants, drawings, BOMs, supplier data, and engineering changes; "
            "Tecnomatix can model the new factory and handling sequence for very large units; Opcenter can provide "
            "production, inspection, and test traceability. The practical outcome is a more controlled commissioning "
            "and ramp with fewer late layout changes, quality escapes, and record gaps."
        ),
        "qualification_status": "qualified",
        "opportunity_score": 90,
        "manufacturing_fit_score": 100,
        "trigger_score": 86,
        "solution_fit_score": 96,
        "evidence_quality_score": 96,
    },
]


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

    published = {keyword_id: 0 for keyword_id in keywords_before}
    persisted: list[dict] = []
    for prospect in PROSPECTS:
        for evidence in prospect["signals"]:
            verify_company_identity(make_signal(prospect, evidence), prospect["identity"])

        evidence_results = []
        company = None
        for evidence in prospect["signals"]:
            saved, company = database.persist_verified_signal(
                make_signal(prospect, evidence), prospect["identity"]
            )
            evidence_results.append(
                {
                    "source_url": evidence["source_url"],
                    "created": saved.created,
                    "duplicate_url": saved.duplicate_url,
                }
            )
        if company is None:
            raise RuntimeError(f"No company result for {prospect['company_name']}")

        links = []
        for keyword_id in prospect["keyword_ids"]:
            row = database.record_keyword_company(
                keyword_id,
                prospect["company_name"],
                prospect["company_domain"],
                source_url=prospect["keyword_source_url"],
                source_title=prospect["keyword_source_title"],
                source_publisher=prospect["keyword_source_publisher"],
                signal_label=prospect["signal_label"],
                signal_date=prospect["signal_date"],
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
                raise RuntimeError(
                    f"Could not link {prospect['company_name']} to keyword {keyword_id}"
                )
            published[keyword_id] += 1
            links.append(
                {
                    "keyword_id": keyword_id,
                    "company_id": row.company_id,
                    "status": row.qualification_status,
                    "opportunity_score": row.opportunity_score,
                }
            )
        persisted.append(
            {
                "company_id": links[0]["company_id"],
                "company_name": company.company_name,
                "company_domain": company.company_domain,
                "signal_count": company.signal_count,
                "evidence": evidence_results,
                "links": links,
            }
        )

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
