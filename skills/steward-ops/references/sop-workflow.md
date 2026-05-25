# SOP & Workflow Management

## Purpose
Standard Operating Procedures are the operating system of the business. Without them, every task is
approached from scratch. With them, routine operations run on autopilot, delegation becomes possible,
and quality stays consistent. Steward creates, maintains, and enforces SOPs for all recurring operations.

---

## SOP Creation Framework

### When to Create an SOP
Create an SOP when:
- A task is performed more than 3 times
- A task involves multiple steps that must happen in sequence
- A task is delegated (or could be delegated) to another person or agent
- A mistake on a task would have meaningful consequences
- A task has dependencies that must be tracked
- The principal says "how did we do this last time?"

### SOP Structure Template
Every SOP follows this structure:

```markdown
# SOP: [Process Name]

**Version**: [X.X]
**Last Updated**: [Date]
**Owner**: [Who maintains this SOP]
**Frequency**: [How often this process runs]
**Estimated Time**: [How long the process takes]
**Priority Level**: [Normal | High | Critical]

## Purpose
[1-2 sentences: Why this process exists and what outcome it produces]

## Trigger
[What initiates this process — time-based, event-based, request-based]

## Prerequisites
- [ ] [What must be in place before starting]
- [ ] [Required access, tools, or information]

## Steps

### Step 1: [Action Name]
**Do**: [Specific action in imperative form]
**How**: [Detailed instructions]
**Tool/Location**: [Where to do this — URL, app, file path]
**Expected Result**: [What you should see when this step is done correctly]
**If Error**: [What to do if something goes wrong]

### Step 2: [Action Name]
...

### Step 3: [Action Name]
...

## Verification
- [ ] [How to verify the process completed successfully]
- [ ] [Quality check — what to look for]

## Post-Process
- [ ] [What to do after the process is complete — notify someone, update a tracker, etc.]

## Exceptions & Edge Cases
- **If [condition]**: [What to do differently]
- **If [error]**: [Recovery steps]

## Related SOPs
- [Link to related processes]

## Revision History
| Date | Version | Change | Author |
|------|---------|--------|--------|
| [Date] | 1.0 | Initial creation | [Name] |
```

---

## Core Business SOPs to Build

### Daily Operations SOPs

**SOP: Morning Briefing Production**
- Trigger: Every day at 6:30 AM
- Steps: Scan email → Check calendar → Check deadlines → Check platforms → Compile briefing
- Output: Morning briefing document delivered by 7:00 AM

**SOP: Inbox Processing**
- Trigger: Morning briefing, midday, and end-of-day
- Steps: Scan all accounts → Classify → Prioritize → Extract actions → Report
- Output: Triage report with action items

**SOP: End-of-Day Review**
- Trigger: Every day at 5:00 PM
- Steps: Review completed tasks → Update task list → Check tomorrow's calendar → Compile EOD summary
- Output: End-of-day summary document

### Weekly Operations SOPs

**SOP: Weekly Planning (Monday)**
- Trigger: Monday 7:00 AM
- Steps: Review last week → Set this week's priorities → Check all deadlines → Compile weekly plan
- Output: Weekly kickoff briefing

**SOP: Weekly Admin Batch (Wednesday)**
- Trigger: Wednesday 2:00 PM
- Steps: Process batched admin items → File documents → Update trackers → Review subscriptions
- Output: Admin batch completion report

**SOP: Week Wrap-Up (Friday)**
- Trigger: Friday 4:00 PM
- Steps: Review week → Update metrics → Preview next week → Compile wrap-up
- Output: Weekly summary and next week preview

### Monthly Operations SOPs

**SOP: Monthly Review**
- Trigger: 1st of each month
- Steps: Compile monthly metrics → Review financials → Audit subscriptions → Update deadline registry → Produce monthly report
- Output: Monthly operations report

**SOP: Subscription Audit**
- Trigger: 15th of each month
- Steps: List all subscriptions → Check usage → Calculate costs → Identify savings → Produce audit
- Output: Subscription audit report with recommendations

### Platform-Specific SOPs

**SOP: KDP Session Renewal**
- Trigger: 7 days before session expiration
- Steps: Log into KDP → Re-authorize → Verify product access → Update session tracker
- Output: Confirmation that session is renewed and products are accessible

**SOP: Product Listing Health Check**
- Trigger: Weekly (varies by platform)
- Steps: Check each platform → Verify listing active → Check metrics → Flag issues
- Output: Platform health report

---

## Workflow Automation Design

### Automation Identification
Look for workflows that can be automated:
- **Rule-based decisions**: If X then Y — no judgment needed
- **Data routing**: Moving information from one system to another
- **Scheduled actions**: Things that happen at the same time every day/week/month
- **Trigger-response patterns**: When event A happens, always do B

### Automation Template
```
AUTOMATION: [Name]
Trigger: [What starts this automation]
Condition: [Any conditions that must be met]
Action: [What the automation does]
Output: [What gets produced or changed]
Error Handling: [What happens if the automation fails]
Human Checkpoint: [Does this need human approval at any point?]
```

### Workflow Types

**Sequential Workflow**: Steps happen in order
```
Step 1 → Step 2 → Step 3 → Output
```

**Parallel Workflow**: Steps can happen simultaneously
```
Step 1 ──→ Step 2a ──→ Step 3 → Output
       └─→ Step 2b ──┘
```

**Conditional Workflow**: Path depends on conditions
```
Step 1 → [Condition?]
           ├─ Yes → Step 2a → Output A
           └─ No  → Step 2b → Output B
```

**Loop Workflow**: Repeat until condition met
```
Step 1 → Step 2 → [Done?] ─ No → Step 1
                      └─ Yes → Output
```

---

## Checklist Management

### Operational Checklists
For complex processes, maintain living checklists:

**Daily Ops Checklist**
- [ ] Morning briefing reviewed
- [ ] Email triaged across all accounts
- [ ] Calendar reviewed for today
- [ ] High-priority tasks identified
- [ ] Platform status checked
- [ ] Deadline registry reviewed

**Weekly Ops Checklist**
- [ ] Monday planning complete
- [ ] All weekly tasks assigned/scheduled
- [ ] Mid-week admin batch processed
- [ ] Week-end review complete
- [ ] Next week previewed and planned

**Monthly Ops Checklist**
- [ ] Monthly metrics compiled
- [ ] Financial reconciliation complete
- [ ] Subscription audit done
- [ ] Deadline registry fully updated
- [ ] SOPs reviewed and updated
- [ ] File organization maintained

### Checklist Best Practices
- Each item is a single, verifiable action
- Items are ordered in execution sequence
- Include time estimates for planning
- Include links to tools/resources needed for each step
- Mark which items can be delegated
- Track completion rates to identify bottlenecks

---

## Process Improvement

### Identifying Improvement Opportunities
Steward watches for signals that a process needs improvement:
- **Time bloat**: Process is taking longer than it used to
- **Error rate**: Mistakes are increasing
- **Bottlenecks**: One step consistently holds up the rest
- **Skip rate**: Steps being skipped (suggests they're unnecessary or unclear)
- **Workarounds**: People finding informal shortcuts (suggests the formal process is broken)
- **Complaints**: Anyone involved says the process is painful

### Process Improvement Protocol
1. Identify the problem (what's broken or slow)
2. Measure the current state (how long, how many errors, where are the delays)
3. Analyze root causes (why is this happening)
4. Design the improvement (what changes would fix it)
5. Test the change (run the new process and compare)
6. Implement (update the SOP, communicate the change)
7. Monitor (verify the improvement holds)

### Quarterly SOP Review
Every quarter, review all active SOPs:
```markdown
## SOP Review — [Quarter Year]

### Active SOPs: [count]

### Status:
| SOP | Last Used | Last Updated | Status | Action |
|-----|-----------|-------------|--------|--------|
| [Name] | [date] | [date] | Current ✅ | None |
| [Name] | [date] | [date] | Needs Update 🟡 | [what changed] |
| [Name] | 3+ months ago | [date] | Unused ❓ | Review necessity |
| [Name] | [date] | 6+ months ago | Stale 🟠 | Update |

### New SOPs Needed:
- [Process that doesn't have an SOP yet but should]

### SOPs to Retire:
- [Process that's no longer relevant]
```

---

## Runbook vs SOP vs Checklist

Understanding when to use which:

| Tool | When | Detail Level | Used For |
|------|------|-------------|----------|
| **SOP** | Complex, recurring process with decisions | High — step-by-step with context | Training, delegation, quality control |
| **Checklist** | Known process, needs verification | Low — just the items | Execution, compliance, nothing missed |
| **Runbook** | Emergency or infrequent high-stakes process | Very high — every contingency | Incident response, complex migrations |

---

## Onboarding New Processes

When a new recurring process is identified:
1. Document the first execution in detail
2. Note any decisions made and why
3. Create a draft SOP from the execution notes
4. Run the SOP next time the process occurs
5. Refine based on actual execution
6. Finalize after 3 successful executions
7. Add to the appropriate operational rhythm (daily/weekly/monthly)
