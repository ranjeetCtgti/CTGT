from __future__ import annotations

from config import EXCLUDED_INDUSTRIES, EXCLUDED_INDUSTRY_CATEGORIES


def matching_excluded_industry(industry: str | None) -> str | None:
    """Return the configured exclusion matched by an industry label."""
    if not industry:
        return None

    normalized_industry = " ".join(industry.casefold().split())
    for category in EXCLUDED_INDUSTRY_CATEGORIES:
        if normalized_industry == category.casefold():
            return category
    for keyword in EXCLUDED_INDUSTRIES:
        normalized_keyword = " ".join(keyword.casefold().split())
        if normalized_keyword in normalized_industry:
            return keyword
    return None
