from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv

from db.database import Database
from enrichment.identity_verification import CompanyIdentityEvidence, canonicalize_domain
from models.schema import ExtractedSignal


LOCK_PATH = Path(
    r"C:\Users\ranjeet.chaudhary\.codex\automations\daily-keyword-company-research\run.lock"
)


HELD_CANDIDATES = [
    "Palitronica",
    "Eclipse Automation",
    "Davie",
    "OSENSA Innovations",
    "Accelovant",
    "GMI Wheels",
    "PowerWood",
    "Oneka Technologies",
    "Jastram Engineering",
    "INKAS",
    "Open Ocean Robotics",
    "Ascension Aerospace",
    "CanHeat Tactical",
    "Charl-Pol",
    "VAC AERO",
    "Armament Technology",
    "Tulmar Safety Systems",
    "Cadex Defence",
    "Nanuk",
    "Revision Military",
    "FELLFAB",
    "Motrec",
    "Ajile Light Industries",
    "Hammond Manufacturing",
    "Titus Steel",
    "Infiniti Electro-Optics",
]


REJECTED = {
    "Eclipse Automation": "exact_keyword_mismatch: established factory-automation integrator, not a robotics startup and no saved-keyword ERP/PLM implementation trigger",
    "PowerWood": "identity_mismatch: held powerwood.ca identity could not be reconciled with the independently evidenced PowerWood manufacturer at powerwood.com",
    "Open Ocean Robotics": "no_current_dated_trigger: verified USV manufacturer, but preserved expansion/funding evidence dates to 2024",
    "Ascension Aerospace": "insufficient_trigger: official composite manufacturing fit passed, but the 2026 procurement notice was not a contract award",
    "CanHeat Tactical": "insufficient_trigger: verified defence heater manufacturer, but CANSEC participation alone is not an operational buying trigger",
    "Charl-Pol": "identity_blocked: official site returned a Cloudflare block, so the ERP case study could not complete the official identity gate",
    "Armament Technology": "insufficient_trigger: verified defence optics manufacturer, but the 2026 sales representation partnership does not establish engineering or production pressure",
    "Cadex Defence": "identity_blocked: official site timed out and no current independently corroborated operational trigger was verified",
    "Nanuk": "non_canadian_manufacturing_fit: 2026 acquisition evidence identifies Mexican production and did not verify qualifying Canadian manufacturing operations",
    "Revision Military": "non_canadian_identity: the official site identifies a Vermont operation, so it fails the Canadian-company keyword gate",
    "FELLFAB": "identity_blocked: official site was inaccessible; a contract amendment alone could not complete the official identity gate",
    "Motrec": "stale_trigger: autonomous-vehicle partnership remains marketed but the preserved dated evidence is older than the allowed lookback without a new ramp milestone",
    "Ajile Light Industries": "no_dated_trigger: official 3D inspection hardware fit passed, but no current funding, facility, hiring, certification, or production event was verified",
    "Hammond Manufacturing": "exact_keyword_mismatch: current $18M enclosure-factory expansion is strong but does not match any saved keyword",
    "Titus Steel": "no_dated_trigger_and_keyword_mismatch: verified steel supplier without a saved-keyword fit or current operational event",
    "Infiniti Electro-Optics": "insufficient_trigger: verified Canadian defence surveillance hardware, but CANSEC attendance and an older product release do not meet the current trigger gate",
}


def dt(value: str) -> datetime:
    return datetime.fromisoformat(value).replace(tzinfo=timezone.utc)


PASSING = [
    {
        "name": "Palitronica Inc.",
        "domain": "palitronica.com",
        "url": "https://www.palitronica.com/",
        "location": "Waterloo, Ontario, Canada",
        "industry": "Electronics hardware testing and supply-chain assurance systems",
        "source_url": "https://www.palitronica.com/post/palitronica-closes-series-a-funding-led-by-bdc-with-three-kings-capital-frostbite-and-unpopular-f",
        "source_title": "Palitronica Closes Series A Funding Led by BDC, with Three Kings Capital, Frostbite, and Unpopular Funds",
        "publisher": "Palitronica",
        "date": dt("2026-08-11"),
        "label": "Series A funds electronics-test platform scale-up",
        "summary": "On August 11, 2026, Palitronica closed an undisclosed Series A led by BDC's Industrial Innovation Venture Fund after Bell Textron selected its hardware-assurance technology for the MV-75 Cheyenne program. The company says the capital will expand R&D, engineering, enterprise integrations and global operations for its Anvil electronics-testing platform. Inference: scaling a patented hardware/firmware product into automotive and defence programs raises requirements, configuration, verification and controlled-change pressure across product and customer variants.",
        "relevance": "Teamcenter can control the product structure, hardware/firmware baselines and customer-specific configurations, while Polarion can connect safety-critical requirements to verification evidence and defects. The fresh financing and named aerospace program create a near-term window to establish scalable product-development controls before engineering and customer deployments expand.",
        "products": ["Teamcenter", "Polarion"],
        "scores": [81, 84, 88, 84, 78],
        "keywords": [8, 14],
        "corroboration": ("https://app.fundz.net/fundings/palitronica-funding-round-f30919",),
    },
    {
        "name": "Davie",
        "domain": "davie.ca",
        "url": "https://www.davie.ca/",
        "location": "Levis, Quebec, Canada",
        "industry": "Ship design and construction",
        "source_url": "https://www.newswire.ca/news-releases/davie-awarded-historic-contract-to-build-six-program-icebreakers-under-the-national-shipbuilding-strategy-888035960.html",
        "source_title": "Davie Awarded Historic Contract to Build Six Program Icebreakers Under the National Shipbuilding Strategy",
        "publisher": "CNW / Davie",
        "date": dt("2026-08-24"),
        "label": "$11.3B six-icebreaker construction contract",
        "summary": "On August 24, 2026, Davie secured an $11.3-billion fixed-price Government of Canada contract to build six Canadian Coast Guard Program Icebreakers; first construction starts in 2027 and deliveries continue through the 2030s. Each 110-120 metre vessel must support Arctic operations, a helicopter, substantial cargo and a 20,000-nautical-mile range. Inference: a fixed-price six-ship class creates sustained pressure on configuration control, supplier coordination, requirements traceability, production planning, quality records and repeat-ship learning.",
        "relevance": "Teamcenter can govern the class BOM, ship configurations, changes and supplier deliverables; Polarion can trace mission and regulatory requirements to verification evidence. Tecnomatix and Opcenter can support yard sequencing, repeatable work instructions, production visibility and quality traceability. The fixed-price award and 2027 construction start make the pre-production systems window immediate.",
        "products": ["Teamcenter", "Polarion", "Tecnomatix", "Opcenter"],
        "scores": [96, 99, 98, 96, 94],
        "keywords": [3],
        "corroboration": ("https://ca.finance.yahoo.com/news/pm-carney-unveils-11-billion-165512858.html",),
    },
    {
        "name": "OSENSA Innovations Corp.",
        "domain": "osensa.com",
        "url": "https://www.osensa.com/",
        "location": "Burnaby, British Columbia, Canada",
        "industry": "Fiber-optic temperature sensing and partial-discharge monitoring hardware",
        "source_url": "https://smb.vernonmorningstar.com/article/Government-of-Canada-invests-over-dollar30-million-to-help-BC-businesses-navigate-trade-disruptions-and-seize-new-opportunities/6a7a1e322e905784f149abe1",
        "source_title": "Government of Canada invests over $30 million to help B.C. businesses navigate trade disruptions and seize new opportunities",
        "publisher": "PacifiCan / PR Newswire syndication",
        "date": dt("2026-08-10"),
        "label": "$650K sensor manufacturing expansion",
        "summary": "On August 10, 2026, PacifiCan announced $650,000 for OSENSA to expand its Burnaby manufacturing facility, add automated production and test equipment, and improve fiber-optic sensing products for global equipment makers. The sensors monitor high-voltage infrastructure in data centres and industrial facilities, and the project targets exports to Europe, Asia and the Middle East. Inference: automated scale-up and broader OEM/customer requirements increase product-configuration, calibration, test-data and traceability demands.",
        "relevance": "Teamcenter can govern sensor variants, BOMs and engineering changes; Opcenter can capture production and automated-test genealogy. Polarion can connect customer and certification requirements to validation results. The newly announced equipment and facility work make process and data standardization timely before export volume grows.",
        "products": ["Teamcenter", "Opcenter", "Polarion"],
        "scores": [83, 91, 85, 85, 84],
        "keywords": [8],
        "corroboration": ("https://www.canada.ca/en/pacific-economic-development/news/2026/08/backgrounder-government-of-canada-invests-over-30-million-to-help-bc-businesses-navigate-trade-disruptions-and-seize-new-opportunities.html",),
    },
    {
        "name": "Accelovant Technologies Corporation",
        "domain": "accelovant.com",
        "url": "https://accelovant.com/",
        "location": "North Vancouver, British Columbia, Canada",
        "industry": "Fiber-optic temperature sensing and edge-control hardware",
        "source_url": "https://search.open.canada.ca/grants/record/pacifican%2C240-2025-2026-Q3-00024%2Ccurrent",
        "source_title": "PacifiCan contribution PC0012611: Reshoring fiber optic sensor production",
        "publisher": "Open Government Canada",
        "date": dt("2025-12-29"),
        "label": "$990K production reshoring and certification program",
        "summary": "PacifiCan's December 29, 2025 agreement provides Accelovant $990,000 through March 2029 to reshore fiber-optic sensor production and diversify export markets; the August 2026 funding announcement says the work will expand and automate manufacturing and obtain certifications for new markets. Accelovant's products operate in semiconductor, AI data-centre and industrial-power environments. Inference: the continuing reshoring program creates supplier-transfer, process-validation, product-certification and manufacturing-traceability demands.",
        "relevance": "Teamcenter can control sensor product structures, transferred manufacturing data and engineering changes; Opcenter can standardize production and test genealogy in the reshored operation. Polarion can link export-market certification requirements to validation evidence. The active multi-year contribution and current automation work provide a practical implementation window.",
        "products": ["Teamcenter", "Opcenter", "Polarion"],
        "scores": [80, 89, 78, 84, 92],
        "keywords": [8],
        "corroboration": ("https://www.canada.ca/en/pacific-economic-development/news/2026/08/backgrounder-government-of-canada-invests-over-30-million-to-help-bc-businesses-navigate-trade-disruptions-and-seize-new-opportunities.html",),
    },
    {
        "name": "GMI Wheels",
        "domain": "gmiwheels.com",
        "url": "https://gmiwheels.com/",
        "location": "Langley, British Columbia, Canada",
        "industry": "Off-highway industrial wheel and rim manufacturing",
        "source_url": "https://www.canada.ca/fr/developpement-economique-pacifique/nouvelles/2026/08/document-dinformation--le-gouvernement-du-canada-investit-plus-de-30-millions-de-dollars-pour-aider-des-entreprises-de-la-colombie-britannique-a-fa.html",
        "source_title": "Le gouvernement du Canada investit plus de 30 millions de dollars pour aider des entreprises de la Colombie-Britannique",
        "publisher": "PacifiCan",
        "date": dt("2026-08-10"),
        "label": "$1M wheel manufacturing modernization",
        "summary": "On August 10, 2026, PacifiCan announced $1 million for GMI Wheels to upgrade its manufacturing facility, adopt new production technologies and increase Canadian capacity for mining, construction and industrial wheels and rims. The project also aims to grow exports and reduce reliance on imported components. Inference: new processes and localized supply increase routing, supplier-quality, variant and shop-floor traceability demands for safety-critical heavy-equipment wheels.",
        "relevance": "Teamcenter can govern CAD/CAM product variants, BOMs and supplier changes; Opcenter can provide production and quality genealogy. Tecnomatix can validate upgraded manufacturing flows before equipment and capacity changes are locked in. The newly funded modernization is the point at which common product and process data can reduce ramp risk.",
        "products": ["Teamcenter", "Opcenter", "Tecnomatix"],
        "scores": [79, 93, 82, 81, 88],
        "keywords": [8],
        "corroboration": ("https://www.canada.ca/en/pacific-economic-development/news/2026/08/backgrounder-government-of-canada-invests-over-30-million-to-help-bc-businesses-navigate-trade-disruptions-and-seize-new-opportunities.html",),
    },
    {
        "name": "Oneka Technologies",
        "domain": "onekawater.com",
        "url": "https://www.onekawater.com/",
        "location": "Sherbrooke, Quebec, Canada",
        "industry": "Wave-powered desalination hardware platforms",
        "source_url": "https://oceansupercluster.ca/project/canadas-ocean-supercluster-announces-4-1m-ai-powered-monitoring-for-sustainable-wave-powered-desalination-project/",
        "source_title": "Canada's Ocean Supercluster Announces $4.1M AI-powered Monitoring for Sustainable Wave-powered Desalination Project",
        "publisher": "Canada's Ocean Supercluster",
        "date": dt("2026-03-04"),
        "label": "$4.1M wave-desalination commercialization project",
        "summary": "On March 4, 2026, Canada's Ocean Supercluster announced a $4.1-million project led by Oneka Technologies, including $1.6 million from the cluster, to commercialize and add AI monitoring to Canadian wave-powered desalination hardware. Partners include Ocean Sonics, Innovobot Labs and Lengkeek Vessel Engineering. Inference: integrating marine structures, pumps, sensing, communications and AI across partners increases system requirements, configuration, simulation and field-validation complexity.",
        "relevance": "Teamcenter can govern the multidisciplinary platform configuration and partner deliverables; Polarion can trace performance and environmental requirements to tests. Simcenter can support hydrodynamic, structural and system-level validation. The funded commercialization program creates urgency to establish controlled baselines before deployments scale.",
        "products": ["Teamcenter", "Polarion", "Simcenter"],
        "scores": [82, 90, 84, 87, 88],
        "keywords": [8],
        "corroboration": ("https://oceansupercluster.ca/project/canadas-ocean-supercluster-announces-4-1m-ai-powered-monitoring-for-sustainable-wave-powered-desalination-project/",),
    },
    {
        "name": "Jastram Engineering",
        "domain": "jastram.com",
        "url": "https://jastram.com/",
        "location": "North Vancouver, British Columbia, Canada",
        "industry": "Marine steering and control-system manufacturing",
        "source_url": "https://www.canada.ca/en/pacific-economic-development/news/2026/08/backgrounder-government-of-canada-invests-over-30-million-to-help-bc-businesses-navigate-trade-disruptions-and-seize-new-opportunities.html",
        "source_title": "Backgrounder: Government of Canada invests over $30 million to help B.C. businesses navigate trade disruptions and seize new opportunities",
        "publisher": "PacifiCan",
        "date": dt("2026-08-10"),
        "label": "$225K marine-control production expansion",
        "summary": "On August 10, 2026, PacifiCan announced $225,000 for Jastram Engineering to buy advanced equipment and train staff, increasing capacity and manufacturing efficiency for steering and control systems used on commercial, recreational and defence vessels. The project targets domestic and export growth in Canada's marine and defence supply chains. Inference: higher custom-system throughput increases configuration, interface, supplier, test and production-planning pressure.",
        "relevance": "Teamcenter can control engineered-to-order steering configurations, interfaces, BOMs and changes; Opcenter can standardize routing, inspection and test genealogy as capacity grows. The new equipment and training program make a controlled digital thread valuable before expanded throughput creates more rework and scheduling risk.",
        "products": ["Teamcenter", "Opcenter"],
        "scores": [79, 95, 82, 84, 90],
        "keywords": [14],
        "corroboration": ("https://www.seaspan.com/press-release/north-vancouver-company-awarded-contract-for-work-on-naval-supply-ships/",),
    },
    {
        "name": "INKAS",
        "domain": "inkasarmored.com",
        "url": "https://inkasarmored.com/",
        "location": "Toronto, Ontario, Canada",
        "industry": "Armoured, tactical and special-purpose vehicle manufacturing",
        "source_url": "https://inkas.ca/inkas-announces-major-north-american-manufacturing-expansion-across-canada-and-the-united-states/",
        "source_title": "INKAS Announces Major North American Manufacturing Expansion Across Canada and the United States",
        "publisher": "INKAS",
        "date": dt("2026-06-30"),
        "label": "Three-facility armoured-vehicle production expansion",
        "summary": "On June 30, 2026, INKAS announced three additional production facilities: 42,000 square feet in Toronto, 200,000 square feet in Charlotte and 31,000 square feet in Fort Pierce, more than doubling its North American armoured-vehicle, defence and special-purpose production footprint by July 31. The expansion supports armoured and tactical vehicles, drones/UAVs and custom platforms. Inference: a rapid multi-site ramp across vehicle and autonomous-system variants creates acute BOM, configuration, supplier, line-planning and quality-traceability pressure.",
        "relevance": "Teamcenter can establish one governed product and configuration backbone across sites; Tecnomatix can validate line layouts and process plans, and Opcenter can standardize execution and quality genealogy. The facilities' immediate commissioning schedule makes cross-site data and process control urgent.",
        "products": ["Teamcenter", "Tecnomatix", "Opcenter"],
        "scores": [92, 98, 94, 93, 88],
        "keywords": [11, 14],
        "corroboration": ("https://ckpgtoday.ca/2026/06/30/toronto-based-armoured-vehicle-maker-inkas-expands-production/",),
    },
    {
        "name": "Vac Aero International Inc.",
        "domain": "vacaero.com",
        "url": "https://vacaero.com/",
        "location": "Burlington, Ontario and Quebec, Canada",
        "industry": "Vacuum-furnace design, manufacturing and aerospace heat treatment",
        "source_url": "https://www.boeing.ca/content/theboeingcompany/ca/en/news/2026/boeing-commits-to-supporting-enhanced-vac-aero-capability.html",
        "source_title": "Boeing commits to supporting enhanced Vac Aero capability",
        "publisher": "Boeing Canada",
        "date": dt("2026-04-02"),
        "label": "$7M Boeing vacuum-furnace commitment",
        "summary": "On April 2, 2026, Boeing committed $7 million to VAC AERO under the CP-8A Poseidon industrial-benefits program and will buy two modern vacuum furnaces for aerospace tube and duct heat treatment supporting commercial, space and defence programs. VAC AERO designs and builds custom vacuum furnaces at Canadian sites in Ontario and Quebec. Inference: delivering program-specific capital equipment increases engineered-to-order configuration, thermal validation, supplier, build-record and acceptance-test requirements.",
        "relevance": "Teamcenter can govern custom-furnace product structures and changes, Simcenter can support thermal and system validation, and Opcenter can capture build and acceptance-test traceability. The funded Boeing order creates a defined program and delivery window for tightening engineering-to-manufacturing control.",
        "products": ["Teamcenter", "Simcenter", "Opcenter"],
        "scores": [89, 97, 91, 92, 91],
        "keywords": [9, 10, 14],
        "corroboration": ("https://www.boeing.ca/content/theboeingcompany/ca/en/news/2026/boeing-commits-to-supporting-enhanced-vac-aero-capability.html",),
    },
    {
        "name": "Tulmar Safety Systems",
        "domain": "tulmar.com",
        "url": "https://www.tulmar.com/",
        "location": "Hawkesbury, Ontario, Canada",
        "industry": "Engineered aviation, defence and civil-safety equipment manufacturing",
        "source_url": "https://thereview.ca/2026/03/07/ontario-investing-896700-to-support-tulmar-safety-systems-manufacturing-expansion-and-export-growth/",
        "source_title": "Ontario investing $896,700 to support Tulmar Safety Systems' manufacturing expansion and export growth",
        "publisher": "The Review Newspaper",
        "date": dt("2026-03-07"),
        "label": "$4.28M protective-systems manufacturing expansion",
        "summary": "On March 7, 2026, Ontario announced $896,700 for Tulmar Safety Systems alongside Tulmar's $3,378,940 investment in workforce training, capital equipment and business development for European defence and aviation growth. Tulmar says the program will scale its Ontario manufacturing and engineering capabilities for engineered protective solutions. Inference: new equipment, export variants and regulated defence/aviation customers increase requirements, configuration, qualification and production-traceability burdens.",
        "relevance": "Teamcenter can govern product variants, BOMs and engineering changes; Polarion can trace regulated customer requirements to qualification evidence, and Opcenter can preserve production and quality genealogy. The combined $4.28-million program is already funding equipment and training, making this the right point to standardize the digital thread.",
        "products": ["Teamcenter", "Polarion", "Opcenter"],
        "scores": [87, 96, 89, 90, 83],
        "keywords": [9, 10, 14],
        "corroboration": ("https://thereview.ca/2026/03/07/ontario-investing-896700-to-support-tulmar-safety-systems-manufacturing-expansion-and-export-growth/",),
    },
]


def main() -> None:
    if len(HELD_CANDIDATES) != 26 or len(REJECTED) + len(PASSING) != 26:
        raise RuntimeError("Held-candidate accounting must equal 26")
    if not LOCK_PATH.exists():
        raise RuntimeError("Exclusive research lock is not held")
    marker = json.loads(LOCK_PATH.read_text(encoding="utf-8"))
    if marker.get("mode") != "manual-broader-rerun":
        raise RuntimeError(f"Unexpected lock owner: {marker}")

    load_dotenv(".env")
    database = Database()
    database.initialize()
    keywords_before = {item.id: item for item in database.list_keywords()}
    if set(keywords_before) != {1, 2, 3, 4, 5, 7, 8, 9, 10, 11, 12, 13, 14, 15}:
        raise RuntimeError("Persistent keyword set changed after the held run")

    existing_links = database.list_keyword_companies(limit=1000)
    workbook_matches = {"davie.ca": 71}
    result = {
        "held_reviewed": len(HELD_CANDIDATES),
        "rejected": REJECTED,
        "identity_blocked": [
            name for name, reason in REJECTED.items()
            if reason.startswith("identity_")
        ],
        "signals_created": 0,
        "signals_duplicate": 0,
        "keyword_links_written": 0,
        "keyword_links_duplicate": 0,
        "companies_new": [],
        "companies_existing": [],
        "eligible_company_ids": [],
        "published": [],
        "keyword_search_counts_before": {
            str(key): value.search_count for key, value in keywords_before.items()
        },
    }

    for item in PASSING:
        existing_by_domain = database.find_company_by_domain(item["domain"])
        existing_by_name = database.find_company_by_identity(item["name"], item["domain"])
        if (existing_by_domain is None) != (existing_by_name is None):
            raise RuntimeError(f"DB identity mismatch for {item['name']}")
        if item["domain"] == "davie.ca" and item["domain"] not in workbook_matches:
            raise RuntimeError("Davie workbook collision was not preserved")

        opportunity, manufacturing, trigger, solution, evidence = item["scores"]
        if opportunity < 65 or evidence < 60 or manufacturing < 60:
            raise RuntimeError(f"Qualification score gate failed for {item['name']}")
        signal = ExtractedSignal(
            company_name=item["name"],
            company_domain=item["domain"],
            company_url=item["url"],
            location=item["location"],
            industry=item["industry"],
            company_industry=item["industry"],
            software=item["products"],
            signal_type="news",
            signal_source="news",
            pain_signals=[item["summary"]],
            expansion_signals=[item["label"]],
            raw_score=opportunity,
            confidence=evidence / 100,
            reason=item["relevance"],
            source_url=item["source_url"],
            source_title=item["source_title"],
            detected_at=item["date"],
        )
        identity = CompanyIdentityEvidence(
            official_name=item["name"],
            official_website_url=item["url"],
            corroborating_urls=item["corroboration"],
        )
        saved, _company = database.persist_verified_signal(signal, identity)
        if saved.created:
            result["signals_created"] += 1
        else:
            result["signals_duplicate"] += 1

        company = database.find_company_by_domain(item["domain"])
        if company is None:
            raise RuntimeError(f"Verified company missing after persistence: {item['name']}")
        if existing_by_domain is None:
            result["companies_new"].append(item["name"])
        else:
            result["companies_existing"].append(item["name"])

        for keyword_id in item["keywords"]:
            current_links = database.list_keyword_companies(limit=1000)
            duplicate = next(
                (
                    row for row in current_links
                    if row.keyword_id == keyword_id
                    and canonicalize_domain(row.company_domain) == item["domain"]
                    and row.source_url == item["source_url"]
                    and row.qualification_status == "qualified"
                ),
                None,
            )
            if duplicate is not None:
                link = duplicate
                result["keyword_links_duplicate"] += 1
            else:
                link = database.record_keyword_company(
                    keyword_id,
                    item["name"],
                    item["domain"],
                    source_url=item["source_url"],
                    source_title=item["source_title"],
                    source_publisher=item["publisher"],
                    signal_label=item["label"],
                    signal_date=item["date"],
                    challenge_summary=item["summary"],
                    why_relevant=item["relevance"],
                    recommended_products=item["products"],
                    qualification_status="qualified",
                    opportunity_score=opportunity,
                    manufacturing_fit_score=manufacturing,
                    trigger_score=trigger,
                    solution_fit_score=solution,
                    evidence_quality_score=evidence,
                )
                if link is None:
                    raise RuntimeError(
                        f"Could not record keyword {keyword_id} for {item['name']}"
                    )
                result["keyword_links_written"] += 1
            result["eligible_company_ids"].append(link.company_id)
            result["published"].append(
                {
                    "company_id": link.company_id,
                    "company": item["name"],
                    "domain": item["domain"],
                    "keyword_id": keyword_id,
                    "status": "qualified",
                    "source_url": item["source_url"],
                }
            )

    keywords_after = {item.id: item for item in database.list_keywords()}
    for keyword_id, before in keywords_before.items():
        if keywords_after[keyword_id].search_count != before.search_count:
            raise RuntimeError(f"Keyword {keyword_id} search counter changed")
    result["keyword_search_counts_after"] = {
        str(key): value.search_count for key, value in keywords_after.items()
    }
    result["eligible_company_ids"] = sorted(set(result["eligible_company_ids"]))
    result["completed_at"] = datetime.now(timezone.utc).isoformat()
    print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    main()
