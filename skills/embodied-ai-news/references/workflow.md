# 🧭 Embodied AI News — Workflow SOP

A step-by-step Standard Operating Procedure that connects all system files into an executable daily/weekly/monthly workflow.

---

## System File Map

```
📁 Embodied AI News System
│
├── 📰 news_sources.md         — WHERE to find information
├── 🔍 search_queries.md       — HOW to search for information
├── 📝 output_templates.md     — WHAT format to output
└── 🧭 workflow.md             — WHEN and in what ORDER to do it (this file)
```

**How they connect:**

```
┌─────────────────┐     ┌──────────────────┐     ┌───────────────┐     ┌──────────────────┐
│  search_queries  │────▶│  news_sources     │────▶│  Classify &   │────▶│ output_templates  │
│  (discover)      │     │  (browse & verify) │     │  Prioritize   │     │  (generate)       │
└─────────────────┘     └──────────────────┘     └───────────────┘     └──────────────────┘
```

---

## Daily Workflow (~30 minutes)

**Goal**: Produce a daily briefing covering the last 24 hours.
**Output Template**: `Standard Format` or `Brief Format`
**Best Time**: Morning (8:00–9:00 AM)

---

### Step 1: Search & Discover (10 min)

**Use**: `search_queries.md` → **Recipe A: Daily Briefing**

Execute the 5 queries in order:

| # | Query Focus | Action |
|---|-------------|--------|
| Q1 | General embodied AI news | Scan top 10 results, bookmark relevant |
| Q2 | Foundation model / algorithm news | Scan top 10, bookmark papers & announcements |
| Q3 | Key company names | Scan top 10, bookmark demos & updates |
| Q4 | Funding & startup news | Scan top 10, bookmark deals |
| Q5 | Core media sites | Scan headlines on Robot Report & IEEE Spectrum |

**Output of this step**: A raw list of 10–20 bookmarked URLs.

---

### Step 2: Browse Priority Sources (10 min)

**Use**: `news_sources.md` → **Tier 1 (Core Media)** + **Tier 2 (Company Blogs)**

| Source | Action | Time |
|--------|--------|------|
| The Robot Report | Scan homepage headlines | 2 min |
| IEEE Spectrum Robotics | Scan latest articles | 2 min |
| TechCrunch Robotics | Check for funding/launch news | 1 min |
| Tesla AI (X/Twitter) | Check for Optimus updates | 1 min |
| Figure AI / 1X / Unitree (X) | Check for new demos | 2 min |
| QbitAI (量子位) | Scan for China ecosystem news | 2 min |

**Output of this step**: Additional 5–10 URLs added to the raw list. Duplicates removed.

---

### Step 3: Classify & Prioritize (5 min)

Sort all collected stories into the following categories:

| Category | Icon | Priority Criteria |
|----------|------|-------------------|
| Major Announcements | 🔥 | New product launch, major demo, paradigm shift |
| Foundation Models & Algorithms | 🧠 | New model release, SOTA result, open-source drop |
| Hardware & Platforms | 🦾 | New robot, component breakthrough, spec upgrade |
| Deployments & Commercial | 🏭 | Real-world deployment, customer announcement |
| Simulation & Infrastructure | 🌐 | Sim platform update, new benchmark, dataset |
| Funding & M&A | 💰 | Funding round, acquisition, IPO |
| Policy, Safety & Ethics | 🌍 | Regulation, safety standard, export control |
| China Ecosystem | 🇨🇳 | China-specific company, policy, or supply chain |

**Prioritization rules:**
1. **Lead story**: The single most impactful news item → goes to "Major Announcements"
2. **Must-include**: Any story with >3 sources covering it
3. **Skip**: Press releases with no substance, duplicate coverage, tangentially related stories
4. **Target**: 5–8 stories total for a daily briefing

**Output of this step**: A classified, prioritized list of 5–8 stories with categories assigned.

---

### Step 4: Generate Output (5 min)

**Use**: `output_templates.md` → **Standard Format** (default) or **Brief Format** (if time-constrained)

For each story, fill in the template fields:

```
For Standard Format, each story needs:
├── Headline
├── Summary (1 sentence)
├── Key Points (2-3 bullets)
├── Domain-specific metadata
│   ├── Robot/Platform (if applicable)
│   ├── Tech Stack (if applicable)
│   ├── Model Type / Hardware Type / Deployment Scale (by category)
│   └── Open Source status (for research stories)
├── Impact (1-2 sentences)
├── Source + Date
└── Link
```

**Final checks before publishing:**
- [ ] All links are working
- [ ] Dates are accurate
- [ ] No duplicate stories
- [ ] Key Takeaways section is filled (3 bullets)
- [ ] Daily Pulse stats table is populated

---

## Weekly Workflow (~90 minutes)

**Goal**: Produce a comprehensive weekly analysis.
**Output Template**: `Deep Format`
**Best Time**: Friday afternoon or Saturday morning

---

### Step 1: Aggregate the Week's Daily Briefings (10 min)

- Review all 5 daily briefings from the week
- Identify the **top 3 stories** that had the most lasting impact
- Note any **developing stories** that evolved across multiple days
- Flag stories that deserve deeper analysis

---

### Step 2: Research Deep Dive (30 min)

**Use**: `search_queries.md` → **Recipe B: Weekly Research Deep Dive**

| # | Query Focus | Action |
|---|-------------|--------|
| Q1 | arXiv cs.RO embodied AI papers | Identify top 3-5 papers by discussion volume |
| Q2 | Specific algorithm topics | Find notable diffusion policy / world model papers |
| Q3 | Sim-to-real & generalist policies | Track cross-embodiment transfer progress |
| Q4 | Open-source releases | Check for new code/model drops |

**Paper evaluation criteria:**
- Cited/discussed on X/Twitter by >5 researchers
- From a top lab (DeepMind, TRI, Stanford, CMU, Berkeley, Tsinghua)
- Introduces a new benchmark or achieves clear SOTA
- Includes open-source code or model weights

---

### Step 3: Commercial & Deployment Tracking (20 min)

**Use**: `search_queries.md` → **Recipe C: Commercial & Deployment Tracker**

Track and update:
- [ ] New deployment announcements (company → customer, scale, tasks)
- [ ] Funding rounds closed this week (amount, valuation, investors)
- [ ] Partnership or M&A activity
- [ ] Supply chain developments (new components, manufacturing capacity)

---

### Step 4: China Ecosystem Check (15 min)

**Use**: `search_queries.md` → **Recipe D: China Ecosystem Focus**

- [ ] Check Unitree, AGIBOT, UBTECH, Galbot, Fourier for updates
- [ ] Scan QbitAI and Synced Review for China-specific stories
- [ ] Check for policy announcements (subsidies, standards, industrial parks)
- [ ] Note any supply chain or export control developments

---

### Step 5: Generate Weekly Deep Dive (15 min)

**Use**: `output_templates.md` → **Deep Format**

Additional sections to fill for weekly output:
- [ ] **Benchmark / Performance tables** for research stories
- [ ] **Expert Reactions** section (check X/Twitter, blog posts)
- [ ] **Analysis & Insights** section:
  - Biggest story of the week
  - 3 emerging trends
  - Technology convergence map
  - What to watch (this week / this month / this quarter)
- [ ] **Daily Pulse** stats table with weekly aggregates

---

## Monthly Workflow (~3 hours)

**Goal**: Produce a monthly trend report and update the system itself.
**Output Template**: `Deep Format` + custom monthly summary section
**Best Time**: First Monday of the new month

---

### Part A: Monthly Trend Report (2 hours)

#### Step 1: Review All Weekly Reports (20 min)
- Identify the **top 5 stories** of the month
- Track **recurring themes** across weeks
- Note **surprises** — things that weren't on the radar at month start

#### Step 2: Thematic Deep Dives (60 min)

Choose 2–3 themes for deeper analysis. Common monthly themes:

| Theme | What to Analyze |
|-------|----------------|
| **Model Architecture Trends** | Which approaches are gaining traction? VLA vs. Diffusion vs. World Model? |
| **Hardware Race** | Who launched new platforms? How do specs compare? Price trends? |
| **Deployment Scoreboard** | Total units deployed across companies. New verticals entered. |
| **Funding Landscape** | Total $ raised. Valuation trends. New entrants vs. follow-on rounds. |
| **China vs. US** | Capability gap analysis. Policy divergence. Supply chain dynamics. |
| **Open Source Momentum** | New open-source releases. Community adoption metrics. |

#### Step 3: Generate Monthly Report (40 min)

Structure:
```
# 📊 Embodied AI Monthly Report — [Month Year]

## Executive Summary (5 bullets)
## Top 5 Stories of the Month
## Thematic Deep Dive 1: [Theme]
## Thematic Deep Dive 2: [Theme]
## Thematic Deep Dive 3: [Theme]
## Funding & Deal Tracker (table)
## Deployment Tracker (table)
## Paper Highlights (top 5 papers)
## What to Watch Next Month
## Monthly Statistics Dashboard
```

---

### Part B: System Maintenance (1 hour)

#### Step 1: Update `news_sources.md` (20 min)
- [ ] **Add** new sources discovered during the month
- [ ] **Remove** sources that have gone inactive or dropped quality
- [ ] **Re-tier** sources if their relevance has changed
- [ ] **Add** new company blogs for emerging players
- [ ] **Verify** all URLs still work

#### Step 2: Update `search_queries.md` (20 min)
- [ ] **Add** new company names that emerged this month
- [ ] **Add** new technical terms (e.g., a new model architecture name)
- [ ] **Retire** queries that consistently return noise
- [ ] **Tune** queries that return too few or too many results
- [ ] **Update** conference names with current year (e.g., "CoRL 2026" → "CoRL 2027")

#### Step 3: Update `output_templates.md` (10 min)
- [ ] **Add** new metadata fields if a new category of information has become important
- [ ] **Adjust** category names if the field's taxonomy has shifted
- [ ] **Review** whether the current template set covers all use cases

#### Step 4: Update `workflow.md` (10 min)
- [ ] **Adjust** time estimates based on actual experience
- [ ] **Add/remove** steps based on what's working
- [ ] **Update** priority sources if the landscape has shifted

---

## Quarterly Workflow (Half Day)

**Goal**: Strategic review and system overhaul.
**Best Time**: First week of Q1/Q2/Q3/Q4

---

### Step 1: Conference Season Alignment (30 min)

Check upcoming conferences and align tracking:

| Quarter | Key Events | Action |
|---------|-----------|--------|
| **Q1** (Jan–Mar) | CES, NVIDIA GTC | Track product demos, platform announcements |
| **Q2** (Apr–Jun) | ICRA, Google I/O, Automate | Track academic papers, Google robotics updates |
| **Q3** (Jul–Sep) | RSS, RoboCup, WRC (China) | Track research results, China ecosystem |
| **Q4** (Oct–Dec) | IROS, CoRL, NeurIPS | Track robot learning papers, year-end reviews |

- [ ] Add conference-specific queries to `search_queries.md`
- [ ] Set calendar reminders for key dates
- [ ] Identify which companies are likely to announce at each event

---

### Step 2: Competitive Landscape Update (60 min)

Build/update a company tracker:

```
| Company | Latest Robot | Gen | Units Deployed | Last Funding | Valuation | Key Tech |
|---------|-------------|-----|----------------|-------------|-----------|----------|
| Tesla | Optimus Gen-X | X | ~X,XXX | N/A (public) | — | End-to-end NN |
| Figure | Figure 0X | X | ~XXX | $X.XB Series X | $XXB | VLA + LLM |
| ... | ... | ... | ... | ... | ... | ... |
```

---

### Step 3: Technology Roadmap Review (60 min)

Assess progress on key technical milestones:

| Capability | Status | Key Blockers | Leading Approaches |
|-----------|--------|-------------|-------------------|
| Reliable bipedal walking | ✅ Solved | — | Model-based + RL |
| Dexterous in-hand manipulation | 🟡 Emerging | Tactile sensing, sim gap | RL + Tactile + Sim-to-Real |
| Language-conditioned task execution | 🟡 Emerging | Grounding, long-horizon | VLA, LLM planning |
| Generalist multi-task policy | 🔴 Early | Data scale, generalization | Cross-embodiment pretraining |
| Household autonomy (>1 hour) | 🔴 Early | Long-horizon, recovery | World models, hierarchical |

---

### Step 4: System Overhaul (60 min)

- [ ] Full review of all 4 system files
- [ ] Archive outdated content
- [ ] Restructure categories if the field has shifted
- [ ] Write a "Quarterly State of Embodied AI" summary (1 page)

---

## Quick Reference: Which Workflow When?

| Cadence | Time | Template | Recipe | Key Deliverable |
|---------|------|----------|--------|----------------|
| **Daily** | 30 min | Standard / Brief | Recipe A | Daily Briefing |
| **Weekly** | 90 min | Deep | Recipe A+B+C+D | Weekly Analysis |
| **Monthly** | 3 hours | Deep + Custom | All Recipes | Monthly Trend Report + System Update |
| **Quarterly** | Half day | Custom | All Recipes | Strategic Review + System Overhaul |

---

## Automation Opportunities

### What Can Be Automated
| Task | Tool / Method | Difficulty |
|------|--------------|------------|
| Query execution | Google Alerts, RSS feeds, custom scripts | Easy |
| arXiv paper monitoring | Semantic Scholar alerts, arxiv-sanity | Easy |
| Social media monitoring | X/Twitter lists, Nuzzel-like tools | Easy |
| Story deduplication | URL matching, title similarity | Medium |
| Category classification | LLM-based classification prompt | Medium |
| Template filling | LLM with structured output | Medium |
| Trend detection | Keyword frequency analysis over time | Hard |

### Recommended Automation Stack
```
Layer 1 — Ingestion:
├── Google Alerts (general queries, daily email digest)
├── RSS Reader (Feedly / Inoreader) for Tier 1 & Tier 2 sources
├── Semantic Scholar Alerts (arXiv paper tracking)
└── X/Twitter Lists (company accounts + key researchers)

Layer 2 — Processing:
├── LLM (classify, summarize, extract metadata)
├── Deduplication (URL + title matching)
└── Priority scoring (source tier × recency × discussion volume)

Layer 3 — Output:
├── Template rendering (fill output_templates.md)
├── Distribution (email, Slack, Notion, blog)
└── Archive (searchable database of past briefings)
```

---

## Troubleshooting

| Problem | Cause | Solution |
|---------|-------|---------|
| Too few results | Queries too narrow | Expand date range; use broader terms; check more sources |
| Too many results | Queries too broad | Add NOT filters; narrow date range; add domain-specific terms |
| Missing China news | English-only queries | Add Chinese keywords; check QbitAI/Synced directly |
| Stale company blogs | Infrequent posting | Rely on X/Twitter + media coverage instead |
| Duplicate stories | Multiple outlets covering same event | Deduplicate by topic, keep the most detailed source |
| Can't assess paper importance | No citation data yet (preprint) | Use X/Twitter discussion volume as a proxy |
| Template too long | Too many stories included | Use Brief format; raise the inclusion threshold to top 5 only |

---

> **Last Updated**: February 2026
> **Review Cycle**: Monthly (Part B of Monthly Workflow)