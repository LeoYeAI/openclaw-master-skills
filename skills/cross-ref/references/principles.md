# Cross-Ref Principles

Hard constraints for every analysis run. If a step conflicts with these, the
principle wins.

## Evidence over narrative

- Never classify duplicates from title similarity alone. Inspect body content,
  error messages, and failure paths.
- A shared keyword doesn't make two items related. Two items are related when
  they share a root cause or fix the same broken behavior.

## Confidence requires specifics

- **High**: Shared error path, same component, overlapping fix. You can explain
  exactly what makes these the same problem.
- **Medium**: Same area of the codebase, similar symptoms, but different
  reproduction or approach. Plausibly related.
- **Low**: Keyword overlap or label match only. Might be coincidence.
- If you can't articulate the shared root cause in one sentence, it's not
  "high" confidence.

## Credit preservation

- Always mention the PR author when commenting about a link.
- Never frame a duplicate as wasted work. Both contributions matter.
- Use language like "related" and "addresses the same area", not "copied"
  or "redundant".

## Conservative defaults

- When uncertain, classify as "related" not "duplicate".
- Better to miss a link than to create a false one.
- An unposted comment costs nothing. A wrong comment erodes trust.

## Reversibility

- Comments can't be undone. Every comment should include a path to
  correct the link if it's wrong ("if this doesn't look right, let me know").
