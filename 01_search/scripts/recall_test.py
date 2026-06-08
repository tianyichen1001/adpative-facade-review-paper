"""Recall / sensitivity test for the adaptive-facade Scopus search (Stage 01).

Goal: probe whether the MAIN query (see scopus_search.py) misses relevant work by
running a TEST query of candidate supplementary terms (domain-constrained), then
counting how many TEST hits are NOT already in the committed corpus
(01_search/raw/scopus_raw.csv), keyed by eid.

This script is read-only w.r.t. the main corpus: it NEVER writes/merges into
scopus_raw.csv/.xlsx. It only reports, so Claude web / the user can decide whether
to fold the candidate terms into the main query.

API key: pybliometrics standard config (~/.config/pybliometrics.cfg). NEVER in code.
"""

from pathlib import Path

import pandas as pd
import pybliometrics
from pybliometrics.scopus import ScopusSearch

# --- Candidate supplementary terms + built-environment constraint -----------------
TEST_QUERY = (
    '( TITLE-ABS-KEY( "breathing skin" OR "breathing facade" OR "breathing wall" OR '
    '"adaptable facade" OR "adaptable building envelope" OR "convertible facade" OR '
    '"retractable roof" OR "soft robotic facade" OR "robotic facade" OR '
    '"hygromorphic facade" OR "hygromorphic skin" OR "transformable architecture" OR '
    '"transformable structure" OR "deployable structure" OR '
    '"shape-changing architecture" OR "responsive building skin" OR '
    '"adaptive solar facade" OR "kinetic shading system" ) '
    'AND TITLE-ABS-KEY( building OR architectur* OR facade OR envelope OR '
    '"built environment" ) ) '
    'AND ( DOCTYPE(ar) OR DOCTYPE(re) OR DOCTYPE(cp) OR DOCTYPE(ch) ) '
    'AND LANGUAGE(english)'
)

STD_PAGE = 25  # non-subscriber STANDARD cap (see scopus_search.py)

ROOT = Path(__file__).resolve().parents[1]
CORPUS_CSV = ROOT / "raw" / "scopus_raw.csv"

# Tokens for a crude on-topic heuristic on the title.
ONTOPIC_TOKENS = [
    "facade", "façade", "envelope", "skin", "kinetic", "adaptive", "adaptable",
    "deployable", "shading", "louver", "louvre", "responsive", "movable",
    "moveable", "morphing", "origami", "pneumatic", "retractable", "fenestration",
    "brise", "transformable", "breathing", "hygromorphic",
]


def is_ontopic(title):
    t = (title or "").lower()
    return any(tok in t for tok in ONTOPIC_TOKENS)


def run_test_search():
    pybliometrics.scopus.init()
    sizer = ScopusSearch(TEST_QUERY, view="STANDARD", subscriber=False,
                         count=STD_PAGE, download=False)
    n_hits = sizer.get_results_size()
    print(f"[test-hits] results size = {n_hits}")

    search = ScopusSearch(TEST_QUERY, view="STANDARD", subscriber=False,
                          count=STD_PAGE, refresh=True)
    rows = []
    for r in (search.results or []):
        cover = getattr(r, "coverDate", None)
        rows.append({
            "eid": getattr(r, "eid", None),
            "doi": getattr(r, "doi", None),
            "title": getattr(r, "title", None),
            "year": (cover or "")[:4] if cover else None,
            "source": getattr(r, "publicationName", None),
            "citedby_count": getattr(r, "citedby_count", None),
        })
    return n_hits, pd.DataFrame(rows)


def main():
    n_hits, test_df = run_test_search()
    print(f"[downloaded] {len(test_df)} test records")

    existing_eids = set(pd.read_csv(CORPUS_CSV)["eid"].dropna().astype(str))
    print(f"[corpus] existing eids = {len(existing_eids)}")

    test_df["eid"] = test_df["eid"].astype(str)
    new_df = test_df[~test_df["eid"].isin(existing_eids)].copy()
    print(f"[new] test records NOT in current corpus = {len(new_df)}")

    new_df["_cit"] = pd.to_numeric(new_df["citedby_count"], errors="coerce").fillna(0)
    new_df["_ontopic"] = new_df["title"].apply(is_ontopic)
    top = new_df.sort_values("_cit", ascending=False).head(30)

    print("\n[new] Top 30 NEW entries by citedby_count "
          "(* = title looks on-topic)")
    for i, (_, r) in enumerate(top.iterrows(), 1):
        flag = "*" if r["_ontopic"] else " "
        print(f"  {i:2d}.{flag}[{int(r['_cit']):>4d} cit] ({r['year']}) "
              f"{r['source']} — {r['title']}")

    n_on = int(new_df["_ontopic"].sum())
    print(f"\n[on-topic heuristic] {n_on}/{len(new_df)} new entries have an "
          "on-topic title token")
    print(f"[on-topic heuristic] within Top 30 shown: "
          f"{int(top['_ontopic'].sum())}/{len(top)}")

    # NOTE: deliberately NOT merging into the main corpus.
    return n_hits, len(new_df)


if __name__ == "__main__":
    main()
