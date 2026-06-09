# PRISMA Counts

> Stage-1 = 标题 + OpenAlex concepts + 期刊 的**高敏感粗筛**(PROJECT_MEMORY.md §4.2 / §3.1)。
> 原则:只剔除**明显**不相关 / 越界者;"物理可动"严判留到 Stage-2(有摘要时)。`include + uncertain` = 进入 Stage-2 的"可能相关"集。
> 脚本:`stage1_screen.py`(Stage-1a 确定性规则)+ `stage1b_rescreen.py`(Stage-1b 弱桶逐条复核)。明细:`stage1_title_keyword.xlsx`;抽检:`stage1_spotcheck_40.csv`、`stage1b_spotcheck_30.csv`。

| 阶段 Stage | 数量 N |
|---|---|
| Identification (Scopus) | 2831 |
| 去重移除 Duplicates removed | 0(corpus 已按 eid 去重,2831 个 eid 唯一) |
| **Stage-1 排除 Excluded(合计)** | **713** |
| └─ Stage-1a(规则粗筛) | 426 |
| └─ Stage-1b(弱桶再筛) | 287 |
| **Stage-1 保留(进入 Stage-2)** | **2118** |
| └─ include(明显可动表皮) | 423 |
| └─ uncertain(拿不准,保守保留) | 1695 |
| 抓摘要数(摘要覆盖) | 1874/2118 = 88.5%(scrape+OpenAlex+Scopus,见 §下 Stage-2) |
| Screening-2 后(摘要细筛) | include 595 + related_review 141 + uncertain_fulltext 1131(exclude 251) |
| Included(纳入集) | **647**(595 + 关键词二轮提级 52;详见 Stage-2b) |

## Stage-1b 弱桶再筛(2026-06-08)

只复核 Stage-1a 最弱的 3 个保留桶(共 **351** 条),逐条读标题(辅以 concepts/source)按 §3.1 判"是否可能为物理可动的建筑表皮/遮阳/可展围护"。**只动这 3 桶,其它桶不变。** 拿不准 → 保留。

| 桶 | 原数 | 保留 | 剔除 |
|---|---|---|---|
| no_signal_keep | 204 | 12 | 192 |
| soft_motion_no_building | 80 | 16 | 64 |
| motion_no_building | 67 | 36 | 31 |
| **合计** | **351** | **64** | **287** |

**保留的 64 条**(eid 见 `scripts/stage1b_rescreen.py` 的 `KEEP_EIDS`)= 真·可动表皮/结构:thermo-pneumatic / 气动自适应遮阳、SMA 双稳结构、origami-linkage 可展、convertible / retractable roof、4D 打印 hygromorph 遮阳、tensegrity / scissor 可展、Milwaukee Art Museum(Calatrava 动态 brise-soleil)、responsive skins 等。

**Stage-1b 剔除 287 条(按类别;类别为自动粗分,keep/exclude 决定为逐条人工判定):**

| reason_category | N |
|---|---|
| off_topic_lowsignal | 88 |
| medical_graphics | 54 |
| other_nonbuilding | 37 |
| ecology_agri | 31 |
| biomed_biology | 26 |
| PV_electrical | 20 |
| transport_infra | 15 |
| aerospace_space | 10 |
| signal_radar | 6 |
| **合计** | **287** |

> 抽检:`stage1b_spotcheck_30.csv`(20 剔除 + 10 保留)。剔除抽样均为真·跨域(CG 渲染、病毒/毒理、火车/车辆、机械手、卫星热分析、作物等);保留抽样均为真·可动结构(origami / 4D 木双层 hygromorph / 可展 scissor / responsive skins)。**类别标签为关键词自动归类、较粗**,但每条的 keep/exclude 系逐条阅读判定。

## Stage-1a 排除明细(按类别,规则粗筛 426)

| reason_category | N | 说明 |
|---|---|---|
| PV_electrical | 213 | 光伏电气(MPPT / PV array / inverter / 海上光伏等),**无建筑语境**;BIPV/遮阳表皮含 facade/shading 者已保留 |
| thermal_static | 76 | 热工动态但视觉静态(PCM 热墙 / 动态保温 / 热质 / trombe);§3.3 |
| optical_static | 49 | 电致/热致变色、PDLC、液晶、media facade(视觉变化无位移);§3.3 |
| medical_graphics | 28 | 计算机图形渲染(shading algorithm / ray tracing / 点云 / relighting)、医学影像 |
| ecology_agri | 22 | 农业/生态(agrivoltaic / 作物 / 遮阴对植物) |
| biomed_biology | 11 | 分子生物/医学(基因组 / 转录因子 / 肝内皮细胞 / 睡眠呼吸) |
| other_nonbuilding | 9 | 牲畜运输、机床、车辆检测等明显跨域 |
| aerospace_space | 9 | 航天器/卫星/空间望远镜可展结构 |
| transport_infra | 8 | 铁路道口/受电弓/轨道交通 |
| signal_radar | 1 | 雷达/天线/信号处理 |
| **合计** | **426** | |

> ⚠️ 关键 QC 教训:OpenAlex **concepts 带消歧噪声**(把建筑 "envelope" 误标为概念 `Envelope (radar)`,把建筑遮阳论文误标 `Computer graphics` / `Signal processing`)。因此**跨域排除只用标题**,concepts 仅作建筑语境/运动信号(此方向高召回安全)。修正后救回多篇被误排的相关论文(如 "morphing of shading"、"adaptive façades control"、"movable PCM layer")。

## Stage-1 保留明细(按理由,Stage-1b 后,合计 2118)

| reason_category | N | 含义 |
|---|---|---|
| soft_motion_facade | 1013 | 表皮 + 软词(adaptive/dynamic/responsive),**运动与否需摘要判定**(Stage-2 主战场) |
| kinetic_facade (include) | 423 | 表皮 + 强运动词(kinetic/movable/origami/SMA/hygromorphic…)→ 明显可动 |
| facade_no_explicit_motion | 391 | 有表皮词但标题无显式运动词(运动线索可能在摘要)→ 保留 |
| building_generic | 227 | 建筑语境但信号弱 → 保守保留 |
| motion_no_building | 36 | 强运动但无建筑语境(origami/SMA/可展结构)→ Stage-1b 复核后保留 |
| soft_motion_no_building | 16 | 软词但无建筑语境(adaptive shading 等)→ Stage-1b 复核后保留 |
| no_signal_keep | 12 | 原零信号桶,Stage-1b 复核后仅留下确像表皮/结构者 |

> 注:`no_signal_keep`(204→12)、`soft_motion_no_building`(80→16)、`motion_no_building`(67→36)三桶经 Stage-1b 逐条复核压缩;其余四桶未动。

## 人工核验 & 最不确定的类别

- **40 条分层随机抽检**(include 13 / exclude 14 / uncertain 13,seed=42)见 `stage1_spotcheck_40.csv`。include 全部为真·可动表皮;exclude 抽样均为真·跨域/静态;uncertain 抽样含预期的高召回噪声。
- **最不确定 / 最需 Stage-2 关注:**
  1. `soft_motion_facade`(1013):"adaptive/dynamic facade" 高度歧义——可能是真·kinetic,也可能是热工动态静态(PCM/动态保温)或控制算法。**Stage-2 摘要细筛将在此大量分流。**
  2. ~~`no_signal_keep`(204):零信号保守保留,含真噪声~~ → **已由 Stage-1b 弱桶再筛处理**(204→12),连同 `soft_motion_no_building`、`motion_no_building` 一并复核,共剔除 287,Stage-2 基数从 2405 降至 **2118**。

---

## Stage-2 摘要细筛(2026-06-09)— 严格 §3.1 物理可动

输入 = Stage-2 集 2118(摘要覆盖 88.5%:`stage2_with_abstracts_v3`)。litmus = **表皮物理部件可见地改变位置/形状**(旋转/平移/折叠/充气/带运动形变)且一手研究;只变光学态/热工/控制固定系统 → 排除。脚本:`scripts/stage2_screen.py`(规则+灰区 AI);抽检 `stage2_spotcheck_40.csv`;桥接表预览 `bridge_preview.md`。

| 决定 Decision | N | 占比 |
|---|---|---|
| **include(物理可动,一手)** | **595** | 28.1% |
| related_review(综述,留作引言/对标) | 141 | 6.7% |
| **exclude** | **251** | 11.8% |
| └ facade_no_movement(光学/热工/媒体静态) | 159 | |
| └ not_facade(跨域噪声) | 92 | |
| └ not_building(可动但非建筑表皮) | 0 | |
| **uncertain_fulltext(摘要未明物理运动,待全文)** | **1131** | 53.4% |

- **无摘要 244 条**(title-only 判,置信降低):uncertain 153 / exclude 60 / include 26 / related_review 5——即 ~63% 无摘要者保守留 uncertain。
- **uncertain 占 53%** 是真实信号,不是失败:大量 "adaptive/dynamic/responsive façade" 在摘要层面分不清是否物理可动——这正是 §1.1 要划界的 conflation 带,留全文核。
- **PRISMA Stage-2 漏斗:** 2118 →(细筛)→ include 595 + related_review 141 + uncertain 1131(待全文)+ exclude 251。**纳入集 = 595(+ 全文核 uncertain 后增补)。**

---

## Stage-2b 关键词二轮筛(2026-06-09)— 并入 Scopus 作者关键词后

并入 Scopus 全导出作者关键词(v4:author_keywords 126→**1559**=73.6%,index_keywords 1352)后,对一轮 1131 个 `uncertain_fulltext` 用 **标题+作者关键词** 重判。**红线:绝不因 adaptive/dynamic/responsive/smart 等 buzzword 提级**(经核实 0 例违规);提级须同时具备**明确运动/机制词 + 表皮语境**。脚本 `scripts/stage2b_rescreen.py`。

| 去向 | N |
|---|---|
| → include(提级,关键词含 kinetic/origami/SMA/movable/foldable… + 表皮语境) | **52** |
| → exclude facade_no_movement(降除:DSF 无 operable / 电致变色 / PCM 蓄热 / 动态保温) | 37 |
| 仍 uncertain_fulltext(真说不清,conflation 证据 / limitation) | 1042 |

### 二轮后 Stage-2 漏斗(终)
| 决定 | N | 占比 |
|---|---|---|
| **include(纳入集 included_final)** | **647** | 30.5% |
| related_review | 141 | 6.7% |
| exclude(facade_no_movement 196 + not_facade 92) | 288 | 13.6% |
| uncertain_fulltext(待全文,limitation) | 1042 | 49.2% |

- **纳入集 included_final = 647**(原 595 + 提级 52)→ `included_final.csv`(含 §4.4 轻量标签)。
- 提级项全列于 `promoted_from_uncertain.csv` 供人工核(~45/52 明确为 kinetic/movable 表皮,余为表皮语境的概念性论文,已标注)。
- uncertain 仍 1042(49%):并入关键词后只能再切出 89 条(52+37),其余确实在摘要+关键词层面分不清是否物理可动——**这正是 §1.1 conflation 的量化证据**,留全文核。
- bridge_preview(在 647 上重算):报告性能 77% / 机制明确 58%(unclear 42%)/ simulation:实验原型 ≈ 0.9:1 —— 与原 595 一致:**「性能重、机制轻」成立;「只仿真不落地」证据弱**(如实)。
