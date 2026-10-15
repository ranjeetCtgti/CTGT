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
LOCK_PATH = Path(
    r"C:\Users\ranjeet.chaudhary\.codex\automations\daily-keyword-company-research\run.lock"
)


CANDIDATES = [
    {
        "keyword_ids": (8,),
        "company_name": "Vivid Machines Inc.",
        "company_domain": "vivid-machines.com",
        "company_url": "https://www.vivid-machines.com/",
        "location": "Toronto, Ontario, Canada",
        "industry": "Precision agriculture imaging hardware",
        "products": ["Solid Edge", "Teamcenter"],
        "source_url": "https://www.canada.ca/en/agriculture-agri-food/news/2026/09/government-of-canada-invests-in-machine-learning-technology-to-improve-crop-management-and-disease-detection-in-vineyards.html",
        "source_title": "Government of Canada invests in machine learning technology to improve crop management and disease detection in vineyards",
        "source_publisher": "Agriculture and Agri-Food Canada",
        "signal_label": "C$1.693M funds Vivid XV camera expansion from orchards to vineyards",
        "signal_date": datetime(2026, 9, 10, tzinfo=timezone.utc),
        "challenge_summary": (
            "On September 10, 2026, Agriculture and Agri-Food Canada awarded up to "
            "C$1,693,412 to Vivid Machines Inc. through the AgriScience Program to "
            "adapt its Vivid XV AI camera from apple orchards to vineyards, upgrade "
            "the camera technology, and train models for early disease detection, "
            "fruit-quality tracking, and yield prediction by vine, row, and block. "
            "The Vivid XV is a physical imaging system mounted on tractors or sprayers; "
            "inference: supporting a new crop environment while revising camera hardware "
            "and field models adds hardware configuration, BOM/change-control, supplier, "
            "and field-validation pressure."
        ),
        "why_relevant": (
            "Solid Edge can support mechanical and electromechanical packaging changes "
            "to the camera, while Teamcenter can control hardware/software variants, BOM "
            "revisions, and field-test evidence across orchard and vineyard configurations. "
            "The funded development program makes these controls timely before new vineyard "
            "builds and pilots scale."
        ),
        "pain_signal": (
            "Must manage camera hardware changes, crop-specific configurations, and field "
            "validation evidence while expanding the Vivid XV platform into vineyards."
        ),
        "expansion_signal": (
            "Received up to C$1,693,412 to upgrade Vivid XV camera technology and expand "
            "the product from apple orchards to grape vineyards."
        ),
        "qualification_status": "qualified",
        "opportunity_score": 90,
        "manufacturing_fit_score": 90,
        "trigger_score": 94,
        "solution_fit_score": 87,
        "evidence_quality_score": 96,
    },
    {
        "keyword_ids": (10,),
        "company_name": "Pazmac Enterprises Ltd.",
        "company_domain": "pazmac.com",
        "company_url": "https://pazmac.com/",
        "location": "Langley, British Columbia, Canada",
        "industry": "Precision CNC aerospace and defence component manufacturing",
        "products": ["Teamcenter", "Opcenter"],
        "source_url": "https://ctemag.com/news/pazmac-canadian-parts-manufacturer-achieves-as9100d-certification/",
        "source_title": "Pazmac, Canadian parts manufacturer, achieves AS9100D certification",
        "source_publisher": "Cutting Tool Engineering",
        "signal_label": "AS9100D opens aerospace and defence OEM work for Pazmac",
        "signal_date": datetime(2026, 4, 14, tzinfo=timezone.utc),
        "challenge_summary": (
            "On April 14, 2026, Cutting Tool Engineering reported that Pazmac achieved "
            "AS9100D certification after more than 50 years in precision parts manufacturing, "
            "positioning its advanced multi-axis CNC operation for complex, high-performance "
            "aerospace and defence OEM work. The standard raises the required level of quality, "
            "traceability, reliability, and operational discipline; inference: customer-drawing "
            "revision control, inspection records, nonconformance handling, and lot genealogy "
            "become persistent execution burdens as certified work grows."
        ),
        "why_relevant": (
            "Teamcenter can govern customer-controlled drawings, revisions, approved process "
            "definitions, and configuration changes, while Opcenter can connect shop-floor "
            "execution with inspection, nonconformance, and lot traceability. The certification "
            "is a current commercial trigger, but no named contract or capacity ramp was disclosed, "
            "so Pazmac belongs on the watchlist rather than in the qualified tier."
        ),
        "pain_signal": (
            "Must sustain AS9100D document control, inspection evidence, nonconformance discipline, "
            "and traceability for complex aerospace and defence parts."
        ),
        "expansion_signal": (
            "Achieved AS9100D certification, enabling pursuit of more demanding aerospace and "
            "defence OEM component work."
        ),
        "qualification_status": "watchlist",
        "opportunity_score": 62,
        "manufacturing_fit_score": 98,
        "trigger_score": 68,
        "solution_fit_score": 91,
        "evidence_quality_score": 86,
    },
]


def main() -> None:
    load_dotenv(REPO_ROOT / ".env")
    marker = json.loads(LOCK_PATH.read_text(encoding="utf-8"))
    if int(marker.get("pid", 0)) <= 0:
        raise RuntimeError("Exclusive automation lock is not held")

    database = Database(os.environ["DATABASE_URL"])
    database.initialize()
    before = {row.id: row for row in database.list_keywords()}
    expected = {1, 2, 3, 4, 5, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16}
    if set(before) != expected:
        raise RuntimeError(f"Persistent keyword set changed: {sorted(before)}")

    published = {keyword_id: 0 for keyword_id in before}
    persisted = []
    for candidate in CANDIDATES:
        identity = CompanyIdentityEvidence(
            official_name=candidate["company_name"],
            official_website_url=candidate["company_url"],
            corroborating_urls=(candidate["source_url"],),
        )
        signal = ExtractedSignal(
            company_name=candidate["company_name"],
            company_domain=candidate["company_domain"],
            company_url=candidate["company_url"],
            location=candidate["location"],
            industry=candidate["industry"],
            company_industry=candidate["industry"],
            software=candidate["products"],
            signal_type="news",
            signal_source="news",
            pain_signals=[candidate["pain_signal"]],
            expansion_signals=[candidate["expansion_signal"]],
            raw_score=candidate["opportunity_score"],
            confidence=candidate["evidence_quality_score"] / 100,
            reason=candidate["challenge_summary"],
            source_url=candidate["source_url"],
            source_title=candidate["source_title"],
            detected_at=candidate["signal_date"],
        )
        saved, company = database.persist_verified_signal(signal, identity)
        links = []
        for keyword_id in candidate["keyword_ids"]:
            row = database.record_keyword_company(
                keyword_id,
                candidate["company_name"],
                candidate["company_domain"],
                source_url=candidate["source_url"],
                source_title=candidate["source_title"],
                source_publisher=candidate["source_publisher"],
                signal_label=candidate["signal_label"],
                signal_date=candidate["signal_date"],
                challenge_summary=candidate["challenge_summary"],
                why_relevant=candidate["why_relevant"],
                recommended_products=candidate["products"],
                qualification_status=candidate["qualification_status"],
                opportunity_score=candidate["opportunity_score"],
                manufacturing_fit_score=candidate["manufacturing_fit_score"],
                trigger_score=candidate["trigger_score"],
                solution_fit_score=candidate["solution_fit_score"],
                evidence_quality_score=candidate["evidence_quality_score"],
                seen_at=RUN_AT,
            )
            if row is None:
                raise RuntimeError(
                    f"Could not link {candidate['company_name']} to keyword {keyword_id}"
                )
            published[keyword_id] += 1
            links.append(
                {
                    "keyword_id": keyword_id,
                    "company_id": row.company_id,
                    "status": row.qualification_status,
                    "opportunity_score": row.opportunity_score,
                }
            )
        persisted.append(
            {
                "company_name": company.company_name,
                "company_domain": company.company_domain,
                "signal_created": saved.created,
                "duplicate_source_url": saved.duplicate_url,
                "signal_count": company.signal_count,
                "links": links,
            }
        )

    for keyword_id in sorted(before):
        if database.record_keyword_search(
            keyword_id, result_count=published[keyword_id], error=None
        ) is None:
            raise RuntimeError(f"Could not record keyword search {keyword_id}")

    after = {row.id: row for row in database.list_keywords()}
    for keyword_id, prior in before.items():
        current = after[keyword_id]
        if current.search_count != prior.search_count + 1:
            raise RuntimeError(f"Keyword {keyword_id} did not advance exactly once")
        if current.last_error is not None:
            raise RuntimeError(f"Keyword {keyword_id} retained error: {current.last_error}")

    print(
        json.dumps(
            {
                "run_at": RUN_AT.isoformat(),
                "persisted": persisted,
                "keyword_audits": [
                    {
                        "id": keyword_id,
                        "keyword": after[keyword_id].keyword,
                        "search_count_before": before[keyword_id].search_count,
                        "search_count_after": after[keyword_id].search_count,
                        "published": published[keyword_id],
                        "last_error": after[keyword_id].last_error,
                    }
                    for keyword_id in sorted(after)
                ],
            },
            indent=2,
            default=str,
        )
    )


if __name__ == "__main__":
    main()
