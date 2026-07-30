# Publishing Guide

This document describes how to publish new versions of this skill to [ClawHub](https://clawhub.ai/skill/nano-banana-pro-prompts-recommend).

## Architecture Overview

The skill uses a **split distribution model**:

| Layer | What | Where | How updated |
|-------|------|-------|-------------|
| **Code** | `SKILL.md`, `setup.js`, `package.json` | ClawHub | Manual `clawhub publish` |
| **Data** | `references/*.json` (31 MB+) | GitHub (this repo) | GitHub Actions (twice daily) |

The `references/` data files are **never uploaded to ClawHub** — they exceed the 20 MB limit. Instead, `scripts/setup.js` downloads them from GitHub at install time via `postinstall`.

---

## When to Publish to ClawHub

| Change type | Action needed |
|-------------|---------------|
| SKILL.md updated | Publish new version to ClawHub |
| `setup.js` logic changed | Publish new version to ClawHub |
| New prompts added to CMS | Push to GitHub only — Actions handle the rest |
| New prompt categories | Push to GitHub only (manifest.json auto-regenerated) |

---

## Publishing a New Version

### 1. Make your changes

Edit files in the local skill directory:
```
skills/nano-banana-pro-prompts-recommend/
```

### 2. Bump the version

Edit `package.json`:
```json
{
  "version": "x.y.z"
}
```

### 3. Create a temp directory with only the required files

**Do NOT publish the full directory** — it includes 31 MB of references data that will exceed ClawHub's 20 MB upload limit.

```bash
TMP_DIR=$(mktemp -d)
SKILL_DIR=~/clawd/skills/nano-banana-pro-prompts-recommend

cp "$SKILL_DIR/SKILL.md"   "$TMP_DIR/"
cp "$SKILL_DIR/README.md"  "$TMP_DIR/"
cp "$SKILL_DIR/package.json" "$TMP_DIR/"
mkdir -p "$TMP_DIR/scripts"
cp "$SKILL_DIR/scripts/setup.js" "$TMP_DIR/scripts/"
mkdir -p "$TMP_DIR/references"
cp "$SKILL_DIR/references/manifest.json" "$TMP_DIR/references/"
```

Total upload size: ~50 KB.

### 4. Publish

```bash
clawhub publish "$TMP_DIR" \
  --slug nano-banana-pro-prompts-recommend \
  --name "Nano Banana Pro Prompt Recommender" \
  --version x.y.z \
  --changelog "describe what changed"
```

### 5. Clean up

```bash
rm -rf "$TMP_DIR"
```

---

## Files Uploaded to ClawHub

| File | Size | Purpose |
|------|------|---------|
| `SKILL.md` | ~15 KB | Agent instructions (rendered on ClawHub page) |
| `README.md` | ~9 KB | Human-readable docs |
| `package.json` | ~1.3 KB | Metadata, postinstall hook |
| `scripts/setup.js` | ~4 KB | Downloads references from GitHub at install time |
| `references/manifest.json` | ~1.6 KB | Category directory (not the prompt data) |

## Files NOT Uploaded (live on GitHub)

- `references/*.json` (except `manifest.json`) — the actual prompt data, 31 MB+
- `scripts/generate-references.ts` — internal CMS sync script, not needed by end users
- `.github/` — CI workflows

---

## Data Updates (No ClawHub Publish Needed)

Prompt data is synced automatically from the CMS:

- **Schedule**: Twice daily at 00:00 and 12:00 UTC via GitHub Actions
- **To force a sync**: trigger `generate-references.yml` manually in GitHub Actions
- **Users update locally**: `pnpm run sync` or `node scripts/setup.js --force`

---

## ClawHub Skill Page

https://clawhub.ai/skill/nano-banana-pro-prompts-recommend
