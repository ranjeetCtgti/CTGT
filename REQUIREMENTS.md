# CTGT Lead Generation System — Requirements Document

**Company:** CTGT Innovations (https://www.ctgti.com/en)  
**Purpose:** Automatically detect companies using Siemens PLM software (Teamcenter, NX, Solid Edge, Polarion, Mendix) and qualify them as potential clients for resale, implementation, and support services.  
**Version:** 1.0  
**Last Updated:** 2026-05

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [System Architecture](#2-system-architecture)
3. [Data Sources](#3-data-sources)
4. [Scraping Infrastructure](#4-scraping-infrastructure)
5. [Signal Detection & Keyword Engine](#5-signal-detection--keyword-engine)
6. [NLP Extraction Layer](#6-nlp-extraction-layer)
7. [Scoring Model](#7-scoring-model)
8. [Data Storage](#8-data-storage)
9. [Pipeline Orchestration](#9-pipeline-orchestration)
10. [API & Credit Budget](#10-api--credit-budget)
11. [Error Handling & Resilience](#11-error-handling--resilience)
12. [Output & Lead Format](#12-output--lead-format)
13. [Tech Stack Summary](#13-tech-stack-summary)
14. [Project Folder Structure](#14-project-folder-structure)
15. [Phased Delivery Plan](#15-phased-delivery-plan)
16. [Constraints & Known Limitations](#16-constraints--known-limitations)

---

## 1. Project Overview

### 1.1 Goal

Build an automated signal-based lead detection pipeline that:
- Collects job postings, career pages, and news articles from the web
- Detects footprints of Siemens PLM software within that content
- Extracts and scores the companies behind those footprints
- Stores qualified leads in a structured database for sales team use

### 1.2 What Counts as a Lead

A company is a qualified lead if it shows verifiable evidence of using or actively seeking to use any of the following Siemens software products that CTGT resells or implements:

| Product | Lead Relevance |
|---|---|
| Teamcenter (all variants) | Primary — highest volume |
| NX / NX CAD / NX CAM | Primary |
| Solid Edge | Primary |
| Polarion ALM | Secondary |
| Mendix | Secondary |
| Siemens Opcenter / MES | Secondary |
| Xcelerator platform | Secondary |

### 1.3 Target Geographies

CTGT operates from Pune (India), Munich (Germany), and Toronto (Canada). Lead detection should prioritize but not be limited to:

- India (all regions)
- Germany, Austria, Switzerland (DACH)
- Canada
- United States
- United Kingdom
- Netherlands, France, Italy (secondary EU)

### 1.4 Target Industries

Siemens PLM software is predominantly used in:
- Automotive & Automotive Suppliers
- Aerospace & Defense
- Industrial Equipment & Machinery
- Electronics & High-Tech Manufacturing
- Medical Devices
- Energy & Power Generation
- Rail & Transportation

Companies in these verticals that are hiring or mentioning Siemens PLM tools should be prioritized.

---

## 2. System Architecture

The system is composed of four sequential layers. Data flows top-to-bottom; no layer skips another.

```
┌─────────────────────────────────────────────────────────────────────┐
│  LAYER 1 — DATA COLLECTION                                          │
│                                                                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────────┐  │
│  │ LinkedIn Jobs│  │    Indeed    │  │       Stepstone DE       │  │
│  │  (scrape.do) │  │  (scrape.do) │  │       (scrape.do)        │  │
│  └──────┬───────┘  └──────┬───────┘  └────────────┬─────────────┘  │
│         │                 │                        │                │
│  ┌──────────────────────────────────────────────┐  │                │
│  │  Career Page Crawler (own httpx scraper)     │  │                │
│  │  News Scraper (own httpx + RSS scraper)      │  │                │
│  └──────────────────────────┬───────────────────┘  │                │
└─────────────────────────────┼───────────────────────┼───────────────┘
                              │                       │
                              ▼                       ▼
┌─────────────────────────────────────────────────────────────────────┐
│  LAYER 2 — SIGNAL EXTRACTION                                        │
│                                                                     │
│  Fast pre-filter (keyword match) → Gemini API NLP batch extractor  │
│  Output: structured ExtractedSignal per source item                │
└──────────────────────────────────┬──────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────┐
│  LAYER 3 — ENRICHMENT & SCORING                                     │
│                                                                     │
│  Deduplication → Company merge → Score calculation → Lead grade    │
└──────────────────────────────────┬──────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────┐
│  LAYER 4 — STORAGE & OUTPUT                                         │
│                                                                     │
│  PostgreSQL → signals table + companies table → CLI output / CSV   │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 3. Data Sources

### 3.1 Source A — LinkedIn Jobs (via scrape.do)

**What we collect:** Job search result pages for PLM-related queries  
**Why:** Largest global job board; many engineering companies post exclusively here  
**Authentication required:** No — public search results are accessible without login  
**Anti-bot difficulty:** High — Cloudflare + behavioral fingerprinting  
**scrape.do mode required:** `render=true` + `super=true` (residential proxy)  

**Search queries (per geography):**

English queries (India, Canada, UK, US):
```
"Teamcenter administrator"
"Teamcenter PLM engineer"
"NX CAD engineer"
"NX CAM engineer"
"Solid Edge designer"
"Polarion ALM engineer"
"Siemens PLM implementation"
"Mendix developer Siemens"
"PLM consultant Teamcenter"
"Siemens digital industries engineer"
"Teamcenter integration developer"
"NX CAD designer manufacturing"
```

German queries (Germany):
```
"Teamcenter Administrator"
"NX Konstrukteur"
"Solid Edge Entwickler"
"Siemens PLM Berater"
"PLM Implementierung Teamcenter"
"Polarion ALM Ingenieur"
```

**URL pattern:**
```
https://www.linkedin.com/jobs/search/?keywords={QUERY}&location={LOCATION}&f_TPR=r86400
```

**Data to extract per job card:**
- Job title
- Company name
- Location (city, country)
- Job description snippet (first 500 chars shown in search results)
- Job URL
- Date posted (if visible)

**Pagination:** Scrape page 1 only per query per location (25 results). If a company appears in results, that is sufficient signal — we do not need to open each job page.

**Rate:** One scrape.do request per (query × location) combination. With 12 English queries × 4 locations + 6 German queries × 1 location = 54 requests per run.

---

### 3.2 Source B — Indeed (via scrape.do)

**What we collect:** Job search result pages  
**Why:** Strong coverage in India (Naukri alternative) and Germany (indeed.de)  
**Authentication required:** No  
**Anti-bot difficulty:** Medium — reCAPTCHA on some pages, otherwise manageable  
**scrape.do mode required:** Try `render=false` first (1 credit); fall back to `render=true` (5 credits) if response is empty  

**URL patterns:**
```
# English
https://www.indeed.com/jobs?q={QUERY}&l={LOCATION}&fromage=7

# India
https://in.indeed.com/jobs?q={QUERY}&l={LOCATION}&fromage=7

# Germany
https://de.indeed.com/jobs?q={QUERY}&fromage=7
```

**Search queries:** Same as LinkedIn (English + German sets above)

**Geographies:** India, Germany, Canada, United States

**Data to extract per job card:**
- Job title
- Company name
- Location
- Job snippet / description excerpt
- Job URL

**Rate:** ~40 requests per run (10 queries × 4 geographies, minus overlapping German queries handled by Stepstone).

---

### 3.3 Source C — Stepstone Germany (via scrape.do)

**What we collect:** Job search result pages  
**Why:** Dominant job board in DACH region; German Mittelstand manufacturing companies prefer Stepstone over LinkedIn  
**Authentication required:** No  
**Anti-bot difficulty:** Low-Medium — mostly server-rendered, `render=false` usually works  
**scrape.do mode required:** `render=false` first; fall back to `render=true`  

**URL pattern:**
```
https://www.stepstone.de/jobs?q={QUERY}
```

**German-language queries:**
```
"Teamcenter Administrator"
"Teamcenter PLM Ingenieur"
"NX CAD Konstrukteur"
"NX CAM Programmierer"
"Solid Edge Konstrukteur"
"Polarion ALM"
"Siemens PLM Berater"
"Mendix Entwickler"
"PLM Implementierung"
"Siemens NX Entwickler"
"CAD Teamcenter Spezialist"
```

**Data to extract:** Same as LinkedIn/Indeed.

**Rate:** ~11 requests per run (one per query, single geography).

---

### 3.4 Source D — Company Career Pages (own httpx scraper, no scrape.do)

**What we collect:** HTML content of the `/careers`, `/jobs`, or `/stellenangebote` pages of known target companies  
**Why:** Companies that post exclusively on their own site are missed by job boards; the career page also reveals the full job description with detailed tool requirements  
**Authentication required:** No  
**Anti-bot difficulty:** Very low — company career pages almost never have bot protection  
**Scraper type:** Plain `httpx` with rotating `User-Agent` headers. No scrape.do needed. This is free.

**How we build the target company list:**

Start with a seed list of known manufacturing companies by region. This list is maintained manually in a CSV file (`data/career_page_targets.csv`) with columns:
```
company_name, domain, careers_url, country, industry
```

Initial seed should include ~200–500 companies across:
- German automotive suppliers (Bosch, Continental, ZF, Schaeffler, etc.)
- Indian engineering companies (Tata Technologies, L&T, Mahindra Engineering, etc.)
- Canadian aerospace/industrial (Bombardier, Pratt & Whitney Canada, etc.)
- Global manufacturing companies known to use Siemens tools

**What to look for on each career page:**
- Any job title or description containing PLM keywords (see Section 5)
- The full text of each job listing found

**Crawl depth:** Career page index only (no following to individual job pages unless the index is paginated). If the career page uses JavaScript to load jobs, fall back to scrape.do for that specific URL.

**Rate:** Run daily. Process up to 500 URLs per day. At ~0.5s per request with delays, this takes ~10–15 minutes.

**Selector strategy:** Since career pages vary wildly, use a broad text extraction approach:
1. Extract all `<p>`, `<li>`, `<div>`, `<h1>`–`<h4>` text
2. Run keyword pre-filter (Section 5.1) on the combined text
3. If any keyword matches, pass the full page text to the NLP extractor

---

### 3.5 Source E — News & Press (own httpx + RSS scraper, no scrape.do)

**What we collect:** News articles, press releases, and blog posts mentioning Siemens PLM software alongside company names  
**Why:** A company announcing a Teamcenter implementation or signing a digital transformation partnership is a very hot lead — they are actively in a buying or deployment cycle  
**Authentication required:** No  
**Anti-bot difficulty:** Very low for RSS feeds; low for news sites  
**Scraper type:** RSS feed polling + targeted Google News RSS queries. Free.

**RSS feeds to monitor:**

Google News RSS (replace spaces with `+`):
```
https://news.google.com/rss/search?q=Teamcenter+implementation&hl=en
https://news.google.com/rss/search?q=Siemens+PLM+rollout&hl=en
https://news.google.com/rss/search?q="Solid+Edge"+manufacturing&hl=en
https://news.google.com/rss/search?q=Teamcenter+digital+transformation&hl=en
https://news.google.com/rss/search?q=Siemens+Xcelerator+implementation&hl=en
https://news.google.com/rss/search?q=Polarion+ALM+deployment&hl=en
https://news.google.com/rss/search?q=NX+CAD+Siemens+company&hl=en
# German
https://news.google.com/rss/search?q=Teamcenter+Implementierung&hl=de
https://news.google.com/rss/search?q=Siemens+PLM+Einführung&hl=de
```

**What to extract per article:**
- Article title
- Article URL
- Publication date
- Source/publisher name
- Article snippet/description from RSS

**Processing:** Pass the title + snippet to the NLP extractor. If a clear company name + Siemens product is identified, create a signal with `signal_type = "news"` and a higher base score than a job posting.

**Rate:** Poll RSS feeds every 6 hours. Each feed fetch = 1 plain HTTP request. ~10 feeds = negligible cost.

---

## 4. Scraping Infrastructure

### 4.1 scrape.do API Integration

**Base URL:** `https://api.scrape.do/`  
**Authentication:** `token` query parameter  
**Documentation:** https://scrape.do/documentation/

**Key parameters used in this project:**

| Parameter | Value | Reason |
|---|---|---|
| `token` | `{SCRAPEDO_API_KEY}` | Authentication |
| `url` | URL-encoded target URL | Required |
| `render` | `true` / `false` | `true` for LinkedIn, Glassdoor; `false` for Indeed, Stepstone first attempt |
| `super` | `true` / `false` | `true` for LinkedIn (needs residential IP); `false` for others by default |
| `geoCode` | `de`, `in`, `ca`, `us` | Match proxy location to target site's expected geography |
| `waitSelector` | CSS selector | Wait for job cards to appear before returning HTML |
| `blockResources` | `true` | Skip images/CSS/fonts — faster, cheaper |
| `timeout` | `30000` | 30s max wait |
| `device` | `desktop` | Default desktop UA |

**Python call pattern:**
```python
import httpx
import urllib.parse

def scrape(url: str, render: bool = False, super_proxy: bool = False,
           geo: str = None, wait_selector: str = None) -> str | None:
    params = {
        "token": SCRAPEDO_API_KEY,
        "url": urllib.parse.quote(url),
        "render": str(render).lower(),
        "super": str(super_proxy).lower(),
        "blockResources": "true",
        "timeout": "30000",
    }
    if geo:
        params["geoCode"] = geo
    if wait_selector:
        params["waitSelector"] = wait_selector

    response = httpx.get("https://api.scrape.do/", params=params, timeout=40)
    if response.status_code == 200:
        return response.text
    return None
```

**Retry logic:** On failure (non-200, timeout), retry once with `super=true` if not already set. After two failures, log and skip — do not retry infinitely.

**Credit tracking:** Log credits consumed per request based on mode:
- `render=false, super=false` → 1 credit
- `render=true, super=false` → 5 credits  
- `render=true, super=true` → 25 credits
- `render=false, super=true` → 10 credits

Store running total in memory per pipeline run and log at the end.

### 4.2 Own Scraper (Career Pages & News)

**Library:** `httpx` (async-capable, modern alternative to requests)  
**Parsing:** `beautifulsoup4` + `lxml` parser  
**Rate limiting:** 1 request per 2–4 seconds (randomized delay) per domain  
**User-Agent rotation:** Maintain a list of 10+ real browser User-Agent strings; rotate per request  
**Timeout:** 15 seconds per request  
**Failure handling:** Log failed URLs; skip and continue — do not block the pipeline  
**Robots.txt:** Respect `robots.txt` for career pages. Check once per domain per week.

**User-Agent list (minimum):**
```python
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_4_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4.1 Safari/605.1.15",
]
```

---

## 5. Signal Detection & Keyword Engine

### 5.1 Pre-filter (Fast Keyword Match)

Before sending any text to the Gemini API, run a fast lowercase string search. Only pass text to Gemini if at least one keyword from the master list is found. This saves API tokens.

**Master keyword list by product:**

```python
PLM_KEYWORDS = {
    "Teamcenter": [
        "teamcenter", "teamcenter x", "teamcenter manufacturing",
        "teamcenter mes", "teamcenter rapid author", "tc plm",
        "tc administration", "siemens teamcenter",
        "teamcenter integration", "teamcenter upgrade",
        "teamcenter migration", "product lifecycle management siemens",
    ],
    "NX": [
        "siemens nx", "nx cad", "nx cam", "nx cae", "nx nastran",
        "nx designer", "nx engineer", "nx modeling", "nx manufacturing",
        "unigraphics", "ugii",
    ],
    "Solid Edge": [
        "solid edge", "solid edge cad", "solid edge designer",
        "solid edge simulation", "solid edge manufacturing",
        "solid edge for manufacturing",
    ],
    "Polarion": [
        "polarion", "polarion alm", "polarion requirements",
        "siemens polarion", "polarion testng",
    ],
    "Mendix": [
        "mendix", "mendix developer", "mendix low-code",
        "mendix platform", "siemens mendix",
    ],
    "Siemens_General": [
        "siemens plm", "siemens digital industries",
        "siemens opcenter", "siemens mindsphere",
        "xcelerator", "siemens eda", "capital electra",
    ],
}
```

**German keyword extensions** (for Stepstone + German news):
```python
PLM_KEYWORDS_DE = {
    "Teamcenter": ["teamcenter", "tc-administration", "plm siemens"],
    "NX": ["siemens nx", "nx konstrukteur", "nx entwickler", "unigraphics"],
    "Solid Edge": ["solid edge", "solid edge konstrukteur"],
    "Polarion": ["polarion", "polarion alm"],
    "Mendix": ["mendix entwickler", "mendix plattform"],
}
```

### 5.2 Intent Classification Keywords

These are not product keywords — they are context signals that boost score when found alongside product keywords.

**Migration signals** (very high value — company switching from competitor):
```
"migrating from windchill"
"replacing windchill"
"transition from enovia"
"moving from catia"
"ptc windchill"
"dassault systemes"
"enovia"
"autodesk vault"
"autodesk pdm"
"sap plm"
"legacy pdm"
"legacy plm system"
"replace our current plm"
"evaluating plm solutions"
```

**Pain signals** (medium value — need for implementation/support services):
```
"implementation"
"rollout"
"deployment"
"upgrade"
"migration project"
"go-live"
"support engineer"
"system administrator"
"customization"
"integration developer"
"consultant"
"managed services"
"post go-live"
"change management"
```

**Expansion signals** (medium value — growing = new software seats needed):
```
"scaling engineering team"
"new r&d center"
"new manufacturing facility"
"new plant"
"digital transformation"
"industry 4.0"
"smart manufacturing"
"growing team"
"expanding operations"
```

---

## 6. NLP Extraction Layer

### 6.1 Purpose

The NLP extractor converts unstructured text (job posting, news article, career page content) into a structured `ExtractedSignal` object with:
- Confirmed company name
- Detected Siemens products (validated list, not free-text)
- Intent classification (migration / pain / expansion)
- Confidence score
- Industry guess

### 6.2 Model

**Model:** `gemma-4-31b-it` (Gemini API — free tier, sufficient for testing)  
**API:** Google Gemini API (`/v1beta/models/gemma-4-31b-it:generateContent`)  
**Max tokens per response:** 2048  
**Batch size:** 10 items per API call (reduces cost and latency vs. one call per item)

### 6.3 System Prompt Requirements

The system prompt must:
- Instruct the model to return **only valid JSON**, no markdown, no preamble
- Define the exact output schema (see below)
- Provide the constrained list of valid software names (prevents hallucination)
- Explain CTGT's business context so the model can make informed inferences
- Include examples of migration signals to watch for

**Output schema per item:**
```json
{
  "company_name": "string",
  "location": "city, country",
  "industry": "one of: Automotive, Aerospace, Industrial Equipment, Electronics, Medical Devices, Energy, Rail, Other Manufacturing, Unknown",
  "software_detected": ["only from: Teamcenter, NX, Solid Edge, Polarion, Mendix, Siemens PLM"],
  "migration_detected": true | false,
  "migration_from": "competitor name or null",
  "pain_signals": ["list of phrases found"],
  "expansion_signals": ["list of phrases found"],
  "confidence": 0.0 to 1.0,
  "reasoning": "one sentence"
}
```

### 6.4 Pre-filter Before Gemini API Call

Do NOT call Gemini API if:
- The text passes the keyword pre-filter but contains fewer than 50 characters of relevant context
- The company name is already known and processed in the last 7 days (dedup check against DB)
- The source URL has already been processed (URL dedup check)

### 6.5 Post-processing

After receiving Gemini's response:
1. Parse JSON (strip any accidental markdown fences)
2. Validate `software_detected` values against the allowed list — reject any not in the list
3. Reject signals where `software_detected` is empty (no Siemens tool confirmed)
4. Reject signals where `confidence < 0.3`
5. Compute `raw_score` using the scoring model (Section 7)

---

## 7. Scoring Model

Every `ExtractedSignal` gets a numeric score. Scores from multiple signals for the same company accumulate in the `companies` table.

### 7.1 Base Scores per Signal

| Signal | Points | Rationale |
|---|---|---|
| Job posting detected (any source) | 10 | Base value — company is hiring for the tool |
| Career page detection | 25 | Higher confidence — the company itself lists it |
| News article mention | 20 | Public announcement = active use |
| RSS/press release | 20 | Same as news |

### 7.2 Intent Bonus Points

| Intent | Points | Rationale |
|---|---|---|
| Migration signal detected | +30 | Actively switching PLM systems = urgent need |
| Each pain signal phrase | +10 (max 30) | More pain phrases = clearer service need |
| Each expansion signal phrase | +15 (max 30) | Growth = new seats + implementation |

### 7.3 Volume Bonus (same company, multiple signals)

| Condition | Bonus |
|---|---|
| 2nd signal from same company | +15 |
| 3rd+ signal from same company | +20 |
| Signals from 2+ different sources | +25 |

### 7.4 Confidence Multiplier

`final_score = raw_score × confidence`

Where `confidence` is 0.0–1.0 from the NLP extractor.

### 7.5 Lead Grade Thresholds

| Total Score | Grade | Meaning |
|---|---|---|
| ≥ 70 | 🔴 HOT | Multiple strong signals, immediate follow-up |
| 35–69 | 🟡 WARM | Clear footprint, add to nurture sequence |
| < 35 | 🟢 COLD | Weak or single signal, monitor only |

### 7.6 Score Decay (Future Phase)

If a company had signals 30+ days ago but no new signals, decay the score by 20% per month. Not required in Phase 1.

---

## 8. Data Storage

### 8.1 Database

**Engine:** PostgreSQL (v14+)  
**ORM/Query layer:** SQLAlchemy Core (not ORM) — raw SQL for control and performance  
**Connection:** Single connection pool via `DATABASE_URL` env variable  
**Recommended hosting:** Supabase free tier (500MB, sufficient for Phase 1) or local PostgreSQL

### 8.2 Table: `signals`

Stores every individual detection event. One row per source URL processed that yielded a valid signal.

```sql
CREATE TABLE signals (
    id                SERIAL PRIMARY KEY,
    company_name      TEXT NOT NULL,
    company_domain    TEXT,
    location          TEXT,
    industry          TEXT,
    software          JSONB,                    -- ["Teamcenter", "NX"]
    signal_type       TEXT,                    -- job_posting | career_page | news
    signal_source     TEXT,                    -- linkedin | indeed | stepstone | career_page | news
    migration         BOOLEAN DEFAULT FALSE,
    migration_from    TEXT,
    pain_signals      JSONB,                   -- ["implementation", "upgrade"]
    expansion_signals JSONB,
    raw_score         INT DEFAULT 0,
    confidence        FLOAT DEFAULT 0,
    source_url        TEXT UNIQUE,             -- dedup key
    source_title      TEXT,
    detected_at       TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_signals_company ON signals(LOWER(company_name));
CREATE INDEX idx_signals_detected_at ON signals(detected_at);
```

### 8.3 Table: `companies`

Deduplicated company records. One row per company. Score accumulates here as new signals arrive.

```sql
CREATE TABLE companies (
    id              SERIAL PRIMARY KEY,
    company_name    TEXT NOT NULL,
    company_domain  TEXT,
    location        TEXT,
    industry        TEXT,
    employee_count  TEXT,                      -- from enrichment (future)
    revenue_range   TEXT,                      -- from enrichment (future)
    software        JSONB,                     -- union of all detected software
    signal_sources  JSONB,                     -- ["linkedin", "indeed"]
    signal_count    INT DEFAULT 0,
    migration_risk  BOOLEAN DEFAULT FALSE,
    total_score     INT DEFAULT 0,
    lead_score      TEXT DEFAULT 'cold',       -- hot | warm | cold
    contacts        JSONB DEFAULT '[]',        -- from enrichment (future)
    first_seen      TIMESTAMPTZ DEFAULT NOW(),
    last_updated    TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(company_domain)
);

CREATE INDEX idx_companies_score ON companies(total_score DESC);
CREATE INDEX idx_companies_lead_score ON companies(lead_score);
CREATE INDEX idx_companies_name ON companies(LOWER(company_name));
```

### 8.4 Table: `scrape_log`

Tracks every scrape.do request for credit accounting and debugging.

```sql
CREATE TABLE scrape_log (
    id            SERIAL PRIMARY KEY,
    source        TEXT,                        -- linkedin | indeed | stepstone
    query         TEXT,
    target_url    TEXT,
    status        TEXT,                        -- success | failed | skipped
    credits_used  INT DEFAULT 0,
    cards_found   INT DEFAULT 0,
    signals_found INT DEFAULT 0,
    scraped_at    TIMESTAMPTZ DEFAULT NOW()
);
```

### 8.5 Deduplication Rules

1. **Signal dedup:** `source_url` is UNIQUE in `signals` table — same URL never processed twice
2. **Company dedup:** Match by `company_domain` first, then by `LOWER(company_name)` similarity (Levenshtein distance ≤ 2) — prevents "Bosch GmbH" and "Robert Bosch GmbH" from creating two records
3. **Recency dedup:** If a company was updated < 24 hours ago and a new signal comes from the same source, skip (prevents double-counting daily runs)

---

## 9. Pipeline Orchestration

### 9.1 Main Pipeline Flow

```
pipeline.py run
    │
    ├─ Step 1: Collect raw data
    │   ├─ scrape_linkedin()     → list[RawJobPosting]
    │   ├─ scrape_indeed()       → list[RawJobPosting]
    │   ├─ scrape_stepstone()    → list[RawJobPosting]
    │   ├─ crawl_career_pages()  → list[RawCareerPage]
    │   └─ fetch_news_rss()      → list[RawNewsItem]
    │
    ├─ Step 2: Pre-filter
    │   └─ keyword_prefilter()   → discard items with no PLM keywords
    │
    ├─ Step 3: NLP extraction
    │   └─ extract_signals()     → list[ExtractedSignal]
    │       (batches of 10 → Gemini API)
    │
    ├─ Step 4: Persist
    │   ├─ save_signal()         → signals table (one row per signal)
    │   └─ upsert_company()      → companies table (merge + rescore)
    │
    └─ Step 5: Report
        └─ print summary: hot/warm counts, credits used, signals found
```

### 9.2 CLI Interface

```bash
# Full run — all sources
python pipeline.py

# Specific sources only
python pipeline.py --source linkedin indeed

# Dry run — no DB writes (for testing)
python pipeline.py --dry-run

# Limit queries per source (for credit budgeting during dev)
python pipeline.py --max-queries 2 --dry-run

# Print current lead table
python pipeline.py --leads

# Export leads to CSV
python pipeline.py --export leads_export.csv
```

### 9.3 Scheduling

Run the full pipeline once daily, overnight (low traffic on job boards).

**Recommended schedule:**
- Job board scrapers (LinkedIn, Indeed, Stepstone): 02:00 UTC daily
- Career page crawler: 03:00 UTC daily
- News RSS: every 6 hours

Use `apscheduler` (Python) or a simple cron job. Do not run more than once per day per source to avoid pattern detection.

---

## 10. API & Credit Budget

### 10.1 scrape.do Credit Cost per Run

| Source | Queries | Locations | Mode | Credits/req | Total |
|---|---|---|---|---|---|
| LinkedIn | 12 EN + 6 DE | 4 EN + 1 DE | render + super | 25 | ~1,125 |
| Indeed | 10 | 4 | render=false → render=true | 1–5 | ~60–200 |
| Stepstone | 11 | 1 | render=false → render=true | 1–5 | ~15–55 |
| **Total per run** | | | | | **~1,200–1,380** |

> **Note on free tier:** The 1,000 free credits are enough for testing. For production daily runs, the Starter plan (~$49/mo for 250,000 credits) is sufficient.

**Development/testing budget:** Use `--max-queries 2` and `--source indeed stepstone` during development. This costs ~20–30 credits per test run, preserving free credits.

### 10.2 Gemini API Cost per Run

Assume 500 job postings collected → 200 pass keyword pre-filter → 20 batches of 10.

Each batch: ~800 input tokens + ~400 output tokens = ~1,200 tokens.  
20 batches = ~24,000 tokens total.

Using Gemini API free tier (`gemma-3-27b-it`), this is **$0.00 per daily run** during testing. Monitor free tier quota limits.

---

## 11. Error Handling & Resilience

### 11.1 scrape.do Failures

| Failure type | Action |
|---|---|
| HTTP 200 but empty HTML | Retry with `render=true` if wasn't already; else log + skip |
| HTTP 429 (rate limit) | Wait 60 seconds, retry once |
| HTTP 500 (scrape.do error) | Log + skip (scrape.do doesn't charge for failures) |
| Timeout | Log + skip |
| No job cards found in HTML | Log selector miss, flag for manual CSS selector review |

### 11.2 Gemini API Failures

| Failure type | Action |
|---|---|
| JSON parse error | Log raw response; skip batch; continue |
| API timeout | Retry once after 10 seconds |
| Invalid software name in response | Strip the invalid value; keep the rest |
| Empty `software_detected` | Discard signal entirely |
| Rate limit (429) | Exponential backoff: 5s, 15s, 45s |

### 11.3 Career Page / RSS Failures

| Failure type | Action |
|---|---|
| Connection timeout | Log URL + skip |
| Non-200 status | Log + skip |
| Empty page content | Log + skip |
| Robots.txt disallow | Skip permanently; mark in target CSV |

### 11.4 Database Failures

- Wrap all writes in try/except
- On unique constraint violation (duplicate URL): silently ignore
- On connection failure: log + abort the pipeline run (do not lose data silently)

### 11.5 Logging

Use `loguru` for all logging. Log levels:
- `INFO`: Normal flow — pages scraped, signals found, DB writes
- `DEBUG`: Individual HTML parsing steps (disabled in production)
- `WARNING`: Fallbacks triggered (render upgrade, proxy upgrade)
- `ERROR`: Unrecoverable failures for a single item
- `CRITICAL`: Pipeline-level failures (DB down, API key invalid)

Log to both console and a rotating file (`logs/pipeline_{date}.log`). Keep 7 days of logs.

---

## 12. Output & Lead Format

### 12.1 Console Output (End of Each Run)

```
═══ CTGT Lead Engine — 2026-05-18 02:00 UTC ═══

Scraping summary:
  LinkedIn:    48 pages scraped | 312 job cards | 18 signals
  Indeed:      40 pages scraped | 280 job cards | 14 signals
  Stepstone:   11 pages scraped |  87 job cards |  9 signals
  Career pages: 200 pages crawled | 22 signals
  News RSS:    10 feeds | 45 articles | 6 signals

NLP extraction: 69 signals from 520 items (keyword hit rate: 41%)
scrape.do credits used this run: 847

🔴 HOT LEADS (score ≥ 70):
──────────────────────────────────────────────────────────────────
COMPANY                       SCORE  SOFTWARE              LOCATION
──────────────────────────────────────────────────────────────────
Schaeffler AG                  112   Teamcenter, NX        Germany
Tata Technologies Ltd           98   Teamcenter            India
XYZ Automotive GmbH             87   NX, Solid Edge        Germany
──────────────────────────────────────────────────────────────────

🟡 WARM LEADS (score 35–69):
[table of warm leads]

Total companies in DB: 847 | Hot: 23 | Warm: 156 | Cold: 668
```

### 12.2 CSV Export Format

When running `python pipeline.py --export leads.csv`, output a CSV with:

```
company_name, company_domain, location, industry, software_detected,
signal_sources, signal_count, migration_risk, total_score, lead_score,
first_seen, last_updated
```

### 12.3 Data Retained per Company Record

```json
{
  "company_name": "Schaeffler AG",
  "company_domain": "schaeffler.com",
  "location": "Herzogenaurach, Germany",
  "industry": "Automotive",
  "software_detected": ["Teamcenter", "NX"],
  "signal_sources": ["linkedin", "stepstone", "career_page"],
  "signal_count": 7,
  "migration_risk": false,
  "total_score": 112,
  "lead_score": "hot",
  "first_seen": "2026-05-10T02:00:00Z",
  "last_updated": "2026-05-18T02:00:00Z"
}
```

---

## 13. Tech Stack Summary

| Component | Technology | Version | Purpose |
|---|---|---|---|
| Language | Python | 3.11+ | All components |
| Job board scraping | scrape.do API | — | LinkedIn, Indeed, Stepstone |
| Career/news scraping | httpx | 0.27+ | Own scraper for career pages + RSS |
| HTML parsing | BeautifulSoup4 + lxml | latest | Parse scraped HTML |
| NLP extraction | Google Gemini API | gemma-3-27b-it (free tier) | Signal extraction from text |
| Data models | Pydantic | v2 | Validated data structures |
| Database | PostgreSQL | 14+ | Lead storage |
| DB access | SQLAlchemy Core | 2.0+ | SQL queries |
| Retry logic | tenacity | 8.x | Resilient API calls |
| Scheduling | apscheduler | 3.x | Daily pipeline runs |
| Logging | loguru | 0.7+ | Structured log output |
| Config | python-dotenv | 1.x | Environment variables |

---

## 14. Project Folder Structure

```
lead_engine/
│
├── scrapers/
│   ├── __init__.py
│   ├── scrapedo_client.py      # scrape.do API wrapper (shared)
│   ├── linkedin.py             # LinkedIn Jobs scraper
│   ├── indeed.py               # Indeed scraper (EN + DE)
│   ├── stepstone.py            # Stepstone DE scraper
│   ├── career_pages.py         # Own httpx career page crawler
│   └── news_rss.py             # RSS feed fetcher + parser
│
├── extractors/
│   ├── __init__.py
│   ├── prefilter.py            # Fast keyword match (no API call)
│   └── nlp.py                  # Gemini API batch extractor
│
├── models/
│   ├── __init__.py
│   └── schema.py               # Pydantic models (RawJobPosting, ExtractedSignal, CompanyLead)
│
├── db/
│   ├── __init__.py
│   └── database.py             # PostgreSQL init, save_signal, upsert_company, get_leads
│
├── data/
│   └── career_page_targets.csv # Seed list of company career page URLs
│
├── logs/                       # Auto-created; gitignored
│
├── pipeline.py                 # Main orchestrator + CLI entry point
├── config.py                   # All keywords, scores, queries, settings
├── requirements.txt
├── .env.example
├── REQUIREMENTS.md             # This document
└── README.md                   # Quick-start guide
```

---

## 15. Phased Delivery Plan

### Phase 1 — Core Pipeline (Target: 2–3 weeks)

- [ ] `scrapedo_client.py` — scrape.do wrapper with credit tracking
- [ ] `linkedin.py` — search page scraper + card parser
- [ ] `indeed.py` — search page scraper (EN + DE)
- [ ] `stepstone.py` — search page scraper (DE)
- [ ] `prefilter.py` — keyword pre-filter
- [ ] `nlp.py` — Gemini API batch extractor
- [ ] `schema.py` — Pydantic models
- [ ] `database.py` — PostgreSQL tables + queries
- [ ] `pipeline.py` — CLI orchestrator
- [ ] `config.py` — keyword dictionary + scoring

**Definition of done for Phase 1:** Pipeline runs end-to-end, collects real job postings from all 3 job boards, extracts signals, stores leads in PostgreSQL, prints HOT/WARM summary.

### Phase 2 — Own Scrapers (Target: 1–2 weeks after Phase 1)

- [ ] `career_pages.py` — httpx crawler for `/careers` pages
- [ ] `news_rss.py` — RSS feed monitor
- [ ] `data/career_page_targets.csv` — initial seed list of 200 companies
- [ ] Integrate both into `pipeline.py`

### Phase 3 — Robustness & Ops (Target: 1 week after Phase 2)

- [ ] `scrape_log` table and credit accounting
- [ ] Scheduling via `apscheduler`
- [ ] CSV export (`--export` flag)
- [ ] Selector health check — alert if a scraper returns 0 cards consistently
- [ ] Rotate CSS selectors strategy (document fallback selectors for each job board)

### Phase 4 — Enrichment (Future)

- [ ] Apollo.io API integration for company size + contacts
- [ ] Domain resolution (company name → domain via Clearbit or manual lookup)
- [ ] Score decay for stale leads
- [ ] Simple web dashboard (Flask or Streamlit) to browse leads

---

## 16. Constraints & Known Limitations

### 16.1 LinkedIn Scraping Reliability

LinkedIn is the most aggressive anti-bot platform. scrape.do's residential proxies (`super=true`) provide good success rates but are not guaranteed. Expect 70–85% success rate on LinkedIn. Mitigation:
- Always retry failed LinkedIn requests with `super=true` if not already set
- If a search query consistently fails, rotate the query phrasing
- Monitor LinkedIn HTML structure changes — their React frontend updates frequently

### 16.2 CSS Selector Brittleness

All three job boards (LinkedIn, Indeed, Stepstone) render job card HTML using React/Next.js. CSS class names are auto-generated and change with each deploy. Each scraper must:
- Have 2–3 fallback selectors per element
- Log clearly when 0 cards are found (signals a selector break, not empty results)
- Be easy to update — all selectors should be in one place per scraper file

### 16.3 Company Name Disambiguation

"Bosch" and "Robert Bosch GmbH" are the same company. "Siemens AG" (the parent) is NOT a CTGT client — Siemens is the software vendor. The NLP extractor must:
- Normalize company names
- Exclude Siemens AG itself and its direct subsidiaries as leads
- Exclude competitors (PTC, Dassault, Autodesk) as leads

Add an explicit exclusion list to `config.py`:
```python
EXCLUDED_COMPANIES = [
    "siemens ag", "siemens", "ptc inc", "dassault systemes",
    "autodesk", "ansys", "hexagon ab", "aveva",
]
```

### 16.4 Data Privacy

- Do not collect or store personal data (individual names, emails) in Phase 1
- The `contacts` field in `companies` table is reserved for Phase 4 (enrichment)
- Company names, job titles, and public job posting URLs are public data — no GDPR concerns
- Career page URLs are public — no GDPR concerns

### 16.5 Legal

Scraping public job boards is a legally grey area. Key guidelines:
- Only scrape publicly accessible pages (no login required)
- Do not bypass paywalls or authentication
- Respect `robots.txt` on all own-scraper targets (career pages, news)
- scrape.do handles the proxy and browser layer — CTGT is the data consumer, not the scraper operator, which reduces legal exposure
- Do not store raw HTML long-term — discard after extraction

---

*End of Requirements Document*
