from __future__ import annotations

import json
from datetime import datetime, timezone

from dotenv import load_dotenv

from db.database import Database
from models.schema import ExtractedSignal


RUN_AT = datetime.now(timezone.utc)


def dt(year: int, month: int, day: int) -> datetime:
    return datetime(year, month, day, tzinfo=timezone.utc)


CANDIDATES = [
    {
        "keyword_ids": [10],
        "company_name": "Velocity Machining & Welding Inc.",
        "company_domain": "velocitymachining.ca",
        "company_url": "https://velocitymachining.ca/",
        "location": "Dartmouth, Nova Scotia, Canada",
        "industry": "Precision machining, welding and fabrication for aerospace, marine and industrial customers",
        "products": ["NX", "Opcenter"],
        "scores": {
            "opportunity": 90,
            "manufacturing": 99,
            "trigger": 97,
            "solution": 92,
            "evidence": 99,
        },
        "pain_signals": [
            "Must commission automated machining equipment while preserving drawing, CNC-program and job-routing control across aerospace, marine, transportation and other high-mix component work.",
            "Must add at least 75 productive machining hours per week with the existing workforce while maintaining inspection discipline and delivery performance.",
        ],
        "expansion_signals": [
            "Received a C$875,500 repayable ACOA contribution for automated machining equipment at its Dartmouth facility.",
            "The automation project is expected to add at least 75 hours of production capacity each week and shorten component delivery times.",
        ],
        "evidence": {
            "signal_date": dt(2026, 7, 28),
            "source_url": "https://www.canada.ca/en/atlantic-canada-opportunities/news/2026/07/federal-investment-helps-dartmouth-manufacturer-produce-critical-parts-faster.html",
            "source_title": "Federal investment helps Dartmouth manufacturer produce critical parts faster",
            "source_publisher": "Atlantic Canada Opportunities Agency",
            "signal_label": "C$875,500 funds automated machining equipment adding at least 75 production hours per week",
            "challenge_summary": (
                "On July 28, 2026, ACOA announced a C$875,500 repayable contribution for Velocity Machining & Welding to purchase and install automated machining equipment at its Dartmouth facility; the system is expected to add at least 75 production hours per week and speed delivery of industrial components to aerospace, marine, transportation and other customers. Velocity's official site confirms in-house 3D CAD, prototypes through complete machines and assemblies, CNC machining, fabrication and quality inspection, while its current hiring describes 5-axis mill-turn programming and unattended production. Inference: adding automated capacity to a high-mix job shop creates immediate pressure to keep customer drawings, CNC programs, routings, inspection results and production priorities synchronized while doing more with the existing workforce."
            ),
            "why_relevant": (
                "NX is the narrow CAD/CAM fit for controlling complex part geometry and multiaxis machining programs as Velocity expands automated mill-turn capacity. Opcenter can dispatch released work, track machine and job progress, capture in-process inspection and provide the production visibility needed to turn the new 75 weekly hours into reliable on-time output. The equipment purchase and installation are active now, so programming, execution and quality controls should be established before the new capacity becomes operational."
            ),
        },
    },
    {
        "keyword_ids": [2],
        "company_name": "ForceN Inc.",
        "company_domain": "forcen.tech",
        "company_url": "https://www.forcen.tech/",
        "location": "Toronto, Ontario, Canada",
        "industry": "Force-torque sensing hardware for surgical, logistics and frontier robotics",
        "products": ["Teamcenter", "Opcenter"],
        "scores": {
            "opportunity": 86,
            "manufacturing": 96,
            "trigger": 92,
            "solution": 91,
            "evidence": 90,
        },
        "pain_signals": [
            "Must industrialize new force-torque sensor variants by connecting mechanical, electronic and embedded-system design changes to manufacturing processes and quality controls.",
            "Must scale production from a single prototype to more than 1,000 units while controlling new-product introduction, design for manufacturability and production outcomes.",
        ],
        "expansion_signals": [
            "Posted a Toronto Manufacturing Engineer role on July 23, 2026 to bridge design and production and own new-product introduction for new sensor variants.",
            "The role is explicitly responsible for scaling builds from one prototype to high-rate production of more than 1,000 units.",
        ],
        "evidence": {
            "signal_date": dt(2026, 7, 23),
            "source_url": "https://techjobs.marsdd.com/companies/forcen/jobs/87203320-manufacturing-engineer",
            "source_title": "Manufacturing Engineer @ Forcen",
            "source_publisher": "MaRS Discovery District Job Board",
            "signal_label": "Manufacturing Engineer hire targets NPI scale-up from one prototype to 1,000+ sensor units",
            "challenge_summary": (
                "On July 23, 2026, ForceN posted a Toronto Manufacturing Engineer role to bridge design and production, own new-product introduction for new force-torque sensor variants, improve designs and processes for manufacturability, and scale output from one prototype to more than 1,000 units. ForceN's official site confirms that its Toronto team designs, tests and manufactures high-precision sensing systems for surgical, logistics and frontier-robotics customers, with calibration traceability and ISO 9001/ISO 13485 production support. Inference: rapid variant industrialization creates immediate mechanical, electronic and embedded-release, bill-of-material, process-change, supplier-quality and device-genealogy pressure."
            ),
            "why_relevant": (
                "Teamcenter can keep sensor variants, bills of material, design releases and manufacturing changes aligned across hardware engineering, suppliers and production. Opcenter can execute the released build process and capture unit-level assembly, calibration and quality history as volume moves from prototypes to 1,000-plus units. The dedicated NPI hire makes the buying window current: ForceN is defining the processes and systems that will govern its next production scale now."
            ),
        },
    },
    {
        "keyword_ids": [14],
        "company_name": "North Vector Dynamics Inc.",
        "company_domain": "northvectordynamics.com",
        "company_url": "https://northvectordynamics.com/",
        "location": "Calgary, Alberta, Canada",
        "industry": "Defence and aerospace propulsion, autonomous systems and precision weapons",
        "products": ["Simcenter", "Teamcenter"],
        "scores": {
            "opportunity": 89,
            "manufacturing": 94,
            "trigger": 91,
            "solution": 95,
            "evidence": 91,
        },
        "pain_signals": [
            "Must coordinate propulsion design, analysis, test evidence and configuration changes across a new investor-partner and a Department of National Defence-backed hypersonic R&D network.",
            "Must mature overlapping defence-propulsion and hypersonic roadmaps while preserving traceable technical baselines across complex, safety-critical hardware programs.",
        ],
        "expansion_signals": [
            "NordSpace Ventures disclosed a strategic investment in North Vector Dynamics on July 31, 2026 as part of the company's late-2025 strategic fundraise.",
            "The investment deepens an active technical partnership exploring defence applications for rocket propulsion and is intended to accelerate overlapping propulsion and hypersonic roadmaps built in Canada.",
        ],
        "evidence": {
            "signal_date": dt(2026, 7, 31),
            "source_url": "https://betakit.com/nordspaces-venture-arm-makes-undisclosed-strategic-investment-in-north-vector-dynamics/",
            "source_title": "NordSpace's venture arm makes undisclosed strategic investment in North Vector Dynamics",
            "source_publisher": "BetaKit",
            "signal_label": "NordSpace investment accelerates shared defence-propulsion and hypersonic roadmaps",
            "challenge_summary": (
                "On July 31, 2026, BetaKit reported that NordSpace Ventures made a strategic investment in Calgary-based North Vector Dynamics as part of its late-2025 fundraise, deepening an active technical partnership that is exploring defence applications for NordSpace rocket propulsion. Both companies participate in a Department of National Defence-backed hypersonic R&D network, and North Vector said the closer partnership will accelerate overlapping defence-propulsion and hypersonic roadmaps built in Canada. Inference: moving faster across two organizations on high-speed propulsion hardware increases coupled aerodynamic, thermal and structural simulation workload and creates configuration, test-evidence and technical-data control pressure."
            ),
            "why_relevant": (
                "Simcenter is the narrow engineering fit for multidisciplinary propulsion and hypersonic analysis, including thermal, flow and structural validation before expensive hardware tests. Teamcenter can keep models, requirements-derived configurations, test results and partner-controlled technical data aligned as NordSpace and North Vector converge their roadmaps. The new strategic capital and closer working relationship create urgency now, while shared methods and configuration controls can still be established before program activity expands."
            ),
        },
    },
    {
        "keyword_ids": [15],
        "company_name": "Enedym Inc.",
        "company_domain": "enedym.com",
        "company_url": "https://enedym.com/",
        "location": "Hamilton, Ontario, Canada",
        "industry": "Rare-earth-free electric motors, powertrains and motor-control technology",
        "products": ["Teamcenter", "Opcenter", "Tecnomatix"],
        "scores": {
            "opportunity": 79,
            "manufacturing": 96,
            "trigger": 76,
            "solution": 92,
            "evidence": 90,
        },
        "pain_signals": [
            "Must expand pilot motor production from a few thousand to 10,000 units per year while supporting as many as 25 motor variants and multiple licensing or joint-venture partners.",
            "Must plan a Hamilton GigaFARM and coordinate stator, rotor and winding-equipment partners without losing product configuration, process or quality traceability.",
        ],
        "expansion_signals": [
            "In a January 16, 2026 interview, Enedym said its Hamilton FARM would expand from a few thousand units to 10,000 motors per year within 18 to 24 months and support up to 25 motor variants.",
            "The company also disclosed plans for a Hamilton GigaFARM while advancing licensing and joint-venture production models with strategic component and equipment partners.",
        ],
        "evidence": {
            "signal_date": dt(2026, 1, 16),
            "source_url": "https://autotechinsight.spglobal.com/news/5286151/we-have-solved-the-technical-limitations-associated-with-switched-reluctance-motors-ali-emadi-founder-and-ceo-enedym-inc",
            "source_title": "We have solved the technical limitations associated with switched reluctance motors: Ali Emadi, founder and CEO, Enedym Inc.",
            "source_publisher": "S&P Global AutoTechInsight",
            "signal_label": "Hamilton FARM plans 10,000 annual motors, 25 variants and a future GigaFARM",
            "challenge_summary": (
                "In a January 16, 2026 interview, Enedym said its Hamilton Facility for Advanced Rapid Manufacturing would expand from a few thousand motors per year to 10,000 within 18 to 24 months, covering as many as 25 motor variants, while the company plans a larger Hamilton GigaFARM and advances licensing and joint-venture production. Enedym identified JFE Shoji for stator and rotor cores and Marsilli for motor-winding equipment, alongside in-house, licensed and joint-venture manufacturing paths. Inference: multiplying volume and variants across internal and partner factories creates immediate bill-of-material, design-release, tooling, process, capacity-planning and motor-genealogy complexity."
            ),
            "why_relevant": (
                "Teamcenter can control the 25 motor configurations, partner-specific bills of material and released engineering changes across in-house, licensed and joint-venture production. Tecnomatix can model the 10,000-unit FARM expansion and future GigaFARM flow before equipment and layout decisions are locked, while Opcenter can execute production and preserve unit-level process and quality history. The 18-to-24-month capacity plan is already running, so factory and information-system decisions need to precede the volume ramp."
            ),
        },
    },
]


COVERAGE = {
    1: (5, 1, 4, ["Startup Gallery", "X.com public/X-ray", "BetaKit", "NGen", "SpaceQ", "AIAC", "ventureLAB HCI", "BDC"], "No new qualifying newly formed Canadian aerospace manufacturer. Mandatory Startup Gallery and public X-ray checks returned zero relevant new candidates; direct X and the in-app Browser were unavailable because the trusted browser dependency could not initialize."),
    2: (7, 4, 2, ["Startup Gallery", "X.com public/X-ray", "BetaKit", "NGen", "ventureLAB HCI", "Communitech", "MaRS", "BDC Capital"], "ForceN cleared the gate on a July 23 NPI/manufacturing hire corroborated by its official hardware-manufacturing site. Other robotics results were older, software-led, directory-only or duplicate; direct X was unavailable."),
    3: (5, 2, 3, ["Startup Gallery", "X.com public/X-ray", "BetaKit", "NGen", "Canada's Ocean Supercluster", "Naval News", "CanadaBuys"], "No new shipbuilder cleared the gate. Marine equipment, technology and software suppliers were not treated as shipbuilders; direct X was unavailable and Startup Gallery yielded zero relevant leads."),
    4: (5, 3, 2, ["Startup Gallery", "X.com public/X-ray", "BetaKit", "NGen", "APMA", "OVIN", "Electric Autonomy Canada", "BDC"], "No new Canadian vehicle OEM had both verified manufacturing identity and a current trigger. Directory and ecosystem membership remained discovery-only; direct X was unavailable."),
    5: (5, 2, 3, ["Startup Gallery", "X.com public/X-ray", "BetaKit", "NGen", "Canada.ca/ISED", "BDC Climate Tech", "FedDev Ontario", "PLANT"], "Recent searches mostly resurfaced existing energy manufacturers or non-manufacturing operators. Startup Gallery and X-ray returned no new qualifying lead; direct X was unavailable."),
    7: (6, 1, 5, ["Startup Gallery", "X.com public/X-ray", "BetaKit", "NGen", "SpaceQ", "AIAC", "BDC StrongNorth", "ventureLAB HCI"], "SpaceQ, AIAC and BetaKit resurfaced existing aerospace and launch companies; no new domain cleared the gate. Startup Gallery and X-ray yielded no relevant new candidate; direct X was unavailable."),
    8: (6, 3, 3, ["Startup Gallery", "X.com public/X-ray", "BetaKit", "NGen", "BDC Capital", "MaRS", "Communitech", "FedDev Ontario"], "Funding searches resurfaced Greentank, Landing Zones and other existing companies. Startup Gallery supplied discovery-only leads without a corroborated current trigger; direct X was unavailable."),
    9: (6, 1, 5, ["Startup Gallery", "X.com public/X-ray", "BetaKit", "NGen", "SpaceQ", "AIAC Industry Guide", "CanadaBuys", "BDC"], "Recent aerospace operations searches mainly resurfaced existing qualified domains. AIAC profiles remained discovery-only, and Startup Gallery/X-ray produced no new qualifying candidate; direct X was unavailable."),
    10: (8, 3, 4, ["Startup Gallery", "X.com public/X-ray", "BetaKit", "NGen", "SpaceQ", "AIAC Member Directory", "ACOA", "Canadian Metalworking"], "Velocity Machining cleared the gate on a dated federal automation investment and official machining evidence. AIAC directory entries were not published without triggers; Canadian Metalworking was blocked by robots.txt and direct X was unavailable."),
    11: (5, 3, 2, ["Startup Gallery", "X.com public/X-ray", "BetaKit", "NGen", "APMA", "OVIN", "Electric Autonomy Canada", "PLANT"], "No new Canadian OEM cleared the gate. Searches returned ecosystem pages, established companies without a new trigger, or non-OEM suppliers; direct X was unavailable."),
    12: (5, 4, 1, ["Startup Gallery", "X.com public/X-ray", "BetaKit", "NGen", "CME", "BDC LIFT", "PLANT", "manufacturer career pages"], "No company-specific ERP/PLM integration trigger was found. Software vendors and consultants were rejected, and direct X was unavailable."),
    13: (6, 2, 4, ["Startup Gallery", "X.com public/X-ray", "BetaKit", "NGen", "SpaceQ", "AIAC", "BDC StrongNorth", "CanadaBuys"], "Recent searches resurfaced existing autonomous-aircraft and drone companies. ForceN supplies robotic sensing but does not itself develop an autonomous vehicle or drone, so it was not linked here; direct X was unavailable."),
    14: (7, 3, 3, ["Startup Gallery", "X.com public/X-ray", "BetaKit", "NGen", "CADSI GATEWAY", "AIAC", "CanadaBuys", "BDC StrongNorth"], "North Vector Dynamics' existing qualified identity received a new July 31 strategic-investment and technical-partnership signal and was linked to this new defence-products keyword. Startup Gallery and public X-ray produced no new qualifying domain; direct X was unavailable."),
    15: (7, 4, 2, ["Startup Gallery", "X.com public/X-ray", "BetaKit", "NGen EVMP", "APMA Project Arrow", "OVIN", "Electric Autonomy Canada", "BDC Capital"], "Enedym cleared the ongoing-evidence gate on a 10,000-unit Hamilton motor-production plan with 25 variants and a future GigaFARM. The 30-day mandatory searches yielded no new EV startup; direct X was unavailable and directory or portfolio membership alone was not used."),
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


def main() -> None:
    load_dotenv(".env")
    database = Database()
    database.initialize()
    keywords_before = {item.id: item for item in database.list_keywords()}
    if set(keywords_before) != set(COVERAGE):
        raise RuntimeError(f"Persistent keyword set changed: {sorted(keywords_before)}")

    existing_rows = database.list_keyword_companies(limit=5000)
    existing_leads = database.get_leads()
    diagnostics = {
        candidate["company_name"]: {
            "company_matches": [
                {"name": lead.company_name, "domain": lead.company_domain, "signal_count": lead.signal_count}
                for lead in existing_leads
                if str(candidate["company_name"]).lower().split()[0] in lead.company_name.lower()
                or lead.company_domain == candidate["company_domain"]
            ],
            "keyword_matches": [
                {"company_id": row.company_id, "keyword_id": row.keyword_id, "status": row.qualification_status, "source_url": row.source_url}
                for row in existing_rows
                if str(candidate["company_name"]).lower().split()[0] in row.company_name.lower()
                or row.company_domain == candidate["company_domain"]
            ],
        }
        for candidate in CANDIDATES
    }

    published_counts = {keyword_id: 0 for keyword_id in keywords_before}
    signal_results = []
    linked_companies = []

    for candidate in CANDIDATES:
        saved, company = database.persist_signal(make_signal(candidate))
        evidence = candidate["evidence"]
        scores = candidate["scores"]
        signal_results.append({
            "company": candidate["company_name"],
            "source_url": evidence["source_url"],
            "created": saved.created,
            "duplicate_url": saved.duplicate_url,
            "domain": company.company_domain,
            "signal_count": company.signal_count,
        })
        for keyword_id in candidate["keyword_ids"]:
            linked = database.record_keyword_company(
                keyword_id,
                str(candidate["company_name"]),
                str(candidate["company_domain"]),
                source_url=str(evidence["source_url"]),
                source_title=str(evidence["source_title"]),
                source_publisher=str(evidence["source_publisher"]),
                signal_label=str(evidence["signal_label"]),
                signal_date=evidence["signal_date"],
                challenge_summary=str(evidence["challenge_summary"]),
                why_relevant=str(evidence["why_relevant"]),
                recommended_products=list(candidate["products"]),
                qualification_status="qualified",
                opportunity_score=int(scores["opportunity"]),
                manufacturing_fit_score=int(scores["manufacturing"]),
                trigger_score=int(scores["trigger"]),
                solution_fit_score=int(scores["solution"]),
                evidence_quality_score=int(scores["evidence"]),
                seen_at=RUN_AT,
            )
            if linked is None:
                raise RuntimeError(f"Could not link {candidate['company_name']} to keyword {keyword_id}")
            published_counts[keyword_id] += 1
            linked_companies.append({
                "keyword_id": keyword_id,
                "company_id": linked.company_id,
                "company": linked.company_name,
                "domain": linked.company_domain,
            })

    for keyword_id, result_count in published_counts.items():
        if database.record_keyword_search(keyword_id, result_count=result_count) is None:
            raise RuntimeError(f"Could not record search completion for keyword {keyword_id}")

    keywords_after = {item.id: item for item in database.list_keywords()}
    final_rows = database.list_keyword_companies(limit=5000)
    eligible_ids = sorted({
        row.company_id for row in final_rows if row.qualification_status in {"qualified", "watchlist"}
    })
    per_keyword = {}
    for keyword_id, (reviewed, rejected, duplicates, sources, notes) in COVERAGE.items():
        before = keywords_before[keyword_id]
        after = keywords_after[keyword_id]
        if after.search_count != before.search_count + 1:
            raise RuntimeError(f"Keyword {keyword_id} search count did not increment exactly once")
        per_keyword[keyword_id] = {
            "keyword": before.keyword,
            "lookback": "rolling 30 days, then 180-day fallback for ongoing evidence",
            "candidates_reviewed": reviewed,
            "rejected_before_persistence": rejected,
            "qualified_published": published_counts[keyword_id],
            "watchlist_published": 0,
            "existing_records_upgraded_or_hidden": 0,
            "duplicates_skipped": duplicates,
            "sources_checked": sources,
            "blockers_or_zero_results": notes,
            "search_count_before": before.search_count,
            "search_count_after": after.search_count,
            "last_result_count": after.last_result_count,
            "last_error": after.last_error,
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
