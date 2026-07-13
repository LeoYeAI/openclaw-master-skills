# Heuristic Evaluation Template

Template for conducting heuristic evaluations of interfaces against established usability principles.

## How to Use

- Use when you need systematic expert feedback against a **standard set of heuristics**.
- Can be done by multiple evaluators independently to improve coverage.

## Heuristic Evaluation Template

```markdown
# Heuristic Evaluation – [Product / Flow]

Evaluator: [...]
Date: [...]
Version / build: [...]

## 1. Objectives

- What aspects of the UI/UX are being evaluated?
  - [...]
- What decisions will results inform?
  - [...]

## 2. Heuristics Set

List the heuristic framework being used (e.g., Nielsen’s 10 usability heuristics):

1. Visibility of system status
2. Match between system and the real world
3. User control and freedom
4. Consistency and standards
5. Error prevention
6. Recognition rather than recall
7. Flexibility and efficiency of use
8. Aesthetic and minimalist design
9. Help users recognize, diagnose, and recover from errors
10. Help and documentation

## 3. Scope

- Screens / flows included:
  - [...]
- User scenarios:
  - [...]

## 4. Findings Log

For each issue, capture:

- ID:
- Location (screen/flow, device, state):
- Heuristic violated:
- Severity rating (e.g., 0 = cosmetic, 1 = minor, 2 = major, 3 = critical):
- Description and rationale:
- Suggested improvement:

Example entry:

- ID: H‑01
- Location: Checkout – payment step (desktop)
- Heuristic violated: Visibility of system status
- Severity: 2 (major)
- Description: No feedback is shown while payment is being processed; users click the button multiple times and become unsure if it worked.
- Recommendation: Add a clear loading state and confirmation message; prevent double submissions.
```

## Key References for Heuristic Evaluation

- Jakob Nielsen & Rolf Molich, original work on heuristic evaluation and the 10 usability heuristics.
- Jakob Nielsen, *Usability Engineering* – chapters on heuristic evaluation.
- Nielsen Norman Group articles on heuristic evaluation and practical guidelines for applying heuristics (`https://www.nngroup.com/articles/heuristic-evaluation/`). 

