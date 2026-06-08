"""Crossref (secondary) enrichment + final merge for the adaptive-facade corpus.

Run AFTER enrich_openalex.py.

Inputs:
  01_search/raw/scopus_raw.csv          original corpus (columns kept untouched)
  02_enrichment/openalex_flat.csv       oa_* columns from enrich_openalex.py
Crossref (habanero, DOI'd records only): funder / license / reference-count /
  ISSN / container-title / published year / type.

Outputs:
  02_enrichment/crossref_flat.csv       eid + cr_* columns
  02_enrichment/enriched.csv / .xlsx    scopus_raw (unchanged) + oa_* + cr_*
  02_enrichment/enrichment_log.md       coverage report (OpenAlex + Crossref)

API is free, no key. Polite-pool `mailto` only.
"""

import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import pandas as pd
from habanero import Crossref

MAILTO = "tianyi.chen1001@gmail.com"
cr = Crossref(mailto=MAILTO)

ROOT = Path(__file__).resolve().parents[1]
CORPUS_CSV = ROOT.parent / "01_search" / "raw" / "scopus_raw.csv"
OA_FLAT = ROOT / "openalex_flat.csv"
CR_FLAT = ROOT / "crossref_flat.csv"
ENRICHED_CSV = ROOT / "enriched.csv"
ENRICHED_XLSX = ROOT / "enriched.xlsx"
LOG_MD = ROOT / "enrichment_log.md"

WORKERS = 5         # modest concurrency to stay within Crossref polite-pool limits
MAX_RETRIES = 4     # retry transient errors (e.g. 429) with backoff


def norm_doi(doi):
    if not isinstance(doi, str) or not doi.strip():
        return None
    d = doi.strip().lower()
    d = re.sub(r"^https?://(dx\.)?doi\.org/", "", d)
    return d or None


def empty_cr(match="none"):
    return {
        "cr_match": match,
        "cr_funders": None,
        "cr_n_funders": 0,
        "cr_license_types": None,
        "cr_has_license": False,
        "cr_reference_count": None,
        "cr_issn": None,
        "cr_container_title": None,
        "cr_published_year": None,
        "cr_type": None,
    }


def parse_cr(m):
    funders = [f.get("name") for f in (m.get("funder") or []) if f.get("name")]
    lic = m.get("license") or []
    lic_types = sorted({l.get("content-version") for l in lic if l.get("content-version")})
    container = (m.get("container-title") or [None])
    container = container[0] if container else None
    # published year
    year = None
    for key in ("published", "published-print", "published-online", "issued"):
        dp = (m.get(key) or {}).get("date-parts") if m.get(key) else None
        if dp and dp[0] and dp[0][0]:
            year = dp[0][0]
            break
    return {
        "cr_match": "doi",
        "cr_funders": "; ".join(funders),
        "cr_n_funders": len(funders),
        "cr_license_types": "; ".join(lic_types),
        "cr_has_license": bool(lic),
        "cr_reference_count": m.get("reference-count"),
        "cr_issn": "; ".join(m.get("ISSN") or []),
        "cr_container_title": container,
        "cr_published_year": year,
        "cr_type": m.get("type"),
    }


def fetch_one(doi):
    """Fetch one DOI with retry+backoff. Distinguishes 'not found' (404) from
    transient errors so rate-limiting (429) is retried, not silently dropped."""
    last = None
    for attempt in range(MAX_RETRIES):
        try:
            r = cr.works(ids=doi)
            return doi, parse_cr(r["message"])
        except Exception as exc:  # noqa: BLE001
            last = exc
            msg = str(exc)
            if "404" in msg or "Not Found" in msg or "not found" in msg.lower():
                return doi, empty_cr("not_found")
            time.sleep(0.5 * (2 ** attempt))  # 0.5, 1, 2, 4s
    return doi, empty_cr(f"error:{type(last).__name__}")


def main():
    df = pd.read_csv(CORPUS_CSV)
    df["_ndoi"] = df["doi"].apply(norm_doi)
    doi_to_eids = {}
    for _, r in df[df["_ndoi"].notna()].iterrows():
        doi_to_eids.setdefault(r["_ndoi"], []).append(r["eid"])
    unique_dois = list(doi_to_eids.keys())
    print(f"[crossref] fetching {len(unique_dois)} unique DOIs with {WORKERS} workers")

    cr_by_doi = {}
    done = 0
    with ThreadPoolExecutor(max_workers=WORKERS) as ex:
        futures = {ex.submit(fetch_one, d): d for d in unique_dois}
        for fut in as_completed(futures):
            doi, flat = fut.result()
            cr_by_doi[doi] = flat
            done += 1
            if done % 250 == 0:
                print(f"  .. {done}/{len(unique_dois)}")

    n_found = sum(1 for v in cr_by_doi.values() if v["cr_match"] == "doi")
    print(f"[crossref] resolved: {n_found}/{len(unique_dois)} unique DOIs")

    # Flat per eid
    cr_rows = []
    for _, r in df.iterrows():
        nd = r["_ndoi"]
        flat = cr_by_doi.get(nd, empty_cr("none")) if nd else empty_cr("no_doi")
        cr_rows.append({"eid": r["eid"], **flat})
    cr_flat = pd.DataFrame(cr_rows)
    cr_flat.to_csv(CR_FLAT, index=False)
    print(f"[saved] {CR_FLAT}")

    # --- Merge: original corpus (untouched) + oa_* + cr_* -----------------------
    base = pd.read_csv(CORPUS_CSV)  # original columns, untouched
    oa_flat = pd.read_csv(OA_FLAT)
    enriched = base.merge(oa_flat, on="eid", how="left").merge(cr_flat, on="eid", how="left")
    enriched.to_csv(ENRICHED_CSV, index=False)
    enriched.to_excel(ENRICHED_XLSX, index=False)
    print(f"[saved] {ENRICHED_CSV}\n[saved] {ENRICHED_XLSX}  ({len(enriched)} rows, "
          f"{enriched.shape[1]} cols)")

    report = build_report(enriched)
    LOG_MD.write_text(report, encoding="utf-8")
    print(f"[saved] {LOG_MD}")
    print("\n" + report)


def build_report(e):
    n = len(e)

    def pct(mask):
        c = int(mask.sum())
        return f"{c}/{n} = {100*c/n:.1f}%"

    has_concepts = e["oa_concepts"].fillna("").astype(str).str.len() > 0
    has_authors = e["oa_n_authors"].fillna(0) > 0
    has_inst_ctry = (e["oa_institutions"].fillna("").astype(str).str.len() > 0) & \
                    (e["oa_countries"].fillna("").astype(str).str.len() > 0)
    has_refs = e["oa_n_referenced_works"].fillna(0) > 0
    has_funder = e["cr_n_funders"].fillna(0) > 0
    has_license = e["cr_has_license"].fillna(False).astype(bool)
    has_refcount = e["cr_reference_count"].notna()

    n_doi = int((e["oa_match"] == "doi").sum())
    n_title = int((e["oa_match"] == "title").sum())
    n_unmatched = int(e["oa_match"].isin(["none", "low"]).sum())
    n_cr = int((e["cr_match"] == "doi").sum())

    lines = []
    A = lines.append
    A("# Enrichment Log — OpenAlex (primary) + Crossref (secondary)\n")
    A(f"输入 corpus:`01_search/raw/scopus_raw.csv`(N = {n});补全 API 免费无 key,"
      f"礼貌池 mailto = `{MAILTO}`(仅请求头标识,不入库为密钥)。\n")
    A("## OpenAlex 覆盖率(主补全)\n")
    A("| 指标 | 值 |")
    A("|---|---|")
    A(f"| 按 DOI 匹配 | {n_doi} |")
    A(f"| 按标题匹配(sim ≥ 0.9) | {n_title} |")
    A(f"| 未匹配(none/low) | {n_unmatched} |")
    A(f"| 有 concepts(关键词等价物) | {pct(has_concepts)} |")
    A(f"| 有全部作者 | {pct(has_authors)} |")
    A(f"| 有机构 + 国家 | {pct(has_inst_ctry)} |")
    A(f"| 有 referenced_works(参考文献) | {pct(has_refs)} |")
    A("\n## Crossref 覆盖率(辅,仅 DOI'd)\n")
    A("| 指标 | 值 |")
    A("|---|---|")
    A(f"| 按 DOI 解析成功 | {n_cr} |")
    A(f"| 有 funder(资助方) | {pct(has_funder)} |")
    A(f"| 有 license | {pct(has_license)} |")
    A(f"| 有 reference-count | {pct(has_refcount)} |")
    A("\n## 对比:补全前后(对照 Scopus STANDARD view)\n")
    A("| 字段 | Scopus 原始 | 补全后 |")
    A("|---|---|---|")
    A(f"| 关键词等价物(concepts) | 0.0%(authkeywords 全空) | {pct(has_concepts)}(OpenAlex concepts) |")
    A(f"| 全部作者 | 0.0%(仅 first_author/creator) | {pct(has_authors)}(OpenAlex authorships) |")
    A(f"| 国家 | 仅 affiliation_country(首作者域) | {pct(has_inst_ctry)}(全机构 + 国家) |")
    A("\n## 5 条补全前后对照样例\n")
    sample = e[e["oa_match"] == "doi"].head(5)
    for _, r in sample.iterrows():
        A(f"### {r['eid']} — {str(r['title'])[:90]}")
        A(f"- **Scopus 原始**:first_author=`{r.get('first_author')}` | "
          f"author_names=`{r.get('author_names')}`(空) | "
          f"authkeywords=`{r.get('authkeywords')}`(空) | "
          f"affiliation_country=`{r.get('affiliation_country')}`")
        A(f"- **OpenAlex 全作者**:{str(r.get('oa_authors'))[:200]}")
        A(f"- **OpenAlex 机构**:{str(r.get('oa_institutions'))[:200]}")
        A(f"- **OpenAlex 国家**:{r.get('oa_countries')}")
        A(f"- **OpenAlex concepts**:{str(r.get('oa_concepts'))[:200]}")
        A(f"- **Crossref funder**:{r.get('cr_funders')} | license_types=`{r.get('cr_license_types')}` "
          f"| ref-count={r.get('cr_reference_count')}\n")
    A("> 原始嵌套 OpenAlex 记录见 `openalex_raw.jsonl`(含 referenced_works 全列表,"
      "供后续共被引 / 文献耦合)。引用数仍以 Scopus 为准(§5),OpenAlex/Crossref 仅交叉校验。")
    return "\n".join(lines)


if __name__ == "__main__":
    sys.exit(main())
