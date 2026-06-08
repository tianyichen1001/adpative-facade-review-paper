"""Recover DOIs for the 316 no-DOI Stage-2 records via OpenAlex, with verification.

Two rounds (PROJECT_MEMORY.md §6 — title+year matching, low-confidence rejected):
  1. enriched_oa : reuse the OpenAlex record already matched during enrichment
                   (openalex_id in enriched.csv -> doi in openalex_raw.jsonl).
  2. fresh_oa    : for still-missing records, query OpenAlex live by title+year.

A recovered DOI is ACCEPTED only if BOTH:
  - normalized titles are identical OR token Jaccard >= 0.90, AND
  - |year_scopus - year_openalex| <= 1.
Otherwise the record stays no_doi.

Output: 04_abstracts/scrape_inputs/no_doi_recovered.csv
(eid, recovered_doi, doi_url, title, source, match_method, title_sim, year_diff)

Does NOT scrape abstracts. Free API, polite-pool mailto only.
"""

import json
import re
import sys
import time
from pathlib import Path

import pandas as pd
import pyalex
from pyalex import Works

MAILTO = "tianyi.chen1001@gmail.com"
pyalex.config.email = MAILTO
pyalex.config.max_retries = 3
pyalex.config.retry_backoff_factor = 0.5

ROOT = Path(__file__).resolve().parents[1]            # 04_abstracts/
SCRAPE_DIR = ROOT / "scrape_inputs"
NO_DOI = SCRAPE_DIR / "no_doi.csv"
ENRICHED = ROOT.parent / "02_enrichment" / "enriched.csv"
OA_JSONL = ROOT.parent / "02_enrichment" / "openalex_raw.jsonl"
OUT = SCRAPE_DIR / "no_doi_recovered.csv"

JACCARD_MIN = 0.90


def norm(t):
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ]+", " ", str(t or "").lower())).strip()


def jaccard(a, b):
    ta, tb = set(norm(a).split()), set(norm(b).split())
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / len(ta | tb)


def verify(scopus_title, oa_title, scopus_year, oa_year):
    """Return (ok, sim, year_diff)."""
    na, nb = norm(scopus_title), norm(oa_title)
    sim = 1.0 if (na and na == nb) else jaccard(scopus_title, oa_title)
    yd = None
    try:
        yd = abs(int(float(scopus_year)) - int(float(oa_year)))
    except (TypeError, ValueError):
        yd = None
    ok = sim >= JACCARD_MIN and yd is not None and yd <= 1
    return ok, round(sim, 3), yd


def norm_doi(doi):
    if not doi:
        return None
    d = str(doi).strip().lower()
    d = re.sub(r"^https?://(dx\.)?doi\.org/", "", d)
    return d or None


def main():
    nod = pd.read_csv(NO_DOI)
    e = pd.read_csv(ENRICHED)[["eid", "openalex_id", "year"]]
    nod = nod.merge(e, on="eid", how="left")
    print(f"[input] no_doi records: {len(nod)}")

    # OpenAlex id -> (doi, title, year) from the cached raw records
    id_map = {}
    for line in open(OA_JSONL, encoding="utf-8"):
        r = json.loads(line)
        id_map[r.get("id")] = (r.get("doi"), r.get("title") or r.get("display_name"),
                               r.get("publication_year"))

    recovered = []
    remaining = []

    # ---- Round 1: enriched_oa --------------------------------------------------
    for _, row in nod.iterrows():
        oaid = row.get("openalex_id")
        rec = id_map.get(oaid) if isinstance(oaid, str) else None
        accepted = False
        if rec and rec[0]:
            doi = norm_doi(rec[0])
            ok, sim, yd = verify(row["title"], rec[1], row.get("year"), rec[2])
            if doi and ok:
                recovered.append({
                    "eid": row["eid"], "recovered_doi": doi,
                    "doi_url": f"https://doi.org/{doi}", "title": row["title"],
                    "source": row["source"], "match_method": "enriched_oa",
                    "title_sim": sim, "year_diff": yd})
                accepted = True
        if not accepted:
            remaining.append(row)
    print(f"[round1 enriched_oa] recovered: {len(recovered)}; remaining: {len(remaining)}")

    # ---- Round 2: fresh_oa -----------------------------------------------------
    n_fresh = 0
    for j, row in enumerate(remaining, 1):
        title = str(row["title"] or "")
        if not title.strip():
            continue
        try:
            cands = Works().search_filter(title=norm(title)).get(per_page=5)
        except Exception:  # noqa: BLE001
            cands = []
            time.sleep(1.0)
        best, best_sim, best_yd = None, 0.0, None
        for w in cands:
            ok, sim, yd = verify(title, w.get("title") or w.get("display_name"),
                                 row.get("year"), w.get("publication_year"))
            if w.get("doi") and ok and sim > best_sim:
                best, best_sim, best_yd = w, sim, yd
        if best is not None:
            doi = norm_doi(best.get("doi"))
            recovered.append({
                "eid": row["eid"], "recovered_doi": doi,
                "doi_url": f"https://doi.org/{doi}", "title": row["title"],
                "source": row["source"], "match_method": "fresh_oa",
                "title_sim": best_sim, "year_diff": best_yd})
            n_fresh += 1
        if j % 50 == 0:
            print(f"  .. fresh {j}/{len(remaining)} (recovered so far {n_fresh})")
        time.sleep(0.1)
    print(f"[round2 fresh_oa] recovered: {n_fresh}")

    rec_df = pd.DataFrame(recovered)
    rec_df.to_csv(OUT, index=False)
    n_rec = len(rec_df)
    print(f"\n[saved] {OUT}  ({n_rec} recovered)")
    print(f"[summary] total recovered {n_rec}/{len(nod)} "
          f"(enriched_oa={sum(r['match_method']=='enriched_oa' for r in recovered)}, "
          f"fresh_oa={n_fresh}); still no_doi = {len(nod) - n_rec}")
    return rec_df


if __name__ == "__main__":
    main()
    sys.exit(0)
