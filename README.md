# CTGT Lead Engine - Phase 1

Phase 1 uses JobSpy for LinkedIn, Indeed, and Google, keeps Stepstone on scrape.do, adds direct career-page crawling and Google News RSS ingestion, and then runs keyword prefiltering, configurable LLM extraction, PostgreSQL persistence, and CLI summaries.

## Setup

1. Install dependencies:

```powershell
pip install -r requirements.txt
```

2. Fill in real values in `.env`:

- `SCRAPEDO_API_KEY` for Stepstone runs
- `GEMINI_API_KEY` when `LLM_PROVIDER=gemini`
- `GEMINI_MODEL=gemma-4-31b-it` to use Gemma 4 31B on the Gemini API
- `GROQ_API_KEY` when `LLM_PROVIDER=groq`
- `GROQ_MODEL_ID=qwen/qwen3-32b` unless you want a different Groq-supported model
- `LLM_REQUESTS_PER_MINUTE=25` to keep layer 2 model traffic in the current 25-30 RPM limit
- `DATABASE_URL`
- optionally expand `data/career_page_targets.csv` with your target companies

Default sample configuration uses Gemini with `gemma-4-31b-it`. Groq remains available by setting `LLM_PROVIDER=groq`.
Hugging Face provider support is currently disabled.

## Commands

Smoke test:

```powershell
python pipeline.py --smoke-test
```

Single-source smoke test:

```powershell
python pipeline.py --source linkedin --smoke-test
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
- Testing mode is non-production and caps scrape.do requests to `3` for Stepstone
- layer 2 LLM batch calls are throttled to 25 requests per minute by default; temporary supported range is 25-30 via `LLM_REQUESTS_PER_MINUTE`
- LinkedIn, Indeed, and Google are collected via JobSpy and do not consume scrape.do credits in the default path
- Career pages and news RSS are collected via direct `httpx` requests and do not consume scrape.do credits
- Set `PIPELINE_PHASE=production` to remove the testing caps and use the normal query-derived request budget

## Current Constraints

- Live selector verification depends on valid API keys and network access.
- DB dedup and lead aggregation are implemented, but end-to-end verification still requires a real PostgreSQL target.
- LLM batch responses are validated strictly; count mismatches fail the batch instead of silently dropping items.
