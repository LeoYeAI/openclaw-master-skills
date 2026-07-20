# Contributing Guide

Thanks for your interest in contributing to `deepsearch-mpro`!

This document defines a lightweight workflow for proposing changes, reporting issues, and submitting pull requests.

## 1. How to Contribute

You can contribute in multiple ways:

- Improve documentation (`README.md`, `SKILL.md`, `references/`)
- Add or refine report templates (`assets/`, `assets/templates/`)
- Improve scripts and tooling (`scripts/`)
- Report bugs or suggest enhancements

## 2. Development Workflow

### 2.1 Fork and Branch

Create a feature branch from `main`:

```bash
git checkout -b feat/short-description
```

Recommended branch prefixes:

- `feat/` for new features
- `fix/` for bug fixes
- `docs/` for documentation updates
- `refactor/` for non-functional code changes
- `chore/` for maintenance tasks

### 2.2 Commit Style

Use clear and scoped commit messages:

```text
type(scope): short summary
```

Examples:

- `feat(templates): add competitor matrix section`
- `fix(scripts): handle empty search result safely`
- `docs(readme): clarify github upload steps`

### 2.3 Keep Changes Focused

- One pull request should solve one coherent problem.
- Avoid mixing unrelated refactors with feature work.
- Update docs when behavior or usage changes.

## 3. Pull Request Checklist

Before submitting a PR, confirm:

- [ ] Change is focused and clearly described
- [ ] Relevant docs are updated
- [ ] No sensitive data or private credentials included
- [ ] `CHANGELOG.md` updated when appropriate
- [ ] Local verification completed (scripts/docs rendering if applicable)

## 4. Documentation Rules

- Keep docs concise, accurate, and executable.
- Prefer concrete examples over abstract descriptions.
- If you add a new workflow or template, include:
  - purpose
  - usage scenario
  - minimal example

## 5. Report/Data Quality Expectations

When contributing analysis logic or report structures:

- Do not fabricate data.
- Ensure key claims can be traced to sources.
- Prefer multi-source validation for critical metrics.
- If data is unavailable, mark it explicitly.

## 6. Code Quality Expectations

For script updates (`scripts/`):

- Keep functions small and readable.
- Add comments only for non-obvious logic.
- Fail gracefully on missing dependencies or invalid input.
- Preserve compatibility with existing project structure.

## 7. Security and Compliance

- Never commit API keys, tokens, or credentials.
- Respect source website terms and robots constraints.
- Keep third-party content attribution where required.

## 8. Questions and Proposals

If your change is large or architectural, open an issue first and describe:

- problem statement
- proposed solution
- alternatives considered
- expected impact

This helps reviewers provide faster and clearer feedback.
