"""Scopus topic search for the adaptive-facade systematic+bibliometric review.

Stage 01 — Identification (metadata only, NO abstracts; see PROJECT_MEMORY.md §4.2, §5).

Database: Scopus only (PROJECT_MEMORY.md §5).
Search is by topic, no journal whitelist, so top-tier venues (Nature etc.) are not missed.

API key handling: configured via pybliometrics standard config
(~/.config/pybliometrics.cfg) or pybliometrics.init(). The key is NEVER stored in
this script or committed to the repo (.gitignore covers pybliometrics.cfg / .env).

Outputs:
  01_search/raw/scopus_raw.csv
  01_search/raw/scopus_raw.xlsx
"""

from pathlib import Path

import pandas as pd
import pybliometrics
from pybliometrics.scopus import ScopusSearch

# --- FINAL search query (verbatim) -------------------------------------------------
# This is the LOCKED query after folding in synonyms validated by the recall
# sensitivity test (recall_test.py): adaptable / convertible / hygromorphic added to
# the modifier list; "building envelope(s)" added to the target list; breathing
# skin/facade/wall added to the phrase list. Noisy aerospace/metamaterial terms
# (deployable structure, transformable architecture, ...) were deliberately NOT added.
# See PROJECT_MEMORY.md §3 scope / §5 strategy and 01_search/search_log.md.
QUERY = (
    '( TITLE-ABS-KEY( ( adaptive OR adaptable OR kinetic OR dynamic OR responsive OR '
    'movable OR moveable OR convertible OR deployable OR transformable OR reconfigurable '
    'OR morphing OR "shape changing" OR "shape-changing" OR retractable OR foldable OR '
    'folding OR origami OR kirigami OR pneumatic OR inflatable OR "shape memory" OR '
    'hygromorphic OR biomimetic OR "bio-inspired" OR "bio inspired" OR actuated OR '
    'bistable ) W/3 ( facade OR facades OR "building envelope" OR "building envelopes" OR '
    '"building skin" OR "building skins" OR "second skin" OR "double skin facade" OR '
    'shading OR louver OR louvers OR louvre OR louvres OR "brise soleil" OR '
    '"brise-soleil" OR fenestration OR "solar screen" OR "sun screen" ) ) OR '
    'TITLE-ABS-KEY( "kinetic envelope" OR "adaptive envelope" OR "dynamic envelope" OR '
    '"responsive envelope" OR "deployable envelope" OR "movable envelope" OR '
    '"kinetic architecture" OR "adaptive building envelope" OR '
    '"responsive building envelope" OR "breathing skin" OR "breathing facade" OR '
    '"breathing wall" ) ) '
    'AND ( DOCTYPE(ar) OR DOCTYPE(re) OR DOCTYPE(cp) OR DOCTYPE(ch) ) '
    'AND LANGUAGE(english)'
)

RAW_DIR = Path(__file__).resolve().parents[1] / "raw"
CSV_PATH = RAW_DIR / "scopus_raw.csv"
XLSX_PATH = RAW_DIR / "scopus_raw.xlsx"

# Fields to persist (PROJECT_MEMORY.md §6 / task step 6). Mapping from ScopusSearch
# result tuple attribute -> output column name.
FIELD_MAP = [
    ("eid", "eid"),
    ("doi", "doi"),
    ("title", "title"),
    ("coverDate", "year"),               # year derived from coverDate below
    ("publicationName", "source"),
    ("issn", "issn"),
    ("volume", "volume"),
    ("issueIdentifier", "issue"),
    ("pageRange", "pageRange"),
    ("subtypeDescription", "doctype"),
    ("creator", "first_author"),
    ("author_names", "author_names"),
    ("author_ids", "author_ids"),
    ("affilname", "affilname"),
    ("affiliation_country", "affiliation_country"),
    ("citedby_count", "citedby_count"),
    ("openaccess", "openaccess"),
    ("authkeywords", "authkeywords"),
]


def run_search():
    """Run the query, trying COMPLETE view first, falling back to STANDARD.

    COMPLETE view requires a subscriber (institutional) API key. With a
    non-subscriber key, COMPLETE raises Scopus401Error and the per-page limit
    drops to 25 with cursor pagination (subscriber=False), so we fall back to
    STANDARD view + subscriber=False.
    """
    pybliometrics.scopus.init()

    # Non-subscriber keys cap STANDARD pages at 25 (pybliometrics defaults to 200,
    # which the API rejects with a 400 "Exceeds the maximum number allowed"). We
    # override count=25 and use start-based pagination (subscriber=False).
    STD_PAGE = 25

    # Step 1: hit count only (no download).
    sizer = ScopusSearch(QUERY, view="STANDARD", subscriber=False,
                         count=STD_PAGE, download=False)
    n_hits = sizer.get_results_size()
    print(f"[hits] results size = {n_hits}")

    # Step 2: download, COMPLETE -> STANDARD fallback.
    try:
        search = ScopusSearch(QUERY, view="COMPLETE", refresh=True)
        used_view = "COMPLETE"
        print("[view] using COMPLETE")
    except Exception as exc:  # noqa: BLE001 - report and fall back
        print(f"[view] COMPLETE failed ({exc}); falling back to STANDARD")
        search = ScopusSearch(QUERY, view="STANDARD", subscriber=False,
                              count=STD_PAGE, refresh=True)
        used_view = "STANDARD"
        print("[view] using STANDARD (subscriber=False, count=25, start pagination)")

    return n_hits, used_view, search


def to_dataframe(results):
    """Build the export DataFrame from ScopusSearch results."""
    rows = []
    for r in results:
        row = {}
        for attr, col in FIELD_MAP:
            val = getattr(r, attr, None)
            if col == "year":
                row["year"] = (val or "")[:4] if val else None
            else:
                row[col] = val
        rows.append(row)
    cols = [col for _, col in FIELD_MAP]
    return pd.DataFrame(rows, columns=cols)


def coverage_report(df):
    """Print field-coverage percentages for key columns."""
    n = len(df)
    print(f"\n[coverage] over {n} records")
    for col in ["doi", "authkeywords", "affilname", "affiliation_country"]:
        present = df[col].notna() & (df[col].astype(str).str.strip() != "")
        pct = 100.0 * present.sum() / n if n else 0.0
        print(f"  {col:22s}: {present.sum():5d} / {n}  = {pct:5.1f}%")


def doctype_report(df):
    """Print the distribution of document types (subtypeDescription)."""
    n = len(df)
    print(f"\n[doctype] distribution over {n} records")
    counts = df["doctype"].fillna("(none)").value_counts()
    for label, cnt in counts.items():
        pct = 100.0 * cnt / n if n else 0.0
        print(f"  {str(label):20s}: {cnt:5d}  = {pct:5.1f}%")


def samples(df):
    """Print top-25 by citations and latest-15 by year."""
    work = df.copy()
    work["_cit"] = pd.to_numeric(work["citedby_count"], errors="coerce").fillna(0)
    work["_yr"] = pd.to_numeric(work["year"], errors="coerce").fillna(0)

    print("\n[sample] Top 25 by citedby_count")
    top = work.sort_values("_cit", ascending=False).head(25)
    for i, (_, r) in enumerate(top.iterrows(), 1):
        print(f"  {i:2d}. [{int(r['_cit']):>5d} cit] ({r['year']}) "
              f"{r['source']} — {r['title']}")

    print("\n[sample] Latest 15 by year")
    latest = work.sort_values("_yr", ascending=False).head(15)
    for i, (_, r) in enumerate(latest.iterrows(), 1):
        print(f"  {i:2d}. ({r['year']}) {r['title']}")


def increment_report(df, old_eids):
    """Report net-new records vs the previous corpus (by eid)."""
    cur = df.copy()
    cur["eid"] = cur["eid"].astype(str)
    new = cur[~cur["eid"].isin(old_eids)].copy()
    print(f"\n[increment] previous corpus eids = {len(old_eids)}")
    print(f"[increment] net-new (not in previous corpus) = {len(new)}")

    ontopic = [
        "facade", "façade", "envelope", "skin", "kinetic", "adaptive", "adaptable",
        "convertible", "breathing", "hygromorphic", "deployable", "shading", "louver",
        "louvre", "responsive", "movable", "moveable", "morphing", "origami",
        "pneumatic", "retractable", "fenestration", "brise", "transformable",
    ]
    new["_cit"] = pd.to_numeric(new["citedby_count"], errors="coerce").fillna(0)
    new["_on"] = new["title"].fillna("").str.lower().apply(
        lambda t: any(tok in t for tok in ontopic))

    top = new.sort_values("_cit", ascending=False).head(25)
    print("\n[increment] Top 25 net-new by citedby_count (* = on-topic title)")
    for i, (_, r) in enumerate(top.iterrows(), 1):
        flag = "*" if r["_on"] else " "
        print(f"  {i:2d}.{flag}[{int(r['_cit']):>4d} cit] ({r['year']}) "
              f"{r['source']} — {r['title']}")
    print(f"\n[increment] on-topic titles: {int(new['_on'].sum())}/{len(new)} of all "
          f"net-new; {int(top['_on'].sum())}/{len(top)} within Top 25")
    return len(new)


def save(df):
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(CSV_PATH, index=False)
    df.to_excel(XLSX_PATH, index=False)
    print(f"\n[saved] {CSV_PATH}")
    print(f"[saved] {XLSX_PATH}")


def main(save_full=True):
    # Capture previous corpus eids BEFORE any overwrite, for the increment report.
    old_eids = set()
    if CSV_PATH.exists():
        old_eids = set(pd.read_csv(CSV_PATH)["eid"].dropna().astype(str))

    n_hits, used_view, search = run_search()
    df = to_dataframe(search.results or [])
    print(f"[downloaded] {len(df)} records (view={used_view})")
    doctype_report(df)
    coverage_report(df)
    increment_report(df, old_eids)
    samples(df)

    # Guardrail: pause if outside 200..6000.
    if n_hits > 6000 or n_hits < 200:
        print(f"\n[guardrail] hits={n_hits} outside 200..6000 — NOT saving full corpus; "
              "awaiting confirmation.")
        return df
    if save_full:
        save(df)
    return df


if __name__ == "__main__":
    main()
