from __future__ import annotations

from datetime import datetime, timezone

from dotenv import load_dotenv

from db.database import Database
from models.schema import ExtractedSignal


NOW = datetime.now(timezone.utc)

COMPANY = {
    "keyword_id": 2,
    "name": "Spaceium Inc.",
    "domain": "spaceium.com",
    "url": "https://spaceium.com/",
    "location": "Ottawa, Ontario, Canada",
    "industry": "Autonomous in-space refuelling and spacecraft-servicing systems",
}

EVIDENCE = [
    {
        "source_url": "https://spaceium.com/spaceium-successfully-demonstrates-in-space-refueling-actuator/",
        "source_title": "Spaceium Successfully Demonstrates In-Space Refueling Actuator",
        "source_publisher": "Spaceium",
        "signal_label": "0.003-degree robotic actuator demonstrated in orbit; full refuelling system is next",
        "signal_date": datetime(2026, 2, 10, 12, 0, tzinfo=timezone.utc),
        "challenge_summary": (
            "On February 10, 2026, Spaceium reported that a robotic refuelling actuator "
            "built by its two founders in five months flew on SpaceX's Transporter-15 mission "
            "and achieved verified 0.003-degree rotation accuracy in orbit, which the company "
            "describes as more than 70 times the precision of robotic arms currently operating "
            "in space. Spaceium is now moving from the component demonstration toward full fuel-transfer "
            "missions and a full-scale autonomous refuelling system. Inference: scaling the actuator "
            "into a robotic arm that must grapple spacecraft and transfer cryogenic fuel under vacuum, "
            "radiation, and temperature cycling creates immediate requirements, configuration, interface, "
            "simulation, reliability, safety, and verification-evidence pressure."
        ),
        "why_relevant": (
            "Teamcenter can govern the actuator, arm, cryogenic-fluid, thermal, electrical, and controls "
            "configurations as the prototype becomes a complete system. NX and Simcenter can support "
            "mechanism, structural, thermal, motion, and harsh-environment validation, while Polarion "
            "can trace autonomous docking and fuel-transfer requirements into tests and anomalies. "
            "The opportunity is current because Spaceium has finished an orbital component proof and "
            "is explicitly beginning the scale-up to full refuelling missions."
        ),
        "recommended_products": ["Teamcenter", "NX", "Simcenter", "Polarion"],
        "opportunity_score": 96,
        "manufacturing_fit_score": 98,
        "trigger_score": 97,
        "solution_fit_score": 99,
        "evidence_quality_score": 98,
    },
    {
        "source_url": "https://www.ycombinator.com/companies/spaceium-inc",
        "source_title": "Spaceium Inc: In-Space Refueling",
        "source_publisher": "Y Combinator",
        "signal_label": "$86.1M binding contracts, $230M pipeline, and embedded-software hiring",
        "signal_date": None,
        "challenge_summary": (
            "Spaceium's active Y Combinator profile currently reports $86.1 million in binding "
            "commercial contracts, another $230 million in its pipeline, and $1 billion in letters "
            "of intent for automated stations that refuel and repair spacecraft; it also lists an "
            "Ottawa-based embedded-software engineering role. The system combines a modular robotic "
            "arm, interchangeable repair tooling, zero-boil-off cryogenic storage, closed-loop cooling, "
            "thermal control, and multi-fuel transfer. Inference: contracted delivery expectations and "
            "controls-software hiring increase the urgency of coordinating hardware, embedded software, "
            "customer interfaces, requirements, and verification across a rapidly growing product baseline."
        ),
        "why_relevant": (
            "Teamcenter and Polarion can create a controlled digital thread between customer commitments, "
            "system requirements, multidisciplinary product structures, software versions, and qualification "
            "evidence. Capital can support electrical architecture when the robotic and cryogenic subsystems "
            "expand. The reported contract backlog and active embedded-software hiring make this more than "
            "a directory lead: Spaceium is building delivery capacity while its technical baseline is still evolving."
        ),
        "recommended_products": ["Teamcenter", "Polarion", "Capital"],
        "opportunity_score": 94,
        "manufacturing_fit_score": 98,
        "trigger_score": 96,
        "solution_fit_score": 98,
        "evidence_quality_score": 88,
    },
]

SEARCH_RESULTS = {1: 0, 2: 1, 3: 0, 4: 0}


def main() -> None:
    load_dotenv()
    database = Database()
    database.initialize()
    keywords = {keyword.id: keyword for keyword in database.list_keywords()}

    for evidence in EVIDENCE:
        detected_at = evidence["signal_date"] or NOW
        signal = ExtractedSignal(
            company_name=COMPANY["name"],
            company_domain=COMPANY["domain"],
            company_url=COMPANY["url"],
            location=COMPANY["location"],
            industry=COMPANY["industry"],
            company_industry=COMPANY["industry"],
            software=evidence["recommended_products"],
            signal_type="news",
            signal_source="news",
            pain_signals=[evidence["challenge_summary"]],
            expansion_signals=[evidence["signal_label"]],
            raw_score=evidence["opportunity_score"],
            confidence=evidence["evidence_quality_score"] / 100,
            reason=evidence["why_relevant"],
            source_url=evidence["source_url"],
            source_title=evidence["source_title"],
            detected_at=detected_at,
        )
        saved = database.save_signal(signal)
        database.upsert_company(signal)
        ledger = database.record_keyword_company(
            COMPANY["keyword_id"],
            COMPANY["name"],
            COMPANY["domain"],
            source_url=evidence["source_url"],
            source_title=evidence["source_title"],
            source_publisher=evidence["source_publisher"],
            signal_label=evidence["signal_label"],
            signal_date=evidence["signal_date"],
            challenge_summary=evidence["challenge_summary"],
            why_relevant=evidence["why_relevant"],
            recommended_products=evidence["recommended_products"],
            qualification_status="qualified",
            opportunity_score=evidence["opportunity_score"],
            manufacturing_fit_score=evidence["manufacturing_fit_score"],
            trigger_score=evidence["trigger_score"],
            solution_fit_score=evidence["solution_fit_score"],
            evidence_quality_score=evidence["evidence_quality_score"],
        )
        if ledger is None:
            raise RuntimeError("Could not persist Spaceium qualification evidence")
        print(f"{evidence['source_publisher']}: signal_created={saved.created}")

    for keyword_id, result_count in SEARCH_RESULTS.items():
        database.record_keyword_search(keyword_id, result_count=result_count)
        print(f"{keywords[keyword_id].keyword}: published={result_count}")


if __name__ == "__main__":
    main()
