"""Step 2/3: keyword-enriched 2nd pass on the 1131 uncertain_fulltext rows.

Now that clean author/index keywords are available (v4), re-judge uncertain rows:
  - PROMOTE -> include: explicit movement/mechanism word in TITLE or AUTHOR KEYWORDS
    (kinetic/origami/deployable/foldable/retractable/pneumatic/inflatable/SMA/
     shape-memory/morphing/hygromorph/bistable/movable + rotating/tilting/tracking
     NEAR a facade element). RED LINE: never promote on adaptive/dynamic/responsive/
     smart/intelligent buzzwords.
  - DEMOTE -> exclude(facade_no_movement): explicit no-movement signal (electrochromic
     /thermochromic, PCM/phase-change thermal-only, DSF without operable element,
     dynamic insulation, breathing/porous wall, switchable glazing) AND no movement cue.
  - else stay uncertain_fulltext (conflation evidence / limitation).
High sensitivity: ambiguous -> uncertain.

Outputs: updated stage2_screened.csv (new_decision), included_final.csv,
promoted_from_uncertain.csv, recomputed bridge_preview.md, prisma update.
"""
import re
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]              # 03_screening/
V4 = ROOT.parent / "04_abstracts" / "reports" / "stage2_with_abstracts_v4.csv"
SCREENED = ROOT / "stage2_screened.csv"
INCLUDED = ROOT / "included_final.csv"
PROMOTED = ROOT / "promoted_from_uncertain.csv"

# explicit movement/mechanism words (title + author keywords) — allowed to promote
PROMOTE = re.compile(
    r"\bkinetic(s|-)?\b|origami|kirigami|deployable|foldable|\bfolding\b|retractable|"
    r"pneumatic|inflatable|shape[- ]?memory|\bsma\b|shape[- ]?morph|\bmorphing\b|"
    r"hygromorph|bistable|movable|moveable|"
    r"(rotat\w*|rotatable|tilt\w*|tracking)[\w\s,'-]{0,22}"
    r"(louver|louvre|panel|shading|blind|\bfin\b|slat|fa.ade|skin)|"
    r"(louver|louvre|panel|shading|blind|\bfin\b|slat)[\w\s,'-]{0,22}"
    r"(rotat\w*|rotatable|tilt\w*|tracking)")
# facade/envelope context — required for promotion (drops "kinetic furniture/tiles/
# architecture" conceptual & non-facade objects)
FACADE_CTX = re.compile(
    r"fa.ade|building skin|building envelope|\benvelope\b|\blouver|louvre|\bblind|"
    r"shading|brise|fenestration|mashrabiya|curtain wall|\bwindow|glazing|\bskin\b|"
    r"sunshade|shutter|daylight|second skin|double skin|solar (control|shading)|"
    r"\bbipv\b|building[- ]integrated|screen")
# broad movement / operable cue (guards demote, e.g. operable DSF with blinds/vents)
MOVE_ANY = re.compile(
    PROMOTE.pattern + r"|operable|\bactuat|\bunfold|\bdeploy\w*|sliding|\bslid\w*|"
    r"\bmoving\b|self[- ]shaping|telescop|scissor|\bblind|\blouver|louvre|\bvent\b|"
    r"venetian|adjustable|opening|openable|shutter")
# explicit no-movement signals
DEMOTE = re.compile(
    r"electrochrom|thermochrom|photochrom|gasochrom|\bpcm\b|phase[- ]change|"
    r"latent heat|thermal energy storage|thermal storage|dynamic insulation|"
    r"breathing wall|porous wall|switchable glaz|switchable window|suspended particle|"
    r"liquid crystal|\bpdlc\b|\bdsf\b|double[- ]skin")

MECH = [
    ("material-driven", re.compile(r"\bsma\b|shape[- ]memory|hygromorph|hygroscop|"
                                   r"thermo[- ]?respons|bimetal|4d print|stimuli")),
    ("pneumatic-soft", re.compile(r"pneumatic|inflat|air chamber|etfe|soft (actuat|robot)|cushion")),
    ("origami-deployable", re.compile(r"origami|kirigami|deploy|scissor|tessellat|foldable|\bfold")),
    ("compliant", re.compile(r"compliant mechanism|bistable|buckl|elastic instab|flexible hinge")),
    ("mechanical", re.compile(r"rotat|\bslid|tilt|pivot|\bhinge|motor|linkage|gear|"
                              r"louver|slat|operable|retract|telescop|movable")),
]
STUDY = [
    ("experiment", re.compile(r"experiment|measured|wind tunnel|fabricat|tested|"
                              r"field (test|measurement)|monitored")),
    ("prototype", re.compile(r"prototype|mock[- ]?up|full[- ]scale|demonstrator|physical model")),
    ("simulation", re.compile(r"simulat|numerical|\bcfd\b|energyplus|modell?ed|"
                              r"computational|parametric|finite element|optimi[sz]ation")),
    ("theoretical", re.compile(r"theoretical|analytical model|mathematical|closed[- ]form")),
    ("case-study", re.compile(r"case study|case-study")),
]
PERF = {
    "energy": re.compile(r"\benergy\b|heating|cooling|\bload\b|consumption|\bkwh|energy saving|demand"),
    "daylight": re.compile(r"daylight|illuminance|\bglare\b|lighting|\budi\b|daylight autonomy|visual"),
    "comfort": re.compile(r"thermal comfort|visual comfort|\bpmv\b|occupant comfort|comfort"),
}


def tag(text, has_abstract):
    mech = next((n for n, r in MECH if r.search(text)), "unclear")
    study = next((n for n, r in STUDY if r.search(text)), "unclear")
    hit = [k for k, r in PERF.items() if r.search(text)]
    perf = "multiple" if len(hit) > 1 else (hit[0] if hit else ("none" if has_abstract else "unclear"))
    return mech, study, perf


def hits(rgx, t):
    return "; ".join(sorted({m.group(0) for m in rgx.finditer(t)})[:3])


def main():
    v4 = pd.read_csv(V4)[["eid", "abstract", "abstract_status", "author_keywords",
                          "index_keywords"]]
    s = pd.read_csv(SCREENED).drop(columns=["abstract_status"], errors="ignore") \
        .merge(v4, on="eid", how="left")

    new_dec, why, newconf, m_f, s_t, p_r = [], [], [], [], [], []
    promoted = []
    n_prom = n_dem = n_stay = 0
    for _, r in s.iterrows():
        dec = r["decision"]
        if dec != "uncertain_fulltext":
            new_dec.append(dec); why.append(""); newconf.append(r["confidence"])
            m_f.append(r["mechanism_family"]); s_t.append(r["study_type"])
            p_r.append(r["performance_reported"])
            continue
        title = str(r["title"] or "").lower()
        kw = str(r.get("author_keywords") or "").lower()
        ik = str(r.get("index_keywords") or "").lower()
        ab = str(r.get("abstract") or "").lower() if r["abstract_status"] == "ok" else ""
        title_kw = title + " || " + kw            # promote signal source (high precision)
        has_kw = bool(kw.strip())
        judged = "abstract+keywords" if ab else ("title+keywords" if has_kw else "title_only")
        conf = "high" if (ab or has_kw) else "low"

        allt = " ".join([title, kw, ik, ab])
        prom = PROMOTE.search(title_kw) if FACADE_CTX.search(allt) else None
        move_any = bool(MOVE_ANY.search(allt))
        dem = DEMOTE.search(allt)

        if prom:
            full = " ".join([title, ab, kw])
            mech, study, perf = tag(full, bool(ab))
            new_dec.append("include"); why.append("PROMOTE: " + hits(PROMOTE, title_kw))
            newconf.append(conf); m_f.append(mech); s_t.append(study); p_r.append(perf)
            promoted.append({"eid": r["eid"], "title": r["title"],
                             "matched": hits(PROMOTE, title_kw),
                             "author_keywords": r.get("author_keywords"),
                             "abstract_head": str(r.get("abstract") or "")[:200],
                             "mechanism_family": mech, "study_type": study,
                             "performance_reported": perf, "judged_on": judged})
            n_prom += 1
        elif dem and not move_any:
            new_dec.append("exclude"); why.append("DEMOTE facade_no_movement: " + hits(DEMOTE, " ".join([title, kw, ab])))
            newconf.append(conf); m_f.append(""); s_t.append(""); p_r.append("")
            n_dem += 1
        else:
            new_dec.append("uncertain_fulltext")
            why.append("stay: no explicit movement/no-movement keyword cue")
            newconf.append("low" if judged == "title_only" else conf)
            m_f.append(""); s_t.append(""); p_r.append("")
            n_stay += 1

    s["new_decision"] = new_dec
    s["pass2_note"] = why
    s["confidence"] = newconf
    s["mechanism_family"] = m_f
    s["study_type"] = s_t
    s["performance_reported"] = p_r
    # demoted rows get reason_category facade_no_movement
    s.loc[(s["decision"] == "uncertain_fulltext") & (s["new_decision"] == "exclude"),
          "reason_category"] = "facade_no_movement"
    print(f"[pass2] uncertain 1131 -> promote={n_prom}, demote={n_dem}, stay={n_stay}")

    # write back screened (with new_decision) + drop merged helper cols
    keep = ["eid", "eff_doi", "title", "source", "doctype", "abstract_status",
            "decision", "new_decision", "reason_category", "confidence", "judged_on",
            "pass2_note", "mechanism_family", "study_type", "performance_reported",
            "one_line"]
    s[keep].to_csv(SCREENED, index=False)

    # included_final = original include + promoted
    inc = s[s["new_decision"] == "include"].copy()
    inc[["eid", "eff_doi", "title", "source", "doctype", "mechanism_family",
         "study_type", "performance_reported", "decision", "pass2_note"]].to_csv(
        INCLUDED, index=False)
    pd.DataFrame(promoted).to_csv(PROMOTED, index=False)
    print(f"[saved] {SCREENED.name}, {INCLUDED.name} (N={len(inc)}), "
          f"{PROMOTED.name} (N={len(promoted)})")

    bridge(inc)
    return s


def bridge(inc):
    n = len(inc)
    orig = inc[inc["decision"] == "include"]
    prom = inc[inc["decision"] == "uncertain_fulltext"]
    ct = pd.crosstab(inc["mechanism_family"], inc["performance_reported"])
    perf_any = int(inc["performance_reported"].isin(["energy", "daylight", "comfort", "multiple"]).sum())
    mech_spec = int((inc["mechanism_family"] != "unclear").sum())
    sim = int(inc["study_type"].eq("simulation").sum())
    built = int(inc["study_type"].isin(["experiment", "prototype"]).sum())

    L, A = [], lambda x: L.append(x)
    A("# Bridge-table 预览 v2(included_final,关键词二轮后)\n")
    A(f"> abstract/keyword-level 粗标,待全文核。included_final **N={n}** "
      f"(原 include {len(orig)} + 提级 {len(prom)})。\n")
    A("## 机制 × 性能 交叉表\n")
    A("| mechanism＼perf | " + " | ".join(ct.columns) + " |")
    A("|" + "---|" * (len(ct.columns) + 1))
    for idx, row in ct.iterrows():
        A(f"| {idx} | " + " | ".join(str(x) for x in row.values) + " |")
    A("\n## 关键读数(included_final vs 原 595)\n")
    A("| 指标 | 原 595 | included_final |")
    A("|---|---|---|")
    A(f"| N | 595 | {n} |")
    A(f"| 报告性能 % | 78% | {100*perf_any/n:.0f}% |")
    A(f"| 明确机制 % | 61% | {100*mech_spec/n:.0f}% |")
    A(f"| 机制 unclear % | 39% | {100*(n-mech_spec)/n:.0f}% |")
    A(f"| simulation : 实验/原型 | 0.9:1 (213/244) | {sim/max(built,1):.1f}:1 ({sim}/{built}) |")
    A(f"\n- included_final 占 Stage-2:{n}/2118 = {100*n/2118:.0f}%。")
    A("- 诚实:若 unclear 机制仍高 + 报告性能仍 ~78%,持续支持「性能重、机制轻」;"
      "simulation:built 仍接近 1:1,『只仿真不落地』证据仍不强 → 正文据实收敛。")
    (ROOT / "bridge_preview.md").write_text("\n".join(L), encoding="utf-8")
    print(f"[saved] bridge_preview.md (recomputed on included_final N={n})")


if __name__ == "__main__":
    main()
    sys.exit(0)
