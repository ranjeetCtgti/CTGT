from datetime import datetime, timezone
import unittest

from enrichment.identity_verification import (
    CompanyIdentityEvidence,
    IdentityVerificationError,
    verify_company_identity,
)
from models.schema import ExtractedSignal


def _signal(**updates: object) -> ExtractedSignal:
    values = {
        "company_name": "Evio",
        "company_domain": "evio.aero",
        "company_url": "https://evio.aero/",
        "linkedin_url": "https://www.linkedin.com/company/evio-aircraft",
        "signal_type": "news",
        "signal_source": "news",
        "source_url": "https://example.com/evio-investment",
        "detected_at": datetime.now(timezone.utc),
    }
    values.update(updates)
    return ExtractedSignal(**values)


def _evidence(**updates: object) -> CompanyIdentityEvidence:
    values = {
        "official_name": "EVIO, Inc.",
        "official_website_url": "https://evio.aero/",
        "corroborating_urls": ("https://example.com/evio-investment",),
        "linkedin_url": "https://www.linkedin.com/company/evio-aircraft",
        "linkedin_website_url": "https://evio.aero/",
    }
    values.update(updates)
    return CompanyIdentityEvidence(**values)


class IdentityVerificationTests(unittest.TestCase):
    def test_accepts_consistent_official_and_linkedin_domains(self) -> None:
        identity = verify_company_identity(_signal(), _evidence())
        self.assertEqual(identity.company_domain, "evio.aero")
        self.assertEqual(identity.company_url, "https://evio.aero/")
        self.assertEqual(
            identity.linkedin_url,
            "https://www.linkedin.com/company/evio-aircraft",
        )

    def test_rejects_wrong_candidate_domain(self) -> None:
        with self.assertRaisesRegex(IdentityVerificationError, "conflicts with official domain"):
            verify_company_identity(
                _signal(company_domain="evio.ca", company_url="https://evio.ca/"),
                _evidence(),
            )

    def test_rejects_linkedin_page_for_another_company(self) -> None:
        with self.assertRaisesRegex(IdentityVerificationError, "LinkedIn website domain"):
            verify_company_identity(
                _signal(linkedin_url="https://www.linkedin.com/company/evio-pvt-ltd"),
                _evidence(
                    linkedin_url="https://www.linkedin.com/company/evio-pvt-ltd",
                    linkedin_website_url="https://www.evioglobal.com/",
                ),
            )

    def test_requires_independent_corroboration(self) -> None:
        with self.assertRaisesRegex(IdentityVerificationError, "outside the official"):
            verify_company_identity(
                _signal(),
                _evidence(corroborating_urls=("https://evio.aero/company/",)),
            )


if __name__ == "__main__":
    unittest.main()
