from __future__ import annotations

import math
import unittest

from extractors.nlp import (
    BaseExtractor,
    GeminiClientError,
    GeminiExtractor,
    _build_prompt,
    candidate_from_job_posting,
)
from models.schema import RawJobPosting


def _candidate(
    description: str,
    *,
    company_name: str = "Acme Manufacturing GmbH",
    company_url: str | None = "https://www.linkedin.com/company/acme-manufacturing",
    company_url_direct: str | None = "https://www.acme.example/careers",
    company_industry: str | None = "Motor Vehicle Manufacturing",
    query: str = "Teamcenter administrator",
    job_id: str = "1",
):
    posting = RawJobPosting(
        source="indeed",
        query=query,
        title="PLM Systems Engineer",
        company_name=company_name,
        company_url=company_url,
        company_url_direct=company_url_direct,
        company_industry=company_industry,
        location="Munich, Germany",
        description=description,
        job_url=f"https://jobs.example.test/{job_id}",
    )
    return candidate_from_job_posting(posting)


def _raw_item(**overrides):
    item = {
        "id": 1,
        "is_relevant": True,
        "company_name": "Incorrect Model Company",
        "location": "Munich, Germany",
        "industry": "Industrial Equipment",
        "software_detected": ["Teamcenter"],
        "software_evidence": [
            {
                "software": "Teamcenter",
                "quote": "administer and support Siemens Teamcenter",
            }
        ],
        "migration_detected": False,
        "migration_from": None,
        "migration_evidence": None,
        "pain_signals": [],
        "expansion_signals": [],
        "confidence": 0.91,
        "reasoning": "This unvalidated model explanation must not be persisted.",
    }
    item.update(overrides)
    return item


class EvidenceGroundingTests(unittest.TestCase):
    def setUp(self) -> None:
        self.extractor = BaseExtractor()

    def test_accepts_strong_exact_evidence_and_jobspy_domain(self) -> None:
        candidate = _candidate(
            "The end-user engineering team will administer and support Siemens "
            "Teamcenter for product releases and manufacturing change workflows."
        )

        signal, decision = self.extractor._post_process_item(candidate, _raw_item())

        self.assertEqual(decision, "accepted")
        self.assertIsNotNone(signal)
        assert signal is not None
        self.assertEqual(signal.company_name, "Acme Manufacturing GmbH")
        self.assertEqual(signal.company_industry, "Motor Vehicle Manufacturing")
        self.assertEqual(signal.company_domain, "acme.example")
        self.assertEqual(
            signal.company_url,
            "https://www.linkedin.com/company/acme-manufacturing",
        )
        self.assertEqual(signal.domain_resolution_source, "jobspy_company_url_direct")
        self.assertEqual(signal.domain_resolution_confidence, 1.0)
        self.assertEqual(
            signal.linkedin_url,
            "https://www.linkedin.com/company/acme-manufacturing",
        )
        self.assertIn("administer and support Siemens Teamcenter", signal.reason or "")
        self.assertNotIn("unvalidated model explanation", signal.reason or "")

    def test_excludes_configured_vendor_company(self) -> None:
        candidate = _candidate(
            "The team administers and supports Siemens Teamcenter.",
            company_name="OpenText",
        )

        signal, decision = self.extractor._post_process_item(candidate, _raw_item())

        self.assertIsNone(signal)
        self.assertEqual(decision, "excluded_or_missing_company")

    def test_fabricated_quote_is_rejected(self) -> None:
        candidate = _candidate(
            "The team will administer and support Siemens Teamcenter for engineering."
        )
        raw = _raw_item(
            software_evidence=[
                {
                    "software": "Teamcenter",
                    "quote": "migrating a global Teamcenter estate to production",
                }
            ]
        )

        signal, decision = self.extractor._post_process_item(candidate, raw)

        self.assertIsNone(signal)
        self.assertEqual(decision, "no_grounded_software")

    def test_one_products_quote_cannot_validate_another_product(self) -> None:
        candidate = _candidate(
            "The role will administer and support Siemens Teamcenter. A separate design "
            "group creates production models with Siemens NX CAD."
        )
        raw = _raw_item(
            software_detected=["NX"],
            software_evidence=[
                {
                    "software": "NX",
                    "quote": "administer and support Siemens Teamcenter",
                }
            ],
        )

        signal, decision = self.extractor._post_process_item(candidate, raw)

        self.assertIsNone(signal)
        self.assertEqual(decision, "no_grounded_software")

    def test_non_boolean_relevance_and_invalid_confidence_are_rejected(self) -> None:
        candidate = _candidate(
            "The role will administer and support Siemens Teamcenter for engineering."
        )
        cases = (
            (_raw_item(is_relevant="true"), "model_marked_irrelevant"),
            (_raw_item(confidence="0.95"), "low_confidence"),
            (_raw_item(confidence=math.nan), "low_confidence"),
            (_raw_item(confidence=1.1), "low_confidence"),
        )

        for raw, expected_decision in cases:
            with self.subTest(raw=raw):
                signal, decision = self.extractor._post_process_item(candidate, raw)
                self.assertIsNone(signal)
                self.assertEqual(decision, expected_decision)

    def test_consultancy_is_rejected_even_with_exact_product_evidence(self) -> None:
        candidate = _candidate(
            "Consultants administer and support Siemens Teamcenter for external client projects.",
            company_name="Example Technology Consulting GmbH",
        )

        signal, decision = self.extractor._post_process_item(candidate, _raw_item())

        self.assertIsNone(signal)
        self.assertEqual(decision, "consulting_company")

    def test_excluded_sector_classified_from_stepstone_or_news_is_rejected(self) -> None:
        candidate = _candidate(
            "The bank will administer and support Siemens Teamcenter for engineering.",
        )

        signal, decision = self.extractor._post_process_item(
            candidate,
            _raw_item(industry="Banking & Financial Services"),
        )

        self.assertIsNone(signal)
        self.assertEqual(decision, "excluded_industry")

    def test_company_url_fallback_prevents_external_domain_resolution(self) -> None:
        candidate = _candidate(
            "The role will administer and support Siemens Teamcenter for engineering.",
            company_url="https://de.indeed.com/cmp/acme",
            company_url_direct=None,
        )

        signal, decision = self.extractor._post_process_item(candidate, _raw_item())

        self.assertEqual(decision, "accepted")
        assert signal is not None
        self.assertEqual(signal.company_domain, "de.indeed.com")
        self.assertEqual(signal.domain_resolution_source, "jobspy_company_url")
        self.assertEqual(signal.domain_resolution_confidence, 1.0)

    def test_job_board_direct_url_is_not_treated_as_employer_website(self) -> None:
        candidate = _candidate(
            "The role will administer and support Siemens Teamcenter for engineering.",
            company_url=None,
            company_url_direct="https://de.indeed.com/cmp/acme",
        )

        signal, decision = self.extractor._post_process_item(candidate, _raw_item())

        self.assertEqual(decision, "accepted")
        assert signal is not None
        self.assertIsNone(signal.company_domain)
        self.assertIsNone(signal.domain_resolution_source)


class BatchContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.extractor = BaseExtractor()
        self.batch = [
            _candidate(
                "The role will administer and support Siemens Teamcenter for engineering.",
                job_id=str(index),
            )
            for index in (1, 2)
        ]

    def test_reversed_ids_are_paired_by_id_not_position(self) -> None:
        raw_items = [{"id": 2, "marker": "second"}, {"id": 1, "marker": "first"}]

        paired = self.extractor._pair_batch_items(self.batch, raw_items)

        self.assertIs(paired[0][0], self.batch[0])
        self.assertEqual(paired[0][1]["marker"], "first")
        self.assertIs(paired[1][0], self.batch[1])
        self.assertEqual(paired[1][1]["marker"], "second")

    def test_duplicate_missing_non_integer_and_out_of_range_ids_fail(self) -> None:
        invalid_sets = (
            [{"id": 1}, {"id": 1}],
            [{"id": 1}],
            [{"id": 1}, {"id": "2"}],
            [{"id": 1}, {"id": True}],
            [{"id": 1}, {"id": 3}],
        )

        for raw_items in invalid_sets:
            with self.subTest(raw_items=raw_items):
                with self.assertRaises(GeminiClientError):
                    self.extractor._pair_batch_items(self.batch, raw_items)

    def test_contract_violation_retries_once(self) -> None:
        class RetryExtractor(BaseExtractor):
            def __init__(self) -> None:
                self.calls = 0

            def _generate_batch_text(self, batch, single_item_retry=False):
                self.calls += 1
                if self.calls == 1:
                    return '[{"id":1},{"id":1}]'
                return '[{"id":2},{"id":1}]'

        extractor = RetryExtractor()

        items = extractor._request_batch_items(self.batch)

        self.assertEqual(extractor.calls, 2)
        self.assertEqual([item["id"] for item in items], [2, 1])


class ModelPayloadTests(unittest.TestCase):
    def test_prompt_omits_retrieval_anchors_and_payload_uses_prompt_json(self) -> None:
        candidate = _candidate(
            "The role will administer and support Siemens Teamcenter for engineering.",
            query="secret retrieval phrase Teamcenter",
        )
        prompt = _build_prompt([candidate])

        self.assertNotIn("secret retrieval phrase", prompt)
        self.assertNotIn("retrieval_query", prompt)
        self.assertNotIn("prefilter_products", prompt)
        self.assertIn("software_evidence", prompt)

        extractor = GeminiExtractor(api_key="test-key", batch_size=1)
        try:
            payload = extractor._build_payload([candidate])
        finally:
            extractor.close()

        config = payload["generationConfig"]
        self.assertEqual(config["temperature"], 0.1)
        self.assertGreaterEqual(config["maxOutputTokens"], 8192)
        self.assertNotIn("responseMimeType", config)
        self.assertNotIn("responseJsonSchema", config)
        self.assertNotIn("thinkingConfig", config)


if __name__ == "__main__":
    unittest.main()
