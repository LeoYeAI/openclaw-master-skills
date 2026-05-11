# SignalRadar Release Checklist

## Environment Fingerprint Gates (Blocker)

- Before functional checks, pick one target profile:
  - `local-publish` (validate publish repository on local machine)
  - `remote-runtime` (validate deployed skill on remote OpenClaw workspace)
- Both profiles must validate `skills/signalradar/RELEASE_FINGERPRINT.json`.
- If profile/target mismatches, stop immediately and mark result as `WRONG_TARGET`.
- Do not score blocked checks as pass.

### Profile A: local-publish

- Verify:
  - workspace path is expected local path
  - `git remote -v` points to publish repository
  - current `HEAD` contains expected release commit
  - `RELEASE_FINGERPRINT.json` matches expected commit

### Profile B: remote-runtime

- Verify:
  - skill path exists at runtime workspace
  - `RELEASE_FINGERPRINT.json` exists and matches expected commit
  - do not require remote git branch/remote URL to equal local publish repo
  - runtime gates (clean dry-run) pass on target host

## Packaging

- Include: `SKILL.md`, `RELEASE_FINGERPRINT.json`, `references/*`, required scripts/assets only.
- Exclude: secrets, local cache, logs, user private data.

## Contract Quality Gates

- Protocol examples validate against current schema.
- `abs_pp` default trigger (`5.0`) passes regression checks.
- Dedup default-off behavior is verified.
- Retry and idempotent delivery behavior is verified.
- Failure paths emit standard error envelope.

## UX Gates

- Push text contains full market question (no truncation).
- Push text includes baseline/current/abs delta/time/reason/request_id.
- Time render matches `UTC + user timezone`.

## Compatibility Gates

- ClawHub package metadata and directory layout are valid.
- Core protocol remains platform-agnostic.
- Adapter changes do not alter core object contracts.

## Runtime Reliability Gates (MVP)

- Install-time smoke test passes:
  - `python3 scripts/sr_smoke_test.py --json`
  - must return `ok=true`.
  - if network is restricted in CI/sandbox and source fetch fails, record as `WARN_ENV` and rerun in a network-allowed environment before release.
- Prepublish gate passes:
  - `python3 scripts/sr_prepublish_gate.py --json`
  - dry-run must return `ok=true` (no longer depends on scheduler runtime logs).
- Workspace path hardcode scan passes:
  - run path scan on runtime scripts and user-facing docs
  - no `/root/.openclaw/workspace` hardcoded path should remain

## Compliance Notes

- State clearly: monitoring tool only, not investment advice.
- User local override must remain highest precedence.
