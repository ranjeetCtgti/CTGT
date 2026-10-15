from __future__ import annotations

from datetime import datetime, timezone

from dotenv import load_dotenv

from db.database import Database
from models.schema import ExtractedSignal


SEEN_AT = datetime.now(timezone.utc)
SIGNAL_DATE = datetime(2026, 8, 4, tzinfo=timezone.utc)


def publish(
    database: Database,
    *,
    keyword_id: int,
    signal: ExtractedSignal,
    source_publisher: str,
    signal_label: str,
    challenge_summary: str,
    why_relevant: str,
    recommended_products: list[str],
    opportunity_score: int,
    manufacturing_fit_score: int,
    trigger_score: int,
    solution_fit_score: int,
    evidence_quality_score: int,
) -> tuple[int, bool]:
    saved = database.save_signal(signal)
    database.upsert_company(signal)
    linked = database.record_keyword_company(
        keyword_id,
        signal.company_name,
        signal.company_domain,
        source_url=str(signal.source_url),
        source_title=signal.source_title,
        source_publisher=source_publisher,
        signal_label=signal_label,
        signal_date=SIGNAL_DATE,
        challenge_summary=challenge_summary,
        why_relevant=why_relevant,
        recommended_products=recommended_products,
        qualification_status="qualified",
        opportunity_score=opportunity_score,
        manufacturing_fit_score=manufacturing_fit_score,
        trigger_score=trigger_score,
        solution_fit_score=solution_fit_score,
        evidence_quality_score=evidence_quality_score,
        seen_at=SEEN_AT,
    )
    if linked is None:
        raise RuntimeError(f"Could not link {signal.company_name} to keyword {keyword_id}")
    return linked.company_id, saved.created


def main() -> None:
    load_dotenv(".env")
    database = Database()
    database.initialize()
    keywords = {item.id: item for item in database.list_keywords()}
    if set(keywords) != {1, 2, 3, 4}:
        raise RuntimeError(f"Unexpected keyword ids: {sorted(keywords)}")

    telesat_challenge = (
        "On August 4, 2026, Telesat signed the largest contract in its history: an initial approximately $2.3 billion, 15-year Defence Investment Agency award for secure Military Ka-band Arctic service, with two option periods taking potential value to $2.7 billion. The award immediately expands Lightspeed from 156 to 225 fully funded satellites, requires Telesat to integrate satellites, user terminals, ground and control infrastructure, training, and support, and adds Mil-Ka capability for service beginning in 2028; Telesat says total network investment will reach about $7 billion. Inference: a 44% constellation expansion plus defence-grade interoperability creates immediate requirements, configuration, interface, verification, supplier, and program-baseline pressure across space and ground segments."
    )
    telesat_relevance = (
        "Teamcenter can govern the 225-satellite constellation baseline, ground-segment configurations, supplier deliverables, and engineering changes across the 15-year program. Polarion can connect Canadian Armed Forces and allied operational requirements to Mil-Ka verification and acceptance evidence, while Capital can support electrical and communications architecture across satellite, terminal, and control-system interfaces. Milestone payments begin in Q3 2026 and global service remains targeted for Q1 2028, so the digital-thread and compliance decisions are urgent now."
    )
    telesat_signal = ExtractedSignal(
        company_name="Telesat",
        company_domain="telesat.com",
        company_url="https://www.telesat.com/",
        linkedin_url="https://www.linkedin.com/company/telesat.com/",
        location="Ottawa, Ontario, Canada",
        industry="Satellite communications and defence constellation operations",
        company_industry="LEO satellite constellation engineering and systems integration",
        software=[],
        signal_type="news",
        signal_source="news",
        pain_signals=[
            "Must expand and control a mixed commercial and Military Ka-band constellation from 156 to 225 satellites.",
            "Must integrate satellites, user terminals, ground and control infrastructure, training, and support under defence requirements.",
            "Must maintain configuration and verification evidence for allied interoperability across a 15-year service program.",
        ],
        expansion_signals=[
            "Signed an initial approximately $2.3 billion Defence Investment Agency contract, with options bringing potential value to $2.7 billion.",
            "The contract fully funds 69 additional satellites and milestone payments begin in Q3 2026.",
        ],
        raw_score=93,
        confidence=0.97,
        reason=telesat_challenge,
        source_url="https://www.telesat.com/press/press-releases/telesat-secures-2-3-billion-arctic-military-satcom-contract-expanding-telesat-lightspeed-network-and-capacity-by-44/",
        source_title="Telesat secures $2.3 billion Arctic military satcom contract, expanding Telesat Lightspeed network and capacity by 44%",
        detected_at=SIGNAL_DATE,
    )
    telesat_id, telesat_created = publish(
        database,
        keyword_id=1,
        signal=telesat_signal,
        source_publisher="Telesat",
        signal_label="$2.3B Arctic defence contract expands Lightspeed to 225 satellites",
        challenge_summary=telesat_challenge,
        why_relevant=telesat_relevance,
        recommended_products=["Teamcenter", "Polarion", "Capital"],
        opportunity_score=93,
        manufacturing_fit_score=88,
        trigger_score=98,
        solution_fit_score=95,
        evidence_quality_score=97,
    )

    mda_challenge = (
        "On August 4, 2026, MDA Space received a $474 million follow-on order tied to Telesat's expansion of Lightspeed to 225 fully funded satellites. MDA must add 27 MDA AURORA satellites to its prior 198-unit build, retrofit the full production set with 500 MHz of Military Ka-band capability, manage long-lead items, and manufacture, test, and deliver the spacecraft through its high-volume Montréal facility; MDA is also the prime contractor for the program's planned UHF and X-band constellation. Inference: the added variants, defence spectrum, long-lead procurement, high-rate production, and end-to-end mission responsibility increase BOM, configuration, supplier, test, quality, and production-schedule complexity immediately."
    )
    mda_relevance = (
        "Teamcenter can control AURORA configurations, defence/commercial variants, approved long-lead suppliers, and engineering changes across the 225-satellite program. Opcenter can provide unit-level production genealogy, inspection and nonconformance control at the Montréal factory; Polarion can link Mil-Ka, UHF, and X-band requirements to verification evidence, while Capital supports communications and electrical architecture changes. Most of the $474 million increase enters backlog in Q3 2026, creating a current production-planning and configuration-control trigger."
    )
    mda_signal = ExtractedSignal(
        company_name="MDA Space",
        company_domain="mda.space",
        company_url="https://mda.space/",
        linkedin_url="https://www.linkedin.com/company/mdaspace/",
        location="Montreal, Quebec, Canada",
        industry="Satellite manufacturing, space systems, and defence engineering",
        company_industry="High-volume satellite manufacturing and space systems",
        software=[],
        signal_type="news",
        signal_source="news",
        pain_signals=[
            "Must add 27 satellites and Military Ka-band changes to an already high-volume production program.",
            "Must control long-lead procurement, unit genealogy, test evidence, and defence/commercial configurations.",
            "Must prepare for prime-contractor responsibility across UHF and X-band mission definition and delivery.",
        ],
        expansion_signals=[
            "Received a $474 million follow-on order for the expanded Telesat Lightspeed constellation.",
            "Will manufacture and test the expanded satellite set at its high-volume Montreal facility.",
        ],
        raw_score=97,
        confidence=0.98,
        reason=mda_challenge,
        source_url="https://www.prnewswire.com/news-releases/mda-space-awarded-474-million-to-expand-the-telesat-lightspeed-leo-constellation-302841785.html",
        source_title="MDA Space awarded $474 million to expand the Telesat Lightspeed LEO constellation",
        detected_at=SIGNAL_DATE,
    )
    mda_id, mda_created = publish(
        database,
        keyword_id=1,
        signal=mda_signal,
        source_publisher="MDA Space / PR Newswire",
        signal_label="$474M order adds satellites and Military Ka-band production changes",
        challenge_summary=mda_challenge,
        why_relevant=mda_relevance,
        recommended_products=["Teamcenter", "Opcenter", "Polarion", "Capital"],
        opportunity_score=97,
        manufacturing_fit_score=100,
        trigger_score=98,
        solution_fit_score=98,
        evidence_quality_score=98,
    )

    # Volta Energy Solutions Canada was rediscovered in the automotive source rotation.
    refreshed = database.record_keyword_company(
        4,
        "Volta Energy Solutions Canada Inc.",
        "volta-energysolutions.com",
        source_url="https://www.canada.ca/en/innovation-science-economic-development/news/2026/07/government-of-canada-invests-70-million-to-strengthen-the-ev-battery-supply-chain-in-quebec.html",
        seen_at=SEEN_AT,
    )
    if refreshed is None:
        raise RuntimeError("Could not refresh Volta Energy Solutions Canada")

    for keyword_id, result_count in {1: 2, 2: 0, 3: 0, 4: 1}.items():
        database.record_keyword_search(keyword_id, result_count=result_count)

    print(
        f"Telesat company_id={telesat_id} signal_created={telesat_created}; "
        f"MDA Space company_id={mda_id} signal_created={mda_created}"
    )
    print("Search counts recorded: aerospace=2 robotics=0 shipbuilding=0 automotive=1")


if __name__ == "__main__":
    main()
