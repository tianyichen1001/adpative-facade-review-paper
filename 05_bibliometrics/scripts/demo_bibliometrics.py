"""Bibliometrics DEMO (pipeline test, NOT the final analysis).

Final bibliometrics run on the INCLUDED set (PROJECT_MEMORY.md §4.3); this is a
dry-run on the Stage-2 set (2118) to prove: merge abstracts+metadata, draw figures
(matplotlib), build a concept co-occurrence network, export GraphML/CSV for GUI tools
(VOSviewer/Gephi), and a light gensim LDA. Heavy clustering/mapping is GUI-only.
"""

import re
import sys
from collections import Counter
from itertools import combinations
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]            # 05_bibliometrics/
ENRICHED = ROOT.parent / "02_enrichment" / "enriched.csv"
ABS = ROOT.parent / "04_abstracts" / "reports" / "stage2_with_abstracts.csv"
CORPUS = ROOT / "corpus_for_biblio" / "corpus_stage2.csv"
FIG = ROOT / "figures"
EXP = ROOT / "exports"
for d in (FIG, EXP, CORPUS.parent):
    d.mkdir(parents=True, exist_ok=True)


def barh(series, title, fname, xlabel="count"):
    fig, ax = plt.subplots(figsize=(8, 6))
    series = series.iloc[::-1]
    ax.barh(series.index.astype(str), series.values, color="#3b7dd8")
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    fig.tight_layout()
    fig.savefig(FIG / fname, dpi=120)
    plt.close(fig)


def merge_corpus():
    e = pd.read_csv(ENRICHED)
    a = pd.read_csv(ABS)[["eid", "abstract", "abstract_status", "eff_doi"]]
    corpus = a.merge(e, on="eid", how="left")        # a = Stage-2 (2118)
    corpus.to_csv(CORPUS, index=False)
    n_ab = int((corpus["abstract_status"] == "ok").sum())
    print(f"[corpus] Stage-2 = {len(corpus)}; with abstract = {n_ab} "
          f"({100*n_ab/len(corpus):.1f}%)")
    print(f"[saved] {CORPUS}")
    return corpus


def split_multi(series, sep="; "):
    c = Counter()
    for v in series.dropna():
        for tok in str(v).split(sep):
            tok = tok.strip()
            if tok:
                c[tok] += 1
    return c


def figures(corpus):
    # 1) year trend
    yr = pd.to_numeric(corpus["year"], errors="coerce").dropna().astype(int)
    yr = yr[(yr >= 1980) & (yr <= 2026)].value_counts().sort_index()
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot(yr.index, yr.values, marker="o", color="#3b7dd8")
    ax.set_title("Annual publication trend (Stage-2, N=%d)" % len(corpus))
    ax.set_xlabel("year"); ax.set_ylabel("publications")
    fig.tight_layout(); fig.savefig(FIG / "01_year_trend.png", dpi=120); plt.close(fig)
    peak = (int(yr.idxmax()), int(yr.max()))

    # 2) top journals
    barh(corpus["source"].value_counts().head(15),
         "Top 15 sources", "02_top_sources.png")
    # 3) countries
    cc = pd.Series(split_multi(corpus["oa_countries"])).sort_values(ascending=False).head(15)
    barh(cc, "Top 15 countries (OpenAlex)", "03_top_countries.png")
    # 4) institutions
    ins = pd.Series(split_multi(corpus["oa_institutions"])).sort_values(ascending=False).head(15)
    barh(ins, "Top 15 institutions (OpenAlex)", "04_top_institutions.png")
    # 5) most cited (Scopus citedby_count)
    cited = corpus.assign(c=pd.to_numeric(corpus["citedby_count"], errors="coerce")) \
                  .nlargest(15, "c")
    s = pd.Series(cited["c"].values,
                  index=[str(t)[:42] for t in cited["title"]])
    barh(s, "Top 15 most-cited (Scopus)", "05_top_cited.png", xlabel="citations")
    # 6) doctype pie
    dt = corpus["doctype"].value_counts()
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.pie(dt.values, labels=dt.index, autopct="%1.0f%%", startangle=90)
    ax.set_title("Document types (Stage-2)")
    fig.tight_layout(); fig.savefig(FIG / "06_doctypes.png", dpi=120); plt.close(fig)
    print(f"[figures] 6 PNGs -> {FIG}")
    return peak, cc, ins


def parse_concepts(cell, thr=0.3):
    out = []
    if not isinstance(cell, str):
        return out
    for part in cell.split(";"):
        part = part.strip()
        if not part or ":" not in part:
            continue
        name, _, sc = part.rpartition(":")
        try:
            if float(sc) >= thr:
                out.append(name.strip())
        except ValueError:
            continue
    return out


def concepts_network(corpus):
    per_paper = corpus["oa_concepts"].apply(parse_concepts)
    freq = Counter(c for lst in per_paper for c in lst)
    top30 = pd.Series(dict(freq.most_common(30)))
    barh(top30.sort_values(ascending=False), "Top 30 concepts (score>=0.3)",
         "07_top_concepts.png")

    # wordcloud
    try:
        from wordcloud import WordCloud
        wc = WordCloud(width=1000, height=500, background_color="white")
        wc.generate_from_frequencies(dict(freq))
        wc.to_file(str(FIG / "08_concept_wordcloud.png"))
    except Exception as e:  # noqa: BLE001
        print("[wordcloud] skipped:", e)

    # co-occurrence on top40
    top40 = [c for c, _ in freq.most_common(40)]
    idx = set(top40)
    co = Counter()
    for lst in per_paper:
        present = sorted(set(c for c in lst if c in idx))
        for a, b in combinations(present, 2):
            co[(a, b)] += 1

    G = nx.Graph()
    for c in top40:
        G.add_node(c, freq=int(freq[c]))
    for (a, b), w in co.items():
        if w >= 2:
            G.add_edge(a, b, weight=int(w))

    # matrix CSV
    mat = pd.DataFrame(0, index=top40, columns=top40)
    for (a, b), w in co.items():
        mat.loc[a, b] = w
        mat.loc[b, a] = w
    mat.to_csv(EXP / "concept_cooccurrence_matrix.csv")
    nx.write_graphml(G, EXP / "concept_cooccurrence.graphml")

    # spring layout figure
    if G.number_of_edges():
        fig, ax = plt.subplots(figsize=(12, 10))
        pos = nx.spring_layout(G, k=0.6, seed=42, weight="weight")
        sizes = [G.nodes[n]["freq"] * 6 for n in G]
        widths = [0.3 + G[u][v]["weight"] * 0.15 for u, v in G.edges()]
        nx.draw_networkx_edges(G, pos, width=widths, alpha=0.25, ax=ax)
        nx.draw_networkx_nodes(G, pos, node_size=sizes, node_color="#e07b39",
                               alpha=0.85, ax=ax)
        nx.draw_networkx_labels(G, pos, font_size=7, ax=ax)
        ax.set_title("Concept co-occurrence (top 40, edge>=2) — DRAFT/dirty")
        ax.axis("off")
        fig.tight_layout(); fig.savefig(FIG / "09_concept_cooccurrence.png", dpi=120)
        plt.close(fig)
    print(f"[concepts] top40 nodes={G.number_of_nodes()} edges={G.number_of_edges()}; "
          f"GraphML+matrix -> {EXP}")
    return top30, G


def lda_demo(corpus, n_topics=6):
    sub = corpus[corpus["abstract_status"] == "ok"].copy()
    docs = (sub["title"].fillna("") + ". " + sub["abstract"].fillna("")).tolist()
    try:
        from gensim import corpora
        from gensim.models import LdaModel
        from gensim.parsing.preprocessing import STOPWORDS
    except Exception as e:  # noqa: BLE001
        print("[lda] gensim unavailable:", e)
        return None
    extra = {"abstract", "study", "paper", "results", "using", "based", "research",
             "proposed", "approach", "method", "analysis", "different", "model"}
    stop = STOPWORDS.union(extra)
    toks = []
    for d in docs:
        words = re.findall(r"[a-zA-Z]{3,}", d.lower())
        toks.append([w for w in words if w not in stop])
    dic = corpora.Dictionary(toks)
    dic.filter_extremes(no_below=5, no_above=0.5)
    bow = [dic.doc2bow(t) for t in toks]
    lda = LdaModel(bow, num_topics=n_topics, id2word=dic, passes=5, random_state=42)
    rows = []
    print(f"[lda] {n_topics} topics over {len(docs)} abstracts:")
    for tid in range(n_topics):
        words = [w for w, _ in lda.show_topic(tid, topn=10)]
        print(f"  T{tid}: {', '.join(words)}")
        rows.append({"topic": tid, "top_words": ", ".join(words)})
    pd.DataFrame(rows).to_csv(EXP / "lda_topics.csv", index=False)
    print(f"[lda] saved {EXP/'lda_topics.csv'}")
    return rows


def main():
    corpus = merge_corpus()
    peak, cc, ins = figures(corpus)
    top30, G = concepts_network(corpus)
    lda_demo(corpus)
    print(f"\n[read] year peak = {peak[0]} (N={peak[1]}); "
          f"top country = {cc.index[0]} ({int(cc.iloc[0])}); "
          f"top institution = {ins.index[0]} ({int(ins.iloc[0])})")
    print(f"[read] top concept = {top30.idxmax()} ({int(top30.max())})")


if __name__ == "__main__":
    main()
    sys.exit(0)
