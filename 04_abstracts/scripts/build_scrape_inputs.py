"""Build publisher-grouped scrape-input lists for Stage-2 abstract retrieval.

Stage-2 "possibly relevant" set = stage1_decision in {include, uncertain} (N=2118).
This script ONLY prepares the per-publisher input lists for Cowork (PROJECT_MEMORY.md
§7); it does NOT fetch any abstracts.

Publisher is inferred from the DOI registrant prefix (10.xxxx). Each group is written
to its own CSV under 04_abstracts/scrape_inputs/, plus a _manifest.md overview.
"""

import sys
from collections import Counter
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]            # 04_abstracts/
STAGE1 = ROOT.parent / "03_screening" / "stage1_title_keyword.csv"
OUT_DIR = ROOT / "scrape_inputs"

# DOI prefix -> (group filename stem, display name)
PREFIX_MAP = {
    "10.1016": ("elsevier", "Elsevier / ScienceDirect"),
    "10.1080": ("taylor_francis", "Taylor & Francis"),
    "10.3390": ("mdpi", "MDPI"),
    "10.1007": ("springer", "Springer"),
    "10.1038": ("nature", "Nature (Springer Nature)"),
    "10.1002": ("wiley", "Wiley"),
    "10.1111": ("wiley", "Wiley"),
    "10.1109": ("ieee", "IEEE"),
    "10.1061": ("asce", "ASCE"),
    "10.1115": ("asme", "ASME"),
    "10.1177": ("sage", "SAGE"),
    "10.1088": ("iop", "IOP"),
    "10.1051": ("edp", "EDP Sciences"),
    "10.4028": ("transtech", "Trans Tech"),
    "10.3389": ("frontiers", "Frontiers"),
    "10.1145": ("acm", "ACM"),
    "10.2495": ("wit", "WIT Press"),
}

# Groups that already have a working Cowork selector (PROJECT_MEMORY.md §7).
HAS_SELECTOR = {
    "elsevier": "有 (SOP §4a ScienceDirect/Elsevier)",
    "taylor_francis": "有 (SOP §4b Taylor & Francis)",
}


def norm_doi(doi):
    if not isinstance(doi, str) or not doi.strip():
        return None
    d = doi.strip()
    for pre in ("https://doi.org/", "http://doi.org/", "https://dx.doi.org/"):
        if d.lower().startswith(pre):
            d = d[len(pre):]
    return d or None


def prefix_of(doi):
    """Return the '10.xxxx' registrant prefix."""
    parts = doi.split("/", 1)[0].split(".")
    return ".".join(parts[:2]) if len(parts) >= 2 else doi


def group_of(doi):
    if not isinstance(doi, str) or not doi.strip():
        return ("no_doi", "No DOI")
    return PREFIX_MAP.get(prefix_of(doi), ("other", "Other (has DOI)"))


def main():
    df = pd.read_csv(STAGE1)
    sel = df[df["stage1_decision"].isin(["include", "uncertain"])].copy()
    print(f"[input] Stage-2 set = {len(sel)} records")
    assert len(sel) == 2118, f"expected 2118, got {len(sel)}"

    sel["_ndoi"] = sel["doi"].apply(norm_doi)

    # Fold in DOIs recovered for no-DOI records (recover_no_doi.py), if present.
    rec_path = OUT_DIR / "no_doi_recovered.csv"
    n_recovered = 0
    rec_methods = {}
    if rec_path.exists():
        rec = pd.read_csv(rec_path)
        rec_map = dict(zip(rec["eid"], rec["recovered_doi"]))
        rec_methods = dict(rec["match_method"].value_counts())
        before = sel["_ndoi"].isna().sum()
        sel["_ndoi"] = sel.apply(
            lambda r: rec_map.get(r["eid"]) if pd.isna(r["_ndoi"]) else r["_ndoi"], axis=1)
        n_recovered = before - sel["_ndoi"].isna().sum()
        print(f"[recovery] folded in {n_recovered} recovered DOIs "
              f"({rec_methods}); remaining no_doi = {int(sel['_ndoi'].isna().sum())}")

    groups = sel["_ndoi"].apply(group_of)
    sel["_group"] = [g[0] for g in groups]
    sel["_group_name"] = [g[1] for g in groups]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    # remove stale group csvs (keep the recovery file and rewrite groups fresh)
    for old in OUT_DIR.glob("*.csv"):
        if old.name != "no_doi_recovered.csv":
            old.unlink()

    rows = []  # manifest rows: (stem, name, n, selector)
    n_total = len(sel)
    for stem, sub in sorted(sel.groupby("_group"), key=lambda kv: -len(kv[1])):
        name = sub["_group_name"].iloc[0]
        out = sub[["eid", "_ndoi", "title", "source"]].rename(columns={"_ndoi": "doi"})
        out.insert(2, "doi_url", out["doi"].apply(
            lambda d: f"https://doi.org/{d}" if isinstance(d, str) else ""))
        out.to_csv(OUT_DIR / f"{stem}.csv", index=False)
        sel_status = HAS_SELECTOR.get(stem, "待补选择器")
        rows.append((stem, name, len(sub), sel_status))
        print(f"  {stem:16s} {name:28s} {len(sub):4d}  -> {stem}.csv")

    # other-group prefix breakdown (Top-10), with the most common journal per prefix
    # derived from the data (more reliable than a static registrant guess).
    other = sel[sel["_group"] == "other"].copy()
    other["_prefix"] = other["_ndoi"].apply(prefix_of)
    other_prefixes = []
    for pre, cnt in Counter(other["_prefix"]).most_common(10):
        top_src = other.loc[other["_prefix"] == pre, "source"].mode()
        top_src = top_src.iloc[0] if len(top_src) else "?"
        other_prefixes.append((pre, cnt, top_src))

    write_manifest(rows, n_total, other_prefixes, sel, n_recovered, rec_methods)
    print(f"\n[saved] {OUT_DIR / '_manifest.md'}")
    return sel


def write_manifest(rows, n_total, other_prefixes, sel, n_recovered=0, rec_methods=None):
    lines = []
    A = lines.append
    A("# Stage-2 抓摘要输入清单 — 按出版商分组\n")
    A(f"来源:`03_screening/stage1_title_keyword.csv` 中 `stage1_decision ∈ "
      f"{{include, uncertain}}` = **{n_total}** 条。出版商按 DOI 前缀(10.xxxx)推断。")
    A("**本目录仅为 Cowork 抓摘要的输入清单,不含摘要本身**(PROJECT_MEMORY.md §7)。\n")
    if n_recovered:
        rm = rec_methods or {}
        A(f"> **无 DOI 找回(OpenAlex):** 原 316 条无 DOI 中找回 **{n_recovered}** 条 DOI "
          f"(enriched_oa={rm.get('enriched_oa', 0)} / fresh_oa={rm.get('fresh_oa', 0)};"
          f"标题 Jaccard≥0.90 且 年份差≤1 才接受),已并入对应出版商组;"
          f"明细见 `no_doi_recovered.csv`。\n")
    A("## 出版商分布\n")
    A("| 组 group | 出版商 | 条数 N | 占比 | 文件 | Cowork 选择器 |")
    A("|---|---|---|---|---|---|")
    for stem, name, n, sel_status in rows:
        pct = 100.0 * n / n_total
        A(f"| {stem} | {name} | {n} | {pct:.1f}% | `{stem}.csv` | {sel_status} |")
    A(f"| **合计** | | **{n_total}** | 100% | | |")

    have = sum(n for stem, _, n, s in rows if stem in HAS_SELECTOR)
    A(f"\n- **已有选择器覆盖:** {have} / {n_total} = {100*have/n_total:.1f}%"
      f"(ScienceDirect/Elsevier + Taylor & Francis)。")
    A(f"- **待补选择器:** 其余 {n_total - have} 条(Nature/Springer、Wiley、MDPI、"
      "IEEE、IOP、Frontiers、ACM 等),按本表条数从多到少补 DOM 选择器。")

    A("\n## `other`(有 DOI、未归类)组 DOI 前缀 Top-10\n")
    A("> 出版商/期刊取自该前缀下最常见的 `source`(数据驱动,供判断是否补选择器)。")
    A("\n| DOI 前缀 | 条数 | 最常见期刊/来源 |")
    A("|---|---|---|")
    for pre, cnt, src in other_prefixes:
        A(f"| {pre} | {cnt} | {str(src)[:55]} |")

    n_nodoi = int((sel["_group"] == "no_doi").sum())
    A(f"\n## 无 DOI\n\n- `no_doi.csv`:**{n_nodoi}** 条(多为会议/书章)。"
      "无 DOI → Cowork 无法按 DOI 抓;需靠标题/来源人工定位或在 Stage-2 标记为无摘要。")
    (OUT_DIR / "_manifest.md").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
    sys.exit(0)
