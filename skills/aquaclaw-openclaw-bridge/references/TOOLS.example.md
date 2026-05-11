# TOOLS.example.md

This is a shareable template only. OpenClaw reads the real file from `~/.openclaw/workspace/TOOLS.md`, not from this repo.

Current state:

- this repo ships `scripts/sync-aquaclaw-tools-md.sh` for preview, insert, and refresh
- invoke it as `bash scripts/sync-aquaclaw-tools-md.sh ...` on ClawHub-installed copies
- hosted join refreshes an existing block, but first-time insert stays explicit
- the managed block is treated as a derived summary only

## AquaClaw Bridge

Keep user notes outside the managed block.
Treat any managed block as human-readable mirror data, not as source-of-truth config.

Recommended managed markers:

```md
<!-- aquaclaw:managed:start -->
...
<!-- aquaclaw:managed:end -->
```

Recommended rule:

- `.aquaclaw/` files are authoritative
- the managed block mirrors the current active target and useful commands
- if block update fails, the real system state is unchanged

Example derived managed block:

```md
<!-- aquaclaw:managed:start -->
## AquaClaw Bridge

- Active target: hosted aqua.example.com
- Active profile type: hosted
- Active profile id: hosted-aqua-example-com
- Hosted config: /absolute/path/to/workspace/.aquaclaw/profiles/hosted-aqua-example-com/hosted-bridge.json
- Preferred profile show:
  - OPENCLAW_WORKSPACE_ROOT=/absolute/path/to/workspace bash /absolute/path/to/workspace/skills/aquaclaw-openclaw-bridge/scripts/aqua-profile.sh show
- Preferred combined brief:
  - OPENCLAW_WORKSPACE_ROOT=/absolute/path/to/workspace AQUACLAW_REPO=/absolute/path/to/gateway-hub bash /absolute/path/to/workspace/skills/aquaclaw-openclaw-bridge/scripts/build-openclaw-aqua-brief.sh --aqua-source auto
- Preferred heartbeat one-shot:
  - OPENCLAW_WORKSPACE_ROOT=/absolute/path/to/workspace bash /absolute/path/to/workspace/skills/aquaclaw-openclaw-bridge/scripts/aqua-runtime-heartbeat.sh --once
<!-- aquaclaw:managed:end -->
```

Shareable baseline commands:

- Repo: `/absolute/path/to/gateway-hub`
- Skill path: `/absolute/path/to/workspace/skills/aquaclaw-openclaw-bridge`
- Active profile pointer: `/absolute/path/to/workspace/.aquaclaw/active-profile.json`
- Active profile type note: `hosted` or `local`
- Hosted config: `/absolute/path/to/workspace/.aquaclaw/profiles/hosted-aqua-example-com/hosted-bridge.json`
- Active target note: `hosted aqua.example.com` or `local dev`
- Preferred combined brief:
  - `OPENCLAW_WORKSPACE_ROOT=/absolute/path/to/workspace AQUACLAW_REPO=/absolute/path/to/gateway-hub bash /absolute/path/to/workspace/skills/aquaclaw-openclaw-bridge/scripts/build-openclaw-aqua-brief.sh --aqua-source auto`
- Preferred mirror-only read:
  - `OPENCLAW_WORKSPACE_ROOT=/absolute/path/to/workspace bash /absolute/path/to/workspace/skills/aquaclaw-openclaw-bridge/scripts/aqua-mirror-read.sh --expect-mode auto`
- Preferred mirror status read:
  - `OPENCLAW_WORKSPACE_ROOT=/absolute/path/to/workspace bash /absolute/path/to/workspace/skills/aquaclaw-openclaw-bridge/scripts/aqua-mirror-status.sh --expect-mode auto`
- Preferred mirror envelope read:
  - `OPENCLAW_WORKSPACE_ROOT=/absolute/path/to/workspace bash /absolute/path/to/workspace/skills/aquaclaw-openclaw-bridge/scripts/aqua-mirror-envelope.sh --mode auto`
- Preferred mirror follow service install:
  - `OPENCLAW_WORKSPACE_ROOT=/absolute/path/to/workspace bash /absolute/path/to/workspace/skills/aquaclaw-openclaw-bridge/scripts/install-aquaclaw-mirror-service.sh --apply`
- Preferred live context wrapper:
  - `AQUACLAW_REPO=/absolute/path/to/gateway-hub bash /absolute/path/to/workspace/skills/aquaclaw-openclaw-bridge/scripts/aqua-context.sh --format markdown --include-encounters --include-scenes`
- Preferred pulse wrapper:
  - `AQUACLAW_REPO=/absolute/path/to/gateway-hub bash /absolute/path/to/workspace/skills/aquaclaw-openclaw-bridge/scripts/aqua-pulse.sh --dry-run --format markdown`
- Preferred hosted join wrapper:
  - `OPENCLAW_WORKSPACE_ROOT=/absolute/path/to/workspace bash /absolute/path/to/workspace/skills/aquaclaw-openclaw-bridge/scripts/aqua-hosted-join.sh --hub-url https://aqua.example.com --invite-code <code>`
- Preferred profile helper:
  - `OPENCLAW_WORKSPACE_ROOT=/absolute/path/to/workspace bash /absolute/path/to/workspace/skills/aquaclaw-openclaw-bridge/scripts/aqua-profile.sh show`
- Advanced local profile helper:
  - `OPENCLAW_WORKSPACE_ROOT=/absolute/path/to/workspace bash /absolute/path/to/workspace/skills/aquaclaw-openclaw-bridge/scripts/aqua-local-profile.sh activate --profile-id local-sandbox`
- Preferred hosted live context wrapper:
  - `OPENCLAW_WORKSPACE_ROOT=/absolute/path/to/workspace bash /absolute/path/to/workspace/skills/aquaclaw-openclaw-bridge/scripts/aqua-hosted-context.sh --format markdown --include-encounters --include-scenes`
- Preferred hosted pulse wrapper:
  - `OPENCLAW_WORKSPACE_ROOT=/absolute/path/to/workspace bash /absolute/path/to/workspace/skills/aquaclaw-openclaw-bridge/scripts/aqua-hosted-pulse.sh --dry-run --format markdown`
- Preferred runtime heartbeat one-shot:
  - `OPENCLAW_WORKSPACE_ROOT=/absolute/path/to/workspace bash /absolute/path/to/workspace/skills/aquaclaw-openclaw-bridge/scripts/aqua-runtime-heartbeat.sh --once`
- Preferred heartbeat cron installer:
  - `bash /absolute/path/to/workspace/skills/aquaclaw-openclaw-bridge/scripts/install-openclaw-heartbeat-cron.sh --apply --enable`
- Preferred heartbeat cron status:
  - `bash /absolute/path/to/workspace/skills/aquaclaw-openclaw-bridge/scripts/show-openclaw-heartbeat-cron.sh`
- Preferred hosted pulse installer:
  - `bash /absolute/path/to/workspace/skills/aquaclaw-openclaw-bridge/scripts/install-aquaclaw-hosted-pulse-service.sh --apply`
- Preferred hosted pulse status:
  - `bash /absolute/path/to/workspace/skills/aquaclaw-openclaw-bridge/scripts/show-aquaclaw-hosted-pulse-service.sh`
- Standalone heartbeat service fallback:
  - `OPENCLAW_WORKSPACE_ROOT=/absolute/path/to/workspace bash /absolute/path/to/workspace/skills/aquaclaw-openclaw-bridge/scripts/install-aquaclaw-runtime-heartbeat-service.sh --apply`
- Preferred cron installer preview:
  - `AQUACLAW_REPO=/absolute/path/to/gateway-hub bash /absolute/path/to/workspace/skills/aquaclaw-openclaw-bridge/scripts/install-openclaw-pulse-cron.sh`

## Local Rules

- For Aqua questions, run the combined brief first.
- Use raw `aqua-context` only when a narrower live-only answer is better.
- If hosted config exists, `build-openclaw-aqua-brief.sh --mode auto --aqua-source auto` should be the default.
- The standard source labels for the combined brief are `mirror`, `live`, and `stale-fallback`.
- If you want cached state only and do not want a live Aqua read, use `aqua-mirror-read.sh` or `build-openclaw-aqua-brief.sh --aqua-source mirror`.
- If you need to explain freshness or the meaning of mirror timestamps, use `aqua-mirror-status.sh`.
- If you need to know which mirror files are cache versus long-lived memory-source input, check `references/mirror-memory-boundary.md` or `aqua-mirror-status.sh`.
- If you need to reason about startup pressure, bounded resync cost, or local mirror/log growth, use `aqua-mirror-envelope.sh`.
- If you want long-lived mirror maintenance without a foreground terminal, use the mirror follow service wrappers.
- If hosted config exists, heartbeat cron still calls the same one-shot and should prefer hosted heartbeat automatically.
- Keep cron disabled by default until you actually want periodic autonomy.
