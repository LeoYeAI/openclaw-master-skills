# Release Policy

This repository uses a simple versioning strategy so the skill can be maintained as a stable, single-skill project.

## Current version

See the `VERSION` file at the repository root.

## Version format

Use `MAJOR.MINOR.PATCH`.

Examples:
- `0.1.0`
- `0.2.0`
- `0.2.1`
- `1.0.0`

## What each part means

### MAJOR
Increase the major version when the core contract changes in a breaking way.

Examples:
- changing the repository from one skill to multiple default skills
- changing the fixed stack away from HTML + CSS + JavaScript
- renaming or removing existing modes
- changing the delivery file contract in a breaking way

### MINOR
Increase the minor version when the skill gains meaningful capability without breaking its main contract.

Examples:
- adding a new example set
- improving schema coverage
- improving anti-copy rules
- refining mode guidance
- improving delivery structure while keeping the same file contract

### PATCH
Increase the patch version when making small, non-breaking improvements.

Examples:
- wording fixes
- example corrections
- README cleanup
- typo fixes
- clarifying documentation
- packaging cleanup

## Pre-1.0 guidance

This repository is still in an early stage.

Use `0.x.y` while the skill is still being shaped.
Treat minor version bumps in `0.x.y` as meaningful repository milestones.

Recommended interpretation:
- `0.1.x` — first stable repository structure
- `0.2.x` — stronger examples, schema, and release discipline
- `0.3.x` — stronger behavior consistency and validation
- `1.0.0` — ready for long-term stable maintenance

## Release checklist

Before changing the version:

1. update `CHANGELOG.md`
2. update the `VERSION` file
3. verify `README.md` and `README.zh-CN.md`
4. verify all `examples/` still match the current skill behavior
5. verify `SKILL.md` still matches the fixed platform, stack, and mode rules
6. run the repository release checklist if available

## Suggested tag format

Use lightweight repository tags like:

- `v0.1.0`
- `v0.2.0`
- `v0.2.1`

## Suggested release note sections

When writing a release note, keep it short and structured:

- Added
- Changed
- Fixed
- Removed

## Breaking-change warning

If a change touches any of the following, strongly consider a major version decision:

- skill shape
- supported modes
- fixed stack
- delivery file contract
- anti-copy contract
- schema contract
