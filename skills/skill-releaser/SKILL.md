---
name: skill-releaser
description: Release skills to ClawhHub through the full publication pipeline — auto-scaffolding, OPSEC scan, dual review (agent + user), force-push release, security scan verification. Use when releasing a skill, preparing a skill for release, reviewing a skill for publication, or checking release readiness.
version: 1.5.0
triggers:
  - release skill
  - publish skill
  - prepare for clawhub
  - release readiness
  - skill release review
  - publish to clawhub
---

# Skill Releaser

Orchestrates the full skill publication pipeline from internal repo to ClawhHub.

## When to Use

- User says "release {skill}" or "publish {skill} to clawhub"
- User says "prepare {skill} for release" or "check release readiness"
- User says "review {skill} for publication"
- Cron-triggered release check during refactory pipeline

## Assumptions

**How OpenClaw and user interact during release:**
- Agent runs on a machine with shell access (exec tool) for git and CLI operations
- User communicates via messaging channel (Telegram, Discord, Signal, etc.) — likely on a phone
- User reviews the private GitHub repo directly in their browser/phone — the repo IS the review artifact, not a text summary
- User approves or rejects by replying to the agent's message (natural language: "approve", "revise: fix the readme", "reject")
- Agent can create and manage GitHub repos via `gh` CLI on behalf of the user's authenticated account
- Agent pushes to the private staging repo BEFORE requesting user review, so there is something to review
- Agent does NOT publish anything publicly without explicit user approval — this is a hard gate
- The repo starts private for staging and review. At release time, history is erased via orphan branch + force push (single clean commit), then flipped to public
- The full release can span multiple sessions — the private staging repo preserves state so any agent can resume
- Multiple skills can be in different stages of the pipeline simultaneously

## Prerequisites

- `gh` CLI authenticated (for repo creation and visibility changes)
- `clawhub` CLI installed (for ClawhHub publishing)
- A skill directory with at least a `SKILL.md` file

## Scope & Boundaries

**This skill handles:** The full release pipeline — structure scaffolding, OPSEC scanning, review, publishing.
**This skill does NOT handle:** Skill content creation or design. The SKILL.md must already describe what the skill does. Everything else (boilerplate, structure, scaffolding) is this pipeline's job.

A user with a finished SKILL.md should be able to say "release this skill" and this skill handles everything from there — including generating all missing structure files.

## Automation Model

The pipeline has two fully automated phases separated by one human gate. **Both single and batch releases follow the same model.**

### Single Skill
```
Phase 1 (AUTO): Steps 1-7 — scaffold, validate, stage, scan, review, push
     ↓
  GATE: User reviews private repo, replies "approve" / "revise" / "reject"
     ↓
Phase 2 (AUTO): Steps 9-12 — erase history, flip public, publish, verify scan, deliver
```

### Batch Release (multiple skills)
```
Phase 1 (PARALLEL): Spawn subagents — one per skill, all run Phase 1 simultaneously
     ↓
  GATE: ONE batch review message with all repo links
        User replies: "approve all" / "approve A,C; revise B: fix readme"
     ↓
Phase 2 (PARALLEL): Spawn subagents for approved skills, all publish simultaneously
     ↓
  DELIVERY: ONE batch summary with all links and scan results
```

**Batch rules:**
- Never serialize releases — spawn parallel subagents for Phase 1
- Never block on one approval to start the next Phase 1
- Assign each skill a short unique ID (A, B, C...) in the batch review message
- Collect all Phase 1 results, present ONE batch review message with short IDs
- Accept batch approvals: "approve all" / "approve A,C" / "revise B: fix readme"
- Run all Phase 2s in parallel after approval

**Design principles:**
- User says "release these skills" once. Agent runs all Phase 1s in parallel without interruption.
- Agent sends ONE message: all review links + recommendations. Then waits.
- User replies once. Agent runs all Phase 2s in parallel without interruption.
- Agent sends ONE delivery message with all results.
- If any step fails, agent fixes it automatically and continues. Only report to user if unfixable.
- Rate limits, retries, and delays are handled silently (sleep + retry, not "rate limited, should I try again?")

**Anti-patterns (never do these):**
- Do not serialize releases — always parallelize with subagents
- Do not block on approval for skill A before starting Phase 1 for skill B
- Do not send per-skill review messages — batch them
- Do not ask "should I create the repo?" — just create it
- Do not report intermediate steps — only the batch review and batch delivery
- Do not ask about rate limits or transient errors — retry silently

## Process

### Step 1: Structure Scaffolding (Auto-Generate Boilerplate)
Before any quality checks, generate all missing structure files from the existing SKILL.md:

**Auto-generate if missing:**

| File | Source | Generation Method |
|------|--------|-------------------|
| `skill.yml` | SKILL.md frontmatter + triggers | Extract name, description, version, triggers from SKILL.md |
| `README.md` | SKILL.md description + usage | GitHub landing page for humans: what it does, how to install, future work. NOT agent instructions. |
| `CHANGELOG.md` | Version from skill.yml + git log | `## v{version} — {date}` + summary of current state |
| `tests/test-triggers.json` | SKILL.md triggers + "When to Use" | `shouldTrigger` from triggers list, `shouldNotTrigger` from anti-patterns |
| `scripts/` | Create directory | Empty dir or placeholder README if no scripts needed |
| `references/` | Create directory | Empty dir or placeholder README if no references needed |
| `LICENSE` | Default MIT | Standard MIT license text |
| `.gitignore` | Standard | `node_modules/`, `.DS_Store`, `*.log` |

**Rules:**
- Never overwrite existing files — only generate what's missing
- All generated content derives from SKILL.md — no hallucinated features
- If SKILL.md lacks enough info to generate a file, flag it as a content gap (user must fix SKILL.md first)
- Generated README.md must make sense to a stranger who has never seen the skill before

**Validation after scaffolding:**
- Run `scripts/validate-structure.sh` — must score 8/8
- If not 8/8, identify what's still missing and fix it

### Step 1.5: Version Bump (updates only)
If this skill has been published before, bump the version before proceeding:

1. **Check current published version:**
```bash
clawhub inspect {slug}
```

2. **Bump version** in both `skill.yml` and `SKILL.md` frontmatter:
   - Patch (1.0.0 → 1.0.1): bug fixes, typos, minor doc updates
   - Minor (1.0.0 → 1.1.0): new features, new sections, structural changes
   - Major (1.0.0 → 2.0.0): breaking changes, full rewrites

3. **Update CHANGELOG.md** with new version entry describing what changed

4. **Verify `display_name` is set in `skill.yml`** — this is the human-readable title shown on ClawhHub.
   It must be set explicitly; never derive it from the slug or guess it.
   If missing, add it now:
   ```yaml
   display_name: "Human Readable Title"  # Required — used as ClawhHub listing title
   ```
   Rules:
   - Title case, plain English, no jargon
   - Describes what the skill does, not how it's implemented
   - Example: slug `autonomous-task-runner` → `display_name: "Autonomous Task Runner"`
   - Example: slug `skill-releaser` → `display_name: "Skill Releaser"`

Skip this step for first-time releases (but still verify `display_name` exists).

### Step 2: Readiness Check
Verify the skill directory is complete:
- `SKILL.md` exists with description and usage instructions
- `skill.yml` exists with name, description, triggers
- Structure score 8/8 (from Step 1)
- No obvious OPSEC violations (quick scan)

If any check fails, report what needs fixing. Do not proceed.

### Step 3: Create Private Staging Repo
```bash
# Check if repo already exists
gh repo view your-org/openclaw-skill-{name} 2>/dev/null

# If not, create it — CRITICAL: use the SANITIZED description, not the source skill.yml
# Run OPSEC scan on the description string BEFORE passing to gh repo create
gh repo create your-org/openclaw-skill-{name} --private --description "{sanitized description}"
```

**OPSEC on repo metadata:** The description passed to `gh repo create` is public when the repo flips to public. It must be scanned for the same patterns as file contents (org names, personal info, internal project names). This is not covered by file-based scanners — it must be checked explicitly.

### Step 4: Prepare Release Content
Copy ONLY the skill directory content to a clean staging area:
```bash
mkdir -p /tmp/skill-release-{name}
cp -r skills/{name}/* /tmp/skill-release-{name}/

# Remove internal-only files
rm -f /tmp/skill-release-{name}/WORKSPACE.md
rm -f /tmp/skill-release-{name}/.gitignore
rm -rf /tmp/skill-release-{name}/_meta.json
rm -rf /tmp/skill-release-{name}/.clawhub
```

**CRITICAL VALIDATION — verify before proceeding:**
```bash
# The release directory must contain ONLY skill files.
# If you see ANY of these, you copied from the wrong directory — STOP and fix:
#   - USER.md, MEMORY.md, AGENTS.md, SOUL.md (workspace/repo root files)
#   - audits/, shared/, scripts/ (repo directories)
#   - memory/, slides/, projects/ (personal data)
#   - .gitmodules (repo root)
ls /tmp/skill-release-{name}/
# Expected: SKILL.md, skill.yml, README.md, CHANGELOG.md, LICENSE, tests/, references/, scripts/
# If file count exceeds ~15 files, something is wrong. Verify source path.
```

Add release files if missing:
- `LICENSE` (MIT by default)
- `README.md` (must work as GitHub landing page for strangers)
- `.gitignore`

### Step 5: Release Content Validation (HARD GATE)
```bash
bash scripts/validate-release-content.sh /tmp/skill-release-{name}
```
**This is a deterministic script that blocks pushes if the release directory contains repo-level files (USER.md, MEMORY.md, audits/, etc.), has too many files (>50), or contains suspicious file types (logs, images, PDFs).**

Must return SAFE (exit 0). If BLOCKED, you copied from the wrong directory. **Do NOT proceed. Fix the source path and re-copy.**

### Step 6: OPSEC Deep Scan
```bash
bash scripts/opsec-scan.sh /tmp/skill-release-{name}
```
Must return CLEAN (exit 0). If violations found, fix them in the release copy. Do NOT modify the source in openclaw-knowledge — keep the internal version as-is.

### Step 7: Agent Review
Generate review document:
```markdown
# Release Review: {skill-name}

## Checklist
- [ ] SKILL.md clear and useful to a stranger
- [ ] README.md works as GitHub landing page
- [ ] skill.yml triggers accurate and complete
- [ ] Scripts work without hardcoded dependencies
- [ ] Tests present and described
- [ ] CHANGELOG.md current
- [ ] LICENSE present
- [ ] No references to internal repos, infrastructure, or personal info
- [ ] OPSEC scan: CLEAN
- [ ] Competitive position: {novel|ahead}

## OPSEC Scan Output
{paste scan output}

## Competitive Summary
{from audits/{name}-competitive.md}

## Recommendation
APPROVE / REVISE: {reasons}
```

Save to `openclaw-knowledge/reviews/{name}-release-review.md`

### Step 8: Push to Private Staging Repo
Push sanitized content so user can review the actual repo on any device (phone, laptop):
```bash
cd /tmp/skill-release-{name}
git init
git config user.email "agent@localhost"
git config user.name "SkillEngineer"

# Install OPSEC pre-commit hook — prevents sensitive data from entering git history
cp /tmp/openclaw-knowledge/scripts/opsec-precommit-hook.sh .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit

git add .
git commit -m "v{version}: Initial release of {name}"
git remote add origin https://github.com/your-org/openclaw-skill-{name}.git
git branch -M main
git push -u origin main
```

### Step 9: User Review
For single skills, send review link. For batch releases, collect all Phase 1 results and send ONE message.

**Single skill:**
```
RELEASE REVIEW: {skill-name}

{score} | OPSEC: CLEAN
{1-line description}
https://github.com/your-org/openclaw-skill-{name}

Reply: approve / revise:{feedback} / reject
```

**Batch review (assign short IDs for easy approval):**
```
BATCH RELEASE REVIEW — {N} skills

A. {skill-name} — {score} | CLEAN | {1-line description}
https://github.com/your-org/openclaw-skill-{name}

B. {skill-name} — {score} | CLEAN | {1-line description}
https://github.com/your-org/openclaw-skill-{name}

C. {skill-name} — {score} | CLEAN | {1-line description}
https://github.com/your-org/openclaw-skill-{name}

Reply: approve all / approve A,C / revise B:{feedback}
```

**Rules:**
- Links on their own line (never in tables — not clickable on mobile)
- Short IDs (A, B, C) for batch approval — user should never type full skill names
- The repo IS the review artifact. User reviews actual files, not a summary.
- Wait for user response. Do not proceed without explicit approval.

### Step 10: Erase History & Flip to Public (after user approval)
Erase git history (may contain OPSEC fixes from earlier revisions) and make the repo public:
```bash
cd /tmp/skill-release-{name}
# Orphan branch erases all history
git checkout --orphan clean
git add -A
git commit -m "v{version}: {name}"
git branch -D main
git branch -m main
git push -f origin main

# Flip visibility
gh repo edit your-org/openclaw-skill-{name} --visibility public

# Verify repo metadata is OPSEC-clean (description, topics are now public)
gh repo view your-org/openclaw-skill-{name} --json description,repositoryTopics -q '.description + " " + (.repositoryTopics | join(" "))'
# Manually check output for org names, personal info, internal project names
# If dirty: gh repo edit your-org/openclaw-skill-{name} --description "{clean description}"
```

Single commit, clean history, one repo. No dual-repo complexity.

### Step 11: Prepare Publish Package and Request Approval

**ClawhHub publish is an irreversible external action. It requires explicit user approval via a D-## ID before execution.**

Extract the publish parameters and log an approval request — do NOT run `clawhub publish` yet:

```bash
# Extract publish parameters directly from skill.yml
SLUG=$(grep '^name:' /tmp/skill-release-{name}/skill.yml | awk '{print $2}')
DISPLAY_NAME=$(grep '^display_name:' /tmp/skill-release-{name}/skill.yml | sed 's/display_name: *//' | tr -d '"')
VERSION=$(grep '^version:' /tmp/skill-release-{name}/skill.yml | awk '{print $2}')

echo "slug:         $SLUG"
echo "display_name: $DISPLAY_NAME"
echo "version:      $VERSION"

if [ -z "$SLUG" ] || [ -z "$DISPLAY_NAME" ] || [ -z "$VERSION" ]; then
  echo "ERROR: Missing slug, display_name, or version in skill.yml — fix before proceeding"
  exit 1
fi
```

If `display_name` is missing from `skill.yml`, add it now (see Step 1.5).

**Then add a pending publish entry to ESCALATIONS.md:**
```
D-##: Publish {display_name} v{version} (slug: {slug}) to ClawhHub? — yes/no
```

**Stop here. Wait for My Lord to reply "D-## yes" before proceeding to Step 11.5.**

Only proceed to Step 11.5 if My Lord has explicitly approved this specific publish in the current session.

### Step 11.5: Execute Publish + Verify (APPROVAL REQUIRED)

**Only run this step after receiving explicit "D-## yes" from My Lord.**

```bash
clawhub publish /tmp/skill-release-{name} \
  --slug "$SLUG" \
  --name "$DISPLAY_NAME" \
  --version "$VERSION" \
  --changelog "{summary of changes from CHANGELOG.md}"
```

**Post-publish verification — verify the live listing matches skill.yml exactly:**

After publishing, verify the live listing matches the source skill.yml exactly.
**This step catches wrong titles, version mismatches, and stale metadata before delivery.**

```bash
clawhub inspect "$SLUG" 2>&1
```

Compare the output against skill.yml:

| Field | Expected (from skill.yml) | Actual (from clawhub inspect) | Match? |
|-------|--------------------------|-------------------------------|--------|
| Display name | `display_name` value | First line of inspect output | ✅ / ❌ |
| Version | `version` value | `Latest:` field | ✅ / ❌ |
| Description | First sentence of `description` | `Summary:` field (truncated) | ✅ / ❌ |
| Owner | your ClawhHub username | `Owner:` field | ✅ / ❌ |

**If any field does not match:**
1. Do NOT proceed to Step 12
2. Identify the mismatch (wrong `--name`, wrong `--slug`, stale `skill.yml`)
3. Fix the source (skill.yml or publish command), bump patch version, republish
4. Re-run Step 11.5 until all fields match
5. Only proceed to Step 12 when the table shows ✅ on all rows

**Common mismatches and fixes:**

| Mismatch | Cause | Fix |
|----------|-------|-----|
| Wrong display name | `display_name` missing from skill.yml; name was guessed | Add `display_name` to skill.yml, republish |
| Wrong version | skill.yml not updated before publish | Bump version in skill.yml, republish |
| Wrong slug | `name` field in skill.yml doesn't match intended slug | Fix `name` in skill.yml or use correct `--slug` |
| Wrong owner | Published under wrong account | Check `clawhub whoami`, re-authenticate if needed |

### Step 12: Verify Security Scan (Browser Required)
ClawhHub automatically scans all published skills via VirusTotal (Code Insight) and OpenClaw's own scanner. **Do not consider the release complete until scans are reviewed.**

**Use the browser tool to check scan results — ClawhHub pages require JS rendering:**

1. **Open the skill detail page with browser:**
```
browser start (profile=openclaw)
browser navigate → https://clawhub.ai/{username}/{slug}
browser snapshot (refs=aria)
```

2. **Find the "Security Scan" section** in the snapshot. It shows:
   - **VirusTotal verdict:** Benign / Suspicious / Malicious / Pending
   - **OpenClaw verdict:** Benign / Suspicious / Malicious with confidence level
   - **Detail text:** Explanation of what was flagged (expand "Details" if collapsed)
   - **VirusTotal report link:** Direct URL to full analysis

3. **Interpret results and act:**

| Verdict | Meaning | Action |
|---------|---------|--------|
| Benign (both) | Clean, auto-approved | Proceed to Step 13 |
| Pending | Still processing | Wait 2 minutes, re-snapshot |
| Suspicious (undeclared permissions) | Skill needs privileged access not in metadata | Add `permissions` to skill.yml, bump version, re-publish |
| Suspicious (other) | Flagged behavior | Review detail text. If false positive, contact OpenClaw security team. If real, fix and re-publish |
| Malicious | Blocked from download | Fix immediately, bump version, re-run from Step 1.5 |

4. **Common fix — undeclared permissions:**
   If flagged for privileged CLI access (gh, clawhub, git, filesystem), add a `permissions` field to `skill.yml`:
   ```yaml
   permissions:
     - exec: git, gh CLI (repo creation, visibility changes)
     - exec: clawhub CLI (publishing)
     - filesystem: read/write skill directories
     - browser: verify scan results on ClawhHub
   ```
   Then bump version and re-publish. This declares intent and resolves the flag.

5. **If VirusTotal is still Pending** after 5 minutes, proceed to Step 12 but note it in the delivery. The scan completes asynchronously.

### Step 13: Deliver
Confirm the release is live and deliver all links and scan status to the user:

```
RELEASED: {skill-name} v{version}

GitHub: https://github.com/your-org/openclaw-skill-{name}
ClawhHub: https://clawhub.ai/{username}/{slug}
VirusTotal: {verdict} — {report link}
OpenClaw Scan: {verdict} ({confidence})

{1-line description}
```

### Pipeline Ends Here

Skill-releaser scope ends at Step 13 (delivery). Post-release bookkeeping (STATUS.json updates, submodule conversion, memory logging) is a **refactory system responsibility**, not a release pipeline responsibility. See REFACTORY-SYSTEM.md "Post-Release Stage."

## Error Handling

| Error | Cause | Fix |
|-------|-------|-----|
| Readiness check fails | Score too low or OPSEC dirty | Complete refactoring first |
| OPSEC scan finds violations in release copy | Sanitization incomplete | Fix in release copy, re-scan |
| gh repo create fails | Auth issue or name taken | Check `gh auth status`, try different name |
| clawhub publish fails | CLI not installed or auth | Run `npm install -g clawhub`, authenticate |
| User rejects | Feedback provided | Address feedback, restart from Step 4 |

## Configuration

No persistent configuration required. The pipeline uses environment-level tools
(`gh`, `clawhub`, `git`) that must be authenticated before use.

**Required tools:**

| Tool | Purpose | Check |
|------|---------|-------|
| `gh` CLI | GitHub repo creation, visibility changes | `gh auth status` |
| `clawhub` CLI | Publish to ClawhHub registry | `clawhub whoami` |
| `git` | Version control | Built-in |
| `python3` | OPSEC scanner (optional) | `python3 --version` |

**Pipeline scripts (in `scripts/`):**

| Script | Purpose |
|--------|---------|
| `validate-structure.sh` | Score skill structure completeness (8 checks) |
| `validate-release-content.sh` | Block placeholder text, empty files |
| `opsec-scan.sh` | Scan for sensitive data before public release |

**Org/username:** Update `your-org` in the pipeline steps to your GitHub
username or org. The clawhub `--slug` argument uses the skill's `name` field
from `skill.yml`.

## Examples

**Release a specific skill:**
"Release skill-engineer to clawhub"

**Check readiness without releasing:**
"Is evidence-based-investigation ready for release?"

**Batch readiness check:**
"Which skills are ready to publish?"

