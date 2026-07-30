---
title: "ai-news-daily-brief"
---

# AI News Daily Brief

AI News Daily Brief 是一个用于生成 **AI 新闻日报** 的 Skill。  
它会基于固定的中外 AI 新闻源与官方信源，检索最近 24 小时的重要 AI 新闻，完成去重、分类、摘要提炼与影响判断，并输出一份结构化的中文日报。

---

## 1. Skill Purpose

本 Skill 用于帮助用户快速获取最近 24 小时内最重要的 AI 行业动态，避免手动浏览大量新闻网站和重复信息。

它的核心能力包括：
- 基于固定信源检索 AI 新闻
- 过滤低价值、弱相关、重复内容
- 合并同一事件的多源报道
- 区分官方一手源与媒体二手报道
- 输出结构化中文日报
- 提供简要趋势判断与产品启示

---

## 2. Supported Source Types

Skill 使用以下三类信源：

### 中文媒体源
- AIBase
- 36Kr AI
- 机器之心
- 量子位

### 国外媒体源
- Reuters
- The Verge
- WIRED
- VentureBeat

### 官方一手源
- Google DeepMind Blog
- OpenAI News
- Anthropic Newsroom
- Anthropic Engineering
- NVIDIA Blog

详细入口链接与说明请见：
- `references/sources.md`

---

## 3. Main Behavior

该 Skill 的默认行为如下：

1. 检索最近 24 小时内的重要 AI 新闻
2. 根据相关性和价值进行筛选
3. 对重复事件进行去重和合并
4. 优先采用官方源和高优先级媒体源
5. 生成一份中文 AI 新闻日报
6. 通常输出 12–15 条新闻
7. 高价值新闻不足时，可降至 8–10 条
8. 极少数高密度新闻周期下，可扩展至最多 20 条

---

## 4. Output Structure

日报通常包含以下三部分：

### 一、今日最重要的 5 条 AI 新闻
每条包含：
- 标题
- 类别
- 主来源
- 发布时间
- 事件摘要
- 关键看点
- 影响判断
- 原始链接
- 补充来源（如有）

### 二、完整新闻清单
按类别分组输出全部收录新闻，通常为 12–15 条。

分类包括：
- 模型与产品发布
- Agent与应用落地
- 企业与商业化动态
- 基础设施 / 芯片 / 算力
- 政策 / 监管 / AI安全
- 研究进展与技术趋势

### 三、日报总结
包括：
- 今日最值得关注的 3 个信号
- 对 AI 产品经理最有价值的 3 条启示
- 对企业 AI / 知识库 / RAG / 办公场景相关的机会点或风险点

详细输出模板请见：
- `references/output-template.md`

分类定义与分类边界请见：
- `references/category-taxonomy.md`
---

## 5. Search and Filtering Rules

Skill 在检索和整理时遵循以下原则：

- 中文源优先使用中文检索
- 国外源和官方源优先使用英文检索
- 重要跨语言事件可中英文双检索
- 同一事件只保留一个主条目
- 优先级：官方源 > Reuters > 国外主流科技媒体 > 中文垂直媒体 > 聚合类媒体
- 低价值、营销型、重复转载、弱相关内容默认过滤

详细规则请见：
- `references/search-rules.md`

分类口径和归类规则请见：
- `references/category-taxonomy.md`

---

## 6. Output Language

默认输出语言为 **简体中文**。

规则：
- 标题、摘要、分类、分析、总结默认使用简体中文
- 原文标题在必要时可保留英文
- 除非用户明确要求英文，否则不输出英文日报

---

## 7. Recommended Use Cases

适合以下场景：
- 每日 AI 行业动态跟踪
- AI 产品经理晨报 / 晚报
- 团队内部 AI 新闻简报
- 企业 AI 竞争情报整理
- 知识库 / RAG / Agent / AI 办公方向的趋势观察
- 管理汇报前的快速信息收集

---

## 8. Example User Requests

- 帮我整理今天的 AI 新闻日报
- 汇总最近 24 小时 AI 圈的重要新闻
- 基于固定信源生成今日 AI 简报
- 给我一份 AI 行业日报
- Generate today’s AI news daily brief

---

## 9. Folder Structure

```text
ai-news-daily-brief/
├─ SKILL.md
├─ README.md
└─ references/
   ├─ sources.md
   ├─ search-rules.md
   ├─ output-template.md
   └─ category-taxonomy.md
```
