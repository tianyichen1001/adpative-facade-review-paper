"""Format the corpus DOIs into Scopus Advanced Search DOI-OR query batches.

Pure formatting (no data fetch). Per PROJECT_MEMORY.md §6.1: paste each batch into
Scopus advanced search -> export Abstract + Author keywords (+ References at the
metrics stage). Each DOI is wrapped DOI("<doi>") (quotes guard 1990s DOIs that
contain parentheses), joined with " OR ", batched to keep the query short enough.

Default input = Stage-2 set (stage2_with_abstracts_v3.csv eff_doi, ~1886 unique).
Pass --full to use the whole corpus (enriched.csv doi, ~2831).
"""

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]            # 04_abstracts/
STAGE2 = ROOT / "reports" / "stage2_with_abstracts_v3.csv"
ENRICHED = ROOT.parent / "02_enrichment" / "enriched.csv"
OUT_DIR = ROOT / "scopus_export"

N_PER_BATCH = 50   # 50 verified OK in Scopus; raise to 100 if accepted, drop if "query too long"


def norm_doi(d):
    if not isinstance(d, str) or not d.strip():
        return None
    d = d.strip()
    for pre in ("https://doi.org/", "http://doi.org/", "https://dx.doi.org/"):
        if d.lower().startswith(pre):
            d = d[len(pre):]
    return d.lower() or None


def load_dois(full=False):
    if full:
        col, src = "doi", ENRICHED
    else:
        col, src = "eff_doi", STAGE2
    s = pd.read_csv(src)[col].map(norm_doi).dropna()
    # de-dup, preserve first-seen order
    seen, out = set(), []
    for d in s:
        if d not in seen:
            seen.add(d)
            out.append(d)
    print(f"[input] {src.name}::{col} -> {len(out)} unique DOIs")
    return out


def main():
    full = "--full" in sys.argv
    dois = load_dois(full)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    # clear stale batch files
    for old in OUT_DIR.glob("query_batch_*.txt"):
        old.unlink()

    batches = [dois[i:i + N_PER_BATCH] for i in range(0, len(dois), N_PER_BATCH)]
    rows = []
    md = ["# Scopus DOI-OR 查询分批(逐批复制到 Scopus 高级检索)\n",
          f"总 DOI {len(dois)} · 批数 {len(batches)} · 每批 ≤{N_PER_BATCH}。"
          "每个 DOI 写作 `DOI(\"…\")`,用 ` OR ` 连接。\n"]
    for i, batch in enumerate(batches, 1):
        query = " OR ".join(f'DOI("{d}")' for d in batch)
        fname = f"query_batch_{i:02d}.txt"
        (OUT_DIR / fname).write_text(query + "\n", encoding="utf-8")
        rows.append((fname, len(batch), len(query)))
        md.append(f"## Batch {i:02d} — {len(batch)} DOIs, {len(query)} chars\n")
        md.append("```\n" + query + "\n```\n")
        print(f"  {fname}: {len(batch):3d} DOIs, {len(query):5d} chars")

    (OUT_DIR / "query_batches_all.md").write_text("\n".join(md), encoding="utf-8")
    print(f"[saved] {len(batches)} batch txt + query_batches_all.md -> {OUT_DIR}")
    print(f"[summary] {len(dois)} DOIs in {len(batches)} batches; "
          f"max chars = {max(r[2] for r in rows)}")


if __name__ == "__main__":
    main()
    sys.exit(0)
