# CTGT Lead Engine - Project Status

Last updated: 2026-05-21

## Current Phase Status

Overall status: core pipeline is operational, Phase 2 source expansion is partially complete, and Phase 3/4 work remains mostly open.

## Phase 1 - Core Pipeline

Status: Mostly complete

- [x] `scrapers/scrapedo_client.py` implemented for Stepstone credit-tracked scraping
- [x] JobSpy-based collection implemented for `linkedin`, `indeed`, and `google`
- [x] `scrapers/stepstone.py` implemented
- [x] `extractors/prefilter.py` implemented
- [x] `extractors/nlp.py` implemented
- [x] `models/schema.py` implemented
- [x] `db/database.py` implemented
- [x] `pipeline.py` implemented
- [x] `config.py` implemented
- [x] CLI summary output implemented
- [x] `--dry-run`, `--smoke-test`, and `--leads` implemented
- [x] `--validate-phase1` readiness and smoke validation command implemented
- [x] PostgreSQL persistence and company aggregation implemented
- [ ] End-to-end production validation with all intended live sources still depends on live credentials and network verification

Notes:

- The codebase uses Google instead of Glassdoor in the JobSpy source set.
- The implemented Phase 1 source set is `linkedin`, `indeed`, `google`, and `stepstone`.

## Phase 2 - Own Scrapers

Status: Partially complete

- [x] `scrapers/career_pages.py` implemented
- [x] `scrapers/news_rss.py` implemented
- [x] `data/career_page_targets.csv` present
- [x] Career pages integrated into `pipeline.py`
- [x] News RSS integrated into `pipeline.py`
- [ ] Source quality, coverage, and live-run hardening still need more validation

## Phase 3 - Robustness and Ops

Status: Partially complete

- [x] `scrape_log` persistence for per-source run activity and scrape credit usage
- [ ] Scheduling via `apscheduler` or external orchestration later
- [ ] CSV export via `--export` intentionally deferred because the Next.js dashboard will read the DB directly
- [x] Health checks / alerting for repeated failed scraper runs and repeated zero-card runs
- [ ] Documented selector rotation strategy

## Phase 4 - Enrichment

Status: Not started, with one dashboard item already present early

- [ ] Apollo or equivalent enrichment integration
- [ ] Domain resolution enrichment
- [ ] Score decay for stale leads
- [x] Simple dashboard exists in `dashboard.py`

## Recommended Next Milestone

The clean next milestone is to continue the remaining Phase 3/4 work after enrichment is wired:

1. Finish enrichment and persist enrichment outputs.
2. Add scheduler/orchestration once the full write path is stable.
3. Revisit selector fallback/rotation strategy where needed.
