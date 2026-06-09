"""Step 1: merge Scopus full export (author + index keywords, fill 5 missing
abstracts) into the Stage-2 table -> v4. Join key = EID. Rows in export not in our
corpus are discarded; our 2118 rows are preserved.
"""
import re
import sys
from pathlib import Path

import pandas as pd

ABS = Path(__file__).resolve().parents[1]              # 04_abstracts/
EXPORT = ABS / "scopus_export" / "all_abstract_and_information.csv"
V3 = ABS / "reports" / "stage2_with_abstracts_v3.csv"
OUT = ABS / "reports" / "stage2_with_abstracts_v4.csv"


def clean_abstract(s):
    if not isinstance(s, str):
        return ""
    s = re.sub(r"\s+", " ", s).strip()
    s = re.sub(r"^\s*abstract[:\s]*", "", s, flags=re.I)
    s = re.sub(r"\s*©\s*\d{4}.*$", "", s).strip()
    return s


def clean_kw(s):
    if not isinstance(s, str) or s.strip().lower() in ("", "nan"):
        return ""
    return "; ".join(k.strip() for k in re.split(r"[;,]", s) if k.strip())


def main():
    exp = pd.read_csv(EXPORT)
    # de-dup EID: keep the most complete row (longest abstract, then keywords)
    exp["_ablen"] = exp["Abstract"].fillna("").str.len()
    exp["_kwlen"] = exp["Author Keywords"].fillna("").str.len()
    exp = exp.sort_values(["_ablen", "_kwlen"], ascending=False).drop_duplicates("EID")
    ak = {e: clean_kw(k) for e, k in zip(exp["EID"], exp["Author Keywords"])}
    ik = {e: clean_kw(k) for e, k in zip(exp["EID"], exp["Index Keywords"])}
    eab = {e: clean_abstract(a) for e, a in zip(exp["EID"], exp["Abstract"])}
    print(f"[export] unique EID={len(exp)}; with AK={sum(bool(v) for v in ak.values())}, "
          f"IK={sum(bool(v) for v in ik.values())}")

    df = pd.read_csv(V3)
    df["abstract"] = df["abstract"].fillna("")

    # author_keywords: prefer export (more complete) else existing v3
    def merge_ak(r):
        return ak.get(r["eid"]) or (r["author_keywords"] if isinstance(r["author_keywords"], str) else "")
    df["author_keywords"] = df.apply(merge_ak, axis=1)
    df["index_keywords"] = df["eid"].map(lambda e: ik.get(e, ""))

    # fill missing abstracts from export
    n_fill = 0
    for i, r in df.iterrows():
        if r["abstract_status"] == "missing":
            a = eab.get(r["eid"], "")
            if a:
                df.at[i, "abstract"] = a
                df.at[i, "abstract_source"] = "scopus_export"
                df.at[i, "abstract_status"] = "ok"
                df.at[i, "abstract_len"] = len(a)
                n_fill += 1

    df.to_csv(OUT, index=False)
    n = len(df)
    n_ak = int((df["author_keywords"].fillna("").str.len() > 0).sum())
    n_ik = int((df["index_keywords"].fillna("").str.len() > 0).sum())
    n_ok = int((df["abstract_status"] == "ok").sum())
    print(f"[saved] {OUT.name} ({n} rows)")
    print(f"[v4] author_keywords={n_ak} ({100*n_ak/n:.1f}%); index_keywords={n_ik} "
          f"({100*n_ik/n:.1f}%); abstracts filled from export={n_fill}; "
          f"abstract ok now={n_ok} ({100*n_ok/n:.1f}%)")


if __name__ == "__main__":
    main()
    sys.exit(0)
