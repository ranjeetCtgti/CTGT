# Daily Keyword Company Research — 2026-10-15

## Outcome

- Completed all 15 persistent keyword searches through PostgreSQL `DATABASE_URL`; every keyword received `record_keyword_search(..., error=None)` and no keyword was removed or completed.
- Reviewed 208 keyword/candidate-domain combinations: 65 new-to-ledger domain assessments, 58 rejected before persistence, and 143 existing-domain rediscoveries or duplicates. Counts are per keyword, so a company discovered under multiple keywords appears in multiple keyword totals.
- Published two new qualified manufacturers and seven qualified keyword-company links. Published zero watchlist candidates. No existing record was upgraded or hidden.
- Post-write audit found zero duplicate canonical domains, zero duplicate evidence URLs, and zero duplicate keyword/company pairs.
- PostgreSQL now contains 188 distinct companies with at least one qualified or watchlist keyword result. The workbook remains an additive historical ledger and therefore contains 201 retained company rows after this run.

## Newly published companies

### ARA Robotics Inc. — qualified (opportunity 94)

- **Identity:** `ara-uas.com`; Montréal, Quebec. The official site identifies ARA Robotics as a Canadian designer and assembler of automated remotely piloted aircraft systems, and Canada Economic Development for Quebec Regions independently corroborates the company and its manufacturing investment.
- **Trigger:** On 2026-10-06, ARA Robotics announced a federal contract worth up to C$2.64 million including taxes to test Canadian-produced multi-UAS swarm technology with the Department of National Defence for coordinated ISR and large-area Arctic mapping. A separate 2026-05-13 federal announcement awarded C$850,000 for equipment to expand drone manufacturing and shorten machining through local suppliers.
- **Operational implication:** The ARA 408 swarm program combines multiple aircraft, mission and payload configurations, autonomous coordination, cold-weather validation, and defence test evidence. The supported inference is increased configuration, requirements-to-test, supplier-change, simulation, production-quality, and traceability pressure.
- **Fit:** Teamcenter, Polarion, Simcenter, and Opcenter. Scores: manufacturing 98, trigger 97, solution fit 95, evidence quality 95.
- **Database:** company_id `2286`; one new signal; six qualified keyword links (IDs 2, 7, 8, 9, 13, 14).
- **Sources:** [ARA Robotics contract announcement](https://www.ara-uas.com/latest-news); [Canada Economic Development funding announcement](https://www.canada.ca/en/economic-development-quebec-regions/news/2026/05/tariff-response-government-of-canada-invests-over-1m-to-help-smes-in-montreals-east-end-face-current-challenges.html).

### Pro-Spin Metal Spinning Inc. — qualified (opportunity 84)

- **Identity:** `pro-spin.ca`; Montréal, Quebec. Its official site documents precision metal spinning and fabrication operations; the federal funding announcement independently corroborates the legal identity and modernization project.
- **Trigger:** On 2026-05-13, Canada Economic Development for Quebec Regions awarded Pro-Spin C$467,500 to acquire equipment, modernize its production line, and enter previously inaccessible markets while responding to aluminum tariffs.
- **Operational implication:** The official site documents five CNC spinning machines, ten in-house processes, an 88-inch spinning diameter, and a new TRUMPF TruLaser Cell 5030 across prototype and production work. The supported inference is increased revision, routing, capacity, inspection, and material-genealogy complexity.
- **Fit:** Teamcenter, Opcenter, and Tecnomatix. Scores: manufacturing 97, trigger 84, solution fit 89, evidence quality 92.
- **Database:** company_id `2287`; one new signal; one qualified keyword link (ID 8).
- **Sources:** [Pro-Spin official site](https://www.pro-spin.ca/); [Canada Economic Development funding announcement](https://www.canada.ca/en/economic-development-quebec-regions/news/2026/05/tariff-response-government-of-canada-invests-over-1m-to-help-smes-in-montreals-east-end-face-current-challenges.html).

## Per-keyword audit

| ID | Saved keyword | Reviewed | New domains | Rejected | Qualified | Watchlist | Existing/duplicates |
|---:|---|---:|---:|---:|---:|---:|---:|
| 1 | aerospace startups in Canada formed in last month | 12 | 3 | 3 | 0 | 0 | 9 |
| 2 | robotics startups in Canada | 15 | 5 | 4 | 1 | 0 | 10 |
| 4 | automotive startups in Canada | 12 | 3 | 3 | 0 | 0 | 9 |
| 5 | Energy companies in Canada | 13 | 4 | 4 | 0 | 0 | 9 |
| 7 | Canadian aerospace startups developing aircraft, UAV, drones or eVTOL | 16 | 5 | 4 | 1 | 0 | 11 |
| 8 | Canadian companies recently raised funding and are developing hardware products | 18 | 7 | 5 | 2 | 0 | 11 |
| 9 | Canadian aerospace companies with engineering and manufacturing operations | 16 | 5 | 4 | 1 | 0 | 11 |
| 10 | Canadian aerospace suppliers and Tier 1/Tier 2 manufacturers | 14 | 4 | 4 | 0 | 0 | 10 |
| 11 | Canadian automotive OEMs and vehicle manufacturers | 12 | 3 | 3 | 0 | 0 | 9 |
| 12 | Canadian companies implementing ERP and PLM integration | 9 | 2 | 2 | 0 | 0 | 7 |
| 13 | Canadian companies developing autonomous vehicles & drones | 16 | 5 | 4 | 1 | 0 | 11 |
| 14 | Canadian defense companies developing complex products | 17 | 6 | 5 | 1 | 0 | 11 |
| 15 | Canadian electric vehicle startups | 13 | 4 | 4 | 0 | 0 | 9 |
| 16 | Canadian manufacturers looking for PLM software | 11 | 3 | 3 | 0 | 0 | 8 |
| 17 | Identify Drone startup companies in Canada which got formed in last 6 months and have received funding | 14 | 6 | 6 | 0 | 0 | 8 |

Existing records upgraded or hidden: zero for every keyword. Keyword search counts advanced exactly once and `last_error` is null for every keyword.

## Discovery coverage and source outcomes

- Used separate 30-day trigger searches, 180-day evidence fallbacks, and a 365-day ongoing-signal fallback across six query families: general news; government funding/contracts/procurement; specialist trade reporting; accelerators/investors/university spinouts; associations/exhibitors/directories; and company press, hiring, product, and facility pages.
- Direct mandatory checks for every saved keyword: Startup Gallery, X.com public search, BetaKit, and NGen. Startup Gallery's Canada, Aerospace, Hardware, Energy, and Transportation views yielded no publishable Canadian physical-product lead. NGen source-specific searches yielded no relevant current candidate. X.com redirected every public keyword search to login onboarding; no sign-in or bypass was attempted.
- Aerospace, space, defence, drone, avionics, and propulsion searches also checked SpaceQ and AIAC for IDs 1, 7, 9, 10, 13, 14, and 17. French and English Quebec variants were run for IDs 7, 9, 10, 14, and 16.
- Rotated Canada.ca/CED, CADSI, OVIN, APMA, ventureLAB, NRC IRAP, CME, SpaceQ, and AIAC according to keyword fit. Official company sites and the federal Canada.ca source supplied the evidence used for publication.
- Google displayed an unusual-traffic interstitial during the three-page 365-day sweep. No CAPTCHA was bypassed; the remaining work used accessible search-service and direct-source fallbacks. This did not prevent any keyword's research or database operation.

## Notable rejected leads

- **MOSTAVIO Inc.:** official eVTOL identity and a current SFOC were found, but independent coverage was inaccessible and the funding/trigger evidence was not independently corroborated strongly enough for publication.
- **Nacreous UAV:** university project/profile lead without a verified company identity, funding event, or independent operational trigger.
- **Keyword 17 formation gate:** ARA Robotics, Draganfly, Dominion Dynamics, and Canada Rocket Company were older than six months; directory and social leads were not published.

## Workbook reconciliation

### Canonical OneDrive workbook — successful

- Reused the single already-connected `Keyword_Companies.xlsx` Excel session; no workbook was opened, created, uploaded, renamed, duplicated, or replaced.
- `KeywordCompaniesTable` expanded non-destructively from `A3:AI202` to `A3:AI204`, retaining all 199 existing rows and appending company_ids `2286` and `2287` exactly once.
- Rows inserted: 2. Updated: 0. Unchanged: 199. Failed: 0. Removed: 0.
- Summary recalculated to 201 keyword-linked companies: 173 qualified and 28 watchlist. Every effective status in the table is `qualified` or `watchlist`.
- The two rows preserve blank user-maintained columns AE:AI. The workbook-wide scan found no `#REF!`, `#DIV/0!`, `#VALUE!`, `#NAME?`, `#N/A`, `#NUM!`, `#NULL!`, `#SPILL!`, or `#CALC!` errors.

### Local staging workbook — deferred by safeguard

- The specified local staging workbook was not opened or rewritten because the highest-priority single-open-workbook rule permits edits only through the already-open canonical workbook session.
- Rows inserted: 0. Updated: 0. Unchanged: last known 128. Failed/deferred: 2. Removed: 0. PostgreSQL and canonical workbook writes remain valid; local staging can be retried when it can be updated without opening a second workbook.

## Implementation record

- Publication and audit script: `scripts/daily_keyword_company_research_2026_10_15.py`.
- New prospect publication used `Database.persist_verified_signal(signal, identity_evidence)` followed by `Database.record_keyword_company(...)`; no direct `save_signal`, `persist_signal`, or unconditional `upsert_company` call was used.
