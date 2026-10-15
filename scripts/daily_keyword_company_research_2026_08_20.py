from __future__ import annotations

import json
from datetime import datetime, timezone

from dotenv import load_dotenv

from db.database import Database
from models.schema import ExtractedSignal


RUN_AT = datetime.now(timezone.utc)


def dt(year: int, month: int, day: int) -> datetime:
    return datetime(year, month, day, tzinfo=timezone.utc)


GIT = {
    "company_name": "GIT Coatings Inc.",
    "company_domain": "gitcoatings.com",
    "company_url": "https://gitcoatings.com/",
    "location": "Dartmouth, Nova Scotia, Canada",
    "industry": "Graphene-based marine coating development and manufacturing",
    "products": ["Teamcenter", "Opcenter", "Polarion"],
    "scores": {"opportunity": 88, "manufacturing": 96, "trigger": 95, "solution": 91, "evidence": 98},
    "pain_signals": [
        "Must industrialize a new icebreaking hull coating while controlling formulations, raw-material lots, batch recipes, inspections and customer-specific release evidence.",
        "Must keep production records and Lloyd's Register or IMO compliance evidence aligned as the XGIT product family expands across commercial and defence fleets.",
    ],
    "expansion_signals": [
        "Received a C$737,500 repayable federal contribution to buy and install a production mixer for a new icebreaking hull coating.",
        "Launched XGIT-FORCE in February 2026, obtained Lloyd's Register type approval in March, and began deployment across more than ten vessels after experience on 600-plus vessels.",
    ],
    "evidence": [
        {
            "signal_date": dt(2026, 7, 29),
            "source_url": "https://www.canada.ca/en/atlantic-canada-opportunities/news/2026/07/git-coatings-to-expand-production-with-federal-investment-in-canadas-defence-sector.html",
            "source_title": "GIT Coatings to expand production with federal investment in Canada's defence sector",
            "source_publisher": "Atlantic Canada Opportunities Agency",
            "signal_label": "C$737,500 funds production mixer for a new icebreaking hull coating",
            "challenge_summary": (
                "On July 29, 2026, ACOA announced a C$737,500 repayable contribution for Dartmouth-based GIT Coatings to purchase and install a new production mixer for its latest icebreaking hull coating for defence and security vessels. The equipment moves a new graphene-based formulation into expanded domestic production as Canada rebuilds marine and defence supply capacity. Inference: a larger batch process for a new regulated product creates immediate formulation-version, raw-material lot, recipe, in-process inspection, finished-batch release and customer traceability pressure."
            ),
            "why_relevant": (
                "Teamcenter can govern released coating formulations, specifications and engineering changes, while Opcenter can execute mixer recipes and preserve batch, material and quality genealogy. Polarion is justified narrowly for linking defence, environmental and classification requirements to test and approval evidence. The mixer is being purchased and installed now, so the digital controls should be defined before production volume and customer qualification work increase."
            ),
        },
        {
            "signal_date": dt(2026, 3, 12),
            "source_url": "https://www.lr.org/en/knowledge/press-room/press-listing/press-release/2026/lloyds-register-grants-approval-for-git-coatings-next-generation-graphene-based-hull-coating/",
            "source_title": "LR grants approval for GIT Coatings' next generation graphene-based hull coating",
            "source_publisher": "Lloyd's Register",
            "signal_label": "Lloyd's Register type approval confirms IMO anti-fouling compliance for XGIT-FORCE",
            "challenge_summary": (
                "On March 12, 2026, Lloyd's Register granted type approval and technical assurance to GIT Coatings' XGIT-FORCE graphene-based hull coating, confirming assessment against applicable technical requirements and compliance with the International Maritime Organization anti-fouling convention. Commercializing a newly approved formulation requires GIT to keep the certified design basis, production batches, inspection results and later in-service changes traceable to the approved configuration. Inference: expanding use without weakening the approval basis creates controlled-change and verification-evidence work that must remain synchronized with manufacturing."
            ),
            "why_relevant": (
                "Polarion can connect classification and regulatory requirements to validation results, deviations and approval evidence, while Teamcenter can keep the approved formulation and controlled product revisions aligned with manufacturing releases. Opcenter can preserve which recipe, materials and inspections produced each delivered batch. Approval has moved the product from development into a commercial scale-up window, making controlled release and compliance traceability urgent before broader fleet adoption."
            ),
        },
        {
            "signal_date": dt(2026, 2, 24),
            "source_url": "https://gitcoatings.com/news/x-git-force_launch/",
            "source_title": "GIT Coatings Unlocks a New Era of Hull Performance Management with the Launch of XGIT-FORCE",
            "source_publisher": "GIT Coatings",
            "signal_label": "XGIT-FORCE launch begins rollout to 10+ vessels after 600+ vessel applications",
            "challenge_summary": (
                "On February 24, 2026, GIT Coatings launched XGIT-FORCE, reporting first applications underway and plans to coat more than ten LPG, dry-bulk, Ro-Ro, container and cruise vessels over the following months after learning from applications across more than 600 vessels. The product is promoted with a guaranteed 6% out-of-dock power gain and up to 10% fuel savings while tolerating ice friction, impacts and repeated cleaning. Inference: a multi-segment rollout of a performance-guaranteed coating increases variant, vessel-specific application, test-result, batch-quality and field-feedback complexity."
            ),
            "why_relevant": (
                "Teamcenter can control the XGIT product family, vessel-specific specifications and approved change history; Opcenter can provide repeatable recipe execution and batch genealogy as order mix grows. Polarion can tie performance and durability requirements to laboratory, approval and in-service evidence where customer guarantees must be defended. The first multi-vessel rollout is already underway, so GIT needs consistent product and production evidence before adoption expands further."
            ),
        },
    ],
}


DOMINION = {
    "company_name": "Dominion Dynamics",
    "company_domain": "defendthedominion.com",
    "company_url": "https://www.defendthedominion.com/",
    "location": "Ottawa, Ontario, Canada",
    "industry": "Defence systems and autonomous aircraft",
    "products": ["Teamcenter", "Polarion", "Simcenter"],
    "scores": {"opportunity": 97, "manufacturing": 97, "trigger": 100, "solution": 98, "evidence": 98},
    "pain_signals": [
        "Must scale Scout autonomous aircraft and Arctic sensing, communications and command systems from a new Kanata manufacturing facility while expanding engineering and international operations.",
    ],
    "expansion_signals": [
        "Closed a C$139 million Series A and moved into a 25,000-square-foot Kanata manufacturing facility in June 2026.",
    ],
    "evidence": {
        "signal_date": dt(2026, 6, 30),
        "source_url": "https://www.prnewswire.com/news-releases/dominion-dynamics-raises-139m-cad-series-a-to-scale-arctic-surveillance-network-and-drone-systems-302813965.html",
        "source_title": "Dominion Dynamics raises $139M CAD Series A to scale Arctic surveillance network and drone systems",
        "source_publisher": "Dominion Dynamics / PR Newswire",
        "signal_label": "C$139M Series A supports new 25,000-square-foot Kanata manufacturing facility",
        "challenge_summary": (
            "On June 30, 2026, Dominion Dynamics announced a C$139 million Series A, moved into a 25,000-square-foot manufacturing facility in Kanata and opened a Toronto development office to scale its Scout autonomous collaborative aircraft and AuraNet Arctic surveillance network. The company plans to grow beyond 100 employees while expanding into allied markets, increasing the number of hardware, electronics, software and mission configurations that engineering and production must release and verify. Inference: this ramp creates immediate configuration, defence-requirement, supplier, multidisciplinary simulation, test-evidence and production-control pressure."
        ),
        "why_relevant": (
            "Teamcenter can govern aircraft, sensor, electronics and software configurations across engineering, suppliers and manufacturing. Polarion can trace mission and safety requirements through verification, while Simcenter can support flight, thermal, structural and systems validation before expensive hardware tests. The factory, hiring plan and funded product ramp are active now, so shared development and release controls need to be established before programs and allied deployments multiply."
        ),
    },
}


COVERAGE = {
    1: (5, 1, 4, ["Startup Gallery", "X.com public/X-ray", "BetaKit", "NGen", "SpaceQ", "AIAC", "ventureLAB HCI", "CanadaBuys"], "Avro was directory-only; Dominion, Wyvern, Canada Rocket Company and Sentinel were existing identities. Startup Gallery and public X/X-ray surfaced no new qualifying company."),
    2: (5, 1, 4, ["Startup Gallery", "X.com public/X-ray", "BetaKit", "NGen", "ventureLAB HCI", "MaRS", "Communitech", "CanadaBuys"], "Laplace Robotics remained an NGen discovery lead without a corroborated dated scale trigger; four results were existing robotics companies."),
    3: (5, 2, 3, ["Startup Gallery", "X.com public/X-ray", "BetaKit", "NGen", "Canada's Ocean Supercluster", "Naval News", "CanadaBuys", "Marine Log"], "GIT Coatings and ASDAC are marine or aerospace suppliers, not shipbuilders; three shipyard identities were duplicates."),
    4: (4, 2, 2, ["Startup Gallery", "X.com public/X-ray", "BetaKit", "NGen EVMP", "APMA", "OVIN", "Electric Autonomy Canada", "BDC"], "Hanon Systems is an established foreign-owned component supplier rather than a Canadian automotive startup; ecosystem-only leads were not published."),
    5: (4, 2, 2, ["Startup Gallery", "X.com public/X-ray", "BetaKit", "NGen", "Canada.ca/ISED", "FedDev Ontario", "BDC Climate Tech", "PLANT"], "GIT Coatings is not an energy company, and directory-only energy technology suppliers lacked a qualifying trigger; existing Volta and Tempel records were reassessed."),
    7: (6, 1, 5, ["Startup Gallery", "X.com public/X-ray", "BetaKit", "NGen", "SpaceQ", "AIAC", "ventureLAB HCI", "Canadian Space Agency"], "Avro remained directory-only; five aerospace, launch or drone identities were already known."),
    8: (6, 2, 3, ["Startup Gallery", "X.com public/X-ray", "BetaKit", "NGen", "BDC Capital", "MaRS", "Communitech", "FedDev Ontario"], "GIT Coatings qualified on a dated federal production investment; SproutCo and Calogy were discovery-only or lacked a new corroborated trigger."),
    9: (6, 1, 5, ["Startup Gallery", "X.com public/X-ray", "BetaKit", "NGen", "SpaceQ", "AIAC Industry Guide", "CanadaBuys", "ACOA"], "ASDAC remained a self-submitted CanadaBuys discovery profile; five aerospace operators or manufacturers were duplicates."),
    10: (6, 2, 4, ["Startup Gallery", "X.com public/X-ray", "BetaKit", "NGen", "SpaceQ", "AIAC Member Directory", "CanadaBuys", "Canadian Metalworking"], "ASDAC and ProtoSpace profiles lacked an independently corroborated current buying trigger; four suppliers were existing identities."),
    11: (4, 2, 2, ["Startup Gallery", "X.com public/X-ray", "BetaKit", "NGen", "APMA", "OVIN", "Electric Autonomy Canada", "Canada.ca/ISED"], "Hanon Systems manufactures EV compressors but is neither a vehicle OEM nor a Canadian OEM; no new OEM passed the gate."),
    12: (4, 3, 1, ["Startup Gallery", "X.com public/X-ray", "BetaKit", "NGen digital-twin case studies", "CME", "PLANT", "manufacturer hiring pages", "CanadaBuys"], "The NGen CenterLine case was older ongoing context, while software vendors and consultants were excluded. No dated company-specific ERP/PLM integration trigger cleared the gate."),
    13: (6, 2, 4, ["Startup Gallery", "X.com public/X-ray", "BetaKit", "NGen", "SpaceQ", "AIAC", "BDC StrongNorth", "CanadaBuys"], "OSCP and Avro were discovery-only; four autonomous aircraft, drone or robotics identities were duplicates."),
    14: (5, 2, 1, ["Startup Gallery", "X.com public/X-ray", "BetaKit", "NGen", "SpaceQ", "CADSI", "CanadaBuys", "Canada.ca/ACOA"], "GIT Coatings qualified on a defence-production expansion and Dominion Dynamics was newly linked from existing C$139M/factory evidence. ASDAC and OSCP remained directory-only."),
    15: (4, 2, 2, ["Startup Gallery", "X.com public/X-ray", "BetaKit", "NGen EVMP", "APMA Project Arrow", "OVIN", "Electric Autonomy Canada", "Canada.ca/ISED"], "Hanon Systems is not a startup and SproutCo was directory-only; Enedym and other matching companies were existing identities."),
}


def make_signal(company: dict[str, object], evidence: dict[str, object]) -> ExtractedSignal:
    scores = company["scores"]
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
        pain_signals=list(company["pain_signals"]),
        expansion_signals=list(company["expansion_signals"]),
        raw_score=int(scores["opportunity"]),
        confidence=int(scores["evidence"]) / 100,
        reason=str(evidence["challenge_summary"]),
        source_url=str(evidence["source_url"]),
        source_title=str(evidence["source_title"]),
        detected_at=evidence["signal_date"],
    )


def record_link(database: Database, keyword_id: int, company: dict[str, object], evidence: dict[str, object]):
    scores = company["scores"]
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
        opportunity_score=int(scores["opportunity"]),
        manufacturing_fit_score=int(scores["manufacturing"]),
        trigger_score=int(scores["trigger"]),
        solution_fit_score=int(scores["solution"]),
        evidence_quality_score=int(scores["evidence"]),
        seen_at=RUN_AT,
    )
    if row is None:
        raise RuntimeError(f"Could not link {company['company_name']} to keyword {keyword_id}")
    return row


def main() -> None:
    load_dotenv(".env")
    database = Database()
    database.initialize()
    before = {row.id: row for row in database.list_keywords()}
    if set(before) != set(COVERAGE):
        raise RuntimeError(f"Persistent keyword set changed: {sorted(before)}")

    signals = []
    git_company = None
    for evidence in GIT["evidence"]:
        saved, git_company = database.persist_signal(make_signal(GIT, evidence))
        signals.append({"company": GIT["company_name"], "source_url": evidence["source_url"], "created": saved.created, "duplicate_url": saved.duplicate_url, "signal_count": git_company.signal_count})

    dominion_evidence = DOMINION["evidence"]
    saved, dominion_company = database.persist_signal(make_signal(DOMINION, dominion_evidence))
    signals.append({"company": DOMINION["company_name"], "source_url": dominion_evidence["source_url"], "created": saved.created, "duplicate_url": saved.duplicate_url, "signal_count": dominion_company.signal_count})

    published = {keyword_id: 0 for keyword_id in before}
    links = []
    for keyword_id in (8, 14):
        row = record_link(database, keyword_id, GIT, GIT["evidence"][0])
        published[keyword_id] += 1
        links.append({"keyword_id": keyword_id, "company_id": row.company_id, "company": row.company_name, "domain": row.company_domain})
    row = record_link(database, 14, DOMINION, dominion_evidence)
    published[14] += 1
    links.append({"keyword_id": 14, "company_id": row.company_id, "company": row.company_name, "domain": row.company_domain})

    for keyword_id in before:
        if database.record_keyword_search(keyword_id, result_count=published[keyword_id]) is None:
            raise RuntimeError(f"Could not record keyword {keyword_id}")

    after = {row.id: row for row in database.list_keywords()}
    final_rows = database.list_keyword_companies(limit=5000)
    eligible_ids = sorted({row.company_id for row in final_rows if row.qualification_status in {"qualified", "watchlist"}})
    report = {}
    for keyword_id, (reviewed, rejected, duplicates, sources, notes) in COVERAGE.items():
        if after[keyword_id].search_count != before[keyword_id].search_count + 1:
            raise RuntimeError(f"Keyword {keyword_id} did not advance exactly once")
        report[keyword_id] = {
            "keyword": before[keyword_id].keyword,
            "lookback": "rolling 30 days, then 180-day fallback",
            "candidates_reviewed": reviewed,
            "new_domains_reviewed": 1 if keyword_id in {8, 14} else 0,
            "rejected_before_persistence": rejected,
            "qualified_published": published[keyword_id],
            "watchlist_published": 0,
            "existing_records_upgraded_or_hidden": 0,
            "duplicates_skipped_or_reassessed": duplicates,
            "sources_checked": sources,
            "blockers_or_zero_results": notes,
            "search_count_before": before[keyword_id].search_count,
            "search_count_after": after[keyword_id].search_count,
            "last_result_count": after[keyword_id].last_result_count,
            "last_error": after[keyword_id].last_error,
        }

    print(json.dumps({
        "run_at": RUN_AT.isoformat(),
        "signals": signals,
        "links": links,
        "new_company_id": links[0]["company_id"] if links else None,
        "eligible_company_count": len(eligible_ids),
        "per_keyword": report,
        "in_app_browser": "blocked: trusted browser-service dependency could not resolve; focused source-specific web search was used and no barrier was bypassed",
    }, indent=2, default=str))


if __name__ == "__main__":
    main()
