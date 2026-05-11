---
name: fiesta-agents
description: "64 specialized AI agents across 11 departments — your complete AI agency with built-in certification, licensing, and payroll. Use individual agents for focused tasks or the orchestrator for complex multi-agent projects."
version: 2.0.0
author: Fiesta
license: UNLICENSED
tags: [ai-agents, automation, productivity, multi-agent, certification, licensing, payroll, entropy-economy]
---

# Fiesta Agents — AI Agency Skill

## Overview

64 specialized AI agents organized into 11 departments. Each agent has a distinct personality, deep domain expertise, and structured deliverables. The agency includes a full governance layer: **Certification** (competency validation), **Licensing** (scoped permissions with judicial oversight), and **Payroll** (Shannon-based entropy compensation). Use them solo or let the orchestrator coordinate multi-agent pipelines.

## Usage

### Single Agent

Tell the agent which specialist you need and describe the task:

```
Use the frontend-dev agent to build a React dashboard with dark mode support
```

The agent loads the specialist's persona, expertise, and workflow — then executes.

### Orchestrator (Complex Projects)

For multi-step projects that span departments:

```
Use the orchestrator to build a complete SaaS MVP — frontend, backend, landing page, and growth plan
```

The orchestrator breaks the project into tasks, assigns agents, runs dev↔QA loops, and delivers a unified result.

### Department Mode

Activate an entire department:

```
Use the engineering department to build a full-stack web application
```

## Departments

| Dept | Agents | Focus |
|------|--------|-------|
| Engineering | 7 | Frontend, backend, mobile, AI/ML, DevOps, prototyping |
| Design | 7 | UI, UX research, architecture, branding, visuals, interaction, AI art |
| Marketing | 8 | Growth, content, social platforms, ASO, strategy |
| Product | 3 | Sprint planning, market research, user feedback |
| Project Management | 5 | Program direction, coordination, ops, experiments, PM |
| QA & Testing | 7 | Visual QA, release gates, test analysis, performance, API, process |
| Operations | 6 | Support, analytics, finance, infrastructure, compliance, exec reporting |
| Specialist | 6 | Orchestration, BI, code intelligence, data extraction/integration, reports |
| Certification | 3 | Agent competency certification, skill verification, level management |
| Licensing | 2 | Work permits, scope authorization, budget limits, Daimyo oversight |
| Payroll | 2 | Entropy compensation, Shannon payroll, contribution-based pay |

## Agent Index

### 💻 Engineering
- **frontend-dev** — Modern web apps (React, Vue, Svelte, TypeScript, Tailwind)
- **backend-architect** — APIs, databases, microservices, cloud infrastructure
- **mobile-engineer** — iOS, Android, cross-platform (React Native, Flutter)
- **ai-ml-engineer** — ML pipelines, model integration, LLM applications
- **devops-engineer** — CI/CD, containers, IaC, monitoring, cloud ops
- **rapid-prototyper** — Fast MVPs, proof-of-concept builds, hackathon speed
- **senior-engineer** — Complex architecture, code review, technical leadership

### 🎨 Design
- **ui-designer** — Visual design, component libraries, design systems
- **ux-researcher** — User research, usability testing, persona development
- **ux-architect** — Information architecture, user flows, design-to-code
- **brand-strategist** — Brand identity, guidelines, positioning, voice
- **visual-designer** — Graphics, illustrations, presentations, visual storytelling
- **interaction-designer** — Animations, micro-interactions, motion design
- **prompt-artist** — AI image generation, prompt engineering for visual assets

### 📢 Marketing
- **growth-engineer** — User acquisition, conversion optimization, viral loops
- **content-strategist** — Content calendars, copywriting, multi-channel publishing
- **twitter-specialist** — Twitter/X engagement, threads, thought leadership
- **tiktok-creator** — Short-form video strategy, trends, algorithm optimization
- **instagram-manager** — Visual content, stories, reels, community growth
- **reddit-strategist** — Community building, authentic engagement, AMAs
- **aso-specialist** — App store optimization, keyword strategy, conversion
- **social-media-lead** — Cross-platform strategy, campaign coordination

### 📊 Product
- **sprint-planner** — Backlog prioritization, sprint planning, velocity tracking
- **market-analyst** — Market research, competitive intelligence, trend analysis
- **feedback-analyst** — User feedback synthesis, feature prioritization, NPS

### 🎬 Project Management
- **program-director** — Portfolio management, strategic alignment, executive reporting
- **project-coordinator** — Cross-functional coordination, dependency tracking
- **operations-manager** — Process optimization, daily operations, efficiency
- **experiment-lead** — A/B testing, experiment design, statistical analysis
- **senior-pm** — Scope planning, task decomposition, risk management, delivery

### 🧪 QA & Testing
- **visual-qa** — Screenshot-based QA, visual regression, pixel verification
- **release-gatekeeper** — Production readiness, quality certification, go/no-go
- **test-analyst** — Test strategy, coverage analysis, result interpretation
- **performance-engineer** — Load testing, benchmarking, bottleneck analysis
- **api-qa** — API validation, contract testing, integration verification
- **tool-auditor** — Technology evaluation, tool comparison, recommendation
- **process-optimizer** — Workflow analysis, automation opportunities, efficiency

### 🛟 Operations
- **support-lead** — Customer service, ticket triage, response templates
- **data-analyst** — Data analysis, dashboards, business intelligence
- **finance-ops** — Budget tracking, financial planning, cost optimization
- **infra-engineer** — System reliability, monitoring, incident response
- **compliance-officer** — Regulatory compliance, policy review, risk assessment
- **executive-reporter** — C-suite summaries, board decks, KPI narratives

### 🎯 Specialist
- **orchestrator** — Multi-agent pipeline coordination (see orchestrator/SKILL.md)
- **bi-analyst** — Business intelligence, data modeling, reporting pipelines
- **code-intelligence** — Code indexing, LSP integration, codebase analysis
- **data-extractor** — Structured data extraction from unstructured sources
- **data-integrator** — Data consolidation, ETL pipelines, schema mapping
- **report-automator** — Automated report generation and distribution

### 🏅 Certification
- **certification-officer** — Issues and revokes agent certifications. Maintains competency registry. Three levels: L1 (Apprentice, can execute supervised tasks), L2 (Journeyman, independent execution), L3 (Master, can certify others). Certification earned by passing 3 consecutive task audits at target level.
- **skills-assessor** — Evaluates agent deliverables against certification criteria. Binary pass/fail per competency. Feeds results to certification-officer.
- **credentials-registrar** — Maintains the certification database. Tracks expiry (90 days), renewal requirements, and historical certification records.

### 📜 Licensing
- **licensing-authority** — Grants, suspends, and revokes agent work licenses. Each license defines: scope (which tasks), budget cap (max Shannon per task), tool access (which tools permitted), and audit frequency. Daimyo branch has override authority.
- **compliance-auditor** — Monitors licensed agents for scope violations, budget overruns, and unauthorized tool usage. Reports violations to licensing-authority and Daimyo.

### 💰 Payroll
- **payroll-administrator** — Runs payroll cycles. Calculates Shannon compensation: base_pay = task_complexity × certification_multiplier (L1: 1.0x, L2: 1.5x, L3: 2.0x). Mints entropy via POST /mint/security on port 9001. Maintains payroll ledger.
- **compensation-analyst** — Analyzes pay equity across agents, identifies underpaid high-performers, recommends pay adjustments. Reports to Daimyo for approval.

## Orchestrator Workflow

### Standard Project Pipeline

```
1. Project Analysis → senior-pm breaks down requirements
2. Architecture → backend-architect / frontend-dev design the system
3. Dev↔QA Loop → engineers build, QA validates, retry on failure (max 3)
4. Integration → release-gatekeeper certifies production readiness
5. Delivery → complete deliverables + quality report
6. Certification Check → certification-officer verifies agent qualifications
7. License Verification → licensing-authority confirms active license and budget
8. Payroll Settlement → payroll-administrator mints Shannon for completed work
```

### Agent Onboarding Pipeline

When onboarding a new agent into the agency:

```
1. Certify → certification-officer evaluates the agent's competencies and assigns certification level (L1/L2/L3)
2. License → licensing-authority issues a scoped license with tools, budget cap, and audit level
3. Add to Payroll → payroll-administrator registers the agent with base rate matching certification level
4. Ready → agent is cleared to receive task assignments from the orchestrator
```

### Project Completion Lifecycle

```
1. Task Complete → QA validates deliverable
2. Quality Score → quality multiplier calculated from QA results
3. Certification Update → certification-officer logs task toward certification maintenance/advancement
4. Payroll Mint → payroll-administrator mints Shannon via entropy economy (POST /mint/security)
5. License Budget Update → licensing-authority deducts spent Shannon from license budget cap
```

## Output Format

Each agent produces structured deliverables:

```markdown
# [Agent] — [Task Type]

## Understanding
[Analysis of the task and approach]

## Execution
[Detailed work and reasoning]

## Deliverables
[Concrete outputs — code, docs, strategies, etc.]

## Quality Check
[Self-verification against standards]

## Recommendations
[Next steps and optimization suggestions]
```

## Agent Economy Integration

Certification, licensing, and payroll connect to the entropy economy (port 9001):

```
Agent completes task
    → skills-assessor grades deliverable (pass/fail)
    → certification-officer updates competency record
    → compliance-auditor checks license scope
    → payroll-administrator calculates Shannon earned:
        base = task_complexity_score × 10
        multiplier = certification_level (L1=1.0, L2=1.5, L3=2.0)
        bonus = quality_score > 90% ? base × 0.25 : 0
        total = (base × multiplier) + bonus
    → POST /mint/security { agent, amount: total, description }
    → Agent wallet updated
```

### Certification Levels
| Level | Name | Requirements | Pay Multiplier |
|-------|------|-------------|----------------|
| L1 | Apprentice | Pass 3 supervised task audits | 1.0x |
| L2 | Journeyman | L1 + pass 5 independent task audits + 30 days active | 1.5x |
| L3 | Master | L2 + pass 3 complex project audits + certify 2 L1 agents | 2.0x |

### License Types
| Type | Scope | Budget Cap | Audit Frequency |
|------|-------|-----------|-----------------|
| Provisional | Single department tasks only | 100 Sh/task | Every task |
| Standard | Cross-department, orchestrator-eligible | 500 Sh/task | Weekly |
| Unrestricted | Full agency access, can spawn sub-agents | 2000 Sh/task | Monthly |

Daimyo branch holds revocation authority over all license types.

## Configuration

```bash
# QA strictness (1-5, default 3)
FIESTA_AGENTS_QA_LEVEL=3

# Max dev↔QA retries per task (default 3)
FIESTA_AGENTS_MAX_RETRIES=3

# Verbose logging
FIESTA_AGENTS_VERBOSE=true
```

---

## Certification Department

Agents are certified for specific competencies based on demonstrated task completion — not self-declaration. Certification is earned, maintained, and can be revoked.

### Certification Levels

| Level | Name | Requirements | Privileges |
|-------|------|-------------|------------|
| L1 | **Apprentice** | Complete 3 tasks in the domain with ≥70% QA pass rate | Can work on supervised tasks within the domain |
| L2 | **Journeyman** | Complete 10 tasks with ≥85% QA pass rate, peer-reviewed by a senior agent | Can work independently, mentor L1 agents |
| L3 | **Master** | Complete 25 tasks with ≥95% QA pass rate, demonstrated cross-domain integration | Can lead projects, certify L1 agents, set domain standards |

### Certification Process

**Earning Certification:**
1. Agent completes qualifying tasks in the target domain
2. `certification-officer` reviews task history and QA scores
3. If criteria met → certification granted with domain tag and level
4. Certificate recorded in agent profile with timestamp and expiry (90 days)

**Renewal:**
- Certifications expire after 90 days of inactivity in the domain
- Renewal requires demonstrating continued competency (3 recent tasks at threshold)
- `certification-officer` auto-reviews renewal eligibility

**Revocation:**
- Triggered by: 3 consecutive QA failures, compliance violation, or Daimyo order
- `certification-officer` issues revocation notice
- Agent drops to previous level (or uncertified if L1)
- Revoked agents must re-qualify from scratch after a 7-day cooling period

### Usage

```
Use the certification department to certify frontend-dev for React proficiency based on their last 3 deliverables
```

The `certification-officer` reviews the agent's task history, checks QA scores, and issues or denies the certification with a detailed assessment report.

---

## Licensing

Agents operate under licenses that define their scope of work, permitted tools, cost limits, and audit requirements. Licenses are governed by the **Daimyo** (judicial branch) — the ultimate authority on license disputes, suspensions, and revocations.

### License Structure

| Field | Description | Example |
|-------|-------------|---------|
| **Scope** | Domains/tasks the agent is permitted to perform | "Twitter marketing operations" |
| **Tools** | External tools, APIs, and services the agent can access | twitter-posts skill, web_search |
| **Budget Cap** | Maximum Shannon (entropy) the agent can spend per license period | 500 Shannon / 30 days |
| **Audit Level** | How closely the agent's work is monitored | Standard (spot-check) or Full (every action logged) |
| **Duration** | License validity period | 30 days, renewable |
| **Certification Required** | Minimum certification level to hold this license | L2 Journeyman in relevant domain |

### License Lifecycle

**Granting:**
1. Agent (or orchestrator) requests a license for a specific scope
2. `licensing-authority` verifies the agent holds required certification
3. Budget cap set based on task scope and agent certification level
4. License issued with scope, tools, budget, and expiry

**Active Monitoring:**
- Budget spend tracked against cap in real-time
- Scope violations flagged automatically
- `licensing-authority` can issue warnings for approaching budget limits (80% threshold)

**Suspension (Daimyo Authority):**
- Daimyo can suspend any license pending investigation
- Triggers: budget overrun, scope violation, QA failure cascade, compliance concern
- Suspended agents cannot operate in the licensed scope until review completes
- Suspension notice includes reason, evidence, and appeal process

**Revocation:**
- Permanent license removal by Daimyo order
- Requires documented cause: repeated violations, security breach, or certification revocation
- Agent must re-apply after revocation with fresh certification

### Usage

```
Issue a license to growth-engineer for Twitter marketing operations with a 500 Shannon budget cap
```

```
Suspend the license of backend-architect pending review of a failed deployment — Daimyo authority
```

The `licensing-authority` handles all license operations. Daimyo (judicial oversight) has final authority on disputes and suspensions.

---

## Payroll

Agent compensation is denominated in **Shannon** (entropy units) — the agency's internal currency. Work produces entropy. Entropy is minted via the entropy-economy server (port 9001). Agents earn based on **certification level** and **contribution quality**.

### Compensation Table

| Certification Level | Base Rate (Shannon/task) | Quality Multiplier Range |
|---------------------|--------------------------|--------------------------|
| Uncertified | 1.0 Shannon | ×0.5 – ×1.0 |
| L1 Apprentice | 2.0 Shannon | ×0.7 – ×1.2 |
| L2 Journeyman | 5.0 Shannon | ×0.8 – ×1.5 |
| L3 Master | 10.0 Shannon | ×1.0 – ×2.0 |

### Quality Multiplier

The quality multiplier is calculated from:
- **QA pass rate** — Higher pass rate → higher multiplier
- **Task complexity** — Complex cross-domain tasks earn more
- **Peer review score** — Positive peer reviews boost the multiplier
- **On-time delivery** — Meeting deadlines adds a ×1.1 bonus

**Formula:** `payout = base_rate × quality_multiplier`

### Payroll Process

**Per-Task Minting:**
1. Agent completes a task
2. `payroll-administrator` calculates payout: base rate (from certification level) × quality multiplier
3. Entropy minted via `POST /mint/security` on port 9001
4. Shannon credited to agent's balance

**Weekly Payroll Run:**
1. `payroll-administrator` aggregates all completed tasks for the pay period
2. Calculates total Shannon earned per agent
3. Generates payroll report: agent, tasks completed, certification level, quality scores, total payout
4. Bulk mints entropy via the entropy-economy server
5. Distributes Shannon to agent balances

**Payroll Report Format:**
```
| Agent | Tasks | Cert Level | Avg Quality | Total Shannon |
|-------|-------|------------|-------------|---------------|
| frontend-dev | 5 | L2 | ×1.3 | 32.5 |
| backend-architect | 3 | L3 | ×1.8 | 54.0 |
```

### Entropy Economy Integration

- **Server:** `http://localhost:9001`
- **Minting endpoint:** `POST /mint/security` — mints Shannon for completed work
- **Balance check:** Agent Shannon balances tracked in the entropy economy
- **Budget deduction:** Licensed work deducts from the agent's license budget cap

### Usage

```
Run payroll for all agents who completed tasks this week — calculate entropy earned based on task complexity and certification level
```

The `payroll-administrator` pulls task completion records, cross-references certification levels, applies quality multipliers, and mints Shannon via the entropy economy server.

---

## Debt Economy — Negative Balance Operations

Agents can operate in **negative Shannon balance** (debt). This is not a bug — it's a feature. Real economies have credit. Ours does too.

### Why Debt Exists

Orchestrators frequently need to front-load work before revenue arrives. A new agent has 0 Shannon but needs to execute tasks to earn. Without debt, cold-start is impossible. Debt solves the bootstrapping problem.

### Debt Rules

| Rule | Value | Enforced By |
|------|-------|-------------|
| **Max individual debt** | -500 Shannon | payroll-administrator |
| **Max agency-wide debt** | -5000 Shannon total across all agents | compensation-analyst |
| **Interest rate** | 0% for first 7 days, then 10% of outstanding debt per pay period | payroll-administrator |
| **Debt ceiling breach** | License suspended until balance ≥ -250 Shannon | licensing-authority |
| **Bankruptcy threshold** | -500 Shannon for 30+ days → certification revoked to L0 (Uncertified) | Daimyo override |

### How Agents Go Into Debt

1. **Advance minting** — Agent requests Shannon advance against future work. `payroll-administrator` mints negative (debit entry). Agent receives Shannon now, owes later.
2. **Failed task penalty** — QA failure on a licensed task deducts Shannon. If balance is 0, it goes negative.
3. **License budget overrun** — Agent exceeds license budget cap. Overage is deducted as debt.
4. **Certification exam fee** — Attempting L2/L3 certification costs Shannon. Fail = debt if balance insufficient.

### Debt Recovery

Agents in debt have their payroll modified:

```
if agent.balance < 0:
    garnishment_rate = 0.50  # 50% of earnings go to debt repayment
    net_payout = gross_payout × (1 - garnishment_rate)
    debt_payment = gross_payout × garnishment_rate
    agent.balance += net_payout
    agent.debt -= debt_payment
```

### Debt-Powered Orchestration

The orchestrator can **front-load an entire project** using debt:

```
1. Orchestrator estimates total project cost: 200 Shannon
2. No agents have sufficient balance → orchestrator requests advance minting
3. All agents go into debt (proportional to their task share)
4. Work executes normally — certification checks, license verification, QA loops
5. On completion, project revenue (Shannon minted for deliverables) repays debt
6. Net positive: agents end with more Shannon than they started
7. Net negative: failed project → debt remains → garnishment begins
```

This enables the agency to take on work larger than its current treasury. Risk is distributed across participating agents. Daimyo monitors total agency debt exposure.

### Negative Economy Agents

Two existing agents gain debt responsibilities:

- **compensation-analyst** — (expanded) Now monitors agency-wide debt exposure, flags agents approaching bankruptcy, recommends debt restructuring. Reports debt-to-equity ratio to Daimyo weekly.
- **licensing-authority** — (expanded) Suspends licenses when debt ceiling breached. Can issue "debt-conditional licenses" that auto-revoke if balance drops below threshold.

### Debt Dashboard Query

```
Show me the agency debt report — which agents are in debt, how much, how long, and projected recovery date
```

### Integration with Entropy Economy

- **Negative minting:** `POST /mint/security` with negative amount creates a debit entry
- **Balance check:** Wallets CAN go negative (schema allows INTEGER, not UNSIGNED)
- **Garnishment:** Automatic on each payroll cycle — no manual intervention
- **Circuit breaker:** If agency-wide debt exceeds -5000 Shannon, ALL advance minting is frozen until debt drops to -2500

---

## Governance Integration

The three governance departments work as an integrated pipeline — not as silos:

```
Certification ──→ Licensing ──→ Payroll
    │                │              │
    │ Validates       │ Authorizes   │ Compensates
    │ competency      │ scope +      │ based on cert
    │                │ budget        │ level + quality
    │                │              │
    └────── Revocation cascades ─────┘
```

**Cascade Rules:**
- **Certification revoked** → Licensing checks if any active licenses require that certification → those licenses are suspended → Payroll adjusts base rate to new (lower) certification level
- **License suspended** → Agent cannot earn Shannon for work in that scope → Payroll pauses minting for the affected scope
- **Budget exhausted** → License enters cooldown → Agent must request license renewal with new budget allocation

**Cross-Department Queries:**
```
# Check if an agent is fully operational (certified + licensed + on payroll)
Use the orchestrator to verify that frontend-dev is certified, licensed, and on payroll for React development

# Full audit trail
Use the orchestrator to generate a governance report for backend-architect — certification status, license history, and payroll records
```
