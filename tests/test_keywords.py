from datetime import datetime, timezone

from db.database import CompanyRecord, KeywordRecord, _names_similar, init_database


def test_all_keywords_remain_available_after_each_search() -> None:
    database = init_database("sqlite+pysqlite:///:memory:")
    with database.session() as session, session.begin():
        session.add_all(
            [
                KeywordRecord(
                    keyword="aerospace startups in Canada",
                    google_xray_enabled=True,
                ),
                KeywordRecord(keyword="robotics companies in Germany"),
            ]
        )

    keywords = database.list_keywords()

    assert [item.keyword for item in keywords] == [
        "aerospace startups in Canada",
        "robotics companies in Germany",
    ]
    assert keywords[0].google_xray_enabled is True
    assert keywords[1].google_xray_enabled is False

    searched = database.record_keyword_search(keywords[0].id, result_count=12)

    assert searched is not None
    assert searched.search_count == 1
    assert searched.last_result_count == 12
    assert searched.last_searched_at is not None
    assert len(database.list_keywords()) == 2


def test_keyword_search_error_does_not_remove_the_keyword() -> None:
    database = init_database("sqlite+pysqlite:///:memory:")
    with database.session() as session, session.begin():
        session.add(KeywordRecord(keyword="battery manufacturers in Sweden"))

    keyword = database.list_keywords()[0]
    searched = database.record_keyword_search(keyword.id, error="Browser session unavailable")

    assert searched is not None
    assert searched.search_count == 1
    assert searched.last_error == "Browser session unavailable"
    assert database.list_keywords()[0].keyword == "battery manufacturers in Sweden"


def test_keyword_company_ledger_only_contains_explicitly_attributed_companies() -> None:
    database = init_database("sqlite+pysqlite:///:memory:")
    with database.session() as session, session.begin():
        session.add(KeywordRecord(keyword="robotics startups in Canada"))
        session.add_all(
            [
                CompanyRecord(company_name="Codex Robotics", company_domain="codexrobotics.ca"),
                CompanyRecord(company_name="Ordinary Pipeline Company"),
            ]
        )

    keyword = database.list_keywords()[0]
    first = database.record_keyword_company(
        keyword.id,
        "Codex Robotics",
        "codexrobotics.ca",
        source_url="https://codexrobotics.ca/",
    )
    second = database.record_keyword_company(
        keyword.id,
        "Codex Robotics",
        "codexrobotics.ca",
        source_url="https://codexrobotics.ca/about",
    )

    assert first is not None
    assert second is not None
    assert second.times_seen == 2
    results = database.list_keyword_companies()
    assert [item.company_name for item in results] == ["Codex Robotics"]
    assert results[0].keyword == "robotics startups in Canada"
    assert results[0].source_url == "https://codexrobotics.ca/about"


def test_keyword_company_qualification_brief_is_persisted_and_retained() -> None:
    database = init_database("sqlite+pysqlite:///:memory:")
    with database.session() as session, session.begin():
        session.add(KeywordRecord(keyword="aerospace manufacturers in Canada"))
        session.add(
            CompanyRecord(
                company_name="Northstar Aerospace",
                company_domain="northstar.example",
            )
        )

    keyword = database.list_keywords()[0]
    signal_date = datetime(2026, 7, 21, tzinfo=timezone.utc)
    qualified = database.record_keyword_company(
        keyword.id,
        "Northstar Aerospace",
        "northstar.example",
        source_url="https://news.example/northstar-expansion",
        source_title="Northstar opens a new composite manufacturing line",
        source_publisher="Manufacturing News",
        signal_label="New composite manufacturing line",
        signal_date=signal_date,
        challenge_summary="Scaling engineering change control across a new production line.",
        why_relevant=(
            "Teamcenter can govern product and process revisions while Tecnomatix validates "
            "the expanded factory flow."
        ),
        recommended_products=["Teamcenter", "Tecnomatix", "NX"],
        qualification_status="qualified",
        opportunity_score=86,
        manufacturing_fit_score=95,
        trigger_score=85,
        solution_fit_score=90,
        evidence_quality_score=80,
    )

    assert qualified is not None
    assert qualified.qualification_status == "qualified"
    assert qualified.opportunity_score == 86
    assert qualified.signal_date == signal_date
    assert qualified.recommended_products == ["Teamcenter", "Tecnomatix", "NX"]
    assert qualified.qualified_at is not None

    seen_again = database.record_keyword_company(
        keyword.id,
        "Northstar Aerospace",
        "northstar.example",
        source_url="https://northstar.example/",
    )

    assert seen_again is not None
    assert seen_again.times_seen == 2
    assert seen_again.qualification_status == "qualified"
    assert seen_again.opportunity_score == 86
    assert seen_again.source_url == "https://news.example/northstar-expansion"
    assert seen_again.challenge_summary == (
        "Scaling engineering change control across a new production line."
    )
    assert seen_again.recommended_products == ["Teamcenter", "Tecnomatix", "NX"]


def test_qualified_keyword_leads_exclude_unqualified_and_enriched_companies() -> None:
    database = init_database("sqlite+pysqlite:///:memory:")
    enriched_at = datetime(2026, 7, 28, tzinfo=timezone.utc)
    with database.session() as session, session.begin():
        session.add(KeywordRecord(keyword="Canadian advanced manufacturers"))
        session.add_all(
            [
                CompanyRecord(company_name="Qualified Cold Company", lead_score="cold"),
                CompanyRecord(
                    company_name="Already Enriched Company",
                    lead_score="hot",
                    last_enrichment_at=enriched_at,
                ),
                CompanyRecord(company_name="Needs Review Company", lead_score="hot"),
            ]
        )

    keyword = database.list_keywords()[0]
    database.record_keyword_company(
        keyword.id,
        "Qualified Cold Company",
        qualification_status="qualified",
        opportunity_score=80,
    )
    database.record_keyword_company(
        keyword.id,
        "Already Enriched Company",
        qualification_status="qualified",
        opportunity_score=90,
    )
    database.record_keyword_company(
        keyword.id,
        "Needs Review Company",
        qualification_status="needs_review",
        opportunity_score=40,
    )

    unenriched = database.get_qualified_keyword_leads()
    all_qualified = database.get_qualified_keyword_leads(only_unenriched=False)

    assert [lead.company_name for lead in unenriched] == ["Qualified Cold Company"]
    assert {lead.company_name for lead in all_qualified} == {
        "Qualified Cold Company",
        "Already Enriched Company",
    }


def test_short_brand_names_are_not_merged_by_shared_industry_descriptor() -> None:
    assert _names_similar("ABCO Industries", "Ebco Industries Ltd.") is False


def test_short_aerospace_brands_are_not_merged() -> None:
    assert _names_similar("PAL Aerospace", "GAL Aerospace") is False


def test_acquired_brand_is_not_merged_into_parent_name_without_identity_evidence() -> None:
    assert _names_similar("Creaform - Ametek", "AMETEK") is False


def test_brand_name_can_match_a_contextual_industry_suffix() -> None:
    assert _names_similar("Wyvern", "Wyvern Space") is True


def test_legal_suffix_variants_still_match() -> None:
    assert _names_similar("GHGSat", "GHGSat Inc.") is True
