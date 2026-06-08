# Changelog

## 4.2.1 — 2026-02-28
- README.md (bundle): Added pi0/skillman (JS/TS) alongside existing
  chrisvoncsefalvay/skillman (Python) in ecosystem references. Added
  research subsection with Xu & Yan (2026) agent skills survey paper.
- README.md (root): Added pi0/skillman to related projects alongside
  existing Python skillman reference.
- CHANGELOG.md: Renumbered all post-3.0.0 entries to align with git tag
  v4.0.0. Merged former 4.1.0 and 4.2.0 into single 4.0.0 entry matching
  the tagged release.

## 4.2.0 — 2026-02-28
- README.md (root): Rewrote with explicit value statement, before/after
  comparison, platform support matrix with tested/untested status,
  comparison table against git tags, filename suffixes, and Skillman,
  and "when not to use this" guidance.
- AGENTS.md: New file. Repo-level guide for AI agents with repository
  structure, pre/post-change protocols, key rules, and testing
  instructions.
- CONTRIBUTING.md: New file. Contribution guide with versioning protocol
  for bundle changes and code style expectations.
- .github/ISSUE_TEMPLATE/compatibility-report.yml: New file. Structured
  issue template for cross-platform test results.
- validate.sh: Added sha256sum fallback for Linux portability. Script
  now auto-detects shasum (macOS) or sha256sum (Linux) at startup.
- README.md (bundle): Updated validate.sh dependency description to
  include sha256sum.

## 4.1.0 — 2026-02-28
- Adopted semver for bundle versioning. Updated SKILL.md spec to replace
  integer-only rule with semver for bundle_version and integer for per-file
  revision counts. Updated MANIFEST.yaml, CHANGELOG.md, and README examples
  to use semver throughout.
- README.md (root): Added Skillman reference to related projects.
- README.md (bundle): Added Skillman to ecosystem references.
- CHANGELOG.md: Retroactively mapped all prior releases to semver,
  aligned with git tag v4.0.0.

## 4.0.0 — 2026-02-27
- SKILL.md: Added Gemini CLI to frontmatter constraint table and
  cross-platform considerations section with three-tier discovery,
  install path, and management commands. Switched default frontmatter_mode
  to minimal for maximum cross-platform portability. Added git commit
  message generation (step 6) to session close protocol and required
  per-file handoff summaries. Refined the model so internal headers are
  used when safe, strict-format files are manifest-only, `MANIFEST.yaml`
  is not self-listed, and the bundle itself ships in minimal frontmatter
  mode for maximum portability.
- README.md: Added Gemini CLI to quick start surface table. Added Gemini
  Gems workflow guidance with tracking instructions, example prompt, and
  limitations. Added Gemini ecosystem references. Added local hash
  validation section, clarified that the checked-in directory is the
  canonical cross-platform source bundle and that strict-format files
  rely on manifest-only version tracking.
- evals.json: Added evals 9-13: Gemini CLI compatibility bootstrap,
  Gemini Gems prompt extraction, git commit message generation, handoff
  with per-file changes, local hash validation. Aligned all expectations
  with minimal frontmatter mode, manifest-only tracking for strict-format
  files, and the manifest control-file rule. Now 13 evals total.
- validate.sh: New file. Hardened for portable update-mode rewrites and
  locale-stable hash verification against MANIFEST.yaml.

## 3.0.0 — 2026-02-10
- All files: Renamed bundle from skill-versioning to skill-provenance.
  All internal references, frontmatter, and manifest entries updated.
- evals.json: Added 3 new evals (6, 7, 8) covering cross-platform
  Codex bootstrap, frontmatter_mode toggling, and compatibility block
  generation. All 8 evals now aligned with 2.0.0 SKILL.md capabilities.
- Prepared for public release on GitHub under snapsynapse org.

## 2.0.0 — 2026-02-10
- SKILL.md: Added cross-platform interoperability section (Codex, Copilot,
  agentskills.io). Added compatibility block to manifest spec. Expanded
  file_role values (reference, asset, agents). Documented SKILL.md frontmatter
  constraints per platform with compatibility table. Made description and
  problem statement platform-agnostic. Added cross-platform notes for Codex
  and GitHub Copilot surfaces.
- README.md: Added references section (official docs, blog posts, ecosystem
  links, support articles). Added spec relationship section. Simplified
  bootstrap prompt (Claude inventories files itself). Fixed macOS .skill
  extraction instructions (Archive Utility won't open .skill, unzip -d
  required). Added troubleshooting for unzip destination behavior.
- evals.json: Not updated — did not yet cover cross-platform scenarios,
  compatibility block generation, or frontmatter_mode toggling.

## 1.0.0 — 2026-02-10
- Bootstrap from initial design session. Created SKILL.md with session
  protocol, manifest spec, changelog spec, version header spec, and
  cross-surface considerations. Created README.md with worked example
  and porting workflows. Created evals.json with 5 structural evals.
- No content from prior sessions — this was the first versioned release.
