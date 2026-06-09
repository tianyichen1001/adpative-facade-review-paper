# Bibliometrics DEMO — 流水线试跑(非最终计量)

> ⚠️ **这是流水线测试,不是最终计量。** 最终计量按 PROJECT_MEMORY.md §4.3 跑在**纳入集**(Stage-2 摘要细筛后),不是这版 Stage-2 集(2118,仍含 PV/MPPT 等待剔除的离题项)。
> 脚本:`scripts/demo_bibliometrics.py`。

## 产出文件

| 路径 | 内容 |
|---|---|
| `corpus_for_biblio/corpus_stage2.csv` | 元数据(concepts/作者/机构/国家/被引/参考文献)⋈ 摘要,2118 行;其中 **1439 带摘要(67.9%)** |
| `figures/01_year_trend.png` | 年度发文趋势 |
| `figures/02_top_sources.png` | 高产期刊 Top15 |
| `figures/03_top_countries.png` | 国家 Top15(OpenAlex) |
| `figures/04_top_institutions.png` | 机构 Top15(OpenAlex) |
| `figures/05_top_cited.png` | 高被引 Top15(Scopus citedby) |
| `figures/06_doctypes.png` | 文献类型饼图 |
| `figures/07_top_concepts.png` | 概念词频 Top30(score≥0.3) |
| `figures/08_concept_wordcloud.png` | 概念词云 |
| `figures/09_concept_cooccurrence.png` | 概念共现网络(Top40,edge≥2)— **草稿/脏** |
| `exports/concept_cooccurrence.graphml` | 共现网络 GraphML(**VOSviewer/Gephi 可读**) |
| `exports/concept_cooccurrence_matrix.csv` | 共现矩阵(40×40) |
| `exports/lda_topics.csv` | gensim LDA 6 主题 × Top10 词 |

## API 连通性(本机实测 ✅)

| API | 库 | 结果 |
|---|---|---|
| OpenAlex | `pyalex` 0.21 | ✅ 现查单条记录成功 |
| Crossref | `habanero` 2.4.0 | ✅ 现查单条记录成功 |
| Scopus | `pybliometrics` 4.4.1 | ✅ 可连(STANDARD view,~/.config key);`TITLE(kinetic facade)`=107 |

→ **三个数据 API 在 Claude Code 本机都能连**(§4.3 的"连 API 抓数据/建语料"这步可在本机做)。

## 库可用性

| 库 | 状态 |
|---|---|
| pandas / numpy / scipy / matplotlib / networkx / wordcloud | ✅ 装/导入成功 |
| gensim(LDA) | ✅ 装/导入成功,已跑 6 主题 |
| pyalex / habanero / pybliometrics | ✅ |
| **BERTopic** | 未尝试硬装(依赖重:sentence-transformers/torch/hdbscan);如需再评估,本步用 gensim LDA 代替 |
| **R + bibliometrix** | ❌ 本环境**无 R / Rscript**;bibliometrix 跑不了 |

## ❗ Claude Code 做不了、必须用 GUI/桌面工具的部分

§4.3 明确"出图/聚类不连 API、吃导出文件、不手搓计量",这些**桌面端 GUI** Claude Code 跑不了,只能**导文件交接**:

- **VOSviewer**(桌面 Java App)— 关键词/概念共现聚类、密度图、叠加可视化。→ 交接:`exports/concept_cooccurrence.graphml` + 矩阵 CSV;最终建议从 OpenAlex/Scopus 导 VOSviewer 原生格式。
- **CiteSpace**(桌面 Java App)— 共被引、突现词(burst)、时间线。→ 需 Scopus/WoS 原始导出;Claude Code 可备 `referenced_works`(已在 enriched/openalex_raw)。
- **Bibliometrix / biblioshiny**(R 包)— 描述统计、三场图、主题演化。→ 本环境无 R;Claude Code 这边已用 matplotlib 出等价描述图,聚类仍建议 biblioshiny。
- **Gephi**(桌面)— 网络精修排版。→ 吃 `exports/*.graphml`。

> 即:**抓数据/建语料/描述性出图/导网络文件 = Claude Code 能做;交互式聚类/共被引/突现/精修可视化 = GUI-only,Claude Code 只负责把文件备好。**

## 这版的脏数据警告(最终聚类前必须清洗)

- **概念有消歧噪声**:Top 概念被通用词占据(`Computer science` 1051、`Engineering` 431、`Environmental science` 494),还有此前发现的 `Envelope (radar)`、`Computer graphics` 等假同源。真正主题词(Shading/Facade/Building envelope/Daylight)被压在后面。**最终计量前要建停用概念表 + 去消歧噪声**。
- **Stage-2 集仍含离题项**:高被引 Top 里仍有 PV MPPT 论文(479/381 cit)——这些在 Stage-2 摘要细筛会被剔除;**最终计量应在纳入集上重跑**。
- **LDA 仅 demo**:6 主题已能粗分(热工围护 / adaptive facade / kinetic shading / daylight-comfort),但有 `ade/ades` 等分词碎片;最终如采用需调停用词与主题数,或与共现互证(§4.3)。
