"""PRISMA Stage-1b — lightweight re-screen of the 3 weakest kept buckets.

Stage-1 (stage1_screen.py) kept everything plausibly relevant (high recall). Three
buckets were kept on the weakest signal and contain substantial off-topic noise that
would waste downstream Cowork abstract-scraping:
    no_signal_keep, motion_no_building, soft_motion_no_building   (351 records)

Here every one of those 351 titles was read individually (model judgment, per
PROJECT_MEMORY.md §3.1: is this PLAUSIBLY a building skin/envelope that adapts via
PHYSICAL MOTION/displacement — shading/louver/deployable/SMA/pneumatic/origami/
morphing?). Records judged still-plausible are KEPT (listed below, by eid); the rest
are EXCLUDED with a best-fit category. Unsure -> kept (still high-recall).

This touches ONLY those 3 buckets; all other Stage-1 rows are left untouched.
Excluded rows get: stage1_decision='exclude', method='ai_rescreen', reason_category
= best-fit cross-domain class.
"""

import re
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CSV = ROOT / "stage1_title_keyword.csv"
XLSX = ROOT / "stage1_title_keyword.xlsx"

TARGET_BUCKETS = {"no_signal_keep", "motion_no_building", "soft_motion_no_building"}

# Records in the 3 buckets judged STILL plausibly an adaptive/movable building skin,
# shading device, or deployable/origami/SMA/pneumatic/membrane structure -> KEEP.
# (Per-title model judgment; e.g. thermo-pneumatic adaptive shading, SMA bi-stable
# structures, origami-linkage deployable, convertible/retractable roofs, hygromorphic
# 4D-print shading, Calatrava Milwaukee kinetic brise-soleil, responsive skins.)
KEEP_EIDS = {
    "2-s2.0-105024445764", "2-s2.0-105010957276", "2-s2.0-105002776077",
    "2-s2.0-105003105190", "2-s2.0-105027912674", "2-s2.0-85213353712",
    "2-s2.0-85195308006", "2-s2.0-85181014575", "2-s2.0-85184285537",
    "2-s2.0-85194749202", "2-s2.0-85207224128", "2-s2.0-85198731386",
    "2-s2.0-85148695173", "2-s2.0-85136534272", "2-s2.0-85143490994",
    "2-s2.0-85142533892", "2-s2.0-85132177960", "2-s2.0-85118508179",
    "2-s2.0-85129265183", "2-s2.0-85104604035", "2-s2.0-85099220530",
    "2-s2.0-85090845855", "2-s2.0-85083001459", "2-s2.0-85079212903",
    "2-s2.0-85053584841", "2-s2.0-84978473795", "2-s2.0-85000624359",
    "2-s2.0-85012864563", "2-s2.0-84936869055", "2-s2.0-84951037925",
    "2-s2.0-84942288016", "2-s2.0-84928232788", "2-s2.0-84883729570",
    "2-s2.0-84912544649", "2-s2.0-77953076867", "2-s2.0-39649108871",
    "2-s2.0-85214140676", "2-s2.0-85208768810", "2-s2.0-85206446952",
    "2-s2.0-85192358221", "2-s2.0-85169091659", "2-s2.0-85196944411",
    "2-s2.0-85141161213", "2-s2.0-85112097850", "2-s2.0-85044530680",
    "2-s2.0-85063474676", "2-s2.0-85072232827", "2-s2.0-85029901904",
    "2-s2.0-85010991418", "2-s2.0-84908406878", "2-s2.0-84906901718",
    "2-s2.0-84891276041", "2-s2.0-85209745683", "2-s2.0-85145608238",
    "2-s2.0-85133409780", "2-s2.0-85134547337", "2-s2.0-85124423553",
    "2-s2.0-85045693815", "2-s2.0-85040784002", "2-s2.0-85105618539",
    "2-s2.0-84994591823", "2-s2.0-84915749440", "2-s2.0-11144284617",
    "2-s2.0-0034781545",
}

# Best-fit category for EXCLUDED rows (title-based; for PRISMA bookkeeping only —
# the keep/exclude call is the model judgment above, category is secondary).
CATEGORY_RULES = [
    ("PV_electrical", re.compile(
        r"photovoltaic|\bpv\b|\bmppt\b|maximum power|inverter|solar cell|solar panel|"
        r"solar array|solar module|solar power|solar station|microgrid|converter|"
        r"\bvipv\b|\bcpv\b|power point|charging|wireless power|voltage regulation|"
        r"shaded pole|solar road")),
    ("ecology_agri", re.compile(
        r"greenhouse|\bcrop\b|crops|\brice\b|coffee|tomato|wheat|soybean|\bplant\b|"
        r"plants|seedling|\bforest\b|coral|fishery|fisheries|stream temp|agro|"
        r"cultivar|vermicompost|\bleaf\b|petiole|phytochrome|grass|\bspecies\b|"
        r"micropropagation|intercrop|orchard|vegetat|horticult|chlorophyll|"
        r"agrivolt|biofilt|phytosystem")),
    ("medical_graphics", re.compile(
        r"rendering|illumination|graphics|toon|stylized|stylised|\bpixel\b|shader|"
        r"ray tracing|tomograph|echocardio|angiograph|\bcamera\b|relight|splatting|"
        r"saliency|screentone|manga|visualization|global illumination|deferred shading|"
        r"shape-from-shading|shaded-relief|skeleton|eikonal|point cloud")),
    ("biomed_biology", re.compile(
        r"cancer|cochlear|cardiovascular|\bpatient|dental|virus|toxic|\bhealth\b|"
        r"anxiety|biosignal|\becg\b|lymphedema|genom|dystrophin|epithel|"
        r"\bfever\b|\brats\b|hearing|pancreas|ulcer|amalgam|"
        r"microplastic|formaldehyde|osteoarth|relaxation|cervical|virology")),
    ("aerospace_space", re.compile(
        r"cubesat|satellite|payload fairing|spacecraft|space age|space telescope|"
        r"\biue\b|flight test|aerospace|astronaut|star tracker|\borbit|young stellar|"
        r"astrochem|wind tunnel|fairing")),
    ("transport_infra", re.compile(
        r"\btrain\b|maglev|vehicle|powertrain|subway|\btunnel\b|railway|\bemu\b|"
        r"bogie|\bgauge\b|automotive|driving simulator|locomotive")),
    ("signal_radar", re.compile(
        r"\brf\b|amplifier|\bhemt\b|semiconductor|antenna|\bradar\b|sspa|"
        r"integrated circuit|predistortion")),
    ("other_nonbuilding", re.compile(
        r"robot|gripper|manipulator|artificial muscle|nanobeam|machine tool|"
        r"machining|grinding|forging|drilling|\bmusic\b|midi|timbre|piano|jazz|"
        r"economic|finance|oil price|cartel|linguistic|genocid|education|"
        r"e-learning|biometric|advertis|\bbid\b")),
]


def assign_category(title, concepts):
    # Drop the OpenAlex disambiguation artifact "Envelope (radar)" so building
    # "envelope" papers are not mislabeled signal_radar.
    c = str(concepts or "").lower().replace("envelope (radar)", "")
    text = (str(title or "") + " " + c).lower()
    for cat, rgx in CATEGORY_RULES:
        if rgx.search(text):
            return cat
    return "off_topic_lowsignal"


def main():
    df = pd.read_csv(CSV)
    mask = df["reason_category"].isin(TARGET_BUCKETS)
    target = df[mask]
    print(f"[stage1b] target rows (3 weak buckets): {len(target)}")
    assert len(target) == 351, f"expected 351, got {len(target)}"

    excl_mask = mask & ~df["eid"].isin(KEEP_EIDS)
    n_excl = int(excl_mask.sum())
    n_keep = int(mask.sum()) - n_excl
    print(f"[stage1b] keep={n_keep}  exclude={n_excl}")

    df.loc[excl_mask, "stage1_decision"] = "exclude"
    df.loc[excl_mask, "method"] = "ai_rescreen"
    df.loc[excl_mask, "reason_category"] = df.loc[excl_mask].apply(
        lambda r: assign_category(r["title"], r["oa_concepts"]), axis=1)

    df.to_csv(CSV, index=False)
    df.to_excel(XLSX, index=False)
    print(f"[saved] {CSV}\n[saved] {XLSX}")

    print("\n[stage1b excluded by category]")
    print(df.loc[excl_mask, "reason_category"].value_counts().to_string())

    print("\n[overall decisions now]")
    print(df["stage1_decision"].value_counts().to_string())
    return df


if __name__ == "__main__":
    main()
    sys.exit(0)
