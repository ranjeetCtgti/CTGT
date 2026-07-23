from __future__ import annotations

import unittest

from db.database import Database
from pipeline_config import (
    PipelineLocation,
    PipelineQuery,
    PipelineSearchConfig,
    build_jobspy_search_plan,
    build_stepstone_search_plan,
    set_runtime_search_config,
)


class PipelineConfigPlanTests(unittest.TestCase):
    def tearDown(self) -> None:
        set_runtime_search_config(None)

    def test_jobspy_plan_matches_source_and_locale(self) -> None:
        set_runtime_search_config(
            PipelineSearchConfig(
                queries=(
                    PipelineQuery("English query", "en", ("linkedin", "google")),
                    PipelineQuery("German query", "de", ("linkedin",)),
                    PipelineQuery("Indeed only", "en", ("indeed",)),
                ),
                locations=(
                    PipelineLocation("Canada", "en", ("linkedin", "indeed")),
                    PipelineLocation("Germany", "de", ("linkedin",)),
                ),
            )
        )

        self.assertEqual(
            build_jobspy_search_plan("linkedin"),
            [("English query", "Canada"), ("German query", "Germany")],
        )
        self.assertEqual(
            build_jobspy_search_plan("indeed"),
            [("Indeed only", "Canada")],
        )
        self.assertEqual(build_jobspy_search_plan("google"), [])

    def test_stepstone_requires_a_matching_configured_location(self) -> None:
        query = PipelineQuery("Stepstone query", "de", ("stepstone",))
        set_runtime_search_config(
            PipelineSearchConfig(
                queries=(query,),
                locations=(),
            )
        )
        self.assertEqual(build_stepstone_search_plan(), [])

        set_runtime_search_config(
            PipelineSearchConfig(
                queries=(query,),
                locations=(PipelineLocation("Germany", "de", ("stepstone",)),),
            )
        )
        self.assertEqual(build_stepstone_search_plan(), ["Stepstone query"])

    def test_query_limit_applies_after_dynamic_plan_is_built(self) -> None:
        set_runtime_search_config(
            PipelineSearchConfig(
                queries=(
                    PipelineQuery("One", "en", ("linkedin",)),
                    PipelineQuery("Two", "en", ("linkedin",)),
                ),
                locations=(PipelineLocation("Canada", "en", ("linkedin",)),),
            )
        )

        self.assertEqual(build_jobspy_search_plan("linkedin", max_queries=1), [("One", "Canada")])

    def test_database_seeds_defaults_once_and_respects_later_deletions(self) -> None:
        database = Database("sqlite:///:memory:")
        database.initialize()
        seeded = database.get_pipeline_search_config()
        self.assertGreater(len(seeded.queries), 0)
        self.assertGreater(len(seeded.locations), 0)

        with database.engine.begin() as connection:
            connection.exec_driver_sql("DELETE FROM pipeline_queries")

        database.initialize()
        restarted = database.get_pipeline_search_config()
        self.assertEqual(restarted.queries, ())
        self.assertEqual(restarted.locations, seeded.locations)
        database.engine.dispose()


if __name__ == "__main__":
    unittest.main()
