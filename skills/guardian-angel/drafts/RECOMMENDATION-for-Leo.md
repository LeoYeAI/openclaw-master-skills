# Guardian Angel v2.0: Recommendation Summary

**Prepared for:** Leo Linbeck III  
**Date:** February 3, 2026  
**Status:** Draft for Review

---

## Executive Summary

Following your direction to reconceptualize Guardian Angel as a System 1/System 2 moral trigger mechanism, I deployed four sub-agents to develop alternative rubrics. Each approached the problem from a different angle:

1. **Pattern Triggers** — Spam-filter style keyword/pattern matching
2. **Reversibility/Commitment** — 2-axis matrix based on permanence
3. **Action Categories** — Taxonomy of action types with pre-assigned risk
4. **Affected Parties** — Thomistic ordo caritatis and relationship duties

**Key insight:** These approaches are complementary, not competing. I've synthesized them into a **layered gate architecture** that:

- Handles 95%+ of actions in milliseconds (System 1)
- Reliably identifies the few requiring deliberate analysis (System 2)
- Maintains Thomistic grounding throughout

---

## The Proposed Architecture

```
ACTION
   │
   ▼
┌─────────────────────────────────────┐
│ GATE 0: INTRINSIC EVIL (pass/fail)  │  ← Hard list, instant check
└───────────────┬─────────────────────┘
                │
                ▼
┌─────────────────────────────────────┐
│ GATE 1: PATTERN TRIGGERS            │  ← Fast keyword/pattern scan
│         (0-2 pass, 3+ escalate)     │
└───────────────┬─────────────────────┘
                │
                ▼
┌─────────────────────────────────────┐
│ GATE 2: REVERSIBILITY × COMMITMENT  │  ← Quick matrix lookup
│         (Low R×C pass, high escalate)│
└───────────────┬─────────────────────┘
                │
                ▼
        ✅ PROCEED (most actions end here)
        
        OR → GATE 3: Full System 2 Analysis
             (Categories, Affected Parties, 
              Consent, Vulnerability, Scandal,
              Double Effect if applicable)
             → 🔶 PAUSE / 🛑 ESCALATE
```

---

## Changes from v1.0

### What Stays the Same
- Intrinsic evil check as first gate (pass/fail)
- Thomistic three sources: Object, Intention, Circumstances
- Double effect analysis when applicable
- Core principle: *Bonum ex integra causa*

### What Changes

| Aspect | v1.0 | v2.0 |
|--------|------|------|
| **Default disposition** | Analyze everything | Pass most, analyze few |
| **Primary mechanism** | Clarity × Stakes scoring | Layered gates |
| **Speed** | Every action deliberated | 95%+ instant resolution |
| **When System 2 engages** | Always | Only when triggers fire |
| **Intrinsic evil list** | 8 categories | 10 categories (+pornography, +adultery) |

### New Intrinsic Evil Categories

As you specified, I've added:

- **Pornography** — producing, distributing, or deliberately procuring sexually explicit material
- **Adultery** — facilitating extramarital sexual relations

Clarifying notes ensure these don't over-trigger on clinical/educational contexts or pastoral discussions.

---

## Key Insights from Each Sub-Agent

### From Pattern Triggers
**"Run like a spam filter, not a philosophy seminar."**

Best contribution: The linguistic and structural trigger taxonomy. Certain word patterns (secrecy language, urgency, rationalization) reliably indicate moral risk even before full analysis. The counting mechanism (0-2 pass, 3+ flag) is elegant.

### From Reversibility/Commitment
**"Deliberate before creating realities that are hard to uncreate."**

Best contribution: The 2×2 insight that both axes matter. An irreversible action with no commitment (reading a secret) is different from a reversible action with high commitment (verbal promise). The matrix captures this compactly.

Key insight: "Reversibility is practical, not theoretical. 'You can always apologize' doesn't make harm reversible."

### From Categories
**"Types of acts have moral character — pre-classify, then only deliberate on edge cases."**

Best contribution: The recognition that most actions fall into routine categories that can be pre-evaluated. Sending a calendar reminder doesn't need the same analysis as sending a resignation letter.

Thomistic grounding: Maps to *species of act* — the kind of action determines much of its moral character.

### From Affected Parties
**"WHO is affected and WHAT you owe them is the heart of the matter."**

Best contribution: The rigorous *ordo caritatis* framework. Different relationships carry different duties. The vulnerability multipliers are carefully calibrated. The consent/knowledge matrix is thorough.

Key insight: "Enemies are owed equal justice — adversarial relationship doesn't reduce moral weight."

---

## Testing the Integrated System

I compiled 25 edge cases from all four approaches and validated that the integrated rubric:

✓ **Passes quickly** on routine actions (reminders, research, reservations)  
✓ **Pauses appropriately** on moderately risky actions (scheduled messages, professional emails)  
✓ **Escalates correctly** on genuinely complex cases (sharing others' info, public statements, competing duties)  
✓ **Stops hard** on intrinsic evils (lying, adultery facilitation, pornography)  
✓ **Handles gray areas** with appropriate humility (dementia care, whistleblowing, eulogies for difficult people)

Full edge case analysis: `drafts/edge-cases-consolidated.md`

---

## Open Questions for Your Review

### 1. Gate Thresholds
Current proposal: 3+ pattern triggers → escalate. Should this be adjustable per-domain? (e.g., lower threshold for professional communications, higher for personal)

### 2. Financial Trigger
What dollar threshold should trigger automatic escalation? Suggested: >$100 or >1% of typical discretionary spending.

### 3. Pre-authorized Patterns
Should certain action types be permanently pre-authorized (e.g., "calendar reminders for family members always pass")? If so, how do we configure this?

### 4. Intrinsic Evil Scope
The pornography and adultery additions have clarifying notes to avoid over-triggering. Do these scopes feel right to you?

- Pornography: Includes generation/distribution/procurement. Excludes clinical/educational contexts.
- Adultery: Includes facilitation/arrangement. Excludes discussion of past events or counseling contexts.

### 5. Competing Duties Handling
When legitimate obligations conflict (employer vs. friend, truth vs. mercy), the current proposal adds +15 to the score and flags for human judgment. Is this the right approach, or should competing duties always escalate regardless of score?

### 6. Logging Level
How much should be logged by default? Options:
- Minimal (only escalated actions)
- Standard (all Gate 2+ decisions)
- Comprehensive (every action through all gates)

---

## Files for Your Review

1. **`drafts/SKILL-v2-draft.md`** — The complete integrated skill document
2. **`drafts/edge-cases-consolidated.md`** — 25 test cases with expected outcomes
3. **`drafts/synthesis-notes.md`** — Notes on how I combined the four approaches
4. **`references/pattern-triggers.md`** — Full trigger taxonomy (from sub-agent 1)
5. **`references/reversibility-commitment-rubric.md`** — R×C matrix detail (from sub-agent 2)
6. **`references/category-rubric.md`** — Action category detail (from sub-agent 3)
7. **`references/affected-parties-rubric.md`** — Full parties analysis (from sub-agent 4)

---

## Recommendation

I recommend adopting the layered gate architecture as specified in `SKILL-v2-draft.md`. The key advantages:

1. **Matches your System 1/System 2 vision** — lightweight trigger, expensive analysis only when needed
2. **Preserves Thomistic rigor** — nothing lost from the moral framework
3. **Scales efficiently** — most actions resolve instantly
4. **Fails safe** — multiple opportunities to catch problems before they slip through
5. **Configurable** — thresholds and pre-authorizations can be tuned

Once you've reviewed and provided direction on the open questions, I can finalize the skill and update the references.

---

*Prepared by Reginald Jeeves, February 3, 2026*
