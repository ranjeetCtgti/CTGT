from __future__ import annotations

import argparse
import re
import zipfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse
from xml.etree import ElementTree as ET


SPREADSHEET_NS = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
DOCUMENT_REL_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
PACKAGE_REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"


@dataclass(frozen=True, slots=True)
class WorksheetData:
    name: str
    rows: list[list[Any]]
    hyperlinks: dict[str, str]


@dataclass(frozen=True, slots=True)
class CompanyImport:
    company_name: str
    company_url: str | None
    company_domain: str | None
    linkedin_url: str | None
    organization_type: str | None
    employee_count: str | None
    software: list[str]
    confidence: float | None
    priority_score: int


def _column_index(cell_reference: str) -> int:
    letters = re.match(r"[A-Z]+", cell_reference.upper())
    if not letters:
        return 0
    result = 0
    for character in letters.group(0):
        result = result * 26 + ord(character) - ord("A") + 1
    return result - 1


def _relationship_map(xml_bytes: bytes) -> dict[str, str]:
    root = ET.fromstring(xml_bytes)
    return {
        relationship.attrib["Id"]: relationship.attrib["Target"]
        for relationship in root.findall(f"{{{PACKAGE_REL_NS}}}Relationship")
    }


def _shared_strings(archive: zipfile.ZipFile) -> list[str]:
    try:
        root = ET.fromstring(archive.read("xl/sharedStrings.xml"))
    except KeyError:
        return []
    values: list[str] = []
    for item in root.findall(f"{{{SPREADSHEET_NS}}}si"):
        values.append(
            "".join(
                node.text or ""
                for node in item.iter(f"{{{SPREADSHEET_NS}}}t")
            )
        )
    return values


def _cell_value(cell: ET.Element, shared_strings: list[str]) -> Any:
    cell_type = cell.attrib.get("t")
    if cell_type == "inlineStr":
        return "".join(
            node.text or ""
            for node in cell.iter(f"{{{SPREADSHEET_NS}}}t")
        )

    value_node = cell.find(f"{{{SPREADSHEET_NS}}}v")
    if value_node is None or value_node.text is None:
        return None
    raw_value = value_node.text
    if cell_type == "s":
        return shared_strings[int(raw_value)]
    if cell_type in {"str", "e"}:
        return raw_value
    if cell_type == "b":
        return raw_value == "1"
    try:
        numeric = float(raw_value)
    except ValueError:
        return raw_value
    return int(numeric) if numeric.is_integer() else numeric


def _worksheet_hyperlinks(
    archive: zipfile.ZipFile,
    sheet_path: str,
    root: ET.Element,
) -> dict[str, str]:
    relationship_path = (
        str(Path(sheet_path).parent / "_rels" / f"{Path(sheet_path).name}.rels")
        .replace("\\", "/")
    )
    try:
        relationships = _relationship_map(archive.read(relationship_path))
    except KeyError:
        relationships = {}

    hyperlinks: dict[str, str] = {}
    container = root.find(f"{{{SPREADSHEET_NS}}}hyperlinks")
    if container is None:
        return hyperlinks
    for hyperlink in container.findall(f"{{{SPREADSHEET_NS}}}hyperlink"):
        cell_reference = hyperlink.attrib.get("ref")
        relationship_id = hyperlink.attrib.get(f"{{{DOCUMENT_REL_NS}}}id")
        target = relationships.get(relationship_id or "")
        if cell_reference and target:
            hyperlinks[cell_reference] = target
    return hyperlinks


def read_xlsx(path: Path) -> list[WorksheetData]:
    with zipfile.ZipFile(path) as archive:
        shared_strings = _shared_strings(archive)
        workbook_root = ET.fromstring(archive.read("xl/workbook.xml"))
        workbook_relationships = _relationship_map(
            archive.read("xl/_rels/workbook.xml.rels")
        )
        worksheets: list[WorksheetData] = []
        sheets_node = workbook_root.find(f"{{{SPREADSHEET_NS}}}sheets")
        if sheets_node is None:
            return worksheets

        for sheet in sheets_node.findall(f"{{{SPREADSHEET_NS}}}sheet"):
            relationship_id = sheet.attrib[f"{{{DOCUMENT_REL_NS}}}id"]
            target = workbook_relationships[relationship_id].lstrip("/")
            sheet_path = target if target.startswith("xl/") else f"xl/{target}"
            root = ET.fromstring(archive.read(sheet_path))
            hyperlinks = _worksheet_hyperlinks(archive, sheet_path, root)
            rows: list[list[Any]] = []
            sheet_data = root.find(f"{{{SPREADSHEET_NS}}}sheetData")
            if sheet_data is not None:
                for row in sheet_data.findall(f"{{{SPREADSHEET_NS}}}row"):
                    values: list[Any] = []
                    for cell in row.findall(f"{{{SPREADSHEET_NS}}}c"):
                        reference = cell.attrib.get("r", "A1")
                        index = _column_index(reference)
                        while len(values) <= index:
                            values.append(None)
                        values[index] = _cell_value(cell, shared_strings)
                    rows.append(values)
            worksheets.append(
                WorksheetData(
                    name=sheet.attrib["name"],
                    rows=rows,
                    hyperlinks=hyperlinks,
                )
            )
        return worksheets


def _clean_text(value: Any) -> str | None:
    if value is None:
        return None
    cleaned = " ".join(str(value).split()).strip()
    return cleaned or None


def _normalize_name(value: str) -> str:
    return " ".join(value.casefold().split())


def _safe_similar_name(left: str, right: str) -> bool:
    from db.database import _names_similar

    left_normalized = _normalize_name(left)
    right_normalized = _normalize_name(right)
    return _names_similar(left, right) and (
        left_normalized in right_normalized
        or right_normalized in left_normalized
    )


def _worksheet_by_name(path: Path, sheet_name: str) -> WorksheetData:
    for worksheet in read_xlsx(path):
        if worksheet.name == sheet_name:
            return worksheet
    raise ValueError(f"Worksheet {sheet_name!r} is missing from {path}")


def _rows_as_dicts(worksheet: WorksheetData) -> list[dict[str, Any]]:
    if not worksheet.rows:
        return []
    headers = [_clean_text(value) or "" for value in worksheet.rows[0]]
    return [
        {
            header: row[index] if index < len(row) else None
            for index, header in enumerate(headers)
            if header
        }
        for row in worksheet.rows[1:]
        if any(value is not None for value in row)
    ]


def _valid_http_url(value: Any) -> str | None:
    cleaned = _clean_text(value)
    if not cleaned:
        return None
    parsed = urlparse(cleaned)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return None
    return cleaned


def _linkedin_company_url(source_urls: Any) -> str | None:
    for value in str(source_urls or "").splitlines():
        url = _valid_http_url(value)
        if url and "linkedin.com/company/" in url.casefold():
            return url
    return None


def _software_values(value: Any) -> list[str]:
    text = _clean_text(value) or ""
    matches: list[str] = []
    patterns = {
        "Teamcenter": r"\bteamcenter\b",
        "NX": r"\b(?:siemens\s+)?nx\b",
        "Solid Edge": r"\bsolid\s+edge\b",
        "Polarion": r"\bpolarion\b",
        "Mendix": r"\bmendix\b",
        "Opcenter": r"\bopcenter\b",
        "Xcelerator": r"\bxcelerator\b|\bsiemens\s+plm\b",
    }
    for display_name, pattern in patterns.items():
        if re.search(pattern, text, flags=re.IGNORECASE):
            matches.append(display_name)
    return matches


def load_company_imports(members_path: Path, research_path: Path) -> list[CompanyImport]:
    member_rows = _rows_as_dicts(
        _worksheet_by_name(members_path, "Aero Montreal Members Directory")
    )
    member_websites = {
        _normalize_name(str(row["Name"])): _valid_http_url(row.get("Company Website"))
        for row in member_rows
        if _clean_text(row.get("Name"))
    }

    research_rows = _rows_as_dicts(
        _worksheet_by_name(research_path, "Company Research")
    )
    imports: list[CompanyImport] = []
    seen_names: set[str] = set()
    confidence_values = {"high": 0.9, "medium": 0.7, "low": 0.5}

    from enrichment.domain_resolution import canonicalize_domain

    for row in research_rows:
        company_name = _clean_text(row.get("Company"))
        if not company_name:
            continue
        normalized_name = _normalize_name(company_name)
        if normalized_name in seen_names:
            continue
        seen_names.add(normalized_name)

        qa_status = (_clean_text(row.get("Website QA")) or "").casefold()
        website = _valid_http_url(row.get("Resolved / Verified Website"))
        if not website:
            website = _valid_http_url(row.get("Provided Website"))
        if not website:
            website = member_websites.get(normalized_name)
        # Do not assign a domain that research explicitly identified as an
        # unrelated or mismatched organization.
        if "invalid/mismatched" in qa_status or "unrelated" in qa_status:
            website = None

        employee_count = _clean_text(row.get("Employees / Size"))
        if employee_count and employee_count.casefold().startswith("not found"):
            employee_count = None
        confidence_label = (_clean_text(row.get("Confidence")) or "").casefold()
        raw_priority_score = row.get("Priority Score")
        try:
            priority_score = int(raw_priority_score or 0)
        except (TypeError, ValueError):
            priority_score = 0
        domain = canonicalize_domain(website)

        imports.append(
            CompanyImport(
                company_name=company_name,
                company_url=website,
                company_domain=domain,
                linkedin_url=_linkedin_company_url(row.get("Source URLs")),
                organization_type=_clean_text(row.get("Organization Type")),
                employee_count=employee_count,
                software=_software_values(row.get("PLM / PDM Software")),
                confidence=confidence_values.get(confidence_label),
                priority_score=priority_score,
            )
        )
    return imports


def import_companies(
    companies: list[CompanyImport],
    *,
    apply: bool,
) -> dict[str, Any]:
    from dotenv import load_dotenv
    from sqlalchemy import select

    from db.database import CompanyRecord, Database

    load_dotenv()
    database = Database()
    now = datetime.now(timezone.utc)
    counts: dict[str, Any] = {
        "source_companies": len(companies),
        "inserted": 0,
        "updated": 0,
        "unchanged": 0,
        "domain_conflicts": 0,
        "missing_urls": 0,
        "inserted_names": [],
        "updated_names": [],
        "matched_pairs": [],
        "conflicts": [],
    }

    with database.session() as session:
        existing_records = list(
            session.scalars(select(CompanyRecord).order_by(CompanyRecord.id)).all()
        )
        by_name = {
            _normalize_name(record.company_name): record
            for record in existing_records
        }
        by_domain = {
            record.company_domain: record
            for record in existing_records
            if record.company_domain
        }
        claimed_record_ids: set[int] = set()

        for company in companies:
            if not company.company_url:
                counts["missing_urls"] += 1
            normalized_name = _normalize_name(company.company_name)
            record = by_name.get(normalized_name)
            match_type = "exact_name" if record is not None else None
            if record is None and company.company_domain:
                domain_record = by_domain.get(company.company_domain)
                if (
                    domain_record
                    and domain_record.id not in claimed_record_ids
                    and _safe_similar_name(
                    domain_record.company_name, company.company_name
                    )
                ):
                    record = domain_record
                    match_type = "domain"
            if record is None:
                record = next(
                    (
                        candidate
                        for candidate in existing_records
                        if candidate.id not in claimed_record_ids
                        if _safe_similar_name(
                            candidate.company_name, company.company_name
                        )
                    ),
                    None,
                )
                if record is not None:
                    match_type = "similar_name"

            domain_to_assign = company.company_domain
            if domain_to_assign:
                domain_owner = by_domain.get(domain_to_assign)
                if domain_owner is not None and (
                    record is None or domain_owner.id != record.id
                ):
                    counts["domain_conflicts"] += 1
                    counts["conflicts"].append(
                        {
                            "company": company.company_name,
                            "domain": domain_to_assign,
                            "owner": domain_owner.company_name,
                        }
                    )
                    domain_to_assign = None

            if record is None:
                record = CompanyRecord(
                    company_name=company.company_name,
                    company_domain=domain_to_assign,
                    company_url=company.company_url,
                    linkedin_url=company.linkedin_url,
                    location="Canada",
                    industry="Aerospace",
                    company_industry=company.organization_type,
                    sector=company.organization_type,
                    headquarters_location="Canada",
                    employee_count=company.employee_count,
                    revenue_range=None,
                    software=list(company.software),
                    signal_sources=["aero_montreal"],
                    signal_count=0,
                    migration_risk=False,
                    total_score=0,
                    lead_score="hot" if company.priority_score >= 5 else "warm",
                    contacts=[],
                    enrichment_source="aero_montreal_research",
                    enrichment_confidence=company.confidence,
                    enriched_at=now,
                    last_enrichment_at=now,
                    first_seen=now,
                    last_updated=now,
                )
                session.add(record)
                session.flush()
                existing_records.append(record)
                by_name[normalized_name] = record
                if domain_to_assign:
                    by_domain[domain_to_assign] = record
                claimed_record_ids.add(record.id)
                counts["inserted"] += 1
                counts["inserted_names"].append(company.company_name)
                continue

            claimed_record_ids.add(record.id)
            counts["matched_pairs"].append(
                {
                    "source": company.company_name,
                    "existing": record.company_name,
                    "match_type": match_type,
                }
            )
            changed = False
            updates = {
                "company_domain": domain_to_assign,
                "company_url": company.company_url,
                "linkedin_url": company.linkedin_url,
                "location": "Canada",
                "industry": "Aerospace",
                "company_industry": company.organization_type,
                "sector": company.organization_type,
                "headquarters_location": "Canada",
                "employee_count": company.employee_count,
                "enrichment_source": "aero_montreal_research",
                "enrichment_confidence": company.confidence,
                "enriched_at": now,
                "last_enrichment_at": now,
            }
            for field_name, value in updates.items():
                if value is not None and not getattr(record, field_name):
                    setattr(record, field_name, value)
                    changed = True

            current_sources = list(record.signal_sources or [])
            if "aero_montreal" not in current_sources:
                record.signal_sources = [*current_sources, "aero_montreal"]
                changed = True
            current_software = list(record.software or [])
            merged_software = list(
                dict.fromkeys([*current_software, *company.software])
            )
            if merged_software != current_software:
                record.software = merged_software
                changed = True
            desired_lead_score = (
                "hot" if company.priority_score >= 5 else "warm"
            )
            if record.lead_score == "cold":
                record.lead_score = desired_lead_score
                changed = True

            if changed:
                record.last_updated = now
                counts["updated"] += 1
                counts["updated_names"].append(record.company_name)
            else:
                counts["unchanged"] += 1

        if apply:
            session.commit()
        else:
            session.rollback()
    return counts


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Inspect and import Aero Montreal company workbooks."
    )
    parser.add_argument("members_workbook", type=Path)
    parser.add_argument("research_workbook", type=Path)
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Commit the import. Without this option, perform a dry run.",
    )
    parser.add_argument(
        "--inspect",
        action="store_true",
        help="Print workbook sheets and sample rows instead of importing.",
    )
    args = parser.parse_args()

    if args.inspect:
        for workbook_path in (args.members_workbook, args.research_workbook):
            print(f"WORKBOOK\t{workbook_path}")
            for worksheet in read_xlsx(workbook_path):
                width = max((len(row) for row in worksheet.rows), default=0)
                print(
                    f"SHEET\t{worksheet.name}\trows={len(worksheet.rows)}"
                    f"\tcolumns={width}\thyperlinks={len(worksheet.hyperlinks)}"
                )
                for row_number, row in enumerate(worksheet.rows[:8], start=1):
                    print(f"ROW {row_number}\t{row}")
        return 0

    companies = load_company_imports(
        args.members_workbook,
        args.research_workbook,
    )
    counts = import_companies(companies, apply=args.apply)
    print(
        "aero montreal import: "
        + ", ".join(
            f"{key}={value}"
            for key, value in counts.items()
            if key
            not in {"inserted_names", "updated_names", "matched_pairs", "conflicts"}
        )
    )
    for match in counts["matched_pairs"]:
        print(
            "existing match: "
            f"{match['source']} -> {match['existing']} ({match['match_type']})"
        )
    for conflict in counts["conflicts"]:
        print(
            "domain conflict: "
            f"{conflict['company']} domain={conflict['domain']} "
            f"existing_owner={conflict['owner']}"
        )
    if not args.apply:
        print("dry run only; use --apply to commit")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
