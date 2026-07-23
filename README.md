# CTGT Lead Engine - Phase 1

Phase 1 uses JobSpy for LinkedIn, Indeed, and Google, keeps Stepstone on scrape.do, adds direct career-page crawling and Google News RSS ingestion, and then runs keyword prefiltering, configurable LLM extraction, PostgreSQL persistence, and CLI summaries.
Lead enrichment is a separate post-pipeline pass. Scraping and NLP persistence finish first; company/contact enrichment runs afterward against the persisted leads table.

## Setup

1. Install dependencies:

```powershell
pip install -r requirements.txt
```

2. Fill in real values in `.env`:

- `SCRAPEDO_API_KEY` for Stepstone runs
- `GEMINI_API_KEY` when `LLM_PROVIDER=gemini`
- `GEMINI_MODEL=gemini-2.5-flash-lite` for the default Gemini extractor
- `GROQ_API_KEY` when `LLM_PROVIDER=groq`
- `GROQ_MODEL_ID=qwen/qwen3-32b` unless you want a different Groq-supported model
- `LLM_REQUESTS_PER_MINUTE=25` to keep layer 2 model traffic in the current 25-30 RPM limit
- `SERPER_API_KEY` for fallback company-domain resolution
- `DATABASE_URL`
- optionally expand `data/career_page_targets.csv` with your target companies
- optionally tune `CAREER_PAGE_MAX_PAGES_PER_TARGET` for broader Phase 2 career-page coverage

Default sample configuration uses Gemini with `gemini-2.5-flash-lite`. Groq remains available by setting `LLM_PROVIDER=groq`.
Hugging Face provider support is currently disabled.

For JobSpy records, the original job-board profile in `company_url` is preserved unchanged, including LinkedIn or Indeed profile URLs. `company_url_direct` supplies the preferred canonical `company_domain`; when it is absent, the host from `company_url` is used instead. Serper domain resolution runs only when neither URL yields a domain.

Apollo enrichment is disabled by default, even when `APOLLO_API_KEY` is present. It runs only when `APOLLO_ENRICHMENT_ENABLED=true` is explicitly configured; otherwise the enrichment pass continues with Google LinkedIn lookup and Hunter contact fallback.

## Commands

Smoke test:

```powershell
python pipeline.py --smoke-test
```

Single-source smoke test:

```powershell
python pipeline.py --source linkedin --smoke-test
python lead_enrichment_pass.py
```

Career page smoke test:

```powershell
python pipeline.py --source career_page --smoke-test
```

News RSS smoke test:

```powershell
python pipeline.py --source news --smoke-test
```

Google smoke test:

```powershell
python pipeline.py --source google --smoke-test
```

Phase 1 validation pass:

```powershell
python pipeline.py --validate-phase1
```

Dry run with explicit query cap:

```powershell
python pipeline.py --dry-run --max-queries 2
```

Full persistence run:

```powershell
python pipeline.py --max-queries 2
```

Production run with normal scrape budgets:

```powershell
$env:PIPELINE_PHASE="production"
python pipeline.py --max-queries 2
```

Render cron wrapper:

```powershell
python render_cron.py pipeline
python render_cron.py enrichment
```

Print current leads:

```powershell
python pipeline.py --leads
```

## Render Deployment

This repository now includes a root-level `render.yaml` Blueprint with:

- `ctgt-pipeline`: a cron job that runs `pipeline.py`
- `ctgt-lead-enrichment`: a cron job that runs `lead_enrichment_pass.py`
- `ctgt-postgres`: a Render PostgreSQL database

Default schedules in `render.yaml` are UTC:

- pipeline: `0 2 * * *`
- enrichment: `30 2 * * *`

Render cron jobs use an ephemeral filesystem, so this deployment relies on PostgreSQL for persistence and does not depend on local files surviving between runs.

### Deploy steps

1. Push this repository to GitHub/GitLab/Bitbucket.
2. In Render, create a new Blueprint and point it at this repo.
3. Review `render.yaml`, then provide the required secret env vars in the Render dashboard.
4. Trigger the pipeline cron manually once.
5. After it completes, trigger the enrichment cron manually once.

### Important env vars on Render

Set these for the pipeline cron if you use the corresponding providers:

- `SCRAPEDO_API_KEY`
- `GEMINI_API_KEY` or `GROQ_API_KEY`
- `SERPER_API_KEY`

Set these for the enrichment cron as needed:

- `GOOGLE_SEARCH_API_KEY`
- `GOOGLE_SEARCH_ENGINE_ID`
- `HUNTER_API_KEY`
- `SERPER_API_KEY`

Apollo is intentionally not configured in the current Render blueprint, so the enrichment pass will skip Apollo company/profile contact lookup stages while still running domain resolution, LinkedIn lookup, and Hunter fallback when configured.

### Runtime tuning

You can change job behavior without editing code:

- `PIPELINE_ARGS`
  Example: `--source all --max-queries 2`
- `ENRICHMENT_ARGS`
  Example: `--limit 100 --freshness-days 3`

If you change the schedules, remember that Render cron expressions are interpreted in UTC.

## Smoke Test Behavior

- Forces `--dry-run`
- Defaults `--max-queries` to `3` if not provided
- Returns non-zero if any selected source errors, if no pages are scraped, or if no job cards are parsed

## Phase 1 Validation

- `--validate-phase1` runs static readiness checks for the intended Phase 1 source set: `linkedin`, `indeed`, `google`, and `stepstone`
- it then runs a Phase 1-only smoke validation pass in `--dry-run` mode
- it returns non-zero if source registration/config is incomplete, required environment variables are missing, or the smoke validation fails

## Request Budget Mode

- Default mode is `testing` (`PIPELINE_PHASE` unset or not `production`)
- Testing mode is non-production and caps scrape.do requests to `3` for Stepstone
- layer 2 LLM batch calls are throttled to 25 requests per minute by default; temporary supported range is 25-30 via `LLM_REQUESTS_PER_MINUTE`
- LinkedIn, Indeed, and Google are collected via JobSpy and do not consume scrape.do credits in the default path
- Career pages and news RSS are collected via direct `httpx` requests and do not consume scrape.do credits
- Set `PIPELINE_PHASE=production` to remove the testing caps and use the normal query-derived request budget

## Operational Logging

- persisted runs now write one `scrape_log` row per selected source with source status, pages scraped, cards found, signals found, and scrape.do credits used
- the pipeline also checks recent persisted history and prints health alerts when a source has repeated failed runs or repeated zero-card runs
- `--dry-run` still avoids DB writes, so operational logs are only written on persisted runs

## Current Constraints

- Live selector verification depends on valid API keys and network access.
- DB dedup and lead aggregation are implemented, but end-to-end verification still requires a real PostgreSQL target.
- LLM batch responses are validated strictly; count mismatches fail the batch instead of silently dropping items.
