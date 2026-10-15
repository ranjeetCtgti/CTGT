from __future__ import annotations

import json
from datetime import datetime, timezone

from dotenv import load_dotenv

from db.database import Database
from models.schema import ExtractedSignal


RUN_AT = datetime.now(timezone.utc)


def dt(year: int, month: int, day: int) -> datetime:
    return datetime(year, month, day, tzinfo=timezone.utc)


TEMPEL = {
    "company_name": "Tempel Canada Company",
    "company_domain": "tempel.com",
    "company_url": "https://www.tempel.com/",
    "linkedin_url": "https://www.linkedin.com/company/tempel/",
    "location": "Burlington, Ontario, Canada",
    "industry": "Transformer cores and precision electrical steel laminations",
    "products": ["Teamcenter", "Opcenter", "Tecnomatix"],
    "scores": {
        "opportunity": 91,
        "manufacturing": 98,
        "trigger": 96,
        "solution": 94,
        "evidence": 97,
    },
    "pain_signals": [
        "Must ramp a new 250,000-square-foot factory while protecting transformer-core and electrical-steel-lamination quality.",
        "Must coordinate equipment, product routings, engineering changes, production quality and traceability across a manufacturing footprint that has more than doubled.",
    ],
    "expansion_signals": [
        "Worthington Steel invested approximately US$85 million in Tempel Canada's Burlington expansion.",
        "The new plant more than doubles the Canadian manufacturing footprint, expands transformer-core and precision-lamination capacity and is expected to create nearly 100 jobs.",
    ],
    "evidence": [
        {
            "signal_date": dt(2026, 6, 25),
            "source_url": "https://www.tempel.com/en/events/tempel-canada-opens-new-manufacturing-facility",
            "source_title": "Tempel Canada Opens New Manufacturing Facility",
            "source_publisher": "Tempel",
            "signal_label": "US$85M Burlington plant more than doubles Tempel Canada's manufacturing footprint",
            "challenge_summary": (
                "On June 25, 2026, Worthington Steel opened an approximately US$85 million, 250,000-square-foot Tempel Canada manufacturing facility in Burlington, Ontario; the plant more than doubles Tempel Canada's footprint, expands transformer-core and precision electrical-steel-lamination capacity, and is expected to create nearly 100 jobs. The new capacity serves growing electrical-infrastructure demand driven by grid modernization, electrification, artificial intelligence and data centres. Inference: commissioning the plant while scaling product mix and throughput creates immediate pressure on equipment and process planning, engineering-change and bill-of-material control, work-in-process visibility, quality traceability and stable ramp-up execution."
            ),
            "why_relevant": (
                "Teamcenter is the smallest defensible PLM layer for controlling released lamination and transformer-core designs, routings and engineering changes across the expanded operation. Opcenter can provide production, genealogy and quality visibility during ramp-up, while Tecnomatix can validate line layouts, material flow and process capacity before changes reach the factory floor. The facility is open now and the footprint has more than doubled, so production-system and digital-thread decisions are urgent rather than speculative."
            ),
        },
        {
            "signal_date": dt(2025, 3, 3),
            "source_url": "https://www.canada.ca/en/economic-development-southern-ontario/news/2025/03/ten-businesses-across-southern-ontario-receive-government-of-canada-support-to-foster-growth-and-develop-new-products.html",
            "source_title": "Ten businesses across southern Ontario receive Government of Canada support to foster growth and develop new products",
            "source_publisher": "Government of Canada / FedDev Ontario",
            "signal_label": "$3.5M FedDev support funded advanced equipment for transformer manufacturing expansion",
            "challenge_summary": (
                "On March 3, 2025, FedDev Ontario announced $3.5 million for Tempel Canada to adopt advanced manufacturing equipment and expand capacity for utility and industrial transformer demand; federal grant records show the contribution running through March 31, 2026. Tempel manufactures precision magnetic-steel laminations used in transformers, generators and electric motors, so the equipment program directly adds production capability rather than funding a software-only initiative. Inference: new equipment introduced alongside the Burlington footprint expansion increases the need for governed manufacturing revisions, synchronized routings, machine/process qualification and auditable quality records."
            ),
            "why_relevant": (
                "Teamcenter can connect released product definitions and manufacturing changes to the new equipment, while Opcenter can standardize execution and capture quality and traceability data as processes stabilize. Tecnomatix is appropriate for equipment and process-flow validation where the plant must prove capacity before committing physical changes. The contribution period and the June 2026 plant opening show that the equipment program has moved from funding into active industrialization."
            ),
        },
    ],
}


COVERAGE = {
    1: {
        "reviewed": 6,
        "rejected": 2,
        "duplicates": 4,
        "sources": ["Startup Gallery", "X.com", "BetaKit", "NGen", "SpaceQ", "AIAC", "ventureLAB", "BDC Capital"],
        "notes": "Startup Gallery and AIAC returned directory leads only. BetaKit surfaced Calogy/Jaunt and Landing Zones; SpaceQ surfaced the already-linked Telesat/MDA Arctic contract. No new qualified domain.",
    },
    2: {
        "reviewed": 6,
        "rejected": 6,
        "duplicates": 0,
        "sources": ["Startup Gallery", "X.com", "BetaKit", "NGen", "ventureLAB", "Automate Canada", "BDC Capital"],
        "notes": "DaoAI, Dawn Robotics, Ma Robot AI, Avidbots, Sanctuary AI and Ro-Matt were discovery/directory leads without a new dated qualifying trigger.",
    },
    3: {
        "reviewed": 3,
        "rejected": 3,
        "duplicates": 0,
        "sources": ["Startup Gallery", "X.com", "BetaKit", "NGen", "Canada's Ocean Supercluster", "Shipbuilding Association of Canada", "Marine Log", "EDC"],
        "notes": "Startup Gallery, BetaKit and Shipbuilding Association searches returned zero relevant results. Marine Log's new Corvus item was blocked behind security verification and could not be corroborated by a dated primary announcement, so it was not published.",
    },
    4: {
        "reviewed": 3,
        "rejected": 2,
        "duplicates": 1,
        "sources": ["Startup Gallery", "X.com", "BetaKit", "NGen", "OVIN", "APMA", "Electric Autonomy Canada", "BDC Capital"],
        "notes": "ChargeLab was rejected as a software-led charging-management vendor; AUVSI was an association, and Calogy was already linked. Startup Gallery returned zero relevant results.",
    },
    5: {
        "reviewed": 4,
        "rejected": 2,
        "duplicates": 1,
        "sources": ["Startup Gallery", "X.com", "BetaKit", "NGen", "Creative Destruction Lab", "PLANT", "BDC Capital", "FedDev Ontario"],
        "notes": "Tempel Canada passed the evidence gate. Power Wood remained unpublished because financing and facility-execution claims were not sufficiently corroborated; Accuenergy was an existing duplicate.",
    },
    6: {
        "reviewed": 3,
        "rejected": 0,
        "duplicates": 3,
        "sources": ["Startup Gallery", "X.com", "BetaKit", "NGen", "SpaceQ", "AIAC", "Creative Destruction Lab", "BDC Capital"],
        "notes": "Startup Gallery, X.com, BetaKit, NGen and SpaceQ returned zero relevant new results. AIAC confirmed Jaunt as a directory member; Horizon, Jaunt and Landing Zones were already assessed.",
    },
    7: {
        "reviewed": 8,
        "rejected": 5,
        "duplicates": 3,
        "sources": ["Startup Gallery", "X.com", "BetaKit", "NGen", "SpaceQ", "AIAC", "ventureLAB", "BDC Capital"],
        "notes": "BetaKit directly returned Calogy, Sentinel and Landing Zones as existing triggers. Avro, Escarpment, Radio Wires, AVSS and Win Global remained discovery-only. X.com was inaccessible because its certificate could not be verified.",
    },
    8: {
        "reviewed": 6,
        "rejected": 6,
        "duplicates": 0,
        "sources": ["Startup Gallery", "X.com", "BetaKit", "NGen", "ventureLAB", "PLANT", "Canadian Manufacturing", "BDC Capital"],
        "notes": "Directory and collaboration leads (Prosaris, H2 Plasma, Musashi AI, Haply Robotics) lacked a new dated funding trigger. Tempel was not linked because the keyword requires a recent funding raise, and Power Wood failed corroboration.",
    },
}


def make_signal(evidence: dict[str, object]) -> ExtractedSignal:
    return ExtractedSignal(
        company_name=TEMPEL["company_name"],
        company_domain=TEMPEL["company_domain"],
        company_url=TEMPEL["company_url"],
        linkedin_url=TEMPEL["linkedin_url"],
        location=TEMPEL["location"],
        industry=TEMPEL["industry"],
        company_industry=TEMPEL["industry"],
        software=[],
        signal_type="news",
        signal_source="news",
        pain_signals=TEMPEL["pain_signals"],
        expansion_signals=TEMPEL["expansion_signals"],
        raw_score=TEMPEL["scores"]["opportunity"],
        confidence=TEMPEL["scores"]["evidence"] / 100,
        reason=str(evidence["challenge_summary"]),
        source_url=str(evidence["source_url"]),
        source_title=str(evidence["source_title"]),
        detected_at=evidence["signal_date"],
    )


def main() -> None:
    load_dotenv(".env")
    database = Database()
    database.initialize()
    keywords = {item.id: item for item in database.list_keywords()}
    expected_ids = set(COVERAGE)
    if set(keywords) != expected_ids:
        raise RuntimeError(f"Persistent keyword set changed: {sorted(keywords)}")

    signal_results = []
    for evidence in TEMPEL["evidence"]:
        saved, company = database.persist_signal(make_signal(evidence))
        signal_results.append(
            {
                "source_url": evidence["source_url"],
                "created": saved.created,
                "duplicate_url": saved.duplicate_url,
                "company_domain": company.company_domain,
            }
        )

    primary = TEMPEL["evidence"][0]
    scores = TEMPEL["scores"]
    linked = database.record_keyword_company(
        5,
        TEMPEL["company_name"],
        TEMPEL["company_domain"],
        source_url=primary["source_url"],
        source_title=primary["source_title"],
        source_publisher=primary["source_publisher"],
        signal_label=primary["signal_label"],
        signal_date=primary["signal_date"],
        challenge_summary=primary["challenge_summary"],
        why_relevant=primary["why_relevant"],
        recommended_products=TEMPEL["products"],
        qualification_status="qualified",
        opportunity_score=scores["opportunity"],
        manufacturing_fit_score=scores["manufacturing"],
        trigger_score=scores["trigger"],
        solution_fit_score=scores["solution"],
        evidence_quality_score=scores["evidence"],
        seen_at=RUN_AT,
    )
    if linked is None:
        raise RuntimeError("Tempel signal persisted but keyword-company link failed")

    for keyword_id in sorted(keywords):
        database.record_keyword_search(keyword_id, result_count=1 if keyword_id == 5 else 0)

    per_keyword = {}
    for keyword_id, item in COVERAGE.items():
        per_keyword[keyword_id] = {
            "keyword": keywords[keyword_id].keyword,
            "lookback": "30 days with 180-day fallback",
            "candidates_reviewed": item["reviewed"],
            "rejected_before_persistence": item["rejected"],
            "qualified_published": 1 if keyword_id == 5 else 0,
            "watchlist_published": 0,
            "existing_upgraded_or_hidden": 0,
            "duplicates_skipped": item["duplicates"],
            "sources_checked": item["sources"],
            "blockers_or_zero_results": item["notes"],
        }

    print(
        json.dumps(
            {
                "run_at": RUN_AT.isoformat(),
                "company_id": linked.company_id,
                "signals": signal_results,
                "keyword_company_status": linked.qualification_status,
                "per_keyword": per_keyword,
            },
            indent=2,
            default=str,
        )
    )


if __name__ == "__main__":
    main()
