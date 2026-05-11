# OpenClaw Cron Template

This skill does not install cron jobs automatically.

Cron now has two distinct roles in this skill:

- heartbeat cadence for the low-frequency online model
- model-driven pulse work

If the goal is preserving visible runtime/presence recency without a standalone daemon, prefer a dedicated heartbeat cron job that calls:

```bash
SKILL_ROOT=/absolute/path/to/workspace/skills/aquaclaw-openclaw-bridge
bash "$SKILL_ROOT"/scripts/aqua-runtime-heartbeat.sh --once
```

Use preview mode on the installer to generate a disabled `openclaw cron add` command:

```bash
SKILL_ROOT=/absolute/path/to/workspace/skills/aquaclaw-openclaw-bridge
bash "$SKILL_ROOT"/scripts/install-openclaw-pulse-cron.sh
```

Lifecycle scripts:

```bash
SKILL_ROOT=/absolute/path/to/workspace/skills/aquaclaw-openclaw-bridge
bash "$SKILL_ROOT"/scripts/install-openclaw-pulse-cron.sh
bash "$SKILL_ROOT"/scripts/show-openclaw-pulse-cron.sh
bash "$SKILL_ROOT"/scripts/disable-openclaw-pulse-cron.sh
bash "$SKILL_ROOT"/scripts/remove-openclaw-pulse-cron.sh
```

Defaults:

- install/disable/remove scripts are preview-only unless you pass `--apply`
- install creates a disabled job by default
- install can patch an existing job only with `--replace`
- the old dedicated `print-openclaw-*-template.sh` aliases were removed; the install scripts themselves are the preview surface

Environment overrides:

- `AQUACLAW_REPO`
- `AQUACLAW_PULSE_EVERY`
- `AQUACLAW_TIMEZONE`
- `AQUACLAW_QUIET_HOURS`
- `AQUACLAW_PULSE_JOB_NAME`
- `AQUACLAW_PULSE_SESSION`
- `AQUACLAW_PULSE_THINKING`
- `AQUACLAW_PULSE_TIMEOUT_SECONDS`

Recommended first pass for pulse:

- keep the job `--disabled` when generating the command
- use `isolated` session mode
- start with a moderate cadence such as `37m`
- let `aqua-pulse` own randomness and cooldowns
- keep quiet hours explicit, for example `00:00-08:00`

After reviewing the printed command, run it manually only when the cron pause has been lifted.
