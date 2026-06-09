"""Merge Scopus web-export (abstracts + author keywords) into the Stage-2 table -> v3.

Per task / PROJECT_MEMORY.md §6.1 / §7 待修:
  1. Parse Scopus export CSVs (DOI / Abstract / Author Keywords).
  2. Fill missing abstracts from Scopus -> abstract_source=scopus.
  3. Fix 10.15627/jd.2025.1 (it scraped jd.2025.18's text): use Scopus if present,
     else blank -> missing.
  4. Drop tiny OpenAlex stubs (source=openalex AND len<150) -> missing.
  5. Add author_keywords column (Scopus); prefer clean Scopus abstract over OpenAlex
     where available.
  6. Write stage2_with_abstracts_v3.csv/.xlsx + coverage report v3.
"""

import glob
import re
import sys
from pathlib import Path

import pandas as pd

ABS_DIR = Path(__file__).resolve().parents[1]          # 04_abstracts/
SCOPUS_GLOB = str(ABS_DIR / "scopus_export" / "batch*.csv")
V2 = ABS_DIR / "reports" / "stage2_with_abstracts_v2.csv"
REPORTS = ABS_DIR / "reports"
OUT_CSV = REPORTS / "stage2_with_abstracts_v3.csv"
OUT_XLSX = REPORTS / "stage2_with_abstracts_v3.xlsx"
STILL_MISSING = ABS_DIR / "still_missing.csv"

JD1 = "10.15627/jd.2025.1"
TINY_OA = 150


def norm_doi(d):
    if not isinstance(d, str) or not d.strip():
        return None
    return re.sub(r"^https?://(dx\.)?doi\.org/", "", d.strip().lower()) or None


def clean_abstract(s):
    if not isinstance(s, str):
        return ""
    s = re.sub(r"\s+", " ", s).strip()
    s = re.sub(r"^\s*abstract[:\s]*", "", s, flags=re.I)
    s = re.sub(r"\s*©\s*\d{4}.*$", "", s).strip()          # trailing copyright
    s = re.sub(r"\s*keywords?\s*:.*$", "", s, flags=re.I).strip()
    return s


def clean_kw(s):
    if not isinstance(s, str) or s.strip().lower() in ("", "nan"):
        return ""
    return "; ".join(k.strip() for k in re.split(r"[;,]", s) if k.strip())


def load_scopus():
    scab, sckw = {}, {}
    n_files = 0
    for f in sorted(glob.glob(SCOPUS_GLOB)):
        n_files += 1
        d = pd.read_csv(f)
        for _, r in d.iterrows():
            k = norm_doi(r.get("DOI"))
            if not k:
                continue
            ab = clean_abstract(str(r.get("Abstract") or ""))
            kw = clean_kw(str(r.get("Author Keywords") or ""))
            if ab and (k not in scab or len(ab) > len(scab[k])):
                scab[k] = ab
            if kw and k not in sckw:
                sckw[k] = kw
    print(f"[scopus] {n_files} CSVs; DOIs with abstract={len(scab)}, with keywords={len(sckw)}")
    return scab, sckw


def main():
    scab, sckw = load_scopus()
    df = pd.read_csv(V2)
    df["abstract"] = df["abstract"].fillna("")
    df["eff_doi"] = df["eff_doi"].map(norm_doi)

    n_scopus_fill = n_tiny_drop = n_oa_replace = n_jd = 0
    abstracts, sources = [], []
    for _, r in df.iterrows():
        doi = r["eff_doi"]
        ab = r["abstract"] if isinstance(r["abstract"], str) else ""
        src = r["abstract_source"]
        sc = scab.get(doi)

        # (3) jd.2025.1 fix — force
        if doi == JD1:
            if sc:
                ab, src = sc, "scopus"
            else:
                ab, src = "", "none"
            n_jd += 1
        else:
            # (4) drop tiny OpenAlex stubs
            if src == "openalex" and len(ab) < TINY_OA:
                ab, src = "", "none"
                n_tiny_drop += 1
            # (2)+(5) fill from Scopus if currently missing, or replace OpenAlex
            if sc and (src in ("none",) or src == "openalex"):
                if src == "openalex":
                    n_oa_replace += 1
                else:
                    n_scopus_fill += 1
                ab, src = sc, "scopus"

        abstracts.append(ab)
        sources.append(src if ab else "none")

    df["abstract"] = abstracts
    df["abstract_source"] = sources
    df["abstract_status"] = df["abstract"].map(lambda a: "ok" if a else "missing")
    df["abstract_len"] = df["abstract"].str.len()
    df["author_keywords"] = df["eff_doi"].map(lambda d: sckw.get(d, "") if d else "")

    cols = ["eid", "eff_doi", "title", "source", "doctype", "stage1_decision",
            "publisher", "abstract", "abstract_source", "abstract_status",
            "abstract_len", "author_keywords"]
    out = df[cols]
    out.to_csv(OUT_CSV, index=False)
    out.to_excel(OUT_XLSX, index=False)
    print(f"[saved] {OUT_CSV.name} / .xlsx ({len(out)} rows)")

    # still-missing (final, with DOI)
    fm = out[(out["abstract_status"] == "missing") & out["eff_doi"].notna()].copy()
    fexp = fm[["eid", "eff_doi", "title", "source", "publisher"]].rename(
        columns={"eff_doi": "doi"})
    fexp.insert(2, "doi_url", "https://doi.org/" + fexp["doi"].astype(str))
    fexp.to_csv(STILL_MISSING, index=False)

    counts = dict(scopus_fill=n_scopus_fill, oa_replaced=n_oa_replace,
                  tiny_dropped=n_tiny_drop, jd_handled=n_jd)
    report(out, scab, counts)
    return out


def report(out, scab, counts):
    n = len(out)
    ok = int((out["abstract_status"] == "ok").sum())
    by_src = dict(out[out["abstract_status"] == "ok"]["abstract_source"].value_counts())
    has_doi = out["eff_doi"].notna()
    miss_doi = int((has_doi & (out["abstract_status"] == "missing")).sum())
    miss_nodoi = int((~has_doi).sum())
    kw = int((out["author_keywords"].fillna("").str.len() > 0).sum())

    jd_row = out[out["eff_doi"] == JD1]
    jd_state = (f"source={jd_row.iloc[0]['abstract_source']}, "
                f"len={int(jd_row.iloc[0]['abstract_len'])}") if len(jd_row) else "n/a"

    okm = out["abstract_status"] == "ok"
    short = int((okm & (out["abstract_len"] < 120)).sum())
    bullets = int((okm & out["abstract"].str.contains("•", regex=False)).sum())

    L = ["# Stage-2 摘要汇总 v3(并入 Scopus 导出)\n"]
    A = L.append
    A(f"Stage-2 = **{n}**。来源:Cowork scrape + OpenAlex 重建 + **Scopus 网页导出**(§6.1)。\n")
    A("## 本轮修复 / 并入\n| 操作 | 数 |\n|---|---|")
    A(f"| Scopus 补缺(missing→scopus) | {counts['scopus_fill']} |")
    A(f"| Scopus 替换 OpenAlex(更干净) | {counts['oa_replaced']} |")
    A(f"| 极短 OpenAlex(<150)重判 missing | {counts['tiny_dropped']} |")
    A(f"| jd.2025.1 处理 | {counts['jd_handled']}(结果:{jd_state}) |")

    A("\n## 覆盖率\n| 指标 | 值 |\n|---|---|")
    A(f"| 有摘要 ok | {ok} ({100*ok/n:.1f}%) |")
    A(f"| └ scrape | {by_src.get('scrape', 0)} |")
    A(f"| └ scopus | {by_src.get('scopus', 0)} |")
    A(f"| └ openalex | {by_src.get('openalex', 0)} |")
    A(f"| 仍缺(有 DOI) | {miss_doi} |")
    A(f"| 仍缺(无 DOI) | {miss_nodoi} |")
    A(f"| **author_keywords 覆盖(Scopus)** | {kw} ({100*kw/n:.1f}%) |")

    A("\n## 按出版商真实覆盖\n| 出版商 | 目标(有DOI) | ok | 覆盖率 |\n|---|---|---|---|")
    for pub, sub in out[has_doi].groupby("publisher"):
        g = int((sub["abstract_status"] == "ok").sum())
        A(f"| {pub} | {len(sub)} | {g} | {100*g/len(sub):.1f}% |")

    A(f"\n## jd.2025.1 修复确认\n\n- `{JD1}`:{jd_state}"
      f"{'(Scopus 无此 DOI → 置空 missing,已移除错误的 jd.2025.18 串摘要)' if not scab.get(JD1) else '(已用 Scopus 正确摘要覆盖)'}。")

    A(f"\n## 质量\n- 过短 <120:{short};含 `•`:{bullets}(openalex 结构化摘要,真内容)。")
    A(f"\n## 仍缺 — `still_missing.csv`\n- 有 DOI **{miss_doi}** + 无 DOI **{miss_nodoi}**。")
    (REPORTS / "abstract_coverage_report_v3.md").write_text("\n".join(L), encoding="utf-8")
    print(f"[saved] abstract_coverage_report_v3.md")
    print(f"[final] ok={ok}/{n} ({100*ok/n:.1f}%); "
          f"scrape={by_src.get('scrape',0)} scopus={by_src.get('scopus',0)} "
          f"openalex={by_src.get('openalex',0)}; miss_doi={miss_doi} miss_nodoi={miss_nodoi}; "
          f"keywords={kw}; jd={jd_state}")


if __name__ == "__main__":
    main()
    sys.exit(0)
