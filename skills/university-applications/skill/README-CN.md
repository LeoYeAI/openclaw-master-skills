# 🎓 香港各大学硕士招生信息采集 Skill

> 一个纯 Markdown 实现的 Prompt Skill，用于采集香港所有大学的官方硕士项目招生信息。

## 概述

本 Skill 完全由 Markdown 文件构成，是一个 **基于 Prompt 的工作流**。**无需任何编程语言、无需安装依赖、无需运行环境**。通过精心设计的 Prompt 模板，引导 LLM 从官方渠道采集、整理并格式化招生数据。

## 使用方式（自然语言）

直接用自然语言告诉 AI 助手你想做什么即可：

### 采集全部信息
```
请使用香港大学招生信息 Skill，收集所有香港大学的硕士招生信息，并输出所有格式。
```

### 采集单所大学
```
只收集港大的硕士项目信息，输出为 Markdown 和 HTML。
```

### 指定输出格式
```
把已收集的数据输出为 Excel 格式。
```

### 🗣️ 自然语言命令速查表

你可以使用**中文或英文**与本 Skill 交互：

| 说什么 | 做什么 |
|--------|--------|
| "收集所有香港大学硕士招生信息" | 运行全量采集工作流，覆盖全部 22 所院校 |
| "只收集港大的硕士项目" | 单校采集（支持中英文校名识别） |
| "输出为Excel格式" | 生成 TSV 文件，可直接导入 Excel / Google Sheets |
| "输出为HTML网页" | 生成交互式网页（支持搜索、筛选、暗色模式） |
| "输出所有格式" | 一次生成全部 5 种格式（Excel/Word/PDF/HTML/Markdown） |
| "比较各校学费" | 生成跨校对比表格 |
| "输出为[格式]" | 生成指定格式（Excel/Word/PDF/HTML/Markdown） |
| "收集[大学名]的硕士项目" | 采集指定大学的信息 |
| "比较各校[字段]" | 比较学费 / 截止日期 / 英语要求等 |
| "显示[学科领域]的项目" | 按学科领域筛选项目 |

### 🏫 大学名称识别

Skill 支持多种名称识别方式，中英文均可：

| 大学 | 可识别的名称 |
|------|------------|
| 香港大学 | HKU、港大、香港大学 |
| 香港中文大学 | CUHK、中大、香港中文大学 |
| 香港科技大学 | HKUST、UST、科大、香港科技大学 |
| 香港理工大学 | PolyU、理工、香港理工大学 |
| 香港城市大学 | CityU、城大、香港城市大学 |
| 香港浸会大学 | HKBU、浸大、浸會、香港浸会大学 |
| 岭南大学 | LingU、嶺南、岭南大学 |
| 香港教育大学 | EdUHK、教大、香港教育大学 |
| 香港都会大学 | HKMU、都會、都会大学、公开大学、OUHK |
| 香港树仁大学 | HKSYU、树仁、仁大 |
| 香港恒生大学 | HSUHK、恒大、恒生 |
| 圣方济各大学 | SFU、珠海学院、珠海 |
| 香港演艺学院 | HKAPA、演艺、演艺学院 |
| 东华学院 | TWC、东华 |
| 香港能仁专上学院 | NYC、能仁 |
| 香港高等教育科技学院 | THEi、高科院 |
| 宏恩基督教学院 | GCC、宏恩 |
| 明爱专上学院 | CIHE、明爱 |
| 港专学院 | HKCT、港专 |
| 香港伍伦贡学院 | UOWCHK、伍伦贡 |
| 职业训练局 | VTC、职训局 |

## Skill 文件结构

```
skill/
├── skill.md                           # ⭐ Skill 入口文件（一体化定义）
├── README.md                          # 英文入口 - 使用指南
├── README-CN.md                       # 本文件 - 中文使用指南
├── SKILL-SPEC.md                      # 规范定义 - 规则与约束
├── DATA-SCHEMA.md                     # 数据结构 - 字段定义与格式标准
├── COLLECTION-PROMPT.md               # 主采集 Prompt - 数据收集工作流
├── universities/                      # 22 所院校独立采集模板
│   ├── 01-hku.md                      # 香港大学
│   ├── 02-cuhk.md                     # 香港中文大学
│   ├── 03-hkust.md                    # 香港科技大学
│   ├── 04-polyu.md                    # 香港理工大学
│   ├── 05-cityu.md                    # 香港城市大学
│   ├── 06-hkbu.md                     # 香港浸会大学
│   ├── 07-lingu.md                    # 岭南大学
│   ├── 08-eduhk.md                    # 香港教育大学
│   ├── 09-hkmu.md                     # 香港都会大学（原公开大学）
│   ├── 10-hksyu.md                    # 香港树仁大学
│   ├── 11-hsuhk.md                    # 香港恒生大学
│   ├── 12-sfu.md                      # 圣方济各大学（原珠海学院）
│   ├── 13-hkapa.md                    # 香港演艺学院
│   ├── 14-twc.md                      # 东华学院
│   ├── 15-nyc.md                      # 香港能仁专上学院
│   ├── 16-thei.md                     # 香港高等教育科技学院
│   ├── 17-chuhai-redirect.md          # 珠海学院重定向 → 12-sfu.md
│   ├── 18-ouhk-redirect.md            # 公开大学重定向 → 09-hkmu.md
│   ├── 19-gcc.md                      # 宏恩基督教学院
│   ├── 20-cihe.md                     # 明爱专上学院
│   ├── 21-hkct.md                     # 港专学院
│   ├── 22-uowchk.md                   # 香港伍伦贡学院
│   └── 23-vtc.md                      # 职业训练局
├── output-templates/                  # 5 种输出格式模板
│   ├── excel-template.md              # Excel/CSV 输出模板
│   ├── word-template.md               # Word 文档输出模板
│   ├── pdf-template.md                # PDF 输出模板
│   ├── html-template.md               # HTML 网页输出模板
│   └── markdown-template.md           # Markdown 输出模板
├── workflows/                         # 工作流编排
│   ├── full-collection.md             # 全量采集工作流
│   ├── single-university.md           # 单校采集工作流
│   └── format-conversion.md           # 格式转换工作流
└── examples/                          # 输出示例
    └── sample-output.md               # 预期输出样本
```

## 覆盖院校（共 22 所）

### 🏛️ UGC 资助大学（8 所）

| # | 大学名称 | 缩写 | 官方招生页面 |
|---|---------|------|------------|
| 1 | 香港大学 | HKU | https://www.gradsch.hku.hk/gradsch/prospective-students/programmes-on-offer |
| 2 | 香港中文大学 | CUHK | https://www.gs.cuhk.edu.hk/admissions/programme/taught |
| 3 | 香港科技大学 | HKUST | https://pg.ust.hk/prospective-students/admissions/taught-postgraduate-admissions |
| 4 | 香港理工大学 | PolyU | https://www.polyu.edu.hk/study/pg/taught-postgraduate |
| 5 | 香港城市大学 | CityU | https://www.cityu.edu.hk/pg/taught-postgraduate-programmes |
| 6 | 香港浸会大学 | HKBU | https://gs.hkbu.edu.hk/admission/taught-postgraduate-programmes |
| 7 | 岭南大学 | LingU | https://www.ln.edu.hk/sgs/taught-postgraduate-programmes |
| 8 | 香港教育大学 | EdUHK | https://www.eduhk.hk/gradsch/index.php/prospective-students/taught-postgraduate-programmes |

### 🏢 自资 / 私立院校（14 所）

| # | 院校名称 | 缩写 | 官方招生页面 |
|---|---------|------|------------|
| 9 | 香港都会大学（原公开大学） | HKMU | https://admissions.hkmu.edu.hk/tpg/ |
| 10 | 香港树仁大学 | HKSYU | https://gao.hksyu.edu/postgraduate-programmes/ |
| 11 | 香港恒生大学 | HSUHK | https://www.hsu.edu.hk/en/academic-programmes/postgraduate-programmes/ |
| 12 | 圣方济各大学（原珠海学院） | SFU | https://www.sfu.edu.hk/en/programmes/postgraduate/ |
| 13 | 香港演艺学院 | HKAPA | https://www.hkapa.edu/academic-programmes/postgraduate |
| 14 | 东华学院 | TWC | https://www.twc.edu.hk/en/Programmes/postgraduate |
| 15 | 香港能仁专上学院 | NYC | https://www.ny.edu.hk/en/programmes |
| 16 | 香港高等教育科技学院 | THEi | https://www.thei.edu.hk/programme/postgraduate |
| 17 | 宏恩基督教学院 | GCC | https://www.gratia.edu.hk/programmes |
| 18 | 明爱专上学院 | CIHE | https://www.cihe.edu.hk/en/programmes |
| 19 | 港专学院 | HKCT | https://www.hkct.edu.hk/en/programmes |
| 20 | 香港伍伦贡学院 | UOWCHK | https://www.uowchk.edu.hk/programmes |
| 21 | 职业训练局 | VTC | https://www.vtc.edu.hk/admission/en/programme/ |

> ⚠️ **注意**：部分私立院校以本科课程为主，采集时会验证其硕士课程开设情况。若无硕士课程将在输出中注明。

> 📌 **院校更名**：珠海学院 → 圣方济各大学（2022年）；香港公开大学 → 香港都会大学（2021年）

## 采集数据字段

每个硕士项目采集以下信息：

| # | 字段 | 说明 |
|---|------|------|
| 1 | 大学名称 | 中英文 |
| 2 | 学院/系 | 所属学院或学系 |
| 3 | 项目名称 | 中英文全称 |
| 4 | 学位类型 | MSc / MA / MBA / MEd / MFA 等 |
| 5 | 修读模式 | 全日制 / 兼读制 / 混合制 |
| 6 | 修读年限 | 如"1年全日制 / 2年兼读制" |
| 7 | 学费（总计） | 以港币（HKD）计 |
| 8 | 学费（每年） | 如分年缴纳 |
| 9 | 申请开放时间 | 开始接受申请的日期 |
| 10 | 申请截止日期（主轮） | 主要截止日期 |
| 11 | 申请截止日期（补轮） | 如有补录轮次 |
| 12 | 雅思要求 | IELTS 总分及小分要求 |
| 13 | 托福要求 | TOEFL iBT 分数要求 |
| 14 | 其他英语要求 | CET-6 等其他认可考试 |
| 15 | 其他入学要求 | 专业背景、工作经验等 |
| 16 | 项目简介 | 简要描述 |
| 17 | 项目官方链接 | 直达项目页面的 URL |
| 18 | 数据采集日期 | 记录采集时间 |
| 19 | 数据时效提示 | 是否需要验证 |

## 输出格式说明

| 格式 | 说明 | 适用场景 |
|------|------|---------|
| 📊 **Excel** | TSV 格式，可直接导入 Excel / Google Sheets | 数据分析、排序筛选 |
| 📄 **Word** | Word 兼容的 HTML 格式 | 正式报告、打印 |
| 📕 **PDF** | 打印优化的 HTML，浏览器另存为 PDF | 分享、存档 |
| 🌐 **HTML** | 交互式网页，支持搜索、筛选、暗色模式 | 在线浏览、交互查询 |
| 📝 **Markdown** | 带目录的结构化 Markdown 文档 | 文档管理、版本控制 |

## 核心规则

1. ✅ **仅使用大学官方网站**作为数据来源
2. ❌ **严禁使用任何第三方来源**（中介网站、论坛、排名网站等）
3. ✅ 所有链接必须指向官方域名（`.hku.hk`、`.cuhk.edu.hk`、`.ust.hk` 等）
4. ✅ 必须记录数据采集日期，便于追踪时效性
5. ✅ 无法获取的信息标注为"请查阅官方网站"

## 工作流说明

### 全量采集工作流
```
Step 1: 准备     → 读取规范和数据结构定义
Step 2: 采集     → 逐校采集所有硕士项目信息
Step 3: 验证     → 校验数据完整性、链接有效性
Step 4: 统计     → 计算汇总统计（学费、截止时间、英语要求等）
Step 5: 格式化   → 按请求的格式生成输出
Step 6: 交付     → 呈现结果并附使用说明
```

### 单校采集工作流
```
Step 1: 识别大学  → 从用户输入中识别目标大学
Step 2: 读取模板  → 加载对应的大学采集模板
Step 3: 采集     → 收集该校所有硕士项目
Step 4: 输出     → 按请求的格式生成结果
```

### 格式转换工作流
```
Step 1: 确认数据  → 确保数据已采集
Step 2: 选择格式  → 识别用户请求的输出格式
Step 3: 应用模板  → 使用对应的输出模板
Step 4: 交付     → 呈现格式化结果
```

---

> 📖 English version: [README.md](README.md)
