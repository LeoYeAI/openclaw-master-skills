# Contributing

This repository is for a **single OpenClaw skill with multiple modes**.

Before changing anything, keep the core contract stable:

- One skill, not multiple separate skills in this repo
- Fixed platform: **H5 / Web**
- Fixed stack: **HTML + CSS + JavaScript**
- Supported modes only:
  - `analysis`
  - `proposal`
  - `architecture`
  - `delivery`
  - `full`

Do not expand this repository back into a multi-framework or generic image-to-code project.

## Contribution goals

Good contributions should improve one or more of these:

- output stability
- mode clarity
- anti-copy protection
- handoff quality
- schema consistency
- example quality
- documentation consistency

## Do not change these without a deliberate versioned decision

Treat these as protected rules:

1. **Fixed stack**
   - Do not add Vue, React, Uni-app, or framework-specific guidance.
   - Do not add framework-specific examples.

2. **Skill shape**
   - Do not split the repo content into multiple default skills.
   - Keep the repository centered on one skill with mode-based behavior.

3. **Anti-copy rule**
   - Do not weaken the rule that the skill must transform references into a new campaign.
   - Do not allow superficial reskinning to pass as valid output.

4. **Mode contract**
   - Do not blur the differences between `analysis`, `proposal`, `architecture`, `delivery`, and `full`.
   - If mode behavior changes, update all related examples and docs.

## When you must update multiple files together

If you change one of the following, you must update all related files in the same commit.

### A. Skill behavior changes
If you change `SKILL.md`, also review and update:

- `README.md`
- `README.zh-CN.md`
- `references/scope.md`
- relevant files in `examples/`
- `CHANGELOG.md`

### B. Mode changes
If you change any mode definition, also update:

- `README.md`
- `README.zh-CN.md`
- `SKILL.md`
- the matching `examples/mode-*.md`
- `examples/full-delivery-example.md`
- `CHANGELOG.md`

### C. Output structure changes
If you change the output sections, file layout, schema shape, or handoff format, also update:

- `SKILL.md`
- `examples/output-example.md`
- `examples/full-delivery-example.md`
- `examples/campaign-schema-example.json`
- `CHANGELOG.md`

### D. Repository structure changes
If you add, rename, or remove files, also update:

- `README.md`
- `README.zh-CN.md`
- `CHANGELOG.md`

## Required review checklist before merging

Before merging a contribution, verify all of the following.

### 1. Stack discipline
- No mention of unsupported frameworks
- No code output outside HTML/CSS/JS
- No examples suggesting alternate front-end stacks

### 2. Mode discipline
- `analysis` stays analysis-only
- `proposal` stays proposal-first
- `architecture` stays structure-first
- `delivery` stays code-delivery-first
- `full` still covers the complete flow

### 3. Anti-copy discipline
- The skill still requires transformation, not duplication
- New examples do not look like the same page with renamed text
- Examples still show changes in at least two of:
  - campaign theme
  - reward mechanism
  - task structure
  - major module sequence or core interaction

### 4. Documentation discipline
- English and Chinese README files still describe the same product
- File lists are still accurate
- Example names in docs still match real files
- Terminology is still consistent across all docs

## Example contribution types

### Good changes
- tighten the mode prompts
- improve anti-copy instructions
- improve schema clarity
- add a better H5/Web example
- make output sections more consistent
- improve English/Chinese wording consistency

### Risky changes
These need extra review:

- adding new modes
- changing default mode behavior
- changing delivery file names
- changing the schema contract
- changing anti-copy rules
- changing the fixed stack

## File naming guidance

Keep naming stable and descriptive.

Preferred pattern for examples:
- `mode-analysis-example.md`
- `mode-proposal-example.md`
- `mode-architecture-example.md`
- `mode-delivery-example.md`
- `full-delivery-example.md`

Avoid vague names like:
- `new-example.md`
- `demo.md`
- `test-output.md`

## Formatting guidance

- Keep `.editorconfig` at the repository root.
- Use `.editorconfig` as the formatting baseline for Markdown and JSON changes.
- Do not introduce a formatter rule that conflicts with the repository `.editorconfig` without a versioned decision.

## Writing guidance

When editing docs:

- keep language direct
- prefer stable wording over clever wording
- avoid overpromising
- avoid implying pixel-perfect visual recovery
- separate observed content from inferred or assumed content when relevant
- keep the skill framed as a handoff-ready planning and delivery tool

## Ownership and licensing

- Keep `LICENSE` present at the repository root.
- Keep `CODEOWNERS` present at the repository root.
- Replace the placeholder owner in `CODEOWNERS` before using this repository in a shared GitHub project.
- If repository ownership changes, update `CODEOWNERS`, `README.md`, and `README.zh-CN.md` together when needed.

## Release discipline

Before publishing a new version:

1. update `CHANGELOG.md`
2. update the `VERSION` file
3. review `RELEASE.md` if the release policy needs adjustment
4. run through `RELEASE-CHECKLIST.md`
5. verify README file lists
6. verify all mode examples still match the current behavior
7. verify no outdated stack wording has slipped back in

## Suggested commit scope

Use small commits when possible:

- docs only
- examples only
- schema only
- mode behavior update
- release prep

This makes it easier to track why a change was made and whether all required files were updated.
