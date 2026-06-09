"""PRISMA Stage-2 abstract screening — strict §3.1 physical-movement litmus.

Input : 04_abstracts/reports/stage2_with_abstracts_v3.csv (2118; abstract + keywords)
Litmus: INCLUDE only if a physical facade/envelope part visibly changes POSITION or
SHAPE (rotate/translate/fold/inflate/deform-with-motion) in a PRIMARY study.
Exclude facade_no_movement if the change is only optical/material-state, thermal, or
control-of-a-fixed-system. (PROJECT_MEMORY.md §1.1 / §3.1 / §3.3 / §4.4)

Decisions: include / exclude(not_facade|facade_no_movement|not_building) /
related_review / uncertain_fulltext. High sensitivity:真模糊 -> uncertain.
Abstracts judged on text; missing-abstract rows judged on title+concepts (lower conf).
"""

import re
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]            # 03_screening/
V3 = ROOT.parent / "04_abstracts" / "reports" / "stage2_with_abstracts_v3.csv"
ENRICHED = ROOT.parent / "02_enrichment" / "enriched.csv"
OUT = ROOT / "stage2_screened.csv"

# ---- physical movement (geometry/position change) — INCLUDE trigger --------------
# (a) standalone unambiguous mechanism / motion words
MOVE_MECH = re.compile(
    r"origami|kirigami|pneumatic|inflat|shape[- ]memory|\bsma\b|hygromorph|hygroscopic|"
    r"\bscissor|telescop|compliant mechanism|bistable|soft robot|unfold|"
    r"deployable|retractable|4d[- ]print|morphing|self[- ]shaping|foldable|"
    r"movable|moveable|operable (window|facade|fa.ade|panel|skin|shad)|"
    r"kinetic fa.ade|kinetic shad|kinetic envelope|kinetic skin|kinetic louver|"
    r"\bactuator|actuated|origami-inspired|umbrella-like|fan-like|"
    r"reconfigurable fa.ade|articulated (panel|louver|facade|fa.ade|element)")
# (b) motion verb NEAR a facade element (both word orders) — avoids "deployed system",
#     "tilt angle", "rotating artwork" false matches
_VERB = r"rotat\w*|\bslid\w*|\btilt\w*|pivot\w*|swivel\w*|\bfold\w*|deploy\w*|" \
        r"\bmov(e|es|ing|able)\b|adjust\w*|retract\w*|\bturn(s|ing)?\b"
_ELEM = r"louvers?|louvres?|slats?|blades?|\bfins?\b|panels?|shading|shade|shutter|" \
        r"fa.ade|\bskin\b|membrane|aperture|screen|fabric|module|wing|flap|component|unit"
MOVE_CTX = re.compile(
    rf"(?:{_VERB})[\w\s,'-]{{0,28}}(?:{_ELEM})|(?:{_ELEM})[\w\s,'-]{{0,28}}(?:{_VERB})")
MOVE = re.compile(MOVE_MECH.pattern + "|" + MOVE_CTX.pattern)
MOVE_STRONG = MOVE

# ---- media / LED facade (visual, no physical movement) -> facade_no_movement -----
MEDIA = re.compile(
    r"media facade|media architecture|media architectural|led facade|led display|"
    r"digital facade|lighting facade|projection facade|screen facade|"
    r"media (interface|content|wall)")

# ---- no-movement (optical / material-state) --------------------------------------
OPTICAL = re.compile(
    r"electrochrom|thermochrom|photochrom|gasochrom|\bpdlc\b|liquid crystal|"
    r"suspended particle|smart glass|switchable glaz|switchable window|chromogenic|"
    r"\btint|colou?r change|coloration|variable transmittance|variable transparency|"
    r"\bhaze\b|optical switch|transmittance modulation|radiative cooling coating|"
    r"thermochromic|photovoltaic glaz")
# ---- no-movement (thermal-dynamic, no moving part) -------------------------------
THERMAL = re.compile(
    r"phase change material|\bpcm\b|latent heat|thermal energy storage|"
    r"thermal storage|heat storage|dynamic insulation|breathing wall|porous wall|"
    r"\btrombe|thermal mass|thermochemical|switchable insulation|"
    r"ventilated (cavity|facade) (for|thermal)|air gap thermal")

# ---- facade / envelope context ---------------------------------------------------
FACADE = re.compile(
    r"fa.ade|building skin|building envelope|\benvelope\b|\blouver|louvre|\bblind|"
    r"shading (device|system|element|screen)|\bshading\b|brise|fenestration|mashrabiya|"
    r"curtain wall|\bwindow|glazing|\bskin\b|sunshade|shutter|daylight|second skin|"
    r"double skin|solar shading|building integrated|architectural")

# ---- cross-domain (not_facade) on title+abstract ---------------------------------
CROSS = re.compile(
    r"photovoltaic (array|system|module|cell)|\bmppt\b|maximum power point|inverter|"
    r"partial shading.*(pv|photovolta|array|panel)|microgrid|power converter|"
    r"\brendering\b|ray tracing|global illumination|gaussian splatting|point cloud|"
    r"tomograph|\bmri\b|echocardio|crop|greenhouse (crop|plant|tomato|lettuce)|"
    r"agrivoltaic|chlorophyll|photosynthesis|\bcancer\b|\bclinical\b|genome|"
    r"transcription factor|\bantenna\b|\bradar\b(?! chart)|wind turbine blade|"
    r"music|economic|finance")
# ---- not_building (moving structure, not a building skin) -------------------------
NOT_BLD = re.compile(
    r"spacecraft|satellite|space structure|space telescope|aerospace|aircraft wing|"
    r"\buav\b|drone|robot(ic)? (gripper|hand|arm|manipulat|finger)|grasper|"
    r"artificial muscle|prosthe|exoskeleton|wing morph|deployable boom|solar sail|"
    r"orbit|microgravity")

# ---- review markers --------------------------------------------------------------
REVIEW_WORDS = re.compile(r"review|state of the art|state-of-the-art|bibliometric|"
                          r"systematic literature|overview of")


def hits(rgx, t):
    found = [m.group(0) for m in rgx.finditer(t)]
    return "; ".join(sorted(set(found))[:3])


def classify(row):
    title = str(row["title"] or "")
    ab = str(row["abstract"] or "") if row["abstract_status"] == "ok" else ""
    kw = str(row.get("author_keywords") or "")
    con = str(row.get("oa_concepts") or "")
    judged_on = "abstract" if ab else "title_only"
    text = " ".join([title, ab, kw, con]).lower()

    facade = bool(FACADE.search(text))
    move = bool(MOVE.search(text))
    strong = bool(MOVE_STRONG.search(text))
    optical = bool(OPTICAL.search(text))
    thermal = bool(THERMAL.search(text))
    media = bool(MEDIA.search(text))
    cross = bool(CROSS.search(text))
    notbld = bool(NOT_BLD.search(text))
    is_review = str(row["doctype"]).strip().lower() == "review" or \
        bool(REVIEW_WORDS.search(title.lower()))

    conf = "high" if judged_on == "abstract" else "low"

    # 1) cross-domain & not facade -> not_facade
    if cross and not facade and not strong:
        return _r("exclude", "not_facade", conf, judged_on,
                  f"cross-domain ({hits(CROSS, text)}), no facade context")
    # 2) reviews -> related_review (if facade-relevant) else not_facade
    if is_review:
        if facade or strong:
            return _r("related_review", "review", conf, judged_on,
                      "review/secondary on facade topic — kept for intro/benchmark")
        return _r("exclude", "not_facade", conf, judged_on, "off-topic review")
    # 3) moving structure but not a building skin -> not_building
    if (strong or move) and notbld and not facade:
        return _r("exclude", "not_building", conf, judged_on,
                  f"movable structure but not building skin ({hits(NOT_BLD, text)})")
    # 4) facade context
    if facade:
        if strong:
            return _r("include", "", conf, judged_on,
                      f"facade + physical movement ({hits(MOVE_STRONG, text)})")
        if media:
            return _r("exclude", "facade_no_movement", conf, judged_on,
                      "media/LED facade — visual only, no physical movement")
        if optical and not move:
            return _r("exclude", "facade_no_movement", conf, judged_on,
                      f"optical/material-state, no geometry ({hits(OPTICAL, text)})")
        if thermal and not move:
            return _r("exclude", "facade_no_movement", conf, judged_on,
                      f"thermal-dynamic, no moving part ({hits(THERMAL, text)})")
        if move:  # movement word co-occurs with optical/thermal -> let full-text decide
            return _r("uncertain_fulltext", "", "low", judged_on,
                      "facade w/ both movement & optical/thermal cues — verify full text")
        # facade but no movement, no optical/thermal -> dynamic/adaptive unclear
        return _r("uncertain_fulltext", "", "low", judged_on,
                  "facade but abstract gives no explicit movement/optical/thermal cue")
    # 5) movement but no facade context (could be facade missing the word)
    if strong:
        return _r("uncertain_fulltext", "", "low", judged_on,
                  "movement mechanism but facade context unclear")
    # 6) nothing actionable
    return _r("exclude", "not_facade", conf, judged_on,
              "no facade context and no movement signal")


def _r(decision, reason, conf, judged_on, one_line):
    return decision, reason, conf, judged_on, one_line


# ---- lightweight tags for includes -----------------------------------------------
MECH = [
    ("material-driven", re.compile(r"\bsma\b|shape[- ]memory|hygromorph|hygroscop|"
                                   r"thermo[- ]?respons|bimetal|4d print|stimuli")),
    ("pneumatic-soft", re.compile(r"pneumatic|inflat|air chamber|etfe|soft (actuat|robot)|"
                                  r"cushion")),
    ("origami-deployable", re.compile(r"origami|kirigami|deploy|scissor|tessellat|"
                                      r"foldable|\bfold")),
    ("compliant", re.compile(r"compliant mechanism|bistable|buckl|elastic instab|"
                             r"flexible hinge")),
    ("mechanical", re.compile(r"rotat|\bslid|tilt|pivot|\bhinge|motor|linkage|gear|"
                              r"louver|slat|operable|retract|telescop")),
]
STUDY = [
    ("experiment", re.compile(r"experiment|measured|wind tunnel|fabricat|tested|"
                              r"field (test|measurement)|monitored")),
    ("prototype", re.compile(r"prototype|mock[- ]?up|full[- ]scale|demonstrator|"
                             r"physical model")),
    ("simulation", re.compile(r"simulat|numerical|\bcfd\b|energyplus|modell?ed|"
                              r"computational|parametric|finite element|optimi[sz]ation")),
    ("theoretical", re.compile(r"theoretical|analytical model|mathematical|closed[- ]form")),
    ("case-study", re.compile(r"case study|case-study")),
]
PERF = {
    "energy": re.compile(r"\benergy\b|heating|cooling|\bload\b|consumption|\bkwh|"
                         r"energy saving|energy demand"),
    "daylight": re.compile(r"daylight|illuminance|\bglare\b|lighting|\budi\b|"
                           r"daylight autonomy|visual"),
    "comfort": re.compile(r"thermal comfort|visual comfort|\bpmv\b|occupant comfort|"
                          r"comfort"),
}


def tag(row, text):
    mech = next((n for n, r in MECH if r.search(text)), "unclear")
    study = next((n for n, r in STUDY if r.search(text)), "unclear")
    perf_hit = [k for k, r in PERF.items() if r.search(text)]
    if len(perf_hit) > 1:
        perf = "multiple"
    elif perf_hit:
        perf = perf_hit[0]
    else:
        perf = "none" if row["abstract_status"] == "ok" else "unclear"
    return mech, study, perf


def main():
    df = pd.read_csv(V3)
    con = pd.read_csv(ENRICHED)[["eid", "oa_concepts"]]
    df = df.merge(con, on="eid", how="left")
    print(f"[input] {len(df)} rows; with abstract={int((df['abstract_status']=='ok').sum())}")

    recs = []
    for _, row in df.iterrows():
        decision, reason, conf, judged_on, one_line = classify(row)
        text = " ".join([str(row["title"]), str(row["abstract"]),
                         str(row.get("author_keywords") or "")]).lower()
        if decision == "include":
            mech, study, perf = tag(row, text)
        else:
            mech = study = perf = ""
        recs.append({
            "eid": row["eid"], "eff_doi": row["eff_doi"], "title": row["title"],
            "source": row["source"], "doctype": row["doctype"],
            "abstract_status": row["abstract_status"], "decision": decision,
            "reason_category": reason, "confidence": conf, "judged_on": judged_on,
            "mechanism_family": mech, "study_type": study,
            "performance_reported": perf, "one_line": one_line})
    out = pd.DataFrame(recs)
    out.to_csv(OUT, index=False)
    print(f"[saved] {OUT}")
    print("\n[decisions]")
    print(out["decision"].value_counts().to_string())
    print("\n[exclude by reason]")
    print(out[out["decision"] == "exclude"]["reason_category"].value_counts().to_string())
    print("\n[judged_on among non-ok abstracts]")
    nm = out[out["abstract_status"] == "missing"]
    print(nm["decision"].value_counts().to_string())
    return out


if __name__ == "__main__":
    main()
    sys.exit(0)
