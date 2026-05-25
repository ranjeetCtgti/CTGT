# CTGT Lead Engine: Actual Project Architecture and Data Flow

## Purpose

This document describes the architecture that is actually implemented in the current codebase, and how data flows through it. It also highlights where the implementation differs from `REQUIREMENTS.md`.

## 1. Architecture Summary

The current project is a batch ETL-style lead-detection pipeline with a separate read-only dashboard.

It is not a distributed system. It runs as a single Python process for pipeline execution, plus a separate Python HTTP server for dashboard viewing.

The implemented architecture is:

1. Configuration layer
2. Collection layer
3. Domain model layer
4. Extraction layer
5. Persistence and aggregation layer
6. Presentation layer

In short:

`Job board scrapers -> RawJobPosting -> keyword prefilter -> Gemini extraction -> ExtractedSignal -> signals table -> company aggregation -> companies table -> CLI summary / dashboard`

## 2. High-Level Component Architecture

### 2.1 Configuration Layer

File: `config.py`

This layer holds all central runtime constants:

- Siemens PLM software names and aliases
- keyword dictionaries
- exclusion list
- scoring constants
- lead thresholds
- Gemini API URL and model name
- query sets and locations for each scraper
- runtime defaults such as batch size and timeout

This file acts as the control plane for the rest of the system.

### 2.2 Collection Layer

Files:

- `scrapers/scrapedo_client.py`
- `scrapers/jobspy_adapter.py`
- `scrapers/stepstone.py`
- `scrapers/career_pages.py`
- `scrapers/news_rss.py`

This layer is responsible for fetching raw HTML from job boards and parsing job cards into structured Python objects.

Implemented sources:

- LinkedIn
- Indeed
- Google
- Stepstone
- Career pages
- News RSS

Stepstone depends on the shared `ScrapeDoClient`, which centralizes:

- scrape.do API requests
- request parameters
- retry handling
- request counting
- estimated credit tracking
- per-source request limits

### 2.3 Domain Model Layer

File: `models/schema.py`

This layer defines the core data contracts used by the project:

- `RawJobPosting`: output of scraping/parsing
- `ExtractedSignal`: NLP-normalized signal event
- `CompanyLead`: aggregated company-level lead record

These models are implemented using Pydantic and act as the schema boundary between pipeline stages.

### 2.4 Extraction Layer

Files:

- `extractors/prefilter.py`
- `extractors/nlp.py`

This layer converts scraped text into qualified Siemens PLM lead signals.

It has two sub-stages:

1. Fast keyword pre-filter
2. Gemini-based structured extraction

The pre-filter reduces unnecessary Gemini calls by discarding low-signal postings.

The Gemini extractor then:

- batches candidates
- prompts Gemini with strict JSON schema instructions
- validates the response
- normalizes software names
- drops excluded companies
- enforces confidence threshold
- computes raw score

### 2.5 Persistence and Aggregation Layer

File: `db/database.py`

This layer stores accepted signal rows and maintains per-company aggregates.

Main persisted entities:

- `signals` table: one row per accepted unique source URL
- `companies` table: one row per deduplicated company

Main responsibilities:

- initialize DB schema
- save signal rows
- deduplicate by `source_url`
- merge companies by domain/name similarity
- recalculate total company score
- assign lead band: `hot`, `warm`, `cold`

### 2.6 Orchestration Layer

File: `pipeline.py`

This is the main runtime coordinator.

It handles:

- CLI argument parsing
- environment validation
- source selection
- scrape budget logic
- calling scrapers
- prefiltering
- NLP extraction
- DB persistence
- run summary output

### 2.7 Presentation Layer

File: `dashboard.py`

This is a lightweight read-only local dashboard served by Python’s built-in HTTP server.

It reads data from the database and renders:

- lead summary cards
- source-level stats
- filtered signal tables
- top company leads

It does not trigger scraping or extraction. It is strictly a read layer over persisted data.

## 3. Exact Flow of Data

## 3.1 Pipeline Entry

Pipeline execution starts in `pipeline.py`.

Flow:

1. Load environment variables
2. Configure logging
3. Parse CLI args
4. Validate runtime configuration
5. If `--leads`, read from DB only
6. Otherwise run the full pipeline

## 3.2 Source Selection and Budgeting

Inside `run_pipeline()`:

- selected sources are determined
- pipeline phase is derived as `testing` or `production`
- per-source request caps are calculated
- DB is initialized unless `--dry-run`
- `ScrapeDoClient` is opened

This means scrape budgeting is decided before collection begins.

## 3.3 Collection Stage

Function: `collect_postings()`

The orchestrator gets source functions from `get_source_scrapers()`:

- `scrape_linkedin`
- `scrape_indeed`
- `scrape_google`
- `scrape_stepstone`
- `scrape_career_pages`
- `scrape_news`

The collectors do not all use the same fetch path:

1. JobSpy-backed job boards build query/location plans and return normalized `RawJobPosting` rows
2. Stepstone uses `ScrapeDoClient` and HTML parsing
3. Career pages use direct `httpx` fetches and page-text extraction
4. News uses RSS fetch + XML parsing

### LinkedIn flow

- Uses `render=true`
- Uses `super=true`
- Uses geo code by location
- Parses search result cards only

### Indeed flow

- Uses JobSpy
- Supports configured geographies from `config.py`

### Google flow

- Uses JobSpy
- Supports configured geographies from `config.py`

### Stepstone flow

- Germany only
- Tries `render=false` first
- Falls back to `render=true`

## 3.4 Raw Data Structure

The collection stage outputs `list[RawJobPosting]`.

Each `RawJobPosting` contains:

- source
- query
- title
- company name
- location
- snippet
- job URL
- posted date
- scraped timestamp

At this point, data is structured but not yet validated as a useful lead signal.

## 3.5 Prefilter Stage

Function: `filter_postings()`

For each posting, the pipeline creates a combined text string from:

- query
- title
- company name
- location
- snippet

That text is passed into `keyword_prefilter()`.

The prefilter:

- normalizes text
- checks for Siemens PLM product keywords
- checks for migration phrases
- checks for pain phrases
- checks for expansion phrases
- extracts relevant context

Pass condition:

- at least one product keyword matched
- enough context or enough text exists

Output:

- rejected postings are dropped
- passing postings continue

The result is still `list[RawJobPosting]`, but reduced to likely-relevant candidates.

## 3.6 NLP Extraction Stage

Function: `extract_signals()`

This stage transforms filtered postings into extraction candidates and sends them to Gemini.

### Internal flow

1. Optionally fetch already processed source URLs from DB
2. Optionally fetch recently processed companies from DB
3. Convert `RawJobPosting` -> `ExtractionCandidate`
4. Re-apply internal filtering in `GeminiExtractor`
5. Batch candidates
6. Build strict Gemini prompt
7. Send HTTP request to Gemini API
8. Parse JSON response
9. Normalize output fields
10. Accept or reject each item
11. Compute raw score
12. Return `list[ExtractedSignal]`

### Gemini acceptance rules

A candidate is rejected if:

- company name is missing
- company is in excluded companies
- no allowed software is detected
- confidence is below minimum threshold

### `ExtractedSignal` content

Each accepted signal contains:

- company name
- company domain (currently usually `None`)
- location
- industry
- software list
- signal type
- signal source
- migration flag
- migration source
- pain signals
- expansion signals
- raw score
- confidence
- reason
- source URL
- source title
- detection timestamp

This is the first fully qualified lead-signal object in the pipeline.

## 3.7 Persistence Stage

Function: `process_signals()`

This stage takes `list[ExtractedSignal]`.

For each signal:

1. Increment in-memory source stats
2. If dry-run:
   - aggregate only in memory
3. If not dry-run:
   - save signal row
   - if duplicate URL, skip company aggregation
   - upsert company aggregate

### Signal persistence

`save_signal()` writes one row to `signals`.

Dedup key:

- `source_url` unique constraint

This makes the `signals` table the event log of accepted evidence.

### Company aggregation

`upsert_company()` updates `companies`.

Company matching logic:

1. match by `company_domain` if available
2. exact lowercase name match
3. fuzzy similarity match

Aggregation logic:

- merge software list
- merge signal sources
- increment signal count
- propagate migration risk
- update location/industry if new data exists
- add signal score
- add 2nd-signal bonus
- add 3rd-plus-signal bonus
- add multi-source bonus
- recompute lead band

This makes `companies` the sales-facing aggregate view.

## 3.8 Summary Output

After processing completes, `print_run_summary()` prints:

- mode
- scrape.do caps
- per-source pages/cards/prefilter/signals/persisted/duplicates
- total NLP signals from total candidates
- estimated credits used
- lead-band counts
- top leads by band

This is operational output only. It is not a persisted report artifact.

## 3.9 Dashboard Read Flow

The dashboard is a separate process from the pipeline.

Flow:

1. Start `dashboard.py`
2. Initialize DB connection
3. Serve local HTTP endpoint
4. On request:
   - read leads via `get_leads()`
   - read signals via `get_signals()`
   - read source summary via `get_dashboard_source_stats()`
5. Render HTML

Important point:

The dashboard never participates in scraping, filtering, or extraction. It only reads persisted DB state.

## 4. Actual Data Lifecycle

The data lifecycle in the current implementation is:

1. Source data is collected from JobSpy, scrape.do, direct HTTP career pages, or RSS feeds
2. The raw source payload is normalized into `RawJobPosting` or `RawSignalDocument`
3. Text is filtered by keyword rules
4. Candidate text is sent to Gemini
5. Gemini response becomes `ExtractedSignal`
6. Signal is written to `signals`
7. Company aggregate is updated in `companies`
8. CLI summary and dashboard read from aggregated results

## 5. Implemented vs Intended Architecture

## 5.1 Implemented Now

Implemented in the current repo:

- LinkedIn JobSpy collector
- Indeed JobSpy collector
- Google JobSpy collector
- Stepstone scraper
- career page crawler
- news/RSS ingestion
- scrape.do wrapper
- keyword prefilter
- Gemini extractor
- Pydantic models
- SQLAlchemy DB layer
- signals persistence
- company aggregation
- CLI pipeline
- local dashboard

## 5.2 Present in Requirements but Not Yet Implemented

Defined in `REQUIREMENTS.md` but not present as working modules in the current codebase:

- `scrape_log` table
- CSV export command
- scheduler
- enrichment APIs
- contact/person data enrichment

This is no longer fully consistent with the original Phase 1 implementation plan, because the codebase already includes:

- career pages
- news RSS
- local dashboard

Still not implemented from later phases:

- scheduling
- CSV export
- enrichment

## 6. Architectural Conclusion

The exact current architecture is a Phase 1 core pipeline plus partial Phase 2 source expansion.

The system of record is PostgreSQL.

The authoritative runtime flow is:

`Scrapers -> RawJobPosting -> Prefilter -> GeminiExtractor -> ExtractedSignal -> signals table -> company upsert -> companies table -> CLI summary / dashboard`

The requirement document describes a broader future-state architecture, but the actual running project today is still missing Phase 3 and Phase 4 operational features:

- no scrape log table
- no CSV export
- no scheduler
- no enrichment integrations

## 7. File Map

Core files for this architecture:

- `pipeline.py`
- `config.py`
- `models/schema.py`
- `extractors/prefilter.py`
- `extractors/nlp.py`
- `db/database.py`
- `scrapers/scrapedo_client.py`
- `scrapers/jobspy_adapter.py`
- `scrapers/stepstone.py`
- `scrapers/career_pages.py`
- `scrapers/news_rss.py`
- `dashboard.py`
- `REQUIREMENTS.md`
- `PHASE1_IMPLEMENTATION_PLAN.md`
