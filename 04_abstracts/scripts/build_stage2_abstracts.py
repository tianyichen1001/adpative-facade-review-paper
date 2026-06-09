"""Merge Cowork abstract slices and build the Stage-2 abstract list + coverage report.

Steps (per task):
  2. Merge slices/*.json -> {normalized_doi: abstract}; clean; flag duplicate text.
  3. Build Stage-2 list (2118) with effective DOI (original or recovered) -> abstract.
  4. Coverage + quality report; export still-missing (with DOI) by publisher.

Reads slices from 04_abstracts/slices/ (already tidied by content).
"""

import json
import re
import sys
from collections import defaultdict
from pathlib import Path
from statistics import median

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]            # 04_abstracts/
SLICES = ROOT / "slices"
STAGE1 = ROOT.parent / "03_screening" / "stage1_title_keyword.csv"
RECOVERED = ROOT / "scrape_inputs" / "no_doi_recovered.csv"
REPORTS = ROOT / "reports"
REMAIN_DIR = ROOT / "scrape_inputs_remaining"

# Publisher mapping by DOI prefix (report grouping, per task).
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


def merge_slices():
    merged = {}
    text_to_dois = defaultdict(set)
    n_files = 0
    for f in sorted(SLICES.glob("*.json")):
        n_files += 1
        data = json.load(open(f, encoding="utf-8"))
        for k, v in data.items():
            nd = norm_doi(k)
            ab = clean_abstract(v)
            if not nd or not ab:
                continue
            # keep the longest if a DOI appears in multiple slices
            if nd not in merged or len(ab) > len(merged[nd]):
                merged[nd] = ab
    for nd, ab in merged.items():
        text_to_dois[ab].add(nd)
    dups = {t: ds for t, ds in text_to_dois.items() if len(ds) > 1}
    print(f"[merge] slice files: {n_files}; unique DOIs with abstract: {len(merged)}")
    print(f"[merge] duplicate abstract texts (same text, >1 DOI): {len(dups)} "
          f"covering {sum(len(d) for d in dups.values())} DOIs")
    return merged, dups


def main():
    REPORTS.mkdir(exist_ok=True)
    merged, dups = merge_slices()

    df = pd.read_csv(STAGE1)
    s2 = df[df["stage1_decision"].isin(["include", "uncertain"])].copy()
    assert len(s2) == 2118, f"expected 2118, got {len(s2)}"

    rec = pd.read_csv(RECOVERED)
    rec_map = {e: norm_doi(d) for e, d in zip(rec["eid"], rec["recovered_doi"])}

    def eff_doi(row):
        nd = norm_doi(row["doi"])
        return nd if nd else rec_map.get(row["eid"])

    s2["eff_doi"] = s2.apply(eff_doi, axis=1)
    s2["abstract"] = s2["eff_doi"].map(lambda d: merged.get(d, "") if d else "")
    s2["abstract_status"] = s2["abstract"].map(lambda a: "ok" if a else "missing")
    s2["abstract_len"] = s2["abstract"].str.len()
    s2["publisher"] = s2["eff_doi"].map(publisher)

    out = s2[["eid", "doi", "eff_doi", "title", "source", "doctype",
              "stage1_decision", "publisher", "abstract_status", "abstract_len",
              "abstract"]].rename(columns={"doi": "orig_doi"})
    REPORTS.mkdir(exist_ok=True)
    out.to_csv(REPORTS / "stage2_with_abstracts.csv", index=False)
    out.to_excel(REPORTS / "stage2_with_abstracts.xlsx", index=False)
    print(f"[saved] {REPORTS/'stage2_with_abstracts.csv'} / .xlsx ({len(out)} rows)")

    write_report(s2, merged, dups)
    return s2


def write_report(s2, merged, dups):
    n = len(s2)
    ok = int((s2["abstract_status"] == "ok").sum())
    miss = n - ok
    has_doi = s2["eff_doi"].notna()
    n_doi = int(has_doi.sum())
    n_nodoi = n - n_doi
    cov_doi = 100.0 * ok / n_doi if n_doi else 0.0

    # by-publisher
    pub_rows = []
    for pub, sub in s2[has_doi].groupby("publisher"):
        got = int((sub["abstract_status"] == "ok").sum())
        pub_rows.append((pub, len(sub), got, 100.0 * got / len(sub)))
    pub_rows.sort(key=lambda r: -r[1])

    # still-missing WITH DOI -> export by publisher
    REMAIN_DIR.mkdir(exist_ok=True)
    for old in REMAIN_DIR.glob("*.csv"):
        old.unlink()
    miss_doi = s2[has_doi & (s2["abstract_status"] == "missing")]
    remain_rows = []
    for pub, sub in miss_doi.groupby("publisher"):
        exp = sub[["eid", "eff_doi", "title", "source"]].rename(columns={"eff_doi": "doi"})
        exp.insert(2, "doi_url", "https://doi.org/" + exp["doi"].astype(str))
        exp.to_csv(REMAIN_DIR / f"{pub}.csv", index=False)
        remain_rows.append((pub, len(sub)))
    remain_rows.sort(key=lambda r: -r[1])

    # quality checks
    okmask = s2["abstract_status"] == "ok"
    empties = s2[okmask & (s2["abstract"].str.strip() == "")]
    short = s2[okmask & (s2["abstract_len"] < 120)]
    bullets = s2[okmask & s2["abstract"].str.contains("•", regex=False)]
    kw = s2[okmask & s2["abstract"].str.contains(r"keywords?\s*:", case=False, regex=True)]
    lens = s2.loc[okmask, "abstract_len"].tolist()

    L = []
    A = L.append
    A("# Stage-2 摘要覆盖率 & 质量报告\n")
    A(f"Stage-2 集 = **{n}**(include+uncertain)。摘要来源:Cowork slices(`04_abstracts/slices/`,"
      "164 个分片;Cowork STATUS 记 180 分片已扫,16 个分片结果未随上传到位)。\n")
    A("## 1. 覆盖率总览\n")
    A("| 指标 | 值 |")
    A("|---|---|")
    A(f"| Stage-2 总数 | {n} |")
    A(f"| 有摘要 ok | {ok} |")
    A(f"| 缺摘要 missing | {miss} |")
    A(f"| 有效 DOI 数(原 DOI + 找回) | {n_doi} |")
    A(f"| 无 DOI(无抓取路径) | {n_nodoi} |")
    A(f"| **覆盖率(ok / 有 DOI)** | **{ok}/{n_doi} = {cov_doi:.1f}%** |")
    A(f"| 覆盖率(ok / 全 2118) | {ok}/{n} = {100.0*ok/n:.1f}% |")
    A(f"| 合并到的唯一摘要 DOI 数 | {len(merged)} |")

    A("\n## 2. 按出版商覆盖率(有 DOI)\n")
    A("| 出版商 | 目标(有DOI) | 抓到 | 覆盖率 |")
    A("|---|---|---|---|")
    for pub, tot, got, pct in pub_rows:
        A(f"| {pub} | {tot} | {got} | {pct:.1f}% |")

    A("\n## 3. 仍缺摘要(有 DOI)按出版商 → 可补跑\n")
    A(f"导出至 `04_abstracts/scrape_inputs_remaining/<publisher>.csv`(列同 scrape_inputs)。"
      f"合计 **{int(miss_doi.shape[0])}** 条。\n")
    A("| 出版商 | 仍缺条数 |")
    A("|---|---|")
    for pub, cnt in remain_rows:
        A(f"| {pub} | {cnt} |")

    A(f"\n## 4. 无 DOI 仍缺\n\n- **{n_nodoi}** 条无有效 DOI → Cowork 无抓取路径,"
      "留 Stage-2 用 标题+concepts 兜底筛(记为 limitation)。\n")

    A("## 5. 质量检查\n")
    A("| 检查 | 命中数 |")
    A("|---|---|")
    A(f"| ① 空摘要(status=ok 却空,应为 0) | {len(empties)} |")
    A(f"| ② 过短 <120 字符 | {len(short)} |")
    A(f"| ③ 含 `•`(疑似 Highlights,重点查 elsevier) | {len(bullets)} |")
    A(f"| ④ 含残留 `Keywords:`(MDPI 通病) | {len(kw)} |")
    if lens:
        A(f"\n摘要长度分布(ok={ok}):min={min(lens)} / 中位={int(median(lens))} / max={max(lens)} 字符。")

    def listing(title, frame, k=12):
        A(f"\n**{title}**(列前 {min(k,len(frame))} 条):")
        if not len(frame):
            A("- (无)")
            return
        for _, r in frame.head(k).iterrows():
            frag = re.sub(r"\s+", " ", str(r["abstract"]))[:90]
            A(f"- `{r['eid']}` [{r['publisher']}] len={r['abstract_len']} — {frag}")

    if len(short):
        listing("② 过短 <120", short)
    if len(bullets):
        listing("③ 含 • 项目符号", bullets)
    if len(kw):
        listing("④ 含 Keywords:", kw)

    if dups:
        A("\n## 6. 疑似重复摘要(同文本 → 多 DOI)\n")
        A(f"共 {len(dups)} 组。前 10 组:")
        for i, (t, ds) in enumerate(sorted(dups.items(), key=lambda x: -len(x[1]))[:10], 1):
            A(f"- 组{i}({len(ds)} DOI):{', '.join(sorted(ds)[:4])}"
              f"{' …' if len(ds) > 4 else ''} — “{t[:80]}…”")

    (REPORTS / "abstract_coverage_report.md").write_text("\n".join(L), encoding="utf-8")
    print(f"[saved] {REPORTS/'abstract_coverage_report.md'}")
    print(f"[quality] empty={len(empties)} short={len(short)} bullets={len(bullets)} "
          f"keywords={len(kw)} dup_groups={len(dups)}")
    print(f"[coverage] ok={ok}/{n_doi} (with DOI) = {cov_doi:.1f}%; nodoi_missing={n_nodoi}")


if __name__ == "__main__":
    main()
    sys.exit(0)
