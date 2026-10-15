from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv

from db.database import Database
from enrichment.identity_verification import CompanyIdentityEvidence
from models.schema import ExtractedSignal


RUN_AT = datetime.now(timezone.utc)
LOCK_PATH = Path(
    r"C:\Users\ranjeet.chaudhary\.codex\automations\daily-keyword-company-research\run.lock"
)


def dt(year: int, month: int, day: int) -> datetime:
    return datetime(year, month, day, tzinfo=timezone.utc)


PROSPECTS = {
    "haply": {
        "company_name": "Haply Robotics",
        "company_domain": "haply.co",
        "company_url": "https://www.haply.co/",
        "location": "Montreal, Quebec, Canada",
        "industry": "Haptic robotics and force-feedback hardware",
        "products": ["Teamcenter", "Opcenter", "Simcenter"],
        "scores": {
            "opportunity": 91,
            "manufacturing": 96,
            "trigger": 88,
            "solution": 94,
            "evidence": 96,
        },
        "pain_signals": [
            "Must control electromechanical product configurations, supplier parts, force-feedback validation and production quality while expanding manufacturing.",
        ],
        "expansion_signals": [
            "Closed US$11.75 million (C$16 million) and said the funds will support expansion, manufacturing and hiring.",
        ],
        "evidence": {
            "signal_date": dt(2026, 2, 9),
            "source_url": "https://betakit.com/haply-robotics-raises-16-million-to-build-the-steering-wheels-for-physical-ai/",
            "source_title": "Haply Robotics raises $16 million to build the 'steering wheels' for physical AI",
            "source_publisher": "BetaKit",
            "signal_label": "C$16M seed-plus round funds manufacturing expansion and hiring",
            "challenge_summary": (
                "On February 9, 2026, BetaKit reported that Haply Robotics closed US$11.75 million (C$16 million), bringing total funding above C$20 million, to expand manufacturing and hiring for its Inverse3, MinVerse and HARP haptic-robotics platform. Haply manufactures at its multi-level Montreal headquarters, had roughly 50 employees and more than 150 customers, including 30 Fortune 500 companies, and planned to strengthen manufacturing while opening a California office. Inference: scaling several precision electromechanical devices and robotics integrations increases product-variant, supplier, BOM, engineering-change, calibration, test and production-traceability pressure."
            ),
            "why_relevant": (
                "Teamcenter can govern released device configurations, supplier parts and engineering changes across the Inverse and HARP product families. Simcenter can support force-feedback, mechanical and controls validation, while Opcenter can preserve assembly, calibration, inspection and serial-level production records as output grows. The funded manufacturing and hiring plan is already underway, so process and product controls need to mature before more customer variants and enterprise deployments are released."
            ),
        },
        "identity": CompanyIdentityEvidence(
            official_name="Haply Robotics",
            official_website_url="https://www.haply.co/",
            corroborating_urls=(
                "https://betakit.com/haply-robotics-raises-16-million-to-build-the-steering-wheels-for-physical-ai/",
            ),
        ),
        "keywords": (2, 8),
    },
    "promise": {
        "company_name": "Promise Robotics",
        "company_domain": "promiserobotics.com",
        "company_url": "https://promiserobotics.com/",
        "location": "Calgary, Alberta, Canada",
        "industry": "Robotic manufacturing systems and industrialized homebuilding",
        "products": ["NX", "Teamcenter", "Tecnomatix"],
        "scores": {
            "opportunity": 89,
            "manufacturing": 97,
            "trigger": 84,
            "solution": 95,
            "evidence": 91,
        },
        "pain_signals": [
            "Must release and validate robotic hardware for multiple industries while synchronizing automated BOMs, manufacturing instructions and factory processes.",
        ],
        "expansion_signals": [
            "Posted a Calgary Senior Mechanical Engineer role on July 29, 2026 to lead core robotic manufacturing technology development.",
        ],
        "evidence": {
            "signal_date": dt(2026, 7, 29),
            "source_url": "https://techjobs.marsdd.com/companies/promise-robotics/jobs/87948373-senior-mechanical-engineer",
            "source_title": "Senior Mechanical Engineer @ Promise Robotics",
            "source_publisher": "MaRS Discovery District Job Board",
            "signal_label": "Hiring mechanical engineering leadership for core robotic manufacturing technologies",
            "challenge_summary": (
                "On July 29, 2026, Promise Robotics posted a Calgary-based Senior Mechanical Engineer role to develop its core robotic manufacturing technologies, covering mechanical design and hardware used in automated off-site homebuilding. Its production platform converts builder designs into manufacturing instructions and coordinates automated bills of materials, procurement, robotic production and installation sequencing. Inference: adding mechanical engineering capacity while scaling factory hardware increases design-release, BOM, configuration, robotic-cell validation and engineering-change workload across machines and customer projects."
            ),
            "why_relevant": (
                "NX can support detailed mechanical design of the robotic production equipment, while Teamcenter can control product structures, released drawings, supplier parts and engineering changes. Tecnomatix can validate robotic cells, manufacturing sequences and throughput before changes reach the factory floor. The active engineering hire makes the opportunity current and upgrades the prior watchlist record from general fit to a concrete product-development trigger."
            ),
        },
        "identity": CompanyIdentityEvidence(
            official_name="Promise Robotics",
            official_website_url="https://promiserobotics.com/",
            corroborating_urls=(
                "https://techjobs.marsdd.com/companies/promise-robotics/jobs/87948373-senior-mechanical-engineer",
            ),
        ),
        "keywords": (2,),
    },
    "connor": {
        "company_name": "Connor Industries Ltd.",
        "company_domain": "stanleyboats.ca",
        "company_url": "https://stanleyboats.ca/",
        "location": "Parry Sound, Ontario, Canada",
        "industry": "Custom welded-aluminum boat manufacturing",
        "products": ["Solid Edge", "Teamcenter", "Opcenter"],
        "scores": {
            "opportunity": 90,
            "manufacturing": 100,
            "trigger": 94,
            "solution": 94,
            "evidence": 99,
        },
        "pain_signals": [
            "Must integrate new production equipment while controlling configurable vessel drawings, BOMs, welding quality and as-built records.",
        ],
        "expansion_signals": [
            "Received C$461,952 for equipment, infrastructure upgrades and new technology at its Parry Sound plant, expanding capacity and hiring.",
        ],
        "evidence": {
            "signal_date": dt(2026, 8, 18),
            "source_url": "https://www.canada.ca/en/fednor/news/2026/08/government-of-canada-investing-over-17-million-to-enhance-economic-development-in-the-parry-sound---muskoka-area.html",
            "source_title": "Government of Canada investing over $1.7 million to enhance economic development in the Parry Sound - Muskoka area",
            "source_publisher": "Federal Economic Development Agency for Northern Ontario",
            "signal_label": "C$461,952 funds watercraft equipment, plant upgrades and hiring",
            "challenge_summary": (
                "On August 18, 2026, FedNor announced a C$461,952 repayable investment for Connor Industries to acquire and install innovative watercraft manufacturing equipment, upgrade infrastructure and implement new technology at its Parry Sound plant, expanding capacity and enabling new hires. Connor builds custom Stanley welded-aluminum boats in a 50,000-square-foot CWB-certified facility with an in-house naval architect and engineering technicians. Inference: equipment integration and higher custom-vessel throughput increase variant, drawing, BOM, supplier, welding-quality, work-order and as-built traceability demands."
            ),
            "why_relevant": (
                "Solid Edge can support configurable hull and outfitting design for this small-to-mid-sized custom builder, while Teamcenter can govern released drawings, vessel options, BOMs and engineering changes. Opcenter can connect work orders, inspections, welding records and as-built genealogy to the correct vessel configuration. The new equipment and infrastructure are being installed now, so Connor has a near-term window to define the digital controls around the expanded production system."
            ),
        },
        "identity": CompanyIdentityEvidence(
            official_name="Connor Industries Ltd.",
            official_website_url="https://stanleyboats.ca/",
            corroborating_urls=(
                "https://www.canada.ca/en/fednor/news/2026/08/government-of-canada-investing-over-17-million-to-enhance-economic-development-in-the-parry-sound---muskoka-area.html",
            ),
        ),
        "keywords": (3,),
    },
    "north_vector": {
        "company_name": "North Vector Dynamics",
        "company_domain": "northvectordynamics.com",
        "company_url": "https://www.northvectordynamics.com/",
        "location": "Calgary, Alberta, Canada",
        "industry": "Precision interception and advanced propulsion systems",
        "products": ["Teamcenter", "Simcenter", "Polarion"],
        "scores": {
            "opportunity": 97,
            "manufacturing": 99,
            "trigger": 96,
            "solution": 98,
            "evidence": 98,
        },
        "pain_signals": [
            "Must coordinate missile and rocket-propulsion configurations, interfaces, simulation and verification evidence across two engineering organizations.",
        ],
        "expansion_signals": [
            "NordSpace made a strategic investment and gave North Vector access to the manufacturing and test infrastructure behind its Hadfield-150 engine.",
        ],
        "evidence": {
            "signal_date": dt(2026, 7, 30),
            "source_url": "https://spaceq.ca/nordspace-ventures-invests-in-north-vector-dynamics-technologies/",
            "source_title": "NordSpace Ventures invests in North Vector Dynamics technologies",
            "source_publisher": "SpaceQ",
            "signal_label": "Strategic investment connects missile programs to rocket-engine manufacturing and test infrastructure",
            "challenge_summary": (
                "On July 30, 2026, SpaceQ reported that NordSpace Ventures made a strategic investment in North Vector Dynamics, pairing NordSpace's orbital-propulsion infrastructure with North Vector's CM-70 interceptor, counter-drone and hypersonic missile programs. North Vector holds a C$4.2-million Defence Research and Development Canada contract for high-speed aeropropulsion and gains access to the manufacturing and testing infrastructure behind NordSpace's Hadfield-150 rocket engine. Inference: pooling teams and hardware programs increases interface, configuration, aerodynamic/propulsion simulation, requirements and test-evidence complexity across sovereign defence products."
            ),
            "why_relevant": (
                "Teamcenter can govern shared product structures, interfaces, released configurations and change control across North Vector and NordSpace. Simcenter can support aerodynamic, propulsion, thermal and structural validation, while Polarion can trace defence requirements through verification results and defects. The investment and infrastructure-sharing agreement are active, making aligned configuration and test governance urgent before joint programs move further into hardware integration."
            ),
        },
        "identity": CompanyIdentityEvidence(
            official_name="North Vector Dynamics",
            official_website_url="https://www.northvectordynamics.com/",
            corroborating_urls=(
                "https://spaceq.ca/nordspace-ventures-invests-in-north-vector-dynamics-technologies/",
            ),
        ),
        "keywords": (8, 9, 14),
    },
    "mda": {
        "company_name": "MDA Space",
        "company_domain": "mda.space",
        "company_url": "https://mda.space/",
        "location": "Montreal, Quebec, Canada",
        "industry": "Satellite manufacturing, space systems and defence engineering",
        "products": ["Teamcenter", "Opcenter", "Polarion", "Tecnomatix"],
        "scores": {
            "opportunity": 99,
            "manufacturing": 100,
            "trigger": 100,
            "solution": 100,
            "evidence": 100,
        },
        "pain_signals": [
            "Must convert a rapidly growing multi-program satellite backlog into high-rate production while controlling configurations, suppliers, requirements, quality and delivery schedules.",
        ],
        "expansion_signals": [
            "Booked C$808.9 million in Q2 orders, lifted backlog to C$4.0 billion and added 27 Lightspeed satellites after quarter-end.",
        ],
        "evidence": {
            "signal_date": dt(2026, 8, 10),
            "source_url": "https://spaceq.ca/mda-space-books-809-million-in-q2/",
            "source_title": "MDA Space books $809 million in Q2 orders",
            "source_publisher": "SpaceQ",
            "signal_label": "C$808.9M Q2 orders and 27 more Lightspeed satellites expand high-rate production load",
            "challenge_summary": (
                "On August 10, 2026, SpaceQ reported that MDA Space booked C$808.9 million in Q2 orders against C$498.6 million of revenue, lifting backlog to C$4.0 billion with a 1.6 book-to-bill ratio. Awards included a C$688-million RADARSAT follow-on satellite, defence payload and antenna work, and—after quarter-end—a C$474-million expansion for 27 additional Telesat Lightspeed satellites, bringing the funded constellation to 225 spacecraft. Inference: simultaneously ramping multiple government and constellation programs increases configuration, supplier, requirements, production-planning, quality and schedule-control pressure at MDA's high-volume Montreal satellite operation."
            ),
            "why_relevant": (
                "Teamcenter can maintain the digital thread and exact satellite, payload and customer configurations across engineering and suppliers. Opcenter and Tecnomatix can support production execution, quality genealogy, line balancing and capacity planning, while Polarion can trace government and defence requirements through verification evidence. The order intake now exceeds deliveries and adds near-term 2027-2028 revenue, so operational systems must absorb the expanded backlog before throughput and variant count rise further."
            ),
        },
        "identity": CompanyIdentityEvidence(
            official_name="MDA Space",
            official_website_url="https://mda.space/",
            corroborating_urls=(
                "https://spaceq.ca/mda-space-books-809-million-in-q2/",
            ),
        ),
        "keywords": (9,),
    },
}


COVERAGE = {
    1: (7, 5, 2, ["Startup Gallery aerospace", "X.com public search", "BetaKit aerospace", "NGen aerospace aircraft manufacturing", "SpaceQ", "AIAC 2026 guide/member directory", "ventureLAB", "CanadaBuys"], "Startup Gallery results were non-Canadian; X.com was inaccessible with ERR_CERT_AUTHORITY_INVALID. AIAC's current guide and member pages were discovery-only; no newly formed Canadian aerospace startup cleared the dated-evidence gate."),
    2: (9, 4, 5, ["Startup Gallery robotics", "X.com public search", "BetaKit robotics manufacturing", "NGen robotics manufacturing", "MaRS", "ventureLAB", "Communitech", "BDC"], "Haply and Promise Robotics produced publishable evidence. TetraGen, A&K Robotics and 4AG were existing duplicates; directory-only or software-led robotics companies were rejected."),
    3: (7, 4, 3, ["Startup Gallery transportation", "X.com public search", "BetaKit shipbuilding", "NGen shipbuilding marine manufacturing", "Canada's Ocean Supercluster", "Shipbuilding Association of Canada", "Marine Log", "Naval News", "FedNor"], "Connor Industries produced a new official funding trigger. Ocean Supercluster results were older or project-level; foreign yards, service firms and non-shipbuilders were rejected."),
    4: (7, 4, 3, ["Startup Gallery transportation", "X.com public search", "BetaKit automotive", "NGen automotive manufacturing", "APMA Project Arrow", "OVIN", "Electric Autonomy Canada", "BDC"], "OVIN program pages generated leads but did not independently verify a vehicle-maker trigger. Hanon remained outside the startup/OEM scope and no new automotive startup passed."),
    5: (8, 5, 3, ["Startup Gallery energy", "X.com public search", "BetaKit energy hardware", "NGen energy manufacturing", "Canada.ca", "BDC", "PLANT", "FedNor"], "Recent infrastructure and process-company results were established operators or outside the saved-keyword product scope. Power Wood remained unpublished because the parent/subsidiary identity and independent corroboration gate did not clear."),
    7: (8, 5, 3, ["Startup Gallery aerospace", "X.com public search", "BetaKit drone", "NGen drone UAV manufacturing", "SpaceQ", "AIAC", "Canadian Space Agency", "Aero Montreal"], "SpaceQ and AIAC were directly checked. Current named manufacturers were existing identities; Startup Gallery candidates were non-Canadian and no new startup identity passed."),
    8: (10, 5, 5, ["Startup Gallery hardware", "X.com public search", "BetaKit hardware manufacturing", "NGen hardware funding", "MaRS", "Communitech", "BDC Capital", "Canada.ca"], "Haply and North Vector were published from verified independent sources. Promise remained linked to robotics rather than a recent funding keyword; software and directory-only leads were rejected."),
    9: (11, 5, 6, ["Startup Gallery aerospace", "X.com public search", "BetaKit aerospace manufacturing", "NGen aerospace engineering", "SpaceQ", "AIAC 2026 industry guide", "DAIR Aerospace", "Aero Montreal", "CanadaBuys"], "MDA Space and North Vector produced new publishable evidence. DAIR and Aero Montreal yielded no dated named trigger; other aerospace identities were duplicates or service-only."),
    10: (8, 5, 3, ["Startup Gallery aerospace", "X.com public search", "BetaKit aerospace suppliers", "NGen precision manufacturing", "SpaceQ", "AIAC member directory", "CanadaBuys", "Canadian Metalworking"], "CanadaBuys surfaced contract amendments, but Pylon was calibration services and Shark Marine lacked enough contract detail to meet the evidence-writing standard. No supplier was published."),
    11: (7, 5, 2, ["Startup Gallery transportation", "X.com public search", "BetaKit vehicle manufacturing", "NGen automotive OEM", "APMA", "OVIN", "Electric Autonomy Canada", "Canada.ca"], "Project Arrow remains a demonstrator rather than an OEM. GM, Honda and Hanon did not meet the Canadian startup/OEM gate, and no new vehicle manufacturer passed."),
    12: (6, 5, 1, ["Startup Gallery hardware", "X.com public search", "BetaKit PLM", "NGen ERP PLM integration", "CME", "PLANT", "manufacturer hiring pages", "Oakville Chamber of Commerce"], "BetaKit PLM results were irrelevant software/news items; NGen results were generic program pages. Oakville Chamber search yielded no dated company-specific ERP/PLM trigger."),
    13: (9, 5, 4, ["Startup Gallery robotics", "X.com public search", "BetaKit autonomous drone", "NGen autonomous vehicle drone", "SpaceQ", "AIAC", "CanadaBuys", "OVIN"], "Calogy, Volatus and other physical-autonomy companies were existing identities. Software and service providers were rejected, and no new company passed."),
    14: (10, 5, 5, ["Startup Gallery aerospace", "X.com public search", "BetaKit defence hardware", "NGen defence manufacturing", "SpaceQ", "AIAC", "CADSI", "CanadaBuys", "BDC StrongNorth"], "North Vector produced new corroborated evidence. Pylon was service-led, Shark Marine's current amendment lacked sufficient scope detail, and directory-only defence leads remained unpublished."),
    15: (8, 5, 3, ["Startup Gallery transportation", "X.com public search", "BetaKit electric vehicle", "NGen electric vehicle manufacturing", "APMA Project Arrow", "OVIN", "Electric Autonomy Canada", "Canada.ca"], "OVIN's current awards were infrastructure or component-technology projects, not verified Canadian EV startups. Existing EV identities were reassessed and no new company passed."),
}


def make_signal(prospect: dict[str, object]) -> ExtractedSignal:
    evidence = prospect["evidence"]
    scores = prospect["scores"]
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
        raw_score=int(scores["opportunity"]),
        confidence=int(scores["evidence"]) / 100,
        reason=str(evidence["challenge_summary"]),
        source_url=str(evidence["source_url"]),
        source_title=str(evidence["source_title"]),
        detected_at=evidence["signal_date"],
    )


def record_link(database: Database, keyword_id: int, prospect: dict[str, object]):
    evidence = prospect["evidence"]
    scores = prospect["scores"]
    row = database.record_keyword_company(
        keyword_id,
        str(prospect["company_name"]),
        str(prospect["company_domain"]),
        source_url=str(evidence["source_url"]),
        source_title=str(evidence["source_title"]),
        source_publisher=str(evidence["source_publisher"]),
        signal_label=str(evidence["signal_label"]),
        signal_date=evidence["signal_date"],
        challenge_summary=str(evidence["challenge_summary"]),
        why_relevant=str(evidence["why_relevant"]),
        recommended_products=list(prospect["products"]),
        qualification_status="qualified",
        opportunity_score=int(scores["opportunity"]),
        manufacturing_fit_score=int(scores["manufacturing"]),
        trigger_score=int(scores["trigger"]),
        solution_fit_score=int(scores["solution"]),
        evidence_quality_score=int(scores["evidence"]),
        seen_at=RUN_AT,
    )
    if row is None:
        raise RuntimeError(f"Could not link {prospect['company_name']} to keyword {keyword_id}")
    return row


def acquire_lock() -> int | None:
    LOCK_PATH.parent.mkdir(parents=True, exist_ok=True)
    try:
        fd = os.open(LOCK_PATH, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError:
        print(json.dumps({"status": "skipped", "reason": "active run marker exists"}))
        return None
    os.write(fd, json.dumps({"pid": os.getpid(), "started_at": RUN_AT.isoformat()}).encode("utf-8"))
    return fd


def main() -> None:
    lock_fd = acquire_lock()
    if lock_fd is None:
        return
    try:
        load_dotenv(".env")
        database = Database()
        database.initialize()
        before = {row.id: row for row in database.list_keywords()}
        if set(before) != set(COVERAGE):
            raise RuntimeError(f"Persistent keyword set changed: {sorted(before)}")

        published = {keyword_id: 0 for keyword_id in before}
        signals = []
        links = []
        for prospect in PROSPECTS.values():
            saved, company = database.persist_verified_signal(
                make_signal(prospect), prospect["identity"]
            )
            signals.append(
                {
                    "company_id": company.id if hasattr(company, "id") else None,
                    "company": company.company_name,
                    "domain": company.company_domain,
                    "source_url": str(prospect["evidence"]["source_url"]),
                    "created": saved.created,
                    "duplicate_url": saved.duplicate_url,
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
                        "domain": row.company_domain,
                    }
                )

        for keyword_id in sorted(before):
            if database.record_keyword_search(
                keyword_id, result_count=published[keyword_id]
            ) is None:
                raise RuntimeError(f"Could not record keyword {keyword_id}")

        after = {row.id: row for row in database.list_keywords()}
        final_rows = database.list_keyword_companies(limit=5000)
        eligible_ids = sorted(
            {
                row.company_id
                for row in final_rows
                if row.qualification_status in {"qualified", "watchlist"}
            }
        )
        report = {}
        for keyword_id, (reviewed, rejected, duplicates, sources, notes) in COVERAGE.items():
            if after[keyword_id].search_count != before[keyword_id].search_count + 1:
                raise RuntimeError(f"Keyword {keyword_id} did not advance exactly once")
            report[keyword_id] = {
                "keyword": before[keyword_id].keyword,
                "lookback": "rolling 30 days, then 180-day fallback; older evidence only where ongoing",
                "candidates_reviewed": reviewed,
                "new_domains_reviewed": 0,
                "rejected_before_persistence": rejected,
                "qualified_published": published[keyword_id],
                "watchlist_published": 0,
                "existing_records_upgraded_or_hidden": 1 if keyword_id == 2 else 0,
                "duplicates_skipped_or_reassessed": duplicates,
                "sources_checked": sources,
                "blockers_or_zero_results": notes,
                "search_count_before": before[keyword_id].search_count,
                "search_count_after": after[keyword_id].search_count,
                "last_result_count": after[keyword_id].last_result_count,
                "last_error": after[keyword_id].last_error,
            }

        print(
            json.dumps(
                {
                    "status": "completed",
                    "run_at": RUN_AT.isoformat(),
                    "signals": signals,
                    "links": links,
                    "new_company_ids": [],
                    "eligible_company_count": len(eligible_ids),
                    "per_keyword": report,
                    "x_com": "inaccessible for every keyword: ERR_CERT_AUTHORITY_INVALID; no warning bypassed",
                },
                indent=2,
                default=str,
            )
        )
    finally:
        os.close(lock_fd)
        LOCK_PATH.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
