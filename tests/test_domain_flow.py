from __future__ import annotations

import os
import unittest
from contextlib import contextmanager
from types import SimpleNamespace
from unittest.mock import patch

import enrichment
from db.database import Database
from models.schema import ExtractedSignal
from pipeline import (
    JOBSPY_COMPANY_DOMAIN_SOURCE,
    JOBSPY_COMPANY_URL_DOMAIN_SOURCE,
    PipelineSummary,
    _propagate_trusted_jobspy_domains,
    resolve_signal_domains,
)


def _signal(
    company_name: str,
    source_url: str,
    *,
    company_domain: str | None = None,
    domain_source: str | None = None,
    company_url: str | None = None,
    linkedin_url: str | None = None,
    company_industry: str | None = None,
) -> ExtractedSignal:
    return ExtractedSignal(
        company_name=company_name,
        company_domain=company_domain,
        company_url=company_url,
        linkedin_url=linkedin_url,
        company_industry=company_industry,
        software=["Teamcenter"],
        signal_type="job_posting",
        signal_source="indeed",
        raw_score=10,
        confidence=1.0,
        domain_resolution_source=domain_source,
        domain_resolution_confidence=1.0 if domain_source else None,
        source_url=source_url,
    )


class DomainPropagationTests(unittest.TestCase):
    def test_company_url_domain_skips_fallback_resolver(self) -> None:
        signal = _signal(
            "Acme GmbH",
            "https://jobs.example/profile-domain",
            company_domain="linkedin.com",
            domain_source=JOBSPY_COMPANY_URL_DOMAIN_SOURCE,
            company_url="https://www.linkedin.com/company/acme",
        )
        summary = PipelineSummary()

        with patch.object(enrichment, "build_domain_resolver") as build_resolver:
            resolve_signal_domains([signal], summary, database=None)

        build_resolver.assert_not_called()
        self.assertEqual(signal.company_domain, "linkedin.com")
        self.assertEqual(summary.domain_resolution.companies_considered, 0)

    def test_unique_jobspy_domain_propagates_to_unresolved_same_company(self) -> None:
        direct = _signal(
            "Acme GmbH",
            "https://jobs.example/1",
            company_domain="www.acme.example",
            domain_source=JOBSPY_COMPANY_DOMAIN_SOURCE,
        )
        unresolved = _signal("Acme", "https://jobs.example/2")
        summary = PipelineSummary()

        _propagate_trusted_jobspy_domains([direct, unresolved], summary)

        self.assertEqual(unresolved.company_domain, "acme.example")
        self.assertEqual(
            unresolved.domain_resolution_source,
            JOBSPY_COMPANY_DOMAIN_SOURCE,
        )
        self.assertEqual(unresolved.domain_resolution_confidence, 1.0)
        self.assertEqual(summary.domain_resolution.conflicts, 0)

    def test_conflicting_jobspy_domains_are_not_propagated(self) -> None:
        first = _signal(
            "Acme",
            "https://jobs.example/1",
            company_domain="acme-one.example",
            domain_source=JOBSPY_COMPANY_DOMAIN_SOURCE,
        )
        second = _signal(
            "Acme GmbH",
            "https://jobs.example/2",
            company_domain="acme-two.example",
            domain_source=JOBSPY_COMPANY_DOMAIN_SOURCE,
        )
        unresolved = _signal("Acme AG", "https://jobs.example/3")
        summary = PipelineSummary()

        _propagate_trusted_jobspy_domains([first, second, unresolved], summary)

        self.assertIsNone(unresolved.company_domain)
        self.assertEqual(summary.domain_resolution.conflicts, 1)

    def test_cold_signal_still_uses_fallback_resolver(self) -> None:
        unresolved = _signal("Cold Acme", "https://jobs.example/cold")
        calls: list[str] = []

        class Resolver:
            def resolve(self, company_name: str, **_: object) -> SimpleNamespace:
                calls.append(company_name)
                return SimpleNamespace(
                    company_domain="cold-acme.example",
                    confidence=0.9,
                    source="serper",
                    reason="test result",
                )

        @contextmanager
        def build_resolver():
            yield Resolver()

        summary = PipelineSummary()
        with patch.dict(os.environ, {"ENRICHMENT_ENABLED": "true"}), patch.object(
            enrichment,
            "build_domain_resolver",
            build_resolver,
        ):
            resolve_signal_domains([unresolved], summary, database=None)

        self.assertEqual(calls, ["Cold Acme"])
        self.assertEqual(unresolved.company_domain, "cold-acme.example")
        self.assertEqual(summary.domain_resolution.attempted, 1)
        self.assertEqual(summary.domain_resolution.resolved, 1)


class JobSpyDomainPersistenceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.database = Database("sqlite+pysqlite:///:memory:")
        self.database.initialize()

    def test_jobspy_replaces_resolver_domain_and_persists_linkedin(self) -> None:
        self.database.upsert_company(
            _signal(
                "Acme GmbH",
                "https://jobs.example/old",
                company_domain="wrong.example",
                domain_source="serper",
            )
        )

        jobspy_signal = _signal(
            "Acme GmbH",
            "https://jobs.example/new",
            company_domain="right.example",
            domain_source=JOBSPY_COMPANY_DOMAIN_SOURCE,
            company_url="https://www.linkedin.com/company/acme",
            linkedin_url="https://www.linkedin.com/company/acme",
            company_industry="Motor Vehicle Manufacturing",
        )
        self.database.save_signal(jobspy_signal)
        lead = self.database.upsert_company(jobspy_signal)

        self.assertEqual(lead.company_domain, "right.example")
        self.assertEqual(lead.company_url, "https://www.linkedin.com/company/acme")
        self.assertEqual(lead.enrichment_source, JOBSPY_COMPANY_DOMAIN_SOURCE)
        self.assertEqual(lead.linkedin_url, "https://www.linkedin.com/company/acme")
        self.assertEqual(lead.company_industry, "Motor Vehicle Manufacturing")
        saved_signal = self.database.get_signals(limit=1)[0]
        self.assertEqual(
            saved_signal.company_url,
            "https://www.linkedin.com/company/acme",
        )
        self.assertEqual(saved_signal.company_industry, "Motor Vehicle Manufacturing")

    def test_company_url_fallback_domain_is_persisted(self) -> None:
        signal = _signal(
            "Profile-only Acme",
            "https://jobs.example/profile-only",
            company_domain="linkedin.com",
            domain_source=JOBSPY_COMPANY_URL_DOMAIN_SOURCE,
            company_url="https://www.linkedin.com/company/profile-only-acme",
            linkedin_url="https://www.linkedin.com/company/profile-only-acme",
        )

        self.database.save_signal(signal)
        lead = self.database.upsert_company(signal)

        self.assertEqual(lead.company_domain, "linkedin.com")
        self.assertEqual(
            lead.company_url,
            "https://www.linkedin.com/company/profile-only-acme",
        )
        self.assertEqual(lead.enrichment_source, JOBSPY_COMPANY_URL_DOMAIN_SOURCE)

    def test_duplicate_jobspy_signal_backfills_company_industry(self) -> None:
        original = _signal(
            "Industry Backfill GmbH",
            "https://jobs.example/industry-backfill",
        )
        self.database.save_signal(original)
        self.database.upsert_company(original)

        enriched_duplicate = _signal(
            "Industry Backfill GmbH",
            "https://jobs.example/industry-backfill",
            company_industry="Industrial Machinery Manufacturing",
        )
        result = self.database.save_signal(enriched_duplicate)
        self.database.update_company_industry(enriched_duplicate)

        self.assertFalse(result.created)
        saved_signal = self.database.get_signals(limit=1)[0]
        saved_company = self.database.get_leads(limit=1)[0]
        self.assertEqual(
            saved_signal.company_industry,
            "Industrial Machinery Manufacturing",
        )
        self.assertEqual(
            saved_company.company_industry,
            "Industrial Machinery Manufacturing",
        )

    def test_jobspy_replaces_legacy_and_company_name_guesses(self) -> None:
        cases = (
            ("Legacy Acme", "legacy-acme", None),
            ("Historic Widgets", "historic-widgets", "company_name_domain"),
        )
        for company_name, slug, old_source in cases:
            with self.subTest(old_source=old_source):
                self.database.upsert_company(
                    _signal(
                        company_name,
                        f"https://jobs.example/{slug}-legacy",
                        company_domain=f"{slug}-legacy.example",
                        domain_source=old_source,
                    )
                )

                lead = self.database.upsert_company(
                    _signal(
                        company_name,
                        f"https://jobs.example/{slug}-direct",
                        company_domain=f"{slug}-direct.example",
                        domain_source=JOBSPY_COMPANY_DOMAIN_SOURCE,
                    )
                )

                self.assertEqual(lead.company_domain, f"{slug}-direct.example")
                self.assertEqual(
                    lead.enrichment_source,
                    JOBSPY_COMPANY_DOMAIN_SOURCE,
                )

    def test_jobspy_does_not_take_domain_owned_by_another_company(self) -> None:
        self.database.upsert_company(
            _signal(
                "Acme GmbH",
                "https://jobs.example/acme-old",
                company_domain="acme.example",
                domain_source="serper",
            )
        )
        self.database.upsert_company(
            _signal(
                "Other Corporation",
                "https://jobs.example/other",
                company_domain="claimed.example",
                domain_source=JOBSPY_COMPANY_DOMAIN_SOURCE,
            )
        )

        lead = self.database.upsert_company(
            _signal(
                "Acme GmbH",
                "https://jobs.example/acme-new",
                company_domain="claimed.example",
                domain_source=JOBSPY_COMPANY_DOMAIN_SOURCE,
            )
        )

        self.assertEqual(lead.company_name, "Acme GmbH")
        self.assertEqual(lead.company_domain, "acme.example")
        owner = self.database.find_company_by_domain("claimed.example")
        self.assertIsNotNone(owner)
        self.assertEqual(owner.company_name, "Other Corporation")


if __name__ == "__main__":
    unittest.main()
