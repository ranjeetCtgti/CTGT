from __future__ import annotations

import unittest
from io import StringIO
from pathlib import Path
from unittest.mock import patch

from scrapers.career_pages import load_targets


class CareerPageIndustryFilterTests(unittest.TestCase):
    def test_excluded_sector_targets_are_not_loaded(self) -> None:
        csv_text = (
            "company_name,domain,careers_url,country,industry\n"
            "Useful Manufacturer,useful.example,https://useful.example/careers,Germany,Automotive\n"
            "Excluded Consultancy,excluded.example,https://excluded.example/careers,Germany,IT Services and IT Consulting\n"
        )
        with (
            patch.object(Path, "exists", return_value=True),
            patch.object(Path, "open", return_value=StringIO(csv_text)),
        ):
            targets = load_targets(Path("targets.csv"))

        self.assertEqual([target.company_name for target in targets], ["Useful Manufacturer"])


if __name__ == "__main__":
    unittest.main()
