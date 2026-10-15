from __future__ import annotations

from datetime import datetime, timezone

from dotenv import load_dotenv

from db.database import Database
from models.schema import ExtractedSignal


SEEN_AT = datetime.now(timezone.utc)


def save_qualified_company(
    database: Database,
    *,
    keyword_id: int,
    signal: ExtractedSignal,
    source_title: str,
    source_publisher: str,
    signal_label: str,
    signal_date: datetime,
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
        source_title=source_title,
        source_publisher=source_publisher,
        signal_label=signal_label,
        signal_date=signal_date,
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

    csmc_date = datetime(2026, 7, 23, tzinfo=timezone.utc)
    csmc_challenge = (
        "On July 23, 2026, SpaceQ reported that Canadian Strategic Missions Corporation received a $4.5 million FedDev Ontario investment to take its Arctic microreactor through detailed design and a fuelled demonstration; the company is targeting fleet-scale deployment by 2030 and has an MOU with Telesat for secure remote monitoring over Lightspeed. This moves the system from concept into a physical nuclear demonstration while coordinating reactor design, fuelled-test evidence, remote operations, defence requirements, suppliers, and a regulated product baseline. Inference: the compressed commercialization timeline creates immediate configuration-control, simulation, requirements-traceability, and verification pressure before the design is frozen for demonstration."
    )
    csmc_relevance = (
        "Teamcenter can govern reactor configurations, bills of material, engineering changes, and supplier-controlled design data; Polarion can connect defence, safety, remote-operation, and test requirements to verification evidence. NX and Simcenter fit detailed mechanical design and the thermal, structural, and multiphysics validation needed before a fuelled demonstration. The new federal funding and stated 2030 fleet target make these engineering-system decisions current rather than speculative."
    )
    csmc_signal = ExtractedSignal(
        company_name="Canadian Strategic Missions Corporation",
        company_domain="strategicmissions.ca",
        company_url="https://strategicmissions.ca/",
        linkedin_url="https://ca.linkedin.com/company/strategicmissions",
        location="Waterloo, Ontario, Canada",
        industry="Space, defence, and nuclear microreactor engineering",
        company_industry="Dual-use Arctic nuclear microreactor development",
        software=[],
        signal_type="news",
        signal_source="news",
        pain_signals=[
            "Must control a regulated reactor design baseline through detailed design and a fuelled demonstration.",
            "Must trace defence, safety, remote-operation, and verification requirements across a multi-year fleet-scale deployment plan.",
            "Must coordinate mechanical, thermal, structural, fuel, supplier, and secure-connectivity interfaces.",
        ],
        expansion_signals=[
            "Received $4.5 million from FedDev Ontario for detailed design and a fuelled microreactor demonstration.",
            "Targets fleet-scale Arctic deployment by 2030 and has a Telesat connectivity MOU for remote monitoring.",
        ],
        raw_score=93,
        confidence=0.95,
        reason=csmc_challenge,
        source_url="https://spaceq.ca/csmc-secures-4-5-million-federal-investment-for-arctic-microreactor-development/",
        source_title="CSMC secures $4.5 million federal investment for Arctic microreactor development",
        detected_at=csmc_date,
    )
    csmc_company_id, csmc_created = save_qualified_company(
        database,
        keyword_id=1,
        signal=csmc_signal,
        source_title=csmc_signal.source_title or "",
        source_publisher="SpaceQ",
        signal_label="$4.5M Arctic microreactor detailed-design and fuelled-demonstration program",
        signal_date=csmc_date,
        challenge_summary=csmc_challenge,
        why_relevant=csmc_relevance,
        recommended_products=["Teamcenter", "Polarion", "NX", "Simcenter"],
        opportunity_score=93,
        manufacturing_fit_score=96,
        trigger_score=96,
        solution_fit_score=94,
        evidence_quality_score=94,
    )

    # Preserve the company's own dated announcement as independent primary evidence.
    csmc_primary = csmc_signal.model_copy(
        update={
            "source_url": "https://www.newswire.ca/news-releases/canadian-strategic-missions-corporation-awarded-4-5-million-through-the-government-of-canada-to-accelerate-micro-nuclear-technology-for-canada-s-arctic-843485403.html",
            "source_title": "Canadian Strategic Missions Corporation awarded $4.5 million through the Government of Canada to accelerate micro-nuclear technology for Canada's Arctic",
        }
    )
    database.save_signal(csmc_primary)
    database.upsert_company(csmc_primary)

    marmen_date = datetime(2026, 7, 7, tzinfo=timezone.utc)
    marmen_challenge = (
        "On July 7, 2026, Canadian Defence Review reported that Marmen became a strategic Canadian manufacturing partner after TKMS was selected as preferred supplier for Canada's Patrol Submarine Project. Subject to final negotiations, Marmen will produce structural subassemblies for the 212CD submarine, including complex machining and assembly to TKMS technical specifications, quality standards, and delivery schedules, and it intends to establish a North American submarine-component centre of excellence. The program adds long-lived defence configuration, sovereign supply-chain, quality, machining, assembly, and delivery-control demands across a platform whose workshare will be finalized over the coming year. Inference: Marmen must prepare its digital product and production backbone before detailed work packages and capital commitments are locked."
    )
    marmen_relevance = (
        "NX and Simcenter can support manufacturability, tooling, machining, structural validation, and production engineering for complex submarine sections. Teamcenter can control TKMS specifications, workshare configurations, bills of material, engineering changes, and approved supplier data, while Opcenter can maintain shop-floor genealogy, inspection records, nonconformance handling, and schedule visibility. Preferred-supplier selection has started the negotiation and capacity-planning window now, ahead of final scope confirmation."
    )
    marmen_signal = ExtractedSignal(
        company_name="Marmen",
        company_domain="marmeninc.com",
        company_url="https://marmeninc.com/en",
        linkedin_url=None,
        location="Trois-Rivieres, Quebec, Canada",
        industry="Defence, aerospace, and high-precision manufacturing",
        company_industry="Submarine structural assemblies and high-precision fabrication",
        software=[],
        signal_type="news",
        signal_source="news",
        pain_signals=[
            "Must manufacture complex 212CD structural subassemblies to TKMS technical, quality, and delivery requirements.",
            "Must prepare machining, assembly, inspection, and capacity systems while final workshare is negotiated.",
            "Must maintain defence-program configuration and build traceability across a sovereign Canadian supply chain.",
        ],
        expansion_signals=[
            "Selected as a strategic Canadian manufacturing partner for the Canadian Patrol Submarine Project.",
            "Plans a North American centre of excellence for submarine-component manufacturing.",
        ],
        raw_score=88,
        confidence=0.94,
        reason=marmen_challenge,
        source_url="https://canadiandefencereview.com/marmen-welcomes-tkms-selection-as-preferred-supplier-for-cpsp/",
        source_title="MARMEN Welcomes TKMS Selection as Preferred Supplier for CPSP",
        detected_at=marmen_date,
    )
    marmen_company_id, marmen_created = save_qualified_company(
        database,
        keyword_id=3,
        signal=marmen_signal,
        source_title=marmen_signal.source_title or "",
        source_publisher="Canadian Defence Review",
        signal_label="212CD submarine structural-subassembly manufacturing workshare",
        signal_date=marmen_date,
        challenge_summary=marmen_challenge,
        why_relevant=marmen_relevance,
        recommended_products=["NX", "Teamcenter", "Simcenter", "Opcenter"],
        opportunity_score=88,
        manufacturing_fit_score=99,
        trigger_score=90,
        solution_fit_score=92,
        evidence_quality_score=93,
    )

    marmen_primary = marmen_signal.model_copy(
        update={
            "source_url": "https://www.tkmsgroup.com/news/article/tkms-and-marmen-sign-strategic-teaming-agreement-to-support-production-of-212cd-submarine-segments-in-canada",
            "source_title": "TKMS and Marmen sign strategic Teaming Agreement to support production of 212CD submarine segments in Canada",
            "detected_at": datetime(2025, 12, 18, tzinfo=timezone.utc),
        }
    )
    database.save_signal(marmen_primary)
    database.upsert_company(marmen_primary)

    # Existing qualified candidates rediscovered in this pass: refresh the ledger only.
    existing_links = [
        (1, "Maritime Launch Services", "maritimelaunch.com", "https://www.maritimelaunch.com/news/sovereign-space-access-for-Germany-and-Canada-july-2026"),
        (2, "4AG Robotics", "4ag.ai", "https://4ag.ai/4ag-robotics-raises-40m-series-b-to-power-the-future-of-autonomous-mushroom-farming/"),
        (4, "Volta Energy Solutions Canada Inc.", "volta-energysolutions.com", "https://www.canada.ca/en/innovation-science-economic-development/news/2026/07/government-of-canada-invests-70-million-to-strengthen-the-ev-battery-supply-chain-in-quebec.html"),
    ]
    for keyword_id, company_name, company_domain, source_url in existing_links:
        linked = database.record_keyword_company(
            keyword_id,
            company_name,
            company_domain,
            source_url=source_url,
            seen_at=SEEN_AT,
        )
        if linked is None:
            raise RuntimeError(f"Could not refresh {company_name}")

    for keyword_id, result_count in {1: 2, 2: 1, 3: 1, 4: 1}.items():
        database.record_keyword_search(keyword_id, result_count=result_count)

    print(
        f"CSMC company_id={csmc_company_id} signal_created={csmc_created}; "
        f"Marmen company_id={marmen_company_id} signal_created={marmen_created}"
    )
    print("Search counts recorded: aerospace=2 robotics=1 shipbuilding=1 automotive=1")


if __name__ == "__main__":
    main()
