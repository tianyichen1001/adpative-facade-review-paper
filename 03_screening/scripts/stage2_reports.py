"""Generate Stage-2 spot-check (40) and bridge-table preview (切入点 B test)."""
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
S = pd.read_csv(ROOT / "stage2_screened.csv")
SPOT = ROOT / "stage2_spotcheck_40.csv"
BRIDGE = ROOT / "bridge_preview.md"


def spotcheck():
    parts = []
    for dec, k in [("include", 12), ("uncertain_fulltext", 10),
                   ("exclude", 10), ("related_review", 4)]:
        sub = S[S["decision"] == dec]
        parts.append(sub.sample(min(k, len(sub)), random_state=42))
    low = S[S["confidence"] == "low"].sample(4, random_state=7)
    samp = pd.concat(parts + [low]).drop_duplicates("eid").head(40)
    samp[["eid", "title", "source", "doctype", "abstract_status", "decision",
          "reason_category", "confidence", "judged_on", "mechanism_family",
          "study_type", "performance_reported", "one_line"]].to_csv(SPOT, index=False)
    print(f"[saved] {SPOT.name} ({len(samp)})")


def bridge():
    inc = S[S["decision"] == "include"]
    n = len(inc)
    ct = pd.crosstab(inc["mechanism_family"], inc["performance_reported"])
    perf_any = int(inc["performance_reported"].isin(
        ["energy", "daylight", "comfort", "multiple"]).sum())
    mech_spec = int((inc["mechanism_family"] != "unclear").sum())
    sim = int(inc["study_type"].eq("simulation").sum())
    built = int(inc["study_type"].isin(["experiment", "prototype"]).sum())

    L, A = [], lambda x: L.append(x)
    A("# Bridge-table 预览(切入点 B 早期验证)\n")
    A(f"> ⚠️ **abstract-level 粗标,待全文核**(mechanism_family 因摘要常不写机制→unclear 偏高)。"
      f"在 **include 集(物理可动,N={n})** 上做,**如实呈现,即便与假设不符**。\n")
    A("## 1. 驱动机制\n| mechanism_family | N | % |\n|---|---|---|")
    for k, v in inc["mechanism_family"].value_counts().items():
        A(f"| {k} | {v} | {100*v/n:.0f}% |")
    A("\n## 2. 是否报告性能\n| performance_reported | N | % |\n|---|---|---|")
    for k, v in inc["performance_reported"].value_counts().items():
        A(f"| {k} | {v} | {100*v/n:.0f}% |")
    A("\n## 3. 研究类型\n| study_type | N | % |\n|---|---|---|")
    for k, v in inc["study_type"].value_counts().items():
        A(f"| {k} | {v} | {100*v/n:.0f}% |")
    A("\n## 4. 交叉表:机制 × 性能(核心证据预览)\n")
    A("| mechanism＼perf | " + " | ".join(ct.columns) + " |")
    A("|" + "---|" * (len(ct.columns) + 1))
    for idx, r in ct.iterrows():
        A(f"| {idx} | " + " | ".join(str(x) for x in r.values) + " |")
    A("\n## 5. 切入点 B 读数(诚实)\n")
    A(f"- 报告性能的 include:**{perf_any}/{n} = {100*perf_any/n:.0f}%**;"
      f"明确机制的:**{mech_spec}/{n} = {100*mech_spec/n:.0f}%**"
      f"(即 {100*(n-mech_spec)/n:.0f}% 连机制都没在摘要讲清)。"
      f"→ 支持「性能重、机制轻」:即便在已确认可动的论文里,性能叙述也多于机制刻画。")
    A(f"- 交叉表中 `unclear 机制` 行的性能格最满"
      f"(multiple={int(ct.loc['unclear','multiple'])}, energy={int(ct.loc['unclear','energy'])})"
      f"——谈性能却不点机制的论文集中于此,即断层带。")
    A(f"- ⚠️ 与假设**不符**的一点:simulation={sim} vs 实验/原型={built}"
      f"(约 {sim/max(built,1):.1f}:1),**并非压倒性仿真**;实验/原型({built})可观。"
      f"「只仿真不落地」在本语料证据不强,正文须据此收敛,勿硬撑。")
    A(f"- 全局:include(可动)= {n}/2118 = {100*n/2118:.0f}%,与 §1.1「~24% 碰运动」量级一致;"
      f"其余多落在 uncertain 的 adaptive/dynamic 大伞(印证 conflation)。")
    BRIDGE.write_text("\n".join(L), encoding="utf-8")
    print(f"[saved] {BRIDGE.name}")


if __name__ == "__main__":
    spotcheck()
    bridge()
    sys.exit(0)
