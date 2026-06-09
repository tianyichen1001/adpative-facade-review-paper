# 项目记忆 / Project Memory — Adaptive Facade Review

| 字段 | 内容 |
|---|---|
| **版本 Version** | v0.5 |
| **最后更新 Last updated** | 2026-06-09 |
| **维护者 Maintained by** | Claude (web) + 用户(用户手动同步到 Claude Code 与 project folder) |

> **⚠️ Claude Code 注意:** 本文件**只读**。每次执行任务前**先通读全文**。**不要修改本文件**;更新一律由用户手动上传。严格执行第 3 节纳排标准 + 第 1 节切入点,**不得擅自重新解释或放宽**。

---

## 0. 本文件用途
本综述项目的**唯一事实源**。Claude web、Claude Code、用户三方共享。任何一方开始任务前先读它。关键步骤后由 Claude web 提议更新,用户拍板并手动同步。

---

## 1. 项目目标 + 切入点 (Goal & Angle) — 最关键

- **目标:** 写一篇 **physically-movable facade(物理可动建筑表皮)** 的综述,投 **Journal of Building Engineering**(Elsevier)。类型 = **bibliometric 计量 + systematic 主题综述** 混合。

### 1.1 切入点(已锁定,2026-06-09)
> **可动表皮被当作"性能与控制问题"反复研究(我们语料:72% 谈性能、41% 谈控制),却很少被当作"物理作动的机械系统"对待(仅 24% 碰运动、5% 碰作动)。做机构的人(origami/SMA/气动/柔顺机构)和做性能/控制的人是两拨人、互不引用——中间是断的。这篇综述去定义、量化、并弥合这道断层。**

- 现有 4 篇综述各自坐在断层一边、没人点破:Wang 2024(控制)、Tahmasbi 2025(技术survey)、Avcı 2025(遮阳)、Özlük 2025(AI 优化)。详见 §12 对标表。

### 1.2 四点贡献
1. **正名/划界**:用严格"是否物理运动"把真·可动表皮从 adaptive/responsive 大伞里切出(分离材料变色/热工动态/被动),并量化这片标签有多杂。
2. **计量揭示断层**:计量映射领域结构 + 用交叉统计把"机制↔控制↔性能↔落地"的断层钉死(核心发现)。
3. **机制驱动分类学**:按驱动机制分类(刚性机械/柔顺机构/材料驱动[SMA·湿驱动]/气动软体/折叠-可展)——填补 4 篇都没做的维度(它们只有 adaptive/kinetic/passive、simple/complex、adaptive/non-adaptive 等粗分)。
4. **打通链条 + 议程**:沿 机构→作动→控制→性能→落地 综合,指出每环缺口,给整合议程。

> **全篇脊柱 = §4.4 抽取表生成的"机制 × 是否报性能 × 控制 × 是否落地"交叉表,不是论文逐篇堆砌。**
> **诚实前提:** 此角度成立的前提是交叉表真显示断层;72/5 信号强烈支持,但**按数据如实报告,不硬撑故事**。

---

## 2. 角色分工 (Roles)
| 角色 | 职责 |
|---|---|
| **Claude web** | 策略、检索式、质量把关、维护本 memory |
| **Claude Code** | 执行:Scopus/OpenAlex/Crossref API、Python、计量、GitHub |
| **Cowork** | 浏览器抓 abstract(见 project 内 HOWTO);环境偶发不稳(VM/Cloudflare) |
| **本 memory** | 唯一事实源;Claude web/用户维护;**Claude Code 只读** |

**GitHub:** repo `tianyichen1001/adpative-facade-review-paper`(public),分支 `claude/determined-pasteur-21Qfu`(PR #1)。

---

## 3. 研究范围与操作型纳排标准 (Scope) — 锁定

### 3.1 主题定义
建筑表皮/围护通过**物理运动/位移**适应环境或功能。运动可由机械、材料、生物方式驱动。
> **核心判据 = 是否物理可动。** 针对"可动";**不**针对视觉静态的材料态变化/热工动态。

### 3.2 纳入 / 3.3 排除(摘要)
- **纳入:** 机械可动构件(旋转/平移百叶、可开合、可折叠);SMA 驱动;气动/充气(ETFE);origami/折叠/可展;仿生真实运动;湿驱动 hygromorphic(真实形变);物理可动的 breathing skin。
- **排除:** LED/媒体立面;视觉静态变色(电致/热致);热工动态但不动(动态保温、被动呼吸墙、PCM 蓄热);与建筑表皮无关的可动结构。

### 3.4 边界(已拍板,摘要)
SMA / 气动 / origami / 平移旋转百叶 / 湿驱动真实形变 / 物理可动 breathing skin = ✅;LED / 视觉静态变色 / breathing wall·动态保温·PCM 热围护(视觉静态)= ❌。新边界 case → 记 §11,Claude web + 用户裁定。

---

## 4. 方法论 (Methodology)

### 4.1 锚定框架
PRISMA 2020(流程图)+ bibliometric 指南(Donthu 2021)/ SPAR-4-SLR;全程可复现;AI 生成的概括必须对照原摘要核对,不得幻觉。

### 4.2 PRISMA 两阶段筛选(漏斗,现状)
1. Identification:Scopus → **2831**。✅
2. Screening-1(标题 + concepts + 期刊):**2831 → 排除 713 → 进 Stage-2 2118**(含 Stage-1b)。✅
3. 仅对 2118 收摘要(§7)。✅(82%,补缺中)
4. Screening-2(摘要细筛,严格 §3.1)→ 纳入集。← **下一步**
5. Included → 计量 + 抽取 + 写作。
- 全程 PRISMA 流程图、按 DOI/eid 去重。

### 4.3 计量分析(跑「纳入集」)— 工具链已更新
- **计量主体跑纳入集;** 唯一例外:大池子的发文趋势/高产期刊等纯元数据描述统计,可做引言全景。
- **工具分工(2026-06-08 demo 验证后更新):**
  - **Claude Code 用 Python 成熟库端到端跑**(非手搓):**pyBibX**(bibliometrix 等价:EDA/引用·合作·共现网络/AI 主题建模)、**litstudy**(原生 OpenAlex)、**leidenalg + igraph**(= VOSviewer 同款 Leiden 聚类,做共词主题簇)。
  - **VOSviewer / CiteSpace / Gephi = 可选**,仅用于交互探索或精修密度/叠加图;Claude Code 导 GraphML/矩阵交接。**R/bibliometrix 本环境无,不依赖。**
  - demo 已证:OpenAlex/Crossref/Scopus 三 API 在 Claude Code 本机可连;描述图 + 共现网络 + LDA 可出。
- **共词分析用「作者关键词」(Scopus 导出,干净),不用 OpenAlex concepts**(concepts 有消歧噪声:Computer science / Envelope(radar),demo 已证脏)。concepts 仅作备份。
- **共被引/文献耦合**:用 Scopus 导出的 cited references(见 §6.1)。
- 主题图(四象限)+ 时间演化;可选 LDA/BERTopic 跑 title+abstract 互证。

### 4.4 结构化抽取表(纳入集逐篇)— 桥接表的引擎
| 列 | 取值 |
|---|---|
| ID / DOI / 年 / 期刊 | 标识 |
| **驱动机制** | 刚性机械 / 柔顺机构 / 材料驱动(SMA·湿驱动·热响应)/ 气动软体 / 折叠-可展 / 其他 |
| **运动类型** | 旋转 / 平移 / 折叠 / 充气 / 变形 / 展开 / 其他 |
| **适应目标** | 采光 / 得热 / 眩光 / 通风 / 隐私 / 美学 / 结构 / 能耗 |
| **控制方式** | 未指明 / 手动 / 规则 / 模型 / ML-AI / 传感反馈 |
| **是否报告性能** | 是/否 + 哪些指标(能耗/采光/舒适/无) |
| **研究类型** | 仿真 / 实验 / 原型 / 理论 / 案例 |
| **落地程度** | 概念 / 仅仿真 / 实验室原型 / 足尺样机 / 已建并监测 |
| **关键发现** | 一句话 |
> 这张表**直接产出 §4.6 第 5 节那张"机制 × 性能 × 控制 × 落地"交叉表**——全篇核心证据。

### 4.6 综述结构 & 篇幅(已定)
- **篇幅目标 ~13–15k 词正文**(走 Özlük ~17k / Wang ~13.6k 的精简端;**别学 Avcı 42 页逐属性硬铺**)。JBE 综述实测 14–20k 词。
- **6 节:**
  1. **引言** — conflation 划界 + 抛断层。
  2. **方法** — PRISMA 漏斗 + 计量法 + 抽取协议(对标 Özlük)。
  3. **计量全景** — 增长/期刊/国家/高产 + 共词聚类;**首次直观显示"性能/控制大陆 vs 机制小岛"**。
  4. **机制分类学** — 按驱动机制(那根脊柱)。
  5. **桥接(核心)** — 机制×性能×控制×落地交叉表,量化断层(对标 Avcí 的 review-results 交叉节,但瞄准断层)。
  6. **议程 + 结论** — 顺链指缺口 + 整合议程。
- 模板教训:Özlük = 方法模板;Avcí review-results = 第 5 节模板;Wang(类型→性能→控制割裂)= 我们要**反着用链条重组**的反面。

---

## 5. 检索策略 (Search) — 已定稿
- 数据库 **仅 Scopus**(无 WoS API,limitation 说明);按主题搜不做期刊白名单;引用以 Scopus 为准,截至 2026-06-08。
- 检索日期 2026-06-08;命中 **2831**(Article 1604 / Conf 986 / Review 133 / BookCh 108);doctype ar+re+cp+ch;English;view=STANDARD。
- 定稿检索式见 `01_search/search_log.md`(W/3 邻近 + envelope 短语块;高召回,噪声留筛选)。
- STANDARD view 无 author_names / authkeywords → OpenAlex 补(§6);**最终关键词改用 Scopus 网页导出(§6.1)**。

---

## 6. 元数据补全 (Enrichment) — ✅ 已完成
- OpenAlex 匹配 2570/2831;concepts 90.7% / 全作者 90.5% / 机构+国家 80.4% / 参考文献 79.2%;Crossref funder 24.8% / license 64.1%。
- 产物:`02_enrichment/enriched.csv`(2831×47)、`openalex_raw.jsonl`(全嵌套,**含 abstract_inverted_index** → 已用于摘要补缺)、flat CSVs、脚本、log。

### 6.1 Scopus 网页导出(关键新增)— 摘要/关键词/参考文献的来源
- **API(STANDARD)不返回摘要/关键词/参考文献;但 Scopus 网页"导出"勾字段后可导出 Abstract + Author keywords + Cited references。**
- **两处用途:**
  1. **现在:** 补 §7 那 148 个缺摘要的 DOI(导 Abstract + Author keywords)——不碰 Cloudflare、躲开 Cowork 不稳。
  2. **计量阶段:** 对最终纳入集(~150)导 **Abstract + Author keywords + References** → 喂 pyBibX/litstudy/VOSviewer。**共词用作者关键词(干净)、耦合用参考文献。**
- 操作:DOI 分批粘进 Scopus 高级检索(`DOI(x) OR DOI(y)…` 每批 ~50)→ Select all → Export CSV 勾字段。需确认订阅放开字段导出。

---

## 7. 摘要抓取 (Abstracts) — 基本完成,补缺中
- 路径:Cowork 抓(§4c 通用 JS,已修复 ScienceDirect Highlights 误抓 + STATE_BOT)+ **OpenAlex 本地重建补缺**(从 openalex_raw.jsonl 的 inverted_index)。
- **现状(stage2_with_abstracts_v2,2026-06-09):** Stage-2 2118 → 有摘要 **1738(82.1%)** = scrape 1462 + openalex 276;列含 `abstract_source`(scrape/openalex/none)记来源(透明 + limitation)。
- 按出版商:mdpi/ieee/iop/t&f/wiley/asce/nature/sage 100%、springer 99.4%、other 93.2%、elsevier 82.1%。SAGE 经 round-2 修复(round-1 失败是 Cloudflare 并发争抢,非死墙)。
- **仍缺:** 有 DOI **148**(elsevier 108 + other 39 + springer 1)→ **用 Scopus 导出补(§6.1)**;无 DOI **232** → Stage-2 标题+concepts 筛(limitation)。
- **待修(下次并表):** ① `10.15627/jd.2025.1` 抓串了 jd.2025.18 的摘要,用 Scopus 导出覆盖;② abstract_source=openalex 且 <150 字的极短重建 → 重判 missing。

---

## 8. 文件夹与 GitHub
```
adpative-facade-review-paper/  (分支 claude/determined-pasteur-21Qfu)
├── PROJECT_MEMORY.md            # 本文件(用户同步,Claude Code 不改)
├── 01_search/ 02_enrichment/    # ✅ 检索 / 补全
├── 03_screening/                # PRISMA(stage1_title_keyword.xlsx, prisma_counts.md)
├── 04_abstracts/                # abstract_extractor.js · slices/ slices_round2/ shards/
│   ├── reports/                 # stage2_with_abstracts_v2.{csv,xlsx} · coverage_report_v2.md
│   ├── scrape_inputs/ scrape_inputs_remaining/ still_missing.csv(148)
│   └── scopus_export/           # ← 即将放 Scopus 导出 CSV
├── 05_bibliometrics/            # demo:corpus_for_biblio/ figures/ exports/(GraphML)
├── 06_extraction/               # 结构化抽取表(§4.4)
└── README.md
```
规范:阶段前缀 + 语义名;每关键步一次 commit;留所有脚本/Excel;**Claude Code 不改 PROJECT_MEMORY.md**;合并按文件内容(名字可能被截 8.3)。

---

## 9. 当前进度 (Status)
- [x] 流程/方法/纳排/**切入点(B)** 锁定
- [x] 检索定稿 + Scopus 检索(2831)
- [x] OpenAlex + Crossref 补全
- [x] Stage-1 + Stage-1b(2831 → 2118)
- [x] 摘要收集(1738/2118 = 82%);**补最后 148(Scopus 导出)进行中**
- [ ] **Stage-2 摘要细筛 ← 补完即做**(严格 §3.1,产纳入集)
- [ ] 计量(纳入集,Python 工具链 + 作者关键词共词)
- [ ] 结构化抽取(§4.4)
- [ ] systematic 写作(§4.6,~13–15k 词)

---

## 10. 决策日志 (Decision Log) — 近期
| 日期 | 决策 | 说明 |
|---|---|---|
| 2026-06-08 | 检索定稿 2831;纳会议+书章;breathing wall 等热工静态筛选阶段排除 | 见 §3.4/§5 |
| 2026-06-08 | 元数据补全完成(OpenAlex 主 + Crossref 辅) | concepts/作者/国家/参考文献 |
| 2026-06-08 | Stage-1 完成 2831→2118 | 含 Stage-1b 剔 287;prisma_counts.md |
| 2026-06-08 | **计量工具链 → Python 成熟库(pyBibX/litstudy/leidenalg),VOSviewer 可选,R 不依赖;共词用作者关键词不用 OpenAlex concepts** | demo 验证 API 可连、出图可行;concepts 脏 |
| 2026-06-09 | 摘要收集 = Cowork scrape + OpenAlex 本地补缺 = 1738/2118(82%);SAGE 修复(CF 并发非死墙) | 来源记 abstract_source |
| 2026-06-09 | **综述切入点锁定 = B(机制↔性能/控制断层:量化 + 弥合)** | §1.1;前提是交叉表证实断层,否则按数据改写 |
| 2026-06-09 | **结构 = 6 节,~13–15k 词(Özlük/Wang 精简端)** | §4.6 |
| 2026-06-09 | **Scopus 网页导出 = 摘要缺口补充 + 最终纳入集关键词/参考文献来源** | §6.1;共词靠作者关键词、耦合靠参考文献 |
| 2026-06-09 | 路线选 (a):先 Scopus 补 148 → 再一次性进 Stage-2 | 保护 ScienceDirect 召回 |

---

## 11. 开放问题 (Open Questions)
- **桥接交叉表是否真显示断层**(切入点的承重假设)——按数据如实报告。
- 最终纳入集量级(Stage-2 后剩多少)。
- Scopus 订阅是否放开 abstract/keywords/references 导出(先试导一小批验证)。
- 无 DOI 232 + 仍缺 148 中 Scopus 也无的 → 标题筛,记 limitation。
- 计量是否加 LDA/BERTopic(看价值)。
- 可选独立专利全景(Lens.org)——仍 deferred。
- 新边界 case(随时补 §3.4)。

---

## 12. 对标:4 篇 JBE 综述(差异化用)
| 综述 | 范围 | 分类法 | 方法 & 规模 | 主要 gap |
|---|---|---|---|---|
| Wang 2024 | 动态表皮 + 智能控制 | 4 类:adaptive/kinetic/biomimetic/passive | PRISMA;WoS+Scopus;**97 篇** | 控制方法缺系统梳理 |
| Tahmasbi 2025 | 广:adaptive/DSF/PV/材料 | 按技术类型 | 叙述式(无明确 PRISMA/N) | 材料/多准则/制造 |
| Avcı 2025 | 遮阳(adaptive vs 非) | adaptive/non-adaptive + 参数/控制/目标 | 半系统(4 步);Scopus;**103 篇** | 整合性能目标 + AI 建模 |
| Özlük 2025 | adaptive facade 的 AI/仿真/优化 | 运动 simple/complex | **PRISMA+计量+VOSviewer**;**75 篇** | AI 优化缺整体性 |
> 我们差异化:**机制驱动分类学(白地)+ 更大更全语料(纳会议)+ 量化断层** —— 见 §1.1/§1.2。
