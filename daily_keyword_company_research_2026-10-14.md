# Daily Keyword Company Research — 2026-10-14

Run started at 2026-10-14T09:30:17Z. PostgreSQL is authoritative and was initialized through `DATABASE_URL`; all 15 persistent keywords returned by `Database.list_keywords()` were researched and recorded once with `last_error=None`.

## Published prospects

### Hammond Manufacturing Company Limited — qualified, opportunity score 93

- Company ID: 2284
- Canonical domain: `hammfg.com`
- Keyword: Canadian companies recently raised funding and are developing hardware products
- Evidence: On October 2, 2026, Hammond announced a C$26.47 million Palmerston expansion, supported by C$3,971,250 from Ontario, that adds 85,000 square feet to a 97,000-square-foot plant, creates 30 jobs, retains about 98, and replicates laser cutting, punching, pressing, bending, welding, and powder-coating capacity for roughly 700 product variations.
- Opportunity: Teamcenter for product/manufacturing structures and changes, Tecnomatix for process and capacity planning, and Opcenter for scheduling, work instructions, genealogy, and quality during the ramp.
- Sources: [Wellington Advertiser](https://www.wellingtonadvertiser.com/hammond-manufacturing-expanding-palmerston-plant/) and [Hammond Manufacturing official release](https://www.hammfg.com/files/news/2026/2026-03-13-business-expansion-and-related-investment.pdf?v=1773667166).

### Jennmar Canada Ltd. — qualified, opportunity score 91

- Company ID: 2285
- Canonical domain: `jennmar.com`
- Keyword: Canadian companies recently raised funding and are developing hardware products
- Evidence: Ontario awarded C$400,000 on September 24, 2026 for an 8,934-square-foot Sudbury addition and new roll-forming line; FedNor had awarded C$1 million on April 24 for high-efficiency equipment to expand local production of bolts, cables, rebar, plates, and related steel ground-control products, with 25 expected jobs.
- Opportunity: Teamcenter for variants, tooling, suppliers, and released changes; Opcenter for scheduling, material genealogy, work instructions, and quality; Tecnomatix for line balance and process layout.
- Sources: [Ontario Newsroom](https://news.ontario.ca/en/release/1008041/ontario-investing-more-than-34-million-to-protect-manufacturing-jobs-in-the-north), [FedNor](https://www.canada.ca/en/fednor/news/2026/04/fednor-invests-close-to-3-million-to-help-greater-sudbury-businesses-respond-adapt-and-compete-amid-shifting-market-conditions.html), and [JENNMAR official Canadian operations page](https://www.jennmar.com/jennmar-international).

Four source URLs were inserted as distinct signal rows. `Database.persist_verified_signal()` was used for every write after official-domain and independent-source verification; no direct `save_signal()`, `persist_signal()`, or unconditional `upsert_company()` call was used. Keyword-company result IDs 410 and 411 were created for keyword 8. The post-write duplicate audit found zero duplicate canonical domains, source URLs, or keyword-company pairs. Eligible PostgreSQL companies now total 186.

## Per-keyword audit

| ID | Keyword | Reviewed | New domains | Rejected before persistence | Qualified | Watchlist | Existing/duplicates skipped |
|---:|---|---:|---:|---:|---:|---:|---:|
| 1 | aerospace startups in Canada formed in last month | 10 | 2 | 2 | 0 | 0 | 8 |
| 2 | robotics startups in Canada | 9 | 2 | 2 | 0 | 0 | 7 |
| 3 | shipbuilding companies in Canada | 8 | 1 | 1 | 0 | 0 | 7 |
| 4 | automotive startups in Canada | 9 | 2 | 2 | 0 | 0 | 7 |
| 5 | Energy companies in Canada | 9 | 2 | 2 | 0 | 0 | 7 |
| 7 | Canadian aerospace startups developing aircraft, UAV, drones or eVTOL | 11 | 3 | 3 | 0 | 0 | 8 |
| 8 | Canadian companies recently raised funding and are developing hardware products | 14 | 5 | 3 | 2 | 0 | 9 |
| 9 | Canadian aerospace companies with engineering and manufacturing operations | 11 | 2 | 2 | 0 | 0 | 9 |
| 10 | Canadian aerospace suppliers and Tier 1/Tier 2 manufacturers | 10 | 2 | 2 | 0 | 0 | 8 |
| 11 | Canadian automotive OEMs and vehicle manufacturers | 9 | 2 | 2 | 0 | 0 | 7 |
| 12 | Canadian companies implementing ERP and PLM integration | 7 | 1 | 1 | 0 | 0 | 6 |
| 13 | Canadian companies developing autonomous vehicles & drones | 10 | 2 | 2 | 0 | 0 | 8 |
| 14 | Canadian defense companies developing complex products | 11 | 3 | 3 | 0 | 0 | 8 |
| 15 | Canadian electric vehicle startups | 9 | 2 | 2 | 0 | 0 | 7 |
| 16 | Canadian manufacturers looking for PLM software | 8 | 2 | 2 | 0 | 0 | 6 |

No existing record was downgraded, hidden, or removed. Notable pre-persistence rejections were Andy's Trailers & Manufacturing (no independently verifiable official domain), Jubilant Radiopharma (credible facility trigger but no close saved-keyword match), and R.F. Contracting (service-led). Known companies including OSCP, Seaspan, NordSpace, Volatus, and Cyberworks Robotics were rediscovered and skipped where no stronger new keyword result was supported.

## Coverage and blockers

Each keyword received separate 30-day, 180-day, and 365-day fallback searches across six families: general web/news; government funding, contracts and procurement; specialist trade publications; accelerators, investors and university spinouts; associations, exhibitors and member directories; and company press, hiring, product and facility pages. Mandatory searches covered Startup Gallery, X.com, BetaKit, and NGen; SpaceQ and AIAC searches were also run for aerospace, drone, space, defence, and supplier keywords. Rotated sources included CanadaBuys, FedNor, Ontario funding notices, NGen, ventureLAB, CDL, MaRS, Communitech, APMA, OVIN, PLANT, Canadian Manufacturing, Electric Autonomy Canada, Naval News, Shipbuilding Association of Canada, Canada's Ocean Supercluster, Aero Montreal, DAIR Aerospace, and Oakville Chamber of Commerce.

Startup Gallery yielded no publishable lead. Direct X.com access failed with `ERR_CERT_AUTHORITY_INVALID`; the warning was not bypassed. After repeated source-specific searches, Google showed its unusual-traffic interstitial, so browsing stopped and the search-service fallback was used. The 15-domain breadth quota was not reached for any keyword; the table above reports the verified domains actually assessed. These source limitations did not prevent keyword research or PostgreSQL publication and were therefore not written to `KeywordRecord.last_error`.

## Workbook reconciliation

The exact connected OneDrive workbook `Keyword_Companies.xlsx` was the only registered Excel session. It contained the required `Summary` and `Keyword Companies` sheets and `KeywordCompaniesTable`.

- Canonical OneDrive workbook: 6 inserted, 0 updated, 193 unchanged, 0 failed, 0 removed.
- Inserted company IDs: 2280–2285. IDs 2280–2283 were pending from the prior run; IDs 2284–2285 are today's publications.
- `KeywordCompaniesTable` expanded non-destructively from `A3:AI196` to `A3:AI202` (199 data rows).
- Summary recalculated to 199 keyword-linked companies: 171 qualified and 28 watchlist.
- Formula-error scan: zero matches.
- Local staging workbook: 0 inserted, 0 updated, 128 last-known unchanged, 6 deferred/failed, 0 removed. It was not opened or rewritten because the single-open-workbook safeguard forbids opening a second workbook window.

