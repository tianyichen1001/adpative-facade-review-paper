# PRISMA Counts

> Stage-1 = 标题 + OpenAlex concepts + 期刊 的**高敏感粗筛**(PROJECT_MEMORY.md §4.2 / §3.1)。
> 原则:只剔除**明显**不相关 / 越界者;"物理可动"严判留到 Stage-2(有摘要时)。`include + uncertain` = 进入 Stage-2 的"可能相关"集。
> 脚本:`03_screening/scripts/stage1_screen.py`(确定性、可复现);明细:`stage1_title_keyword.xlsx`;抽检:`stage1_spotcheck_40.csv`。

| 阶段 Stage | 数量 N |
|---|---|
| Identification (Scopus) | 2831 |
| 去重移除 Duplicates removed | 0(corpus 已按 eid 去重,2831 个 eid 唯一) |
| **Stage-1 排除 Excluded** | **426** |
| **Stage-1 保留(进入 Stage-2)** | **2405** |
| └─ include(明显可动表皮) | 423 |
| └─ uncertain(拿不准,保守保留) | 1982 |
| 抓摘要数(Cowork) | 〔Stage-2 时回填,基数 = 2405〕 |
| Screening-2 后(摘要细筛) | 〔待填〕 |
| Included | 〔待填〕 |

## Stage-1 排除明细(按类别)

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

## Stage-1 保留明细(按理由)

| reason_category | N | 含义 |
|---|---|---|
| soft_motion_facade | 1013 | 表皮 + 软词(adaptive/dynamic/responsive),**运动与否需摘要判定**(Stage-2 主战场) |
| kinetic_facade (include) | 423 | 表皮 + 强运动词(kinetic/movable/origami/SMA/hygromorphic…)→ 明显可动 |
| facade_no_explicit_motion | 391 | 有表皮词但标题无显式运动词(运动线索可能在摘要)→ 保留 |
| building_generic | 227 | 建筑语境但信号弱 → 保守保留 |
| no_signal_keep | 204 | 标题/concepts **无任何信号** → 高召回保守保留(**最低置信**,含真噪声) |
| soft_motion_no_building | 80 | 软词但无建筑语境 → 保留待查 |
| motion_no_building | 67 | 强运动但无建筑语境(可能是缺建筑词的 origami/SMA 表皮)→ 保留 |

## 人工核验 & 最不确定的类别

- **40 条分层随机抽检**(include 13 / exclude 14 / uncertain 13,seed=42)见 `stage1_spotcheck_40.csv`。include 全部为真·可动表皮;exclude 抽样均为真·跨域/静态;uncertain 抽样含预期的高召回噪声。
- **最不确定 / 最需 Stage-2 关注:**
  1. `soft_motion_facade`(1013):"adaptive/dynamic facade" 高度歧义——可能是真·kinetic,也可能是热工动态静态(PCM/动态保温)或控制算法。**Stage-2 摘要细筛将在此大量分流。**
  2. `no_signal_keep`(204):零信号保守保留,抽检可见真噪声(植物光照生长、车辆导航、控制理论、信号处理 "envelope" 假同源)。建议 Claude web 可先目检此列,决定是否在抓摘要前再轻筛一轮以省 Cowork 成本。
