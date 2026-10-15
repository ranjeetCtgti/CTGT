from __future__ import annotations

import json
from datetime import datetime, timezone

from dotenv import load_dotenv

from db.database import Database
from models.schema import ExtractedSignal


RUN_AT = datetime.now(timezone.utc)


EVIDENCE = [
    {
        "keyword_ids": [2, 8, 13],
        "company_name": "A&K Robotics",
        "company_domain": "aandkrobotics.com",
        "company_url": "https://www.aandkrobotics.com/",
        "linkedin_url": "https://ca.linkedin.com/company/a&k-robotics",
        "location": "Vancouver, British Columbia, Canada",
        "industry": "Autonomous electric micromobility and passenger robotics",
        "source_url": "https://betakit.com/ak-robotics-closes-8-million-series-a-round-to-put-self-driving-pods-in-airports/",
        "source_title": "A&K Robotics closes $8-million Series A round to put self-driving pods in airports",
        "source_publisher": "BetaKit",
        "signal_label": "A&K Robotics is scaling Cruz production from dozens to hundreds of autonomous vehicles per month",
        "signal_date": datetime(2026, 4, 21, tzinfo=timezone.utc),
        "challenge_summary": (
            "On April 21, 2026, BetaKit reported that A&K Robotics raised an $8 million CAD Series A, opened a rapid-prototyping and R&D facility, and planned a third Surrey, B.C. hub to expand Cruz autonomous-mobility-pod output from dozens to hundreds of vehicles per month; the company said total funding had reached $10.6 million. Cruz was already serving Vancouver International Airport and Madrid-Barajas Airport, and the round was intended to convert pilots into permanent North American and European deployments. Inference: that step-change creates immediate configuration, engineering-change, safety-requirements, supplier, line-planning, production-quality and unit-traceability pressure across sensing-rich electric vehicles."
        ),
        "why_relevant": (
            "Teamcenter can govern Cruz product structures, released parts, variants and engineering changes as output scales, while Polarion can connect passenger-safety and autonomous-behaviour requirements to test evidence. Tecnomatix and Opcenter can plan the new production flow and maintain build, inspection and quality genealogy as monthly volume rises by an order of magnitude. The financing, newly opened R&D facility and stated move from pilot builds to permanent deployments make the manufacturing-system decisions current rather than speculative."
        ),
        "products": ["Teamcenter", "Polarion", "Tecnomatix", "Opcenter"],
        "scores": {
            "opportunity": 94,
            "manufacturing": 97,
            "trigger": 95,
            "solution": 95,
            "evidence": 94,
        },
        "pain_signals": [
            "Must industrialize a sensor-rich autonomous passenger vehicle while preserving safety requirements and test evidence.",
            "Must expand monthly output from dozens to hundreds while moving airport pilots into permanent deployments.",
        ],
        "expansion_signals": [
            "Raised an $8 million CAD Series A and reported $10.6 million in total funding.",
            "Opened a rapid-prototyping and R&D facility and planned a third hub in Surrey, British Columbia.",
        ],
    },
    {
        "keyword_ids": [3, 13],
        "company_name": "Davie",
        "company_domain": "davie.ca",
        "company_url": "https://www.davie.ca/",
        "linkedin_url": "https://www.linkedin.com/company/chantier-davie-canada-inc-/",
        "location": "Levis, Quebec, Canada",
        "industry": "Shipbuilding and autonomous maritime-vehicle manufacturing",
        "source_url": "https://www.davie.ca/en/news/2026-07-20-davie-autonomous-en/",
        "source_title": "Davie Autonomous Launched in Ontario",
        "source_publisher": "Davie",
        "signal_label": "Davie formed an Ontario company to manufacture composite uncrewed surface vessels and is selecting production sites",
        "signal_date": datetime(2026, 7, 21, tzinfo=timezone.utc),
        "challenge_summary": (
            "On July 21, 2026, Davie formed Davie Autonomous Inc. in Ontario to manufacture and integrate advanced-composite uncrewed surface vessels with Kraken Technology Group, and said it was in advanced negotiations with several Ontario sites for a Canadian production network. The program will combine composites, robotics, automation, mission systems, software and payload integration with suppliers across Canada for surveillance, search-and-rescue, coastal-security, infrastructure-protection and defence customers. Inference: standing up a new multi-site, supplier-intensive product line creates urgent variant/BOM, requirements-to-test, interface, factory-planning, production-quality and unit-genealogy complexity."
        ),
        "why_relevant": (
            "Teamcenter can control vessel configurations, payload options, approved supplier data and engineering changes across Davie's Quebec and future Ontario operations. Polarion can link defence and mission requirements to verification evidence, while Tecnomatix and Opcenter can model the new production network and preserve build and inspection traceability. Site negotiations and the creation of the new manufacturing entity mean the product-data and execution architecture can influence the factory design now, before facilities and suppliers are locked in."
        ),
        "products": ["Teamcenter", "Polarion", "Tecnomatix", "Opcenter"],
        "scores": {
            "opportunity": 97,
            "manufacturing": 99,
            "trigger": 98,
            "solution": 97,
            "evidence": 98,
        },
        "pain_signals": [
            "Must industrialize advanced-composite uncrewed surface vessels with configurable mission systems and payloads.",
            "Must coordinate a new Ontario production network with suppliers, automation and existing sovereign shipbuilding expertise.",
        ],
        "expansion_signals": [
            "Formed Davie Autonomous Inc. on July 21, 2026.",
            "Entered advanced negotiations with several Ontario sites for autonomous-vessel production.",
        ],
    },
]


COVERAGE = {
    1: (6, 4, 2, ["Startup Gallery Aerospace", "X.com", "BetaKit", "NGen", "SpaceQ", "AIAC", "ventureLAB", "Google X-ray"]),
    2: (8, 5, 2, ["Startup Gallery Robotics", "X.com", "BetaKit", "NGen", "ventureLAB", "BDC Capital"]),
    3: (7, 4, 2, ["Startup Gallery Manufacturing", "X.com", "BetaKit", "NGen", "Canada's Ocean Supercluster", "Davie", "PR Newswire"]),
    4: (7, 5, 1, ["Startup Gallery Automotive", "X.com", "BetaKit", "NGen", "OVIN", "APMA", "Government of Canada"]),
    5: (7, 4, 3, ["Startup Gallery Energy", "X.com", "BetaKit", "NGen", "Government of Canada", "PLANT", "BDC Climate Tech"]),
    7: (6, 4, 2, ["Startup Gallery Aerospace", "X.com", "BetaKit", "NGen", "SpaceQ", "AIAC", "ventureLAB"]),
    8: (8, 5, 2, ["Startup Gallery Hardware", "X.com", "BetaKit", "NGen", "ventureLAB Hardware Catalyst", "BDC Industrial Innovation"]),
    9: (8, 4, 4, ["Startup Gallery Aerospace", "X.com", "BetaKit", "NGen", "SpaceQ", "AIAC", "ISED"]),
    10: (7, 4, 3, ["Startup Gallery Aerospace", "X.com", "BetaKit", "NGen", "SpaceQ", "AIAC member directory", "Canadian Metalworking"]),
    11: (7, 5, 2, ["Startup Gallery Automotive", "X.com", "BetaKit", "NGen", "APMA", "OVIN", "Government of Canada"]),
    12: (6, 5, 1, ["Startup Gallery Manufacturing", "X.com", "BetaKit", "NGen", "Canadian Manufacturers & Exporters", "company hiring pages"]),
    13: (9, 5, 2, ["Startup Gallery Robotics", "X.com", "BetaKit", "NGen", "SpaceQ", "AIAC", "CanadaBuys", "ventureLAB"]),
}


def make_signal(item: dict[str, object]) -> ExtractedSignal:
    scores = item["scores"]
    return ExtractedSignal(
        company_name=str(item["company_name"]),
        company_domain=str(item["company_domain"]),
        company_url=str(item["company_url"]),
        linkedin_url=str(item["linkedin_url"]),
        location=str(item["location"]),
        industry=str(item["industry"]),
        company_industry=str(item["industry"]),
        software=[],
        signal_type="news",
        signal_source="news",
        pain_signals=list(item["pain_signals"]),
        expansion_signals=list(item["expansion_signals"]),
        raw_score=int(scores["opportunity"]),
        confidence=int(scores["evidence"]) / 100,
        reason=str(item["challenge_summary"]),
        source_url=str(item["source_url"]),
        source_title=str(item["source_title"]),
        detected_at=item["signal_date"],
    )


def main() -> None:
    load_dotenv(".env")
    database = Database()
    database.initialize()
    keywords = {item.id: item for item in database.list_keywords()}
    if set(keywords) != set(COVERAGE):
        raise RuntimeError(f"Persistent keyword set changed: {sorted(keywords)}")

    counts = {keyword_id: 0 for keyword_id in keywords}
    signals = []
    links = []
    errors = {keyword_id: None for keyword_id in keywords}

    for item in EVIDENCE:
        try:
            saved, company = database.persist_signal(make_signal(item))
            signals.append(
                {
                    "company": item["company_name"],
                    "source_url": item["source_url"],
                    "signal_created": saved.created,
                    "duplicate_url": saved.duplicate_url,
                    "company_domain": company.company_domain,
                }
            )
            scores = item["scores"]
            for keyword_id in item["keyword_ids"]:
                row = database.record_keyword_company(
                    keyword_id,
                    str(item["company_name"]),
                    str(item["company_domain"]),
                    source_url=str(item["source_url"]),
                    source_title=str(item["source_title"]),
                    source_publisher=str(item["source_publisher"]),
                    signal_label=str(item["signal_label"]),
                    signal_date=item["signal_date"],
                    challenge_summary=str(item["challenge_summary"]),
                    why_relevant=str(item["why_relevant"]),
                    recommended_products=list(item["products"]),
                    qualification_status="qualified",
                    opportunity_score=int(scores["opportunity"]),
                    manufacturing_fit_score=int(scores["manufacturing"]),
                    trigger_score=int(scores["trigger"]),
                    solution_fit_score=int(scores["solution"]),
                    evidence_quality_score=int(scores["evidence"]),
                    seen_at=RUN_AT,
                )
                if row is None:
                    raise RuntimeError(f"Failed to link {item['company_name']} to keyword {keyword_id}")
                counts[keyword_id] += 1
                links.append(
                    {
                        "keyword_id": keyword_id,
                        "company_id": row.company_id,
                        "company": row.company_name,
                        "status": row.qualification_status,
                    }
                )
        except Exception as exc:
            for keyword_id in item["keyword_ids"]:
                errors[keyword_id] = str(exc)

    for keyword_id in keywords:
        database.record_keyword_search(
            keyword_id,
            result_count=counts[keyword_id],
            error=errors[keyword_id],
        )

    per_keyword = {}
    for keyword_id, keyword in keywords.items():
        reviewed, rejected, duplicates, sources = COVERAGE[keyword_id]
        per_keyword[keyword_id] = {
            "keyword": keyword.keyword,
            "lookback": "rolling 30 days, then 180-day fallback",
            "candidates_reviewed": reviewed,
            "rejected_before_persistence": rejected,
            "qualified_published": counts[keyword_id],
            "watchlist_published": 0,
            "existing_records_upgraded_or_hidden": 0,
            "duplicates_skipped_or_reassessed": duplicates,
            "sources_checked": sources,
            "startup_gallery": "Direct related-industry page checked; no Canada-specific qualifying lead.",
            "x_com": "Inaccessible: browser URL policy and ERR_CERT_AUTHORITY_INVALID; no workaround attempted.",
            "betakit": "Direct keyword search completed; older/directory-only and software-led results rejected.",
            "ngen": "Direct on-page keyword search completed; no new company-specific qualifying result.",
            "error": errors[keyword_id],
        }

    print(
        json.dumps(
            {
                "run_at": RUN_AT.isoformat(),
                "signals": signals,
                "links": links,
                "published_counts": counts,
                "per_keyword": per_keyword,
            },
            indent=2,
            default=str,
        )
    )


if __name__ == "__main__":
    main()
