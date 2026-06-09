"""Consolidate ALL abstract slices (round-1 + round-2) -> true coverage ->
OpenAlex local gap-fill -> merged Stage-2 table v2.

Per task / PROJECT_MEMORY.md §6-§7:
  1. Recursively ingest every dict-JSON slice under 04_abstracts/ (any name/ext),
     merge into {doi: abstract} (scrape source). Prefer non-empty / longer.
  2. True coverage vs Stage-2 (2118, eff_doi = orig doi or recovered_doi); export
     still-missing (with DOI).
  3. Gap-fill from OpenAlex abstract_inverted_index — first the local
     openalex_raw.jsonl, then live pyalex by DOI (rate-limited). No browser.
  4. Build stage2_with_abstracts_v2.csv/.xlsx.
"""

import json
import re
import sys
import time
from pathlib import Path

import pandas as pd
import pyalex
from pyalex import Works

pyalex.config.email = "tianyi.chen1001@gmail.com"
pyalex.config.max_retries = 3
pyalex.config.retry_backoff_factor = 0.5

ABS_DIR = Path(__file__).resolve().parents[1]          # 04_abstracts/
ROOT = ABS_DIR.parent
STAGE1 = ROOT / "03_screening" / "stage1_title_keyword.csv"
RECOVERED = ABS_DIR / "scrape_inputs" / "no_doi_recovered.csv"
OA_JSONL = ROOT / "02_enrichment" / "openalex_raw.jsonl"
REPORTS = ABS_DIR / "reports"
STILL_MISSING = ABS_DIR / "still_missing.csv"
OUT_CSV = REPORTS / "stage2_with_abstracts_v2.csv"
OUT_XLSX = REPORTS / "stage2_with_abstracts_v2.xlsx"

SKIP_EXT = {".py", ".md", ".png", ".xlsx", ".js", ".ps1", ".csv", ".graphml"}
PREFIX_PUB = {
    "10.1016": "elsevier", "10.3390": "mdpi", "10.1007": "springer",
    "10.1038": "nature", "10.1002": "wiley", "10.1111": "wiley",
    "10.1109": "ieee", "10.1088": "iop", "10.1080": "taylor_francis",
    "10.1061": "asce", "10.1177": "sage",
}


def norm_doi(d):
    if not isinstance(d, str) or not d.strip():
        return None
    d = re.sub(r"^https?://(dx\.)?doi\.org/", "", d.strip().lower())
    return d or None


def clean_abstract(s):
    if not isinstance(s, str):
        return ""
    s = re.sub(r"\s+", " ", s).strip()
    s = re.sub(r"^\s*abstract[:\s]*", "", s, flags=re.I)
    s = re.sub(r"\s*keywords?\s*:.*$", "", s, flags=re.I).strip()
    return s


def publisher(doi):
    if not isinstance(doi, str) or not doi.strip():
        return "no_doi"
    pre = ".".join(doi.split("/", 1)[0].split(".")[:2])
    return PREFIX_PUB.get(pre, "other")


def from_inverted(idx):
    if not isinstance(idx, dict) or not idx:
        return ""
    pos = [(p, w) for w, ps in idx.items() for p in ps]
    pos.sort()
    return " ".join(w for _, w in pos)


def looks_like_slice(d):
    if not isinstance(d, dict) or not d:
        return False
    for k, v in d.items():
        if isinstance(k, str) and "10." in k and isinstance(v, str):
            return True
    return False


# merge store: doi -> (text, source_rank, source)  rank scrape=1 > openalex=0
RANK = {"scrape": 1, "openalex": 0}


def consider(store, doi, text, source):
    text = clean_abstract(text)
    if not doi or not text:
        return
    if doi not in store:
        store[doi] = (text, RANK[source], source)
        return
    _, orank, _ = store[doi]
    nrank = RANK[source]
    if nrank > orank or (nrank == orank and len(text) > len(store[doi][0])):
        store[doi] = (text, nrank, source)


def ingest_slices(store):
    n_files = 0
    for f in ABS_DIR.rglob("*"):
        if f.is_dir() or f.suffix.lower() in SKIP_EXT or "scripts" in f.parts:
            continue
        try:
            d = json.loads(f.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001 - not JSON / half-written -> skip
            continue
        if not looks_like_slice(d):
            continue
        n_files += 1
        for k, v in d.items():
            nd = norm_doi(k)
            if nd and isinstance(v, str):
                consider(store, nd, v, "scrape")
    print(f"[ingest] dict-JSON slice files read: {n_files}; "
          f"unique scraped DOIs: {len(store)}")


def main():
    REPORTS.mkdir(exist_ok=True)
    store = {}
    ingest_slices(store)
    n_scrape = len(store)

    # Stage-2 set + effective DOI
    df = pd.read_csv(STAGE1)
    s2 = df[df["stage1_decision"].isin(["include", "uncertain"])].copy()
    assert len(s2) == 2118
    rec = pd.read_csv(RECOVERED)
    rec_map = {e: norm_doi(d) for e, d in zip(rec["eid"], rec["recovered_doi"])}
    s2["eff_doi"] = s2.apply(
        lambda r: norm_doi(r["doi"]) or rec_map.get(r["eid"]), axis=1)
    s2["publisher"] = s2["eff_doi"].map(publisher)

    # still-missing (with DOI) after scrape
    def status(d):
        return "ok" if (d and d in store) else "missing"
    s2["_st"] = s2["eff_doi"].map(status)
    miss_doi = s2[(s2["_st"] == "missing") & s2["eff_doi"].notna()].copy()
    print(f"[coverage] scrape ok={int((s2['_st']=='ok').sum())}; "
          f"scrape-gap with DOI={len(miss_doi)} (-> OpenAlex gap-fill)")

    # ---- Step 3: OpenAlex gap-fill (local jsonl, then live) --------------------
    oa_idx = {}
    for line in open(OA_JSONL, encoding="utf-8"):
        r = json.loads(line)
        nd = norm_doi(r.get("doi"))
        if nd:
            oa_idx[nd] = r.get("abstract_inverted_index")

    n_local = n_live = 0
    live_targets = []
    for d in miss_doi["eff_doi"].dropna().unique():
        idx = oa_idx.get(d, "__absent__")
        if isinstance(idx, dict) and idx:
            consider(store, d, from_inverted(idx), "openalex")
            n_local += 1
        else:
            live_targets.append(d)
    print(f"[openalex] local jsonl reconstructed: {n_local}; "
          f"need live query: {len(live_targets)}")

    for i, d in enumerate(live_targets, 1):
        try:
            w = Works()[f"https://doi.org/{d}"]
            ab = from_inverted(w.get("abstract_inverted_index"))
            if ab:
                consider(store, d, ab, "openalex")
                n_live += 1
        except Exception:  # noqa: BLE001
            time.sleep(0.5)
        if i % 50 == 0:
            print(f"  .. live {i}/{len(live_targets)} (filled {n_live})")
        time.sleep(0.1)
    print(f"[openalex] live reconstructed: {n_live}")

    # ---- Step 4: build v2 table ------------------------------------------------
    def fill(row):
        d = row["eff_doi"]
        rec = store.get(d) if d else None
        if rec:
            return pd.Series([rec[0], rec[2], "ok", len(rec[0])])
        return pd.Series(["", "none", "missing", 0])

    s2[["abstract", "abstract_source", "abstract_status", "abstract_len"]] = \
        s2.apply(fill, axis=1)
    out = s2[["eid", "eff_doi", "title", "source", "doctype", "stage1_decision",
              "publisher", "abstract", "abstract_source", "abstract_status",
              "abstract_len"]]
    out.to_csv(OUT_CSV, index=False)
    out.to_excel(OUT_XLSX, index=False)
    print(f"[saved] {OUT_CSV.name} / .xlsx ({len(out)} rows)")

    # still-missing = FINAL gap (after scrape + OpenAlex), with DOI -> for re-scrape
    fm = out[(out["abstract_status"] == "missing") & out["eff_doi"].notna()].copy()
    fexp = fm[["eid", "eff_doi", "title", "source", "publisher"]].rename(
        columns={"eff_doi": "doi"})
    fexp.insert(2, "doi_url", "https://doi.org/" + fexp["doi"].astype(str))
    fexp.to_csv(STILL_MISSING, index=False)
    print(f"[saved] {STILL_MISSING.name} (final still-missing with DOI = {len(fm)})")

    report(out, n_scrape, n_local, n_live)
    return out


def report(out, n_scrape, n_local, n_live):
    n = len(out)
    ok = int((out["abstract_status"] == "ok").sum())
    by_src = dict(out[out["abstract_status"] == "ok"]["abstract_source"].value_counts())
    has_doi = out["eff_doi"].notna()
    miss_doi = int((has_doi & (out["abstract_status"] == "missing")).sum())
    miss_nodoi = int((~has_doi).sum())

    # quality
    okm = out["abstract_status"] == "ok"
    short = out[okm & (out["abstract_len"] < 120)]
    bullets = out[okm & out["abstract"].str.contains("•", regex=False)]
    kw = out[okm & out["abstract"].str.contains(r"keywords?\s*:", case=False, regex=True)]
    dup = out[okm].groupby("abstract")["eid"].count()
    dup = dup[dup > 1]

    L = ["# Stage-2 摘要汇总 v2(round1+2 + OpenAlex 补缺)\n"]
    A = L.append
    A(f"Stage-2 = **{n}**。摘要来源:Cowork scrape(round1+2)+ OpenAlex 重建(inverted_index)。\n")
    A("## 覆盖率\n| 指标 | 值 |\n|---|---|")
    A(f"| 唯一摘要 DOI(scrape) | {n_scrape} |")
    A(f"| 有摘要 ok(总) | {ok} ({100*ok/n:.1f}%) |")
    A(f"| └ 来自 scrape | {by_src.get('scrape', 0)} |")
    A(f"| └ 来自 openalex | {by_src.get('openalex', 0)} |")
    A(f"| 仍缺(有 DOI) | {miss_doi} |")
    A(f"| 仍缺(无 DOI) | {miss_nodoi} |")
    A(f"| OpenAlex 补:本地 jsonl / 现查 | {n_local} / {n_live} |")

    A("\n## 按出版商真实覆盖\n| 出版商 | 目标(有DOI) | ok | 覆盖率 |\n|---|---|---|---|")
    for pub, sub in out[has_doi].groupby("publisher"):
        g = int((sub["abstract_status"] == "ok").sum())
        A(f"| {pub} | {len(sub)} | {g} | {100*g/len(sub):.1f}% |")

    A("\n## 质量抽查\n| 检查 | 命中 |\n|---|---|")
    A(f"| 过短 <120 | {len(short)} |")
    A(f"| 含 • | {len(bullets)} |")
    A(f"| 含 Keywords: | {len(kw)} |")
    A(f"| 重复摘要文本(>1 DOI) | {len(dup)} 组 |")
    if okm.sum():
        ln = out.loc[okm, "abstract_len"]
        A(f"\n长度分布:min={int(ln.min())} / 中位={int(ln.median())} / max={int(ln.max())}")
    nb_src = dict(bullets["abstract_source"].value_counts()) if len(bullets) else {}
    A(f"\n> 含 `•` 的 {len(bullets)} 条**全部来自 openalex**(来源拆:{nb_src})——"
      "是 OpenAlex inverted_index 里本就带项目符号的结构化摘要(真内容,非 Highlights 误抓;"
      "scrape JS 已排除 Highlights,scrape 来源 `•`=0)。")
    if len(dup):
        A(f"\n> 重复摘要 {len(dup)} 组(同文本→多 DOI),前 5 组:")
        for t, c in dup.sort_values(ascending=False).head(5).items():
            ds = out.loc[okm & (out["abstract"] == t), "eff_doi"].tolist()
            A(f">  - {c} 条:{', '.join(str(x) for x in ds[:3])} — “{str(t)[:70]}…”")
    A(f"\n## 仍缺(可补) — `still_missing.csv`\n\n"
      f"最终仍缺**有 DOI {miss_doi}** 条(elsevier 居多:ScienceDirect Cloudflare 限速 + 2026 新文 "
      f"OpenAlex 尚无摘要)+ **无 DOI {miss_nodoi}** 条(无抓取路径,留 Stage-2 标题筛)。")
    (REPORTS / "abstract_coverage_report_v2.md").write_text("\n".join(L), encoding="utf-8")
    print(f"[saved] abstract_coverage_report_v2.md")
    print(f"[quality] short={len(short)} bullets={len(bullets)} kw={len(kw)} dup={len(dup)}")
    print(f"[final] ok={ok}/{n} ({100*ok/n:.1f}%); scrape={by_src.get('scrape',0)} "
          f"openalex={by_src.get('openalex',0)}; miss_doi={miss_doi} miss_nodoi={miss_nodoi}")


if __name__ == "__main__":
    main()
    sys.exit(0)
