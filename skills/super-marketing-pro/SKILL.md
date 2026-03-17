---
name: super-marketing-pro
description: >
  Full-stack B2B marketing execution skill equivalent to a 10-person agency team.
  Use for: building ICP and brand messaging, generating multi-platform content matrices,
  writing cold email sequences, SEO topic cluster strategy, competitor battle cards,
  content repurposing (1 long-form → LinkedIn/X/TikTok/Xiaohongshu), and monthly/quarterly
  marketing reports. Covers Chinese platforms (抖音, 小红书, 微信) and Western platforms
  (LinkedIn, YouTube, Instagram, X). Triggers on: marketing strategy, social media content,
  SEO analysis, competitor research, email sequence, content calendar, hashtag, ICP,
  营销策略, 社媒内容, 竞品分析, 内容日历, 邮件序列.
---

# Super Marketing Pro

Full-stack B2B marketing skill. Always run `strategy_builder.py` first to define ICP before generating any content.

## Golden Rule: Strategy First

Never generate copy without an ICP. The workflow is always:
**ICP → Content → Repurpose → Distribute → Monitor → Report**

## Scripts

All scripts are in `scripts/`. Run with `python3`. Requires `openai` package (`pip3 install openai`).

| Script | Function | Key Args |
|--------|----------|----------|
| `strategy_builder.py` | Generate ICP, messaging framework, elevator pitch | `--industry` `--product` |
| `content_repurposer.py` | 1 long-form doc → multi-platform content matrix | `--source <file.md>` `--platforms` |
| `hashtag_generator.py` | Platform-specific hashtag matrix | `--content` `--platforms "linkedin,douyin,xiaohongshu"` |
| `content_calendar.py` | Weekly/monthly publishing schedule | `--months` `--output <file.csv>` |
| `email_sequence_generator.py` | 5-stage cold email sequence | `--target` `--stages` |
| `seo_analyzer.py` | LLM-powered Topic Cluster strategy | `--seed-keyword` `--depth deep` |
| `competitor_monitor.py` | Batch competitor battle cards | `--batch-list <file.txt>` `--export-format json` |
| `data_reporter.py` | Multi-month cross-platform ROI report | `--type monthly` `--months 1,2,3` |
| `llm_utils.py` | Shared LLM utility (auto-imported) | — |

`llm_utils.py` uses `OPENAI_API_KEY` env var. Default model: `gemini-3.0-flash`. Includes exponential backoff retry (3 attempts).

## Execution Workflow

**Stage 1 — Strategy**: Run `strategy_builder.py` → get ICP, buyer personas, messaging pillars.

**Stage 2 — Content Creation**: Based on goal:
- Awareness/SEO: Run `seo_analyzer.py` → write long-form pillar content.
- Lead Gen: Read `references/content_templates.md` → write whitepaper or case study.
- Outbound: Run `email_sequence_generator.py`.

**Stage 3 — Repurpose**: Run `content_repurposer.py` on any long-form asset → get LinkedIn post, X thread, TikTok/Douyin script, Xiaohongshu note.

**Stage 4 — Distribute**: Run `hashtag_generator.py` for tags, then `content_calendar.py` for scheduling.

**Stage 5 — Convert**: Run `email_sequence_generator.py` for lead nurturing sequences.

**Stage 6 — Monitor & Report**: Run `competitor_monitor.py` for battle cards, `data_reporter.py` for attribution reports.

## Knowledge Base (References)

Load the relevant reference file before executing platform-specific tasks:

**Strategy**: `abm_framework.md` (ABM + sales alignment), `messaging_icp_guide.md` (ICP workshop), `funnel_strategy.md` (TOFU/MOFU/BOFU + attribution)

**Channels**: `linkedin_guide.md`, `youtube_seo.md`, `douyin_algorithm.md`, `xiaohongshu_tips.md`

**Content**: `content_templates.md` (whitepapers, case studies, emails), `keyword_library.md` (B2B keyword matrix)
