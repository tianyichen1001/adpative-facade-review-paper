# Stage-2 摘要汇总 v2(round1+2 + OpenAlex 补缺)

Stage-2 = **2118**。摘要来源:Cowork scrape(round1+2)+ OpenAlex 重建(inverted_index)。

## 覆盖率
| 指标 | 值 |
|---|---|
| 唯一摘要 DOI(scrape) | 1454 |
| 有摘要 ok(总) | 1738 (82.1%) |
| └ 来自 scrape | 1462 |
| └ 来自 openalex | 276 |
| 仍缺(有 DOI) | 148 |
| 仍缺(无 DOI) | 232 |
| OpenAlex 补:本地 jsonl / 现查 | 269 / 6 |

## 按出版商真实覆盖
| 出版商 | 目标(有DOI) | ok | 覆盖率 |
|---|---|---|---|
| asce | 24 | 24 | 100.0% |
| elsevier | 604 | 496 | 82.1% |
| ieee | 87 | 87 | 100.0% |
| iop | 72 | 72 | 100.0% |
| mdpi | 197 | 197 | 100.0% |
| nature | 5 | 5 | 100.0% |
| other | 575 | 536 | 93.2% |
| sage | 23 | 23 | 100.0% |
| springer | 170 | 169 | 99.4% |
| taylor_francis | 91 | 91 | 100.0% |
| wiley | 38 | 38 | 100.0% |

## 质量抽查
| 检查 | 命中 |
|---|---|
| 过短 <120 | 1 |
| 含 • | 43 |
| 含 Keywords: | 0 |
| 重复摘要文本(>1 DOI) | 14 组 |

长度分布:min=22 / 中位=1347 / max=3802

> 含 `•` 的 43 条**全部来自 openalex**(来源拆:{'openalex': np.int64(43)})——是 OpenAlex inverted_index 里本就带项目符号的结构化摘要(真内容,非 Highlights 误抓;scrape JS 已排除 Highlights,scrape 来源 `•`=0)。

> 重复摘要 14 组(同文本→多 DOI),前 5 组:
>  - 2 条:10.23919/annsim55834.2022.9859413, 10.23919/annsim55834.2022.9859413 — “Adaptive Façades (AFs) have proven to be effective as a building envel…”
>  - 2 条:10.1145/2070781.2024218, 10.1145/2024156.2024218 — “Automatically discovering high-level facade structures in unorganized …”
>  - 2 条:10.1016/j.proeng.2016.08.031, 10.1016/j.proeng.2016.08.031 — “Barahat Al Nouq is the central square of the heart of Doha, capital of…”
>  - 2 条:10.62754/ais.v6i1.103, 10.48619/ais.v6i1.1087 — “Building Energy (BE) use, representing around one-third of global ener…”
>  - 2 条:10.4324/9781315763279, 10.4324/9781315763279 — “Buildings are increasingly 'dynamic': equipped with sensors, actuators…”

## 仍缺(可补) — `still_missing.csv`

最终仍缺**有 DOI 148** 条(elsevier 居多:ScienceDirect Cloudflare 限速 + 2026 新文 OpenAlex 尚无摘要)+ **无 DOI 232** 条(无抓取路径,留 Stage-2 标题筛)。