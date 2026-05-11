# Health Check Reference

Detection algorithms, report formats, and real-world examples for `--healthcheck` mode (R1-R7).

## Contents

- [R1: Orphan detection](#r1-orphan-detection)
- [R2: Duplicate detection](#r2-duplicate-detection)
- [R3: Trigger collision detection](#r3-trigger-collision-detection)
- [R4: Dependency check](#r4-dependency-check)
- [R5: URL validation](#r5-url-validation)
- [R6: Environment variable check](#r6-environment-variable-check)
- [R7: Token cost estimation](#r7-token-cost-estimation)
- [Report formats](#report-formats)

---

## R1: Orphan detection

**Severity:** HIGH

A skill is orphaned when it exists on disk but is never referenced in any platform config or skill registry, and no active trigger phrase matches real user query patterns.

### Detection algorithm

1. Collect all skill registry files:
   - `~/.openclaw/openclaw.json` (OpenClaw)
   - `~/.claude/settings.json` and `~/.claude/settings.local.json` (Claude Code)
   - `~/.agents/config.json` (OpenAI Codex)
   - Project-level `.claude/settings.json` in current directory
2. Search for any reference to the skill's `name` field in those files.
3. If not found in any registry, flag as potential orphan.
4. Secondary check: scan `description` trigger phrases against recent platform session logs (if available at `~/.openclaw/logs/` or similar). Zero matches in the last 30 days = confirmed orphan.

### Real example (from 22-skill audit)

A skill named `claude-code-autonomy` was installed in `~/.openclaw/skills/`. It had a valid SKILL.md (scan score: 8/10). Static scan found no issues. But it had never been activated — the trigger phrases ("autonomy", "trust level") never appeared in any session. After investigation: the skill was installed during an experiment, the experiment ended, the skill was forgotten. Found with R1, deleted immediately.

### Output

```text
[FAIL] R1 HIGH -- Orphan skill: not referenced in any config or skill registry
       No registry reference found in: ~/.openclaw/openclaw.json, ~/.claude/settings.json
       Trigger phrases matched 0 sessions in last 30 days
       Action: either register in platform config or delete
```

---

## R2: Duplicate detection

**Severity:** HIGH

Two or more skill directories across different locations contain SKILL.md files with the same `name` field. The platform loads one and silently ignores the others.

### Detection algorithm

1. Scan all known skill directories:
   - `~/.openclaw/skills/`
   - `~/.claude/skills/`
   - `~/.agents/skills/`
   - `~/clawd/skills/` (project-level)
   - `.claude/skills/` (current project)
2. For each SKILL.md found, extract the `name` field from YAML frontmatter.
3. Group by `name`. Any name appearing 2+ times = duplicate.
4. Report all paths where the name appears.

### Real example (from 22-skill audit)

The `reprompter` skill existed in both `~/.openclaw/skills/reprompter/` and `~/clawd/skills/reprompter/`. The developer had been editing the `~/clawd/` copy for two weeks. OpenClaw was loading the `~/.openclaw/` copy (older, without recent changes). The updated version was never live.

**Resolution:** Delete the stale copy, keep one canonical location. If access from multiple locations is needed, use a symlink.

### Output

```text
[FAIL] R2 HIGH -- Duplicate name "reprompter" found in 2 locations:
       1. ~/.openclaw/skills/reprompter/SKILL.md (modified: 2 weeks ago)
       2. ~/clawd/skills/reprompter/SKILL.md (modified: today)
       Action: remove duplicate, symlink if needed
```

---

## R3: Trigger collision detection

**Severity:** HIGH

Two or more skills have description trigger phrases that overlap significantly (≥ 80% Jaccard similarity). When the user types a matching phrase, the platform picks one skill non-deterministically.

### Detection algorithm

1. For each skill, extract trigger phrases from the `description` field.
2. Tokenize: lowercase, split on whitespace and punctuation, remove stop words (the, for, use, any, a, an, in, of, to, and, or, with, this, that, is, are, it, on, at, by).
3. For each pair of skills, compute Jaccard similarity: `|A ∩ B| / |A ∪ B|`.
4. Report pairs with similarity ≥ 0.80 (80%).

### Jaccard similarity example

```text
denizevi-music keywords: {müzik, çal, play, music, speaker, ses, seviyesi, playlist}
denizevi keywords:        {müzik, çal, play, music, speaker, status, klima, ışık}

Intersection: {müzik, çal, play, music, speaker} = 5 terms
Union: {müzik, çal, play, music, speaker, ses, seviyesi, playlist, status, klima, ışık} = 11 terms
Jaccard: 5/11 = 0.45 → below threshold, no collision

# If denizevi also had: "ses seviyesi, playlist" in its description:
Intersection: 7, Union: 11 → Jaccard: 0.636 → still below 0.80
# Threshold is intentionally high to avoid false positives
```

### Real example (from 22-skill audit)

Three skills in the research category all had "araştır, research, search, web, find" in their descriptions. Jaccard similarity between any two was 0.83. On the trigger phrase "web'de araştır", all three activated. Platform picked the first loaded. Users reported inconsistent behavior for identical queries.

### Output

```text
[WARN] R3 HIGH -- Trigger overlap 85% between:
       - denizevi-music: "müzik çal", "play music", "speaker", "ses seviyesi"
       - denizevi: "müzik çal", "play music", "speaker status", "klima"
       Shared terms: müzik, çal, play, music, speaker
       Action: make trigger domains exclusive, add cross-references
```

---

## R4: Dependency check

**Severity:** HIGH

A file referenced in SKILL.md (script, config, or resource) does not exist at the expected path.

### Detection algorithm

1. Scan SKILL.md body for file references:
   - Markdown links: `[text](path)`
   - Code block commands: `bash path/to/script.sh`, `python path/to/script.py`
   - Inline code: `` `path/to/file` `` that looks like a file path (contains `/` or `.`)
   - Shell commands: `source path`, `cat path`, `./script.sh`
2. Resolve each path relative to SKILL.md location.
3. Check if the file exists with `stat` or equivalent.
4. Report missing files.

### Real example (from 22-skill audit)

Four skills referenced scripts that had been deleted or moved during a refactor:
- `bash scripts/analyze.sh` → `scripts/` directory deleted months ago
- `python references/config_validator.py` → file renamed to `validate.py`
- `source .env.skill` → `.env.skill` never created (was a planned feature)

All four skills had clean static scan scores. None of the missing files were caught until `--healthcheck` R4.

### Output

```text
[FAIL] R4 HIGH -- Broken dependency: scripts/analyze.sh referenced but not found
       Referenced at: SKILL.md line 47 (bash scripts/analyze.sh)
       Resolved path: ~/.openclaw/skills/my-skill/scripts/analyze.sh
       Action: create the file or update the reference
```

---

## R5: URL validation

**Severity:** MEDIUM

A URL referenced in a curl command or markdown link returns HTTP 404 or does not respond within 5 seconds.

### Detection algorithm

1. Scan SKILL.md and all reference files for URLs:
   - `curl` commands: extract URL argument (first non-flag argument after `curl`)
   - Markdown links: `[text](https://...)`
   - Plain URLs: `https?://[^\s)]+`
2. Skip placeholder URLs: `example.com`, `your-domain.com`, `localhost`, `127.0.0.1`, `192.168.*`.
3. For each real URL, send HTTP HEAD request with 5-second timeout.
4. Flag any URL returning 4xx, 5xx, or timing out.

### Real example (from 22-skill audit)

A home automation skill had curl commands hitting a local API proxy that was decommissioned:

```bash
# In SKILL.md:
curl -X POST https://api.home-proxy.internal/v1/lights

# Returned: Connection refused (proxy was shut down 3 months ago)
# Static scan: PASS. Health check R5: FAIL.
```

After the proxy shutdown, the skill continued to score 10/10 on scan. Every curl in it was broken. Only R5 caught it.

### Output

```text
[WARN] R5 MEDIUM -- Stale endpoint: https://api.example.com/v1 returned 404
       Found in: SKILL.md line 82 (curl -X GET https://api.example.com/v1/status)
       Response: HTTP 404 (checked at 2026-02-19 02:00 UTC)
       Action: update URL or remove the curl command
```

---

## R6: Environment variable check

**Severity:** MEDIUM

A `$VARIABLE_NAME` reference appears in SKILL.md but is not currently set in the environment.

### Detection algorithm

1. Scan SKILL.md and all reference files for `$VAR` patterns:
   - `\$[A-Z][A-Z0-9_]+` (uppercase convention for env vars)
   - Exclude common shell builtins: `$PATH`, `$HOME`, `$USER`, `$SHELL`, `$PWD`, `$TMPDIR`
   - Exclude variable expansions that are clearly code examples (inside triple-backtick blocks labeled as example)
2. Collect unique variable names.
3. Compare against current environment: `env | grep "^${VAR_NAME}="`
4. Report any that are not set.

### Real example (from 22-skill audit)

A music assistant skill referenced four API keys:

```bash
# In SKILL.md:
curl -H "Authorization: Bearer $SUNO_API_KEY" https://api.suno.ai/v1/generate
curl -H "X-API-Key: $SPOTIFY_CLIENT_SECRET" https://api.spotify.com/v1/me
```

`$SUNO_API_KEY` was set. `$SPOTIFY_CLIENT_SECRET` was not — the Spotify integration was planned but never configured. The skill would fail silently at runtime for any Spotify command.

### Output

```text
[WARN] R6 MEDIUM -- Missing env var: $SPOTIFY_CLIENT_SECRET not set
       Referenced at: SKILL.md line 94, line 97
       Action: set the variable or remove the reference if unused
       
[INFO] R6 -- Env var OK: $SUNO_API_KEY (set)
```

---

## R7: Token cost estimation

**Severity:** LOW

Estimates the total token load per session when this skill is active. Includes SKILL.md body plus any reference files that are auto-loaded (listed in a routing table or always-include directive).

### Estimation algorithm

1. For SKILL.md: `wc -w SKILL.md` × 1.5 (mixed prose/code typical multiplier).
2. For each auto-loaded reference file (referenced in SKILL.md routing table): `wc -w <file>` × 1.5 (prose) or × 1.7 (code-heavy — more than 30% of content is code blocks).
3. Sum all auto-loaded files. On-demand reference files (loaded only when requested) are listed separately but not included in base cost.
4. Add YAML frontmatter overhead: ~100 tokens.

### Real examples (from 22-skill audit)

| Skill | SKILL.md | Auto-loaded refs | Total |
|-------|----------|-----------------|-------|
| denizevi | 2,100 tokens | 1,100 (homeassistant-api.md) | 3,200 |
| reprompter | 3,800 tokens | 1,796 (scoring-rubric.md) | 5,596 |
| skeall | 4,500 tokens | none auto-loaded | 4,500 |
| x-research | 2,200 tokens | 800 (query-patterns.md) | 3,000 |

`reprompter` was the heaviest at 5,596 tokens — just under the 5,000-token guideline for SKILL.md body alone. The auto-loaded reference pushed total session cost high. After refactoring the reference to on-demand loading, total dropped to 3,800 tokens.

### Output

```text
[INFO] R7 LOW -- Token cost: ~4,500 tokens loaded per session
       SKILL.md: ~4,500 tokens (3,000 words × 1.5)
       Auto-loaded refs: none
       On-demand refs: references/anti-patterns.md (~3,200 tokens), references/scoring.md (~800 tokens)
       Total auto-load budget: 4,500 tokens (within 5,000 token guideline)
```

---

## Report formats

### Single skill healthcheck

```text
## Skill Health Check: {skill-name}

RUNTIME
  [FAIL] R1 HIGH -- Orphan skill: not referenced in any config or skill registry
  [FAIL] R4 HIGH -- Broken dep: scripts/analyze.sh referenced but file not found
  [WARN] R5 MEDIUM -- Stale endpoint: https://api.example.com/v1 returned 404
  [WARN] R6 MEDIUM -- Missing env var: $SUNO_API_KEY not set
  [INFO] R7 LOW -- Token cost: ~2,450 tokens loaded per session

DUPLICATES
  [FAIL] R2 HIGH -- Duplicate name "reprompter" found in:
    - ~/.openclaw/skills/reprompter/SKILL.md (modified: 2 weeks ago)
    - ~/clawd/skills/reprompter/SKILL.md (modified: today)

TRIGGER COLLISIONS
  [WARN] R3 HIGH -- Trigger overlap 85% between:
    - denizevi-music: "müzik çal", "play music", "speaker"
    - denizevi: "müzik çal", "play music", "speaker status"

Summary: 2 FAIL (must fix) | 2 WARN (runtime risk) | 1 INFO
```

### Batch healthcheck (`--healthcheck-all`)

```text
## Batch Health Check

| Skill | Orphan | Duplicates | Broken Deps | Stale URLs | Missing Env | Est. Tokens |
|-------|--------|------------|-------------|------------|-------------|-------------|
| denizevi | OK | OK | FAIL 2 files | OK | FAIL $HA_TOKEN | 3,200 |
| reprompter | OK | FAIL duplicate | OK | OK | OK | 5,596 |
| x-research | OK | FAIL 3 copies | OK | OK | OK | 3,000 |
| skeall | OK | OK | OK | OK | OK | 4,500 |

Trigger Collisions:
  - denizevi ↔ denizevi-music (85% overlap on: müzik, play, music, speaker)
  - x-research (3 copies found, R2 failure)

Summary: 4 skills checked | 2 with FAIL | 1 with WARN | 1 clean
```

### Label meanings

| Label | Severity | Meaning | Action |
|-------|----------|---------|--------|
| `[FAIL]` | HIGH | Runtime breakage confirmed | Must fix before relying on skill |
| `[WARN]` | MEDIUM | Runtime risk detected | Should fix; skill may partially work |
| `[INFO]` | LOW | Informational only | No action required |
