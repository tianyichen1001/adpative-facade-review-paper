# Adaptive Facade Review (Bibliometric + Systematic)

可动建筑表皮(adaptive / kinetic / dynamic facade)混合式综述项目:bibliometric 计量 + systematic 主题综述,拟投 Journal of Building Engineering。

**Source of truth: `PROJECT_MEMORY.md`** — 不在本仓库编辑它,由维护者手动同步。

## Pipeline
Scopus 检索 → OpenAlex(主)+ Crossref(辅) 补全 → PRISMA 两阶段筛选 → Cowork 抓摘要 → 计量(VOSviewer / Bibliometrix) → 结构化抽取 → 写作。

## Structure
- `01_search/` — Scopus 检索:`scripts/`(pybliometrics)、`raw/` 原始导出、`search_log.md`
- `02_enrichment/` — OpenAlex + Crossref 补全:`scripts/`(pyalex / habanero)、`enriched.xlsx`
- `03_screening/` — PRISMA 两阶段:`stage1_title_keyword.xlsx`、`stage2_abstract.xlsx`、`prisma_counts.md`
- `04_abstracts/` — Cowork 产物:`slice_*.json`
- `05_bibliometrics/` — 计量:`corpus_for_biblio/` 导出、`outputs/` 图与聚类
- `06_extraction/` — 结构化抽取表:`extraction_table.xlsx`

## Conventions
- 阶段前缀 + 语义名;每个关键步骤一次 commit。
- 保留所有 Python 脚本与 Excel 痕迹(可审计、可重跑)。
- **绝不提交 API key**(Scopus 等);见 `.gitignore`。
