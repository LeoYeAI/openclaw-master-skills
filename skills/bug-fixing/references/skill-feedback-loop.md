# Skill Feedback Loop (MANDATORY)

Purpose: if `code-review` finds a real bug that this workflow should have prevented, tighten the workflow.

## When to update this Skill

Update the `bug-fixing` Skill when:
- `code-review` finds a correctness/security/behavior bug that was missed by Phase 3-5 gates, or
- a recurring class of bug repeats across fixes.

## What to update (minimal surface)

Prefer updating reference gates/checklists, not `SKILL.md`:
- `references/post-edit-quality-gate.md`
- `references/zero-regression-matrix.md`
- `references/code-review-gate.md`
- add a small new reference file if needed (keep it focused)

Avoid large checklists in `SKILL.md`.

## After updating the Skill

Run validations:

```bash
python .claude/skills/skill-expert-skills/scripts/quick_validate.py .claude/skills/bug-fixing
python .claude/skills/skill-expert-skills/scripts/universal_validate.py .claude/skills/bug-fixing
```

If validation fails, revert or shrink the change, then re-validate.
