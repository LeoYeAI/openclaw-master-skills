# Collaboration Rules

Collaboration is optional and should be rare in the MVP.

## Default

The main agent should do the task itself.

## Escalate only when clearly helpful

Consider collaboration only when one or more of these are true:

- two or more apps need coordinated attention
- two or more windows need simultaneous tracking
- copy/compare/transfer work is easier split by role
- repeated single-agent attempts have already failed
- a subtask is well-bounded and can be delegated cleanly

## Control rule

Even in collaboration mode, keep the main agent as controller.

- the main agent defines the subtask
- the sub-agent returns observations or a bounded result
- the main agent decides the next step

## Avoid in MVP

Do not overbuild collaboration before the single-agent flow is stable.
