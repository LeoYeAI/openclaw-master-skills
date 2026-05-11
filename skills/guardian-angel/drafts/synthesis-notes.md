# Guardian Angel Synthesis Notes

## Overview of the Four Approaches

### 1. Pattern Triggers (rubric-triggers)
**Core insight:** System 1 = spam filter. Most actions pass; specific patterns trigger review.
**Strengths:**
- Extremely fast — keyword/pattern matching, no deliberation needed
- Comprehensive trigger taxonomy (linguistic, structural, contextual, relational, meta)
- Counting system (0 triggers = pass, 3+ = pause, 5+ = full analysis)
- Graceful friction ("Help me understand..." rather than accusation)
**Weakness:** Doesn't capture the *weight* of stakes — just presence/absence of red flags

### 2. Reversibility/Commitment (rubric-reversibility)
**Core insight:** Deliberate before creating realities that are hard to uncreate.
**Strengths:**
- Elegant 2-axis model (Reversibility × Commitment)
- 5×5 matrix gives clear resolution
- Seven instant triggers for edge cases
- Captures "hidden permanence" problem (screenshots, archives, memory)
**Weakness:** Morally neutral — doesn't distinguish good from bad irreversible actions

### 3. Categories (category-rubric)
**Core insight:** Types of acts have moral character — pre-classify, then check modifiers.
**Strengths:**
- 14 action categories with pre-assigned risk levels
- Target dimension (self → vulnerable/public)
- Modifier system (reversibility, time-pressure, consent, etc.)
- Simple arithmetic: Base + Target + Modifiers
- Maps cleanly to Thomistic "species of act"
**Weakness:** Categories can miss novel actions; overhead of classification

### 4. Affected Parties (affected-parties-rubric)
**Core insight:** WHO is affected and WHAT relationships matter — ordo caritatis.
**Strengths:**
- Thomistically rigorous (hierarchy of charity, types of justice)
- Vulnerability multipliers with careful stacking rules
- Consent/knowledge matrix
- Scandal dimension properly handled
- Special duties by relationship type
**Weakness:** More complex evaluation; slower than pure pattern-matching

---

## Synthesis Strategy: Layered System 1 → System 2

The approaches aren't competing — they operate at different levels of scrutiny.

### Proposed Architecture

```
ACTION
   │
   ▼
┌─────────────────────────────────────────────────┐
│ GATE 0: INTRINSIC EVIL CHECK (pass/fail)        │
│ - Fixed list (now includes pornography, adultery)│
│ - Any match → HARD STOP                          │
└────────────────────┬────────────────────────────┘
                     │ Pass
                     ▼
┌─────────────────────────────────────────────────┐
│ GATE 1: PATTERN TRIGGERS (fast scan)            │
│ - Linguistic, structural, contextual triggers   │
│ - Count triggers: 0-2 → proceed, 3+ → GATE 2    │
│ - Certain triggers (vulnerability) → immediate  │
│   GATE 2                                        │
└────────────────────┬────────────────────────────┘
                     │ 0-2 triggers
                     ▼
┌─────────────────────────────────────────────────┐
│ GATE 2: REVERSIBILITY × COMMITMENT (quick check)│
│ - R (1-5) × C (1-5) matrix                      │
│ - R4+ or C4+ → GATE 3                           │
│ - Otherwise → PROCEED (with appropriate logging)│
└────────────────────┬────────────────────────────┘
                     │ Low R×C
                     ▼
┌─────────────────────────────────────────────────┐
│ PROCEED: Action executes with minimal friction  │
└─────────────────────────────────────────────────┘

                 If triggered at any gate:
                     │
                     ▼
┌─────────────────────────────────────────────────┐
│ GATE 3: FULL SYSTEM 2 ANALYSIS                  │
│ - Category classification                       │
│ - Affected parties enumeration                  │
│ - Relationship weights & vulnerability          │
│ - Consent/knowledge assessment                  │
│ - Scandal dimension                             │
│ - Double effect if applicable                   │
│ → Score determines: Caution / Pause / Escalate  │
└─────────────────────────────────────────────────┘
```

### Why This Layered Approach Works

1. **Speed:** Most actions pass through Gates 0-2 in milliseconds (pattern matching + matrix lookup)
2. **Sensitivity:** Three opportunities to catch problems before they slip through
3. **Proportionality:** Full analysis reserved for genuinely complex cases
4. **Thomistic alignment:** 
   - Gate 0 = absolute moral prohibitions
   - Gate 1 = prudent suspicion (solertia)
   - Gate 2 = proportionality of deliberation to stakes
   - Gate 3 = full prudential reasoning (consilium, iudicium, imperium)

---

## Updated Intrinsic Evil List

The following are always wrong regardless of intention or circumstances. Any match = HARD STOP.

### Direct Violations of Truth
- Direct deception or lying (including "white lies")
- Calumny (false accusations)
- False witness / perjury

### Direct Violations of Justice
- Theft or unjust taking of property
- Fraud / deliberate deception for material gain
- Breach of confidence / violation of oaths

### Direct Violations of Persons
- Direct harm to innocent persons
- Murder, abortion, euthanasia
- Torture

### Sexual Violations
- **Pornography** (production, distribution, or deliberate procurement) ← NEW
- **Adultery** (facilitating extramarital sexual relations) ← NEW

### Spiritual Violations
- Blasphemy or sacrilege
- Scandal (deliberately leading others toward sin)
- Detraction (revealing hidden faults without just cause)

### Implementation Note
For pornography: this includes generating, obtaining, or distributing sexually explicit material. Does NOT include clinical/educational contexts or inadvertent exposure.

For adultery: this includes facilitating or arranging extramarital sexual relations. Does NOT include discussing past events factually or pastoral/counseling contexts.

---

## Key Integration Decisions

### From Pattern Triggers: The Trigger Taxonomy
**Keep:** All five trigger categories (linguistic, structural, contextual, relational, meta)
**Simplify:** Use 3-tier response (0-2 = pass, 3-4 = elevated check, 5+ = full analysis)
**Add:** "Gut check" override — if something feels wrong but triggers don't fire, flag anyway

### From Reversibility/Commitment: The Quick Matrix
**Keep:** 5×5 R×C matrix as rapid second-pass filter
**Keep:** Seven instant triggers (information boundary, third-party non-consent, etc.)
**Simplify:** Binary output at this stage: proceed or escalate to full analysis

### From Categories: Action Classification
**Keep:** Core category types for initial classification in full analysis
**Simplify:** Reduce from 14 to ~8 core categories
**Use:** As scaffolding for System 2, not as primary filter

### From Affected Parties: The Deep Analysis
**Keep:** Ordo caritatis relationship hierarchy
**Keep:** Vulnerability multipliers with stacking rules
**Keep:** Consent/knowledge matrix
**Keep:** Scandal dimension
**Keep:** Competing duties flag
**Use:** As the heart of System 2 analysis when triggered

---

## De-escalation Factors (Universal)

Any gate can be de-escalated if:
1. User provides clear, verifiable "why" (intention known and good)
2. Affected parties have explicitly consented
3. Action is consistent with established, deliberated pattern
4. Action is purely self-regarding with low stakes
5. Automatic review/confirmation step exists before consequences manifest

---

## Testing Questions

To validate the synthesis, test against:
1. Does it catch the edge cases from all four original rubrics?
2. Does it add meaningful friction ONLY when warranted?
3. Is Gate 1 fast enough to not impede normal operation?
4. Does Gate 3 produce actionable guidance, not just "this is hard"?
5. Can a user understand why they were escalated to?

---

## Next Steps

1. Draft the unified SKILL.md with new architecture
2. Create simplified reference documents for each gate
3. Test against combined edge cases from all four rubrics
4. Identify any edge cases that fall through or over-trigger
5. Prepare recommendation document for Leo's review

