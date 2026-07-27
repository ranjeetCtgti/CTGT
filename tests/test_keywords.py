from db.database import KeywordRecord, _names_similar, init_database


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


def test_short_brand_names_are_not_merged_by_shared_industry_descriptor() -> None:
    assert _names_similar("ABCO Industries", "Ebco Industries Ltd.") is False


def test_legal_suffix_variants_still_match() -> None:
    assert _names_similar("GHGSat", "GHGSat Inc.") is True
