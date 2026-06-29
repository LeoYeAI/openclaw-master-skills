# xianyu-service-ops — 闲鱼服务类目运营技能

A Claude Code skill for selling virtual/service-based offerings on 闲鱼 (Xianyu), Alibaba's second-hand marketplace. Covers the full operational stack from listing creation to traffic growth.

> 这是一个 Claude Code skill，帮助卖家在闲鱼平台从 0 开始做服务类目，覆盖选词、上架、定价、诊断、竞品分析等完整运营链路。

---

## What it does

The skill activates whenever you mention Xianyu-related topics and switches into one of four operational modes based on what you need:

| Mode | When to use | What you get |
|------|-------------|--------------|
| **新品上架** | Listing a new service | 3 title variants · pricing recommendation · package structure · detail page copy framework · main image brief |
| **商品优化** | Low traffic or low conversion | Funnel diagnosis (where is it breaking?) · revised titles · specific fixes |
| **账号运营** | Account health and traffic growth | Cold-start roadmap · daily ops rhythm · cross-platform funnel |
| **竞品分析** | Analyzing a competitor's listing | Competitor profile · differentiation opportunities · actionable adjustments |

Outputs are designed to be **copied directly into Xianyu** — no second-pass editing needed.

---

## Algorithm claims are evidence-graded

All platform mechanism claims in this skill are sourced from Xianyu's official technical articles and algorithm disclosure documents, not operator folklore. Each claim carries a grade:

- 🔵 Official docs / official tech team publications
- 🟢 Empirical with data
- 🟡 Multi-person consensus, no hard data
- 🔴 Unverified / contradicted by available evidence

Common claims that are **not supported** by official sources include: video thumbnail traffic boost, "edit = new item boost", the 40/30/20/10 weight breakdown, and specific Zhima Credit thresholds. These are marked 🔴 and the skill does not recommend building strategy around them.

---

## Installation

### Claude Code

```bash
# From your project root, or wherever you keep skills:
git clone <this-repo-url>
# Then point Claude Code at the skill directory:
# Settings → Skills → Add → path/to/xianyu-service-ops
```

Or if you're using a `.skill` package file, drag it into Claude Code's skill panel.

### Manual

Copy the `xianyu-service-ops/` folder to your Claude Code skills directory and restart.

---

## File structure

```
xianyu-service-ops/
├── SKILL.md                    # Main skill instructions (loads automatically)
├── README.md                   # This file
├── references/
│   ├── xianyu-seo.md           # Platform algorithm mechanics (evidence-graded)
│   ├── price-benchmarks.md     # Service category price ranges by type
│   └── compliance-rules.md     # Violation types, penalties, edge case Q&A
└── evals/
    └── evals.json              # Test cases for skill evaluation
```

**`references/` files** are loaded on demand — SKILL.md tells Claude when to consult each one. They don't inflate your context window on every invocation.

---

## Companion skills (optional)

The skill mentions four companion skills that extend its capabilities when installed:

| Skill | Purpose |
|-------|---------|
| `copywriting` | Deep-polish detail page copy (beyond the framework the skill produces) |
| `content-strategy` | Plan Xiaohongshu / Douyin content matrix to drive Xianyu traffic |
| `pricing-strategy` | Complex package design, Van Westendorp analysis |
| `seo-audit` | SEO for external landing pages (not Xianyu in-platform search) |

These are **optional**. The skill works standalone — it will simply note when a companion skill would add value and describe what that skill would do.

---

## Context persistence (optional)

Create `.claude/xianyu-context.md` in your project to save your account state. The skill reads this file at the start of each session and skips re-asking questions it already knows the answers to. Example:

```markdown
# 我的闲鱼账号状态
- 服务类目：简历优化
- 账号状态：全新账号，0 评价
- 当前商品数：0
- 目标：先跑量，前 10 单快速拿评价
```

---

## License

MIT — free to use, modify, and redistribute. Attribution appreciated but not required.

---

## Research sources

The algorithm reference file (`references/xianyu-seo.md`) is based on:
- 《闲鱼社区算法原理及数据处理情况说明》(algorithm disclosure document)
- 闲鱼搜索相关性技术解读 (official tech article on search relevance)
- 《详解闲鱼推荐系统》(official tech article on recommendation system)
- 闲鱼用户服务协议 2025 版 (terms of service, AI features section)
- Xianyu 2025 annual recap reports (AI adoption metrics)
