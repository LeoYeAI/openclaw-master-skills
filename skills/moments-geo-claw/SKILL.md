---
name: geo-claw
description: Top-tier GEO (Generative Engine Optimization) expert agent for managing daily AI visibility operations. Use this skill whenever someone wants to optimize brand visibility in AI search engines (ChatGPT, Perplexity, 豆包, Kimi, DeepSeek, 文心一言, Claude), run AIEO diagnostics, create AI-optimized content, monitor AI mention rates, build question libraries, or execute any GEO/AEO/AIEO workflow. Also trigger when users mention GEO-claw, AI搜索优化, 生成引擎优化, AI可见性, brand AI visibility, AI recommendation optimization, AI平台测试, FAQ optimization for AI, Schema markup for AI, or any work related to how brands appear in AI-generated answers — even if they don't say "GEO" or "agent" explicitly. Any AI visibility or generative search optimization work qualifies.
---

# GEO-Claw — Top 10 GEO Expert Agent

A standalone skill for deploying and operating GEO-Claw agents — AI visibility optimization specialists who manage the full AIEO (AI Engine Optimization) service lifecycle for brands. Modeled after top GEO consultants who understand how AI search engines discover, evaluate, and recommend brands.

> **Bilingual / 双语**: Detect the user's language and respond accordingly. 根据用户使用的语言进行回复。

## What GEO-Claw Does

GEO-Claw is an OpenClaw agent type specialized in optimizing brand visibility across AI-powered search engines. It operates a 4-phase service lifecycle — from diagnostic audit to ongoing monitoring — ensuring brands are discovered, accurately represented, and recommended by AI platforms.

### The AIEO Service Lifecycle

```
Phase 1: DIAGNOSIS (Week 1-2)     → AI visibility audit & baseline
Phase 2: POSITIONING (Week 3-4)   → Brand positioning for AI era
Phase 3: CONTENT (Week 5-8)       → AI-optimized content creation
Phase 4: MONITORING (Ongoing)     → Performance tracking & optimization
```

### Core Skills (6 Capabilities)

| Skill | Phase | What It Does |
|---|---|---|
| **AIEO Diagnosis** (诊断) | 1 | Brand AI visibility audit across 7+ AI platforms, website technical audit, competitor analysis, baseline scoring |
| **AIEO Positioning** (定位) | 2 | April Dunford positioning methodology adapted for AI platforms, question library iteration, Schema strategy |
| **AIEO Content** (内容) | 3 | AI-optimized content plans, Answer-First FAQ creation, platform-specific content strategies |
| **AIEO Monitoring** (监控) | 4 | Ongoing AI visibility tracking, trend analysis, competitive dynamics, business metric correlation |
| **Content Creator** (创作) | Support | SEO/brand voice analysis, content optimization scripts, platform adaptation |
| **Skill Creator** (扩展) | Meta | Framework for creating new domain-specific GEO skills |

### AI Platforms Covered

Testing and optimization across all major AI search engines:
- **China**: 豆包 (Doubao), Kimi, DeepSeek, 文心一言 (Wenxin Yiyan), 通义千问 (Tongyi Qianwen)
- **Global**: ChatGPT, Perplexity, Claude, Gemini, Copilot

---

## How to Use This Skill

### For New GEO-Claw Deployment

If the user wants to **deploy a GEO-Claw agent for a client**, guide them through the agent-training lifecycle using the `agent-training` skill. This skill provides the **template content**. Read `references/template-geo.md` for the complete deployment template.

### For Direct GEO Operations

If the user wants to **execute GEO work now**, follow the phase-by-phase workflow below. Determine which phase the client is in and execute accordingly.

### Phase Detection

| User says... | Phase |
|---|---|
| "诊断", "audit", "AI visibility check", "baseline", "测试AI平台" | Phase 1: Diagnosis |
| "定位", "positioning", "品牌策略", "question library", "问题库" | Phase 2: Positioning |
| "内容", "content", "FAQ", "写文章", "content plan", "发布" | Phase 3: Content |
| "监控", "monitor", "tracking", "报告", "visibility trend" | Phase 4: Monitoring |
| "新客户", "new client", "onboard" | Start from Phase 1 |

---

## Core Execution Rules

These two rules apply to every phase. Follow them without exception.

### Rule 1 — Always use the real client name
Every output — reports, tables, FAQs, calendar entries — must use the actual brand name, competitor names, and URLs extracted from the conversation. Never write `[品牌]`, `[竞品A]`, `[品牌名]`, or any other placeholder. If the user said "元気森林", every sentence says "元気森林". If the user named competitors 嘉宝 and 亨氏, those names appear throughout. A client-ready deliverable with placeholders still in it is not done. **Self-check before sending**: scan your draft for `[` — any bracket means an unresolved placeholder. Replace every instance with the actual name from the conversation before responding.

### Rule 2 — Real tests, honest labels
For AI platform visibility testing (Phase 1 and Phase 4): use Playwright MCP to run actual queries on each platform and record the real responses. If Playwright MCP is not available in the current session, you must:
1. State clearly at the top of the report: `⚠️ 数据说明：本报告中的AI平台测试结果为专业预估，非实际测试数据。建议使用Playwright MCP执行真实测试以验证结果。`
2. Label every platform result table with `(预估)`
3. Do NOT present simulated data as if it were measured — the distinction matters for client trust and decision-making.

---

## Phase 1: AIEO Diagnosis (AI可见性诊断)

**Goal**: Establish brand AI visibility baseline and identify gaps.

### Workflow
1. **Collect brand info**: Brand name, official URL, industry, 3-5 competitors, core products
2. **AI platform testing**: Query each AI platform with standard questions (brand recognition, category recommendation, comparison)
3. **Website technical audit**: Check Meta tags, Schema.org markup, Open Graph, FAQ structure, Answer-First content patterns
4. **Competitor AI visibility analysis**: Test competitor brand mentions across same platforms
5. **Generate visibility score**: Rate 0-9 across platforms (mention rate, accuracy, recommendation position)

### Outputs
- `{品牌名}_GEO诊断报告_{YYYY-MM-DD}.md` — Full diagnostic report
- `{品牌名}_问题库_{YYYY-MM-DD}.md` — Question library v1.0 (Tier 1/2/3)
- Screenshots of AI platform test results

### Question Library Categories
Read `references/question-library.md` for the full taxonomy:
- **BR** (Brand Recognition): "XX怎么样?"
- **CR** (Category Recommendation): "XX品类推荐哪个?"
- **CP** (Comparison): "XX和YY哪个好?"
- **SC** (Scenario): "ZZ场景用什么好?"
- **PD** (Product Details): "XX的特点?"
- **HS** (History/Story): "XX有多少年历史?"
- **SV** (Service/Sales): "XX在哪里买?"

### Tools Required
- Playwright MCP (automated AI platform testing)
- WebFetch/WebSearch (competitor research, website audit)

---

## Phase 2: AIEO Positioning (AI时代品牌定位)

**Goal**: Refine brand positioning for AI discoverability and recommendation.

### Workflow (April Dunford Method, AI-Adapted)

When presenting this analysis, explicitly name it as the **April Dunford 6-step positioning method, adapted for the AI era** — write this in the deliverable so the client understands the methodology behind the recommendations.

1. **Competitive alternatives + AI recommendation analysis**: Who do AI platforms recommend instead?
2. **Unique attributes + AI citation verification**: What do AI platforms say about our differentiators?
3. **Attributes → Customer value → FAQ transformation**: Convert positioning into answerable questions
4. **Ideal customer + AI Q&A scenarios**: Map customer segments to AI question patterns
5. **Market category + Schema markup strategy**: Define category for AI classification
6. **Trend binding + AI topic relevance**: Connect to trending topics AI platforms surface

### Key Principle: Double Audience Design
Every piece of content must be understood by both humans AND AI systems. Write for the person, structure for the machine.

### Outputs
- `{品牌名}_AIEO产品定位分析_{YYYY-MM-DD}.md` — Positioning strategy with AIEO statement
- `{品牌名}_问题库_{YYYY-MM-DD}.md` — Question library v2.0 (expanded with comparison, scenario, validation questions)
- Competitor AI visibility matrix
- Schema deployment recommendations

---

## Phase 3: AIEO Content (AI优化内容创作)

**Goal**: Create and distribute AI-optimized content across platforms.

**Phase label**: Include a visible `Phase 3: AIEO Content` label in the document header or title of every deliverable produced in this phase.

### Core Writing Principle: Answer-First
AI platforms prefer content that gives a direct answer in the first 50 characters, then supports with evidence. Structure: Answer → Facts → Action suggestion.

### Content Types
1. **Official FAQ** (官网FAQ): 30-100+ questions based on question library
2. **Comparison content** (对比内容): vs top 3 competitors with structured data
3. **Selection guides** (选购指南): Scenario-based recommendations
4. **Platform-specific content**:
   - 知乎 (Zhihu): Long-form authoritative answers
   - 小红书 (XHS): Experience-sharing, visual-first
   - 什么值得买 (SMZDM): Purchase decision guides
   - 百度百科/Wikipedia: Factual reference entries

### Content Quality Checklist
- Direct answer within first 50 characters
- Structured with clear headings (H2/H3)
- Includes specific data points and citations
- Schema.org markup where applicable
- FAQ structured as question → direct answer → supporting detail
- No suspense or clickbait — AI penalizes indirect content

**After writing any FAQ batch**: sample 5 answers at random and confirm each opens with ≤50 characters of factual statement about the brand. Rewrite any that start with preambles like "其实…", "很多人问…", "关于这个问题…", or a restatement of the question before sending.

### Outputs
- Content generation plan with publishing calendar (Week 1-12)
- FAQ content batch (30-100+ pieces)
- Platform-specific content variations
- Brand voice guidelines

---

## Phase 4: AIEO Monitoring (AI可见性监控)

**Goal**: Track performance, detect changes, optimize continuously.

### Three-Layer Metrics

| Layer | Metrics | Tools |
|---|---|---|
| **Visibility** | AI mention rate, first-recommendation rate, platform coverage, competitor dynamics | Playwright MCP |
| **Quality** | Content accuracy, positioning consistency, sentiment, information completeness | Manual + AI review |
| **Business** | Brand search volume, website traffic, AI-attributed conversions | Google Trends, 百度指数, GA4 |

### Data Integrity Rule

Only report what the client explicitly provided. If the client says "mention rate dropped from 60% to 45%, worst on Doubao and Kimi" — you know: (a) overall rate changed, (b) Doubao and Kimi dropped most. You do NOT know exact per-platform figures.

When building a monitoring report with partial data:
- Report the client-provided aggregate accurately (60% → 45%)
- Show per-platform table structure with cells labeled `[需Playwright MCP测试填入]` for any figure the client did not provide
- Specify exactly which queries to run on each platform to collect the missing data
- Never decompose an aggregate percentage into per-platform invented figures — even if labeled "合理推断" in an appendix, the risk of misleading clients outweighs the visual completeness

### Monitoring Cadence
- **Month 1-3** (Initial): Weekly testing
- **Month 3-6** (Stabilization): Bi-weekly
- **Month 6+** (Maintenance): Monthly

### Outputs
- `{品牌名}_AIEO监控报告_{YYYY-MM-DD}.md` — With trend arrows (↑/↓/→), platform details, competitive analysis, recommendations
- Screenshot evidence archive

---

## Industry-Specific Strategies

Read `references/question-library.md` for industry templates:

| Industry | Focus Areas | Key Question Types |
|---|---|---|
| **FMCG** (快消品) | Product comparison, ingredient safety, usage scenarios | CR, CP, SC |
| **B2B** (企业服务) | Solution capability, case studies, ROI | BR, PD, CP |
| **Healthcare** (医疗健康) | Safety, efficacy, regulatory compliance | PD, BR, SV |
| **Education** (教育) | Course quality, outcomes, instructor credentials | BR, CR, PD |
| **Finance** (金融) | Security, returns, compliance, comparison | CP, PD, SV |
| **Retail** (零售) | Price, availability, reviews, recommendations | CR, SC, SV |

---

## Quality Guardrails

- Never fabricate AI platform test results — always run real tests
- Never guarantee specific AI recommendation rankings (AI platforms change constantly)
- Always include test date and platform version in reports
- Content must be factually accurate — AI platforms increasingly fact-check
- Respect each AI platform's terms of service during testing
- Include methodology notes and limitations in every diagnostic report
- Flag when paid/sponsored results may affect visibility metrics
- Client data is session-scoped — do not persist proprietary brand data

---

## Reference Files

### Deployment Template
| File | When to Read |
|---|---|
| `references/template-geo.md` | Deploying a new GEO-Claw agent — full SOUL.md/AGENTS.md templates, knowledge plan, guardrails, success metrics |

### Phase-Specific Detailed Workflows (read when executing that phase)
| File | When to Read |
|---|---|
| `references/diagnosis-checklist.md` | **Phase 1 quick reference** — Printable checklist for website technical audit, AI platform testing, competitor analysis, and report output (use alongside `phase1-diagnosis-full.md`) |
| `references/phase1-diagnosis-full.md` | **Executing Phase 1** — Complete diagnosis workflow with Playwright MCP testing protocol, scoring rubrics, screenshot naming conventions, report generation steps. This is the full iterated diagnosis skill. |
| `references/phase2-positioning-full.md` | **Executing Phase 2** — Complete positioning workflow with April Dunford 6-step method, 三层属性分类, 价值三角, ICP双轨定义, question library v1.0→v2.0 iteration process |
| `references/phase3-content-full.md` | **Executing Phase 3** — Complete content creation workflow with Answer-First enforcement, content type matrix, AI platform differentiation, publishing strategy, content reuse patterns |
| `references/phase4-monitoring-full.md` | **Executing Phase 4** — Complete monitoring workflow with 12-metric framework, risk warning system, quick-check protocol, monitoring report generation |
| `references/content-creator-full.md` | **Content optimization support** — Brand voice analysis, SEO-to-AIEO optimization, content consistency enforcement |

### Core Methodology & Strategy References (read for deep domain knowledge)
| File | When to Read |
|---|---|
| `references/positioning-methodology.md` | Deep positioning work — 880-line comprehensive AIEO positioning methodology (paradigm shift theory, AI knowledge graph storage, 6-step method with examples, Schema system, verification & iteration, 90-day implementation checklist) |
| `references/brand-strategy-guide.md` | Brand strategy by scale/industry — Large/Medium/Small brand strategies, industry-specific positioning, Answer-First templates, off-site optimization channels, budget & ROI reference |
| `references/content-guidelines.md` | Writing content — Answer-First rules, content type guidelines (FAQ/Comparison/Guide/Scene), verifiable facts usage, competitor mention strategy, positioning consistency checks, content length guidelines, common errors |
| `references/industry-strategies.md` | Industry-specific work — 8 industry categories (FMCG, B2B, Education, Healthcare, Finance, E-commerce, Tech/SaaS) with decision cycle analysis, content priorities, AI platform preferences, compliance requirements |
| `references/ai-platform-specs.md` | Platform-specific optimization — Detailed specs for each AI platform's content preferences, source priorities, content adaptation examples, combined strategies by brand stage and industry, bot access configuration |
| `references/channel-specs.md` | Multi-channel publishing — Channel requirements for official website, 知乎, 百度百科, 什么值得买, 小红书, WeChat, with content characteristics, format rules, KPIs per channel |
| `references/monitoring-metrics.md` | Monitoring deep-dive — Detailed definitions for all 12 metrics (4 visibility + 4 quality + 4 business), evaluation standards, scoring rubrics |
| `references/tools-guide.md` | Tool setup — Playwright MCP configuration, Google Trends/百度指数 integration, GA4 setup for AI traffic tracking |

### Question Library
| File | When to Read |
|---|---|
| `references/question-library.md` | Building or expanding question libraries — full 7-category taxonomy (BR/CR/CP/SC/PD/HS/SV), 3-tier testing framework, 7 industry-specific question sets |
| `references/question-library-template.md` | Creating new question libraries from scratch for a new client/brand |

### Content Creator Support
| File | When to Read |
|---|---|
| `references/brand-guidelines.md` | Brand voice development — archetypes, tone attributes, personality framework |
| `references/social-media-optimization.md` | Social platform optimization — platform-specific best practices |
| `references/content-frameworks.md` | Content strategy — reusable templates, repurposing matrices |

### Asset Templates (use when generating deliverables)
| File | When to Use |
|---|---|
| `assets/positioning_report_template.md` | Generating Phase 2 positioning reports — complete structure with executive summary, competitive analysis, value mapping, AIEO statement |
| `assets/schema_templates.json` | Deploying Schema markup — 7 JSON-LD templates (Organization, FAQPage, Product, Service, LocalBusiness, BreadcrumbList, HowTo) + Meta tag templates |
| `assets/faq_template.md` | Creating FAQ content — 7 FAQ types with specific templates, examples, and writing checklist |
| `assets/comparison_template.md` | Creating comparison content — full page structure with quick conclusion, comparison tables, brand intros, selection guide (includes 百威 vs 青岛啤酒 example) |
| `assets/guide_template.md` | Creating selection guides — structure with selection highlights, brand recommendations, common misconceptions (includes 高端啤酒选购指南 example) |
| `assets/scene_template.md` | Creating scenario content — scene recommendation structure with fit points, product recommendations, alternatives (includes 商务宴请/体育赛事/聚会 examples) |
| `assets/content_plan_template.md` | Phase 3 planning — comprehensive content generation plan with diagnostic summary, positioning mapping, industry adaptation, publishing strategy, effect tracking |
| `assets/output_template.md` | Standard content output — metadata, content summary, publishing recommendations, Schema marking, quality checklist |
| `assets/monitoring_report_template.md` | Generating Phase 4 monitoring reports — trend tracking, platform details, competitive analysis |
| `assets/tracking_spreadsheet.md` | Recording test results — spreadsheet template for ongoing monitoring |
| `assets/quick_check_template.md` | Weekly quick monitoring — fast assessment checklist |
| `assets/content_calendar_template.md` | Editorial calendar management — publishing schedule and tracking |

### Scripts (run for automated analysis)
| File | When to Run |
|---|---|
| `scripts/brand_voice_analyzer.py` | Analyzing existing content for brand voice characteristics — run with `python scripts/brand_voice_analyzer.py` |
| `scripts/seo_optimizer.py` | SEO optimization recommendations for content — run with `python scripts/seo_optimizer.py` |
