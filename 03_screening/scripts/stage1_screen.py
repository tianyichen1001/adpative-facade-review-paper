"""PRISMA Stage-1 screening (title + OpenAlex concepts + journal).

High-recall coarse screen of the finalized corpus (enriched.csv, N=2831) down to a
"possibly relevant" set for Stage-2 (abstract) screening. Per PROJECT_MEMORY.md
§3.1 (core criterion = PHYSICAL MOTION / displacement), §3.3 (exclude visually-
static optical / thermal-dynamic envelopes), §3.4 (boundary table), §4.2 (PRISMA).

Design principles:
  - HIGH SENSITIVITY: only drop CLEARLY out-of-scope / cross-domain records.
    Anything possibly relevant -> keep. When unsure -> 'uncertain' (kept).
  - Strict "is it physically movable?" is deferred to Stage-2 (needs abstracts).
  - Titles are the primary signal for cross-domain EXCLUSION; OpenAlex concepts are
    supporting only, because they carry disambiguation noise (e.g. the building word
    "envelope" is mislabeled with the concept "Envelope (radar)"). Concepts ARE used
    (with titles) to detect building-context and motion (high recall there is safe).

Method tags:
  - 'rule' : high-precision deterministic rules (cross-domain / thermal / optical
             excludes; strong-motion + building includes).
  - 'ai'   : topical-judgment layer for the gray zone (soft-motion facade,
             building-without-explicit-motion, motion-without-building) -> kept as
             include/uncertain. These heuristics were designed by the model from a
             manual read of the corpus and validated by sampling.

Output: 03_screening/stage1_title_keyword.xlsx (+ .csv) with stage1_decision,
reason_category, method, signals.
"""

import re
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
ENRICHED = ROOT.parent / "02_enrichment" / "enriched.csv"
OUT_XLSX = ROOT / "stage1_title_keyword.xlsx"
OUT_CSV = ROOT / "stage1_title_keyword.csv"

# --- Signal vocabularies (lowercase regex) -----------------------------------------
# Building / facade context (title + concepts). High recall is SAFE here (keeps).
BUILDING = re.compile(
    r"fa.ade|building|architect|\blouver|louvre|venetian|\bblind\b|blinds|"
    r"window|glazing|glaz|daylight|fenestration|brise|mashrabiya|curtain wall|"
    r"\bskin\b|second skin|double skin|indoor|\broom\b|occupant|thermal comfort|"
    r"shading device|shading system|solar shading|\bbipv\b|building.integrated|"
    r"construction|\bhvac\b|\bashrae\b|interior|envelope|sun.?breaker|sunshade|shutter")
BUILDING_JOURNAL = re.compile(
    r"building|architect|construction|civil engineer|\bhvac\b|ashrae|daylight|"
    r"fa.ade|built environment|indoor|sustainab|energy and build|"
    r"computer aided architectural|caad|urban|housing|cities")  # NB: 'solar energy'
    # deliberately omitted — it shelters pure-PV/MPPT papers; genuine BIPV-facade
    # work carries facade/shading/bipv in the title and is kept via BUILDING.

# Strong (unambiguous physical movement)
STRONG = re.compile(
    r"kinetic|movable|moveable|deployable|origami|kirigami|morph|\bfold|retractable|"
    r"pneumatic|inflatable|shape memory|\bsma\b|shape.?chang|bistable|actuat|"
    r"hygromorph|rotat|sliding|\bslide\b|tilting|\btilt\b|scissor|tensegrity|swivel|"
    r"articulat|telescop|expandable|unfold|moving|movement|\bmotion\b|hinged|"
    r"pivot|operable|tracking facade|sun.?tracking|self.?shaping|4d print")
# Soft (ambiguous: could be motion, control, or thermal)
SOFT = re.compile(
    r"adaptive|adaptable|dynamic|responsive|\bsmart\b|intelligent|reconfigurable|"
    r"convertible|biomimetic|bio.?inspired|bioinspired|interactive|\bflexible\b|"
    r"transformable")
# Facade-family component words (a building paper mentioning these but no motion is
# still plausibly a kinetic study described only in the abstract -> keep uncertain).
FACADE_FAMILY = re.compile(
    r"fa.ade|\blouver|louvre|\bblind|shading|\bskin\b|brise|fenestration|"
    r"mashrabiya|envelope|shutter|curtain wall|sunshade")

# Visually-static OPTICAL (no displacement) -> exclude (§3.3)
OPTICAL = re.compile(
    r"electrochrom|thermochrom|photochrom|gasochrom|\bpdlc\b|liquid crystal|"
    r"suspended particle|media facade|media architecture|\bled facade\b|"
    r"lighting facade|switchable glazing|switchable window")
# Thermal-dynamic but static envelope -> exclude (§3.3 / §3.4)
THERMAL = re.compile(
    r"phase change material|\bpcm\b|latent heat|thermal energy storage|"
    r"thermal storage|heat storage|dynamic insulation|breathing wall|breathing panel|"
    r"porous wall|hygrothermal|thermal mass|trombe|thermal buffer|"
    r"variable thermal|switchable insulation")

# Cross-domain EXCLUSION (matched on TITLE ONLY — concepts carry disambiguation
# noise, e.g. "Computer graphics"/"Signal processing"/"Envelope (radar)" get attached
# to building papers; require NOT building-context).
CROSS_DOMAIN = [
    ("PV_electrical", re.compile(
        r"photovoltaic|\bpv\b|\bmppt\b|maximum power point|maximum power|inverter|"
        r"solar cell|dc.?dc|boost converter|buck converter|power point tracking|"
        r"grid.connected|\bmicrogrid\b|state of charge")),
    ("medical_graphics", re.compile(
        r"tomography|volume rendering|radiograph|\bmri\b|ultrasound|computer graphics|"
        r"\bray tracing\b|\brendering\b|relight|splatting|point cloud|photorealistic|"
        r"biomedical|neonatal|breastfeed|\bpatient|clinical|in vitro|in vivo|\btumor")),
    ("ecology_agri", re.compile(
        r"fishery|fisheries|\balgae\b|\bcrop\b|crops|agricultur|agrivoltaic|riparian|"
        r"seedling|\bforest\b|photosynthesis|\bleaf\b|leaves|grazer|grazing|"
        r"desiccation|livestock|\bsoil\b|vegetation|biomass|"
        r"ecosystem|wetland|pollinat|orchard|cultivar|greenhouse crop|sweetpot")),
    ("biomed_biology", re.compile(
        r"genome|transcriptom|transcription factor|endothelial|sinusoidal|hepat|"
        r"steato|metabolic dysfunction|disinfection|phenolog|\bpeach\b|fruit shape|"
        r"sleep.?disorder|nuclei segmentation|\bprotein\b|\benzyme\b|\bgene\b|"
        r"pathogen|antimicrob|antioxidant.propert")),
    ("signal_radar", re.compile(
        r"\bradar\b|antenna|\bsonar\b|waveform|microwave|electromagnetic scatter|"
        r"\bmimo\b|spectrum sensing|music structure")),
    ("aerospace_space", re.compile(
        r"spacecraft|satellite|space telescope|aerospace|\borbit|\bmars\b|martian|"
        r"lunar|deployable boom|solar sail|reentry|re.entry|aircraft wing|\buav\b|"
        r"pyroshock")),
    ("transport_infra", re.compile(
        r"railway|grade crossing|pantograph|high.?speed train|locomotive|catenary|"
        r"mass transit|\blrt\b|highway")),
    ("software_hci", re.compile(
        r"facade pattern|design pattern|microservice|\bapi gateway\b|user interface|"
        r"software architecture|web service|middleware|source code")),
    ("other_nonbuilding", re.compile(
        r"\bpig\b|\bpigs\b|swine|poultry|cattle|\bsheep\b|grinding wheel|"
        r"machine tool|automotive crash|vehicle detection|food packaging|"
        r"textile fashion|garment|footwear|forging")),
]


def first_hits(rgx, text, k=3):
    return "; ".join(sorted(set(rgx.findall(text)))[:k]) if rgx.findall(text) else ""


def classify(title, concepts, source):
    t = str(title or "").lower()
    c = str(concepts or "").lower().replace("envelope (radar)", "")  # drop false friend
    s = str(source or "").lower()
    text = t + " || " + c

    has_building = bool(BUILDING.search(text)) or bool(BUILDING_JOURNAL.search(s))
    strong = bool(STRONG.search(text))
    soft = bool(SOFT.search(text))

    sig = []
    if strong:
        sig.append("strong:" + first_hits(STRONG, text))
    if soft:
        sig.append("soft:" + first_hits(SOFT, text))
    if has_building:
        sig.append("bldg:" + (first_hits(BUILDING, text) or "journal"))
    signals = " | ".join([x for x in sig if x])

    # A soft-motion word next to a facade term is the ambiguous "dynamic/adaptive
    # envelope" case -> never hard-exclude on thermal/optical; keep for Stage-2.
    soft_facade = soft and bool(FACADE_FAMILY.search(text))

    # ---- Building-context records -------------------------------------------------
    if has_building:
        if strong:
            return "include", "kinetic_facade", "rule", signals
        if THERMAL.search(text) and not soft_facade:
            return "exclude", "thermal_static", "rule", "thermal:" + first_hits(THERMAL, text)
        if OPTICAL.search(text) and not soft_facade:
            return "exclude", "optical_static", "rule", "optical:" + first_hits(OPTICAL, text)
        if soft:
            return "uncertain", "soft_motion_facade", "ai", signals
        if FACADE_FAMILY.search(text):
            return "uncertain", "facade_no_explicit_motion", "ai", signals
        return "uncertain", "building_generic", "ai", signals

    # ---- No building-context (cross-domain matched on TITLE only) ------------------
    for cat, rgx in CROSS_DOMAIN:
        if rgx.search(t):
            return "exclude", cat, "rule", cat + ":" + first_hits(rgx, t)
    if THERMAL.search(text) and not strong and not soft_facade:
        return "exclude", "thermal_static", "rule", "thermal:" + first_hits(THERMAL, text)
    if OPTICAL.search(text) and not strong and not soft_facade:
        return "exclude", "optical_static", "rule", "optical:" + first_hits(OPTICAL, text)
    if strong:
        # motion but no building context: could be an origami/SMA facade missing the
        # building word in title -> keep uncertain (high recall).
        return "uncertain", "motion_no_building", "ai", signals
    if soft:
        return "uncertain", "soft_motion_no_building", "ai", signals
    # neither building nor motion nor cross-domain signal in title/concepts: signal is
    # presumably only in the (unseen) abstract -> keep uncertain, do not drop.
    return "uncertain", "no_signal_keep", "ai", signals


def main():
    e = pd.read_csv(ENRICHED)
    assert e["eid"].is_unique, "eid not unique"
    print(f"[input] {len(e)} records (Identification, eid-deduped)")

    out = e[["eid", "doi", "title", "year", "source", "doctype", "oa_concepts"]].copy()
    decisions = e.apply(
        lambda r: classify(r["title"], r["oa_concepts"], r["source"]), axis=1)
    out["stage1_decision"] = [d[0] for d in decisions]
    out["reason_category"] = [d[1] for d in decisions]
    out["method"] = [d[2] for d in decisions]
    out["signals"] = [d[3] for d in decisions]

    out.to_csv(OUT_CSV, index=False)
    out.to_excel(OUT_XLSX, index=False)
    print(f"[saved] {OUT_CSV}\n[saved] {OUT_XLSX}")

    # Summary
    print("\n[decisions]")
    print(out["stage1_decision"].value_counts().to_string())
    print("\n[exclude by category]")
    exc = out[out["stage1_decision"] == "exclude"]
    print(exc["reason_category"].value_counts().to_string())
    print("\n[kept by reason]")
    kept = out[out["stage1_decision"].isin(["include", "uncertain"])]
    print(kept["reason_category"].value_counts().to_string())
    print(f"\n[method] {dict(out['method'].value_counts())}")
    return out


if __name__ == "__main__":
    main()
    sys.exit(0)
