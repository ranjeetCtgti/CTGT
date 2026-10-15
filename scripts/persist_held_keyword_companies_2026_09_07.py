from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from db.database import Database
from enrichment.identity_verification import CompanyIdentityEvidence
from models.schema import ExtractedSignal


RUN_AT = datetime.now(timezone.utc)

PROSPECTS = (
    {
        "company_name": "Robotics Centre Inc.",
        "company_domain": "robotics-centre.com",
        "company_url": "https://robotics-centre.com/",
        "location": "Ottawa, Ontario, Canada",
        "industry": "Defence uncrewed systems engineering and manufacturing",
        "products": ["Teamcenter", "NX", "Simcenter", "Opcenter", "Tecnomatix", "Polarion"],
        "scores": (92, 97, 94, 95, 92),
        "signal_date": datetime(2026, 9, 3, tzinfo=timezone.utc),
        "source_url": "https://robotics-centre.com/news/robotics-centre-secures-bdc-financing-to-support-growth-and-uncrewed-systems-manufacturing",
        "source_title": "Robotics Centre Secures BDC Financing; moves to 365 March Rd. to support Uncrewed Systems Growth",
        "source_publisher": "Robotics Centre",
        "signal_label": "C$5M financing supports new Kanata manufacturing facility",
        "keywords": (7, 8, 9, 13, 14),
        "pain_signals": [
            "Must scale Canadian production of multiple uncrewed aerial platforms while controlling product variants, suppliers, engineering changes, quality evidence and manufacturing processes."
        ],
        "expansion_signals": [
            "Secured C$5 million in BDC financing and occupied a new manufacturing facility at 365 March Road in Kanata to expand equipment, inventory, engineering and workforce capacity."
        ],
        "challenge_summary": (
            "On September 3, 2026, Robotics Centre announced C$5 million in BDC financing and a new manufacturing facility at 365 March Road in Kanata. The company designs and builds the Shuriken, Kukri and Longbow uncrewed aerial platforms and plans to expand equipment, inventory, engineering activity, workforce and production capacity. Inference: scaling several defence UAV configurations creates immediate BOM, supplier, change-control, manufacturing-planning, quality and verification-traceability pressure."
        ),
        "why_relevant": (
            "Teamcenter and NX can govern UAV product structures, variants, interfaces and released designs. Tecnomatix and Opcenter can support production planning, execution and quality genealogy as the new facility ramps. Polarion can trace defence requirements and verification evidence, while Simcenter can support structural, thermal, aerodynamic and system validation."
        ),
        "identity": CompanyIdentityEvidence(
            official_name="Robotics Centre Inc.",
            official_website_url="https://robotics-centre.com/",
            corroborating_urls=(
                "https://ised-isde.canada.ca/cc/lgcy/fdrlCrpDtls.html?corpId=12884682",
                "https://robotics-centre.com/news/robotics-centre-secures-bdc-financing-to-support-growth-and-uncrewed-systems-manufacturing",
            ),
        ),
    },
    {
        "company_name": "Coulson Aviation Canada",
        "company_domain": "coulsonaviation.com",
        "company_url": "https://coulsonaviation.com/",
        "location": "Port Alberni, British Columbia, Canada",
        "industry": "Aerial firefighting aircraft engineering, conversion and manufacturing",
        "products": ["Teamcenter", "NX", "Simcenter", "Opcenter", "Tecnomatix", "Polarion"],
        "scores": (94, 99, 98, 96, 98),
        "signal_date": datetime(2026, 8, 7, tzinfo=timezone.utc),
        "source_url": "https://www.canada.ca/en/public-services-procurement/news/2026/08/government-of-canada-conditionally-sells-retired-cc-130h-hercules-aircraft-to-protect-canadians-by-strengthening-canadas-private-sector-aerial-fire.html",
        "source_title": "Government of Canada conditionally sells retired CC-130H Hercules aircraft to Coulson Aviation",
        "source_publisher": "Public Services and Procurement Canada",
        "signal_label": "Ten-aircraft CC-130H conversion program",
        "keywords": (9,),
        "pain_signals": [
            "Must convert ten military CC-130H aircraft into certified aerial tankers while managing aircraft configuration, proprietary RADS integration, regulatory evidence, suppliers and production schedules."
        ],
        "expansion_signals": [
            "The conditional acquisition doubles Coulson's C-130H fleet; government estimates about 20,000 conversion labour hours per aircraft led from Port Alberni."
        ],
        "challenge_summary": (
            "On August 7, 2026, the Government of Canada announced the conditional sale of ten retired CC-130H Hercules aircraft to Coulson Aviation Canada for conversion into aerial firefighting aircraft. The conversion work will be led from Port Alberni and requires about 20,000 labour hours per aircraft. Coulson performs in-house engineering, aircraft modification, manufacturing and maintenance. Inference: a roughly 200,000-hour multi-aircraft conversion program creates immediate configuration, certification, supplier, production and quality-traceability complexity."
        ),
        "why_relevant": (
            "Teamcenter and NX can govern aircraft baselines, modification kits, released configurations and supplier changes. Polarion can connect certification and safety requirements to tests and evidence. Tecnomatix and Opcenter can plan and execute repeatable conversion work, while Simcenter can support structural, aerodynamic and systems validation."
        ),
        "identity": CompanyIdentityEvidence(
            official_name="Coulson Aviation (Canada) Ltd.",
            official_website_url="https://coulsonaviation.com/",
            corroborating_urls=(
                "https://www.canada.ca/en/public-services-procurement/news/2026/08/government-of-canada-conditionally-sells-retired-cc-130h-hercules-aircraft-to-protect-canadians-by-strengthening-canadas-private-sector-aerial-fire.html",
            ),
        ),
    },
    {
        "company_name": "MesoMat",
        "company_domain": "mesomat.com",
        "company_url": "https://mesomat.com/",
        "location": "Hamilton, Ontario, Canada",
        "industry": "Intelligent tire sensing hardware and fleet analytics",
        "products": ["Teamcenter", "Simcenter", "Polarion", "Capital"],
        "scores": (87, 91, 88, 91, 92),
        "signal_date": datetime(2026, 8, 27, tzinfo=timezone.utc),
        "source_url": "https://www.ovinhub.ca/ontario-vehicle-innovation-network-ovin-invests-in-mesomat-to-advance-next-generation-tire-intelligence-for-commercial-fleets/",
        "source_title": "OVIN Invests in MesoMat to Advance Next-Generation Tire Intelligence for Commercial Fleets",
        "source_publisher": "Ontario Vehicle Innovation Network",
        "signal_label": "C$2.2M intelligent-tire R&D project",
        "keywords": (8,),
        "pain_signals": [
            "Must integrate proprietary tire-mounted sensing hardware, embedded electronics and cloud analytics while validating performance and durability across commercial fleets."
        ],
        "expansion_signals": [
            "Joined an OVIN R&D Partnership Fund project with more than C$2.2 million in total investment, including nearly C$700,000 in Ontario support and C$1.5 million in industry contributions."
        ],
        "challenge_summary": (
            "On August 27, 2026, OVIN announced MesoMat's participation in a C$2.2 million R&D project to advance next-generation intelligent tire systems for commercial fleets, including nearly C$700,000 in Ontario support and C$1.5 million in industry contributions. MesoMat combines proprietary tire-mounted hardware with cloud analytics. Inference: the funded multi-partner program creates immediate sensor-design, electrical-interface, requirements, field-validation and controlled-release complexity."
        ),
        "why_relevant": (
            "Teamcenter can govern sensor assemblies, variants, suppliers and released configurations. Capital can support electrical and electronic architecture, Polarion can trace fleet and safety requirements into tests and defects, and Simcenter can support structural, thermal and durability validation of tire-mounted hardware."
        ),
        "identity": CompanyIdentityEvidence(
            official_name="MesoMat",
            official_website_url="https://mesomat.com/",
            corroborating_urls=(
                "https://www.ovinhub.ca/ontario-vehicle-innovation-network-ovin-invests-in-mesomat-to-advance-next-generation-tire-intelligence-for-commercial-fleets/",
            ),
        ),
    },
    {
        "company_name": "Arcanus Aerial Systems Inc.",
        "company_domain": "arcanus.ca",
        "company_url": "https://arcanus.ca/",
        "location": "Toronto, Ontario, Canada",
        "industry": "Defence unmanned aerial systems engineering and manufacturing",
        "products": ["Teamcenter", "NX", "Simcenter", "Opcenter", "Tecnomatix", "Polarion"],
        "scores": (91, 97, 92, 95, 91),
        "signal_date": datetime(2026, 5, 12, tzinfo=timezone.utc),
        "source_url": "https://www.newswire.ca/news-releases/arcanus-aerial-systems-signs-five-year-production-agreement-with-feralx-systems-inc-and-secures-c-1-million-strategic-investment-commitment-861357305.html",
        "source_title": "Arcanus Aerial Systems Signs Five-Year Production Agreement with FeralX Systems Inc.",
        "source_publisher": "Arcanus Aerial Systems via CNW",
        "signal_label": "Five-year Canadian UAS production agreement",
        "keywords": (7, 9, 13, 14),
        "pain_signals": [
            "Must control multiple UAS platform configurations, contract-manufacturer interfaces, approved purchase orders, assembly and test requirements as Canadian production scales."
        ],
        "expansion_signals": [
            "Signed a five-year production and commercialization agreement with FeralX covering Canadian manufacture, assembly, testing and delivery of UAS components and platforms."
        ],
        "challenge_summary": (
            "Arcanus Aerial Systems signed a five-year Canadian production agreement with FeralX dated May 12, 2026. FeralX may manufacture, assemble, test and deliver UAS components and derivative platforms against approved purchase orders, with larger platforms planned for a dedicated facility as volumes grow. Arcanus also committed a C$1 million strategic investment in FeralX. Inference: multi-platform outsourced production creates immediate configuration, supplier-interface, quality, test-evidence and controlled-release complexity."
        ),
        "why_relevant": (
            "Teamcenter and NX can govern UAS product structures, variants, supplier interfaces and released designs across Arcanus and FeralX. Polarion can connect defence and safety requirements to test evidence. Tecnomatix and Opcenter can support assembly planning, execution and quality genealogy, while Simcenter can support platform validation."
        ),
        "identity": CompanyIdentityEvidence(
            official_name="Arcanus Aerial Systems Inc.",
            official_website_url="https://arcanus.ca/",
            corroborating_urls=(
                "https://www.newswire.ca/news-releases/arcanus-aerial-systems-signs-five-year-production-agreement-with-feralx-systems-inc-and-secures-c-1-million-strategic-investment-commitment-861357305.html",
                "https://ca.linkedin.com/company/arcanusaerial",
            ),
        ),
    },
)


def make_signal(prospect: dict[str, object]) -> ExtractedSignal:
    opportunity, _manufacturing, _trigger, _solution, evidence = prospect["scores"]
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
        raw_score=int(opportunity),
        confidence=int(evidence) / 100,
        reason=str(prospect["challenge_summary"]),
        source_url=str(prospect["source_url"]),
        source_title=str(prospect["source_title"]),
        detected_at=prospect["signal_date"],
    )


def record_link(database: Database, keyword_id: int, prospect: dict[str, object]):
    opportunity, manufacturing, trigger, solution, evidence = prospect["scores"]
    return database.record_keyword_company(
        keyword_id,
        str(prospect["company_name"]),
        str(prospect["company_domain"]),
        source_url=str(prospect["source_url"]),
        source_title=str(prospect["source_title"]),
        source_publisher=str(prospect["source_publisher"]),
        signal_label=str(prospect["signal_label"]),
        signal_date=prospect["signal_date"],
        challenge_summary=str(prospect["challenge_summary"]),
        why_relevant=str(prospect["why_relevant"]),
        recommended_products=list(prospect["products"]),
        qualification_status="qualified",
        opportunity_score=int(opportunity),
        manufacturing_fit_score=int(manufacturing),
        trigger_score=int(trigger),
        solution_fit_score=int(solution),
        evidence_quality_score=int(evidence),
        seen_at=RUN_AT,
    )


def main() -> None:
    load_dotenv(REPO_ROOT / ".env")
    database = Database(os.environ["DATABASE_URL"])
    database.initialize()
    existing_rows = database.list_keyword_companies(limit=5000)
    existing_pairs = {
        (row.keyword_id, row.company_domain)
        for row in existing_rows
    }
    company_ids_by_domain = {
        row.company_domain: row.company_id
        for row in existing_rows
        if row.company_domain
    }
    report = []
    for prospect in PROSPECTS:
        saved, company = database.persist_verified_signal(
            make_signal(prospect), prospect["identity"]
        )
        domain = str(prospect["company_domain"])
        company_id = company_ids_by_domain.get(domain)
        links = []
        for keyword_id in prospect["keywords"]:
            if (keyword_id, domain) in existing_pairs:
                links.append({"keyword_id": keyword_id, "status": "existing"})
                continue
            row = record_link(database, keyword_id, prospect)
            if row is None:
                raise RuntimeError(
                    f"Could not link {prospect['company_name']} to keyword {keyword_id}"
                )
            company_id = row.company_id
            company_ids_by_domain[domain] = row.company_id
            existing_pairs.add((keyword_id, domain))
            links.append({"keyword_id": keyword_id, "status": "created"})
        report.append(
            {
                "company_id": company_id,
                "company_name": company.company_name,
                "company_domain": company.company_domain,
                "signal_created": saved.created,
                "duplicate_source_url": saved.duplicate_url,
                "signal_count": company.signal_count,
                "links": links,
            }
        )
    print(json.dumps({"run_at": RUN_AT.isoformat(), "companies": report}, indent=2))


if __name__ == "__main__":
    main()
