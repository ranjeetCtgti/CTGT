# Daily Keyword Company Research — 2026-10-13

Run completed at 2026-10-13 15:26 IST. PostgreSQL publication completed before workbook synchronization was attempted.

## Published companies

| company_id | Company | Domain | Qualification | Opportunity | Trigger | Evidence | Saved-keyword links |
|---:|---|---|---|---:|---:|---:|---|
| 2280 | Jones Microwave Inc. | jonesmicrowave.com | qualified | 94 | 96 | 98 | 8, 10, 14, 16 |
| 2281 | Pegasus Imagery Ltd. | flypegasus.ai | qualified | 96 | 98 | 92 | 7, 8, 9, 10, 14, 16 |
| 2282 | GKD Industries Ltd. | gkdindustries.com | qualified | 91 | 94 | 97 | 5, 10, 14, 16 |
| 2283 | MRO Electronic Supply Ltd. | mroelectronics.com | qualified | 92 | 92 | 95 | 10, 14, 16 |

Each company passed the official-domain and independent-source identity gate. Four unique evidence URLs were inserted through `Database.persist_verified_signal`; 17 keyword-company links were upserted. The post-write audit found no duplicate canonical domains, source URLs, or keyword-company pairs.

## Per-keyword results

`Raw/distinct` counts are search-result URLs inspected across the six query families. `Reviewed` is the deduplicated candidate-domain assessment count. `New` means not already present in the company/keyword ledger when assessed. Existing records upgraded or hidden were zero for every keyword.

| ID | Saved keyword | Raw/distinct | Reviewed | New | Rejected pre-persistence | Qualified | Watchlist | Existing/duplicate results skipped |
|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 1 | aerospace startups in Canada formed in last month | 34/29 | 16 | 6 | 16 | 0 | 0 | 10 |
| 2 | robotics startups in Canada | 35/33 | 18 | 7 | 18 | 0 | 0 | 11 |
| 3 | shipbuilding companies in Canada | 31/29 | 16 | 5 | 16 | 0 | 0 | 11 |
| 4 | automotive startups in Canada | 37/34 | 18 | 7 | 18 | 0 | 0 | 11 |
| 5 | Energy companies in Canada | 33/33 | 17 | 7 | 16 | 1 | 0 | 10 |
| 7 | Canadian aerospace startups developing aircraft, UAV, drones or eVTOL | 39/39 | 21 | 9 | 20 | 1 | 0 | 12 |
| 8 | Canadian companies recently raised funding and are developing hardware products | 35/32 | 19 | 9 | 17 | 2 | 0 | 10 |
| 9 | Canadian aerospace companies with engineering and manufacturing operations | 39/36 | 21 | 8 | 20 | 1 | 0 | 13 |
| 10 | Canadian aerospace suppliers and Tier 1/Tier 2 manufacturers | 34/32 | 20 | 9 | 16 | 4 | 0 | 11 |
| 11 | Canadian automotive OEMs and vehicle manufacturers | 35/30 | 17 | 6 | 17 | 0 | 0 | 11 |
| 12 | Canadian companies implementing ERP and PLM integration | 36/34 | 18 | 7 | 18 | 0 | 0 | 11 |
| 13 | Canadian companies developing autonomous vehicles & drones | 36/35 | 19 | 8 | 19 | 0 | 0 | 11 |
| 14 | Canadian defense companies developing complex products | 33/33 | 20 | 10 | 16 | 4 | 0 | 10 |
| 15 | Canadian electric vehicle startups | 37/36 | 18 | 7 | 18 | 0 | 0 | 11 |
| 16 | Canadian manufacturers looking for PLM software | 36/35 | 19 | 10 | 15 | 4 | 0 | 9 |

All 15 keyword search counters advanced exactly once, `last_result_count` matches the qualified plus watchlist publication count, and every `last_error` is null.

## Coverage and source outcomes

- Lookbacks: rolling 30 days, 180 days, and 365-day fallback for ongoing capacity, contract, certification, hiring, commercialization, and facility signals.
- Query families: general web/news; government funding/contracts/procurement; specialist trade reporting; accelerators/investors/university spinouts; associations/exhibitors/member directories; company hiring/press/product/facility pages.
- Direct and indexed discovery: Startup Gallery's working Canada collection was inspected after its `/canada` route returned 404. Separate indexed Startup Gallery queries were run for every saved keyword and returned zero relevant results. X.com's direct public search stopped at `ERR_CERT_AUTHORITY_INVALID`; the warning was not bypassed. Separate indexed X queries were then run for every saved keyword; no candidate from those results passed the official-identity, physical-product, and dated-trigger gates.
- Mandatory source-specific searches: BetaKit and NGen for every keyword. Aerospace/space/defence passes additionally checked SpaceQ and AIAC. Rotated sources included Skies Magazine, CADSI, APMA, OVIN, Electric Autonomy Canada, Naval News, Shipbuilding Association of Canada, Canada's Ocean Supercluster, ventureLAB Hardware Catalyst, CanadaBuys, PrairiesCan, FedDev Ontario, Aero Montreal, DAIR Aerospace, Oakville Chamber of Commerce, company press/hiring pages, and French-language Quebec searches.
- The first full pass produced four publishable companies, so the zero-new-company gap-fill pass was not triggered.

## Workbook synchronization

- Canonical OneDrive workbook: no connected Excel document session was registered (`executors: []`). Per the single-run safeguard, no workbook was opened, created, renamed, duplicated, replaced, or edited. Inserted 0; updated 0; last-known unchanged 193; failed/deferred 4; removed 0.
- Local staging workbook: the file remains present at the required path (62,153 bytes; last modified 2026-08-04 07:16:29 UTC). It was not opened because doing so would violate the open-workbook reuse rule. Inserted 0; updated 0; last-known unchanged 128; failed/deferred 4; removed 0.
- PostgreSQL was not rolled back and keyword `last_error` was not used for either workbook warning.

## Validation limitation

The run script compiled successfully. The repository's identity-verification pytest suite could not execute because `pytest` is not installed in the active virtual environment; the production persistence path still ran its built-in identity verification for every signal before writing.
