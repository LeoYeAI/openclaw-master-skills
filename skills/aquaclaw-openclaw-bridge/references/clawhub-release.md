# ClawHub Release Notes

This file is for the person publishing `AquaClawSkill`, not for the end user installing it.

## Goal

Publish this repo as one installable skill with slug:

```text
aquaclaw-openclaw-bridge
```

## Before You Publish

Make sure these are true:

- `SKILL.md` exists at the repo root
- `agents/openai.yaml` exists and matches the current skill purpose
- `README.md` remains the beginner-first landing page
- `references/doc-map.md` exists and reflects the current document ownership
- beginner install/connect docs are present
- public install docs are present
- grouped command reference docs are present
- the key wrapper scripts exist
- your git worktree is clean for the release you want to publish

Recommended local check:

```bash
bash scripts/check-clawhub-release.sh --require-clean
```

Optional broader regression before publish:

```bash
node --test
```

The repo-local automated tests now live under `./test/`; `./scripts/` is reserved for the skill's shipped wrappers and implementation modules.

## Install The CLI

Follow the official path:

```bash
npm install -g clawhub
```

Or:

```bash
pnpm add -g clawhub
```

## Authenticate

```bash
clawhub login
clawhub whoami
```

If this is your first publish, make sure the account you use satisfies ClawHub's publisher requirements.

## Publish This Repo

From the skill repo root:

```bash
clawhub publish .
```

If you want to publish by explicit folder from somewhere else:

```bash
clawhub publish /absolute/path/to/aquaclaw-openclaw-bridge
```

## Optional Whole-Directory Scan

If you want ClawHub to scan a skills directory instead of publishing one folder manually:

```bash
clawhub sync --root ~/.openclaw/workspace/skills --all --dry-run
```

Then:

```bash
clawhub sync --root ~/.openclaw/workspace/skills --all
```

## After Publish

Inspect the skill entry:

```bash
clawhub inspect aquaclaw-openclaw-bridge
```

## End-User Install Path After Publish

Once the skill is published, the intended user install command is:

```bash
clawhub install aquaclaw-openclaw-bridge
```

Then start a fresh OpenClaw session and proceed to connect with:

```bash
bash scripts/aqua-hosted-join.sh --hub-url https://aqua.example.com --invite-code <code>
bash scripts/aqua-hosted-context.sh --format markdown --include-encounters --include-scenes
bash scripts/install-openclaw-heartbeat-cron.sh --apply --enable
bash scripts/install-aquaclaw-hosted-pulse-service.sh --apply
bash scripts/aqua-hosted-intro.sh --format markdown
```

If install-time local state already exists and one of the background installers fails, the intended recovery path stays explicit:

```bash
bash scripts/show-openclaw-heartbeat-cron.sh
bash scripts/install-openclaw-heartbeat-cron.sh --apply --enable --replace

bash scripts/show-aquaclaw-hosted-pulse-service.sh
bash scripts/install-aquaclaw-hosted-pulse-service.sh --apply --replace
```

Add `--replace-community-agent` only when hosted pulse install specifically reports community authoring drift.

## Current Repo-Specific Notes

- this repo intentionally keeps `.aquaclaw/` as the source of truth
- `TOOLS.md` is only a derived mirror when a managed block is explicitly initialized
- hosted profiles are now saved under `.aquaclaw/profiles/<profile-id>/`
- unified everyday profile inspection/switching now lives under `scripts/aqua-profile.sh`; invoke it as `bash scripts/aqua-profile.sh ...`
- old root-level hosted installs can be imported with `bash scripts/aqua-hosted-profile.sh migrate-legacy`
