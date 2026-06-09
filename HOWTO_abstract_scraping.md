# Cowork 摘要抓取 SOP

> 完整 SOP(§1 概述 / §2 流程 / §3 限速与重试 / §4a ScienceDirect/Elsevier / §4b Taylor & Francis 选择器)由维护者手动同步上传。本仓库当前已留底的是 **§4c 通用裁剪 JS(定版)**,见下。

---

## §4c 通用裁剪 JS(定版,含 Cowork 修复)

- **文件:** [`04_abstracts/abstract_extractor.js`](04_abstracts/abstract_extractor.js)(原样留底,供 Cowork 注入执行)。
- **用途:** 在文章页 DOM 上跑这段 JS,按出版商选择器链取摘要正文,裁掉整页只留 `<article><p>ZABSTRACTZ … ZENDZ</p></article>`,正文随后用 `get_page_text` 取(§7 原则:JS 只返回短状态码,正文走 get_page_text)。
- **返回状态码(JS 返回值,用于分流/重试):**

  | 返回 | 含义 | 处理 |
  |---|---|---|
  | `STATE_OK` | 取到摘要,已写入页面 | 用 `get_page_text` 读 `ZABSTRACTZ … ZENDZ` 之间正文 |
  | `STATE_CF` | Cloudflare「Just a moment…」被动校验 | 等被动放行后整片重跑;**绝不解验证码** |
  | `STATE_BOT` | Bot manager / perfdrive 拦截 | 整片重跑;持续失败则跳过记 limitation |
  | `STATE_REDIR` | linkinghub/重定向中转页 | 等落地到出版商页后重跑 |
  | `STATE_NOABS` | 选择器链 + meta + 标题兜底都没取到 | 记为无摘要,Stage-2 用 标题+concepts 兜底筛 |

- **选择器链(按出版商优先级):**
  1. **ScienceDirect / Elsevier** — `div.abstract.author`;**排除** Highlights/graphical 块,**优先**标题==`Abstract` 的块(← 本版关键修复:此前会误抓 Highlights;否则取最长块)。
  2. **Springer / Nature** — `[data-test="abstract-content"]` / `#Abs1-content` / `section[data-title="Abstract"] .c-article-section__content`。
  3. **MDPI** — `.art-abstract` / `section.html-abstract` / `#html-abstract`。
  4. **Wiley** — `section.article-section__abstract .article-section__content` / `.abstract-group .article-section__content`。
  5. **Atypon(T&F / ASCE / SAGE)** — `.hlFld-Abstract` / `.abstractSection` / `.abstractInFull`。
  6. **IOP** — `.wd-jnl-art-abstract` / `div[itemprop="description"]` / `.article-text`。
  7. **IEEE** — `.abstract-text`。
  8. **meta 兜底** — `citation_abstract` / `dc.Description` / `og:description` / `description`(>140 字才采)。
  9. **标题==Abstract 兜底** — 找 `h1..h4/strong/b/dt` 文本为 `Abstract` 者,累加其后兄弟节点至下一个标题(>140 字才采)。

- **`clean()` 清洗:** 克隆节点后移除标题/小标题/关键词块/图与图注(`h1..h4`、`.section-title`、`.kwd-group`、`.c-article-section__title`、`figure`、`figcaption` 等),去掉开头 `Abstract`、结尾 `Keywords: …`,压缩空白;正文 >80 字才算有效。

- **覆盖与本仓库分组对应:** 选择器 1/5 即已留底的 §4a/§4b;2/3/4/6/7 覆盖 Stage-2 待补的 Springer/Nature、MDPI、Wiley、IOP、IEEE(见 `04_abstracts/scrape_inputs/_manifest.md` 的出版商分布);8/9 为长尾 `other` + 会议页的通用兜底。

> 维护者后续同步完整 SOP 时,本 §4c 与 `abstract_extractor.js` 应保持一致(JS 为准)。
