# Stage-2 抓摘要输入清单 — 按出版商分组

来源:`03_screening/stage1_title_keyword.csv` 中 `stage1_decision ∈ {include, uncertain}` = **2118** 条。出版商按 DOI 前缀(10.xxxx)推断。
**本目录仅为 Cowork 抓摘要的输入清单,不含摘要本身**(PROJECT_MEMORY.md §7)。

> **无 DOI 找回(OpenAlex):** 原 316 条无 DOI 中找回 **84** 条 DOI (enriched_oa=83 / fresh_oa=1;标题 Jaccard≥0.90 且 年份差≤1 才接受),已并入对应出版商组;明细见 `no_doi_recovered.csv`。

## 出版商分布

| 组 group | 出版商 | 条数 N | 占比 | 文件 | Cowork 选择器 |
|---|---|---|---|---|---|
| elsevier | Elsevier / ScienceDirect | 604 | 28.5% | `elsevier.csv` | 有 (SOP §4a ScienceDirect/Elsevier) |
| other | Other (has DOI) | 485 | 22.9% | `other.csv` | 待补选择器 |
| no_doi | No DOI | 232 | 11.0% | `no_doi.csv` | 待补选择器 |
| mdpi | MDPI | 197 | 9.3% | `mdpi.csv` | 待补选择器 |
| springer | Springer | 170 | 8.0% | `springer.csv` | 待补选择器 |
| taylor_francis | Taylor & Francis | 91 | 4.3% | `taylor_francis.csv` | 有 (SOP §4b Taylor & Francis) |
| ieee | IEEE | 87 | 4.1% | `ieee.csv` | 待补选择器 |
| iop | IOP | 72 | 3.4% | `iop.csv` | 待补选择器 |
| wiley | Wiley | 38 | 1.8% | `wiley.csv` | 待补选择器 |
| asce | ASCE | 24 | 1.1% | `asce.csv` | 待补选择器 |
| sage | SAGE | 23 | 1.1% | `sage.csv` | 待补选择器 |
| acm | ACM | 20 | 0.9% | `acm.csv` | 待补选择器 |
| asme | ASME | 17 | 0.8% | `asme.csv` | 待补选择器 |
| wit | WIT Press | 15 | 0.7% | `wit.csv` | 待补选择器 |
| frontiers | Frontiers | 14 | 0.7% | `frontiers.csv` | 待补选择器 |
| edp | EDP Sciences | 13 | 0.6% | `edp.csv` | 待补选择器 |
| transtech | Trans Tech | 11 | 0.5% | `transtech.csv` | 待补选择器 |
| nature | Nature (Springer Nature) | 5 | 0.2% | `nature.csv` | 待补选择器 |
| **合计** | | **2118** | 100% | | |

- **已有选择器覆盖:** 695 / 2118 = 32.8%(ScienceDirect/Elsevier + Taylor & Francis)。
- **待补选择器:** 其余 1423 条(Nature/Springer、Wiley、MDPI、IEEE、IOP、Frontiers、ACM 等),按本表条数从多到少补 DOM 选择器。

## `other`(有 DOI、未归类)组 DOI 前缀 Top-10

> 出版商/期刊取自该前缀下最常见的 `source`(数据驱动,供判断是否补选择器)。

| DOI 前缀 | 条数 | 最常见期刊/来源 |
|---|---|---|
| 10.52842 | 69 | Proceedings of the International Conference on Educatio |
| 10.26868 | 30 | Building Simulation Conference Proceedings |
| 10.7480 | 27 | Journal of Facade Design and Engineering |
| 10.1108 | 20 | Open House International |
| 10.15627 | 18 | Journal of Daylighting |
| 10.1201 | 16 | Advances in Engineering Materials Structures and System |
| 10.1117 | 14 | Proceedings of SPIE the International Society for Optic |
| 10.1260 | 12 | International Journal of Architectural Computing |
| 10.13189 | 10 | Civil Engineering and Architecture |
| 10.1063 | 9 | Aip Conference Proceedings |

## 无 DOI

- `no_doi.csv`:**232** 条(多为会议/书章)。无 DOI → Cowork 无法按 DOI 抓;需靠标题/来源人工定位或在 Stage-2 标记为无摘要。