from __future__ import annotations

import unittest

from extractors.nlp import candidate_from_job_posting
from extractors.prefilter import keyword_prefilter
from models.schema import RawJobPosting
from industry_filter import matching_excluded_industry
from scrapers.jobspy_adapter import _normalize_row


class JobSpyNormalizationTests(unittest.TestCase):
    def test_excludes_jobspy_service_sector_company_industry(self) -> None:
        posting = _normalize_row(
            {
                "site": "linkedin",
                "title": "Teamcenter Consultant",
                "company": "Example Consulting",
                "company_industry": "IT Services and IT Consulting",
                "job_url": "https://www.linkedin.com/jobs/view/456",
                "description": "Implement Teamcenter for clients.",
            },
            source="linkedin",
            query="Teamcenter",
            fallback_location="Germany",
        )

        self.assertIsNone(posting)

    def test_keeps_manufacturing_company_industry(self) -> None:
        posting = _normalize_row(
            {
                "site": "linkedin",
                "title": "Teamcenter Administrator",
                "company": "Example Manufacturer",
                "company_industry": "Motor Vehicle Manufacturing",
                "job_url": "https://www.linkedin.com/jobs/view/789",
                "description": "Administer Teamcenter for internal engineering teams.",
            },
            source="linkedin",
            query="Teamcenter",
            fallback_location="Germany",
        )

        self.assertIsNotNone(posting)
        self.assertEqual(posting.company_industry, "Motor Vehicle Manufacturing")

    def test_industry_exclusion_is_case_insensitive_and_matches_specific_labels(self) -> None:
        self.assertEqual(
            matching_excluded_industry("Staffing and Recruiting"),
            "staffing",
        )
        self.assertEqual(
            matching_excluded_industry("PRIMARY AND SECONDARY EDUCATION"),
            "education",
        )
        self.assertIsNone(matching_excluded_industry("Aviation and Aerospace Component Manufacturing"))

    def test_preserves_company_profile_and_direct_company_url(self) -> None:
        posting = _normalize_row(
            {
                "site": "indeed",
                "title": "PLM Engineer",
                "company": "Example Manufacturing GmbH",
                "company_url": "https://de.indeed.com/cmp/Example-Manufacturing",
                "company_url_direct": "https://www.example-manufacturing.de/careers",
                "location": "Munich, Germany",
                "job_url": "https://de.indeed.com/viewjob?jk=123",
                "job_url_direct": "https://jobs.example-manufacturing.de/jobs/123",
                "date_posted": "2026-07-20",
                "description": "Maintain the product lifecycle management environment.",
            },
            source="indeed",
            query="PLM Engineer",
            fallback_location="Germany",
        )

        self.assertIsNotNone(posting)
        assert posting is not None
        self.assertEqual(
            posting.company_url,
            "https://de.indeed.com/cmp/Example-Manufacturing",
        )
        self.assertEqual(
            posting.company_url_direct,
            "https://www.example-manufacturing.de/careers",
        )

    def test_keeps_linkedin_profile_without_inventing_a_direct_url(self) -> None:
        posting = _normalize_row(
            {
                "site": "linkedin",
                "title": "Mechanical Engineer",
                "company": "Example Industries",
                "company_url": "https://www.linkedin.com/company/example-industries",
                "company_url_direct": None,
                "location": "Berlin, Germany",
                "job_url": "https://www.linkedin.com/jobs/view/123",
                "description": "Design mechanical assemblies for industrial equipment.",
            },
            source="linkedin",
            query="Mechanical Engineer",
            fallback_location="Germany",
        )

        self.assertIsNotNone(posting)
        assert posting is not None
        self.assertEqual(
            posting.company_url,
            "https://www.linkedin.com/company/example-industries",
        )
        self.assertIsNone(posting.company_url_direct)


class PrefilterBoundaryTests(unittest.TestCase):
    def test_tc_alias_does_not_match_inside_ordinary_words(self) -> None:
        false_positive_words = (
            "batch",
            "catch",
            "dispatch",
            "match",
            "patch",
            "scratch",
            "watch",
        )

        for word in false_positive_words:
            with self.subTest(word=word):
                result = keyword_prefilter(
                    f"The role will {word} records and maintain reliable business workflows "
                    "for a large manufacturing organization across several locations."
                )
                self.assertNotIn("Teamcenter", result.matched_products)
                self.assertFalse(result.passed)

    def test_accepts_explicit_teamcenter_and_bounded_tc_mentions(self) -> None:
        examples = (
            "The engineering team uses Teamcenter to manage product structures, releases, "
            "and manufacturing change workflows across the enterprise.",
            "The role owns TC administration, user access, workflow configuration, and "
            "production support for the manufacturer's PLM environment.",
        )

        for text in examples:
            with self.subTest(text=text):
                result = keyword_prefilter(text)
                self.assertIn("Teamcenter", result.matched_products)
                self.assertTrue(result.passed)

    def test_accepts_explicit_nx_but_not_nx_inside_a_word(self) -> None:
        positive = keyword_prefilter(
            "Mechanical engineers use Siemens NX for production CAD models, assemblies, "
            "drawings, and release activities at the manufacturing plant."
        )
        negative = keyword_prefilter(
            "The Linux platform supports analytics and ordinary business applications "
            "for teams distributed across multiple offices."
        )

        self.assertIn("NX", positive.matched_products)
        self.assertTrue(positive.passed)
        self.assertNotIn("NX", negative.matched_products)
        self.assertFalse(negative.passed)


class CandidateEvidenceIsolationTests(unittest.TestCase):
    def test_retrieval_query_company_and_location_do_not_trigger_prefilter(self) -> None:
        metadata_cases = (
            {
                "query": "Teamcenter administrator",
                "company_name": "Example Manufacturing",
                "location": "Berlin, Germany",
            },
            {
                "query": "PLM administrator",
                "company_name": "NX Manufacturing",
                "location": "Berlin, Germany",
            },
            {
                "query": "PLM administrator",
                "company_name": "Example Manufacturing",
                "location": "Teamcenter Campus, Germany",
            },
        )

        for metadata in metadata_cases:
            with self.subTest(metadata=metadata):
                posting = RawJobPosting(
                    source="indeed",
                    title="Business Systems Administrator",
                    description=(
                        "Maintain internal business applications, manage user access, "
                        "document routine procedures, and support employees across the organization."
                    ),
                    job_url="https://example.test/jobs/123",
                    **metadata,
                )
                candidate = candidate_from_job_posting(posting)

                self.assertIsNotNone(candidate.prefilter)
                assert candidate.prefilter is not None
                self.assertEqual(candidate.prefilter.matched_products, {})
                self.assertFalse(candidate.prefilter.passed)


if __name__ == "__main__":
    unittest.main()
