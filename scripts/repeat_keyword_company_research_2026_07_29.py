from __future__ import annotations

from datetime import datetime, timezone

from dotenv import load_dotenv

from db.database import Database
from models.schema import ExtractedSignal


def dated(value: str) -> datetime:
    return datetime.fromisoformat(f"{value}T12:00:00+00:00")


COMPANIES = [
    {
        "keyword_id": 1,
        "company_name": "FeralX Systems",
        "company_domain": "feralx.ca",
        "company_url": "https://www.feralx.ca/",
        "location": "Greater Toronto Area, Ontario, Canada",
        "industry": "Defence manufacturing, unmanned systems, and precision machining",
        "qualification": {
            "source_url": (
                "https://www.tradingview.com/news/"
                "tmx_newsfile:3c89124d5094b:0-feralx-systems-inc-announces-closing-of-a-"
                "private-placement-and-the-acquisition-of-two-new-makino-machining-centers/"
            ),
            "source_title": (
                "FeralX Systems Inc. Announces Closing of a Private Placement and the "
                "Acquisition of Two New Makino Machining Centers"
            ),
            "source_publisher": "TMX Newsfile",
            "signal_label": (
                "$2.05M financing and two new Makino machining centers for production scale-up"
            ),
            "signal_date": dated("2026-07-17"),
            "challenge_summary": (
                "On July 17, 2026, FeralX reported July 15 and 17 private-placement "
                "closings totaling $2.05 million and a US$702,000 acquisition of two Makino "
                "a51nx four-axis horizontal machining centres. The machines expand a "
                "standardized five-machine Makino cell with common pallets and tooling, "
                "which FeralX says is being prepared for an automated pallet-handling system "
                "and unattended, lights-out production. Inference: scaling precision defence "
                "and unmanned-system production across a shared automated cell creates "
                "immediate needs for controlled product definitions, machining revisions, "
                "work instructions, capacity planning, and serial-quality traceability."
            ),
            "why_relevant": (
                "Teamcenter can control drone and machined-component BOMs, revisions, and "
                "supplier changes; NX supports product and CAM definitions for the Makino "
                "cell. Opcenter can provide work-order, machine, and quality genealogy, while "
                "Tecnomatix can validate the evolving automated-cell layout and throughput. "
                "Polarion fits traceable defence requirements and verification. The capital "
                "close and installed equipment make this timely because FeralX is moving "
                "toward higher-throughput production now."
            ),
            "recommended_products": [
                "Teamcenter",
                "NX",
                "Opcenter",
                "Tecnomatix",
                "Polarion",
            ],
            "opportunity_score": 96,
            "manufacturing_fit_score": 99,
            "trigger_score": 99,
            "solution_fit_score": 97,
            "evidence_quality_score": 94,
        },
        "signals": [
            {
                "source_url": (
                    "https://www.tradingview.com/news/"
                    "tmx_newsfile:3c89124d5094b:0-feralx-systems-inc-announces-closing-of-a-"
                    "private-placement-and-the-acquisition-of-two-new-makino-machining-centers/"
                ),
                "source_title": (
                    "FeralX Systems Inc. Announces Closing of a Private Placement and the "
                    "Acquisition of Two New Makino Machining Centers"
                ),
                "signal_label": "Automated precision-machining cell expansion",
                "signal_date": dated("2026-07-17"),
                "challenge_summary": (
                    "FeralX added two US$702,000 Makino a51nx machining centres to a "
                    "standardized five-machine cell and is preparing the cell for unattended "
                    "automated pallet handling as production scales."
                ),
                "why_relevant": (
                    "The funded equipment expansion supports an immediate Teamcenter, NX, "
                    "Opcenter, and Tecnomatix opportunity around revisions, CAM definitions, "
                    "production genealogy, quality, and cell-throughput planning."
                ),
            },
            {
                "source_url": (
                    "https://www.newswire.ca/news-releases/"
                    "arcanus-aerial-systems-signs-five-year-production-agreement-with-feralx-"
                    "systems-inc-and-secures-c-1-million-strategic-investment-commitment-"
                    "861357305.html"
                ),
                "source_title": (
                    "Arcanus Aerial Systems Signs Five-Year Production Agreement with FeralX "
                    "Systems Inc. and Secures C$1 Million Strategic Investment Commitment"
                ),
                "signal_label": "Five-year Canadian drone production agreement",
                "signal_date": dated("2026-06-05"),
                "challenge_summary": (
                    "Arcanus appointed FeralX as a five-year Canadian contract manufacturer "
                    "to manufacture, assemble, test, and deliver components and assemblies "
                    "for multiple unmanned-aircraft platforms. Initial interceptor-drone "
                    "deliveries can use FeralX's existing facility, while the partners plan a "
                    "dedicated facility for larger platforms as volume grows; Arcanus also "
                    "committed a C$1 million strategic investment for production scale-up."
                ),
                "why_relevant": (
                    "A multi-platform defence-drone program moving from initial deliveries "
                    "toward a dedicated facility requires product configuration, requirement "
                    "and test traceability, governed production data, and scalable operations "
                    "management across the two companies."
                ),
            },
        ],
    },
    {
        "keyword_id": 3,
        "company_name": "Ocean Pacific Marine",
        "company_domain": "oceanpacificmarine.com",
        "company_url": "http://www.oceanpacificmarine.com/",
        "location": "Campbell River, British Columbia, Canada",
        "industry": "Shipbuilding, marine fabrication, and boatyard operations",
        "qualification": {
            "source_url": (
                "https://www.canada.ca/en/public-services-procurement/news/2026/06/"
                "government-of-canada-awards-contract-for-new-police-coastal-patrol-vessels-"
                "to-strengthen-security-in-british-columbia.html"
            ),
            "source_title": (
                "Government of Canada awards contract for new police coastal patrol vessels "
                "to strengthen security in British Columbia"
            ),
            "source_publisher": "Public Services and Procurement Canada",
            "signal_label": "$74.7M contract for three RCMP coastal patrol vessels",
            "signal_date": dated("2026-07-02"),
            "challenge_summary": (
                "On July 2, 2026, Canada awarded an approximately $74.7 million joint-venture "
                "contract to Ocean Pacific Marine and Camarc Design for three new RCMP coastal "
                "patrol vessels, all to be built at Ocean Pacific's Campbell River shipyard. "
                "The 24–25 metre jet-propelled aluminium vessels must begin entering service "
                "in 2028, operate within 400 nautical miles of home port, and sustain a "
                "four-person crew for up to seven days without refuelling or replenishment. "
                "Inference: translating the design partner's regulated patrol-vessel "
                "definition into three Canadian builds creates configuration, supplier, "
                "requirements, systems-integration, test, and build-quality traceability "
                "pressure."
            ),
            "why_relevant": (
                "Teamcenter can govern the joint product definition, BOM, supplier data, and "
                "engineering changes; NX supports aluminium vessel and production design. "
                "Polarion can trace RCMP endurance, range, safety, and mission requirements "
                "into verification, while Capital supports propulsion, navigation, and "
                "electrical integration. Opcenter can preserve work and quality genealogy "
                "across the three builds. The fixed 2028 service milestone makes digital "
                "control valuable before detailed design and production ramp."
            ),
            "recommended_products": [
                "Teamcenter",
                "NX",
                "Polarion",
                "Capital",
                "Opcenter",
            ],
            "opportunity_score": 95,
            "manufacturing_fit_score": 100,
            "trigger_score": 99,
            "solution_fit_score": 98,
            "evidence_quality_score": 100,
        },
        "signals": [
            {
                "source_url": (
                    "https://www.canada.ca/en/public-services-procurement/news/2026/06/"
                    "government-of-canada-awards-contract-for-new-police-coastal-patrol-"
                    "vessels-to-strengthen-security-in-british-columbia.html"
                ),
                "source_title": (
                    "Government of Canada awards contract for new police coastal patrol "
                    "vessels to strengthen security in British Columbia"
                ),
                "signal_label": "$74.7M three-vessel RCMP build contract",
                "signal_date": dated("2026-07-02"),
                "challenge_summary": (
                    "Ocean Pacific Marine will build three 24–25 metre jet-propelled aluminium "
                    "patrol vessels under an approximately $74.7 million federal contract, "
                    "with service entry beginning in 2028 and defined range and endurance "
                    "requirements."
                ),
                "why_relevant": (
                    "The regulated, multi-vessel build creates a concrete need for controlled "
                    "design and BOM data, requirement verification, electrical integration, "
                    "supplier coordination, and production-quality genealogy."
                ),
            }
        ],
    },
]


def main() -> None:
    load_dotenv()
    database = Database()
    database.initialize()
    keywords = {keyword.id: keyword for keyword in database.list_keywords()}

    for company in COMPANIES:
        qualification = company["qualification"]
        for evidence in company["signals"]:
            signal = ExtractedSignal(
                company_name=company["company_name"],
                company_domain=company["company_domain"],
                company_url=company["company_url"],
                location=company["location"],
                industry=company["industry"],
                company_industry=company["industry"],
                software=qualification["recommended_products"],
                signal_type="news",
                signal_source="news",
                pain_signals=[evidence["challenge_summary"]],
                expansion_signals=[evidence["signal_label"]],
                raw_score=qualification["opportunity_score"],
                confidence=qualification["evidence_quality_score"] / 100,
                reason=evidence["why_relevant"],
                source_url=evidence["source_url"],
                source_title=evidence["source_title"],
                detected_at=evidence["signal_date"],
            )
            saved = database.save_signal(signal)
            database.upsert_company(signal)
            print(
                f"{company['company_name']}: source={evidence['signal_label']} "
                f"created={saved.created}"
            )

        ledger = database.record_keyword_company(
            company["keyword_id"],
            company["company_name"],
            company["company_domain"],
            source_url=qualification["source_url"],
            source_title=qualification["source_title"],
            source_publisher=qualification["source_publisher"],
            signal_label=qualification["signal_label"],
            signal_date=qualification["signal_date"],
            challenge_summary=qualification["challenge_summary"],
            why_relevant=qualification["why_relevant"],
            recommended_products=qualification["recommended_products"],
            qualification_status="qualified",
            opportunity_score=qualification["opportunity_score"],
            manufacturing_fit_score=qualification["manufacturing_fit_score"],
            trigger_score=qualification["trigger_score"],
            solution_fit_score=qualification["solution_fit_score"],
            evidence_quality_score=qualification["evidence_quality_score"],
        )
        if ledger is None:
            raise RuntimeError(f"Could not link {company['company_name']} to its keyword")
        print(f"{company['company_name']}: qualification={ledger.qualification_status}")

    for keyword_id, published in {1: 1, 2: 0, 3: 1, 4: 0}.items():
        result = database.record_keyword_search(keyword_id, result_count=published)
        if result is None:
            raise RuntimeError(f"Could not update keyword {keyword_id}")
        print(f"{keywords[keyword_id].keyword}: published={published}")


if __name__ == "__main__":
    main()
