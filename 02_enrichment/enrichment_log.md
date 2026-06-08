# Enrichment Log — OpenAlex (primary) + Crossref (secondary)

输入 corpus:`01_search/raw/scopus_raw.csv`(N = 2831);补全 API 免费无 key,礼貌池 mailto = `tianyi.chen1001@gmail.com`(仅请求头标识,不入库为密钥)。

## OpenAlex 覆盖率(主补全)

| 指标 | 值 |
|---|---|
| 按 DOI 匹配 | 2416 |
| 按标题匹配(sim ≥ 0.9) | 154 |
| 未匹配(none/low) | 261 |
| 有 concepts(关键词等价物) | 2568/2831 = 90.7% |
| 有全部作者 | 2562/2831 = 90.5% |
| 有机构 + 国家 | 2275/2831 = 80.4% |
| 有 referenced_works(参考文献) | 2241/2831 = 79.2% |

## Crossref 覆盖率(辅,仅 DOI'd)

| 指标 | 值 |
|---|---|
| 按 DOI 解析成功 | 2395 |
| 有 funder(资助方) | 701/2831 = 24.8% |
| 有 license | 1815/2831 = 64.1% |
| 有 reference-count | 2395/2831 = 84.6% |

## 对比:补全前后(对照 Scopus STANDARD view)

| 字段 | Scopus 原始 | 补全后 |
|---|---|---|
| 关键词等价物(concepts) | 0.0%(authkeywords 全空) | 2568/2831 = 90.7%(OpenAlex concepts) |
| 全部作者 | 0.0%(仅 first_author/creator) | 2562/2831 = 90.5%(OpenAlex authorships) |
| 国家 | 仅 affiliation_country(首作者域) | 2275/2831 = 80.4%(全机构 + 国家) |

## 5 条补全前后对照样例

### 2-s2.0-105038431270 — Comparing daylight performance of dynamic and static shadings in office façades across mul
- **Scopus 原始**:first_author=`Ziaee N.` | author_names=`nan`(空) | authkeywords=`nan`(空) | affiliation_country=`Iran`
- **OpenAlex 全作者**:Navid Ziaee; Mehdi Ghiai
- **OpenAlex 机构**:Isfahan University of Art; Texas Tech University
- **OpenAlex 国家**:IR; US
- **OpenAlex concepts**:Daylight:0.876; Shading:0.721; Sky:0.658; Environmental science:0.646; Illuminance:0.608; Noon:0.567; Meteorology:0.531; Sunlight:0.407
- **Crossref funder**: | license_types=`tdm; vor` | ref-count=40.0

### 2-s2.0-105035804991 — Integrating dynamic façade design into architectural education and practice through Mashra
- **Scopus 原始**:first_author=`Fardous I.` | author_names=`nan`(空) | authkeywords=`nan`(空) | affiliation_country=`Saudi Arabia`
- **OpenAlex 全作者**:Isra'a Fardous; Amar Bennadji
- **OpenAlex 机构**:Prince Sultan University; Hanze University of Applied Sciences
- **OpenAlex 国家**:SA; NL
- **OpenAlex concepts**:Context (archaeology):0.634; Sustainability:0.615; Architectural engineering:0.495; Engineering:0.486; Cultural heritage:0.442; Architecture:0.435; Process (computing):0.415; Multidisciplinary approac
- **Crossref funder**: | license_types=`tdm; vor` | ref-count=42.0

### 2-s2.0-105039523489 — Genetic algorithm-based assessment of kinetic façade prototypes for energy optimization an
- **Scopus 原始**:first_author=`Safaripoor S.` | author_names=`nan`(空) | authkeywords=`nan`(空) | affiliation_country=`Iran`
- **OpenAlex 全作者**:Samaneh Safaripoor; Mozhgan Karimi; Marjan Ilbeigi; Fatemeh Ahrari; F. Y. Khalili; Fatemeh Mashhadimohammadzadehvazifeh; Raed Alelwani
- **OpenAlex 机构**:Islamic Azad University Bandar Abbas; Modern College of Business and Science; Islamic Azad University of Birjand; Clemson University; Virginia Tech; Al Baha University
- **OpenAlex 国家**:IR; OM; US; SA
- **OpenAlex concepts**:Daylight:0.664; Computer science:0.557; Energy consumption:0.489; Thermal comfort:0.463; Efficient energy use:0.45; Simulation:0.415; Genetic algorithm:0.412; GLARE:0.391
- **Crossref funder**: | license_types=`tdm; vor` | ref-count=34.0

### 2-s2.0-105036579469 — Optimizing Ventilation and Temperature Reduction in Administrative Buildings Using Kinetic
- **Scopus 原始**:first_author=`Abdelhady M.I.` | author_names=`nan`(空) | authkeywords=`nan`(空) | affiliation_country=`Egypt`
- **OpenAlex 全作者**:Mohamed Ibrahim Abdelhady; Mohamed I.A. Habba; Sherif Mohamed Ahmed Ali; Mai Hamdy Abdel Hamid; Hesham Yahia Essa; Asmaa Abd elmoneim Fahmi; Khadiga Elsayed Ahmed Shakra
- **OpenAlex 机构**:Suez University; Modern Academy for Engineering and Technology; Modern Academy; Beni-Suef University
- **OpenAlex 国家**:EG
- **OpenAlex concepts**:Facade:0.904; Kinetic energy:0.647; Ventilation (architecture):0.575; Reduction (mathematics):0.554; Environmental science:0.479; Thermal:0.479; Response surface methodology:0.417; Energy consumption:
- **Crossref funder**: | license_types=`` | ref-count=50.0

### 2-s2.0-105039829141 — 3D-to-4D printing technologies in construction: Roadmap review of current status and poten
- **Scopus 原始**:first_author=`Rajeev P.` | author_names=`nan`(空) | authkeywords=`nan`(空) | affiliation_country=`Australia`
- **OpenAlex 全作者**:Pathmanathan Rajeev; Satheeskumar Navaratnam; Thisari Munmulla; Jay Sanjayan
- **OpenAlex 机构**:nan
- **OpenAlex 国家**:nan
- **OpenAlex concepts**:Current (fluid):0.651; Engineering:0.613; Systems engineering:0.48; Manufacturing engineering:0.45; Technology roadmap:0.382; Computer science:0.329; Engineering drawing:0.301; Electrical engineering:
- **Crossref funder**:Australian Research Council | license_types=`tdm; vor` | ref-count=151.0

> 原始嵌套 OpenAlex 记录见 `openalex_raw.jsonl`(含 referenced_works 全列表,供后续共被引 / 文献耦合)。引用数仍以 Scopus 为准(§5),OpenAlex/Crossref 仅交叉校验。