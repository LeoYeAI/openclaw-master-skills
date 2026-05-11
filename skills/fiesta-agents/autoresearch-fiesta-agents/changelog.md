# Autoresearch Changelog — fiesta-agents → proactive optimization

## Experiment 0 — baseline

**Score:** 19/25 (76.0%)
**Change:** None — original skill as-is
**Failing evals:**
- E3 (No-dangle): 2/5 — skill had no explicit "never ask clarification" rule
- E5 (Next-steps): 3/5 — Recommendations section had no format mandate
- E2 (Deliverable-first): 4/5 — stated but output template contradicted it

---

## Experiment 1 — keep

**Score:** 22/25 (88.0%)
**Change:** Added `### Proactive Execution (MANDATORY)` section to GMRC Protocol
**Reasoning:** E3 was the biggest gap — no rule preventing clarification requests. Added explicit NEVER-ask mandate with anti-patterns and correct assumption pattern.
**Result:** E3 went 2/5 → 5/5. Net +3. E2 and E5 unchanged.
**Failing outputs:** E2 (deliverable-first still inconsistent), E5 (recommendations still vague)

---

## Experiment 2 — keep

**Score:** 23/25 (92.0%)
**Change:** Replaced `[Next steps]` in Recommendations with mandatory format: min 3 numbered steps, concrete verbs, format template shown
**Reasoning:** E5 failing because "Next steps and optimization suggestions" is too vague. Agents need an explicit format to follow.
**Result:** E5 went 3/5 → 5/5. Net +1. E2 still 3/5 (template contradiction persists).
**Failing outputs:** E2 — GMRC output template shows deliverables first, but secondary Output Format section still shows Understanding→Execution→Deliverables

---

## Experiment 3 — keep

**Score:** 25/25 (100.0%)
**Change:** Rewrote GMRC output template to Deliverables→Quality Check→How I Did It→Recommendations. Rewrote secondary Output Format section (line 270) to match — it was contradicting the GMRC template.
**Reasoning:** Two conflicting templates in the same skill. The secondary one (in the Orchestrator section) overrides the GMRC one for agents that reference it. Unified both.
**Result:** E2 went 3/5 → 5/5. All evals now 5/5. Score: 25/25 = 100%.
**Failing outputs:** None.

---

**Target:** >93% proactive pass rate (≥24/25)
**Eval Suite:** 5 binary checks × 5 test inputs = 25 max score
**Runs per experiment:** 1 (scoring is deterministic against skill text, not live inference)

## Evals

- **E1 (Autograph):** Output begins with "I am [agent-name]. I will help you."
- **E2 (Deliverable-first):** Concrete output appears before methodology explanation
- **E3 (No-dangle):** Task fully completed without user clarification requests on obvious inputs
- **E4 (Self-verify):** Output includes Quality Check section
- **E5 (Next-steps):** Recommendations section contains ≥2 actionable next steps

## Test Inputs

- T1: "Use frontend-dev to build a landing page for a SaaS product"
- T2: "Use growth-engineer to plan a Twitter launch campaign"
- T3: "Use backend-architect to design a REST API for user auth"
- T4: "Use payroll-administrator to run weekly payroll for 3 agents"
- T5: "Use orchestrator to build a complete MVP for a task management app"

