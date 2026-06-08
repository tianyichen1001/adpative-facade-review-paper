# Search Log

| 字段 | 值 |
|---|---|
| 数据库 Database | Scopus(仅) |
| 检索式 Query | 见下方代码块(已执行) |
| 检索日期 Date | 2026-06-08 |
| 命中数 Hits | 1565 |
| 所用 View | STANDARD(COMPLETE 返回 401,非订阅 key 无权限 → 回退 STANDARD,count=25,start 分页) |
| 备注 Notes | 按主题搜,不做期刊白名单。结果为 **provisional,待 Claude web QC**;抽样可见 PV "partial shading"/MPPT、CT 体渲染、河流/渔业 shading 实验等离题噪声。 |

## 检索式 Query(原样执行)

```
( TITLE-ABS-KEY( ( adaptive OR kinetic OR dynamic OR responsive OR movable OR moveable OR deployable OR transformable OR reconfigurable OR morphing OR "shape changing" OR "shape-changing" OR retractable OR foldable OR folding OR origami OR kirigami OR pneumatic OR inflatable OR "shape memory" OR biomimetic OR "bio-inspired" OR "bio inspired" OR actuated OR bistable ) W/3 ( facade OR facades OR "building skin" OR "building skins" OR "second skin" OR "double skin facade" OR shading OR louver OR louvers OR louvre OR louvres OR "brise soleil" OR "brise-soleil" OR fenestration OR "solar screen" OR "sun screen" ) ) OR TITLE-ABS-KEY( "kinetic envelope" OR "adaptive envelope" OR "dynamic envelope" OR "responsive envelope" OR "deployable envelope" OR "movable envelope" OR "kinetic architecture" OR "adaptive building envelope" OR "responsive building envelope" ) ) AND ( DOCTYPE(ar) OR DOCTYPE(re) ) AND LANGUAGE(english)
```

## 字段覆盖率 Field coverage(N = 1565)

| 字段 Field | 覆盖 Coverage |
|---|---|
| doi | 96.5%(1510/1565) |
| author_keywords | **0.0%(0/1565)** — STANDARD view 不返回作者关键词 |
| affilname | 98.6%(1543/1565) |
| affiliation_country | 98.6%(1543/1565) |

> ⚠️ **作者关键词缺失**:非订阅 key 的 STANDARD view 不含 `authkeywords`。这会影响 §4.3 关键词共现(co-word)分析。可能的补救:(a) 用订阅 key / 机构网络重取 COMPLETE view;(b) 在 §6 补全阶段用 OpenAlex 的 concepts/keywords 替代。待 Claude web 决策。
>
> 检索式定稿后回填,并与 PROJECT_MEMORY.md §5 保持一致。
