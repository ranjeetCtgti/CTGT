from __future__ import annotations

import re
from dataclasses import dataclass, field

from config import (
    EXPANSION_SIGNAL_PHRASES,
    MIGRATION_SIGNAL_PHRASES,
    MIN_RELEVANT_CONTEXT_CHARS,
    PAIN_SIGNAL_PHRASES,
    PLM_KEYWORDS,
    PLM_KEYWORDS_DE,
    SOFTWARE_ALIASES,
)


RELEVANT_CONTEXT_RADIUS = 120
AMBIGUOUS_STANDALONE_ALIASES = {"tc", "nx"}


@dataclass
class PrefilterResult:
    passed: bool
    normalized_text: str
    matched_products: dict[str, list[str]] = field(default_factory=dict)
    matched_migration_phrases: list[str] = field(default_factory=list)
    matched_pain_phrases: list[str] = field(default_factory=list)
    matched_expansion_phrases: list[str] = field(default_factory=list)
    relevant_context: str = ""


def normalize_text(text: str) -> str:
    return " ".join(text.lower().split())


def keyword_prefilter(text: str) -> PrefilterResult:
    normalized = normalize_text(text)
    matched_products = _match_keywords(normalized)
    matched_migration = _match_phrases(normalized, MIGRATION_SIGNAL_PHRASES)
    matched_pain = _match_phrases(normalized, PAIN_SIGNAL_PHRASES)
    matched_expansion = _match_phrases(normalized, EXPANSION_SIGNAL_PHRASES)
    relevant_context = _extract_relevant_context(
        normalized,
        list(_flatten_matches(matched_products)) + matched_migration + matched_pain + matched_expansion,
    )

    has_min_context = len(relevant_context.strip()) >= MIN_RELEVANT_CONTEXT_CHARS
    passed = bool(matched_products) and has_min_context
    return PrefilterResult(
        passed=passed,
        normalized_text=normalized,
        matched_products=matched_products,
        matched_migration_phrases=matched_migration,
        matched_pain_phrases=matched_pain,
        matched_expansion_phrases=matched_expansion,
        relevant_context=relevant_context,
    )


def keyword_prefilter_many(texts: list[str]) -> list[PrefilterResult]:
    return [keyword_prefilter(text) for text in texts]


def _match_keywords(normalized_text: str) -> dict[str, list[str]]:
    matched: dict[str, list[str]] = {}
    products = set(PLM_KEYWORDS) | set(PLM_KEYWORDS_DE)
    for product in products:
        keywords = [
            *PLM_KEYWORDS.get(product, []),
            *PLM_KEYWORDS_DE.get(product, []),
            *SOFTWARE_ALIASES.get(product.lower(), set()),
        ]
        hits = sorted(
            {
                normalize_text(keyword)
                for keyword in keywords
                if normalize_text(keyword) not in AMBIGUOUS_STANDALONE_ALIASES
                and _contains_keyword(normalized_text, keyword)
            }
        )
        if hits:
            matched[product] = hits
    return matched


def _contains_keyword(normalized_text: str, keyword: str) -> bool:
    normalized_keyword = normalize_text(keyword)
    if not normalized_keyword:
        return False
    escaped = re.escape(normalized_keyword).replace(r"\ ", r"\s+")
    return re.search(rf"(?<![a-z0-9]){escaped}(?![a-z0-9])", normalized_text) is not None


def _match_phrases(normalized_text: str, phrases: list[str]) -> list[str]:
    return [
        normalize_text(phrase)
        for phrase in phrases
        if _contains_keyword(normalized_text, phrase)
    ]


def _extract_relevant_context(normalized_text: str, phrases: list[str]) -> str:
    snippets: list[str] = []
    seen: set[str] = set()

    for phrase in phrases:
        start = normalized_text.find(phrase)
        if start < 0:
            continue
        context_start = max(0, start - RELEVANT_CONTEXT_RADIUS)
        context_end = min(len(normalized_text), start + len(phrase) + RELEVANT_CONTEXT_RADIUS)
        snippet = normalized_text[context_start:context_end].strip()
        if snippet and snippet not in seen:
            seen.add(snippet)
            snippets.append(snippet)

    return " ... ".join(snippets)


def _flatten_matches(matched_products: dict[str, list[str]]) -> list[str]:
    for phrases in matched_products.values():
        for phrase in phrases:
            yield phrase
