from __future__ import annotations

from dataclasses import dataclass

from config import (
    ENGLISH_QUERIES,
    GERMAN_QUERIES,
    GOOGLE_LOCATIONS,
    INDEED_LOCATIONS,
    LINKEDIN_LOCATIONS,
    STEPSTONE_GERMAN_QUERIES,
)


SEARCH_SOURCES = ("linkedin", "indeed", "google", "stepstone")


@dataclass(frozen=True, slots=True)
class PipelineQuery:
    value: str
    locale: str
    sources: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class PipelineLocation:
    value: str
    locale: str
    sources: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class PipelineSearchConfig:
    queries: tuple[PipelineQuery, ...]
    locations: tuple[PipelineLocation, ...]


_runtime_config: PipelineSearchConfig | None = None


def default_pipeline_search_config() -> PipelineSearchConfig:
    query_map: dict[tuple[str, str], set[str]] = {}
    for value in ENGLISH_QUERIES:
        query_map.setdefault((value, "en"), set()).update(("linkedin", "indeed", "google"))
    for value in GERMAN_QUERIES:
        query_map.setdefault((value, "de"), set()).update(("linkedin", "indeed", "google"))
    for value in STEPSTONE_GERMAN_QUERIES:
        query_map.setdefault((value, "de"), set()).add("stepstone")

    location_map: dict[tuple[str, str], set[str]] = {}
    source_locations = {
        "linkedin": LINKEDIN_LOCATIONS,
        "indeed": INDEED_LOCATIONS,
        "google": GOOGLE_LOCATIONS,
        "stepstone": ("Germany",),
    }
    for source, locations in source_locations.items():
        for value in locations:
            locale = "de" if value.strip().casefold() == "germany" else "en"
            location_map.setdefault((value, locale), set()).add(source)

    return PipelineSearchConfig(
        queries=tuple(
            PipelineQuery(value=value, locale=locale, sources=tuple(sorted(sources)))
            for (value, locale), sources in query_map.items()
        ),
        locations=tuple(
            PipelineLocation(value=value, locale=locale, sources=tuple(sorted(sources)))
            for (value, locale), sources in location_map.items()
        ),
    )


def set_runtime_search_config(config: PipelineSearchConfig | None) -> None:
    global _runtime_config
    _runtime_config = config


def get_runtime_search_config() -> PipelineSearchConfig:
    return _runtime_config if _runtime_config is not None else default_pipeline_search_config()


def build_jobspy_search_plan(source: str, max_queries: int | None = None) -> list[tuple[str, str]]:
    if source not in {"linkedin", "indeed", "google"}:
        raise ValueError(f"Unsupported JobSpy source: {source}")

    config = get_runtime_search_config()
    queries_by_locale: dict[str, list[str]] = {}
    for query in config.queries:
        if source in query.sources:
            queries_by_locale.setdefault(query.locale, []).append(query.value)

    plan: list[tuple[str, str]] = []
    for location in config.locations:
        if source not in location.sources:
            continue
        for query in queries_by_locale.get(location.locale, []):
            plan.append((query, location.value))

    return plan[:max_queries] if max_queries is not None else plan


def build_stepstone_search_plan(max_queries: int | None = None) -> list[str]:
    config = get_runtime_search_config()
    location_locales = {
        location.locale
        for location in config.locations
        if "stepstone" in location.sources
    }
    queries = [
        query.value
        for query in config.queries
        if "stepstone" in query.sources and query.locale in location_locales
    ]
    return queries[:max_queries] if max_queries is not None else queries
