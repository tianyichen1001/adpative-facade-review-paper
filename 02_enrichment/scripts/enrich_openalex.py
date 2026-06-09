"""OpenAlex (primary) metadata enrichment for the adaptive-facade corpus (Stage 02).

Input : 01_search/raw/scopus_raw.csv (N=2831; eid / doi / title / year / ...)
Outputs:
  02_enrichment/openalex_raw.jsonl   full nested OpenAlex records (for later
                                     co-citation / bibliographic coupling)
  02_enrichment/openalex_flat.csv    eid + flattened oa_* columns (one row per
                                     corpus record; blanks where unmatched)

Strategy (PROJECT_MEMORY.md §6):
  - DOI'd records: batch fetch via OpenAlex `doi` filter, 50 DOIs/request (OR-piped).
  - No-DOI records: title search + year(±1); accept only if normalized title
    similarity >= 0.9 (else oa_match = 'low'/'none'). Low match rate is expected.

API is free, no key. Polite-pool `mailto` only (not a secret; appears in headers).
"""

import json
import re
import sys
from difflib import SequenceMatcher
from pathlib import Path

import pandas as pd
import pyalex
from pyalex import Works

MAILTO = "tianyi.chen1001@gmail.com"
pyalex.config.email = MAILTO
pyalex.config.max_retries = 3
pyalex.config.retry_backoff_factor = 0.5

ROOT = Path(__file__).resolve().parents[1]
CORPUS_CSV = ROOT.parent / "01_search" / "raw" / "scopus_raw.csv"
RAW_JSONL = ROOT / "openalex_raw.jsonl"
FLAT_CSV = ROOT / "openalex_flat.csv"

BATCH = 50
TITLE_SIM_THRESHOLD = 0.90


def norm_doi(doi):
    if not isinstance(doi, str) or not doi.strip():
        return None
    d = doi.strip().lower()
    d = re.sub(r"^https?://(dx\.)?doi\.org/", "", d)
    return d or None


def norm_title(t):
    return re.sub(r"[^a-z0-9 ]+", " ", (t or "").lower())
    # collapse handled by similarity tokens


def title_sim(a, b):
    na = re.sub(r"\s+", " ", norm_title(a)).strip()
    nb = re.sub(r"\s+", " ", norm_title(b)).strip()
    return SequenceMatcher(None, na, nb).ratio()


def flatten(work, match, sim=None):
    """Flatten an OpenAlex work record into oa_* fields."""
    auths = work.get("authorships", []) or []
    authors = [a["author"]["display_name"] for a in auths if a.get("author")]
    insts, rors, countries = [], [], []
    for a in auths:
        for inst in a.get("institutions", []) or []:
            if inst.get("display_name"):
                insts.append(inst["display_name"])
            if inst.get("ror"):
                rors.append(inst["ror"])
        for c in a.get("countries", []) or []:
            countries.append(c)

    def uniq(seq):
        seen, out = set(), []
        for x in seq:
            if x and x not in seen:
                seen.add(x)
                out.append(x)
        return out

    concepts = work.get("concepts", []) or []
    concept_str = "; ".join(
        f"{c['display_name']}:{round(c.get('score', 0), 3)}" for c in concepts[:8])
    topics = work.get("topics", []) or []
    topic_str = "; ".join(t.get("display_name", "") for t in topics[:3])

    ploc = work.get("primary_location") or {}
    src = (ploc.get("source") or {}) if ploc else {}
    issns = (src.get("issn") or []) if src else []

    return {
        "oa_match": match,
        "oa_title_sim": round(sim, 3) if sim is not None else None,
        "openalex_id": work.get("id"),
        "oa_authors": "; ".join(authors),
        "oa_n_authors": len(authors),
        "oa_institutions": "; ".join(uniq(insts)),
        "oa_countries": "; ".join(uniq(countries)),
        "oa_rors": "; ".join(uniq(rors)),
        "oa_concepts": concept_str,
        "oa_topics": topic_str,
        "oa_n_referenced_works": len(work.get("referenced_works", []) or []),
        "oa_cited_by_count": work.get("cited_by_count"),
        "oa_counts_by_year": json.dumps(work.get("counts_by_year", []) or []),
        "oa_is_oa": (work.get("open_access") or {}).get("is_oa"),
        "oa_oa_status": (work.get("open_access") or {}).get("oa_status"),
        "oa_source": src.get("display_name") if src else None,
        "oa_issn": "; ".join(issns),
        "oa_pub_year": work.get("publication_year"),
        "oa_type": work.get("type"),
    }


def empty_flat(match):
    f = {k: None for k in flatten({}, match)}
    f["oa_match"] = match
    f["oa_n_authors"] = 0
    f["oa_n_referenced_works"] = 0
    return f


def main():
    df = pd.read_csv(CORPUS_CSV)
    df["_ndoi"] = df["doi"].apply(norm_doi)
    has_doi = df[df["_ndoi"].notna()].copy()
    no_doi = df[df["_ndoi"].isna()].copy()
    print(f"[corpus] total={len(df)}  with_doi={len(has_doi)}  no_doi={len(no_doi)}")

    flat_by_eid = {}
    jsonl_fh = RAW_JSONL.open("w", encoding="utf-8")
    n_written_raw = 0

    # --- DOI batches ------------------------------------------------------------
    doi_to_eids = {}
    for _, r in has_doi.iterrows():
        doi_to_eids.setdefault(r["_ndoi"], []).append(r["eid"])
    unique_dois = list(doi_to_eids.keys())
    print(f"[openalex] DOI batches: {len(unique_dois)} unique DOIs "
          f"in {(-(-len(unique_dois)//BATCH))} requests")

    matched_dois = set()
    for i in range(0, len(unique_dois), BATCH):
        chunk = unique_dois[i:i + BATCH]
        try:
            results = Works().filter(doi="|".join(chunk)).get(per_page=BATCH)
        except Exception as exc:  # noqa: BLE001
            print(f"  ! batch {i//BATCH} failed: {exc}")
            results = []
        for w in results:
            nd = norm_doi(w.get("doi"))
            if nd is None or nd not in doi_to_eids:
                continue
            matched_dois.add(nd)
            jsonl_fh.write(json.dumps(w) + "\n")
            n_written_raw += 1
            flat = flatten(w, "doi")
            for eid in doi_to_eids[nd]:
                flat_by_eid[eid] = flat
        if (i // BATCH) % 10 == 0:
            print(f"  .. {i+len(chunk)}/{len(unique_dois)} DOIs processed")

    # DOI'd but not found in OpenAlex
    for nd, eids in doi_to_eids.items():
        if nd not in matched_dois:
            for eid in eids:
                flat_by_eid[eid] = empty_flat("none")
    print(f"[openalex] DOI matched: {len(matched_dois)}/{len(unique_dois)} unique DOIs")

    # --- No-DOI title search ----------------------------------------------------
    n_title_ok = n_title_low = 0
    for j, (_, r) in enumerate(no_doi.iterrows(), 1):
        title = str(r.get("title") or "")
        try:
            year = int(float(r.get("year"))) if pd.notna(r.get("year")) else None
        except (ValueError, TypeError):
            year = None
        best, best_sim = None, 0.0
        if title.strip():
            try:
                cand = Works().search_filter(title=norm_title(title)).get(per_page=5)
            except Exception:  # noqa: BLE001
                cand = []
            for w in cand:
                if year is not None and w.get("publication_year") is not None:
                    if abs(int(w["publication_year"]) - year) > 1:
                        continue
                s = title_sim(title, w.get("title") or w.get("display_name") or "")
                if s > best_sim:
                    best, best_sim = w, s
        if best is not None and best_sim >= TITLE_SIM_THRESHOLD:
            jsonl_fh.write(json.dumps(best) + "\n")
            n_written_raw += 1
            flat_by_eid[r["eid"]] = flatten(best, "title", best_sim)
            n_title_ok += 1
        else:
            f = empty_flat("low" if best is not None else "none")
            f["oa_title_sim"] = round(best_sim, 3) if best is not None else None
            flat_by_eid[r["eid"]] = f
            n_title_low += 1
        if j % 50 == 0:
            print(f"  .. no-doi {j}/{len(no_doi)} (title-matched so far {n_title_ok})")

    jsonl_fh.close()
    print(f"[openalex] title matched (>= {TITLE_SIM_THRESHOLD}): "
          f"{n_title_ok}/{len(no_doi)}; unmatched/low: {n_title_low}")
    print(f"[openalex] raw records written to jsonl: {n_written_raw}")

    # --- Assemble flat csv keyed by eid (preserve corpus order) -----------------
    flat_rows = []
    for _, r in df.iterrows():
        f = flat_by_eid.get(r["eid"], empty_flat("none"))
        flat_rows.append({"eid": r["eid"], **f})
    flat_df = pd.DataFrame(flat_rows)
    flat_df.to_csv(FLAT_CSV, index=False)
    print(f"[saved] {FLAT_CSV}  ({len(flat_df)} rows)")

    # --- Coverage report --------------------------------------------------------
    n = len(flat_df)
    def pct(mask):
        return f"{mask.sum()}/{n} = {100*mask.sum()/n:.1f}%"
    print("\n[coverage] OpenAlex")
    print("  match=doi   :", (flat_df["oa_match"] == "doi").sum())
    print("  match=title :", (flat_df["oa_match"] == "title").sum())
    print("  unmatched   :", flat_df["oa_match"].isin(["none", "low"]).sum())
    print("  has concepts:", pct(flat_df["oa_concepts"].fillna("").str.len() > 0))
    print("  has authors :", pct(flat_df["oa_n_authors"].fillna(0) > 0))
    inst_country = (flat_df["oa_institutions"].fillna("").str.len() > 0) & \
                   (flat_df["oa_countries"].fillna("").str.len() > 0)
    print("  has inst+ctry:", pct(inst_country))
    print("  has refs    :", pct(flat_df["oa_n_referenced_works"].fillna(0) > 0))


if __name__ == "__main__":
    sys.exit(main())
