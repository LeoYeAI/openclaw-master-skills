# 📱 CN Content Matrix

> One topic, four platforms, zero reformatting. True style transfer for Chinese social media.

[![OpenClaw Skill](https://img.shields.io/badge/OpenClaw-Skill-blue)](https://github.com/anthropics/claude-code)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-1.0.0-brightgreen)]()
[![Platforms](https://img.shields.io/badge/platforms-4-orange)]()

## Overview

CN Content Matrix is not a format converter — it's a **style transfer engine** for Chinese social media. Given a single topic, it generates platform-native content that reads like it was written by a real KOL on each platform, not by an AI doing find-and-replace on templates.

The core insight: a Xiaohongshu post about "home coffee brewing" should feel like your best friend gushing about a discovery, while the same topic on WeChat Official Account should read like a thoughtful industry analysis. Same information, completely different voice, structure, and emotional appeal.

## Supported Platforms

| Platform | Code | Word Count | Tone | Key Elements |
|----------|------|-----------|------|-------------|
| **小红书** (Xiaohongshu) | `xhs` | 300–800 | Casual, bestie-sharing, seed-planting | Emoji-dense, hashtags, first-person sharing, short paragraphs (≤3 sentences) |
| **微信公众号** (WeChat MP) | `wechat` | 1,500–8,000 | Professional, insightful, authoritative | Long-form analysis, data-driven, structured sections, SEO-optimized |
| **抖音** (Douyin/TikTok CN) | `douyin` | 200–5,000 | Fast-paced, punchy, high-energy | Script format, 15-char max per line, 3-second hook, scene cuts annotated |
| **B站** (Bilibili) | `bilibili` | 3,000–15,000 | Knowledgeable, meme-savvy, friendly expert | Rich text (code blocks, tables), table of contents, deep-dive structure |

## Features

- **True Style Transfer** — persona-switching, not template-filling. Each platform gets content written in its native voice
- **Content Core Architecture** — all platform variants derive from a shared "Content Core" document, ensuring message consistency with style diversity
- **Real-time Research** — WebSearch-powered topic research with current-year trending angles and keywords
- **Sensitive Word Detection** — three-tier screening (🔴 hard-ban / 🟡 soft-limit / 🟢 caution) against Chinese advertising law and platform rules
- **Content Compliance Review** — 6-dimension scoring system (word count, format, tone, sensitive words, SEO, publishability) with 60-point scale
- **Shell-based Quality Check** — `content-check.sh` script for quick automated compliance validation
- **Anti-AI Detection** — built-in rules to eliminate "AI smell" phrases like "随着科技的发展", "值得注意的是", etc.
- **Cross-platform Differentiation Check** — automated detection of content overlap (>50 chars repeated = fail)
- **Platform-specific CTAs** — Xiaohongshu → save+comment, WeChat → follow+share, Douyin → comment+follow, Bilibili → triple-click

## Quick Start

```bash
# Install: add to your Claude Code skill directory
# Then invoke via slash command:

# Generate content for a single platform (defaults to Xiaohongshu)
/cn-content-matrix content-gen 家用咖啡机选购 xhs

# Generate for all 4 platforms at once
/cn-content-matrix content-matrix 家用咖啡机选购

# Review existing content for compliance
/cn-content-matrix content-review xhs ~/content-output/2026-03-21/coffee/xhs.md
```

Output is saved to `~/content-output/{date}/{topic-slug}/`.

## Commands

### `/cn-content-matrix content-gen [topic] [platform]`

Generate content for a **single platform**.

```bash
# Examples
/cn-content-matrix content-gen AI编程工具推荐 wechat
/cn-content-matrix content-gen 春季护肤 xhs
/cn-content-matrix content-gen 副业赚钱 douyin
/cn-content-matrix content-gen Rust语言入门 bilibili
```

**Pipeline:** Topic Research → Load Platform Spec → Generate with Style Transfer → Self-check → Output

Output file: `~/content-output/{date}/{topic}/{platform}.md`

```yaml
# Output frontmatter
---
platform: 小红书
topic: 春季护肤
word_count: 526
generated_at: 2026-03-21T14:30:00+08:00
self_check: PASS
---
```

### `/cn-content-matrix content-matrix [topic]`

Generate a **full content matrix** — all 4 platforms from a single Content Core.

```bash
/cn-content-matrix content-matrix 家用咖啡机选购
/cn-content-matrix content-matrix 2026年AI趋势
```

**Pipeline:** Research → Build Content Core → Generate in order (WeChat → Bilibili → Xiaohongshu → Douyin) → Differentiation Check → Overview Report

Output structure:
```
~/content-output/{date}/{topic}/matrix/
├── content-core.md    # Shared content foundation
├── wechat.md          # WeChat Official Account version
├── bilibili.md        # Bilibili column version
├── xhs.md             # Xiaohongshu version
├── douyin.md          # Douyin script version
└── overview.md        # Cross-platform comparison table
```

The `overview.md` includes a comparison table across all platforms (word count, tone, angle, selling points, CTA, special elements) plus publishing time recommendations.

### `/cn-content-matrix content-review [platform] [file]`

**Review existing content** for platform compliance. Scores across 6 dimensions on a 60-point scale.

```bash
/cn-content-matrix content-review xhs ./my-draft.md
/cn-content-matrix content-review wechat ./article.md
```

**Output:** A detailed review report with:
- Overall verdict: PASS ✅ / WARNING ⚠️ / FAIL ❌
- Per-dimension scores (0–10 each): word count, format structure, tone match, sensitive words, SEO friendliness, publishability
- Prioritized fix list: 🔴 must-fix → 🟡 should-fix → 🟢 nice-to-have
- For FAIL results: auto-generated `fix-suggestions-{platform}.md` with copy-paste replacements

## Style Transfer Engine

This is the core differentiator. Here's the same topic — **"Home Coffee Brewing"** — adapted for each platform:

### Xiaohongshu (bestie sharing)
```
☕ 姐妹们！我终于找到在家做出咖啡店味道的方法了！

之前花了大几千买的咖啡机根本不好用 😭
直到我发现了这个 300 块的手冲组合...

✅ 磨豆机选这款就够了
✅ 滤杯别买贵的，新手用扇形
✅ 水温 92 度是灵魂

你们觉得呢？评论区告诉我你们平时怎么冲 ☕
#家用咖啡 #手冲咖啡 #咖啡入门
```

### WeChat Official Account (industry insight)
```
当精品咖啡从「第三空间」走进「第一空间」

据美团数据显示，2025年中国家庭咖啡消费同比增长47%。
这不仅是消费习惯的迁移，更是一场静默的品质革命...

本文将从设备选择、豆源甄别、萃取参数三个维度，
为你搭建一套可复用的家庭咖啡体系。
```

### Douyin (3-second hook script)
```
[画面：精美拉花特写]
「千万别买咖啡机」

[字幕强调：千万别买]
「在你看完这条视频之前」

[画面切换：一堆闲置咖啡机]
「因为我踩过的坑，能帮你省3000块」

[口播加速]
「300块，3样东西，在家做出店里的味道」
```

### Bilibili (knowledgeable friend)
```
# 从零搭建家用咖啡系统 —— 一个软件工程师的咖啡装备进化史

## 目录
1. 为什么我放弃了胶囊机
2. 手冲 vs 意式 vs 摩卡壶：参数化对比
3. 300元档 vs 3000元档盲测结果
4. 我的最终方案（附购买链接）

> 前方高能预警：大量数据表格和对比图
> 一键三连支持一下，评论区见～
```

## Platform Specifications

Each platform has a comprehensive spec file in `references/`:

| File | Covers |
|------|--------|
| `references/xiaohongshu.md` | Title formulas (6 types), body structure, emoji/hashtag rules, engagement patterns, algorithm preferences |
| `references/wechat-mp.md` | Title strategies, long-form structure, SEO optimization for 搜一搜, subscription vs recommendation traffic |
| `references/douyin.md` | 7 hook formulas for the critical 3-second window, script format, scene annotation, pacing rules |
| `references/bilibili.md` | Rich text formatting (code blocks, tables), community culture (弹幕, 梗), title strategies for tech content |
| `references/content-core-template.md` | Template for building the shared Content Core (key arguments, data points, audience personas, emotional tone, keywords) |
| `references/sensitive-words.md` | Three-tier sensitive word database with replacement suggestions, updated for 2026 |

## Content Quality Check

The `scripts/content-check.sh` script provides fast, automated compliance validation from the command line:

```bash
./scripts/content-check.sh <file-path> <platform-code>

# Example
./scripts/content-check.sh ~/content-output/2026-03-21/coffee/xhs.md xhs
```

**Checks performed:**

| Check | Details |
|-------|---------|
| **Word Count** | Validates against platform-specific ranges (e.g., xhs: 300–800, wechat: 1500–8000) |
| **Sensitive Words** | Scans for 🔴 hard-ban terms (advertising law violations, fake claims, traffic-diversion words) |
| **Emoji Density** | Platform-appropriate emoji count (xhs: 5–20 required, wechat: ≤10 recommended) |
| **Paragraph Length** | Flags overly long paragraphs (xhs: >200 chars, wechat: >800 chars, bilibili: >600 chars) |

**Exit codes:** `0` = PASS, `1` = WARNING, `2` = FAIL

Sample output:
```
============================================
 内容合规检查报告
 平台: 小红书 (xhs)
 文件: ~/content-output/coffee/xhs.md
============================================

总评: PASS

--- 逐项检查 ---

[字数]       PASS       字数 526，范围 300-800
[敏感词]     PASS       未发现硬违禁词
[Emoji]      PASS       Emoji 12 个（推荐 5-20）
[段落]       PASS       最长段落 156 字符（OK）
```

## Sensitive Word Detection

Three-tier classification system based on Chinese advertising law and platform-specific rules:

| Level | Meaning | Action | Examples |
|-------|---------|--------|----------|
| 🔴 **Hard Ban** | Violates advertising law or triggers instant content removal | Must remove or replace | 最好, 最佳, 100%, 保证, 根治, 稳赚不赔, 日入过万 |
| 🟡 **Soft Limit** | May trigger algorithmic throttling / reduced distribution | Recommended to replace | Platform-specific marketing terms, borderline claims |
| 🟢 **Caution** | Context-dependent, may be ambiguous | Review case-by-case | Terms that are fine in some contexts but risky in others |

Each banned term comes with **suggested replacements** (e.g., "最好" → "很不错", "100%" → "大概率").

Platform-specific additions:
- **Xiaohongshu:** traffic diversion terms (链接在评论区, 暴富, 月入)
- **WeChat:** viral bait (转发领红包, 不转不是中国人)
- **Douyin:** income claims (赚钱, 搞钱)

## Output Structure

All generated content follows a consistent output format:

```yaml
---
platform: {platform name}
topic: {topic}
word_count: {count}
generated_at: {ISO 8601 timestamp}
self_check: PASS / WARNING
warnings: [{list of warnings, if any}]
---

{publishable content body}

---
<!-- 以下为生成器备注，发布时删除 -->
{generator notes, review warnings, modification suggestions}
```

Content is saved to: `~/content-output/{YYYY-MM-DD}/{topic-slug}/`

If the same topic is generated multiple times on the same day, a timestamp suffix is added to avoid overwriting.

## Contributing

Contributions are welcome! Areas where help is appreciated:

- **Platform spec updates** — Chinese social media rules change frequently; help keep `references/` current
- **Sensitive word database** — additions, removals, and replacement suggestions
- **New platform support** — Zhihu, Weibo, Kuaishou, etc.
- **content-check.sh enhancements** — additional automated checks

## License

MIT

---

## 中文说明

### 项目简介

**CN Content Matrix** 是一个基于 Claude Code 的中文多平台内容矩阵生成器。它的核心理念是**风格迁移而非格式转换**——同一个主题，用四种完全不同的"人格"来表达，让每个平台的内容都像是该平台的原生 KOL 写的。

### 为什么需要这个工具？

做过内容矩阵的人都知道痛点：

- ❌ 把公众号文章删减一下发小红书 → 读起来像说明书
- ❌ 把小红书笔记拉长一下发公众号 → 读起来像聊天记录
- ❌ 一稿多发 → 每个平台都不温不火

**CN Content Matrix 的解决方案：** 不是改格式，而是换人格。

| 平台 | 你的人格身份 | 你在对谁说话 | 写作风格 |
|------|-------------|------------|---------|
| 小红书 | 热爱生活的分享达人 | 闺蜜/同好 | 第一人称、种草体、emoji 密集、口语化 |
| 微信公众号 | 有深度的行业观察者 | 关注专业内容的读者 | 深度分析、数据论证、引经据典、书面语 |
| 抖音 | 说话有趣的内容创作者 | 刷到你的路人 | 口播脚本、每句≤15字、前3秒强钩子 |
| B站 | 懂行的知识UP主 | 愿意看深度内容的粉丝 | 技术科普、用梗、弹幕文化、代码块支持 |

### 三大核心功能

#### 1. 单平台内容生成 (`content-gen`)

给定主题和目标平台，生成一篇可直接复制发布的平台原生内容。

```bash
/cn-content-matrix content-gen 春季护肤攻略 xhs
```

**执行流程：**
1. **主题调研** — 通过 WebSearch 获取最新趋势、热搜关键词、竞品切入点
2. **加载平台规范** — 读取对应平台的完整创作规范和敏感词库
3. **风格迁移生成** — 以该平台 KOL 的身份和语气撰写内容
4. **自查自纠** — 字数、格式、语气、敏感词、原创性、可发布性六项检查
5. **输出文件** — 带 YAML frontmatter 的 Markdown 文件，可直接复制发布

**平台代号对照：**
| 代号 | 平台 | 默认 |
|------|------|------|
| `xhs` | 小红书 | ✅（未指定平台时默认） |
| `wechat` | 微信公众号 | |
| `douyin` | 抖音 | |
| `bilibili` / `bili` | B站专栏 | |

#### 2. 全平台矩阵生成 (`content-matrix`)

一个主题，同时生成四个平台的差异化内容。这是本工具的核心功能。

```bash
/cn-content-matrix content-matrix 2026年AI编程趋势
```

**执行流程：**
1. **构建内容核心（Content Core）** — 提炼核心论点、关键数据、受众画像、情绪基调、关键词集
2. **主题调研** — 多维度 WebSearch 获取最新信息
3. **按序生成四平台内容：**
   - 微信公众号（最深度，先生成作为素材库）
   - B站专栏（次深度，复用分析但调整语气）
   - 小红书（从深度内容提炼种草点）
   - 抖音脚本（提炼最抓眼球的信息）
4. **差异化检查** — 确保各平台开头不同、论证结构不同、无大段重复（>50字连续相同=不合格）、CTA适配平台
5. **生成内容一览表** — 四平台横向对比 + 发布时间建议

**输出目录结构：**
```
~/content-output/2026-03-21/ai编程趋势/matrix/
├── content-core.md    # 内容核心（所有平台的共同基础）
├── wechat.md          # 微信公众号版本
├── bilibili.md        # B站专栏版本
├── xhs.md             # 小红书版本
├── douyin.md          # 抖音脚本版本
└── overview.md        # 内容一览表（四平台对比 + 发布建议）
```

#### 3. 内容合规审查 (`content-review`)

对已有内容进行平台合规性审查，60分满分制，6个维度各10分。

```bash
/cn-content-matrix content-review xhs ./my-xiaohongshu-draft.md
```

**六维评分体系：**

| 维度 | 检查内容 | 满分 |
|------|---------|------|
| 字数 | 是否在平台规范范围内 | 10 |
| 格式结构 | 标题格式、段落结构、平台特有元素（emoji/hashtag/时间轴等） | 10 |
| 语气匹配 | 是否符合平台调性，有无"串台"现象 | 10 |
| 敏感词 | 三级敏感词扫描（🔴🟡🟢） | 10 |
| SEO友好度 | 关键词密度2%-5%、标题含核心词、hashtag相关性 | 10 |
| 可发布性 | 是否可直接复制发布、有无残留占位符 | 10 |

**及格线：36/60。** FAIL 结果会自动生成 `fix-suggestions-{platform}.md`，包含所有🔴级问题的具体修改文本。

### 敏感词检测详解

三级分类系统，基于《广告法》及各平台最新规则：

**🔴 硬违禁（必须删除或替换）：**
- 绝对化用语：最好、最佳、最强、最大、最低价、唯一、100%、绝对
- 虚假宣传：根治、治愈、月瘦X斤、稳赚不赔、日入过万
- 引流违禁：微信号、vx、wx、加我、私我、淘口令
- 各平台特有违禁词（如小红书禁"链接在评论区"，抖音禁"赚钱/搞钱"）

**🟡 软限制（可能触发限流）：**
- 平台特定的营销敏感词
- 擦边表述

**🟢 注意（视语境处理）：**
- 在特定上下文可能产生歧义的词汇

每个违禁词都提供了**替代表达**（例如："最好" → "很不错"，"100%" → "大概率"）。

### 命令行合规检查工具

除了 AI 驱动的 `content-review` 命令，还提供了一个 shell 脚本用于快速自动化检查：

```bash
# 用法
./scripts/content-check.sh <文件路径> <平台代号>

# 示例
./scripts/content-check.sh ~/content-output/2026-03-21/coffee/xhs.md xhs
```

检查项目：字数范围、硬违禁词扫描、Emoji 密度（小红书要求5-20个）、段落长度。

退出码：`0` = 通过，`1` = 警告，`2` = 不通过。可集成到 CI/CD 或发布前自动检查流程。

### 反 AI 味机制

以下表达在任何平台都被禁止使用：

> "在当今社会"、"随着科技的发展"、"众所周知"、"值得注意的是"、"不可否认"、"总而言之"、"让我们一起来看看"、过于工整的排比句、每段都差不多长的"均匀体"

**替代原则：** 用该平台真实用户会用的表达。宁可口语化到略显粗糙，也不要光滑到像 AI。

### 安装方式

将 `cn-content-matrix` 目录放入你的 Claude Code skill 目录即可：

```bash
# 克隆仓库
git clone <repo-url>

# 将 skill 目录复制或链接到你的 skills 目录
cp -r cn-content-matrix /path/to/your/skills/

# 验证安装
# 在 Claude Code 中输入：
/cn-content-matrix content-gen 测试主题 xhs
```

### 各平台规范文件说明

| 文件 | 内容覆盖 | 更新频率 |
|------|---------|---------|
| `references/xiaohongshu.md` | 标题公式（6种）、正文结构、emoji/hashtag规范、互动引导、算法偏好 | 季度更新 |
| `references/wechat-mp.md` | 标题策略、长文结构、搜一搜SEO优化、订阅vs推荐流量 | 季度更新 |
| `references/douyin.md` | 7种钩子公式（前3秒生死线）、脚本格式、画面标注、节奏控制 | 季度更新 |
| `references/bilibili.md` | 富文本格式（代码块/表格）、社区文化（弹幕/梗）、技术内容标题策略 | 季度更新 |
| `references/sensitive-words.md` | 三级敏感词库 + 替代表达建议 | 持续更新 |
| `references/content-core-template.md` | 内容核心模板（论点/数据/受众/情绪/关键词） | 稳定 |
