from __future__ import annotations

import json
import os
from datetime import datetime, timezone

from dotenv import load_dotenv

from db.database import Database
from enrichment.identity_verification import CompanyIdentityEvidence
from models.schema import ExtractedSignal


RUN_AT = datetime.now(timezone.utc)
SIGNAL_DATE = datetime(2026, 8, 27, tzinfo=timezone.utc)
CENGN_URL = (
    "https://www.cengn.ca/information-centre/news/"
    "six-new-cengn-living-lab-projects-announced-valued-at-4-5-million-for-canadian-startups/"
)
EIN_URL = (
    "https://tires.einnews.com/pr_news/936890432/"
    "six-new-cengn-living-lab-projects-announced-valued-at-4-5-million-for-canadian-startups"
)


PROSPECTS = {
    "avidbots": {
        "company_name": "Avidbots Corp.",
        "company_domain": "avidbots.com",
        "company_url": "https://avidbots.com/",
        "location": "Kitchener, Ontario, Canada",
        "industry": "Autonomous commercial cleaning robot design and manufacturing",
        "products": ["Teamcenter", "Polarion", "Simcenter"],
        "scores": (90, 97, 89, 94, 92),
        "pain_signals": [
            "Must redesign and validate the Kas autonomous floor-scrubbing robot against European product regulations while preserving released configurations and production readiness."
        ],
        "expansion_signals": [
            "Selected for a funded CENGN commercialization project to modify Kas for European regulatory compliance and market entry."
        ],
        "challenge_summary": (
            "On August 27, 2026, CENGN selected Avidbots for one of six commercialization projects collectively valued at C$4.5 million and supported by C$1.7 million from ISED's Strategic Response Fund. Avidbots will make design enhancements to its Kas autonomous floor-scrubbing robot so it can pass European regulations and enter the European market; the official company site confirms Avidbots designs and manufactures Kas, Neo and Neo 2W in Kitchener. Inference: regulatory redesign across mechanical, electrical, autonomy and safety functions creates immediate BOM/change-control, requirements-traceability, verification-evidence and variant-management pressure."
        ),
        "why_relevant": (
            "Teamcenter can govern Kas product structures, regulatory variants, released changes and supplier data; Polarion can trace European requirements through test cases, defects and compliance evidence. Simcenter is a defensible fit for structural, motion and system-level validation before the revised robot is released. The funded project is active now, before design changes and conformity evidence multiply across the European launch baseline."
        ),
        "identity": CompanyIdentityEvidence(
            official_name="Avidbots Corp.",
            official_website_url="https://avidbots.com/",
            corroborating_urls=(CENGN_URL, "https://avidbots.com/company/about/?d=1"),
        ),
        "evidence_url": EIN_URL,
        "source_title": "Six new CENGN Living Lab projects announced, valued at C$4.5 million",
        "source_publisher": "CENGN via EIN Presswire",
        "signal_label": "Funded Kas redesign targets European regulatory approval",
        "keywords": (2,),
    },
    "konnexio": {
        "company_name": "KONNEXIO Inc.",
        "company_domain": "konnexio.com",
        "company_url": "https://konnexio.com/",
        "location": "London, Ontario, Canada",
        "industry": "Modular assembly automation and autonomous agricultural robotics manufacturing",
        "products": ["NX", "Teamcenter", "Polarion", "Simcenter"],
        "scores": (87, 95, 87, 92, 91),
        "pain_signals": [
            "Must convert the modular agroTRAX autonomous platform from a proven prototype into a commercially ready field robot and validate a UV-C treatment module in tunnel-grown strawberries."
        ],
        "expansion_signals": [
            "Selected for a funded CENGN commercialization project using the University of Waterloo RoboHub Connected Robotics Living Lab."
        ],
        "challenge_summary": (
            "On August 27, 2026, CENGN selected KONNEXIO for one of six commercialization projects collectively valued at C$4.5 million and backed by C$1.7 million from ISED's Strategic Response Fund. The project moves agroTRAX from a proven prototype toward commercial readiness by field-validating its modular autonomous architecture, active suspension, navigation and a UV-C treatment module for tunnel-grown strawberries; KONNEXIO's official site confirms the London company designs and builds modular automation and test machines. Inference: commercializing configurable field hardware creates product-variant, interface, durability, safety, requirements/test and controlled-release complexity."
        ),
        "why_relevant": (
            "NX and Teamcenter can control the modular robot design, interfaces, revisions and released configurations; Polarion can connect field, safety and treatment requirements to tests and defects. Simcenter can support suspension, structural and system-performance validation under variable agricultural conditions. The funded field-validation project is underway now, making this the practical window to establish a governed product baseline before commercialization."
        ),
        "identity": CompanyIdentityEvidence(
            official_name="KONNEXIO Inc.",
            official_website_url="https://konnexio.com/",
            corroborating_urls=(CENGN_URL,),
        ),
        "evidence_url": CENGN_URL,
        "source_title": "Six New CENGN Living Lab Projects Announced, Valued at $4.5 Million for Canadian Startups",
        "source_publisher": "CENGN",
        "signal_label": "Funded agroTRAX field validation advances commercial readiness",
        "keywords": (2,),
    },
}


# Counts reflect result-level review after source-specific searches and identity
# comparison; narrow/blocked searches are reported rather than padded.
COVERAGE = {
    1: (10, 6, 4, 3, ["Startup Gallery", "X public/X-ray", "BetaKit", "NGen", "SpaceQ", "AIAC", "ventureLAB HCI", "Canada.ca"], "Startup Gallery returned zero relevant Canadian results; direct X was certificate-blocked. Aerospace formation-date evidence remained insufficient."),
    2: (19, 10, 7, 6, ["Startup Gallery", "X public/X-ray", "BetaKit", "NGen", "CENGN Living Labs", "ventureLAB HCI", "Velocity", "Automate Canada"], "Avidbots and KONNEXIO passed. JPlug, LatenceTech and Zighra were software-led; SoilTeck lacked sufficient product-engineering complexity; older robotics results were existing duplicates."),
    3: (11, 7, 4, 4, ["Startup Gallery", "X public/X-ray", "BetaKit", "NGen", "CanadaBuys", "Marine Log", "Ocean Supercluster", "Shipbuilding Association of Canada"], "No shipbuilder with a new committed production trigger cleared the gate; software/service suppliers and procurement-pool entries were rejected."),
    4: (12, 7, 5, 4, ["Startup Gallery", "X public/X-ray", "BetaKit", "NGen", "APMA", "OVIN", "Electric Autonomy Canada", "MaRS"], "KONNEXIO is an automation supplier rather than an automotive startup/OEM; Hanon is an established foreign-headquartered supplier and was not published under this keyword."),
    5: (14, 8, 6, 5, ["Startup Gallery", "X public/X-ray", "BetaKit", "NGen", "Canada.ca", "PLANT", "BDC", "Electric Autonomy Canada"], "Recent clean-energy searches mainly rediscovered Volta, EnerPure, CES and other existing identities; no new exact-fit operator cleared the gate."),
    7: (11, 7, 4, 3, ["Startup Gallery", "X public/X-ray", "BetaKit", "NGen", "SpaceQ", "AIAC", "Aero Montreal", "DAIR Aerospace"], "SpaceQ and AIAC were directly checked; named launch and drone companies were existing or lacked a new publishable contract."),
    8: (18, 10, 8, 6, ["Startup Gallery", "X public/X-ray", "BetaKit", "NGen", "CENGN Living Labs", "BDC", "ventureLAB HCI", "Communitech"], "CENGN produced physical-product leads, but the shared program did not disclose company-level funding amounts; only the exact robotics keyword received the two qualified links."),
    9: (12, 7, 5, 4, ["Startup Gallery", "X public/X-ray", "BetaKit", "NGen", "SpaceQ", "AIAC", "Skies", "Aero Montreal"], "Direct SpaceQ and AIAC checks mostly rediscovered Telesat, MDA, NordSpace and other existing aerospace identities."),
    10: (10, 7, 3, 3, ["Startup Gallery", "X public/X-ray", "BetaKit", "NGen", "AIAC directory", "Canadian Metalworking", "CADSI/CANSEC", "CanadaBuys"], "AIAC profiles were discovery-only; no new Tier 1/Tier 2 supplier had both identity proof and a dated operational trigger."),
    11: (12, 7, 5, 4, ["Startup Gallery", "X public/X-ray", "BetaKit", "NGen", "APMA", "OVIN", "Electric Autonomy Canada", "OEM press pages"], "Searches primarily rediscovered GM, Volta and existing suppliers; Honda's paused investment was not a positive trigger."),
    12: (8, 5, 3, 2, ["Startup Gallery", "X public/X-ray", "BetaKit", "NGen", "PLANT", "Canadian Manufacturing", "CME", "manufacturer hiring pages"], "No new manufacturer exposed a verified current ERP/PLM integration trigger; software vendors and consultants were rejected."),
    13: (15, 9, 6, 5, ["Startup Gallery", "X public/X-ray", "BetaKit", "NGen", "CENGN Living Labs", "CanadaBuys DDI", "OVIN", "company press pages"], "CanadaBuys listed 142 DDI supply arrangements, but C$1 pre-qualification instruments do not establish committed production and remained discovery-only."),
    14: (18, 11, 7, 6, ["Startup Gallery", "X public/X-ray", "BetaKit", "NGen", "CanadaBuys DDI", "SpaceQ", "AIAC", "CADSI/CANSEC"], "Arcanus, Nusakan, Scentroid, Doveka and other DDI pool members lacked committed-work evidence; AP's defence-manufacturing examples were non-fit or existing."),
    15: (13, 8, 5, 4, ["Startup Gallery", "X public/X-ray", "BetaKit", "NGen", "APMA", "OVIN", "Electric Autonomy Canada", "French Quebec searches"], "No new Canadian EV startup cleared identity plus dated-trigger gates; supplier and infrastructure-only results were rejected."),
    16: (8, 5, 3, 2, ["Startup Gallery", "X public/X-ray", "BetaKit", "NGen", "CME", "PLANT", "manufacturer hiring pages", "French PLM/MES searches"], "No new end-user manufacturer explicitly seeking PLM was verified; software providers and consulting profiles were rejected."),
}


def make_signal(prospect: dict[str, object]) -> ExtractedSignal:
    opportunity, _manufacturing, _trigger, _solution, evidence_score = prospect["scores"]
    return ExtractedSignal(
        company_name=str(prospect["company_name"]),
        company_domain=str(prospect["company_domain"]),
        company_url=str(prospect["company_url"]),
        location=str(prospect["location"]),
        industry=str(prospect["industry"]),
        company_industry=str(prospect["industry"]),
        software=list(prospect["products"]),
        signal_type="news",
        signal_source="news",
        pain_signals=list(prospect["pain_signals"]),
        expansion_signals=list(prospect["expansion_signals"]),
        raw_score=int(opportunity),
        confidence=int(evidence_score) / 100,
        reason=str(prospect["challenge_summary"]),
        source_url=str(prospect["evidence_url"]),
        source_title=str(prospect["source_title"]),
        detected_at=SIGNAL_DATE,
    )


def record_link(database: Database, keyword_id: int, prospect: dict[str, object]):
    opportunity, manufacturing, trigger, solution, evidence = prospect["scores"]
    row = database.record_keyword_company(
        keyword_id,
        str(prospect["company_name"]),
        str(prospect["company_domain"]),
        source_url=str(prospect["evidence_url"]),
        source_title=str(prospect["source_title"]),
        source_publisher=str(prospect["source_publisher"]),
        signal_label=str(prospect["signal_label"]),
        signal_date=SIGNAL_DATE,
        challenge_summary=str(prospect["challenge_summary"]),
        why_relevant=str(prospect["why_relevant"]),
        recommended_products=list(prospect["products"]),
        qualification_status="qualified",
        opportunity_score=int(opportunity),
        manufacturing_fit_score=int(manufacturing),
        trigger_score=int(trigger),
        solution_fit_score=int(solution),
        evidence_quality_score=int(evidence),
        seen_at=RUN_AT,
    )
    if row is None:
        raise RuntimeError(f"Could not link {prospect['company_name']} to keyword {keyword_id}")
    return row


def main() -> None:
    load_dotenv(".env")
    database = Database(os.environ["DATABASE_URL"])
    database.initialize()
    before = {row.id: row for row in database.list_keywords()}
    if set(before) != set(COVERAGE):
        raise RuntimeError(f"Persistent keyword set changed: {sorted(before)}")

    prior_domains = {lead.company_domain for lead in database.get_leads(limit=5000)}
    published = {keyword_id: 0 for keyword_id in before}
    new_company_domains: set[str] = set()
    signal_report = []
    link_report = []

    for prospect in PROSPECTS.values():
        domain = str(prospect["company_domain"])
        if domain not in prior_domains:
            new_company_domains.add(domain)
        saved, company = database.persist_verified_signal(make_signal(prospect), prospect["identity"])
        signal_report.append(
            {
                "company": company.company_name,
                "domain": company.company_domain,
                "source_url": str(prospect["evidence_url"]),
                "created": saved.created,
                "duplicate_url": saved.duplicate_url,
                "signal_count": company.signal_count,
            }
        )
        for keyword_id in prospect["keywords"]:
            row = record_link(database, keyword_id, prospect)
            published[keyword_id] += 1
            link_report.append(
                {"keyword_id": keyword_id, "company_id": row.company_id, "company": row.company_name}
            )

    for keyword_id in sorted(before):
        if database.record_keyword_search(keyword_id, result_count=published[keyword_id]) is None:
            raise RuntimeError(f"Could not record keyword search {keyword_id}")

    after = {row.id: row for row in database.list_keywords()}
    coverage_report = {}
    for keyword_id, (reviewed, rejected, duplicates, new_domains, sources, notes) in COVERAGE.items():
        if after[keyword_id].search_count != before[keyword_id].search_count + 1:
            raise RuntimeError(f"Keyword {keyword_id} did not advance exactly once")
        coverage_report[keyword_id] = {
            "keyword": before[keyword_id].keyword,
            "lookback": "rolling 30 days, 180-day evidence fallback, 365-day ongoing discovery fallback",
            "query_families": 8,
            "visible_results_inspected": "72-80 through browser fallback where Google challenge blocked focused results",
            "candidate_domains_reviewed": reviewed,
            "new_to_ledger_domains_reviewed": new_domains,
            "rejected_before_persistence": rejected,
            "qualified_published": published[keyword_id],
            "watchlist_published": 0,
            "existing_records_upgraded_or_hidden": 1 if keyword_id == 2 else 0,
            "duplicates_skipped_or_reassessed": duplicates,
            "sources_checked": sources,
            "notes": notes,
        }

    print(
        json.dumps(
            {
                "run_at": RUN_AT.isoformat(),
                "new_company_domains": sorted(new_company_domains),
                "signals": signal_report,
                "links": link_report,
                "coverage": coverage_report,
                "blockers": [
                    "Direct X.com failed with ERR_CERT_AUTHORITY_INVALID for every keyword; public X-ray searches were completed instead and no safety warning was bypassed.",
                    "Google later presented an automated-traffic challenge; it was not solved or bypassed. Bing fallback returned 72-80 visible results per keyword but was noisy, so candidate-domain counts report only credible named companies rather than raw source domains.",
                    "The 15-domain breadth target was not met for narrow keywords after accessible named-company sources were exhausted; actual counts are reported without padding.",
                    "Startup Gallery returned zero relevant Canadian candidates for most narrow keywords; generic foreign hardware listings remained discovery-only.",
                ],
            },
            indent=2,
            default=str,
        )
    )


if __name__ == "__main__":
    main()
