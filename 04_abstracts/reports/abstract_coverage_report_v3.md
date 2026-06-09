# Stage-2 摘要汇总 v3(并入 Scopus 导出)

Stage-2 = **2118**。来源:Cowork scrape + OpenAlex 重建 + **Scopus 网页导出**(§6.1)。

## 本轮修复 / 并入
| 操作 | 数 |
|---|---|
| Scopus 补缺(missing→scopus) | 141 |
| Scopus 替换 OpenAlex(更干净) | 0 |
| 极短 OpenAlex(<150)重判 missing | 4 |
| jd.2025.1 处理 | 1(结果:source=none, len=0) |

## 覆盖率
| 指标 | 值 |
|---|---|
| 有摘要 ok | 1874 (88.5%) |
| └ scrape | 1461 |
| └ scopus | 141 |
| └ openalex | 272 |
| 仍缺(有 DOI) | 12 |
| 仍缺(无 DOI) | 232 |
| **author_keywords 覆盖(Scopus)** | 126 (5.9%) |

## 按出版商真实覆盖
| 出版商 | 目标(有DOI) | ok | 覆盖率 |
|---|---|---|---|
| asce | 24 | 24 | 100.0% |
| elsevier | 604 | 603 | 99.8% |
| ieee | 87 | 87 | 100.0% |
| iop | 72 | 72 | 100.0% |
| mdpi | 197 | 197 | 100.0% |
| nature | 5 | 5 | 100.0% |
| other | 575 | 564 | 98.1% |
| sage | 23 | 23 | 100.0% |
| springer | 170 | 170 | 100.0% |
| taylor_francis | 91 | 91 | 100.0% |
| wiley | 38 | 38 | 100.0% |

## jd.2025.1 修复确认

- `10.15627/jd.2025.1`:source=none, len=0(Scopus 无此 DOI → 置空 missing,已移除错误的 jd.2025.18 串摘要)。

## 质量
- 过短 <120:3;含 `•`:43(openalex 结构化摘要,真内容)。

## 仍缺 — `still_missing.csv`
- 有 DOI **12** + 无 DOI **232**。