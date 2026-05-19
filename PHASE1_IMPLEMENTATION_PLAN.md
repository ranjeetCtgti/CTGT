# CTGT Lead Engine - Phase 1 Implementation Plan

## Scope
Phase 1 covers the core pipeline only:
- Job board scraping via scrape.do: LinkedIn, Indeed, Stepstone
- Keyword pre-filtering
- NLP extraction (Gemini batch processing)
- PostgreSQL persistence (signals + companies)
- CLI pipeline orchestration and summary output

Excluded from Phase 1: career pages, news RSS, scheduling, CSV export, enrichment.

## Deliverables
- `scrapers/scrapedo_client.py`
- `scrapers/linkedin.py`
- `scrapers/indeed.py`
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
- Add `requirements.txt` with core libs: `httpx`, `beautifulsoup4`, `lxml`, `pydantic`, `sqlalchemy`, `psycopg2-binary`, `tenacity`, `loguru`, `python-dotenv`.
- Add `.env.example` for `SCRAPEDO_API_KEY`, `GEMINI_API_KEY`, `DATABASE_URL`, and run settings.

2. Define domain models and config
- Implement `models/schema.py` with:
  - `RawJobPosting`
  - `ExtractedSignal`
  - `CompanyLead`
- Implement `config.py` for:
  - software keywords and aliases
  - pain/expansion signal phrases
  - excluded companies
  - score constants and lead thresholds
  - board query sets and location maps

3. Build shared scrape.do client
- Implement `scrapers/scrapedo_client.py`:
  - request builder for `render`, `super`, `geoCode`, `waitSelector`, `blockResources`, `timeout`
  - retry behavior and structured logging
  - return payload + metadata needed for credit tracking in-memory during run

4. Implement job board scrapers
- `scrapers/linkedin.py`
  - build search URLs from query/location matrix
  - parse result cards: title, company, location, snippet, url, posted date (if available)
  - LinkedIn defaults: `render=true`, `super=true`
- `scrapers/indeed.py`
  - `render=false` first, fallback `render=true` on empty
  - support EN + IN + DE host variants
- `scrapers/stepstone.py`
  - `render=false` first, fallback `render=true`
  - German query set only
- Add 2-3 fallback selectors per element in each scraper.

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

7. Implement pipeline orchestrator
- `pipeline.py`
  - CLI flags:
    - `--source`
    - `--dry-run`
    - `--max-queries`
    - `--leads`
  - execution flow:
    1) collect from selected job boards
    2) pre-filter
    3) NLP extraction
    4) scoring + persist
    5) print HOT/WARM/COLD summary + credits used
  - graceful error handling per-source so one source failure does not kill whole run.

8. Validate and harden
- Add smoke test path (dry run, max queries = 1 or 2).
- Verify selectors against live pages and tune fallback selectors.
- Verify DB constraints, dedup behavior, and score outcomes.
- Confirm final Definition of Done from requirements.

## Data Flow (Phase 1)
1. Scraper returns `RawJobPosting` list.
2. Pre-filter removes low-signal items.
3. NLP converts candidates to `ExtractedSignal` list.
4. Score is computed and signal is persisted.
5. Company aggregate is upserted and lead grade recalculated.
6. End-of-run summary is printed.

## Acceptance Criteria (Phase 1 DoD)
- Pipeline runs end-to-end from CLI with real LinkedIn/Indeed/Stepstone input.
- Signals are extracted with software + company + source URL.
- `signals` table stores one row per valid unique source URL.
- `companies` table aggregates score and lead grade (`hot`, `warm`, `cold`).
- Console summary prints by source and lead band.
- `--dry-run` works without DB writes.

## Risks and Mitigation
- LinkedIn anti-bot instability:
  - always use `super=true`; retry on transient failures.
- Selector breakage:
  - keep selectors centralized per scraper and log zero-card events clearly.
- NLP schema drift:
  - strict validation and invalid field stripping, skip broken batches safely.
- Credit overrun in development:
  - enforce `--max-queries` during dev runs.

## Suggested Timeline (2-3 weeks)
- Week 1:
  - project skeleton, config/models, scrape.do client
  - initial Indeed + Stepstone scrapers
- Week 2:
  - LinkedIn scraper, prefilter, NLP module
  - DB layer + scoring + upsert
- Week 3:
  - pipeline integration, dry-run/live-run stabilization
  - documentation and Definition-of-Done verification
