---
name: skill-provenance
description: >
  Version tracking for Agent Skills bundles and their associated files
  across sessions, surfaces, and platforms. Use when creating, editing,
  versioning, validating, packaging, or handing off a skill bundle; when
  checking or updating MANIFEST.yaml, CHANGELOG.md, hashes, stale evals,
  or frontmatter mode; and when keeping version identity with the bundle
  instead of filenames. Compatible with the agentskills.io open standard.
metadata:
  author: Snap Synapse (snapsynapse.com)
  source: https://github.com/snapsynapse/skill-provenance
---

# Skill Provenance

## The Problem This Solves

Skill projects move between sessions, surfaces (Chat, IDE, CLI, Cowork),
platforms (Claude, Gemini CLI, Codex, Copilot), and local storage
(Obsidian, working directories, git repos). Version identity gets lost
when it lives only in filenames. A file renamed from `SKILL_v4.md` to
`SKILL_v5.md` with no internal record of what changed creates ambiguity.

This skill establishes three conventions that prevent that:

1. Version identity lives inside files when their format allows it, and
   always in the manifest.
2. A recent changelog travels with the skill bundle, while longer history
   can live in the source repo.
3. A manifest lists all files in the bundle so any session can verify completeness.

## What Gets Versioned

A skill bundle is a SKILL.md plus all associated files. Typical contents:

- SKILL.md (the skill definition)
- evals.json (evaluation suite)
- Generation scripts (e.g., generate.js, generate.py)
- Output artifacts (.docx, .pdf) produced by evals or real use
- Handoff notes
- Source material provided by the user (tracked but not versioned)

The skill itself (SKILL.md) and evals are the primary versioned artifacts.
Scripts and outputs are tracked by the manifest but version with the bundle
rather than independently. Handoff notes are optional convenience artifacts.


## Internal Version Header

Files that can safely carry YAML frontmatter begin with a YAML frontmatter
block (or extend an existing one) containing these fields:

```yaml
---
skill_bundle: my-skill            # bundle name, stable across versions
file_role: skill                  # skill | evals | script | output | handoff
version: 5                        # integer, monotonically increasing
version_date: 2026-02-10          # date of this version
previous_version: 4               # null for v1
change_summary: >
  Rewrote Phase 5 layout rules. Removed per-section page breaks.
  Added content flow check. Added validation checklist as standalone final page.
---
```

### Rules

**version** is an integer for per-file tracking. It counts revisions to
that specific file within the bundle. The bundle-level version
(`bundle_version` in MANIFEST.yaml) uses semver.

**change_summary** is required for every version after v1. One to three
sentences. It must describe what changed, not just that something changed.

**previous_version** creates a chain. Any session can trace the lineage.

**file_role** values:
- `skill` — the SKILL.md itself
- `evals` — the evals.json file
- `script` — generation scripts, utility scripts
- `output` — rendered artifacts (.docx, .pdf)
- `handoff` — session handoff notes
- `source` — user-provided source material (tracked, not versioned)
- `reference` — documentation in references/ loaded on demand
- `asset` — templates, images, fonts in assets/ used in output
- `agents` — platform UI metadata (e.g., Codex's agents/openai.yaml)

For files that cannot safely carry YAML frontmatter (binary files and
strict-format files such as `.json` or executable `.sh`), the manifest
tracks their version and its `version` field is authoritative.

**SKILL.md frontmatter constraint:** The Agent Skills open standard
(agentskills.io) requires `name` and `description`. Different platforms
enforce different rules about additional fields:

| Platform | Allowed SKILL.md frontmatter |
|---|---|
| **agentskills.io spec** | `name`, `description`, `license`, `metadata`, `compatibility`, `allowed-tools` |
| **Claude Chat / Settings UI** | Same as spec. Claude's settings importer rejects unrecognized fields. |
| **Claude Code** | Spec fields plus extensions: `disable-model-invocation`, `user-invocable`, `context`, `agent`, `model`, `hooks`, `argument-hint`. These are Claude Code features, not part of the base spec. |
| **Claude API** | Skills uploaded via `/v1/skills`. Validates `name` and `description`. Supports `metadata`. |
| **Gemini CLI (Google)** | `name` and `description` only. Extra fields not officially supported. |
| **Codex (OpenAI)** | `name` and `description` only. Extra fields rejected. |
| **GitHub Copilot / VS Code** | Follows agentskills.io spec. |
| **Cursor, Roo Code, Junie, others** | Follows agentskills.io spec. See agentskills.io for the full adopter list (30+). |

For maximum portability, keep SKILL.md frontmatter to `name` and
`description` only. If the canonical bundle needs attribution or visible
SKILL.md metadata, use the spec's `metadata` field there and generate a
derived minimal copy for strict platforms:

```yaml
---
name: my-skill
description: What the skill does.
metadata:
  skill_bundle: my-skill
  file_role: skill
  version: 3
  version_date: 2026-02-10
  previous_version: 2
  change_summary: >
    Added Phase 6 validation step.
---
```

If targeting Codex or other strict platforms directly, omit `metadata`
from SKILL.md entirely. The manifest tracks SKILL.md's version either
way, so no version information is lost.

**Note on spec support:** The agentskills.io spec formally supports
`metadata` as an arbitrary key-value map, with `version` shown as an
example use. This means the `metadata.version` approach is now
spec-blessed, not a Claude-only extension. However, the spec's version
is a static label — it does not address staleness tracking, changelogs,
or bundle integrity. Prefer manifest-based tracking as the default and
use `metadata` only when you need version info visible in the file
itself.

## Manifest

The manifest is a YAML file named `MANIFEST.yaml` at the root of the skill
bundle directory — the same level as `SKILL.md`. When the bundle is
packaged as a `.skill` ZIP, the manifest lives inside the ZIP. It is the
single source of truth for what the bundle contains.

```yaml
bundle: my-skill
bundle_version: 5.1.0
bundle_date: 2026-02-10
description: >
  Skill for generating professional documents from source material
  and user briefs. Handles research, structuring, and formatting.

compatibility:
  designed_for:
    surfaces:
      - chat
      - cli
      - ide
    capabilities:
      - minimal SKILL.md frontmatter
      - local filesystem access
      - optional git workflow
  tested_on:
    - platform: Anthropic Claude
      model: Claude Opus 4.6
      surface: Chat
      status: pass
      date: 2026-02-10
    - platform: Anthropic Claude
      model: Claude Sonnet 4.5
      surface: Chat
      status: partial
      date: 2026-02-09
      notes: Misses staleness detection on complex bundles
  spec_version: agentskills.io/1.0
  frontmatter_mode: minimal
    # minimal = name + description only (Codex, Gemini CLI, max portability)
    # metadata = includes metadata block (any platform supporting the spec's metadata field)

dependencies: []
  # List skill names this bundle depends on. Omit or leave empty if none.

deployments:
  api:
    version: 1759178010641129
    workspace: docs-prod
  claude:
    scope: user
  perplexity:
    package_format: zip

files:
  - path: SKILL.md
    role: skill
    version: 5
    hash: sha256:abc123...
    note: Canonical skill definition

  - path: evals.json
    role: evals
    version: 3
    hash: sha256:def456...
    note: 7 evals including real-content synthesis

  - path: scripts/generate.js
    role: script
    version: 4
    hash: sha256:ghi789...
    note: Generation script for eval 3

  - path: outputs/eval3-output.pdf
    role: output
    version: 4
    hash: sha256:jkl012...
    note: Rendered eval 3 output, 10 pages, validated

  - path: sources/article-1.md
    role: source
    version: null
    hash: sha256:pqr678...
    note: Source article 1 (published)
```

### Rules

**bundle_version** uses semver (MAJOR.MINOR.PATCH). Bump MAJOR for
breaking changes to the skill's model or interface, MINOR for new
features or capabilities, PATCH for fixes and documentation updates.
Per-file `version` fields remain integers — they are revision counters,
not release identifiers.

**hash** is sha256 of the file contents. This is how a new session verifies
that the file it received matches what the manifest claims. Compute on save,
verify on load.

**deployments** is optional. Use it to record deployed or installed copies
of the same bundle when you want traceability across surfaces. Keep
`bundle_version` as the author-side semver source of truth. Platform-native
versions (for example API timestamps) stay in `deployments`, not in
`bundle_version`.

**version: null** for source files. They are tracked for completeness but
not versioned by this system.

**Paths are relative** to the bundle root. No absolute paths.

**MANIFEST.yaml is not listed in `files`.** Self-hashing is recursive. Treat
the manifest as the bundle's control file and verify it via git, transport
checksums, or the surrounding package when needed.


## The .skill Package Format

Claude's settings UI exports and imports skills as `.skill` files. These
are standard ZIP archives containing a directory named after the skill.
The versioning artifacts (`MANIFEST.yaml`, `CHANGELOG.md`, `README.md`)
live inside this directory at the same level as `SKILL.md`:

```
skill-name.skill (ZIP)
└── skill-name/
    ├── SKILL.md
    ├── MANIFEST.yaml
    ├── CHANGELOG.md
    ├── README.md
    ├── assets/
    └── references/
```

Claude's settings importer only looks for `SKILL.md` and the directory
structure it expects (references, assets). It ignores files it doesn't
recognize. This means the versioning artifacts travel safely inside the
`.skill` ZIP without affecting import/export behavior.

When bootstrapping or updating a bundle, always include the versioning
artifacts in the `.skill` ZIP so they survive round-trips through
Claude's settings UI.

Some uploaders only accept `.zip` or `.md`. In those cases, rename the
archive from `.skill` to `.zip` without changing its contents.

The spec recommends keeping SKILL.md under 500 lines and moving detailed
reference material to separate files. Provenance artifacts fit naturally
into that model: `MANIFEST.yaml` and `CHANGELOG.md` are load-on-demand
resources, not always-loaded instructions.

Claude Code provides a `${CLAUDE_SKILL_DIR}` variable for bundle-relative
paths. Other platforms may not. Direct relative paths like
`./validate.sh` work when the working directory is the bundle root.

The `.skill` ZIP only carries the skill definition and its references.
Bundles can still track evals, scripts, rendered outputs, and handoff
notes outside the archive. The manifest remains the complete inventory,
not just the package inventory.


## Changelog

The changelog is a file named `CHANGELOG.md` at the root of the skill
bundle directory, alongside `SKILL.md` and `MANIFEST.yaml`. In the
bundle, it carries recent history with newest entries at the top. If the
canonical source lives in git, older entries can be archived in a
repo-level changelog outside the bundle.

```markdown
# Changelog

## 5.1.0 — 2026-02-10
- SKILL.md: Rewrote Phase 5 layout rules. Removed per-section page breaks.
  Added content flow check and a standalone validation checklist.
- evals.json: Not yet updated (stale, needs alignment).

## 5.0.0 — 2026-02-09
- SKILL.md: Reworked body flow rules and added an optional appendix.
- evals.json: Eval 3 expectations updated for content flow.
```

### Rules

**Each entry names every file that changed** and what changed in it.

**Files that are stale get called out.** If SKILL.md changes but evals.json
was not updated to match, the changelog says so. This prevents the silent
drift that caused the v4/v5 confusion.

**Entries are human-written prose**, not auto-generated diffs. The point is
to communicate intent, not enumerate line changes. Git diffs are available
when the bundle is in git.

**Bundle changelogs can be trimmed.** Keeping the last 5-15 entries in
the bundle is reasonable if the source repository maintains a full
append-only changelog elsewhere.


## Session Protocol

### Opening a session

When a skill bundle is loaded into a new session:

1. Read `MANIFEST.yaml` first.
2. Verify all listed files are present. Report any missing files.
3. For files with hashes, verify hashes match. Flag mismatches. In
   local environments, users can run `validate.sh` before uploading
   for reliable hash verification without LLM computation.
4. Read `CHANGELOG.md` to understand recent changes.
5. Check for staleness: if any file's version is lower than the bundle
   version, or if `deployments` clearly show a deployed copy behind the
   local bundle, flag it and ask the user whether it needs updating.
6. If `MANIFEST.yaml` is missing, treat the bundle as unversioned. Offer
   to create one by inventorying the files and asking the user for version
   context.

### Saving / closing a session

When work is complete and files are being delivered:

1. Update internal version headers for changed files that use them.
2. Update `MANIFEST.yaml` with new versions and hashes for every changed
   versioned file, including manifest-only files. If the user deployed or
   reinstalled the skill this session, update any relevant `deployments`
   metadata too.
3. Add a new top entry to `CHANGELOG.md`.
4. If any versioned file was changed but another dependent file was not
   updated (e.g., SKILL.md changed but evals.json was not updated), note
   the staleness explicitly in the changelog entry.
5. Deliver the full bundle to the user, or at minimum the changed files
   plus the updated MANIFEST.yaml and CHANGELOG.md.
6. If the user indicates the bundle is destined for a git repo, provide
   a ready-to-use commit message derived from the changelog entry. Format:

   ```
   skill-name MAJOR.MINOR.PATCH: one-line summary

   - file1.md: what changed
   - file2.json: what changed
   - Stale: file3.js (not updated this session)
   ```

   Return the message inline by default. Only write a transient
   `git_commit.txt` file if the user explicitly asks for a file or if the
   environment makes file output materially more convenient.

### Handoff between sessions

A handoff note is a snapshot of project state for the next session. It
should include:

- Current bundle version
- What was accomplished this session
- What is stale and needs attention
- What the next session should do first
- Any decisions made that are not yet reflected in the files
- Per-file change summaries: for each file modified this session, a
  brief description of what changed (section added, field removed,
  logic rewritten, etc.). This is more granular than the changelog
  entry and helps the next session verify the work without re-reading
  every file.

Create a handoff note only when crossing a non-persistent boundary or when
the user explicitly asks for one. In filesystem-native environments with a
current manifest, changelog, and git history, it is usually unnecessary.
When created, it replaces the previous handoff note; previous handoffs live
in changelog history.

### Conflict resolution

When a session finds version conflicts (e.g., a file claims v5 but the
manifest says v4, or two files claim different bundle versions):

1. Present the conflict to the user with the specific discrepancy.
2. Show what each version claims via its change_summary.
3. Default recommendation: trust the most recent version_date.
4. Always ask the user for explicit confirmation before proceeding.

Never silently resolve a version conflict. The whole point of this system
is to make conflicts visible.


## Cross-Surface and Cross-Platform Considerations

Treat one skill as moving through three states:

- **Canonical source bundle:** The working copy in git or local storage.
  Keep `MANIFEST.yaml` and the active `CHANGELOG.md` here. This is the
  author-side source of truth. If you maintain a full archive in git,
  keep it at repo root or another repo-level path outside the bundle.
- **Strict-platform install copy:** A derived copy for Codex, Gemini CLI,
  Perplexity, or other loaders that only accept `name` and `description`.
  Strip the `metadata` block from SKILL.md, set `frontmatter_mode:
  minimal`, recompute hashes in that copy, and leave the canonical bundle
  unchanged unless you intentionally promote the derived copy.
- **Registry or settings package:** A consumer package such as a `.skill`
  ZIP or ClawHub upload. It may omit development-only files, but its
  `MANIFEST.yaml` must describe exactly what the package contains. Update
  `deployments` only after a real publish, reinstall, or redeploy.

Surface notes:
- **Claude Chat:** Stateless upload/download boundary. Verify on open and
  consider a handoff note.
- **Claude Cowork / Claude Code / Claude Agent SDK:** Persistent
  filesystem. The manifest and changelog live with the bundle.
- **Claude API:** Deployment versions live in `deployments`, not in
  `bundle_version`.
- **Other agentskills clients:** Unknown files are ignored safely.
  `.agents/skills/` can act as a neutral install path.

General principle: the manifest and changelog stay authoritative, and
transformed install or publish copies are derived artifacts, not silent
edits to the canonical bundle.
## Trust and Audit

Use the manifest, changelog, hashes, and optional deployment metadata to
verify what belongs in the bundle, whether files still match their
recorded state, what changed, and which installed or deployed copies may
now be stale. If a bundle comes from an untrusted source, verify it first.


## File Naming

Versioned files use stable names without version numbers:

- `SKILL.md` (not `SKILL_v5.md`)
- `evals.json` (not `evals_v3.json`)
- `generate.js` (not `generate-v4.js`)

The version lives inside the file (via the header) and in the manifest,
not in the filename. Version-numbered filenames are how we got into
trouble in the first place.

Exception: if a user's local storage requires version-in-filename for
their workflow, the manifest is the tiebreaker for which version is
canonical. Internal version identity must still match.


## Bootstrap

To version an existing unversioned skill bundle:

1. Inventory all files present — read the directory structure or uploaded
   file list. Do not ask the user to list files; determine this yourself.
2. Ask the user what version number to assign. If there's a handoff note
   or other context, propose a number based on the history.
3. Add internal version headers to files that can safely carry them and
   record manifest-only versions for strict-format files.
4. Generate `MANIFEST.yaml` with hashes.
5. Create `CHANGELOG.md` with a single entry summarizing known history.
6. Deliver the versioned bundle.

This is a one-time operation per skill bundle.


## Origin

Developed by Snap Synapse. Canonical source:
https://github.com/snapsynapse/skill-provenance
