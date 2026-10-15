from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from db.database import Database
from enrichment.identity_verification import CompanyIdentityEvidence
from models.schema import ExtractedSignal


RUN_AT = datetime.now(timezone.utc)

PROSPECTS = (
    {
        "company_name": "Rbot9 Inc.",
        "company_domain": "rbot9.com",
        "company_url": "https://rbot9.com/",
        "location": "Saint-Hubert, Quebec, Canada",
        "industry": "Industrial cable-robot design and manufacturing",
        "products": ["NX", "Teamcenter", "Simcenter"],
        "scores": (82, 95, 84, 80, 94),
        "signal_date": datetime(2026, 3, 11, tzinfo=timezone.utc),
        "evidence_url": "https://www.investquebec.com/fr/salle-de-presse/rbot9-securise-3-m-pour-accelerer-le-deploiement-linternational-de-ses-robots-cables",
        "source_title": "Rbot9 securise 3 M$ pour accelerer le deploiement a l'international de ses robots a cables",
        "source_publisher": "Investissement Quebec",
        "signal_label": "C$3M round funds international cable-robot deployment",
        "pain_signals": [
            "Must standardize a configurable industrial cable-robot platform across cleaning, palletizing, material-handling and inspection deployments."
        ],
        "expansion_signals": [
            "Closed C$3 million to strengthen production, standardize deployments and accelerate international expansion."
        ],
        "challenge_summary": (
            "On March 11, 2026, Rbot9 announced a C$3 million financing round to strengthen production, standardize deployments and expand its industrial cable robots internationally; VOTTA was already operating in an Icelandic seafood plant. "
            "Its official site confirms a multidisciplinary team developing, integrating and deploying cable robots for industrial cleaning, palletizing, material handling and inspection. "
            "Inference: scaling a mechatronic platform across different tools, factory layouts and overseas installations increases design-variant, simulation and controlled-release pressure."
        ),
        "why_relevant": (
            "NX can manage the mechanical and mechatronic platform design, Teamcenter can govern released product variants and deployment-specific BOMs, and Simcenter can validate structural and motion loads. "
            "The financing creates a near-term window to establish this product backbone before manufacturing and partner deployments scale."
        ),
        "identity": CompanyIdentityEvidence(
            official_name="Rbot9 Inc.",
            official_website_url="https://rbot9.com/",
            corroborating_urls=(
                "https://www.investquebec.com/fr/salle-de-presse/rbot9-securise-3-m-pour-accelerer-le-deploiement-linternational-de-ses-robots-cables",
            ),
        ),
        "keywords": (2, 8),
    },
    {
        "company_name": "Dishon Limited",
        "company_domain": "dishoncnc.com",
        "company_url": "https://www.dishoncnc.com/",
        "location": "Vaughan, Ontario, Canada",
        "industry": "Precision aerospace, space and energy component manufacturing",
        "products": ["NX", "Teamcenter", "Opcenter"],
        "scores": (85, 98, 88, 88, 96),
        "signal_date": datetime(2026, 4, 1, tzinfo=timezone.utc),
        "evidence_url": "https://www.canada.ca/en/economic-development-southern-ontario/news/2026/04/government-of-canada-supports-aerospace-and-space-innovation-to-strengthen-security-boost-prosperity-and-enhance-sovereign-capabilities.html",
        "source_title": "Government of Canada supports aerospace and space innovation to strengthen security, boost prosperity, and enhance sovereign capabilities",
        "source_publisher": "Federal Economic Development Agency for Southern Ontario",
        "signal_label": "C$7.5M investment scales new precision-manufacturing facility",
        "pain_signals": [
            "Must scale high-mix, safety-critical aerospace and space part production while preserving revision, routing, inspection and certification traceability."
        ],
        "expansion_signals": [
            "Received C$7.5 million to adopt advanced machining and precision-measurement equipment at a new 30,000-square-foot Vaughan facility."
        ],
        "challenge_summary": (
            "On April 1, 2026, FedDev Ontario announced C$7.5 million for Dishon to scale production at its new 30,000-square-foot Vaughan facility using advanced machining and precision-measurement equipment. "
            "Dishon's official site confirms Tier 2 production of safety-critical landing-gear, engine, aerostructure, fluid-system and space components in hard metals, castings and forgings. "
            "Inference: the facility ramp increases routing, revision, inspection and certification-traceability complexity across demanding part families."
        ),
        "why_relevant": (
            "NX is the direct CAD/CAM fit for complex multi-axis parts, Teamcenter can control part structures, revisions and released manufacturing data, and Opcenter can support execution, inspection and traceability. "
            "The new facility, equipment adoption and customer-demand growth make process governance urgent before throughput scales."
        ),
        "identity": CompanyIdentityEvidence(
            official_name="Dishon Limited",
            official_website_url="https://www.dishoncnc.com/",
            corroborating_urls=(
                "https://www.canada.ca/en/economic-development-southern-ontario/news/2026/04/government-of-canada-supports-aerospace-and-space-innovation-to-strengthen-security-boost-prosperity-and-enhance-sovereign-capabilities.html",
            ),
        ),
        "keywords": (9, 10, 14),
    },
    {
        "company_name": "Jewel Welding Fabrication and Coatings Ltd.",
        "company_domain": "jewelwfc.com",
        "company_url": "https://jewelwfc.com/",
        "location": "Maple Ridge, British Columbia, Canada",
        "industry": "Industrial pipe fabrication, welding and protective coatings",
        "products": ["Solid Edge", "Teamcenter", "Opcenter", "Tecnomatix"],
        "scores": (78, 94, 82, 76, 95),
        "signal_date": datetime(2026, 3, 18, tzinfo=timezone.utc),
        "evidence_url": "https://archive.news.gov.bc.ca/releases/news_releases_2024-2028/2026JEG0016-000283.htm",
        "source_title": "Bringing new manufacturing jobs to Maple Ridge through support from the Province",
        "source_publisher": "Government of British Columbia",
        "signal_label": "Nearly C$2M backs new fabrication facility and equipment",
        "pain_signals": [
            "Must establish controlled fabrication, weld-quality, material-traceability and capacity-planning processes for larger clean-energy piping projects."
        ],
        "expansion_signals": [
            "Received nearly C$2 million toward a new manufacturing facility and advanced equipment, with up to 45 jobs planned."
        ],
        "challenge_summary": (
            "On March 18, 2026, British Columbia committed nearly C$2 million for Jewel to construct a new manufacturing facility, buy advanced equipment and expand hydroelectric and water-service piping capacity, with up to 45 jobs planned. "
            "Jewel's official site confirms that a purpose-built 30,000-square-foot fabrication shop is under construction for October 2026 completion and that it performs large-diameter pipe fabrication, welding, coatings and hydroelectric work. "
            "Inference: the capacity increase and larger project mix raise fabrication-routing, weld-quality, material-traceability and factory-planning demands."
        ),
        "why_relevant": (
            "Solid Edge can support fabrication design and drawings, Teamcenter can govern revisions and released project data, Opcenter can add shop-floor quality and traceability, and Tecnomatix can plan the new facility and production flows. "
            "The facility build creates a time-sensitive implementation window before equipment and workflows are fixed."
        ),
        "identity": CompanyIdentityEvidence(
            official_name="Jewel Welding Fabrication and Coatings Ltd.",
            official_website_url="https://jewelwfc.com/",
            corroborating_urls=(
                "https://archive.news.gov.bc.ca/releases/news_releases_2024-2028/2026JEG0016-000283.htm",
            ),
        ),
        "keywords": (5,),
    },
)


def make_signal(prospect: dict[str, object]) -> ExtractedSignal:
    opportunity, _manufacturing, _trigger, _solution, evidence = prospect["scores"]
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
        confidence=int(evidence) / 100,
        reason=str(prospect["challenge_summary"]),
        source_url=str(prospect["evidence_url"]),
        source_title=str(prospect["source_title"]),
        detected_at=prospect["signal_date"],
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
        signal_date=prospect["signal_date"],
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
    load_dotenv(REPO_ROOT / ".env")
    database = Database(os.environ["DATABASE_URL"])
    database.initialize()
    keywords_before = {row.id: row for row in database.list_keywords()}
    expected_ids = {1, 2, 3, 4, 5, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16}
    if set(keywords_before) != expected_ids:
        raise RuntimeError(f"Persistent keyword set changed: {sorted(keywords_before)}")

    prior_domains = {lead.company_domain for lead in database.get_leads(limit=5000)}
    published = {keyword_id: 0 for keyword_id in keywords_before}
    new_domains: set[str] = set()
    signals: list[dict[str, object]] = []
    links: list[dict[str, object]] = []

    for prospect in PROSPECTS:
        domain = str(prospect["company_domain"])
        if domain not in prior_domains:
            new_domains.add(domain)
        saved, company = database.persist_verified_signal(make_signal(prospect), prospect["identity"])
        signals.append(
            {
                "company": company.company_name,
                "domain": company.company_domain,
                "created": saved.created,
                "duplicate_url": saved.duplicate_url,
                "source_url": str(prospect["evidence_url"]),
                "signal_count": company.signal_count,
            }
        )
        for keyword_id in prospect["keywords"]:
            row = record_link(database, keyword_id, prospect)
            published[keyword_id] += 1
            links.append(
                {
                    "keyword_id": keyword_id,
                    "company_id": row.company_id,
                    "company": row.company_name,
                    "status": row.qualification_status,
                }
            )

    for keyword_id in sorted(keywords_before):
        if database.record_keyword_search(keyword_id, result_count=published[keyword_id], error=None) is None:
            raise RuntimeError(f"Could not record keyword search {keyword_id}")

    keywords_after = {row.id: row for row in database.list_keywords()}
    for keyword_id, before in keywords_before.items():
        after = keywords_after[keyword_id]
        if after.search_count != before.search_count + 1:
            raise RuntimeError(f"Keyword {keyword_id} did not advance exactly once")
        if after.last_error is not None:
            raise RuntimeError(f"Keyword {keyword_id} retained an unexpected error: {after.last_error}")

    print(
        json.dumps(
            {
                "run_at": RUN_AT.isoformat(),
                "new_company_domains": sorted(new_domains),
                "signals": signals,
                "keyword_links": links,
                "keyword_audits": [
                    {
                        "id": keyword_id,
                        "keyword": keywords_after[keyword_id].keyword,
                        "search_count_before": keywords_before[keyword_id].search_count,
                        "search_count_after": keywords_after[keyword_id].search_count,
                        "qualified": published[keyword_id],
                        "watchlist": 0,
                        "last_error": keywords_after[keyword_id].last_error,
                    }
                    for keyword_id in sorted(keywords_after)
                ],
                "research_notes": {
                    "lookbacks": "rolling 30 days; 180-day evidence fallback; 365-day ongoing-project fallback",
                    "query_families_per_keyword": 6,
                    "mandatory_sources": ["Startup Gallery", "public X/X-ray", "BetaKit", "NGen"],
                    "aerospace_sources": ["SpaceQ", "AIAC"],
                    "additional_sources": [
                        "Canada.ca",
                        "Investissement Quebec",
                        "Government of British Columbia",
                        "ventureLAB",
                        "CanadaBuys",
                        "Ocean Supercluster",
                        "APMA",
                        "OVIN",
                        "Electric Autonomy Canada",
                        "PLANT",
                        "BDC",
                        "MaRS",
                    ],
                    "shortfall": "Direct X was certificate-blocked and Google later presented an automated-traffic challenge; neither warning was bypassed. Accessible result pools were exhausted without padding counts, so the 15-domain target was not demonstrably met for every narrow keyword.",
                    "reassessed_duplicates": [
                        "Bombardier",
                        "InDro Robotics",
                        "MDS Coating Technologies",
                        "Sentinel R&D",
                        "FeralX Systems",
                        "Serenity Power",
                    ],
                    "rejected_examples": [
                        "Hanon Systems - foreign headquartered",
                        "Eclipse Automation - service/integration provider rather than target manufacturer",
                        "CanadaBuys pre-qualified suppliers - no committed production trigger",
                    ],
                },
            },
            indent=2,
            default=str,
        )
    )


if __name__ == "__main__":
    main()
