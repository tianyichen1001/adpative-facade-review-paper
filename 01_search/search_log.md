# Search Log

> **定稿状态 FINAL**:下表为并入灵敏度测试(见文末「灵敏度测试」)结论后的**定稿检索式**与**定稿 corpus**。相对 2552 版,新增已验证安全同义词:修饰词加 `adaptable / convertible / hygromorphic`,目标词加 `"building envelope(s)"`,短语加 `breathing skin/facade/wall`;**未**加入跨域噪声词(deployable structure / transformable architecture 等)。

| 字段 | 值 |
|---|---|
| 数据库 Database | Scopus(仅) |
| 检索式 Query | 见下方代码块(**定稿**,含 cp + ch) |
| 检索日期 Date | 2026-06-08 |
| 命中数 Hits | **2831** |
| 较前一版净新增 Net-new vs 2552 | **+279** |
| 文献类型 DOCTYPE | ar + re + cp + ch(article / review / conference paper / book chapter) |
| 所用 View | STANDARD(COMPLETE 已确认 401,非订阅 key 无权限;count=25,start 分页) |
| 备注 Notes | 按主题搜,不做期刊白名单。仍含部分跨域噪声(PV "partial shading"/MPPT、CT 体渲染、河流/渔业/动物运输等),待 Claude web QC 在筛选阶段剔除。 |

## DOCTYPE 分布(N = 2831)

| 类型 Type | 数量 N | 占比 |
|---|---|---|
| Article | 1604 | 56.7% |
| Conference Paper | 986 | 34.8% |
| Review | 133 | 4.7% |
| Book Chapter | 108 | 3.8% |

## 净新增核查 Net-new vs previous corpus(+279)

- 净新增 **279** 条(最终 2831 − 旧 2552;按 eid 去重)。
- on-topic 标题启发式:154/279(全体)、16/25(净新增 Top-25)。
- 人工粗判:净新增 Top-25 **以建筑围护为主**——dynamic insulation of building envelopes、breathing wall/panel、porous breathing walls、adaptive dynamic building envelope + PCM、dynamic characteristics of building envelope 等;证实新增主要来自 `adaptable/convertible/breathing/hygromorphic` + `"building envelope"`,**而非**灵敏度测试中被否的航天/超材料噪声。
- 少量噪声(如动物运输、新生儿监护)留待筛选阶段剔除。
- ⚠️ §3 范围提示:`breathing wall` 类多为**被动扩散通风/多孔围护**(视觉静态、未必"物理可动"),是否纳入由 Claude web 按 §3.1「物理可动」核心判据裁定。

## 检索式 Query(定稿,原样执行)

```
( TITLE-ABS-KEY( ( adaptive OR adaptable OR kinetic OR dynamic OR responsive OR movable OR moveable OR convertible OR deployable OR transformable OR reconfigurable OR morphing OR "shape changing" OR "shape-changing" OR retractable OR foldable OR folding OR origami OR kirigami OR pneumatic OR inflatable OR "shape memory" OR hygromorphic OR biomimetic OR "bio-inspired" OR "bio inspired" OR actuated OR bistable ) W/3 ( facade OR facades OR "building envelope" OR "building envelopes" OR "building skin" OR "building skins" OR "second skin" OR "double skin facade" OR shading OR louver OR louvers OR louvre OR louvres OR "brise soleil" OR "brise-soleil" OR fenestration OR "solar screen" OR "sun screen" ) ) OR TITLE-ABS-KEY( "kinetic envelope" OR "adaptive envelope" OR "dynamic envelope" OR "responsive envelope" OR "deployable envelope" OR "movable envelope" OR "kinetic architecture" OR "adaptive building envelope" OR "responsive building envelope" OR "breathing skin" OR "breathing facade" OR "breathing wall" ) ) AND ( DOCTYPE(ar) OR DOCTYPE(re) OR DOCTYPE(cp) OR DOCTYPE(ch) ) AND LANGUAGE(english)
```

## 字段覆盖率 Field coverage(N = 2831)

| 字段 Field | 覆盖 Coverage |
|---|---|
| doi | 86.3%(2443/2831)— 会议论文/书章常缺 DOI |
| first_author (creator) | 99.9%(2829/2831) |
| author_names | **0.0%(0/2831)** — STANDARD view 不返回作者列表 |
| author_keywords | **0.0%(0/2831)** — STANDARD view 不返回作者关键词 |
| affilname | 98.3%(2783/2831) |
| affiliation_country | 98.2%(2781/2831) |

> ⚠️ **作者列表 / 作者关键词缺失**:非订阅 key 的 STANDARD view 不含 `author_names` / `authkeywords`。这会影响 §4.3 关键词共现(co-word)与作者合作分析。补救:(a) 用订阅 key / 机构网络重取 COMPLETE view;(b) 在 §6 补全阶段用 OpenAlex 的 concepts/topics + authorships 替代。待 Claude web 决策。
>
> 检索式定稿后回填,并与 PROJECT_MEMORY.md §5 保持一致。

---

## 灵敏度测试 Recall Sensitivity Test(2026-06-08)

目的:检查主检索式是否漏掉相关文献。跑一个**候选补充词 + 建筑域约束**的测试检索式,与已提交 corpus(`scopus_raw.csv`,eid 比对)做去重,看测试集中**有多少不在现有 corpus 的新条目**。脚本:`01_search/scripts/recall_test.py`。**未合并进主 corpus。**

| 字段 | 值 |
|---|---|
| 测试命中 Test hits | 650 |
| 现有 corpus eid 数 | 2552 |
| **新条目 New(不在 corpus)** | **569** |
| on-topic 启发式(标题含 facade/envelope/skin/kinetic/… token) | 328/569 ≈ 58%(**高估,见下**) |

### 测试检索式(原样执行)

```
( TITLE-ABS-KEY( "breathing skin" OR "breathing facade" OR "breathing wall" OR "adaptable facade" OR "adaptable building envelope" OR "convertible facade" OR "retractable roof" OR "soft robotic facade" OR "robotic facade" OR "hygromorphic facade" OR "hygromorphic skin" OR "transformable architecture" OR "transformable structure" OR "deployable structure" OR "shape-changing architecture" OR "responsive building skin" OR "adaptive solar facade" OR "kinetic shading system" ) AND TITLE-ABS-KEY( building OR architectur* OR facade OR envelope OR "built environment" ) ) AND ( DOCTYPE(ar) OR DOCTYPE(re) OR DOCTYPE(cp) OR DOCTYPE(ch) ) AND LANGUAGE(english)
```

### 判读(待 Claude web / 用户裁定是否并入主检索式)

- **on-topic 启发式 58% 系高估**:新条目 Top-30 多为**航天可展结构 / 超材料 / 4D 打印 / 形状记忆聚合物 / origami 人工肌肉 / 神经网络 architecture search**(PNAS、Nature、Nature Comm.、NeurIPS、Ceas Space Journal 等),并非建筑表皮。原因:约束词 `architectur*` 会命中 metamaterial / computing 语境的 "architecture",`deployable / transformable / shape-changing / structure` 这类词在航天与材料领域高频。
- **真正像"漏网"的建筑表皮新条目较少**,例:*Framework for assessing the performance potential of seasonally adaptable facades*(Energy and Buildings, 2014, 102 cit)。
- **初步建议**:`"adaptable facade" / "adaptable building envelope" / "convertible facade" / "breathing skin/facade/wall" / "hygromorphic facade/skin" / "adaptive solar facade" / "kinetic shading system" / "responsive building skin"` 这类**已带 facade/skin/envelope 限定的短语**更可能净增益;而 `"deployable structure" / "transformable structure" / "transformable architecture" / "shape-changing architecture" / "retractable roof"` 引入大量跨域噪声,**不建议直接并入**或需更强建筑域约束(如 W/n 接 facade/envelope)。
- 最终是否并入、并入哪些词,由 **Claude web + 用户**裁定(PROJECT_MEMORY.md §2 协作回路 / §3.4 边界裁定)。
