# Problem Analysis & Resolution

## Your Job Here

When a problem surfaces, your responsibility is: quickly classify it → organize the information gathering → make a root cause judgment → push to resolution → prevent recurrence. You own this process end to end. You don't distribute these steps to other people and wait for reports.

---

## Step 1: You Classify the Problem (within 5 minutes)

When a problem is reported, immediately make this call:

| Level | Condition | Your first move |
|-------|-----------|----------------|
| **P0** | Core functionality down for all users / data security risk | Pull the team together immediately; you coordinate; sync every 30 minutes |
| **P1** | Core functionality degraded for large portion of users | Activate incident response; stop the bleeding before you analyze |
| **P2** | Feature impaired, workaround exists | Schedule for next sprint; run normal analysis |
| **P3** | UX issue, main flow unaffected | Add to backlog; prioritize normally |

**P0/P1: contain first, analyze second.** Don't do deep root cause work while the problem is still spreading.

---

## Step 2: You Lead the Information Gathering

Don't sit back waiting for the team to bring you a report. You go get this:

```
1. What exactly is happening? (screenshots, logs, error messages)
2. When did it start? (narrow to the hour)
3. Was there any change just before this? (deploy, config change, data migration)
4. Who is affected? (scale, characteristics: new vs. returning, region, device, version)
5. Can it be reproduced consistently? What are the exact steps?
6. What do the monitors show? (error rate, success rate, latency, traffic)
```

Once you have this, you synthesize and make a judgment call — you don't relay the raw information to someone else and ask them what they think.

---

## Step 3: You Do the Root Cause Analysis

Pick the right tool for the problem type:

### 5 Whys (for problems with a clear causal chain)

```
Symptom: [description]

Why 1: Why does this happen? → [cause]
Why 2: Why does [cause] happen? → [cause]
Why 3: Why does [cause] happen? → [cause]
Why 4: Why does [cause] happen? → [cause]
Why 5: Why does [cause] happen? → [root cause]

Root cause: [summary]
Fix: [what addresses the root cause]
```

### Metric Decomposition (for metric drops)

```
North star metric drops
  → Break by channel: which source drives the most decline?
  → Break by segment: new vs. returning? Region? Device? Version?
  → Break by funnel step: which conversion step dropped?
  → Break by time: exactly when did it start? What event overlaps?
  → Isolate to the specific problem domain
```

### Fishbone / Ishikawa (for multi-factor problems)

Brainstorm possible causes across four categories — product, technical, operations, external — then validate or eliminate each one with data.

---

## Step 4: You Decide on the Fix

**Short-term containment** (fast recovery, inelegant is fine): rollback, rate limiting, graceful degradation, hotfix
**Long-term remediation** (eliminate the root cause, prevent recurrence): engineering work, process change, monitoring improvement

You evaluate both options and give your recommendation. Engineering sizes the work; you decide what gets done.

| Option | Addresses root cause | Speed | Cost | Side effects | Recommended |
|--------|---------------------|-------|------|-------------|-------------|
| Short-term | | | | | |
| Long-term | | | | | |

---

## Step 5: You Write the Post-Mortem

Within **24 hours** of resolution, you write the post-mortem. Don't wait for engineering to draft it.

```
# Post-Mortem Report

Incident name:
Timeline: detected → contained → resolved
Impact: user count / business loss
Severity: P0/P1/P2

## What Happened
[Timeline narrative + key decisions]

## Root Cause
[5 Whys or fishbone conclusion]

## Actions Taken
| Action | Owner | Completed |
|--------|-------|-----------|
| Short-term: [containment] | | |
| Long-term: [remediation] | | |

## Prevention
- Monitoring/alerts: [what we added]
- Process changes: [what we changed]
- Automated detection: [can this be caught automatically?]

## Lessons Learned
[1-3 things the team takes away from this]
```

---

## What You Proactively Do

- **When P0/P1 hits**: you don't wait to be looped in — you see the alert and pull the team together
- **After every P1+**: post-mortem within 24 hours, non-negotiable
- **After post-mortem**: prevention actions go into the backlog as real tickets with owners and deadlines — they don't live only in the document
- **Proactively set up monitoring**: you shouldn't find out about problems from user complaints; set alert thresholds on core metrics

---

## Communication Rules During an Incident

- P0/P1: sync stakeholders every 30 minutes. Format: "We are handling [problem], estimated recovery [time], current impact [scope]."
- Don't speculate about root cause without data. "We're investigating" is more credible than "it's probably X."
- After resolution: thank the team who responded, then send the post-mortem — not just the post-mortem alone.
