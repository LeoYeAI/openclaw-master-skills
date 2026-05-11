# Changelog

## [1.5.0] - 2026-02-17
### Changed
- Step 11 now prepares publish package and logs D-## approval request — does NOT execute publish
- Step 11.5 is the actual publish execution, gated on explicit "D-## yes" from My Lord
- ClawhHub publish is now a hard-gated external action, not an autonomous step

## 

## v1.4.2 — 2026-02-18

- **Step 11: parameter extraction from skill.yml** — `--slug`, `--name`, `--version` are now
  extracted directly from skill.yml before publish. Guards against wrong/guessed display names.
  Fails loudly if `display_name` is missing.
- **Step 11.5: post-publish verification** — after every publish, `clawhub inspect` is run and
  output compared against skill.yml (name, version, description, owner). Mismatch → fix and
  republish before proceeding to security scan or delivery.
- **Step 1.5: `display_name` field required** — added to scaffolding and version-bump checklist.
  Title case, plain English, must be set explicitly in skill.yml.
- Fixes root cause of "Skill Release Task Runner" wrong title incident (2026-02-18).

## v1.4.1 — 2026-02-17

- Add `scripts/` directory with validate-structure.sh, validate-release-content.sh, opsec-scan.sh
- Add `## Configuration` section

## v1.4.0 — 2026-02-16

- Define two-phase automation model: Phase 1 (auto) → User Gate → Phase 2 (auto)
- Add anti-patterns: no intermediate questions, no step-by-step confirmations
- Silent retry on rate limits and transient errors
- One message per phase: review request (Phase 1) and delivery (Phase 2)
- Fix hardcoded org name in Step 3 examples

## v1.3.0 — 2026-02-16

- Step 11: Use browser tool to verify ClawhHub security scan results (VirusTotal + OpenClaw)
- Add `permissions` field to skill.yml declaring required privileged access
- Add guidance for addressing "Suspicious" scan verdicts (undeclared permissions)
- Fix Step 10 publish path
- Fix ClawhHub URL pattern (clawhub.ai, not clawhub.com)
- Step 12 delivery now includes both scan verdicts and VirusTotal report link

## v1.2.0 — 2026-02-16

- Replace dual-repo model with single-repo force push (orphan branch erases history)
- One repo per skill: starts private, flipped to public at release
- Step 1.5: Version bump guidance for updates (patch/minor/major)

## v1.1.0 — 2026-02-16

- Add Step 1: Structure Scaffolding — auto-generate all boilerplate from SKILL.md
- Pipeline now 11 steps (was 10)
- "Release skill X" takes a bare SKILL.md to ClawhHub with no separate polish step
- Clarified scope: this skill handles everything after SKILL.md content is written

## v1.0.0 — 2026-02-16

- Initial release
- 10-step pipeline: readiness → staging → OPSEC → dual review → publish
- Private staging repo stays private forever (history safety)
- Clean public repo created at release time (single commit)
- Agent review checklist (10 items)
- User review via private repo link
- Error handling table
- Assumptions section documenting agent-user interaction model
