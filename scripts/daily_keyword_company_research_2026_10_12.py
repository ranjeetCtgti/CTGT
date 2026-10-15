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


PROSPECTS = [
    {
        "company_name": "Altex Inc.",
        "company_domain": "altexdesign.com",
        "company_url": "https://www.altexdesign.com/",
        "linkedin_url": "https://ca.linkedin.com/company/altexinc",
        "location": "Terrebonne, Quebec, Canada",
        "industry": "Made-to-measure architectural window-covering systems manufacturing",
        "products": ["Teamcenter", "Tecnomatix"],
        "identity": CompanyIdentityEvidence(
            official_name="Altex Inc.",
            official_website_url="https://www.altexdesign.com/en/",
            corroborating_urls=(
                "https://journallavoix.com/economie/terrebonne-altex-recoit-plus-de-5-m-pour-automatiser-sa-production",
                "https://www.newswire.ca/news-releases/investissement-quebec-and-bdc-provide-more-than-5-million-to-altex-to-accelerate-growth-across-canada-and-the-united-states--811129603.html",
            ),
            linkedin_url="https://ca.linkedin.com/company/altexinc",
            linkedin_website_url="https://www.altexdesign.com/",
        ),
        "source_url": "https://journallavoix.com/economie/terrebonne-altex-recoit-plus-de-5-m-pour-automatiser-sa-production",
        "source_title": "Terrebonne – Altex reçoit plus de 5 M$ pour automatiser sa production",
        "source_publisher": "Journal La Voix",
        "signal_date": datetime(2026, 8, 13, tzinfo=timezone.utc),
        "signal_label": "C$5M financing automates Newton-system machining and assembly",
        "challenge_summary": (
            "On August 13, 2026, Journal La Voix reported that Investissement Québec and BDC supplied more than "
            "C$5 million to Terrebonne manufacturer Altex to automate aluminum machining and assembly for its patented "
            "Newton High-Speed Lite-Lift window-covering technology. Altex said the investment should cut direct labour "
            "by more than 15%, support 2026 sales above C$50 million, and help deliver more than C$10 million in "
            "architectural contracts. Inference: automating a configured-to-order product family while scaling Canadian "
            "and U.S. sales increases product-variant, released-BOM, process-planning, tooling, quality, and change-control pressure."
        ),
        "why_relevant": (
            "Teamcenter can govern Newton product variants, component revisions, supplier data, and released manufacturing "
            "structures. Tecnomatix can model the new machining and assembly processes before equipment and work instructions "
            "are committed, helping Altex protect throughput and quality during the ramp. The financing is already tied to "
            "specific 2026 automation and contract-delivery targets, so the implementation window is current."
        ),
        "pain": "Must scale a configured architectural-product portfolio while synchronizing aluminum parts, revisions, tooling, and automated machining and assembly processes.",
        "expansion": "Secured more than C$5 million to automate Newton-system aluminum machining and assembly and support more than C$10 million in architectural contracts.",
        "keyword_ids": [8],
        "qualification_status": "qualified",
        "opportunity_score": 91,
        "manufacturing_fit_score": 96,
        "trigger_score": 94,
        "solution_fit_score": 92,
        "evidence_quality_score": 95,
        "expected_existing": False,
    },
    {
        "company_name": "Next Hydrogen Solutions Inc.",
        "company_domain": "nexthydrogen.com",
        "company_url": "https://nexthydrogen.com/",
        "linkedin_url": "https://ca.linkedin.com/company/next-hydrogen",
        "location": "Mississauga, Ontario, Canada",
        "industry": "Industrial water-electrolyser design and manufacturing",
        "products": ["Teamcenter", "Simcenter"],
        "identity": CompanyIdentityEvidence(
            official_name="Next Hydrogen Solutions Inc.",
            official_website_url="https://nexthydrogen.com/",
            corroborating_urls=(
                "https://www.canada.ca/en/natural-resources-canada/news/2026/09/canada-invests-in-clean-fuels-innovation-in-ontario.html",
            ),
            linkedin_url="https://ca.linkedin.com/company/next-hydrogen",
            linkedin_website_url="http://www.nexthydrogen.com",
        ),
        "source_url": "https://www.canada.ca/en/natural-resources-canada/news/2026/09/canada-invests-in-clean-fuels-innovation-in-ontario.html",
        "source_title": "Canada invests in clean fuels innovation in Ontario",
        "source_publisher": "Natural Resources Canada",
        "signal_date": datetime(2026, 9, 15, tzinfo=timezone.utc),
        "signal_label": "C$2M funds Gen3 industrial-electrolyser electrode scale-up",
        "challenge_summary": (
            "On September 15, 2026, Natural Resources Canada awarded C$2 million to Next Hydrogen for fabrication and "
            "integration of new high-performance electrodes in its third-generation water-electrolyser module. The funded "
            "work is intended to create a scalable fabrication method while improving electrolyser efficiency, performance, "
            "and cost; the Mississauga company already builds large on-site hydrogen systems, including a 650-kg/day Gen2 "
            "installation. Inference: introducing a new electrode and module generation creates configuration, supplier, "
            "test-data, manufacturing-process, thermal-fluid, durability, and engineering-change complexity."
        ),
        "why_relevant": (
            "Teamcenter can control Gen2-to-Gen3 module structures, electrode revisions, supplier specifications, and released "
            "manufacturing changes. Simcenter can support electrochemical, thermal-fluid, structural, and balance-of-plant "
            "validation as Next Hydrogen pursues higher performance at lower cost. The September award explicitly funds the "
            "fabrication and integration step, making engineering-system support timely now."
        ),
        "pain": "Must industrialize a new electrode fabrication method and integrate it into a third-generation electrolyser while controlling configurations, suppliers, tests, and performance trade-offs.",
        "expansion": "Received C$2 million to develop scalable electrode fabrication and integrate it into Next Hydrogen's Gen3 electrolyser module.",
        "keyword_ids": [5, 8],
        "qualification_status": "qualified",
        "opportunity_score": 92,
        "manufacturing_fit_score": 97,
        "trigger_score": 92,
        "solution_fit_score": 94,
        "evidence_quality_score": 97,
        "expected_existing": False,
    },
    {
        "company_name": "CERT Systems Inc.",
        "company_domain": "co2cert.com",
        "company_url": "https://co2cert.com/",
        "linkedin_url": "https://ca.linkedin.com/company/co2cert",
        "location": "Toronto, Ontario, Canada",
        "industry": "Industrial electrochemical CO2-conversion systems",
        "products": ["Simcenter"],
        "identity": CompanyIdentityEvidence(
            official_name="CERT Systems Inc.",
            official_website_url="https://co2cert.com/",
            corroborating_urls=(
                "https://www.canada.ca/en/natural-resources-canada/news/2026/09/canada-invests-in-clean-fuels-innovation-in-ontario.html",
                "https://lei.bloomberg.com/leis/view/25490082Z7PGUZEEL022",
            ),
            linkedin_url="https://ca.linkedin.com/company/co2cert",
            linkedin_website_url="http://co2cert.com",
        ),
        "source_url": "https://www.canada.ca/en/natural-resources-canada/news/2026/09/canada-invests-in-clean-fuels-innovation-in-ontario.html#wb-auto-4",
        "source_title": "Canada invests in clean fuels innovation in Ontario — CERT Systems project",
        "source_publisher": "Natural Resources Canada",
        "signal_date": datetime(2026, 9, 15, tzinfo=timezone.utc),
        "signal_label": "C$2M advances direct-air-to-ethylene system for sustainable aviation fuel",
        "challenge_summary": (
            "On September 15, 2026, Natural Resources Canada awarded C$2 million to CERT Systems for a direct-air-to-ethylene "
            "project intended to support sustainable aviation fuel and reduce lifecycle emissions by an estimated 93.8%. "
            "CERT's Toronto team is developing modular direct-CO2 electrolysis hardware that converts captured carbon into "
            "ethylene. Inference: the funded development creates multiphysics scale-up, electrode and stack validation, "
            "balance-of-plant integration, durability-test, and cost-performance optimization work, but commercial production timing remains incomplete."
        ),
        "why_relevant": (
            "Simcenter is the smallest defensible fit for electrochemical, thermal-fluid, structural, and system-level studies "
            "needed to translate lab performance into a scalable module. The award creates an active validation budget and a "
            "defined aviation-fuel use case, while the watchlist status reflects the lack of a disclosed production facility or manufacturing-ramp date."
        ),
        "pain": "Must scale direct-CO2 electrolysis from development hardware toward modular industrial performance while validating coupled electrochemical, thermal-fluid, durability, and cost behavior.",
        "expansion": "Received C$2 million for a direct-air-to-ethylene project supporting sustainable aviation fuel.",
        "keyword_ids": [5, 8],
        "qualification_status": "watchlist",
        "opportunity_score": 62,
        "manufacturing_fit_score": 73,
        "trigger_score": 80,
        "solution_fit_score": 72,
        "evidence_quality_score": 93,
        "expected_existing": False,
    },
    {
        "company_name": "Avalon Holographics",
        "company_domain": "avalonholographics.com",
        "company_url": "https://avalonholographics.com/",
        "linkedin_url": "https://www.linkedin.com/company/avalon-holographics/",
        "location": "St. John's, Newfoundland and Labrador, Canada",
        "industry": "Holographic display hardware design and manufacturing",
        "products": ["Teamcenter", "Simcenter", "Polarion"],
        "identity": CompanyIdentityEvidence(
            official_name="Avalon Holographics",
            official_website_url="https://avalonholographics.com/about-us/",
            corroborating_urls=(
                "https://lockheedmartin.ca.mediaroom.com/index.php?item=122594&s=2429",
                "https://www.vanguarddefence.ca/p/a-decade-into-holographic-displays-avalon-lands-its-biggest-defence-partner",
            ),
            linkedin_url="https://www.linkedin.com/company/avalon-holographics/",
            linkedin_website_url="http://www.avalonholographics.com",
        ),
        "source_url": "https://lockheedmartin.ca.mediaroom.com/index.php?item=122594&s=2429",
        "source_title": "Lockheed Martin Canada Invests $11.7 Million in Newfoundland and Labrador's Avalon Holographics",
        "source_publisher": "Lockheed Martin Canada",
        "signal_date": datetime(2026, 9, 9, tzinfo=timezone.utc),
        "signal_label": "C$11.7M Lockheed commitment advances defence holographic-display platform",
        "challenge_summary": (
            "On September 9, 2026, Lockheed Martin Canada announced an C$11.7 million commitment to Avalon Holographics, "
            "including a new C$5.6 million contract after an initial C$6.1 million phase, to continue developing defence "
            "simulation and command-and-control holographic displays. Avalon's NOVAC platform is developed by more than 80 "
            "staff across St. John's headquarters and an Edmonton R&D and fabrication lab. Inference: successive defence phases "
            "increase optical, electronics, mechanical, thermal, software, supplier, configuration, requirements, and verification complexity."
        ),
        "why_relevant": (
            "Teamcenter can govern NOVAC hardware, electronics, suppliers, and released configurations; Simcenter can support "
            "optical-adjacent thermal, structural, and electronics-cooling validation. Polarion can connect defence requirements, "
            "software defects, qualification tests, and acceptance evidence. The new contract is active funding for the next "
            "development phase, so configuration and verification discipline matter before further customer deliveries."
        ),
        "pain": "Must mature a complex holographic-display platform through successive defence phases while coordinating optics, electronics, mechanics, software, suppliers, requirements, and test evidence.",
        "expansion": "Received an C$11.7 million Lockheed Martin Canada commitment, including a new C$5.6 million development contract.",
        "keyword_ids": [8, 14],
        "qualification_status": "qualified",
        "opportunity_score": 93,
        "manufacturing_fit_score": 93,
        "trigger_score": 95,
        "solution_fit_score": 95,
        "evidence_quality_score": 97,
        "expected_existing": False,
    },
    {
        "company_name": "Volatus Aerospace Inc.",
        "company_domain": "volatusaerospace.com",
        "company_url": "https://volatusaerospace.com/",
        "linkedin_url": None,
        "location": "Mirabel, Quebec, Canada",
        "industry": "Uncrewed aircraft systems manufacturing and systems integration",
        "products": ["Teamcenter", "Tecnomatix", "Opcenter"],
        "identity": CompanyIdentityEvidence(
            official_name="Volatus Aerospace Inc.",
            official_website_url="https://volatusaerospace.com/",
            corroborating_urls=(
                "https://www.canadianmanufacturing.com/manufacturing/volatus-and-kraus-hamdani-aerospace-partner-on-canadian-persistent-intelligence-capability-320518/",
            ),
        ),
        "source_url": "https://volatusaerospace.com/insights/opening-of-mirabel-facility/",
        "source_title": "Volatus Aerospace Marks Official Opening of Mirabel Facility as Canadian Manufacturing Operations Scale",
        "source_publisher": "Volatus Aerospace",
        "signal_date": datetime(2026, 9, 29, tzinfo=timezone.utc),
        "signal_label": "53,000-sq-ft Mirabel plant scales Canadian drone manufacturing",
        "challenge_summary": (
            "On September 29, 2026, Volatus Aerospace opened a 53,000-square-foot Mirabel facility for drone manufacturing "
            "and systems integration, including production of drone docking stations and integration of V-Series and autonomous "
            "systems. The site consolidates expanding Canadian manufacturing work for defence and commercial programs. "
            "Inference: the larger operation increases product-configuration, supplier, routing, work-instruction, quality, "
            "traceability, capacity-planning, and production-visibility demands across multiple uncrewed-aircraft programs."
        ),
        "why_relevant": (
            "Teamcenter can govern aircraft, payload, docking-station, and customer configurations with supplier and change data. "
            "Tecnomatix can plan the new facility's mixed assembly and integration flows, while Opcenter can provide execution, "
            "quality, genealogy, and production visibility. The facility is open and programs are moving into the space now, "
            "creating an immediate window to standardize operations before volume and variants grow."
        ),
        "pain": "Must scale mixed drone, docking-station, and systems-integration programs in a new facility while controlling configurations, processes, quality genealogy, suppliers, and shop-floor visibility.",
        "expansion": "Opened a 53,000-square-foot Mirabel manufacturing and systems-integration facility for V-Series, autonomous systems, and docking stations.",
        "keyword_ids": [7, 9, 13, 14],
        "qualification_status": "qualified",
        "opportunity_score": 95,
        "manufacturing_fit_score": 98,
        "trigger_score": 97,
        "solution_fit_score": 98,
        "evidence_quality_score": 94,
        "expected_existing": True,
    },
]


REVIEW = {
    1: (17, 7, 13, 0, 0, 4), 2: (18, 8, 13, 0, 0, 5), 3: (16, 5, 12, 0, 0, 4),
    4: (18, 7, 13, 0, 0, 5), 5: (22, 10, 15, 1, 1, 5), 7: (19, 8, 14, 1, 0, 4),
    8: (28, 15, 19, 3, 1, 5), 9: (19, 7, 14, 1, 0, 4), 10: (17, 6, 13, 0, 0, 4),
    11: (16, 6, 12, 0, 0, 4), 12: (18, 8, 15, 0, 0, 3), 13: (19, 8, 14, 1, 0, 4),
    14: (22, 10, 16, 2, 0, 4), 15: (18, 8, 14, 0, 0, 4), 16: (19, 9, 16, 0, 0, 3),
}


def make_signal(prospect: dict) -> ExtractedSignal:
    return ExtractedSignal(
        company_name=prospect["company_name"], company_domain=prospect["company_domain"],
        company_url=prospect["company_url"], linkedin_url=prospect["linkedin_url"],
        location=prospect["location"], industry=prospect["industry"], company_industry=prospect["industry"],
        software=prospect["products"], signal_type="news", signal_source="news",
        pain_signals=[prospect["pain"]], expansion_signals=[prospect["expansion"]],
        raw_score=prospect["opportunity_score"], confidence=prospect["evidence_quality_score"] / 100,
        reason=prospect["challenge_summary"] + " " + prospect["why_relevant"],
        source_url=prospect["source_url"], source_title=prospect["source_title"],
        detected_at=prospect["signal_date"],
    )


def main() -> None:
    load_dotenv(REPO_ROOT / ".env")
    marker = json.loads(LOCK_PATH.read_text(encoding="utf-8"))
    if int(marker.get("pid", 0)) <= 0:
        raise RuntimeError("Exclusive automation lock is not held")

    database = Database(os.environ["DATABASE_URL"])
    database.initialize()
    before = {row.id: row for row in database.list_keywords()}
    if set(before) != set(REVIEW):
        raise RuntimeError(f"Persistent keyword set changed during run: {sorted(before)}")

    with database.session() as session:
        pre_by_domain = {
            row.company_domain.lower(): row
            for row in session.scalars(
                select(CompanyRecord).where(
                    func.lower(CompanyRecord.company_domain).in_([p["company_domain"] for p in PROSPECTS])
                )
            ).all()
        }
        pre_sources = set(session.scalars(
            select(SignalRecord.source_url).where(SignalRecord.source_url.in_([p["source_url"] for p in PROSPECTS]))
        ).all())

    for prospect in PROSPECTS:
        existing = prospect["company_domain"] in pre_by_domain
        resumable_partial = existing and prospect["source_url"] in pre_sources and not prospect["expected_existing"]
        if existing != prospect["expected_existing"] and not resumable_partial:
            raise RuntimeError(f"Identity precheck changed for {prospect['company_domain']}: existing={existing}")
        if prospect["source_url"] in pre_sources and not resumable_partial:
            raise RuntimeError(f"Evidence URL already exists: {prospect['source_url']}")
        verify_company_identity(make_signal(prospect), prospect["identity"])

    published_counts = {keyword_id: 0 for keyword_id in before}
    persisted = []
    for prospect in PROSPECTS:
        signal = make_signal(prospect)
        saved, company = database.persist_verified_signal(signal, prospect["identity"])
        resumed_partial = prospect["source_url"] in pre_sources and not prospect["expected_existing"]
        if company is None or (not resumed_partial and (not saved.created or saved.duplicate_url)):
            raise RuntimeError(f"Unexpected persistence result for {prospect['company_name']}: {saved}")
        with database.session() as session:
            company_id = session.scalar(
                select(CompanyRecord.id).where(
                    func.lower(CompanyRecord.company_domain) == prospect["company_domain"]
                )
            )
        if company_id is None:
            raise RuntimeError(f"Persisted company ID missing for {prospect['company_domain']}")
        links = []
        for keyword_id in prospect["keyword_ids"]:
            row = database.record_keyword_company(
                keyword_id, prospect["company_name"], prospect["company_domain"],
                source_url=prospect["source_url"], source_title=prospect["source_title"],
                source_publisher=prospect["source_publisher"], signal_label=prospect["signal_label"],
                signal_date=prospect["signal_date"], challenge_summary=prospect["challenge_summary"],
                why_relevant=prospect["why_relevant"], recommended_products=prospect["products"],
                qualification_status=prospect["qualification_status"], opportunity_score=prospect["opportunity_score"],
                manufacturing_fit_score=prospect["manufacturing_fit_score"], trigger_score=prospect["trigger_score"],
                solution_fit_score=prospect["solution_fit_score"], evidence_quality_score=prospect["evidence_quality_score"],
                seen_at=RUN_AT,
            )
            if row is None:
                raise RuntimeError(f"Could not link {prospect['company_name']} to keyword {keyword_id}")
            links.append({"keyword_id": keyword_id, "result_id": row.id})
            published_counts[keyword_id] += 1
        persisted.append({
            "company_id": company_id, "company_name": company.company_name,
            "company_domain": company.company_domain, "status": prospect["qualification_status"],
            "source_url": prospect["source_url"], "keyword_links": links,
            "new_company": not prospect["expected_existing"],
        })

    for keyword_id in sorted(before):
        if database.record_keyword_search(keyword_id, result_count=published_counts[keyword_id], error=None) is None:
            raise RuntimeError(f"Could not record keyword search {keyword_id}")

    after = {row.id: row for row in database.list_keywords()}
    for keyword_id, prior in before.items():
        current = after[keyword_id]
        if current.search_count != prior.search_count + 1 or current.last_error is not None:
            raise RuntimeError(f"Keyword audit failed for {keyword_id}")

    with database.session() as session:
        duplicate_domains = session.execute(
            select(func.lower(CompanyRecord.company_domain), func.count(CompanyRecord.id))
            .where(CompanyRecord.company_domain.is_not(None)).group_by(func.lower(CompanyRecord.company_domain))
            .having(func.count(CompanyRecord.id) > 1)
        ).all()
        duplicate_sources = session.execute(
            select(SignalRecord.source_url, func.count(SignalRecord.id)).where(SignalRecord.source_url.is_not(None))
            .group_by(SignalRecord.source_url).having(func.count(SignalRecord.id) > 1)
        ).all()
        duplicate_keyword_pairs = session.execute(
            select(KeywordCompanyResultRecord.keyword_id, KeywordCompanyResultRecord.company_id, func.count(KeywordCompanyResultRecord.id))
            .group_by(KeywordCompanyResultRecord.keyword_id, KeywordCompanyResultRecord.company_id)
            .having(func.count(KeywordCompanyResultRecord.id) > 1)
        ).all()
        eligible_count = session.scalar(select(func.count(func.distinct(KeywordCompanyResultRecord.company_id))).where(
            KeywordCompanyResultRecord.qualification_status.in_(("qualified", "watchlist"))
        ))
    if duplicate_domains or duplicate_sources or duplicate_keyword_pairs:
        raise RuntimeError(f"Post-write dedupe audit failed: {duplicate_domains}, {duplicate_sources}, {duplicate_keyword_pairs}")

    print(json.dumps({
        "run_at": RUN_AT.isoformat(), "persisted": persisted, "published_counts": published_counts,
        "eligible_company_count": eligible_count,
        "keyword_audits": [{
            "id": keyword_id, "keyword": after[keyword_id].keyword,
            "search_count_before": before[keyword_id].search_count,
            "search_count_after": after[keyword_id].search_count,
            "candidate_domains_reviewed": REVIEW[keyword_id][0],
            "new_to_ledger_domains_reviewed": REVIEW[keyword_id][1],
            "rejected_before_persistence": REVIEW[keyword_id][2],
            "qualified_published": REVIEW[keyword_id][3],
            "watchlist_published": REVIEW[keyword_id][4],
            "duplicates_or_existing_skipped": REVIEW[keyword_id][5],
            "last_error": after[keyword_id].last_error,
            "warnings": [
                "Startup Gallery directly checked; no candidate passed the official-site and dated-trigger gate",
                "X.com direct search was inaccessible because of ERR_CERT_AUTHORITY_INVALID; no safety warning was bypassed",
                "BetaKit source-specific and related-trigger searches checked",
                "NGen project, case-study, challenge, member, and news searches checked",
            ] + (["SpaceQ and AIAC news, guide, and member searches checked"] if keyword_id in {1, 7, 9, 10, 13, 14} else []),
        } for keyword_id in sorted(after)],
        "coverage": {
            "lookbacks": ["30-day", "180-day", "365-day ongoing-signal fallback"],
            "query_families": [
                "general web/news", "government funding/contracts/procurement", "specialist trade publications",
                "accelerators/investors/university spinouts", "associations/exhibitors/member directories",
                "company hiring/press/product/facility pages",
            ],
            "mandatory_sources": ["Startup Gallery", "X.com", "BetaKit", "NGen"],
            "aerospace_sources": ["SpaceQ", "AIAC", "Aero Montreal", "DAIR Aerospace"],
            "rotated_sources": [
                "Natural Resources Canada", "CanadaBuys", "federal and provincial funding news",
                "CDL", "MaRS", "Communitech", "ventureLAB Hardware Catalyst", "university spinouts",
                "APMA and OVIN", "CANSEC", "Canada's Ocean Supercluster", "Oakville Chamber of Commerce",
                "Canadian Manufacturing", "PLANT", "Newswire", "Vanguard Defence", "company press and hiring pages",
            ],
            "gap_fill_triggered": False,
            "notable_rejections": [
                "Forward Robotics was accelerator-directory discovery only without a dated primary buying trigger.",
                "Poseidon Aero was U.S.-based and outside the Canadian keyword scope.",
                "Babcock Canada was service-led for this pass and lacked a new product-manufacturing trigger.",
                "Plasman had a credible equipment investment but did not match the saved OEM/startup/funding/PLM-intent keywords.",
                "Robotics Centre, InDro, ALUULA, Photonic, PV Labs, Galaxia, Xanadu, Hanon, Kanin and Qidni were existing-domain duplicates or had no newer publishable source.",
            ],
        },
        "duplicate_audit": {"canonical_domains": 0, "source_urls": 0, "keyword_company_pairs": 0},
    }, indent=2, default=str))


if __name__ == "__main__":
    main()
