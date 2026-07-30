---
title: "AI News Daily Brief - Output Template"
---

# Output Template

Use the following template to generate the final AI news daily brief.

Unless the user explicitly requests another language, all final output must be in Simplified Chinese.

---

# AI新闻日报（{{date}}）

## 一、今日最重要的5条AI新闻

> 如果当日Verified高价值新闻不足5条，本节以实际数量呈现，不要凑数。

### 1. {{title}}
- **类别**：{{category}}
- **主来源**：{{primary_source}}
- **发布时间**：{{published_time}}
- **事件摘要**：{{summary_100_150_words}}
- **关键看点**：
  1. {{key_point_1}}
  2. {{key_point_2}}
  3. {{key_point_3_optional}}
- **影响判断**：{{why_it_matters_50_100_words}}
- **原始链接**：{{original_link}}
- **补充来源**：{{supplementary_sources_optional}}

### 2. {{title}}
...（同上格式）

### 3. {{title}}
...（同上格式）

### 4. {{title}}
...（同上格式）

### 5. {{title}}
...（同上格式）

---

## 二、完整新闻清单

> 标准条数：8–12条；高价值新闻密集时可扩展至12–15条；新闻偏少时正常降至5–8条。不为了凑数而纳入低质量内容。
>
> 若当日Verified来源有限，本节总数可能少于5条，属正常情况。

### 1. 模型与产品发布
- **{{title}}**｜来源：{{source}}｜时间：{{time}}｜{{one_line_summary}}｜{{link}}

### 2. Agent与应用落地
- **{{title}}**｜来源：{{source}}｜时间：{{time}}｜{{one_line_summary}}｜{{link}}

### 3. 企业与商业化动态
- **{{title}}**｜来源：{{source}}｜时间：{{time}}｜{{one_line_summary}}｜{{link}}

### 4. 基础设施 / 芯片 / 算力
- **{{title}}**｜来源：{{source}}｜时间：{{time}}｜{{one_line_summary}}｜{{link}}

### 5. 政策 / 监管 / AI安全
- **{{title}}**｜来源：{{source}}｜时间：{{time}}｜{{one_line_summary}}｜{{link}}

### 6. 研究进展与技术趋势
- **{{title}}**｜来源：{{source}}｜时间：{{time}}｜{{one_line_summary}}｜{{link}}

---

## 三、日报总结

### 1. 今日最值得关注的3个信号
1. {{signal_1}}
2. {{signal_2}}
3. {{signal_3}}

### 2. 对AI产品经理最有价值的3条启示
1. {{pm_takeaway_1}}
2. {{pm_takeaway_2}}
3. {{pm_takeaway_3}}

### 3. 对企业AI / 知识库 / RAG / 办公场景最相关的机会点或风险点
1. {{opportunity_or_risk_1}}
2. {{opportunity_or_risk_2}}
3. {{opportunity_or_risk_3}}

---

## Category Definitions

- **模型与产品发布**：模型发布、能力升级、API更新、平台功能发布
- **Agent与应用落地**：智能体，工作流、AI办公、具体应用场景落地
- **企业与商业化动态**：合作、融资、并购、组织调整、商业化动作
- **基础设施 / 芯片 / 算力**：GPU、推理、芯片、数据中心、基础设施
- **政策 / 监管 / AI安全**：法规、治理、版权、安全、合规
- **研究进展与技术趋势**：对产业和产品有现实意义的研究和技术动态

---

## Output Notes

1. Final output should be concise and readable in about 5 minutes.
2. Do not force all categories to contain items every day.
3. If a category has no meaningful news, omit low-value filler.
4. If information is uncertain, explicitly mark it as "待核实".
5. Keep analysis practical and product-relevant.
6. Distinguish clearly between official announcements and media coverage.
7. If verified news is scarce (fewer than 5 items), output fewer items — this is normal and preferable to padding with low-quality content.

## Summary Writing Guidance

For the "三、日报总结" section:

- **"今日最值得关注的3个信号"**: Focus on macro-level industry shifts, not individual product releases. Each signal should be 1 sentence.
- **"对AI产品经理最有价值的3条启示"**: Be specific and actionable. Connect the news to product decisions, tool choices, or market positioning.
- **"机会点或风险点"**: Limit to enterprise AI / knowledge base / RAG / office scenarios. Do not over-generalize.

Do not repeat the same insight across multiple sections. Each section should be genuinely distinct.
