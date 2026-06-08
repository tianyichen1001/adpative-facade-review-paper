# 项目记忆 / Project Memory — Adaptive Facade Review

| 字段 | 内容 |
|---|---|
| **版本 Version** | v0.3 |
| **最后更新 Last updated** | 2026-06-08 |
| **维护者 Maintained by** | Claude (web) + 用户(用户手动同步到 Claude Code 与 project folder) |

> **⚠️ Claude Code 注意:** 本文件**只读**。每次执行任务前**先通读全文**。**不要修改本文件**;更新一律由用户手动上传。严格执行第 3 节的纳入/排除标准,**不得擅自重新解释或放宽范围**。

---

## 0. 本文件用途

这是本综述项目的**唯一事实源(single source of truth)**。Claude web、Claude Code、用户三方共享同一份。任何一方开始任务前先读它,避免跑偏。关键步骤后由 Claude web 提议更新,用户拍板并手动同步。

---

## 1. 项目目标 (Goal)

- 写一篇 **adaptive facade(可动建筑表皮)** 主题的综述,投 **Journal of Building Engineering**(Elsevier)。
- 综述类型:**混合式 = bibliometric 计量 + systematic 主题综述**。
- 贡献定位:可动建筑表皮的**分类学(taxonomy)** + 主题综合 + 研究缺口与未来议程。

---

## 2. 角色分工 (Roles)

| 角色 | 职责 |
|---|---|
| **Claude web** | 策略、检索式设计、质量把关、维护本 memory |
| **Claude Code** | 执行层:Scopus API(pybliometrics)、OpenAlex/Crossref 补全、Python、Excel、GitHub 留痕 |
| **Cowork** | 按 DOI 抓 abstract(见 project 内 HOWTO SOP) |
| **本 memory md** | 唯一事实源;Claude web/用户维护;**Claude Code 只读** |

**协作回路:** Claude Code 用 Scopus 出列表 → 用户回传给 Claude web → Claude web 出 **OpenAlex(主)+ Crossref(辅)** 补全 prompt → Claude Code 补全回传 → **Claude web 做质量把关(是否是我们要的文章)** → 必要时补充检索 → 进入下一阶段。

**GitHub 现状:** repo = `tianyichen1001/adpative-facade-review-paper`(public);当前在分支 `claude/determined-pasteur-21Qfu`(PR #1)上推进。

---

## 3. 研究范围与操作型纳排标准 (Scope & Operational Criteria) — 最关键

### 3.1 主题定义
建筑表皮 / 围护(envelope, facade, building skin)通过**物理运动 / 位移**来适应环境或功能需求。运动可由**机械、材料、或生物**方式驱动。
> **核心判据 = 是否发生"物理可动"。** 针对"可动";**不**针对"视觉上静态的材料态变化 / 热工动态"。

### 3.2 纳入 (INCLUDE)
- 机械驱动的可动构件(旋转 / 平移百叶、可开合单元、可折叠遮阳等)
- **形状记忆合金(SMA)** 驱动的运动
- **气动 / 充气**结构(ETFE 气枕等)
- **Origami / 折叠 / 可展(deployable)** 结构
- 仿生 / 生物启发的**真实运动机构**(含湿驱动 hygromorphic 的真实形变)
- 关键词层面:kinetic / movable / adaptive / dynamic / responsive / deployable / shape-changing / morphing + facade / envelope / skin …

### 3.3 排除 (EXCLUDE)
- **LED / 媒体立面**(只变光或影像,无物理运动)
- **纯材料态变化且视觉静态**(电致变色、热致变色、不产生位移的 PCM 等)
- **热工动态但不动的围护**(动态保温 dynamic insulation、被动呼吸/多孔墙 breathing/porous wall、PCM 蓄热围护等——视觉静态、无位移)
- 与建筑表皮无关的可动结构(一般机器人、可变形材料但非建筑表皮)

### 3.4 边界决策(已拍板)

| Case | 判定 | 理由 |
|---|---|---|
| SMA 驱动 | ✅ 纳入 | 材料驱动但**产生位移** |
| 气动 / ETFE | ✅ 纳入 | 物理运动 |
| Origami / 折叠 | ✅ 纳入 | 物理运动 |
| 平移 / 旋转百叶 | ✅ 纳入 | 物理运动 |
| 湿驱动 hygromorphic(真实形变) | ✅ 纳入 | 材料驱动但**产生形变/位移** |
| 物理可动的 breathing skin(如气动) | ✅ 纳入 | 有位移 |
| LED / 媒体立面 | ❌ 排除 | 无物理运动 |
| 电致 / 热致变色(视觉静态) | ❌ 排除 | 无位移 |
| **breathing wall / 动态保温 / PCM 热围护(视觉静态)** | ❌ 排除 | **热工动态但无位移,不满足 §3.1;在筛选阶段剔除** |

> 定稿检索为**高召回**,故 corpus 内含此类"热动/被动呼吸"围护与少量跨域噪声(如软件 "user interface façade"、动物运输),**均在 PRISMA 筛选阶段按 §3.1 剔除**。
> 遇到新的边界 case → 先记入第 11 节「开放问题」,由 **Claude web + 用户**裁定后再补进本表。Claude Code 不自行判定边界。

---

## 4. 方法论 (Methodology)

### 4.1 锚定框架(为过审)
- **筛选与报告:PRISMA 2020**(出 PRISMA 流程图)。
- **计量:** bibliometric 指南(如 Donthu et al. 2021)/ 可选 SPAR-4-SLR 协议。
- **全程可复现:** 记录检索式、数据库、检索日期、纳排标准 → 作为 supplementary。
- **AI 使用声明 + 人工核验:** AI 生成的每条概括必须**对照原摘要核对**,不得幻觉。

### 4.2 PRISMA 两阶段筛选(漏斗)
1. **Identification:** Scopus 主题检索 → 大池子(**仅元数据,无摘要**)。✅ 已完成(N=2831)。
2. **Screening-1(粗筛,便宜):** 按 标题 + 关键词(用 OpenAlex concepts 补)+ 期刊 → "可能相关"集。
3. **仅对"可能相关"集用 Cowork 抓摘要。**
4. **Screening-2(细筛):** 按摘要对照纳排 → 纳入集。
5. **Included:** 纳入集进入计量 + 深读。
- 全程画 **PRISMA 流程图**,记录各级数量。
- 全程**按 DOI / eid 去重**。

### 4.3 计量分析(跑在「纳入集」上)
- **计量主体跑在「纳入集」,不是大池子。**(因为聚类要直接对应 review 章节;且省 Cowork 成本。)
- **唯一例外:** 大池子的「发文量逐年趋势」「高产期刊」等**只用元数据、不碰摘要**的描述统计,可放引言做"领域全景"铺垫。
- **方法骨架:**
  - 描述性(performance):年度产出、高产期刊 / 作者 / 机构 / 国家、高被引。
  - **关键词共现(co-word):** 用 OpenAlex concepts/topics(Scopus 无关键词)→ **聚类结果直接定义 systematic review 的章节结构**。
  - 主题图(thematic map,四象限 motor/niche/emerging/basic)+ 时间演化。
  - 可选:**LDA / BERTopic** 跑 标题+摘要,与共现互证(看时间与价值再定)。
- **工具分工:**
  - 抓数据、建语料(**连 API**):`pybliometrics`(Scopus)、`pyalex`(OpenAlex)、`habanero`(Crossref)。
  - 出图 / 聚类(**不连 API,吃导出文件**):**VOSviewer / Bibliometrix-R / CiteSpace**。**不手搓计量。**
  - 可选 LDA / BERTopic(**不连 API,跑本地标题+摘要**):`gensim` / `bertopic`。

### 4.4 结构化抽取表(纳入集逐篇)
| 列 | 说明 |
|---|---|
| ID / DOI / 第一作者 / 年份 / 期刊 | 标识 |
| 驱动方式 | 机械 / 材料 / 生物 |
| 运动类型 | 旋转 / 平移 / 折叠 / 膨胀 / 其他 |
| 尺度 | 构件 / 单元 / 整面 |
| 适应目标 | 采光 / 得热 / 通风 / 隐私 / 美学 / 结构 / 其他 |
| 性能指标 | 文中报告的量化指标 |
| 研究类型 | 实验 / 模拟 / 原型 / 理论 |
| **关键发现** | = 一句话概括 |
> 这张表**同时支撑聚类与写作**;比纯一句话概括强。

### 4.5 systematic 写作
- 章节结构 = 计量聚类得到的主题。
- 每个主题内做**跨文献综合、对比、缺口**,而非流水账。
- 收尾:研究缺口 + 未来议程 + 分类学。

---

## 5. 检索策略 (Search Strategy) — 已定稿 FINAL

- **数据库:仅 Scopus**(无 WoS API)→ 在 limitation 里说明 Scopus 工程覆盖足够广。
- **按主题搜,不做"期刊白名单"** → Nature / Nature Communications / Science / PNAS 等顶刊由主题命中。
- **引用数:** 统一用 Scopus,注明"截至 2026-06-08"(引用数随时间变)。
- **检索日期:** 2026-06-08
- **命中数:** **2831**(Article 1604 / Conference Paper 986 / Review 133 / Book Chapter 108)
- **文献类型:** ar + re + cp + ch
- **所用 View:** STANDARD(COMPLETE 确认 401,非订阅 key 无权限)
- **灵敏度测试:** 已做。并入验证安全的同义词(`adaptable` / `convertible` / `hygromorphic` + `"building envelope"` + `breathing skin/facade/wall`),净增 279;**拒绝**跨域噪声词(deployable/transformable structure、shape-changing architecture、retractable roof 等)。
- **字段覆盖:** DOI 86.3% | 首作者机构/国家 ~98.2% | **author_names / author_keywords = 0%(STANDARD view 限制)→ 由 OpenAlex 补全(§6)**。

### 5.1 定稿检索式(原样执行)
```
( TITLE-ABS-KEY( ( adaptive OR adaptable OR kinetic OR dynamic OR responsive OR movable OR moveable OR convertible OR deployable OR transformable OR reconfigurable OR morphing OR "shape changing" OR "shape-changing" OR retractable OR foldable OR folding OR origami OR kirigami OR pneumatic OR inflatable OR "shape memory" OR hygromorphic OR biomimetic OR "bio-inspired" OR "bio inspired" OR actuated OR bistable ) W/3 ( facade OR facades OR "building envelope" OR "building envelopes" OR "building skin" OR "building skins" OR "second skin" OR "double skin facade" OR shading OR louver OR louvers OR louvre OR louvres OR "brise soleil" OR "brise-soleil" OR fenestration OR "solar screen" OR "sun screen" ) ) OR TITLE-ABS-KEY( "kinetic envelope" OR "adaptive envelope" OR "dynamic envelope" OR "responsive envelope" OR "deployable envelope" OR "movable envelope" OR "kinetic architecture" OR "adaptive building envelope" OR "responsive building envelope" OR "breathing skin" OR "breathing facade" OR "breathing wall" ) ) AND ( DOCTYPE(ar) OR DOCTYPE(re) OR DOCTYPE(cp) OR DOCTYPE(ch) ) AND LANGUAGE(english)
```

---

## 6. 元数据补全 (Metadata Enrichment) — 下一步(进行中)

> 用途:补 Scopus 元数据的缺口(尤其**全作者列表 / 规范化机构 / 国家 / 引用关系 / 参考文献 / 资助方**)。**只补元数据,不取摘要。**

- **主:OpenAlex**(Python `pyalex`)— **全部作者** + 各作者**机构 + ROR + 国家**、concepts/topics 分类(**替代 Scopus 缺失的关键词**)、referenced_works(参考文献)、cited_by_count、逐年被引、OA 状态。补 Scopus STANDARD view 最常缺的"全作者 / 规范化机构 / 国家 / 引用关系"。
- **辅:Crossref**(Python `habanero`)— 期刊 / 卷期页 / ISSN / 类型 / 出版日期、参考文献列表、**资助方(funder)**、license。作权威书目核对的第二来源。**弱项:作者单位常缺。**
- **匹配:** 按 **DOI** 匹配为主(86%);无 DOI 的 ~14%(多为会议/书章)用 **标题 + 年份**尽力匹配,低置信度留空标记。
- **引用数仍以 Scopus 为准**(§5);OpenAlex / Crossref 的被引数仅作补全 / 交叉校验。
- **摘要不走 API:** Crossref 无 Elsevier 摘要、OpenAlex 新文常 null(均已验证)→ 摘要一律走 Cowork(§7)。
- **DataCite 不用**(只收数据集 / DOI 注册,期刊文章不在)。
- **运行环境:补全在 Claude Code 本机跑**(免费、无需 key、加 mailto 进礼貌池)。Claude web 沙盒出网受限(实测 403),不在沙盒实测。
- **Python 库已验证可装 / 可导入:** `pybliometrics` 4.4.1、`pyalex` 0.21、`habanero` 2.4.0。

---

## 7. 摘要抓取 (Abstract Retrieval)

- **一律用 Cowork。** Scopus API 在本账号权限下**不返回摘要(已多次验证)→ 不再尝试用任何 API 取摘要。**
- 依据:project 内 `HOWTO_批量抓取文献摘要` SOP。
- **现有选择器:** ScienceDirect / Elsevier(SOP §4a)、Taylor & Francis(SOP §4b)。
- **待补选择器:** Nature / Springer、Wiley、MDPI、ASCE、Frontiers 等 — 看**纳入集实际出版商分布**后逐个补(nature.com 等 DOM 与 ScienceDirect 不同)。
- **原则:** JS 只返回短状态码,正文用 `get_page_text` 取;Cloudflare 被动校验等自动放行,**绝不解验证码**;worker **~10–11 篇/片**并行,超时整片重跑。

---

## 8. 文件夹与 GitHub 规范 (Repo & Naming)

```
adpative-facade-review-paper/        # repo 根(分支 claude/determined-pasteur-21Qfu)
├── PROJECT_MEMORY.md            # 本文件(用户手动同步,Claude Code 不改)
├── HOWTO_abstract_scraping.md   # Cowork SOP
├── 01_search/                   # Scopus 检索 ✅
│   ├── scripts/                 # scopus_search.py(定稿)/ recall_test.py
│   ├── raw/                     # scopus_raw.csv / .xlsx(2831 定稿)
│   └── search_log.md            # 检索式 / 日期 / 命中数 / 灵敏度测试
├── 02_enrichment/               # OpenAlex + Crossref 补全(进行中)
│   ├── scripts/                 # pyalex / habanero 脚本
│   └── enriched.xlsx
├── 03_screening/                # PRISMA 两阶段
│   ├── stage1_title_keyword.xlsx
│   ├── stage2_abstract.xlsx
│   └── prisma_counts.md
├── 04_abstracts/                # Cowork 产物 (slice_*.json)
├── 05_bibliometrics/            # 计量 (corpus_for_biblio/ + outputs/)
├── 06_extraction/               # 结构化抽取表
└── README.md
```

- 命名:**阶段前缀 + 语义名**(必要时加日期)。
- **每个关键步骤一次 commit**,commit message 写清做了什么。
- **保留所有 Python 脚本与 Excel 痕迹**(可审计、可重跑)。
- **Claude Code 不修改 `PROJECT_MEMORY.md`。**

---

## 9. 当前进度 (Status)

- [x] 流程与方法对齐
- [x] 操作型纳排标准拍板
- [x] 补全方案定稿(OpenAlex 主 + Crossref 辅)、Python 数据获取库验证
- [x] **检索式定稿 + Scopus 检索(N=2831,已锁定)**
- [ ] **OpenAlex + Crossref 补全 ← 下一步(进行中)**
- [ ] Stage-1 粗筛(标题 + concepts + 期刊)
- [ ] Cowork 抓摘要
- [ ] Stage-2 细筛 + PRISMA 流程图
- [ ] 计量分析(纳入集)
- [ ] 结构化抽取
- [ ] systematic 写作

---

## 10. 决策日志 (Decision Log)

| 日期 | 决策 | 说明 |
|---|---|---|
| 2026-06-07 | 综述类型 = bibliometric + systematic 混合 | 聚类定主题,主题写综述 |
| 2026-06-07 | 计量跑「纳入集」,非大池子 | 聚类要对应 review 章节;省 Cowork 成本 |
| 2026-06-07 | 摘要一律 Cowork | Scopus 权限无摘要(已验证) |
| 2026-06-07 | 仅 Scopus,无 WoS | 无 WoS API;limitation 说明 |
| 2026-06-07 | 按主题搜,不做期刊白名单 | 确保 Nature 系列等顶刊不漏 |
| 2026-06-07 | 纳排:SMA / 气动 / origami / 平移百叶 纳入;LED / 视觉静态变色 排除 | 见 §3.4 |
| 2026-06-07 | 采用 PRISMA 两阶段筛选 | 粗筛省摘要成本 |
| 2026-06-07 | 用结构化抽取表替代纯一句话 | 见 §4.4 |
| 2026-06-07 | 元数据补全 = OpenAlex(主)+ Crossref(辅) | OpenAlex 补机构/国家/引用,Crossref 补书目/参考文献/资助方 |
| 2026-06-07 | Python 数据获取库 = pybliometrics / pyalex / habanero | 沙盒已验证可装可导入;实连在 Claude Code |
| 2026-06-08 | **检索式定稿,命中 2831** | 并入灵敏度验证的安全同义词(adaptable/convertible/hygromorphic + "building envelope" + breathing 短语),净增 279;**拒绝** deployable/transformable structure 等跨域噪声词 |
| 2026-06-08 | 纳入会议论文 + 书章(cp 35% / ch 4%) | 该领域大量成果发在建筑/工程会议(eCAADe 等) |
| 2026-06-08 | breathing wall / 动态保温 / PCM 热围护(视觉静态)边界 → 筛选阶段按 §3.1 排除 | 物理可动的 breathing skin 仍纳入;见 §3.3 / §3.4 |
| 2026-06-08 | Scopus STANDARD view 确认无 author_names / authkeywords | 由 OpenAlex 补全(§6),不追 COMPLETE |

---

## 11. 开放问题 (Open Questions)

- 预估纳入集目标量级(2831 经两阶段筛选后大致剩多少)。
- 计量是否加 LDA/BERTopic(看时间与价值)。
- 无 DOI 的 ~14% 记录(会议/书章)OpenAlex 匹配率,看补全后决定是否单独处理。
- 新出现的边界 case(随时补到 §3.4)。
