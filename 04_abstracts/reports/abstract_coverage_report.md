# Stage-2 摘要覆盖率 & 质量报告

Stage-2 集 = **2118**(include+uncertain)。摘要来源:Cowork slices(`04_abstracts/slices/`,164 个分片;Cowork STATUS 记 180 分片已扫,16 个分片结果未随上传到位)。

## 1. 覆盖率总览

| 指标 | 值 |
|---|---|
| Stage-2 总数 | 2118 |
| 有摘要 ok | 1439 |
| 缺摘要 missing | 679 |
| 有效 DOI 数(原 DOI + 找回) | 1886 |
| 无 DOI(无抓取路径) | 232 |
| **覆盖率(ok / 有 DOI)** | **1439/1886 = 76.3%** |
| 覆盖率(ok / 全 2118) | 1439/2118 = 67.9% |
| 合并到的唯一摘要 DOI 数 | 1432 |

## 2. 按出版商覆盖率(有 DOI)

| 出版商 | 目标(有DOI) | 抓到 | 覆盖率 |
|---|---|---|---|
| elsevier | 604 | 430 | 71.2% |
| other | 575 | 341 | 59.3% |
| mdpi | 197 | 193 | 98.0% |
| springer | 170 | 169 | 99.4% |
| taylor_francis | 91 | 90 | 98.9% |
| ieee | 87 | 84 | 96.6% |
| iop | 72 | 72 | 100.0% |
| wiley | 38 | 32 | 84.2% |
| asce | 24 | 23 | 95.8% |
| sage | 23 | 0 | 0.0% |
| nature | 5 | 5 | 100.0% |

## 3. 仍缺摘要(有 DOI)按出版商 → 可补跑

导出至 `04_abstracts/scrape_inputs_remaining/<publisher>.csv`(列同 scrape_inputs)。合计 **447** 条。

| 出版商 | 仍缺条数 |
|---|---|
| other | 234 |
| elsevier | 174 |
| sage | 23 |
| wiley | 6 |
| mdpi | 4 |
| ieee | 3 |
| asce | 1 |
| springer | 1 |
| taylor_francis | 1 |

## 4. 无 DOI 仍缺

- **232** 条无有效 DOI → Cowork 无抓取路径,留 Stage-2 用 标题+concepts 兜底筛(记为 limitation)。

## 5. 质量检查

| 检查 | 命中数 |
|---|---|
| ① 空摘要(status=ok 却空,应为 0) | 0 |
| ② 过短 <120 字符 | 0 |
| ③ 含 `•`(疑似 Highlights,重点查 elsevier) | 0 |
| ④ 含残留 `Keywords:`(MDPI 通病) | 0 |

摘要长度分布(ok=1439):min=141 / 中位=1351 / max=3636 字符。

## 6. 疑似重复摘要(同文本 → 多 DOI)

共 4 组。前 10 组:
- 组1(2 DOI):10.21273/horttech.20.2.283, 10.7148/2006-0466 — “Climate control is an important aspect of greenhouse crop management. Shading is…”
- 组2(2 DOI):10.1145/2024156.2024218, 10.1145/2070781.2024218 — “Automatically discovering high-level facade structures in unorganized 3D point c…”
- 组3(2 DOI):10.15627/jd.2025.1, 10.15627/jd.2025.18 — “In this study, to control glare in buildings with glass facades, a kinetic facad…”
- 组4(2 DOI):10.48619/ais.v6i1.1087, 10.62754/ais.v6i1.103 — “Building Energy (BE) use, representing around one-third of global energy usage, …”