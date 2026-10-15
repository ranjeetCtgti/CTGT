from __future__ import annotations

import json
from datetime import datetime, timezone

from dotenv import load_dotenv

from db.database import Database
from models.schema import ExtractedSignal


RUN_AT = datetime.now(timezone.utc)


def dt(year: int, month: int, day: int) -> datetime:
    return datetime(year, month, day, tzinfo=timezone.utc)


NEW_CANDIDATES = [
    {
        "keyword_ids": [8],
        "company_name": "Greentank Technologies Corp.",
        "company_domain": "greentanktech.com",
        "company_url": "https://www.greentanktech.com/",
        "location": "Toronto, Ontario, Canada",
        "industry": "Vaporization hardware and advanced-materials manufacturing",
        "products": ["Teamcenter", "Opcenter"],
        "scores": {
            "opportunity": 88,
            "manufacturing": 94,
            "trigger": 94,
            "solution": 91,
            "evidence": 95,
        },
        "pain_signals": [
            "Must industrialize the Quantum Chip platform while coordinating owned semiconductor-style chip production, vaporization-device variants, materials R&D and tier-one customer requirements.",
            "Must preserve controlled bills of material, engineering changes, production recipes and quality genealogy while expanding a semi-automated Toronto manufacturing footprint.",
        ],
        "expansion_signals": [
            "Secured a US$20 million strategic investment from AIR Global at an approximately US$170 million pre-money valuation.",
            "Will use the investment to expand owned chip-manufacturing capacity, advance the Quantum Chip platform and support global commercialization and long-term supply commitments.",
        ],
        "evidence": {
            "signal_date": dt(2026, 7, 31),
            "source_url": "https://www.greentanktech.com/news/greentank-secures-usd-20-million-strategic-investment-from-air-global-plc-to-accelerate-rd-capabilities-and-manufacturing-footprint/",
            "source_title": "Greentank Secures USD $20 Million Strategic Investment from AIR Global PLC to Accelerate R&D Capabilities and Manufacturing Footprint",
            "source_publisher": "Greentank Technologies",
            "signal_label": "US$20M AIR Global investment funds Quantum Chip R&D and owned manufacturing expansion",
            "challenge_summary": (
                "On July 31, 2026, Toronto-based Greentank announced a US$20 million strategic equity investment from AIR Global at an approximately US$170 million pre-money valuation, with proceeds earmarked for the Quantum Chip platform, expanded R&D and a larger fully owned semi-automated chip-manufacturing footprint; the transaction also includes long-term supply commitments. Greentank's official site describes a 7,000-square-foot Toronto R&D laboratory and white-label vaporization hardware produced under formal quality controls. Inference: scaling a materials-intensive chip platform across tier-one customer variants creates immediate bill-of-material, engineering-change, process-recipe, supplier and lot-traceability pressure."
            ),
            "why_relevant": (
                "Teamcenter is the smallest defensible product-data backbone for controlling Quantum Chip variants, approved components, customer configurations and engineering releases. Opcenter can connect those released definitions to semi-automated production, in-process quality and chip-level genealogy, helping Greentank increase capacity without losing repeatability or auditability. The investment and supply commitments make the scale-up active now, before manufacturing volume and customer-specific change traffic rise."
            ),
        },
    },
    {
        "keyword_ids": [5],
        "company_name": "Volta Energy Solutions Canada Inc.",
        "company_domain": "voltasolutions.ca",
        "company_url": "https://voltasolutions.ca/en/",
        "location": "Granby, Quebec, Canada",
        "industry": "Battery-grade copper-foil manufacturing for EV and energy-storage cells",
        "products": ["Tecnomatix", "Opcenter", "Teamcenter"],
        "scores": {
            "opportunity": 92,
            "manufacturing": 99,
            "trigger": 99,
            "solution": 95,
            "evidence": 100,
        },
        "pain_signals": [
            "Must commission a highly automated battery-grade copper-foil plant and stabilize yield, equipment performance, quality genealogy and material flow at industrial scale.",
            "Must expand from 25,000 tonnes per year in 2027 toward 63,000 tonnes while coordinating engineering, production, quality and capital-project changes.",
        ],
        "expansion_signals": [
            "Canada announced up to C$70 million for Volta's C$760.9 million Granby facility upgrade and expansion.",
            "The project targets 25,000 tonnes of annual copper-foil capacity from 2027, scaling to 63,000 tonnes, and 260 new jobs.",
        ],
        "evidence": {
            "signal_date": dt(2026, 7, 30),
            "source_url": "https://www.canada.ca/en/innovation-science-economic-development/news/2026/07/government-of-canada-invests-70-million-to-strengthen-the-ev-battery-supply-chain-in-quebec.html",
            "source_title": "Government of Canada invests $70 million to strengthen the EV battery supply chain in Quebec",
            "source_publisher": "Innovation, Science and Economic Development Canada",
            "signal_label": "C$70M supports Volta's C$760.9M Granby copper-foil factory expansion",
            "challenge_summary": (
                "On July 30, 2026, the Government of Canada announced up to C$70 million for Volta Energy Solutions Canada's C$760.9 million project to upgrade and expand an acquired Granby facility for battery-grade copper foil, creating 260 jobs and targeting 25,000 tonnes of annual output from 2027 before scaling to 63,000 tonnes. Volta's official site says the North American plant will use a fully automated process to make roughly 30-kilometre rolls of ultra-thin foil for EV and energy-storage cells. Inference: commissioning and then more than doubling a precision-materials line creates urgent factory-layout, ramp, process-control, equipment-integration, yield, quality-genealogy and production-visibility demands."
            ),
            "why_relevant": (
                "Tecnomatix can validate line layout, material flow and ramp scenarios before capital changes are locked in, while Opcenter can govern execution, in-process quality and coil or lot genealogy during commissioning. Teamcenter is justified narrowly for controlled plant, process and product definitions that must stay aligned through the 25,000-to-63,000-tonne expansion. Construction and commissioning are moving toward 2027 production, so digital factory and traceability decisions are time-critical now rather than after the line stabilizes."
            ),
        },
    },
]


COVERAGE = {
    1: (7, 2, 5, ["Startup Gallery", "X.com public/X-ray", "BetaKit", "NGen", "SpaceQ", "AIAC", "ventureLAB HCI", "BDC"], "Startup Gallery and direct mandatory-source queries yielded no new qualifying Canadian company. X.com direct browsing was unavailable because the in-app Browser dependency could not initialize; public X-ray results produced no relevant lead. BetaKit's July aerospace results were already known domains."),
    2: (8, 5, 3, ["Startup Gallery", "X.com public/X-ray", "BetaKit", "NGen", "Automate Canada", "ventureLAB HCI", "Velocity", "BDC"], "Mandatory sources produced no new qualifying robotics manufacturer. X.com direct browsing was unavailable; public X-ray results had no usable candidate. Apera AI and other directory leads lacked a sufficiently specific manufacturing trigger or were software-led."),
    3: (8, 3, 5, ["Startup Gallery", "X.com public/X-ray", "BetaKit", "NGen", "Canada's Ocean Supercluster", "CMISA", "Marine Log", "Naval News"], "Mandatory sources yielded no new shipbuilder. Ocean Supercluster and industry reporting primarily resurfaced existing domains or equipment/software suppliers; these were not treated as shipyards. X.com direct browsing was unavailable."),
    4: (6, 4, 2, ["Startup Gallery", "X.com public/X-ray", "BetaKit", "NGen", "OVIN", "APMA", "Electric Autonomy Canada", "BDC"], "No new Canadian vehicle OEM cleared the dated-trigger gate. APMA/OVIN ecosystem pages remained discovery-only, and X.com direct browsing was unavailable."),
    5: (10, 5, 4, ["Startup Gallery", "X.com public/X-ray", "BetaKit", "NGen", "Canada.ca/ISED", "FedDev Ontario", "PLANT", "BDC Climate Tech"], "Volta Energy Solutions Canada cleared the gate on a dated federal factory-expansion announcement and official manufacturing evidence. Other energy results were existing domains, non-manufacturing operators or insufficiently specific leads; X.com direct browsing was unavailable."),
    7: (9, 3, 5, ["Startup Gallery", "X.com public/X-ray", "BetaKit", "NGen", "SpaceQ", "AIAC", "ventureLAB HCI", "BDC StrongNorth"], "Canada Rocket Company's existing primary evidence was newly linked to this exact aircraft/UAV/eVTOL keyword. SpaceQ, AIAC and BetaKit otherwise resurfaced existing or directory-only aerospace domains; X.com direct browsing was unavailable."),
    8: (10, 6, 3, ["Startup Gallery", "X.com public/X-ray", "BetaKit", "NGen", "ventureLAB HCI", "Velocity", "BDC Capital", "FedDev Ontario"], "Greentank cleared the gate on a dated US$20M investment tied directly to owned chip manufacturing and R&D expansion. Startup Gallery's hardware funding results were global discovery leads only; X.com direct browsing was unavailable."),
    9: (9, 2, 7, ["Startup Gallery", "X.com public/X-ray", "BetaKit", "NGen", "SpaceQ", "AIAC Industry Guide", "PacifiCan", "BDC"], "Recent aerospace searches largely resurfaced Canada Rocket Company, NordSpace, North Vector Dynamics and Sentinel. AIAC profiles were discovery-only; no additional domain cleared the gate. X.com direct browsing was unavailable."),
    10: (7, 4, 3, ["Startup Gallery", "X.com public/X-ray", "BetaKit", "NGen", "SpaceQ", "AIAC Industry Guide", "Canadian Metalworking", "CED Quebec"], "No new Tier 1/Tier 2 supplier had both verified manufacturing identity and a sufficiently recent source-backed trigger. AIAC member/guide results stayed discovery-only; X.com direct browsing was unavailable."),
    11: (6, 4, 2, ["Startup Gallery", "X.com public/X-ray", "BetaKit", "NGen", "OVIN", "APMA", "Electric Autonomy Canada", "PLANT"], "No new Canadian OEM cleared the gate. Directory and Project Arrow ecosystem membership were not used as qualification; X.com direct browsing was unavailable."),
    12: (6, 4, 2, ["Startup Gallery", "X.com public/X-ray", "BetaKit", "NGen", "CME", "PLANT", "BDC LIFT", "manufacturer career pages"], "CME/PLANT/BDC searches supplied market context but no new company-specific ERP-PLM integration trigger. Software vendors and consultants were rejected; X.com direct browsing was unavailable."),
    13: (9, 3, 6, ["Startup Gallery", "X.com public/X-ray", "BetaKit", "NGen", "SpaceQ", "AIAC", "CanadaBuys", "BDC StrongNorth"], "Recent results mainly resurfaced already qualified drone and autonomous-aircraft companies. Procurement notices without Canadian manufacturing proof and directory-only leads were not published; X.com direct browsing was unavailable."),
}


def make_signal(candidate: dict[str, object]) -> ExtractedSignal:
    evidence = candidate["evidence"]
    scores = candidate["scores"]
    return ExtractedSignal(
        company_name=str(candidate["company_name"]),
        company_domain=str(candidate["company_domain"]),
        company_url=str(candidate["company_url"]),
        location=str(candidate["location"]),
        industry=str(candidate["industry"]),
        company_industry=str(candidate["industry"]),
        signal_type="news",
        signal_source="news",
        pain_signals=list(candidate["pain_signals"]),
        expansion_signals=list(candidate["expansion_signals"]),
        raw_score=int(scores["opportunity"]),
        confidence=int(scores["evidence"]) / 100,
        reason=str(evidence["challenge_summary"]),
        source_url=str(evidence["source_url"]),
        source_title=str(evidence["source_title"]),
        detected_at=evidence["signal_date"],
    )


def replay_existing_signal(database: Database, row, company) -> None:
    database.persist_signal(
        ExtractedSignal(
            company_name=company.company_name,
            company_domain=company.company_domain,
            company_url=company.company_url,
            linkedin_url=company.linkedin_url,
            location=company.location,
            industry=company.industry,
            company_industry=company.company_industry,
            software=list(company.software or []),
            signal_type="news",
            signal_source="news",
            pain_signals=[row.challenge_summary] if row.challenge_summary else [],
            expansion_signals=[row.signal_label] if row.signal_label else [],
            raw_score=row.opportunity_score,
            confidence=row.evidence_quality_score / 100,
            reason=row.challenge_summary,
            source_url=row.source_url,
            source_title=row.source_title,
            detected_at=row.signal_date or row.last_seen_at,
        )
    )


def main() -> None:
    load_dotenv(".env")
    database = Database()
    database.initialize()
    keywords = {item.id: item for item in database.list_keywords()}
    if set(keywords) != set(COVERAGE):
        raise RuntimeError(f"Persistent keyword set changed: {sorted(keywords)}")

    diagnostics = {
        name: [
            {"id": row.company_id, "name": row.company_name, "domain": row.company_domain, "status": row.qualification_status}
            for row in database.list_keyword_companies(limit=5000)
            if name.lower().split()[0] in row.company_name.lower()
        ]
        for name in ["Greentank Technologies", "Volta Energy Solutions", "Celerity Craft", "Canada Rocket Company"]
    }

    published_counts = {keyword_id: 0 for keyword_id in keywords}
    signal_results = []
    linked_companies = []

    for candidate in NEW_CANDIDATES:
        saved, company = database.persist_signal(make_signal(candidate))
        evidence = candidate["evidence"]
        scores = candidate["scores"]
        signal_results.append({
            "company": candidate["company_name"],
            "source_url": evidence["source_url"],
            "created": saved.created,
            "duplicate_url": saved.duplicate_url,
            "domain": company.company_domain,
        })
        for keyword_id in candidate["keyword_ids"]:
            linked = database.record_keyword_company(
                keyword_id,
                candidate["company_name"],
                candidate["company_domain"],
                source_url=evidence["source_url"],
                source_title=evidence["source_title"],
                source_publisher=evidence["source_publisher"],
                signal_label=evidence["signal_label"],
                signal_date=evidence["signal_date"],
                challenge_summary=evidence["challenge_summary"],
                why_relevant=evidence["why_relevant"],
                recommended_products=candidate["products"],
                qualification_status="qualified",
                opportunity_score=scores["opportunity"],
                manufacturing_fit_score=scores["manufacturing"],
                trigger_score=scores["trigger"],
                solution_fit_score=scores["solution"],
                evidence_quality_score=scores["evidence"],
                seen_at=RUN_AT,
            )
            if linked is None:
                raise RuntimeError(f"Could not link {candidate['company_name']} to keyword {keyword_id}")
            published_counts[keyword_id] += 1
            linked_companies.append({"keyword_id": keyword_id, "company_id": linked.company_id, "company": linked.company_name})

    # Canada Rocket Company already has qualified, primary evidence under the
    # aerospace-operations keyword. Replaying its source is idempotent, then the
    # same assessed evidence is linked to the exact aircraft/UAV/eVTOL keyword.
    all_rows = database.list_keyword_companies(limit=5000)
    rocket_rows = [
        row for row in all_rows
        if row.company_domain == "canadarocketcompany.com"
        and row.qualification_status == "qualified"
        and row.source_url
    ]
    if not rocket_rows:
        raise RuntimeError("Qualified Canada Rocket Company evidence was not found")
    rocket = max(rocket_rows, key=lambda row: row.signal_date or row.last_seen_at)
    leads_by_domain = {lead.company_domain: lead for lead in database.get_leads() if lead.company_domain}
    replay_existing_signal(database, rocket, leads_by_domain[rocket.company_domain])
    rocket_link = database.record_keyword_company(
        7,
        rocket.company_name,
        rocket.company_domain,
        source_url=rocket.source_url,
        source_title=rocket.source_title,
        source_publisher=rocket.source_publisher,
        signal_label=rocket.signal_label,
        signal_date=rocket.signal_date,
        challenge_summary=rocket.challenge_summary,
        why_relevant=rocket.why_relevant,
        recommended_products=rocket.recommended_products,
        qualification_status=rocket.qualification_status,
        opportunity_score=rocket.opportunity_score,
        manufacturing_fit_score=rocket.manufacturing_fit_score,
        trigger_score=rocket.trigger_score,
        solution_fit_score=rocket.solution_fit_score,
        evidence_quality_score=rocket.evidence_quality_score,
        seen_at=RUN_AT,
    )
    if rocket_link is None:
        raise RuntimeError("Could not link Canada Rocket Company to keyword 7")
    published_counts[7] += 1
    linked_companies.append({"keyword_id": 7, "company_id": rocket_link.company_id, "company": rocket_link.company_name})

    for keyword_id, result_count in published_counts.items():
        database.record_keyword_search(keyword_id, result_count=result_count)

    final_rows = database.list_keyword_companies(limit=5000)
    eligible_ids = sorted({
        row.company_id for row in final_rows if row.qualification_status in {"qualified", "watchlist"}
    })
    per_keyword = {}
    for keyword_id, (reviewed, rejected, duplicates, sources, notes) in COVERAGE.items():
        per_keyword[keyword_id] = {
            "keyword": keywords[keyword_id].keyword,
            "lookback": "rolling 30 days, then 180-day fallback for ongoing evidence",
            "candidates_reviewed": reviewed,
            "rejected_before_persistence": rejected,
            "qualified_published": published_counts[keyword_id],
            "watchlist_published": 0,
            "existing_records_upgraded_or_hidden": 0,
            "duplicates_skipped": duplicates,
            "sources_checked": sources,
            "blockers_or_zero_results": notes,
        }

    print(json.dumps({
        "run_at": RUN_AT.isoformat(),
        "preexisting_matches": diagnostics,
        "signals": signal_results,
        "linked_companies": linked_companies,
        "eligible_company_count": len(eligible_ids),
        "eligible_company_ids": eligible_ids,
        "per_keyword": per_keyword,
        "in_app_browser": "blocked: trusted RPC dependency browser-service.mjs did not resolve within the configured trusted code path; no safety barrier was bypassed",
    }, indent=2, default=str))


if __name__ == "__main__":
    main()
