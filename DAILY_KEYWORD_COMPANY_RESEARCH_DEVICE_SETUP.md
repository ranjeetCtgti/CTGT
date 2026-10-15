# Daily Keyword Company Research — second-device setup

This guide recreates the existing Codex scheduled task on another Windows PC
without losing PostgreSQL deduplication history or creating a second canonical
Excel workbook.

## Exact current task settings

- Name: `Daily Keyword Company Research`
- Automation ID/slug: `daily-keyword-company-research`
- Cadence: every day at 3:00 PM in the device/account local timezone
- Intended timezone: `Asia/Kolkata` (India Standard Time)
- Environment: local project checkout
- Model: `gpt-5.6-sol`
- Reasoning: high
- Notifications: failed runs only
- Status: active after cutover

If `gpt-5.6-sol` is unavailable on the destination device, use
`gpt-6.1-sol` with high reasoning. Do not run both devices at the same time.

## 1. Prepare the source device

1. Let any active run finish.
2. Pause the old scheduled task before activating the replacement. There must
   be only one active scheduler against the shared database and workbook.
3. Commit/push the repository or copy the whole project to the destination PC.
   Do not commit `.env`; it is intentionally ignored.
4. Choose one PostgreSQL transfer method from section 3.
5. Export the exact current automation prompt. From the repository root:

   ```powershell
   .\.venv\Scripts\python.exe .\scripts\export_codex_automation_prompt.py | Set-Clipboard
   ```

   This reads the current task's `automation.toml` and copies only its prompt.
   It does not expose `.env` or database credentials.

6. Optional continuity: after the new task exists, securely copy the old
   memory file into the new task's automation directory:

   ```text
   %USERPROFILE%\.codex\automations\daily-keyword-company-research\memory.md
   ```

   Copy `memory.md` only. Do not manually install the old `automation.toml` on
   the new PC; create the task through Codex.

## 2. Install and prepare the destination PC

Install:

- Codex desktop, signed into the intended ChatGPT account
- Git
- Python 3.12
- PostgreSQL client tools (`psql`, `pg_dump`, and `pg_restore`)
- Microsoft Excel desktop
- the official ChatGPT add-in for Excel, signed into the same intended account

Clone/copy the repository to a stable location. Example:

```powershell
cd C:\Users\<NEW_USER>\Desktop
git clone <YOUR_PRIVATE_REPOSITORY_URL> CTGTI_Agent\Scraper
cd C:\Users\<NEW_USER>\Desktop\CTGTI_Agent\Scraper
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Open this folder as a saved project in Codex. A local scheduled task requires
this project and machine to remain available when the task runs.

## 3. PostgreSQL setup

### Recommended: point both installations at the same managed PostgreSQL

This preserves companies, signals, keyword-company links, saved keywords,
search counters, identity corrections, and source-URL idempotency. Put the same
connection URL in the destination `.env`:

```dotenv
DATABASE_URL=postgresql://ctgti_scraper:<URL_ENCODED_PASSWORD>@<HOST>:5432/ctgti_leads?sslmode=require
```

Use the provider's required SSL mode. URL-encode reserved password characters;
for example, `@` becomes `%40`. Never paste the URL into the automation prompt
or commit it to Git.

If creating a new server/database, run the following as a PostgreSQL
administrator, choosing a strong password and restricting network access to the
two trusted devices or a VPN:

```sql
CREATE ROLE ctgti_scraper LOGIN PASSWORD '<STRONG_PASSWORD>';
CREATE DATABASE ctgti_leads OWNER ctgti_scraper;
```

Then run the project's idempotent schema initialization from the destination
repository:

```powershell
.\.venv\Scripts\python.exe -c "from dotenv import load_dotenv; load_dotenv(); from db.database import Database; db=Database(); db.initialize(); print('database initialized')"
```

### Alternative: migrate the current database to a new PostgreSQL server

Pause the old automation first. On the source PC, use a native PostgreSQL URL
(not an SQLAlchemy `postgresql+psycopg2://` URL):

```powershell
pg_dump --dbname="$env:DATABASE_URL" --format=custom --no-owner --file="C:\Temp\ctgti_leads.backup"
```

Transfer the backup securely. Create an empty destination database, set
`DATABASE_URL` to the destination, then restore:

```powershell
pg_restore --dbname="$env:DATABASE_URL" --no-owner --no-privileges "C:\Temp\ctgti_leads.backup"
.\.venv\Scripts\python.exe -c "from dotenv import load_dotenv; load_dotenv(); from db.database import Database; db=Database(); db.initialize(); print('database initialized')"
```

Do not initialize a blank production database and manually recreate only the
keywords if the old history is available. The other tables are necessary for
deduplication and historical qualification decisions.

## 4. Configure `.env`

At minimum, set `DATABASE_URL`. Keep any provider keys needed by the rest of the
project in `.env`, never in the Codex task prompt. The research automation uses
Codex's browser/search surfaces, but other pipeline commands can require the
provider keys listed in `.env.example`.

Verify connectivity and the persistent keyword inventory:

```powershell
.\.venv\Scripts\python.exe -c "from dotenv import load_dotenv; load_dotenv(); from db.database import Database; db=Database(); db.initialize(); rows=db.list_keywords(); print('keyword_count=',len(rows)); [print(x.id, x.google_xray_enabled, x.keyword) for x in rows]"
```

The migrated database should currently contain 15 saved keywords. The task
must load them with `Database.list_keywords()` on every run; do not hard-code
the list into the automation.

## 5. Prepare the canonical Excel connection

1. Sign into OneDrive and Excel with the account that owns the existing
   `Keyword_Companies.xlsx`.
2. Open the existing OneDrive workbook in Excel desktop. Do not upload, rename,
   copy, replace, or use Save As.
3. Confirm it has `Summary`, `Keyword Companies`, and the Excel table
   `KeywordCompaniesTable`.
4. Open the official ChatGPT add-in, sign in, and leave it connected.
5. Leave exactly one workbook named `Keyword_Companies.xlsx` open. The task is
   deliberately forbidden from opening Excel or resolving ambiguous sessions.

The database remains authoritative. If Excel is closed or disconnected at run
time, PostgreSQL work should still finish and workbook sync should fail safely
for retry.

For the optional local staging workbook, use a stable destination path rather
than the old PC's transient Codex worktree path, for example:

```text
C:\Users\<NEW_USER>\Desktop\CTGTI_Agent\Scraper\outputs\Keyword_Companies.xlsx
```

Copy the existing staging file there if desired. Do not open it in Excel while
the canonical workbook is open.

## 6. Export the exact prompt with new paths

On the source device, the helper can replace both device-specific paths while
keeping every other character of the current task prompt:

```powershell
.\.venv\Scripts\python.exe .\scripts\export_codex_automation_prompt.py `
  --project-root "C:\Users\<NEW_USER>\Desktop\CTGTI_Agent\Scraper" `
  --staging-workbook "C:\Users\<NEW_USER>\Desktop\CTGTI_Agent\Scraper\outputs\Keyword_Companies.xlsx" |
  Set-Clipboard
```

Paste the clipboard contents into a temporary local text editor only if you
want to inspect it. This output is the exact operational task prompt, including
the research gates, source matrix, scoring thresholds, identity verification,
database publication rules, and append-only Excel rules.

## 7. Create the task in Codex

In the destination Codex project, paste the following request into a new chat.
Replace the final placeholder by pasting the exported operational prompt:

```text
Create one recurring automation for the project currently open in Codex.

Name: Daily Keyword Company Research
Run: every day at 3:00 PM Asia/Kolkata time
Execution environment: local project checkout
Model: gpt-5.6-sol (if unavailable, use gpt-6.1-sol)
Reasoning effort: high
Notifications: failed runs only
Initial status: paused

Use the operational task prompt below verbatim. Do not shorten, summarize, or
rewrite it. Do not create a second automation if one with this name is already
present; show me the existing task instead. Keep the task paused until I verify
the database, the next-run time, and that the old device's task is paused.

--- BEGIN OPERATIONAL TASK PROMPT ---
<PASTE THE EXPORTED PROMPT HERE>
--- END OPERATIONAL TASK PROMPT ---
```

When Codex shows the task, verify:

- project path is the destination repository
- next run is 3:00 PM India Standard Time
- local environment is selected
- reasoning is high
- notifications are failure-only
- the prompt contains the new project and staging-workbook paths

Then activate the new task only after the old task is paused.

## 8. First-run validation

Run the task manually once while watching it. Confirm:

1. `Database.initialize()` succeeds.
2. `Database.list_keywords()` returns all 15 saved keywords.
3. Every keyword receives a search attempt and a final
   `Database.record_keyword_search()` call.
4. Qualified/watchlist publication uses `persist_verified_signal()` and is
   idempotent by source URL.
5. No disqualified, needs-review, directory-only, or unverifiable new company is
   inserted.
6. Exactly one canonical Excel session is discovered.
7. Workbook reconciliation is append/upsert-only and reports zero rows removed.
8. Closing Excel causes only a workbook-sync warning, not a database rollback.
9. A second overlapping invocation exits safely without writes.

After the first successful run, compare database counts and inspect the task's
run report before leaving the daily schedule active.

## 9. Cutover checklist

- [ ] Old scheduled task paused
- [ ] Repository copied/cloned and dependencies installed
- [ ] `.env` created locally and excluded from Git
- [ ] Existing PostgreSQL database shared or fully restored
- [ ] 15 persistent keywords visible
- [ ] Existing OneDrive workbook open exactly once in Excel desktop
- [ ] ChatGPT Excel add-in signed in and connected
- [ ] Exact operational prompt exported with destination paths
- [ ] New task created paused, checked, and manually tested
- [ ] New task activated only after the old task is disabled
- [ ] Destination PC stays awake with Codex running at the scheduled time

## Official Codex references

- Scheduled tasks: https://learn.chatgpt.com/docs/automations
- Worktrees and local checkouts: https://learn.chatgpt.com/docs/environments/git-worktrees
- Codex best practices: https://learn.chatgpt.com/guides/best-practices
