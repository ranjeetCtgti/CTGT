# CTGT Lead Engine - Phase 1 Implementation Plan

## Scope
Phase 1 covers the core pipeline only:
- JobSpy-backed LinkedIn, Indeed, and Google collection plus scrape.do-backed Stepstone collection
- Keyword pre-filtering
- NLP extraction (Gemini batch processing)
- PostgreSQL persistence (signals + companies)
- CLI pipeline orchestration and summary output

Excluded from Phase 1: career pages, news RSS, scheduling, CSV export, enrichment.

## Deliverables
- `scrapers/jobspy_adapter.py`
- `scrapers/scrapedo_client.py`
- `scrapers/stepstone.py`
- `extractors/prefilter.py`
- `extractors/nlp.py`
- `models/schema.py`
- `db/database.py`
- `pipeline.py`
- `config.py`
- `requirements.txt`
- `.env.example`
- `README.md`

## Implementation Sequence
1. Bootstrap project structure and dependencies
- Create package directories from the requirements structure.
- Add `requirements.txt` with core libs: `python-jobspy`, `httpx`, `beautifulsoup4`, `lxml`, `pydantic`, `sqlalchemy`, `psycopg2-binary`, `tenacity`, `loguru`, `python-dotenv`.
- Add `.env.example` for `SCRAPEDO_API_KEY`, `GEMINI_API_KEY`, `DATABASE_URL`, and run settings.

2. Define domain models and config
- Implement `models/schema.py` with:
  - `RawJobPosting`
  - `ExtractedSignal`
  - `CompanyLead`
- Add `google` to `models.schema.SignalSource` and ensure `RawJobPosting.source` accepts it.
- Implement `config.py` for:
  - software keywords and aliases
  - pain/expansion signal phrases
  - excluded companies
  - score constants and lead thresholds
  - board query sets and location maps
- Keep `config.py` query sets as the source of truth for search terms; the JobSpy adapter receives the active query string and writes it into each normalized posting.

3. Build shared scrape.do client
- Implement `scrapers/scrapedo_client.py`:
  - request builder for `render`, `super`, `geoCode`, `waitSelector`, `blockResources`, `timeout`
  - retry behavior and structured logging
  - return payload + metadata needed for credit tracking in-memory during run
- Scope this client to Stepstone in the default Phase 1 path, while keeping it reusable for explicit future fallbacks.

4. Implement job board collectors
- `scrapers/jobspy_adapter.py`
  - call JobSpy directly from the pipeline
  - query LinkedIn, Indeed, and Google
  - normalize JobSpy rows into `RawJobPosting`
  - map `site -> source`, `company -> company_name`, `description -> snippet`, `date_posted -> posted_date`
  - inject `query` from the active search term because JobSpy rows do not carry it explicitly
  - filter to supported sources only
  - use JobSpy `description` as the canonical text field for Gemini input when available
- `scrapers/stepstone.py`
  - remain scrape.do-based
  - keep current fallback render strategy
  - continue to normalize rows into `RawJobPosting`

5. Implement extraction layer
- `extractors/prefilter.py`
  - normalize text
  - keyword/alias matching against Siemens PLM list
  - return pass/fail + matched keyword set
- `extractors/nlp.py`
  - batch size of 10 items
  - prompt to extract structured signal fields only
  - parse/validate output into `ExtractedSignal`
  - apply confidence and invalid-software stripping rules
  - retries/backoff for timeout/429

6. Implement storage layer
- `db/database.py`
  - database initialization and engine creation
  - create `signals` and `companies` tables
  - `save_signal()` with source URL dedup
  - `upsert_company()` with score update, software/source union, lead grade mapping
  - `get_leads()` for summary listing
- Ensure `google` survives through persistence, lead aggregation, and summary reporting.

7. Implement pipeline orchestrator
- `pipeline.py`
  - CLI flags:
    - `--source`
    - `--dry-run`
    - `--max-queries`
    - `--leads`
  - `--source` should support `linkedin`, `indeed`, `google`, `stepstone`, and `all`
  - replace per-board LinkedIn/Indeed collection with a JobSpy collection path
  - keep per-source stats split by `linkedin`, `indeed`, `google`, and `stepstone`
  - convert `get_source_scrapers()` into a source collector registry:
    - JobSpy-backed collectors emit normalized `RawJobPosting`
    - Stepstone remains separate
  - execution flow:
    1) collect from selected sources
    2) pre-filter
    3) NLP extraction
    4) scoring + persist
    5) print HOT/WARM/COLD summary + scrape.do credits used
  - graceful error handling per-source so one source failure does not kill the whole run.

8. Validate and harden
- Add smoke test path (dry run, max queries = 1 or 2).
- Test JobSpy normalization and site filtering.
- Verify LinkedIn description fetch behavior.
- Verify Google row shape compatibility.
- Verify Stepstone still works unchanged.
- Verify DB constraints, dedup behavior, and score outcomes.
- Confirm final Definition of Done from requirements.

## Data Flow (Phase 1)
1. JobSpy adapter or Stepstone scraper returns `RawJobPosting` list.
2. Pre-filter removes low-signal items.
3. NLP converts candidates to `ExtractedSignal` list.
4. Score is computed and signal is persisted.
5. Company aggregate is upserted and lead grade recalculated.
6. End-of-run summary is printed.

## Acceptance Criteria (Phase 1 DoD)
- Pipeline runs end-to-end from CLI with real LinkedIn, Indeed, Google, and Stepstone input.
- Google is a first-class Phase 1 source in collection, extraction, persistence, and summary output.
- Signals are extracted with software + company + source URL.
- `signals` table stores one row per valid unique source URL.
- `companies` table aggregates score and lead grade (`hot`, `warm`, `cold`).
- Console summary prints by source and lead band.
- `--source google` and `--source all` work as expected.
- `--dry-run` works without DB writes.
- scrape.do budgeting no longer counts LinkedIn or Indeed against request caps.

## Risks and Mitigation
- JobSpy dependency or API shape drift:
  - pin and review `python-jobspy` updates; validate normalization after upgrades.
- Site-specific rate limiting and proxy needs:
  - keep throttling and proxy options available for JobSpy-backed sources.
- Source normalization mismatches from JobSpy dataframe columns:
  - validate required columns and reject unsupported `site` values.
- Stepstone selector and scrape.do risk remains:
  - keep fallback selectors and render escalation intact.

## Suggested Timeline (2-3 weeks)
- Week 1:
  - project skeleton, config/models, JobSpy adapter, scrape.do client
  - initial Stepstone integration
- Week 2:
  - pipeline collection registry, prefilter, NLP module
  - DB layer + scoring + upsert
- Week 3:
  - end-to-end integration, dry-run/live-run stabilization
  - JobSpy normalization checks, Google validation, documentation verification
