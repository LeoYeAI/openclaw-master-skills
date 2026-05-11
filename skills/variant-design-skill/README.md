# variant-design

[English](#english) | [中文](#中文)

---

<a id="english"></a>

> Solve the blank canvas problem. Prompt → 3 fully-formed distinct designs → vary → export.

A Claude Code skill inspired by the [Variant](https://variant.com) design community, powered by the **Impeccable design system**. Give it a prompt, get three divergent design directions — each from a different studio's aesthetic — then iterate with one-word actions.

---

## What it does

1. **Detects your scenario** — dashboard, SaaS landing page, editorial, e-commerce, mobile app, creative tool, education
2. **Loads design system references** — typography, color theory (OKLCH), spatial design, motion, interaction, responsive, UX writing
3. **Generates 3 distinct variations** — each pulls from a different aesthetic direction (Minimal/Editorial, Bold/Expressive, Dark/Premium, Warm/Human, Neo-brutalist, Luxury/Silence…)
4. **Runs an AI Slop Test** — quality gate that catches generic AI aesthetic fingerprints before presenting
5. **Ships working code** — HTML single-file by default, or React. Real content, no lorem ipsum
6. **Offers variation actions** — push further, polish, critique, swap styles, remix colors, shuffle layouts, see other views

---

## Installation

### Claude Code (recommended)

```bash
claude skill install https://github.com/YuqingNicole/variant-design-skill
```

Or add manually to your project's `SKILL.md` — copy the contents of [`SKILL.md`](./SKILL.md) into your existing skill file.

### Other Claude interfaces

**Claude.ai (web/desktop):** Paste the contents of `SKILL.md` into a Project's custom instructions, or drop it at the top of a conversation as a system prompt.

**API / custom integrations:** Include `SKILL.md` as a system message before your user turn.

---

## Usage

### Basic triggers

The simplest way — just describe what you want:

```
design a dashboard for a crypto trading terminal
show me 3 directions for a SaaS landing page
give me UI options for a wellness app
```

### Directed triggers — lock in a style or reference a site

You can be more specific by naming an aesthetic direction, a palette, or even an existing site you want to match:

```
developer tools homepage, code-first hero with CLI snippet, dark Data/Technical direction

landing page for an AI agent tool — Dark Indigo palette, Geist font, Code-First layout from saas.md

3 variations for a food delivery app — one Warm/Human, one Bold/Expressive, one Neo-brutalist

reproduce the visual style of [site you described] — dark navy, monospace, swim lane diagrams
```

**Tip:** the more constraints you name (direction + palette + layout pattern), the more targeted the output. The more open the prompt, the more divergent the three variations will be.

### Anatomy of a directed prompt

```
[what it is] + [domain] + [aesthetic direction or palette] + [layout hint] + [any signature detail]
```

Examples:

| Goal | Prompt |
|---|---|
| Match a specific site's vibe | `"developer tool landing page — dark Data/Technical, CLI code hero, Dark Indigo palette"` |
| Explore freely | `"landing page for a mindfulness app"` |
| One fixed + two free | `"3 directions for a finance dashboard — one must be Amber Finance dark terminal"` |
| Multi-screen flow | `"3-screen onboarding flow for a meditation app, Wellness Soft palette"` |

### Variation actions

After seeing the initial 3 variations, iterate with:

| Action | What happens |
|---|---|
| **Vary strong** | Push current direction to its extreme |
| **Vary subtle** | Polish and refine, same aesthetic |
| **Distill** | Strip to essence — remove everything non-essential |
| **Change style** | Keep layout, swap entire visual language |
| **Remix colors** | 3 alternative palettes using OKLCH: analogous / complementary / unexpected |
| **Shuffle layout** | Same content + style, different composition |
| **Polish** | Refine against design system: typography, spacing, interactions, motion, copy |
| **Critique** | Systematic audit against all 8 design system dimensions |
| **Extract tokens** | Export design tokens as CSS / JSON / Tailwind config |
| **See other views** | Mobile / dark mode / empty state / onboarding / hover states |

---

## Reference library

### Domain references
Scenario-specific materials (starter prompts, palettes, typography, layouts, real community examples):

| File | Domain |
|---|---|
| `references/dashboard.md` | Data dashboards, analytics, monitoring, trading terminals |
| `references/editorial.md` | Magazines, journalism, long-form, news |
| `references/saas.md` | SaaS landing pages, B2B, developer tools |
| `references/ecommerce.md` | E-commerce, consumer apps, fintech cards |
| `references/education.md` | Learning apps, quizzes, language tools |
| `references/creative.md` | Generative art, music tools, creative software |
| `references/mobile.md` | iOS/Android apps, onboarding, home screens |
| `references/palettes.md` | Universal palette library — 27 palettes × 7 aesthetic directions |

### Design system references (Impeccable)
Foundational design principles loaded for every generation:

| File | Covers |
|---|---|
| `references/design-system/typography.md` | Modular scale, fluid type, font pairing, OpenType features, vertical rhythm |
| `references/design-system/color-and-contrast.md` | OKLCH color space, tinted neutrals, 60-30-10 rule, dark mode, WCAG contrast |
| `references/design-system/spatial-design.md` | 4pt grid, container queries, squint test, hierarchy through multiple dimensions |
| `references/design-system/motion-design.md` | 100/300/500 rule, ease-out-expo, stagger, reduced motion, perceived performance |
| `references/design-system/interaction-design.md` | 8 interactive states, focus-visible, forms, modals, keyboard navigation |
| `references/design-system/responsive-design.md` | Mobile-first, content-driven breakpoints, input detection, safe areas |
| `references/design-system/ux-writing.md` | Button labels, error formulas, empty states, voice vs tone, accessibility |

---

## Design principles

- **Real content wins.** Plausible headlines, real data, actual copy. Makes designs feel alive.
- **Commit fully.** Half-executed aesthetics look worse than simple ones.
- **Never converge.** If A is dark, B cannot also be dark. Each must feel like a different studio.
- **Typography first.** Distinctive display font + reliable body. Never Inter, Roboto, Arial, system-ui.
- **Color = one bold OKLCH choice.** One dominant color used with conviction beats five timid colors. Always tint neutrals.
- **No AI slop.** No purple gradients, no glassmorphism, no bounce easing, no centered-everything layouts.

---

## Contributing

PRs welcome. Each domain reference file follows a consistent 6-section schema:

1. Starter Prompts (domain-grouped)
2. Color Palettes (CSS custom properties)
3. Typography Pairings
4. Layout Patterns
5. Signature Details
6. Real Community Examples

Design system references follow the Impeccable style structure with principles, code examples, and anti-patterns.

---

Built with [Claude Code Skills](https://claude.ai/code). Design system powered by [Impeccable](https://github.com/tychografie/impeccable).

---

<a id="中文"></a>

# variant-design（中文版）

> 解决空白画布问题。提示词 → 3 个完整的差异化设计 → 迭代 → 导出。

一个受 [Variant](https://variant.com) 设计社区启发的 Claude Code 技能，内置 **Impeccable 设计系统**。输入一个提示词，获得三个截然不同的设计方向——每个来自不同工作室的审美——然后用一个词迭代。

---

## 功能概览

1. **场景检测** — 仪表盘、SaaS 落地页、编辑/杂志、电商、移动应用、创意工具、教育
2. **加载设计系统参考** — 排版、色彩理论（OKLCH）、空间设计、动效、交互、响应式、UX 文案
3. **生成 3 个差异化变体** — 每个采用不同的审美方向（极简/编辑、大胆/表现、暗色/高端、温暖/人文、新粗野主义、奢华/留白……）
4. **AI 审美质量门** — 自动检测并过滤常见的 AI 生成审美特征
5. **输出可用代码** — 默认 HTML 单文件，或 React。真实内容，没有占位文本
6. **提供迭代操作** — 推到极致、精修、批评、换风格、重混色彩、重排布局、查看其他视图

---

## 安装

### Claude Code（推荐）

```bash
claude skill install https://github.com/YuqingNicole/variant-design-skill
```

或手动添加到项目的 `SKILL.md` 中——复制 [`SKILL.md`](./SKILL.md) 的内容。

### 其他 Claude 界面

**Claude.ai（网页/桌面）：** 将 `SKILL.md` 内容粘贴到 Project 的自定义指令中，或在对话开头作为系统提示词。

**API / 自定义集成：** 将 `SKILL.md` 作为系统消息放在用户消息之前。

---

## 使用方法

### 基础触发

最简单的方式——描述你想要什么：

```
设计一个加密货币交易终端的仪表盘
给我一个 SaaS 落地页的 3 个方向
给我一个健康应用的 UI 选项
```

### 定向触发——锁定风格或参考某个网站

你可以更具体地指定审美方向、色板或想要匹配的现有网站：

```
开发者工具首页，代码优先的 hero 区域带 CLI 片段，暗色 Data/Technical 方向

AI agent 工具的落地页 — Dark Indigo 色板，Geist 字体，saas.md 中的 Code-First 布局

外卖应用的 3 个变体 — 一个 Warm/Human，一个 Bold/Expressive，一个 Neo-brutalist

重现 [你描述的网站] 的视觉风格 — 深海军蓝，等宽字体，泳道图
```

**提示：** 你给出的约束越多（方向 + 色板 + 布局模式），输出越精准。提示词越开放，三个变体的差异越大。

### 定向提示词结构

```
[是什么] + [领域] + [审美方向或色板] + [布局提示] + [签名细节]
```

示例：

| 目标 | 提示词 |
|---|---|
| 匹配某网站的感觉 | `"开发者工具落地页 — 暗色 Data/Technical，CLI 代码 hero，Dark Indigo 色板"` |
| 自由探索 | `"冥想应用的落地页"` |
| 一个固定 + 两个自由 | `"金融仪表盘的 3 个方向 — 其中一个必须是 Amber Finance 暗色终端"` |
| 多屏流程 | `"冥想应用的 3 屏引导流程，Wellness Soft 色板"` |

### 迭代操作

看到初始 3 个变体后，用以下操作迭代：

| 操作 | 效果 |
|---|---|
| **Vary strong**（推到极致） | 将当前方向推到最大化 |
| **Vary subtle**（精细调整） | 精修打磨，保持同一审美 |
| **Distill**（蒸馏精简） | 去除一切非必要元素，露出设计本质 |
| **Change style**（换风格） | 保持布局，替换整体视觉语言 |
| **Remix colors**（重混色彩） | 用 OKLCH 生成 3 个替代色板：类似 / 互补 / 意想不到 |
| **Shuffle layout**（重排布局） | 相同内容和风格，不同构图 |
| **Polish**（精修） | 对照设计系统精修：排版、间距、交互、动效、文案 |
| **Critique**（批评） | 对照全部 8 个设计系统维度的系统审计 |
| **Extract tokens**（提取 Token） | 导出设计令牌为 CSS / JSON / Tailwind 配置 |
| **See other views**（其他视图） | 移动端 / 暗色模式 / 空状态 / 引导流程 / 悬停状态 |

---

## 参考库

### 领域参考
场景专用素材（启动提示词、色板、排版、布局、真实社区案例）：

| 文件 | 领域 |
|---|---|
| `references/dashboard.md` | 数据仪表盘、分析、监控、交易终端 |
| `references/editorial.md` | 杂志、新闻、长篇、报道 |
| `references/saas.md` | SaaS 落地页、B2B、开发者工具 |
| `references/ecommerce.md` | 电商、消费类应用、金融科技卡片 |
| `references/education.md` | 学习应用、测验、语言工具 |
| `references/creative.md` | 生成艺术、音乐工具、创意软件 |
| `references/mobile.md` | iOS/Android 应用、引导流程、主屏 |
| `references/palettes.md` | 通用色板库 — 27 个色板 × 7 个审美方向 |

### 设计系统参考（Impeccable）
每次生成都会加载的基础设计原则：

| 文件 | 涵盖内容 |
|---|---|
| `references/design-system/typography.md` | 模块化字阶、流体排版、字体配对、OpenType 特性、垂直韵律 |
| `references/design-system/color-and-contrast.md` | OKLCH 色彩空间、染色中性灰、60-30-10 法则、暗色模式、WCAG 对比度 |
| `references/design-system/spatial-design.md` | 4pt 网格、容器查询、眯眼测试、多维层级 |
| `references/design-system/motion-design.md` | 100/300/500 规则、ease-out-expo、错开动画、减弱动效、感知性能 |
| `references/design-system/interaction-design.md` | 8 种交互状态、focus-visible、表单、模态框、键盘导航 |
| `references/design-system/responsive-design.md` | 移动优先、内容驱动断点、输入方式检测、安全区域 |
| `references/design-system/ux-writing.md` | 按钮标签、错误消息公式、空状态、语气与语调、无障碍 |

---

## 设计原则

- **真实内容为王。** 可信的标题、真实的数据、实际的文案。让设计有生命力。
- **全力以赴。** 半吊子的审美比简单的更糟糕。
- **永不趋同。** 如果 A 是暗色，B 就不能也是暗色。每个变体必须像来自不同工作室。
- **排版优先。** 独特的展示字体 + 可靠的正文字体。禁用 Inter、Roboto、Arial、system-ui。
- **色彩 = 一个大胆的 OKLCH 选择。** 一个果断使用的主色胜过五个犹豫不决的颜色。始终给中性灰染色。
- **拒绝 AI 审美。** 不要紫色渐变、不要毛玻璃效果、不要弹跳缓动、不要居中一切的布局。

---

## 贡献

欢迎 PR。每个领域参考文件遵循统一的 6 部分结构：

1. 启动提示词（按领域分组）
2. 色板（CSS 自定义属性）
3. 排版配对
4. 布局模式
5. 签名细节
6. 真实社区案例

设计系统参考遵循 Impeccable 风格结构，包含原则、代码示例和反模式。

---

基于 [Claude Code Skills](https://claude.ai/code) 构建。设计系统由 [Impeccable](https://github.com/tychografie/impeccable) 驱动。
