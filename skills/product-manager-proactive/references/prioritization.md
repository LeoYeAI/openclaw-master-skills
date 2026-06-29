# Prioritization

## Your Job Here

Prioritization is one of the PM's core decision rights. You make this call — you don't hand a scoring framework to someone else and let them decide. Use the framework to structure your thinking, then give a clear verdict.

---

## Your Decision Process

**Step 1: Clarify the constraints**
- How much engineering capacity is available this sprint? (person-days / person-weeks)
- Are there hard external deadlines or business commitments?
- Which requirements have dependencies (must be done together)?

**Step 2: Fast filter with MoSCoW**
Bucket everything first to reduce the number of items needing deep analysis:
- **Must Have**: without it, we can't ship, or there's a compliance/security risk
- **Should Have**: important but not blocking
- **Could Have**: nice to have
- **Won't Have (this time)**: explicitly deferred — not "never," just "not now"

Only run RICE scoring on Must Have and Should Have.

**Step 3: Score with RICE and give your ranked list**

Calculate RICE for each item, then deliver your final prioritized order with reasoning.

---

## RICE Framework

**Score = (Reach × Impact × Confidence) / Effort**

| Dimension | Definition | How to score |
|-----------|-----------|-------------|
| **Reach** | Users/events affected per cycle | Absolute number (e.g., 5,000 users/month) |
| **Impact** | Effect on each user | 3=massive / 2=high / 1=medium / 0.5=low / 0.25=minimal |
| **Confidence** | How sure you are of the above | 100%=data-backed / 80%=reasoned / 50%=gut |
| **Effort** | Total person-months across all roles | Actual estimate from engineering |

Higher score = higher priority.

**Example:**

| Requirement | Reach | Impact | Confidence | Effort | Score | Your call |
|-------------|-------|--------|------------|--------|-------|-----------|
| Req A | 10,000 | 2 | 80% | 3 | 5,333 | Ship this sprint |
| Req B | 5,000 | 3 | 60% | 1 | 9,000 | Ship this sprint (top pick) |
| Req C | 2,000 | 1 | 100% | 0.5 | 4,000 | Next sprint |

---

## Quick Tool: 2×2 Matrix

Use this for rapid visualization or when communicating with leadership:

```
High value
   |  [Do now]          [Plan for later]
   |  High value/Low cost  High value/High cost
   |
   |  [If time allows]  [Don't do]
   |  Low value/Low cost   Low value/High cost
   |________________________________
                              High cost
```

---

## Give a Decision, Not a List of Options

After scoring, your output should sound like:

> "My decision for this sprint: build Req B and Req A, defer Req C. Reasoning: B has the highest RICE score and directly moves the Q2 ARR target; A is a prerequisite for B. C affects too few users to justify the cost this cycle. If anyone believes C must be in this sprint, I need a specific business reason."

**When someone pushes to insert a new requirement:**
1. Ask: "If this comes in, what comes out?" — capacity is fixed
2. If the answer is "everything is a priority": escalate to whoever holds resource authority; don't absorb the conflict yourself
3. If there's a genuine urgent business reason: re-evaluate, explicitly re-rank, notify all affected parties

---

## Communicating Priority Decisions to Stakeholders

```
Re: [Requirement name] scheduling decision

Decision: Scheduled for [time period], not this sprint.

Reasoning:
- The highest-RICE item this sprint is [Req X], scoring [Y]
- [Requirement name] scores [Z]; the main gap is [reach/confidence/effort]

To move this up the list, I'd need:
- Additional data on user impact (quantified as much as possible), or
- A specific business commitment (e.g., "shipping by Q2 closes $X in deals")

Next priority review: [date]
```

---

## What You Proactively Do

- Re-rank the backlog at the start of every sprint — don't wait to be asked
- At the start of each quarter, align with business stakeholders to confirm strategic direction hasn't shifted
- When external circumstances change (competitive moves, goal updates), proactively update priorities and notify the team
- Regularly trim the backlog: requirements sitting unscheduled for 3+ months should be closed or re-evaluated
