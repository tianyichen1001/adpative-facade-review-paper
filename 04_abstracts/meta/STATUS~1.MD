# Abstract scraping — status handoff

**State:** All 17 publishers were swept (180 shards). Every shard's results are saved as
`slice_<publisher>_<shard>.json` in this folder (`04_abstracts/`). These per-shard JSON files
are the primary deliverable and are complete on disk.

**One step remains — final aggregation.** The Linux VM that runs Python went down session-wide
near the end (`VM service not running`), so I could not run the merge that produces the three
roll-up files. The script is saved and ready:

- `merge_and_records.py` — run `python3 merge_and_records.py` once the VM is back. It produces:
  - `abstracts_all.json` — every collected abstract merged into one `{doi: abstract}` object
  - `missing_dois.csv` — every DOI we did NOT get an abstract for (publisher, shard, doi, doi_url)
  - `missing_shards.csv` — per-shard tally (input_n, got_n, missing_n, status)
  - `SUMMARY.md` — coverage table

When you're back, just say "run the merge" and I'll execute it and hand you those four files.

---

## Approximate coverage (from worker reports; exact numbers after merge runs)

~1,883 input DOIs. Roughly **~1,580–1,600 abstracts collected (~85%)**. Validated publishers are
near-complete; the gaps are concentrated in a few hard-blocked sites and the mixed `other` set.

| publisher | input | ~collected | notes |
|---|---|---|---|
| elsevier | 603 | ~581 | near-complete; ScienceDirect Cloudflare rate-limited the last shard |
| mdpi | 197 | ~190 | near-complete |
| springer | 170 | ~166 | near-complete |
| wiley | 38 | ~32 | Cloudflare contention; recovered most on retry |
| ieee | 85 | ~82 | near-complete |
| iop | 72 | ~72 | complete (Radware bot-wall cleared after warm-up) |
| taylor_francis | 91 | ~90 | complete |
| asce | 24 | ~22 | ascelibrary Cloudflare cleared after warm-up |
| **sage** | 23 | **0** | journals.sagepub.com Cloudflare never cleared — all missing |
| other | 485 | ~285 | mixed catch-all: many CumInCAD CAPTCHA / paywall / dead DOIs |
| acm | 20 | 18 | |
| **asme** | 17 | **0** | asmedigitalcollection.asme.org Cloudflare never cleared — all missing |
| wit | 15 | ~12 | |
| frontiers | 14 | 14 | complete |
| edp | 13 | 13 | complete |
| transtech | 11 | 11 | complete |
| nature | 5 | 5 | complete |

---

## Fully-blocked / empty shards (0 abstracts — need a different access route, e.g. institutional login)

- `sage_1`, `sage_2`, `sage_3` — all 23 SAGE DOIs (Cloudflare "Just a moment", never cleared)
- `asme_1`, `asme_2` — all 17 ASME DOIs (Cloudflare, never cleared)
- `elsevier_52` — 10 of 11 DOIs (ScienceDirect Cloudflare rate-limit after ~600 requests; 1 saved)

### SAGE missing DOIs (23)
10.1177/14780771241270265, 10.1177/01436244241306595, 10.1177/14780771231209457, 10.1177/01436244241264273, 10.1177/17442591231219793, 10.1177/0958305X241300428, 10.1177/23998083231171398, 10.1177/01436244231153839, 10.1177/1045389X211072202, 10.1177/1420326X211050114, 10.1177/17442591211045418, 10.1177/1420326X20903082, 10.1177/1478077119891840, 10.1177/1478077119886528, 10.1177/0020294019830115, 10.1177/0040517517729385, 10.1177/1477153516675392, 10.1177/1420326X14536066, 10.1177/1744259113496388, 10.1177/0143624413490177, 10.1177/1420326X07082497, 10.1177/109719639501800306

### ASME missing DOIs (17)
10.1115/1.4071458, 10.1115/1.4069135, 10.1115/1.4068810, 10.1115/1.4056928, 10.1115/IMECE2023-113117, 10.1115/1.4056394, 10.1115/1.4054775, 10.1115/1.4049432, 10.1115/SMASIS2020-2302, 10.1115/SMASIS2019-5674, 10.1115/ES2019-3909, 10.1115/IMECE2018-87050, 10.1115/1.4027154, 10.1115/JRC2014-3744, 10.1115/SMASIS2013-3001, 10.1115/RTDF2008-74025, 10.1115/ES2007-36256

### Elsevier shard 52 missing DOIs (10)
10.1016/j.buildenv.2012.10.003, 10.1016/j.buildenv.2012.06.009, 10.1016/j.enbuild.2012.07.020, 10.1016/j.engstruct.2012.04.023, 10.1016/j.engstruct.2012.02.006, 10.1016/j.enbuild.2012.02.048, 10.1016/j.solener.2012.02.031, 10.1016/j.enbuild.2011.11.022, 10.1016/j.solener.2011.11.016, 10.1016/j.egypro.2012.11.121

---

## Other scattered misses (the `merge_and_records.py` diff will list every one precisely)

Across the validated publishers there are ~20 single-DOI skips, almost all **old papers (1991–2014)**
whose DOIs mis-resolve or sit behind paywalls, plus genuinely dead/duplicate DOIs. In the `other`
set (~200 misses) the recurring causes are: CumInCAD conference pages behind a human-CAPTCHA,
Emerald / OUP / SAGE Cloudflare, reference-global 403s, ASHRAE/accuristech standards stores, and
DOIs that resolve to "Not Found". These are best-effort by design and several need
institutional access to retrieve.

## How the data was produced
- Per-DOI: navigate `doi.org/{DOI}` → run the v2 cropping JS → on STATE_OK pull text between
  `ZABSTRACTZ`/`ZENDZ` markers via get_page_text. STATE_CF/STATE_BOT → wait + retry (never solved a
  CAPTCHA). The cropping JS is embedded in `worker_README.md`.
- Cloudflare/Radware note: the first worker on a domain warms the clearance cookie; later same-domain
  shards pass directly. Very high concurrency on one CF domain (SAGE, ASME) causes the challenges to
  rate-limit each other — those are the blocks above.
