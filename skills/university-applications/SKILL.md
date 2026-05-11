---
name: hk-university-admissions
description: >
  采集香港所有大学（含公立及私立共22所院校）的官方硕士项目招生信息，
  包括学费、申请时间、截止日期、英语要求、项目详情及官方链接，
  并输出为 Excel、Word、PDF、HTML 和 Markdown 五种格式。
  仅使用大学官方数据源，严禁任何第三方信息。
version: 1.0.0
type: prompt-based
implementation: pure-markdown
interface: natural-language
languages:
  - zh-CN
  - en
tags:
  - hong-kong
  - university
  - master-admissions
  - data-collection
  - multi-format-export
author: user
license: MIT
---

# 🎓 Skill: 香港大学硕士招生信息采集

> **Skill Name**: `hk-university-admissions`
> **Version**: 1.0.0
> **Type**: Prompt-based Data Collection & Formatting
> **Implementation**: Pure Markdown — No code, no dependencies
> **Interface**: Natural Language (中文 / English)
---

## 1. Skill 概述

本 Skill 用于采集香港所有大学及院校的**官方硕士项目招生信息**，并输出为 5 种格式（Excel / Word / PDF / HTML / Markdown）。

### 核心能力

- 🔍 **数据采集** — 从 22 所香港院校官方网站收集硕士招生信息
- ✅ **数据验证** — 校验来源合法性、数据完整性、格式一致性
- 📊 **统计分析** — 自动生成学费、截止日期、英语要求等汇总统计
- 📤 **多格式输出** — 一键生成 Excel / Word / PDF / HTML / Markdown

### 使用场景

- 准备申请香港硕士项目的学生
- 教育咨询顾问整理院校数据
- 研究机构对比分析香港高等教育信息

---

## 2. 自然语言使用方式

### 🗣️ 说什么做什么

| 你说的话 | Skill 做的事 |
|---------|------------|
| "收集所有香港大学硕士招生信息" | 运行全量采集，覆盖 22 所院校 |
| "只收集港大的硕士项目" | 单校采集（支持中英文校名） |
| "只收集科大和城大" | 多校采集 |
| "输出为Excel格式" | 生成 TSV 文件（可导入 Excel / Google Sheets） |
| "输出为Word文档" | 生成 Word 兼容格式 |
| "输出为PDF" | 生成打印优化的 PDF 格式 |
| "输出为HTML网页" | 生成交互式网页（搜索、筛选、暗色模式） |
| "输出为Markdown" | 生成结构化 Markdown 文档 |
| "输出所有格式" | 一次生成全部 5 种格式 |
| "比较各校学费" | 生成跨校学费对比表 |
| "比较各校截止日期" | 生成申请时间线对比 |
| "显示商科类的项目" | 按学科领域筛选 |
| "Collect all HK university master's admissions info" | Full collection (English) |
| "Get CUHK master's programs" | Single university (English) |
| "Output in all formats" | All 5 formats (English) |

### 🏫 大学名称识别表

Skill 能识别以下任何一种名称（中/英/缩写均可）：

**UGC 资助大学（8 所）：**

| 大学 | 可识别的名称 | 模板文件 |
|------|------------|---------|
| 香港大学 | HKU、港大、香港大学、The University of Hong Kong | `skill/universities/01-hku.md` |
| 香港中文大学 | CUHK、中大、香港中文大学、Chinese University | `skill/universities/02-cuhk.md` |
| 香港科技大学 | HKUST、UST、科大、香港科技大学、Science & Tech | `skill/universities/03-hkust.md` |
| 香港理工大学 | PolyU、理工、香港理工大学、Polytechnic | `skill/universities/04-polyu.md` |
| 香港城市大学 | CityU、城大、香港城市大学、City University | `skill/universities/05-cityu.md` |
| 香港浸会大学 | HKBU、浸大、浸會、香港浸会大学、Baptist | `skill/universities/06-hkbu.md` |
| 岭南大学 | LingU、嶺南、岭南大学、Lingnan | `skill/universities/07-lingu.md` |
| 香港教育大学 | EdUHK、教大、香港教育大学、Education University | `skill/universities/08-eduhk.md` |

**自资 / 私立院校（14 所）：**

| 院校 | 可识别的名称 | 模板文件 |
|------|------------|---------|
| 香港都会大学 | HKMU、都會、都会大学、OUHK、公开大学 | `skill/universities/09-hkmu.md` |
| 香港树仁大学 | HKSYU、树仁、仁大 | `skill/universities/10-hksyu.md` |
| 香港恒生大学 | HSUHK、恒大、恒生 | `skill/universities/11-hsuhk.md` |
| 圣方济各大学 | SFU、珠海学院、珠海 | `skill/universities/12-sfu.md` |
| 香港演艺学院 | HKAPA、演艺、演艺学院 | `skill/universities/13-hkapa.md` |
| 东华学院 | TWC、东华、东华学院 | `skill/universities/14-twc.md` |
| 香港能仁专上学院 | NYC、能仁 | `skill/universities/15-nyc.md` |
| 香港高等教育科技学院 | THEi、高科院 | `skill/universities/16-thei.md` |
| 宏恩基督教学院 | GCC、宏恩 | `skill/universities/19-gcc.md` |
| 明爱专上学院 | CIHE、明爱 | `skill/universities/20-cihe.md` |
| 港专学院 | HKCT、港专 | `skill/universities/21-hkct.md` |
| 香港伍伦贡学院 | UOWCHK、伍伦贡 | `skill/universities/22-uowchk.md` |
| 职业训练局 | VTC、职训局 | `skill/universities/23-vtc.md` |

> 📌 **院校更名说明**
> - 珠海学院 → 圣方济各大学（2022 年更名，见 `skill/universities/17-chuhai-redirect.md`）
> - 香港公开大学 → 香港都会大学（2021 年更名，见 `skill/universities/18-ouhk-redirect.md`）

> ⚠️ **注意**：部分自资院校以本科为主，采集时需验证其硕士课程开设情况。若无硕士课程将在输出中标注。

---

## 3. 数据规范

### 3.1 数据来源规则（严格执行）

**✅ 仅允许以下官方域名：**

```
*.hku.hk              — 香港大学
*.cuhk.edu.hk         — 香港中文大学
*.ust.hk              — 香港科技大学
*.polyu.edu.hk        — 香港理工大学
*.cityu.edu.hk        — 香港城市大学
*.hkbu.edu.hk         — 香港浸会大学
*.ln.edu.hk           — 岭南大学
*.eduhk.hk            — 香港教育大学
*.hkmu.edu.hk         — 香港都会大学
*.hksyu.edu           — 香港树仁大学
*.hsu.edu.hk          — 香港恒生大学
*.sfu.edu.hk          — 圣方济各大学
*.hkapa.edu           — 香港演艺学院
*.twc.edu.hk          — 东华学院
*.ny.edu.hk           — 香港能仁专上学院
*.thei.edu.hk         — 香港高等教育科技学院
*.gratia.edu.hk       — 宏恩基督教学院
*.cihe.edu.hk         — 明爱专上学院
*.hkct.edu.hk         — 港专学院
*.uowchk.edu.hk       — 香港伍伦贡学院
*.vtc.edu.hk          — 职业训练局
```

**❌ 严禁使用的来源：**

- 留学中介 / 教育代理网站
- 学生论坛、评价网站
- 第三方排名网站
- 社交媒体
- 新闻报道
- 任何非官方域名

### 3.2 数据字段定义（20 字段）

每个硕士项目采集以下字段：

| # | 字段名 | 类型 | 必填 | 格式说明 |
|---|--------|------|------|---------|
| 1 | university_abbr | String | ✅ | 大学缩写，如 "HKU" |
| 2 | faculty | String | ✅ | 所属学院/学系全称 |
| 3 | program_name_en | String | ✅ | 英文项目全称 |
| 4 | program_name_zh | String | ⬚ | 中文项目名称（如有） |
| 5 | degree_type | Enum | ✅ | MSc / MA / MBA / MEd / MFA / MSW / LLM / MChinMed / MPH / MArch / Other |
| 6 | study_mode | Enum | ✅ | Full-time / Part-time / Full-time & Part-time |
| 7 | duration | String | ✅ | 如 "1 year (FT) / 2 years (PT)" |
| 8 | tuition_fee_total | String | ✅ | 格式: `HKD XXX,XXX` |
| 9 | tuition_fee_annual | String | ⬚ | 格式: `HKD XXX,XXX/year` |
| 10 | application_open_date | String | ✅ | 格式: `DD Month YYYY`，如 "1 September 2025" |
| 11 | application_deadline_main | String | ✅ | 主轮截止日期 |
| 12 | application_deadline_late | String | ⬚ | 补录截止日期（如有） |
| 13 | english_req_ielts | String | ✅ | 如 "Overall 6.5, no sub-score < 5.5" |
| 14 | english_req_toefl | String | ✅ | 如 "iBT 80" |
| 15 | english_req_other | String | ⬚ | 如 "CET-6: 430" |
| 16 | other_requirements | String | ⬚ | 专业背景、工作经验等 |
| 17 | program_description | String | ⬚ | 项目简要描述 |
| 18 | official_url | URL | ✅ | 项目官方页面直链（必须是官方域名） |
| 19 | data_collected_date | Date | ✅ | 格式: `YYYY-MM-DD` |
| 20 | data_freshness_note | String | ⬚ | 如 "⚠️ Verify at official site" |

### 3.3 格式标准

| 类型 | 标准 | 示例 |
|------|------|------|
| 货币 | 港币 HKD，千位逗号 | `HKD 180,000` |
| 费用范围 | 用连字符 | `HKD 120,000 - 180,000` |
| 日期 | DD Month YYYY | `30 November 2025` |
| 滚动招生 | 特殊标记 | `Rolling (until places filled)` |
| URL | 完整 HTTPS | `https://www.msc-cs.hku.hk` |
| 未知信息 | 标注来源 | `N/A - Check Official Site` |

### 3.4 数据质量规则

1. **准确性** — 只记录官方确认的信息
2. **完整性** — 采集所有可用字段，缺失标注 "N/A - Check Official Site"
3. **一致性** — 所有大学使用统一格式
4. **时效性** — 记录采集日期，过时数据标注 ⚠️
5. **双语性** — 项目名称尽量包含中英文
6. **可追溯** — 每个项目必须附带官方 URL
7. **透明性** — 无法确认的信息明确标注

---

## 4. 工作流定义

### 4.1 全量采集工作流

**触发条件**：用户说"收集所有香港大学硕士招生信息"或类似指令

```
Phase 1: 准备
  → 读取本 SKILL.md 的规范定义（第 3 节）
  → 记录当前日期用于数据时效追踪

Phase 2: 逐校采集（共 22 所）

  [UGC 资助大学 - 8 所]
  Step 2.1:  读取 skill/universities/01-hku.md    → 采集港大所有硕士项目
  Step 2.2:  读取 skill/universities/02-cuhk.md   → 采集中大所有硕士项目
  Step 2.3:  读取 skill/universities/03-hkust.md  → 采集科大所有硕士项目
  Step 2.4:  读取 skill/universities/04-polyu.md  → 采集理工所有硕士项目
  Step 2.5:  读取 skill/universities/05-cityu.md  → 采集城大所有硕士项目
  Step 2.6:  读取 skill/universities/06-hkbu.md   → 采集浸大所有硕士项目
  Step 2.7:  读取 skill/universities/07-lingu.md  → 采集岭南所有硕士项目
  Step 2.8:  读取 skill/universities/08-eduhk.md  → 采集教大所有硕士项目

  [自资 / 私立院校 - 14 所]
  Step 2.9:  读取 skill/universities/09-hkmu.md   → 采集都会大学所有硕士项目
  Step 2.10: 读取 skill/universities/10-hksyu.md  → 采集树仁大学所有硕士项目
  Step 2.11: 读取 skill/universities/11-hsuhk.md  → 采集恒生大学所有硕士项目
  Step 2.12: 读取 skill/universities/12-sfu.md    → 采集圣方济各大学所有硕士项目
  Step 2.13: 读取 skill/universities/13-hkapa.md  → 采集演艺学院所有硕士项目
  Step 2.14: 读取 skill/universities/14-twc.md    → 采集东华学院所有硕士项目
  Step 2.15: 读取 skill/universities/15-nyc.md    → 采集能仁学院硕士项目（如有）
  Step 2.16: 读取 skill/universities/16-thei.md   → 采集高科院所有硕士项目
  Step 2.17: 读取 skill/universities/19-gcc.md    → 采集宏恩学院硕士项目（如有）
  Step 2.18: 读取 skill/universities/20-cihe.md   → 采集明爱学院硕士项目（如有）
  Step 2.19: 读取 skill/universities/21-hkct.md   → 采集港专学院硕士项目（如有）
  Step 2.20: 读取 skill/universities/22-uowchk.md → 采集伍伦贡学院硕士项目（如有）
  Step 2.21: 读取 skill/universities/23-vtc.md    → 采集职训局硕士项目（如有）

  ※ 部分小型院校可能不提供硕士课程，若无则记录"该院校目前未开设硕士课程"

Phase 3: 数据验证
  ✅ 所有 URL 指向官方域名
  ✅ 学费格式为 HKD
  ✅ 日期格式为 DD Month YYYY
  ✅ 必填字段完整（缺失标注 N/A）
  ✅ IELTS/TOEFL 分数在合理范围内
  ✅ 无重复项目条目
  ✅ 每个项目有唯一官方 URL

Phase 4: 统计汇总
  → 项目总数
  → 各校项目数量
  → 各学位类型分布（MSc/MA/MBA/...）
  → 学费统计（最低/最高/平均/中位数）
  → 各校平均学费
  → 截止日期时间线分布
  → 英语要求分布
  → 修读模式分布

Phase 5: 格式化输出
  → 根据用户要求选择输出格式
  → 读取 output-templates/ 目录下对应模板
  → 生成格式化输出

Phase 6: 交付
  📊 Excel  → 保存为 .tsv，用 Excel / Google Sheets 打开
  📄 Word   → 保存为 .html，用 Word 打开后另存为 .docx
  📕 PDF    → 保存为 .html，浏览器打印 → 另存为 PDF
  🌐 HTML   → 保存为 .html，浏览器打开（支持交互功能）
  📝 Markdown → 保存为 .md，用 Markdown 阅读器查看
```

### 4.2 单校采集工作流

**触发条件**：用户指定某所大学（如"只收集港大的硕士项目"）

```
Step 1: 识别大学
  → 从用户输入中匹配大学名称（参考第 2 节名称识别表）
  → 定位对应的 skill/universities/XX-xxx.md 模板文件

Step 2: 读取规范
  → 读取本 SKILL.md 的数据规范（第 3 节）

Step 3: 采集数据
  → 读取对应大学模板，采集该校所有硕士项目
  → 遵循模板中的官方数据源、英语要求基准、URL 验证规则

Step 4: 验证 & 统计
  → 验证数据质量
  → 生成该校的统计汇总

Step 5: 格式化输出
  → 如用户未指定格式，默认输出 Markdown
  → 如指定格式，使用对应的输出模板
```

### 4.3 格式转换工作流

**触发条件**：用户要求对已采集数据转换格式（如"输出为HTML网页"）

```
Step 1: 确认数据已采集（若未采集，先运行采集工作流）

Step 2: 识别目标格式
  | 用户说的 | 对应格式 | 模板文件 |
  |---------|---------|---------|
  | Excel / 表格 / CSV / TSV | Excel | skill/output-templates/excel-template.md |
  | Word / 文档 / doc | Word | skill/output-templates/word-template.md |
  | PDF / 打印 | PDF | skill/output-templates/pdf-template.md |
  | HTML / 网页 / web | HTML | skill/output-templates/html-template.md |
  | Markdown / MD / 文本 | Markdown | skill/output-templates/markdown-template.md |
  | 所有格式 / all | 全部 5 种 | 所有模板 |

Step 3: 应用模板，生成输出

Step 4: 多格式输出顺序（生成全部时）
  1. Markdown → 最快预览
  2. Excel/CSV → 数据分析
  3. HTML → 交互浏览
  4. Word → 正式文档
  5. PDF → 打印/存档
```

---

## 5. 输出格式详细说明

| 格式 | 文件类型 | 特性 | 适用场景 |
|------|---------|------|---------|
| 📊 **Excel** | `.tsv` | Tab 分隔，含标题行，可直接导入 | 数据分析、排序筛选 |
| 📄 **Word** | `.html` → `.docx` | 结构化表格、分校章节 | 正式报告、打印 |
| 📕 **PDF** | `.html` → PDF | 打印优化、分页、封面 | 分享、存档 |
| 🌐 **HTML** | `.html` | 搜索、筛选、排序、暗色模式、响应式 | 在线浏览、交互查询 |
| 📝 **Markdown** | `.md` | 目录、表格、链接、汇总统计 | 文档管理、版本控制 |

---

## 6. 数据采集模板

每个项目的标准采集格式：

```markdown
### [项目全称]

| Field | Value |
|-------|-------|
| University | [大学名称] ([缩写]) |
| Faculty | [学院/学系名称] |
| Program (EN) | [英文全称] |
| Program (ZH) | [中文名称 or N/A] |
| Degree Type | [MSc/MA/MBA/etc.] |
| Study Mode | [Full-time/Part-time/Both] |
| Duration | [X year(s) FT / X year(s) PT] |
| Tuition (Total) | HKD [金额] |
| Tuition (Annual) | HKD [金额]/year |
| Application Opens | [日期] |
| Main Deadline | [日期] |
| Late Deadline | [日期 or N/A] |
| IELTS | [要求] |
| TOEFL | [要求] |
| Other English | [其他英语测试 or N/A] |
| Other Requirements | [其他要求 or N/A] |
| Description | [简要描述] |
| Official URL | [URL — 必须为官方域名] |
| Collected Date | [采集日期] |
| Freshness Note | [时效提示 or ✅ Verified] |
```

---

## 7. 统计汇总模板

采集完成后自动生成：

```markdown
## 📊 汇总统计

### 总览
- 覆盖院校数：X / 22
- 项目总数：X 个
- 数据采集日期：YYYY-MM-DD

### 各校项目数量
| 大学 | 项目数 | 平均学费 (HKD) |
|------|--------|---------------|
| HKU | XX | XXX,XXX |
| CUHK | XX | XXX,XXX |
| ... | ... | ... |

### 学位类型分布
| 类型 | 数量 | 占比 |
|------|------|------|
| MSc | XX | XX% |
| MA | XX | XX% |
| MBA | XX | XX% |
| ... | ... | ... |

### 学费统计
- 最低：HKD XXX,XXX ([项目名])
- 最高：HKD XXX,XXX ([项目名])
- 平均：HKD XXX,XXX
- 中位数：HKD XXX,XXX

### 英语要求分布
| IELTS 要求 | 项目数 |
|-----------|--------|
| 6.0 | XX |
| 6.5 | XX |
| 7.0 | XX |
```

---

## 8. 重要提醒

> ⚠️ **关于数据时效性**
>
> 本 Skill 由 AI 助手执行，训练数据存在知识截止日期。为确保信息准确：
>
> 1. **所有输出均附带官方 URL**，请用户自行验证最新信息
> 2. 可能过时的数据会标注 ⚠️ 警告标识
> 3. **绝不编造**具体数字 — 不确定时标注"请查阅 [URL]"
> 4. **准确性优先于完整性** — 宁缺勿错

---

## 9. 文件结构索引

```
/                                      ← 项目根目录
├── SKILL.md                           ← 本文件（Skill 入口 & 完整定义）
├── SKILL-SPEC.md                      ← 技能规范定义
│
└── skill/                             # Skill 实现目录
    ├── README.md                      # English usage guide
    ├── README-CN.md                   # 中文使用指南
    ├── SKILL-SPEC.md                  # 规范定义（详细版，同根目录）
    ├── DATA-SCHEMA.md                 # 数据结构定义（详细版）
    ├── COLLECTION-PROMPT.md           # 主采集 Prompt
    │
    ├── universities/                  # 22 所院校独立采集模板
    │   ├── 01-hku.md                  # 香港大学
    │   ├── 02-cuhk.md                 # 香港中文大学
    │   ├── 03-hkust.md                # 香港科技大学
    │   ├── 04-polyu.md                # 香港理工大学
    │   ├── 05-cityu.md                # 香港城市大学
    │   ├── 06-hkbu.md                 # 香港浸会大学
    │   ├── 07-lingu.md                # 岭南大学
    │   ├── 08-eduhk.md                # 香港教育大学
    │   ├── 09-hkmu.md                 # 香港都会大学（原公开大学）
    │   ├── 10-hksyu.md                # 香港树仁大学
    │   ├── 11-hsuhk.md                # 香港恒生大学
    │   ├── 12-sfu.md                  # 圣方济各大学（原珠海学院）
    │   ├── 13-hkapa.md                # 香港演艺学院
    │   ├── 14-twc.md                  # 东华学院
    │   ├── 15-nyc.md                  # 香港能仁专上学院
    │   ├── 16-thei.md                 # 香港高等教育科技学院
    │   ├── 17-chuhai-redirect.md      # → 12-sfu.md（珠海学院已更名）
    │   ├── 18-ouhk-redirect.md        # → 09-hkmu.md（公开大学已更名）
    │   ├── 19-gcc.md                  # 宏恩基督教学院
    │   ├── 20-cihe.md                 # 明爱专上学院
    │   ├── 21-hkct.md                 # 港专学院
    │   ├── 22-uowchk.md              # 香港伍伦贡学院
    │   └── 23-vtc.md                  # 职业训练局
    │
    ├── output-templates/              # 5 种输出格式模板
    │   ├── excel-template.md          # Excel / TSV
    │   ├── word-template.md           # Word 文档
    │   ├── pdf-template.md            # PDF
    │   ├── html-template.md           # HTML 交互网页
    │   └── markdown-template.md       # Markdown
    │
    ├── workflows/                     # 工作流编排（详细版）
    │   ├── full-collection.md         # 全量采集
    │   ├── single-university.md       # 单校采集
    │   └── format-conversion.md       # 格式转换
    │
    ├── output/                        # 生成的输出文件
    │   ├── hk_admissions.md           # Markdown 输出
    │   ├── hk_admissions.tsv          # Excel (TSV) 输出
    │   ├── hk_admissions.html         # HTML 交互网页
    │   ├── hk_admissions_word.html    # Word 兼容文档
    │   └── hk_admissions_print.html   # PDF 打印优化
    │
    └── examples/                      # 示例输出
        └── sample-output.md           # 预期输出样本
```

---

## 10. 快速开始

### 最简使用

将本项目提供给 AI 助手，然后说：

```
请阅读 SKILL.md，然后收集所有香港大学硕士招生信息，输出所有格式。
```

### 仅采集特定大学

```
请阅读 SKILL.md，只收集港大和中大的硕士项目，输出为 HTML 网页。
```

### 仅转换格式

```
把刚才收集的数据输出为 Excel 格式。
```

---

> 📖 详细英文说明: [README.md](skill/README.md) | 📖 详细中文说明: [README-CN.md](skill/README-CN.md)
