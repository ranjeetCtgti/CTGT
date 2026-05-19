# Change Log

## 2026-05-18

### Changed
- Switched the pipeline default run mode to `testing` via `PIPELINE_PHASE=testing`.
- Added a non-production scrape.do cap of `3` requests each for LinkedIn, Indeed, and Stepstone (`9` total across all sources).
- Updated smoke-test defaults to `max_queries=3` so LinkedIn can use its full 3-request testing budget.
- Added runtime logging and summary output that clearly marks runs as `testing / non-production` unless `PIPELINE_PHASE=production` is set.

### Added
- Created `PHASE1_IMPLEMENTATION_PLAN.md` with a detailed Phase 1 execution plan based on `REQUIREMENTS.md`.
- Created `log.md` to track project changes over time.
- Bootstrapped Phase 1 project structure:
  - Added directories: `scrapers/`, `extractors/`, `models/`, `db/`, `data/`, `logs/`
  - Added package initializers: `scrapers/__init__.py`, `extractors/__init__.py`, `models/__init__.py`, `db/__init__.py`
- Added `requirements.txt` with core Phase 1 dependencies.
- Added `.env.example` with API, DB, and runtime placeholders.
- Implemented Sequence 2:
  - Added `models/schema.py` with `RawJobPosting`, `ExtractedSignal`, and `CompanyLead` Pydantic models.
  - Added `config.py` with software aliases, pain/expansion phrases, excluded companies, scoring constants, lead thresholds, query sets, and location/geo mappings.

### Fixed
- Updated `models/schema.py` timestamp defaults to timezone-aware UTC values (`datetime.now(timezone.utc)`) for:
  - `scraped_at`
  - `detected_at`
  - `first_seen`
  - `last_updated`
- Increased local `httpx` timeout headroom in `scrapers/scrapedo_client.py` so rendered scrape.do requests are not cut off at the same boundary as the upstream page timeout.
- Updated `scrapers/indeed.py` to retry with `render=true` when the initial `render=false` response parses to zero job cards.
- Updated `scrapers/stepstone.py` to retry with `render=true` when the initial `render=false` response parses to zero job cards.

### Added
- Implemented Sequence 3 with `scrapers/scrapedo_client.py`:
  - Added `ScrapeDoClient` with context manager support, shared `httpx` client, and env-based API key loading.
  - Added `ScrapeRequest` and `ScrapeResponse` dataclasses for structured input/output.
  - Added request parameter builder for `render`, `super`, `geoCode`, `waitSelector`, `blockResources`, `timeout`, and `device`.
  - Added retry policy (`tenacity`) for timeout/transport failures.
  - Added structured logging for request start/success/failure.
  - Added per-request estimated credit accounting and aggregate stats (`request_count`, `credits_used_total`).
- Implemented Sequence 4 job board scrapers:
  - Added `scrapers/linkedin.py` with LinkedIn search-plan generation, scrape.do integration (`render=true`, `super=true`), fallback selectors, and job-card parsing.
  - Added `scrapers/indeed.py` with multi-geo search-plan generation, `render=false` to `render=true` fallback, fallback selectors, and job-card parsing.
  - Added `scrapers/stepstone.py` with German search-plan generation, `render=false` to `render=true` fallback, fallback selectors, and job-card parsing.
- Implemented Sequence 5 extractor layer:
  - Added `extractors/prefilter.py` with normalized keyword matching, intent phrase detection, relevant-context extraction, and 50-character context gating.
  - Added `extractors/nlp.py` with Gemini batch extraction, JSON-only prompt construction, response parsing, validation, confidence filtering, exclusion filtering, and raw-score calculation.
  - Expanded `config.py` with master keyword dictionaries, German keyword extensions, migration phrases, Gemini settings, allowed software mappings, industry list, and extractor thresholds.
- Implemented Sequence 6 storage layer:
  - Added `db/database.py` with SQLAlchemy engine/session initialization and table definitions for `signals` and `companies`.
  - Added `save_signal()` with `source_url` dedup protection and duplicate-safe insert handling.
  - Added `upsert_company()` with company matching by domain/name similarity, 24-hour same-source guard, score accumulation, volume/multi-source bonuses, and lead-grade recalculation.
  - Added `get_leads()` and `init_database()` helpers for pipeline summary and startup flows.
- Added `.env` with the placeholder keys from `.env.example` for local runtime configuration.
- Implemented Sequence 7 pipeline orchestrator:
  - Added `pipeline.py` with CLI flags `--source`, `--dry-run`, `--max-queries`, and `--leads`.
  - Added end-to-end flow for scrape collection, keyword prefiltering, Gemini extraction, optional DB persistence, and summary printing.
  - Added per-source error isolation so one scraper failure does not terminate the full run.
  - Added summary output for source counts, lead bands, and scrape.do credit usage.
- Implemented Sequence 8 hardening work:
  - Added `--smoke-test` mode in `pipeline.py` to run a minimal dry-run validation pass with a default query cap of `1`.
  - Added runtime preflight validation for required environment variables and numeric settings before pipeline execution.
  - Added smoke-test failure criteria for source errors, zero scraped pages, and zero parsed job cards.
  - Added `README.md` with setup instructions, smoke-test commands, and current operational constraints.

### Notes
- Requirements source file in repository is `REQUIREMENTS.md` (not `requirement.md`).
