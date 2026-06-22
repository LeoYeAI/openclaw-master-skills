---
name: client-onboarding-agent
description: 'Client onboarding and business diagnostic framework for AI agent deployments. Covers 4-round diagnostic process, 6 constraint categories, deployment SOP with completion contracts, tiered advisory mode for new automations, and the 6-week sell narrative. Use when onboarding new clients for agent deployments or managed automation services. NOT for self-service SaaS onboarding or consumer products.'
license: MIT
metadata:
  openclaw:
    emoji: '🤝'
---

# Client Onboarding Agent

Framework for onboarding new clients into AI agent deployments. This isn't a sales process — it's a diagnostic process. You're figuring out what's broken, what can be automated, and what the constraints are before you promise anything.

---

## The 4-Round Business Diagnostic

Every client engagement starts with four rounds of structured discovery. Each round has a specific purpose and produces a specific artifact. Do not skip rounds. Do not combine rounds.

### Round 1: Pain Points and Current Tools

**Purpose:** Understand what hurts and what they're already using.

**Duration:** 30-60 minutes

**Questions to ask:**

1. "What are the three tasks that eat the most time in your week?"
2. "What tools are you currently using for [each task mentioned]?"
3. "What breaks most often? What causes the most stress?"
4. "If you could wave a magic wand and automate one thing, what would it be?"
5. "What have you tried before that didn't work? Why?"
6. "How many people touch this workflow?"

**What you're listening for:**
- Repetitive manual tasks (data entry, report generation, email triage)
- Tool sprawl (too many disconnected systems)
- Single points of failure (one person who knows how something works)
- Compliance or accuracy anxiety (fear of mistakes)
- Time sinks that prevent higher-value work

**Artifact: Pain Point Map**

```markdown
## Pain Point Map — [Client Name]
Date: [Date]

### Critical Pain Points (daily impact)
1. [Pain point]: Currently handled by [who] using [tool]. Takes [time].
2. [Pain point]: Currently handled by [who] using [tool]. Takes [time].

### Significant Pain Points (weekly impact)
1. [Pain point]: Currently handled by [who] using [tool]. Takes [time].

### Chronic Pain Points (ongoing frustration)
1. [Pain point]: No current solution / workaround is [description].

### Current Tool Stack
- [Tool 1]: Used for [purpose]. Satisfaction: [1-5]
- [Tool 2]: Used for [purpose]. Satisfaction: [1-5]
- [Tool 3]: Used for [purpose]. Satisfaction: [1-5]
```

---

### Round 2: Workflow Mapping and Data Flow

**Purpose:** Map how information actually flows through the business. Not the org chart — the real flow.

**Duration:** 45-90 minutes

**Questions to ask:**

1. "Walk me through what happens when [trigger event]. Step by step."
2. "Where does the data come from? Where does it end up?"
3. "How do you know when something is done correctly?"
4. "What gets lost between steps? Where do things fall through cracks?"
5. "Who approves what? What needs a human decision vs. what's mechanical?"
6. "Show me the actual tools — can I see your screen for a minute?"

**What you're mapping:**
- Input sources (email, forms, phone calls, spreadsheets)
- Processing steps (who does what in what order)
- Decision points (where human judgment is required vs. rote)
- Output destinations (reports, invoices, communications)
- Handoff points (where work moves between people or systems)
- Data format changes (spreadsheet to email to PDF to data entry)

**Artifact: Workflow Diagram**

```
[Trigger] → [Step 1: who/tool] → [Decision?] → [Step 2: who/tool] → [Output]
                                      ↓
                              [Alternative path]
```

Create one diagram per major workflow. Mark each step with:
- **A** = Automatable (no human judgment needed)
- **H** = Human required (judgment, approval, creativity)
- **P** = Partially automatable (agent can prepare, human decides)

---

### Round 3: Constraint Identification

**Purpose:** Identify what will block or limit the deployment. This is where most onboardings fail — people skip constraint analysis and then hit walls during implementation.

**Duration:** 30-60 minutes

**The 6 Constraint Categories:**

#### 1. Technical Constraints
- What systems can't be integrated? (Legacy software, no API, proprietary formats)
- What data is locked in systems with no export?
- What's the internet reliability? (Important for always-on agents)
- Hardware limitations?

**Questions:**
- "Are there any systems that don't have an API or can't be connected to other tools?"
- "Is your internet connection reliable enough for always-on services?"
- "Do you have any proprietary software that would need special handling?"

#### 2. Financial Constraints
- What's the budget for the deployment? (Monthly, not just setup)
- What's the budget for ongoing API costs?
- What's the ROI threshold? (How quickly does this need to pay for itself?)

**Questions:**
- "What's your budget for this, including ongoing monthly costs?"
- "How do you measure ROI on operational tools?"
- "Are API costs (like Claude API) in your budget, or do we need to factor that in?"

#### 3. Regulatory Constraints
- What compliance requirements apply? (HIPAA, SOC2, PCI, state regulations)
- What data can't leave the premises?
- What needs audit trails?
- What requires licensed professionals to review?

**Questions:**
- "Are there any regulatory requirements that affect how we handle your data?"
- "Does anything need to be reviewed by a licensed professional before it goes out?"
- "Do you need audit trails for compliance?"

#### 4. Organizational Constraints
- Who needs to approve this? (Decision-makers not in the room)
- Who will resist this? (Honestly)
- What's the change management reality?
- How tech-savvy is the team?

**Questions:**
- "Who else needs to sign off on this?"
- "Is anyone on the team skeptical about AI automation? That's fine — I just need to know."
- "How does your team typically adopt new tools?"

#### 5. Data Constraints
- What data is available? What's missing?
- What's the data quality like? (Garbage in, garbage out)
- What's sensitive? What can be processed by external APIs?
- How much historical data exists?

**Questions:**
- "How clean is your data? Are records up to date?"
- "What data would you NOT want processed by an external AI?"
- "Do you have historical data we can use for training or calibration?"

#### 6. Timeline Constraints
- When does this need to be working?
- Are there regulatory deadlines? (Tax season, compliance filings)
- What's the realistic availability of the client for onboarding?

**Questions:**
- "When do you need this operational?"
- "Are there any hard deadlines driving this?"
- "How much time can you dedicate to onboarding in the first two weeks?"

**Artifact: Constraint Matrix**

```markdown
## Constraint Matrix — [Client Name]

| Category       | Constraint                        | Severity | Mitigation                    |
|----------------|-----------------------------------|----------|-------------------------------|
| Technical      | Legacy payroll system, no API     | High     | Manual bridge or CSV export   |
| Financial      | $X/month max budget               | Medium   | Prioritize highest-ROI agents |
| Regulatory     | HIPAA applies to patient data     | High     | On-premise only, no cloud API |
| Organizational | Owner travels 2 weeks/month       | Medium   | Async onboarding + mobile     |
| Data           | 3 years of data in spreadsheets   | Low      | One-time import project       |
| Timeline       | Tax season starts in 8 weeks      | High     | Deploy accounting agent first |
```

---

### Round 4: Solution Design and Prioritization

**Purpose:** Based on Rounds 1-3, design the actual deployment plan and prioritize what gets built first.

**Duration:** 60-90 minutes (may include follow-up)

**Process:**

1. **Match pain points to automatable workflows**
   - For each Critical pain point from Round 1, check if the workflow (Round 2) is automatable and no constraints (Round 3) block it
   - Score each potential automation: Impact (1-5) x Feasibility (1-5)

2. **Prioritize by score**
   - Highest score = first deployment
   - Break ties by favoring the one that delivers visible value fastest

3. **Design the deployment plan**
   - Phase 1: Highest-priority automation (Weeks 1-2)
   - Phase 2: Second-priority automation (Weeks 3-4)
   - Phase 3: Remaining automations (Weeks 5-6)

4. **Set completion contracts for each phase** (see below)

**Artifact: Deployment Plan**

```markdown
## Deployment Plan — [Client Name]

### Phase 1 (Weeks 1-2): [Name of automation]
- Pain point addressed: [from Round 1]
- Workflow automated: [from Round 2]
- Constraints mitigated: [from Round 3]
- Completion contract: [see below]
- Expected impact: [specific, measurable]

### Phase 2 (Weeks 3-4): [Name of automation]
[Same structure]

### Phase 3 (Weeks 5-6): [Name of automation]
[Same structure]
```

---

## Completion Contracts

Every deliverable gets a completion contract. No ambiguity. No "it's mostly done." Done is binary.

### Completion Contract Structure

```markdown
## Completion Contract: [Deliverable Name]

### Done Criteria (ALL must be true)
1. [Specific, observable criterion]
2. [Specific, observable criterion]
3. [Specific, observable criterion]

### Observable Evidence
- [ ] [What you can see/verify to confirm criterion 1]
- [ ] [What you can see/verify to confirm criterion 2]
- [ ] [What you can see/verify to confirm criterion 3]

### Staged Approval
- Stage 1: Internal verification (we confirm it works)
- Stage 2: Client demo (client sees it work)
- Stage 3: Client independent use (client uses it without help)

### Timeout Bounds
- Expected completion: [date]
- Hard deadline: [date]
- If not complete by hard deadline: [what happens — usually rescope]
```

### Example Completion Contract

```markdown
## Completion Contract: Automated Invoice Processing

### Done Criteria
1. Agent can read incoming invoices from email attachments (PDF, image)
2. Agent correctly extracts vendor, amount, date, and line items with >95% accuracy
3. Agent creates corresponding entry in QuickBooks with correct categorization
4. Agent flags anomalies (unusual amounts, new vendors) for human review

### Observable Evidence
- [ ] Process 20 test invoices with known correct values; >19 match
- [ ] New vendor triggers human review notification (test with 3 new vendors)
- [ ] QuickBooks entries match invoice data exactly (spot-check 10)
- [ ] Agent handles unreadable invoices gracefully (flags, doesn't guess)

### Staged Approval
- Stage 1: We process 50 historical invoices, verify accuracy
- Stage 2: Client watches live processing of 5 real invoices
- Stage 3: Client runs independently for 5 business days, reports issues

### Timeout Bounds
- Expected: 10 business days from deployment start
- Hard deadline: 15 business days
- If missed: Rescope to manual-assist mode (agent prepares, human confirms)
```

---

## Tiered Advisory Mode

Not all automations are created equal. Some are safe to let the agent run unsupervised. Some should never run without a human in the loop. Use this tiering system for every automation.

### Tier Definitions

| Tier | Risk Level | Supervision | Promotion Timeline | Example |
|------|-----------|-------------|--------------------:|---------|
| **Low** | Low risk, easily reversible | Self-promote after 3 days of clean operation | 3 days | Email sorting, report generation, data lookups |
| **Medium** | Moderate risk, some consequences | Human approves each action for 2 weeks, then auto with audit log | 2 weeks | Invoice processing, appointment scheduling, client communications |
| **High** | High risk, significant consequences | Human approves for minimum 2 weeks, never fully unsupervised | 2 weeks minimum, always monitored | Financial transactions, legal documents, compliance filings |
| **Restricted** | Critical risk, irreversible consequences | Always draft-only, human executes | Never promotes | Tax filings, wire transfers, contract signing, regulatory submissions |

### How Promotion Works

**Low tier promotion (3 days):**
```
Day 1-3: Agent performs task, human reviews every output
Day 4: If zero errors → agent runs autonomously with daily summary
If any errors → reset counter, fix issue, restart 3-day window
```

**Medium tier promotion (2 weeks):**
```
Week 1: Agent prepares action, human approves before execution
Week 2: Same, with audit log review at end of each day
Week 3+: Agent executes autonomously, human reviews audit log daily
If any error at any stage → drop back to full approval mode
```

**High tier (never fully autonomous):**
```
Week 1-2: Agent prepares, human approves every action
Week 3+: Agent prepares, human approves every action
Always: Human spot-checks are mandatory, not optional
Frequency of checks can decrease but never reach zero
```

**Restricted tier (always draft-only):**
```
Always: Agent prepares draft/recommendation
Always: Human reviews, modifies if needed, and executes
Agent never has credentials/access to execute directly
```

### Assigning Tiers

During Round 4 (Solution Design), assign a tier to every automation:

```markdown
| Automation | Tier | Rationale |
|-----------|------|-----------|
| Email triage | Low | Easily reversible, low consequences |
| Invoice entry | Medium | Financial data, but correctable |
| Client billing | High | Direct financial impact on client |
| Tax filing | Restricted | Regulatory, irreversible, penalties |
```

---

## The 6-Week Sell

### The Narrative

Don't sell what the agent does on Day 1. Sell where the client will be after 6 weeks of compounding agent learning.

**Day 1:** The agent knows nothing about the client. It follows templates. It asks for approval on everything. It's slower than doing it yourself.

**Week 2:** The agent knows the client's preferences. It suggests before being asked. Approval rate is 80%+ on first try. It catches things humans miss.

**Week 4:** The agent handles routine tasks autonomously. It only escalates edge cases. The client forgot what it was like to do those tasks manually.

**Week 6:** The agent has built a memory of the business. It anticipates seasonal patterns. It cross-references data across systems. It's doing things the client never thought to automate because it sees patterns they can't.

### The Day-1 vs. Week-6 Comparison

Use this table in client conversations:

| Dimension | Day 1 | Week 6 |
|-----------|-------|--------|
| **Knowledge** | Template only | Deep client-specific memory |
| **Speed** | Slower than manual | 10-100x faster than manual |
| **Accuracy** | 80% (needs review) | 95%+ (exceeds human) |
| **Autonomy** | Everything needs approval | Routine tasks run independently |
| **Scope** | 1-2 narrow tasks | Expanding to adjacent workflows |
| **Value** | "Interesting experiment" | "Can't imagine going back" |

### How to Present This

> "I want to be honest with you — on Day 1, this agent is going to feel like a new employee who needs training. It'll be slower and it'll ask a lot of questions. That's normal. But unlike a human employee, this agent never forgets what it learns, it works 24/7, and every week it gets faster and more accurate. By Week 6, most clients tell us they can't imagine going back. That's what we're building toward."

---

## Model Staggering Explanation

Clients often ask: "Why not just use the most powerful AI for everything?"

### The Staggering Concept

Different tasks need different levels of AI capability:

```
Task Complexity      →  Model Tier
─────────────────────────────────────
Data lookups, formatting   →  Fast/cheap model (Haiku-class)
Email drafting, summaries  →  Mid-tier model (Sonnet-class)
Strategic analysis, complex reasoning  →  Top-tier model (Opus-class)
```

### Client-Friendly Explanation

> "Think of it like staffing. You wouldn't hire a senior partner to file paperwork, and you wouldn't ask an intern to negotiate a contract. We use the right level of AI for each task — fast and cheap for routine work, powerful and thoughtful for complex decisions. This keeps your API costs manageable while making sure the important stuff gets the best thinking."

### Cost Impact Example

```
Without staggering:  All tasks use Opus  →  ~$X/month API costs
With staggering:     80% Haiku, 15% Sonnet, 5% Opus  →  ~$X/5 month API costs
Same quality for complex tasks, 80% cost reduction overall
```

---

## Onboarding Timeline Template

```
Pre-deployment:
  □ Round 1: Pain Points (Day -14)
  □ Round 2: Workflow Mapping (Day -10)
  □ Round 3: Constraints (Day -7)
  □ Round 4: Solution Design (Day -5)
  □ Agreement signed, hardware sourced (Day -3)

Deployment:
  □ Layer 1-4 deployment (Day 0-1)
  □ Layer 5: Day-1 onboarding (Day 2)

Post-deployment:
  □ Daily check-in (Week 1)
  □ Tier promotion reviews (Day 3, Week 2)
  □ Twice-weekly check-in (Weeks 2-4)
  □ Week-6 review and expansion planning
```

---

## Onboarding Anti-Patterns

- **Skipping the diagnostic.** "Just install the agent and we'll figure it out" leads to mismatched expectations and churn.
- **Over-promising Day 1.** If you set expectations for Day 1 that match Week 6 reality, the client will be disappointed for 5 weeks straight.
- **Ignoring organizational constraints.** The tech can be perfect and the deployment will still fail if the team doesn't buy in.
- **Starting with High/Restricted tier tasks.** Always start with a Low tier win to build trust before tackling high-stakes automation.
- **No completion contracts.** Without binary done criteria, "done" becomes a matter of opinion and scope creeps forever.
- **Treating every client the same.** The diagnostic exists because every business is different. Use it.
