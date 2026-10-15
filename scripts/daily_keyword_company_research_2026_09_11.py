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
LOCK_PATH = Path(
    r"C:\Users\ranjeet.chaudhary\.codex\automations\daily-keyword-company-research\run.lock"
)


COMPANIES = (
    {
        "company_name": "Connor Industries Ltd.",
        "company_domain": "stanleyboats.ca",
        "company_url": "https://stanleyboats.ca/",
        "location": "Parry Sound, Ontario, Canada",
        "industry": "Custom welded-aluminum boat manufacturing",
        "products": ["Solid Edge", "Teamcenter", "Opcenter"],
        "scores": (85, 98, 90, 86, 98),
        "keywords": (3,),
        "identity": CompanyIdentityEvidence(
            official_name="Connor Industries Ltd.",
            official_website_url="https://stanleyboats.ca/",
            corroborating_urls=(
                "https://www.canada.ca/en/fednor/news/2026/08/government-of-canada-investing-over-17-million-to-enhance-economic-development-in-the-parry-sound---muskoka-area0.html",
            ),
        ),
        "signals": (
            {
                "signal_date": datetime(2026, 8, 18, tzinfo=timezone.utc),
                "source_url": "https://www.canada.ca/en/fednor/news/2026/08/government-of-canada-investing-over-17-million-to-enhance-economic-development-in-the-parry-sound---muskoka-area0.html",
                "source_title": "Government of Canada investing over $1.7 million to enhance economic development in the Parry Sound - Muskoka area",
                "source_publisher": "Federal Economic Development Agency for Northern Ontario",
                "signal_label": "C$461,952 adds watercraft manufacturing equipment and capacity",
                "pain_signals": [
                    "Must integrate new production equipment and technology into a custom-vessel workflow while controlling hull variants, released drawings, fabrication routings, and quality records."
                ],
                "expansion_signals": [
                    "Received a C$461,952 repayable FedNor investment for equipment, infrastructure upgrades, and new technology at the Parry Sound boat plant."
                ],
                "challenge_summary": (
                    "On August 18, 2026, FedNor announced a C$461,952 repayable investment for Connor Industries to acquire and install innovative watercraft-manufacturing equipment, upgrade infrastructure, expand production, and create jobs at its Parry Sound plant. "
                    "Connor's official Stanley Boats site confirms that its in-house engineering and naval-architecture team designs and builds custom welded-aluminum commercial, patrol, passenger, and fire-rescue vessels. "
                    "Inference: adding equipment to a custom-vessel line increases pressure on variant control, released drawings, fabrication routings, and build-quality traceability."
                ),
                "why_relevant": (
                    "Solid Edge can support configurable vessel design and fabrication drawings, Teamcenter can govern released variants and engineering changes, and Opcenter can connect routings, work execution, and quality records. "
                    "The funded equipment installation creates a near-term window to establish that digital thread before expanded production and hiring increase process variability."
                ),
            },
        ),
    },
    {
        "company_name": "AVSS - Aerial Vehicle Safety Solutions Inc.",
        "company_domain": "avss.co",
        "company_url": "https://avss.co/",
        "location": "Fredericton, New Brunswick and Carp, Ontario, Canada",
        "industry": "Drone systems, components, and aerospace safety manufacturing",
        "products": ["Teamcenter", "Polarion", "Opcenter"],
        "scores": (94, 99, 98, 95, 99),
        "keywords": (7, 9, 13, 14),
        "identity": CompanyIdentityEvidence(
            official_name="AVSS - Aerial Vehicle Safety Solutions Inc.",
            official_website_url="https://avss.co/",
            corroborating_urls=(
                "https://www.pm.gc.ca/en/news/backgrounders/2026/09/10/canada-and-ukraine-scale-drone-production-build-canadas-defence",
                "https://achatscanada.canada.ca/fr/occasions-de-marche/contrats-octroyes/cw2467626-000",
            ),
        ),
        "signals": (
            {
                "signal_date": datetime(2026, 9, 10, tzinfo=timezone.utc),
                "source_url": "https://www.pm.gc.ca/en/news/backgrounders/2026/09/10/canada-and-ukraine-scale-drone-production-build-canadas-defence",
                "source_title": "Canada and Ukraine to scale up drone production, build up Canada's defence industries, and achieve a just and lasting peace in Ukraine",
                "source_publisher": "Prime Minister of Canada",
                "signal_label": "AVSS Drone D1 selected for initial sovereign-defence procurement",
                "pain_signals": [
                    "Must control a Canadian-made UAS product configuration spanning airframe, electronics, sensors, software, documentation, training, and sustainment under defence acceptance requirements."
                ],
                "expansion_signals": [
                    "Selected for an initial Defence Drone Initiative contract path for the AVSS Drone D1, with manufacturing and assembly in Ontario and most major components sourced in Canada."
                ],
                "challenge_summary": (
                    "On September 10, 2026, the Prime Minister's Office named AVSS and its Drone D1 among the initial Defence Drone Initiative suppliers, stating that the system is predominantly Canadian-made, assembled in Ontario, and uses mainly Canadian components, electronics, sensors, software, and support systems. "
                    "The procurement requires configuration, documentation, training, maintenance, repair, and sustainment in Canada. "
                    "Inference: a defence UAS delivered as a supported system creates immediate BOM, requirements, firmware/configuration, supplier, and serialized-quality traceability pressure."
                ),
                "why_relevant": (
                    "Teamcenter can govern the Drone D1 product structure, supplier-controlled parts, released configurations, and sustainment data; Polarion can connect requirements, verification, defects, and acceptance evidence; Opcenter can support production and serialized quality traceability. "
                    "The initial procurement decision makes the need current because AVSS must move from rapid product growth into repeatable, auditable defence delivery."
                ),
            },
            {
                "signal_date": datetime(2026, 7, 1, tzinfo=timezone.utc),
                "source_url": "https://avss.co/2026/07/record-growth-with-more-months-to-grow-canadian-drone-manufacturer-avss-surpasses-2000-systems-manufactured-year-to-date-reinforcing-canadas-global-leadership-in-drone-technology/",
                "source_title": "Record Growth With More Months to Grow: Canadian Drone Manufacturer AVSS Surpasses 2,000 Systems Manufactured Year-to-Date",
                "source_publisher": "AVSS",
                "signal_label": "Production surpasses 2,000 Canadian-made drone systems and components",
                "pain_signals": [
                    "Must maintain engineering, manufacturing, testing, and quality-assurance control while production volume exceeds the prior full fiscal year."
                ],
                "expansion_signals": [
                    "Manufactured more than 2,000 Canadian-made drone components and systems year-to-date and expected continued growth."
                ],
                "challenge_summary": (
                    "In July 2026, AVSS reported that it had manufactured more than 2,000 Canadian-made drone components and systems year-to-date, already exceeding production for the prior full fiscal year. "
                    "The company states that product development, engineering, manufacturing, testing, and quality assurance remain in Canada. "
                    "Inference: record volume across multiple aerospace products raises revision-control, test-evidence, nonconformance, and serialized-traceability demands before the new defence work begins."
                ),
                "why_relevant": (
                    "Teamcenter and Polarion can keep product changes, requirements, verification evidence, and released configurations synchronized, while Opcenter can preserve execution and quality genealogy at higher volume. "
                    "The record production milestone shows that the operating pressure is already present rather than only prospective."
                ),
            },
        ),
    },
    {
        "company_name": "Beonyx Robotics Inc.",
        "company_domain": "beonyx.ca",
        "company_url": "https://beonyx.ca/",
        "location": "Saguenay, Quebec, Canada",
        "industry": "Autonomous electric all-terrain vehicle manufacturing",
        "products": ["NX", "Teamcenter", "Simcenter", "Polarion"],
        "scores": (92, 99, 98, 94, 99),
        "keywords": (2, 11, 13, 14, 15),
        "identity": CompanyIdentityEvidence(
            official_name="Beonyx Robotics Inc.",
            official_website_url="https://beonyx.ca/",
            corroborating_urls=(
                "https://achatscanada.canada.ca/fr/occasions-de-marche/contrats-octroyes/cw2467495-000",
                "https://www.pm.gc.ca/en/news/news-releases/2026/09/10/canada-and-ukraine-scale-drone-production-build-canadas-defence",
            ),
        ),
        "signals": (
            {
                "signal_date": datetime(2026, 9, 9, tzinfo=timezone.utc),
                "source_url": "https://achatscanada.canada.ca/fr/occasions-de-marche/contrats-octroyes/cw2467495-000",
                "source_title": "W8703-270093 Complex Terrain Uncrewed Ground Vehicle systems Contract 003",
                "source_publisher": "CanadaBuys",
                "signal_label": "C$481,644.86 contract launches complex-terrain UGV delivery",
                "pain_signals": [
                    "Must deliver a rugged autonomous electric vehicle system with spares, support equipment, documentation, training, and in-service support on a five-month defence schedule."
                ],
                "expansion_signals": [
                    "Won a C$481,644.86 Department of National Defence contract running from September 9, 2026 to March 1, 2027 for complex-terrain uncrewed ground vehicles."
                ],
                "challenge_summary": (
                    "On September 9, 2026, CanadaBuys awarded Beonyx Robotics a C$481,644.86 contract through March 1, 2027 to provide complex-terrain uncrewed ground vehicles plus spares, support equipment, documentation, training, sustainment, and related support. "
                    "Beonyx's official site confirms that the Saguenay company develops the modular B1 4x8 and 8x8 autonomous electric all-terrain vehicle. "
                    "Inference: converting that patented platform into a defence-supported system on a five-month schedule adds configuration, ruggedization, requirements, test, service-BOM, and documentation complexity."
                ),
                "why_relevant": (
                    "NX can manage the B1 mechanical and electrical packaging, Teamcenter can control 4x8/8x8 configurations and service BOMs, Simcenter can support structural and mobility validation, and Polarion can connect defence requirements to verification evidence. "
                    "The signed contract and March 2027 end date create immediate delivery pressure."
                ),
            },
        ),
    },
    {
        "company_name": "Draganfly Inc.",
        "company_domain": "draganfly.com",
        "company_url": "https://draganfly.com/",
        "location": "Saskatoon, Saskatchewan and Burnaby, British Columbia, Canada",
        "industry": "Uncrewed aircraft and autonomous systems manufacturing",
        "products": ["Teamcenter", "Polarion", "Opcenter"],
        "scores": (90, 98, 94, 94, 98),
        "keywords": (9, 13, 14),
        "identity": CompanyIdentityEvidence(
            official_name="Draganfly Inc.",
            official_website_url="https://draganfly.com/",
            corroborating_urls=(
                "https://www.pm.gc.ca/en/news/news-releases/2026/09/10/canada-and-ukraine-scale-drone-production-build-canadas-defence",
                "https://canadabuys.canada.ca/en/node/preview/1464482",
            ),
        ),
        "signals": (
            {
                "signal_date": datetime(2026, 9, 10, tzinfo=timezone.utc),
                "source_url": "https://www.pm.gc.ca/en/news/news-releases/2026/09/10/canada-and-ukraine-scale-drone-production-build-canadas-defence",
                "source_title": "Canada and Ukraine to scale up drone production, build up Canada's defence industries, and achieve a just and lasting peace in Ukraine",
                "source_publisher": "Prime Minister of Canada",
                "signal_label": "Named for initial Defence Drone Initiative procurement",
                "pain_signals": [
                    "Must scale Canadian production and ongoing product development for a defence platform while controlling aircraft, sensors, software, documentation, training, and sustainment configurations."
                ],
                "expansion_signals": [
                    "Named among the initial Defence Drone Initiative suppliers; the government confirms established Canadian engineering, manufacturing, integration, training, sustainment, production, and product-development capability."
                ],
                "challenge_summary": (
                    "On September 10, 2026, the Prime Minister's Office named Draganfly among Canada's initial Defence Drone Initiative suppliers and confirmed that it has engineering, manufacturing, integration, training, sustainment, production, and ongoing product development in Canada. "
                    "Draganfly's official production materials identify equipped facilities in Saskatoon and Burnaby with machining, additive manufacturing, expandable lines, and test infrastructure. "
                    "Inference: defence delivery across configurable aircraft, sensors, software, support equipment, and sustainment increases BOM, change, verification, supplier, and quality-genealogy demands."
                ),
                "why_relevant": (
                    "Teamcenter can govern platform variants, released configurations, suppliers, and sustainment structures; Polarion can tie operational requirements to verification and defects; Opcenter can support controlled production and serialized quality records. "
                    "The move from marketplace qualification into initial government procurement makes the process-control need immediate."
                ),
            },
        ),
    },
    {
        "company_name": "Volatus Aerospace Inc.",
        "company_domain": "volatusaerospace.com",
        "company_url": "https://volatusaerospace.com/",
        "location": "Mirabel, Quebec and Vaughan, Ontario, Canada",
        "industry": "Uncrewed aircraft manufacturing, systems integration, and aerial intelligence",
        "products": ["Teamcenter", "Polarion", "Opcenter", "Capital"],
        "scores": (98, 98, 100, 98, 99),
        "keywords": (9, 13, 14),
        "identity": CompanyIdentityEvidence(
            official_name="Volatus Aerospace Inc.",
            official_website_url="https://volatusaerospace.com/",
            corroborating_urls=(
                "https://www.pm.gc.ca/en/news/news-releases/2026/09/10/canada-and-ukraine-scale-drone-production-build-canadas-defence",
                "https://canadabuys.canada.ca/en/tender-opportunities/contract-history/cw2467501-000",
            ),
        ),
        "signals": (
            {
                "signal_date": datetime(2026, 9, 10, tzinfo=timezone.utc),
                "source_url": "https://volatusaerospace.com/insights/defence-contract-tactical-isr/",
                "source_title": "Volatus Aerospace Awarded Canadian Defence Contract for Tactical ISR Uncrewed Aircraft Systems for up to 5,000 systems",
                "source_publisher": "Volatus Aerospace",
                "signal_label": "Five-year tactical ISR contract starts at 100 systems with path to 5,000",
                "pain_signals": [
                    "Must deliver and sustain an end-to-end tactical ISR system spanning aircraft, payloads, ground stations, data links, firmware, training, spares, and documentation."
                ],
                "expansion_signals": [
                    "Won a five-year Canadian Armed Forces contract for 100 tactical ISR UAS, with options for 4,900 more and a procurement framework up to C$25 million."
                ],
                "challenge_summary": (
                    "On September 10, 2026, Volatus announced a five-year Canadian Armed Forces contract for 100 tactical ISR UAS, with options for 4,900 additional systems under a framework capped at C$5,000 per system and C$25 million overall; initial deliveries are expected in Q4 2026. "
                    "The end-to-end package includes aircraft, payloads, ground-control stations, data links, training, sustainment, spares, documentation, software, and firmware support. "
                    "Inference: that breadth and option scale create urgent configuration, supplier, electrical-interface, requirements, release, and serialized-quality control across the Mirabel manufacturing hub and Vaughan operations centre."
                ),
                "why_relevant": (
                    "Teamcenter can govern the complete supported-system configuration and service BOM, Polarion can connect requirements and acceptance tests to defects, Opcenter can preserve production and quality genealogy, and Capital can manage electrical and electronic architecture across aircraft, payload, and ground-system interfaces. "
                    "Q4 deliveries and a potential 50-fold increase from 100 to 5,000 systems make the implementation window immediate."
                ),
            },
        ),
    },
)


def make_signal(company: dict[str, object], evidence: dict[str, object]) -> ExtractedSignal:
    opportunity, _manufacturing, _trigger, _solution, evidence_score = company["scores"]
    return ExtractedSignal(
        company_name=str(company["company_name"]),
        company_domain=str(company["company_domain"]),
        company_url=str(company["company_url"]),
        location=str(company["location"]),
        industry=str(company["industry"]),
        company_industry=str(company["industry"]),
        software=list(company["products"]),
        signal_type="news",
        signal_source="news",
        pain_signals=list(evidence["pain_signals"]),
        expansion_signals=list(evidence["expansion_signals"]),
        raw_score=int(opportunity),
        confidence=int(evidence_score) / 100,
        reason=str(evidence["challenge_summary"]),
        source_url=str(evidence["source_url"]),
        source_title=str(evidence["source_title"]),
        detected_at=evidence["signal_date"],
    )


def record_link(database: Database, keyword_id: int, company: dict[str, object], evidence: dict[str, object]):
    opportunity, manufacturing, trigger, solution, evidence_score = company["scores"]
    row = database.record_keyword_company(
        keyword_id,
        str(company["company_name"]),
        str(company["company_domain"]),
        source_url=str(evidence["source_url"]),
        source_title=str(evidence["source_title"]),
        source_publisher=str(evidence["source_publisher"]),
        signal_label=str(evidence["signal_label"]),
        signal_date=evidence["signal_date"],
        challenge_summary=str(evidence["challenge_summary"]),
        why_relevant=str(evidence["why_relevant"]),
        recommended_products=list(company["products"]),
        qualification_status="qualified",
        opportunity_score=int(opportunity),
        manufacturing_fit_score=int(manufacturing),
        trigger_score=int(trigger),
        solution_fit_score=int(solution),
        evidence_quality_score=int(evidence_score),
        seen_at=RUN_AT,
    )
    if row is None:
        raise RuntimeError(f"Could not link {company['company_name']} to keyword {keyword_id}")
    return row


def main() -> None:
    load_dotenv(REPO_ROOT / ".env")
    marker = json.loads(LOCK_PATH.read_text(encoding="utf-8"))
    if int(marker.get("pid", 0)) <= 0:
        raise RuntimeError("Exclusive automation lock is not held")

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

    for company in COMPANIES:
        domain = str(company["company_domain"])
        if domain not in prior_domains:
            new_domains.add(domain)
        primary_evidence = company["signals"][0]
        company_record = None
        for evidence in company["signals"]:
            saved, company_record = database.persist_verified_signal(
                make_signal(company, evidence), company["identity"]
            )
            signals.append(
                {
                    "company": company_record.company_name,
                    "company_domain": company_record.company_domain,
                    "source_url": evidence["source_url"],
                    "created": saved.created,
                    "duplicate_url": saved.duplicate_url,
                    "signal_count": company_record.signal_count,
                }
            )
        for keyword_id in company["keywords"]:
            row = record_link(database, keyword_id, company, primary_evidence)
            published[keyword_id] += 1
            links.append(
                {
                    "keyword_id": keyword_id,
                    "company_id": row.company_id,
                    "company_name": row.company_name,
                    "qualification_status": row.qualification_status,
                    "opportunity_score": row.opportunity_score,
                }
            )

    for keyword_id in sorted(keywords_before):
        if database.record_keyword_search(
            keyword_id, result_count=published[keyword_id], error=None
        ) is None:
            raise RuntimeError(f"Could not record keyword search {keyword_id}")

    keywords_after = {row.id: row for row in database.list_keywords()}
    for keyword_id, before in keywords_before.items():
        after = keywords_after[keyword_id]
        if after.search_count != before.search_count + 1:
            raise RuntimeError(f"Keyword {keyword_id} did not advance exactly once")
        if after.last_error is not None:
            raise RuntimeError(f"Keyword {keyword_id} retained error: {after.last_error}")

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
                    "mandatory_sources_per_keyword": [
                        "Startup Gallery",
                        "public X/X-ray",
                        "BetaKit",
                        "NGen",
                    ],
                    "aerospace_sources": ["SpaceQ", "AIAC"],
                    "rotated_sources": [
                        "Canada.ca and regional development agencies",
                        "CanadaBuys",
                        "Prime Minister of Canada",
                        "SpaceQ",
                        "AIAC",
                        "Electric Autonomy Canada",
                        "Canadian Manufacturing",
                        "PLANT",
                        "Marine Log",
                        "ventureLAB",
                        "APMA",
                        "OVIN",
                        "Canada's Ocean Supercluster",
                    ],
                    "source_warnings": [
                        "Direct X.com remained certificate-inaccessible; public X-ray results were checked per keyword.",
                        "Google presented a human-verification challenge after 48 mandatory checks; it was not solved or bypassed.",
                        "DuckDuckGo became sparse after fallback searches; zero-result checks were retained and focused source lookup continued.",
                    ],
                    "breadth_shortfall": (
                        "The 15-domain quota was not demonstrably met for every narrow keyword because the accessible result pools and alternate-search fallback became sparse. No candidate was invented to fill the quota."
                    ),
                    "rejected_examples": [
                        "NorBot - official identity found, but no sufficiently detailed independently corroborated manufacturing trigger beyond its funding headline.",
                        "Scopia Surgical - product-development lead without enough manufacturing/production evidence for the saved robotics scope.",
                        "Vention - industrial automation platform and integration vendor rather than the target manufacturer's own product operation.",
                        "Bombardier - existing confirmed exclusion remains disqualified.",
                        "Twenty20 Insight - UK-manufactured platform with Canadian service delivery, so physical manufacturing fit in Canada did not pass.",
                        "Objexis AI - physical systems verified, but the current procurement evidence did not identify a committed award specific enough for publication.",
                    ],
                },
            },
            indent=2,
            default=str,
        )
    )


if __name__ == "__main__":
    main()
