from __future__ import annotations

import json
from datetime import datetime, timezone

from dotenv import load_dotenv
from sqlalchemy import select

from db.database import CompanyRecord, Database, KeywordCompanyResultRecord, SignalRecord


RUN_AT = datetime.now(timezone.utc)


# These companies remain disqualified for the exact "formed in last month"
# keyword. They are re-linked only to broader saved keywords they actually fit.
TARGETS = {
    1776: ({7, 8, 13}, "qualified"),       # Calogy Solutions
    1828: ({7, 9}, "qualified"),           # EVIO
    1882: ({7, 9, 13}, "qualified"),       # Laflamme Aero
    1963: ({9}, "qualified"),              # Reaction Dynamics
    2053: ({9}, "qualified"),              # Canada Rocket Company
    2056: ({9}, "qualified"),              # Wyvern
    2057: ({9}, "qualified"),              # NordSpace
    2058: ({9}, "qualified"),              # Kepler Communications
    2097: ({7, 13}, "watchlist"),           # Limosa
    2104: ({10}, "qualified"),             # ALUULA aerospace composites
    2156: ({10}, "watchlist"),             # Precision ADM
    2157: ({10}, "qualified"),             # TecScan aerospace NDT systems
    2169: ({9, 10}, "qualified"),           # PV Labs
    2171: ({10}, "qualified"),             # FeralX
    2173: ({9}, "qualified"),              # Maritime Launch Services
    2179: ({8, 9}, "qualified"),           # North Vector Dynamics
    2185: ({5, 8}, "qualified"),            # Canadian Strategic Missions
    2187: ({9}, "qualified"),              # Telesat
}


def product_fit(products: list[str]) -> str:
    parts = []
    if "Teamcenter" in products:
        parts.append("Teamcenter can govern product structures, suppliers, released configurations and engineering changes")
    if "NX" in products or "Solid Edge" in products:
        parts.append("NX or Solid Edge can connect detailed design and manufacturing definition")
    if "Simcenter" in products or "Altair tools" in products:
        parts.append("Simcenter or Altair tools can support the documented structural, thermal, aerodynamic or multiphysics validation workload")
    if "Polarion" in products:
        parts.append("Polarion can trace program and safety requirements into tests, defects and verification evidence")
    if "Capital" in products:
        parts.append("Capital can control electrical and electronic architecture")
    if "Opcenter" in products:
        parts.append("Opcenter can provide production, quality and serial or lot genealogy")
    if "Tecnomatix" in products:
        parts.append("Tecnomatix can validate factory, cell and material-flow plans before equipment is fixed")
    if not parts:
        return "The verified engineering and manufacturing program is relevant to CTGTI's product-development portfolio."
    return "; ".join(parts) + "."


def main() -> None:
    load_dotenv(".env")
    database = Database()
    database.initialize()
    results = []

    with database.session() as session:
        prepared = []
        for company_id, (keyword_ids, status) in TARGETS.items():
            company = session.get(CompanyRecord, company_id)
            old = session.scalar(
                select(KeywordCompanyResultRecord)
                .where(KeywordCompanyResultRecord.keyword_id == 1)
                .where(KeywordCompanyResultRecord.company_id == company_id)
            )
            signals = session.scalars(
                select(SignalRecord)
                .where(SignalRecord.company_domain == company.company_domain)
                .where(SignalRecord.raw_score > 0)
                .order_by(SignalRecord.raw_score.desc(), SignalRecord.detected_at.desc())
            ).all()
            if not signals:
                raise RuntimeError(f"No preserved evidence signal for {company.company_name}")
            signal = signals[0]
            prepared.append((company, old, signal, keyword_ids, status))

    for company, old, signal, keyword_ids, status in prepared:
        pain = list(signal.pain_signals or [])
        expansion = list(signal.expansion_signals or [])
        event = pain[0] if pain else signal.reason
        detail = pain[1] if len(pain) > 1 else None
        challenge = event.rstrip(".") + "."
        if detail:
            challenge += " " + detail.rstrip(".") + "."
        challenge += (
            " Inference: the dated program creates immediate configuration, requirements, supplier, "
            "simulation, test and production-traceability pressure as engineering or manufacturing scales."
        )
        products = list(old.recommended_products or [])
        signal_label = expansion[0] if expansion else old.source_title
        why = product_fit(products) + " The " + signal_label.rstrip(".") + " makes the opportunity current."
        raw = int(signal.raw_score or 0)
        evidence = int(round(float(signal.confidence or 0) * 100))
        opportunity = raw if status == "qualified" else min(raw, 64)
        trigger = min(98, max(65, raw)) if status == "qualified" else min(55, max(35, raw - 20))

        for keyword_id in keyword_ids:
            linked = database.record_keyword_company(
                keyword_id,
                company.company_name,
                company.company_domain,
                source_url=signal.source_url,
                source_title=signal.source_title or old.source_title,
                source_publisher=old.source_publisher,
                signal_label=signal_label,
                signal_date=signal.detected_at,
                challenge_summary=challenge,
                why_relevant=why,
                recommended_products=products,
                qualification_status=status,
                opportunity_score=opportunity,
                manufacturing_fit_score=old.manufacturing_fit_score,
                trigger_score=trigger,
                solution_fit_score=old.solution_fit_score,
                evidence_quality_score=evidence,
                seen_at=RUN_AT,
            )
            if linked is None:
                raise RuntimeError(f"Could not re-link {company.company_name} to keyword {keyword_id}")
            results.append({
                "company_id": company.id,
                "company": company.company_name,
                "keyword_id": keyword_id,
                "status": status,
                "source_url": signal.source_url,
            })

    print(json.dumps({"run_at": RUN_AT, "relinked": results}, default=str, indent=2))


if __name__ == "__main__":
    main()
