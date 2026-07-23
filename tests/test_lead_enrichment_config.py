from __future__ import annotations

import os
import unittest
from unittest.mock import patch

from enrichment.lead_enrichment import _build_apollo_client


class ApolloConfigurationTests(unittest.TestCase):
    def test_api_key_alone_does_not_enable_apollo(self) -> None:
        with patch.dict(
            os.environ,
            {"APOLLO_API_KEY": "configured-key"},
            clear=True,
        ):
            self.assertIsNone(_build_apollo_client(timeout_seconds=1))

    def test_explicit_false_disables_apollo(self) -> None:
        with patch.dict(
            os.environ,
            {
                "APOLLO_API_KEY": "configured-key",
                "APOLLO_ENRICHMENT_ENABLED": "false",
            },
            clear=True,
        ):
            self.assertIsNone(_build_apollo_client(timeout_seconds=1))

    def test_explicit_opt_in_requires_key(self) -> None:
        with patch.dict(
            os.environ,
            {"APOLLO_ENRICHMENT_ENABLED": "true"},
            clear=True,
        ):
            self.assertIsNone(_build_apollo_client(timeout_seconds=1))

    def test_explicit_opt_in_with_key_builds_client(self) -> None:
        with patch.dict(
            os.environ,
            {
                "APOLLO_API_KEY": "configured-key",
                "APOLLO_ENRICHMENT_ENABLED": "true",
            },
            clear=True,
        ):
            client = _build_apollo_client(timeout_seconds=1)
            self.assertIsNotNone(client)
            assert client is not None
            client.close()


if __name__ == "__main__":
    unittest.main()
