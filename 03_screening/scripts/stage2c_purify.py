"""Pass-3 purification:
 step0: apply 11 manual-QC decision edits.
 step1: purify the 640 includes -> core / no_specific_system / related_review /
        not_building (must present a CONCRETE movable facade system; vague-only out).
 step2: dissolve the 1052 uncertain into documented exclusion buckets; rescue any
        with a real movement cue back to core (precise read), rest -> insufficient_info.
 step3: included_core = core + rescued; update bridge_preview + prisma.
"""
import re
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]              # 03_screening/
SCREENED = ROOT / "stage2_screened.csv"
V4 = ROOT.parent / "04_abstracts" / "reports" / "stage2_with_abstracts_v4.csv"
CORE = ROOT / "included_core.csv"
REMOVED = ROOT / "removed_from_640.csv"
BUCKETS = ROOT / "uncertain_buckets.csv"
RESCUED = ROOT / "rescued_from_uncertain.csv"

# ---------- step 0 manual QC edits ----------
TO_REVIEW = {"2-s2.0-84992428115"}
TO_UNCERTAIN = {"2-s2.0-85142533892", "2-s2.0-85088049126", "2-s2.0-85018592600",
                "2-s2.0-84865596200", "2-s2.0-81255146361", "2-s2.0-84870586182",
                "2-s2.0-78149400279", "2-s2.0-85148544560", "2-s2.0-85140906999",
                "2-s2.0-70749085882"}

# ---------- vocab ----------
REVIEWY = re.compile(r"\breview\b|\boverview\b|\bsurvey\b|state[- ]of[- ]the[- ]art|"
                     r"systematic literature|bibliometric|a taxonomy of|literature review")
VAGUE = re.compile(
    r"\bframework\b|methodolog|workflow|design process|design tool|toolkit|toolset|"
    r"digital twin|\bbim\b|education|teaching|pedagog|curriculum|\bstudent|\bvision\b|"
    r"roadmap|\bpolicy\b|decision support|conceptual|concept of|theoretical exploration|"
    r"reflection|\bessay\b|discourse|\bart\b|artistic|interactive architecture|"
    r"ambient (display|media)|exhibition|speculative|manifesto|philosoph")
CONCRETE = re.compile(
    r"prototype|experiment|fabricat|mock[- ]?up|full[- ]scale|\btested\b|measured|"
    r"monitored|\bbuilt\b|installed|"
    r"\bmechanism\b|\bactuat|\bsma\b|shape[- ]memory|origami|kirigami|pneumatic|"
    r"hygromorph|\bhinge|linkage|camshaft|\bgear\b|\bmotor\b|\bservo|scissor|telescop|"
    r"bistable|compliant mechanism|"
    r"(rotat\w*|slid\w*|tilt\w*|fold\w*|deploy\w*|retract\w*|movable|operable|"
    r"adjustable)[\w\s,'-]{0,20}(louver|louvre|slat|blade|\bfin\b|panel|shad|module|"
    r"wing|flap|facade|fa.ade|skin|screen)|"
    r"(a|the|novel|new) [\w\s-]{0,18}(system|device|module|panel|louver|prototype) "
    r"(is|was|that|consist|compris|with)")
NOT_BLD = re.compile(r"tensegrity|asymptotic (grid|network)|gridshell|"
                     r"pure (kinematics|mechanism)|spatial structure(?! facade)")

# uncertain bucket vocab (no-movement classes)
CHROMO = re.compile(r"electrochrom|thermochrom|photochrom|gasochrom|switchable glaz|"
                    r"switchable window|chromogenic|suspended particle|\bspd\b|"
                    r"liquid crystal|\bpdlc\b|\btintable\b|thermotropic|smart glass")
PCM = re.compile(r"\bpcm\b|phase[- ]change|latent heat|thermal energy storage|"
                 r"thermal storage|heat storage|thermal mass")
VENT = re.compile(r"dynamic insulation|breathing wall|porous wall|air[- ]permeable|"
                  r"\btrombe|ventilated (cavity|facade|wall)|moisture transfer")
MEDIA = re.compile(r"media facade|media architecture|led facade|led display|"
                   r"digital facade|projection facade|lighting facade")
DSF = re.compile(r"double[- ]skin|\bdsf\b|second skin|double facade|double glass facade")
CONTROL = re.compile(r"control strateg|model predictive|reinforcement learning|"
                     r"\bmpc\b|optimi[sz]ation of (the )?(control|operation)|"
                     r"control of|controller|supervisory control|rule[- ]based control")
FACADE_CTX = re.compile(
    r"fa.ade|building skin|building envelope|\benvelope\b|\blouver|louvre|\bblind|"
    r"shading|brise|fenestration|mashrabiya|curtain wall|\bwindow|glazing|\bskin\b|"
    r"sunshade|shutter|daylight|second skin|double skin|\bbipv\b|building[- ]integrated")
# movement cue (-> movable_possible / rescue)
MOVECUE = re.compile(
    r"operable|\bfold|unfold|sliding|\bslid\w*|rotat\w*|tilt\w*|\bdeploy\w*|retract\w*|"
    r"movable|moveable|kinetic fa.ade|kinetic shad|origami|kirigami|pneumatic|inflat|"
    r"shape[- ]memory|\bsma\b|hygromorph|morphing|bistable|\bactuat|telescop|scissor|"
    r"adjustable (louver|slat|blade|fin|panel|shading)|moving (panel|louver|slat|element)|"
    r"venetian blind|\bflap\b|umbrella|tracking (louver|panel|facade|fin)")
# architectural deployable mechanisms (relevant even w/o explicit "facade", §3.4)
ARCH_DEPLOY = re.compile(r"origami|kirigami|miura|foldable|folded plate|deployable|"
                         r"scissor|tensegrity|hygromorph|\bsma\b|shape[- ]memory|pneumatic")
# hard cross-domain (clearly software/CG/aerospace; "facade" here = SW design pattern)
# -> not_facade unconditionally (building-ambiguous mppt/api deliberately excluded)
CROSS_HARD = re.compile(r"\bjava\b|\brmi\b|middleware|multiprotocol|microservice|"
                        r"distributed computing|software framework|volume rendering|"
                        r"ray tracing|\bspacecraft\b|\bsatellite\b")
# confirm real movement on full abstract (rescue precise read)
MOVE_CONFIRM = re.compile(
    r"physically (move|rotat|fold)|rotat\w* (louver|louvre|slat|blade|panel|fin|module)|"
    r"\bfold(s|ing|ed|able)\b|unfold|sliding (panel|louver|element)|deploy\w*|retract\w*|"
    r"pneumatic|inflat|shape[- ]memory|\bsma\b|hygromorph|origami|kirigami|"
    r"operable (window|panel|louver|facade|vent)|movable (shad|louver|panel|slat|fin)|"
    r"actuat\w* (the )?(louver|panel|facade|slat|fin|module|shade)|"
    r"opening and closing|tilt\w* (louver|slat|blade|panel|fin)|scissor|telescop|"
    r"morphing|bistable|umbrella-like|fan-like|origami-inspired")

MECH = [("material-driven", re.compile(r"\bsma\b|shape[- ]memory|hygromorph|hygroscop|thermo[- ]?respons|bimetal|4d print|stimuli")),
        ("pneumatic-soft", re.compile(r"pneumatic|inflat|air chamber|etfe|soft (actuat|robot)|cushion")),
        ("origami-deployable", re.compile(r"origami|kirigami|deploy|scissor|tessellat|foldable|\bfold")),
        ("compliant", re.compile(r"compliant mechanism|bistable|buckl|elastic instab|flexible hinge")),
        ("mechanical", re.compile(r"rotat|\bslid|tilt|pivot|\bhinge|motor|linkage|gear|louver|slat|operable|retract|telescop|movable|camshaft"))]
STUDY = [("experiment", re.compile(r"experiment|measured|wind tunnel|fabricat|tested|field (test|measurement)|monitored")),
         ("prototype", re.compile(r"prototype|mock[- ]?up|full[- ]scale|demonstrator|physical model")),
         ("simulation", re.compile(r"simulat|numerical|\bcfd\b|energyplus|modell?ed|computational|parametric|finite element|optimi[sz]ation")),
         ("theoretical", re.compile(r"theoretical|analytical model|mathematical|closed[- ]form")),
         ("case-study", re.compile(r"case study|case-study"))]
PERF = {"energy": re.compile(r"\benergy\b|heating|cooling|\bload\b|consumption|\bkwh|demand"),
        "daylight": re.compile(r"daylight|illuminance|\bglare\b|lighting|\budi\b|visual"),
        "comfort": re.compile(r"thermal comfort|visual comfort|\bpmv\b|comfort")}


def tg(text, has_ab):
    mech = next((n for n, r in MECH if r.search(text)), "unclear")
    study = next((n for n, r in STUDY if r.search(text)), "unclear")
    hit = [k for k, r in PERF.items() if r.search(text)]
    perf = "multiple" if len(hit) > 1 else (hit[0] if hit else ("none" if has_ab else "unclear"))
    return mech, study, perf


def main():
    s = pd.read_csv(SCREENED)
    v4 = pd.read_csv(V4)[["eid", "abstract", "abstract_status", "author_keywords", "index_keywords"]]
    s = s.drop(columns=["abstract_status"], errors="ignore").merge(v4, on="eid", how="left")
    s["pass3_note"] = ""
    s["bucket"] = ""

    # ---- step 0 ----
    s.loc[s["eid"].isin(TO_REVIEW), ["new_decision", "pass3_note"]] = ["related_review", "manual QC"]
    s.loc[s["eid"].isin(TO_UNCERTAIN), ["new_decision", "pass3_note"]] = ["uncertain_fulltext", "reverted by manual QC"]
    print("[step0] after edits:", dict(s["new_decision"].value_counts()))

    def text_of(r):
        ab = str(r["abstract"]) if r["abstract_status"] == "ok" else ""
        return " ".join([str(r["title"]), ab, str(r.get("author_keywords") or ""),
                         str(r.get("index_keywords") or "")]).lower()

    # ---- step 1: purify includes ----
    removed = []
    for i, r in s[s["new_decision"] == "include"].iterrows():
        t = text_of(r)
        has_ab = r["abstract_status"] == "ok"
        concrete = bool(CONCRETE.search(t))
        if REVIEWY.search(t) and not concrete:
            s.at[i, "new_decision"] = "related_review"; s.at[i, "pass3_note"] = "pass3: actually review/overview"
            removed.append((r["eid"], r["title"], "related_review", "review/overview, not primary system"))
        elif NOT_BLD.search(t) and not FACADE_CTX.search(t):
            s.at[i, "new_decision"] = "exclude"; s.at[i, "reason_category"] = "not_building"
            s.at[i, "pass3_note"] = "pass3: structural geometry, not building skin"
            removed.append((r["eid"], r["title"], "exclude:not_building", "pure structure/mechanism, no facade"))
        elif VAGUE.search(t) and not concrete:
            s.at[i, "new_decision"] = "exclude"; s.at[i, "reason_category"] = "no_specific_system"
            s.at[i, "pass3_note"] = "pass3: vague framework/vision/pedagogy, no concrete movable system"
            removed.append((r["eid"], r["title"], "exclude:no_specific_system", "kinetic as context only, no concrete system"))
        else:
            s.at[i, "pass3_note"] = "pass3: core (concrete movable system)"
    pd.DataFrame(removed, columns=["eid", "title", "to", "reason"]).to_csv(REMOVED, index=False)
    print(f"[step1] removed from 640: {len(removed)}; core now={int((s['new_decision']=='include').sum())}")

    # ---- step 2: dissolve uncertain ----
    rescued = []
    buckets = []
    for i, r in s[s["new_decision"] == "uncertain_fulltext"].iterrows():
        t = text_of(r)
        has_ab = r["abstract_status"] == "ok"
        facade = bool(FACADE_CTX.search(t))
        if CROSS_HARD.search(t):                     # software/CG/aerospace -> not_facade
            s.at[i, "new_decision"] = "exclude"; s.at[i, "reason_category"] = "not_facade"
            s.at[i, "bucket"] = "not_facade_other"
            continue
        if MOVECUE.search(t):                       # movable_possible -> precise read
            facade_ok = bool(FACADE_CTX.search(t) or ARCH_DEPLOY.search(t))
            if has_ab and MOVE_CONFIRM.search(t) and facade_ok:
                mech, study, perf = tg(t, True)
                s.at[i, "new_decision"] = "include"; s.at[i, "reason_category"] = ""
                s.at[i, "bucket"] = "movable_possible->include"
                s.at[i, "pass3_note"] = "pass3 rescue: movement confirmed"
                s.at[i, "mechanism_family"] = mech; s.at[i, "study_type"] = study
                s.at[i, "performance_reported"] = perf
                rescued.append((r["eid"], r["title"], "include", str(r.get("author_keywords") or "")[:60],
                                str(r["abstract"])[:180] if has_ab else ""))
                continue
            # has cue but not confirmed
            if not has_ab:
                s.at[i, "new_decision"] = "exclude"; s.at[i, "reason_category"] = "insufficient_info"
                s.at[i, "bucket"] = "movable_possible->insufficient_info"
                rescued.append((r["eid"], r["title"], "insufficient_info(no abstract)", "", ""))
                continue
            # abstract present, cue but no confirmed motion -> bucket as static/insufficient
            s.at[i, "new_decision"] = "exclude"; s.at[i, "reason_category"] = "insufficient_info"
            s.at[i, "bucket"] = "movable_possible->insufficient_info"
            rescued.append((r["eid"], r["title"], "insufficient_info(cue but unconfirmed)", "",
                            str(r["abstract"])[:180]))
            continue
        # no movement cue -> static buckets
        if not has_ab and not facade:
            bk, reason = "not_facade_other", "not_facade"
        elif CHROMO.search(t):
            bk, reason = "chromogenic", "facade_no_movement"
        elif PCM.search(t):
            bk, reason = "pcm_thermal", "facade_no_movement"
        elif VENT.search(t):
            bk, reason = "vent_breathing", "facade_no_movement"
        elif MEDIA.search(t):
            bk, reason = "media_led", "facade_no_movement"
        elif DSF.search(t):
            bk, reason = "dsf_static", "facade_no_movement"
        elif CONTROL.search(t) and facade:
            bk, reason = "control_of_static", "facade_no_movement"
        elif not has_ab:
            bk, reason = "insufficient_info", "insufficient_info"
        elif facade:
            bk, reason = "static_other", "facade_no_movement"
        else:
            bk, reason = "not_facade_other", "not_facade"
        s.at[i, "new_decision"] = "exclude"; s.at[i, "reason_category"] = reason; s.at[i, "bucket"] = bk
    pd.DataFrame(rescued, columns=["eid", "title", "outcome", "keywords", "abstract_head"]).to_csv(RESCUED, index=False)

    # bucket counts table (over the rows that were uncertain)
    bk = s[s["bucket"] != ""]
    print(f"[step2] rescued->include: {int((s['bucket']=='movable_possible->include').sum())}; "
          f"buckets: {dict(bk['bucket'].value_counts())}")

    # save uncertain_buckets.csv (all originally-uncertain rows)
    uncert_mask = (s["bucket"] != "") | (s["pass3_note"] == "reverted by manual QC")
    s.loc[s["bucket"] != "", ["eid", "title", "bucket", "new_decision", "reason_category"]].to_csv(BUCKETS, index=False)

    # ---- step 3: outputs ----
    drop_cols = ["abstract", "author_keywords", "index_keywords"]
    s.drop(columns=[c for c in drop_cols if c in s.columns]).to_csv(SCREENED, index=False)
    core = s[s["new_decision"] == "include"].copy()
    core[["eid", "eff_doi", "title", "source", "doctype", "mechanism_family",
          "study_type", "performance_reported", "decision", "bucket", "pass3_note"]].to_csv(CORE, index=False)
    print(f"[step3] included_core N={len(core)}")
    print("[final funnel]", dict(s["new_decision"].value_counts()))
    bridge(core)
    funnel(s)
    return s


def bridge(core):
    n = len(core)
    ct = pd.crosstab(core["mechanism_family"], core["performance_reported"])
    perf = int(core["performance_reported"].isin(["energy", "daylight", "comfort", "multiple"]).sum())
    mech = int((core["mechanism_family"] != "unclear").sum())
    sim = int(core["study_type"].eq("simulation").sum())
    built = int(core["study_type"].isin(["experiment", "prototype"]).sum())
    L, A = [], lambda x: L.append(x)
    A("# Bridge-table 预览 v3(included_core,pass-3 提纯后)\n")
    A(f"> abstract/keyword-level 粗标,待全文。included_core **N={n}**。\n")
    A("## 机制 × 性能\n| mechanism＼perf | " + " | ".join(ct.columns) + " |")
    A("|" + "---|" * (len(ct.columns) + 1))
    for idx, row in ct.iterrows():
        A(f"| {idx} | " + " | ".join(str(x) for x in row.values) + " |")
    A("\n## 关键读数(core vs 原 595 / 647)\n| 指标 | 595 | 647 | **core %d** |" % n)
    A("|---|---|---|---|")
    A(f"| 报告性能 % | 78 | 77 | **{100*perf/n:.0f}** |")
    A(f"| 明确机制 % | 61 | 58 | **{100*mech/n:.0f}** |")
    A(f"| 机制 unclear % | 39 | 42 | **{100*(n-mech)/n:.0f}** |")
    A(f"| simulation:实验原型 | 0.9:1 | 0.9:1 | **{sim/max(built,1):.1f}:1 ({sim}/{built})** |")
    A(f"\n- core 占 Stage-2:{n}/2118 = {100*n/2118:.0f}%。提纯剔除泛泛之作后,"
      "「性能重、机制轻」若仍成立则更稳;simulation:built 仍按数据如实呈现。")
    (ROOT / "bridge_preview.md").write_text("\n".join(L), encoding="utf-8")
    print(f"[saved] bridge_preview.md (core N={n})")


def funnel(s):
    nd = s["new_decision"].value_counts()
    exc = s[s["new_decision"] == "exclude"]
    L, A = [], lambda x: L.append(x)
    A("\n---\n\n## Stage-2c 三轮提纯(2026-06-09)— uncertain 归零\n")
    A("step0 落 11 条人工 QC;step1 对 640 按「具体可动系统」提纯;"
      "step2 把 1052 uncertain 全部装桶销账(movable_possible 精读捞回)。\n")
    A("| 最终决定 | N |\n|---|---|")
    for k in ["include", "related_review", "exclude", "uncertain_fulltext"]:
        A(f"| {k} | {int(nd.get(k, 0))} |")
    A(f"\n**纳入集 included_core = {int(nd.get('include',0))}**(`included_core.csv`)。uncertain 已归零。\n")
    A("### exclude 按 reason\n| reason | N |\n|---|---|")
    for k, v in exc["reason_category"].value_counts().items():
        A(f"| {k} | {v} |")
    A("\n### uncertain 装桶明细(1052)\n| bucket | N |\n|---|---|")
    bk = s[s["bucket"] != ""]
    for k, v in bk["bucket"].value_counts().items():
        A(f"| {k} | {v} |")
    A(f"\n- 提级捞回 movable_possible→include 已并入 core;removed_from_640 见同名 csv;"
      "rescued_from_uncertain.csv 列精读捞回供核。")
    with open(ROOT / "prisma_counts.md", "a", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")
    print("[saved] prisma_counts.md appended")


if __name__ == "__main__":
    main()
    sys.exit(0)
