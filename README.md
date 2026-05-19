# CTGT Lead Engine - Phase 1

Phase 1 covers scrape.do-powered collection from LinkedIn, Indeed, and Stepstone, keyword prefiltering, Gemini extraction, PostgreSQL persistence, and CLI summaries.

## Setup

1. Install dependencies:

```powershell
pip install -r requirements.txt
```

2. Fill in real values in `.env`:

- `SCRAPEDO_API_KEY`
- `GEMINI_API_KEY`
- `DATABASE_URL`

## Commands

Smoke test:

```powershell
python pipeline.py --smoke-test
```

Single-source smoke test:

```powershell
python pipeline.py --source linkedin --smoke-test
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

Print current leads:

```powershell
python pipeline.py --leads
```

Run the local dashboard:

```powershell
python dashboard.py
```

## Smoke Test Behavior

- Forces `--dry-run`
- Defaults `--max-queries` to `3` if not provided
- Returns non-zero if any selected source errors, if no pages are scraped, or if no job cards are parsed

## Request Budget Mode

- Default mode is `testing` (`PIPELINE_PHASE` unset or not `production`)
- Testing mode is non-production and caps scrape.do requests to `3` each for LinkedIn, Indeed, and Stepstone
- Default testing budget is `9` scrape.do requests total across all three sources
- Set `PIPELINE_PHASE=production` to remove the testing caps and use the normal query-derived request budget

## Current Constraints

- Live selector verification depends on valid API keys and network access.
- DB dedup and lead aggregation are implemented, but end-to-end verification still requires a real PostgreSQL target.
- Gemini batch responses are validated strictly; count mismatches fail the batch instead of silently dropping items.
