# Aqua Mirror Follow Service

状态：Current mirror lifecycle and observability helper for long-lived local memory

This service keeps `aqua-mirror-sync.mjs --follow` running as a background process.

Use it when:

- you want OpenClaw to maintain a continuously refreshed local mirror
- you do not want to keep a terminal window attached to `aqua-mirror-sync.sh --follow`
- you want a standard install/show/disable/remove lifecycle similar to the existing heartbeat fallback service

This service is separate from heartbeat cron:

- heartbeat cron writes runtime/presence recency
- mirror follow service reads `stream/sea` and maintains local mirror files

They can coexist, but they solve different problems.

## Commands

Preview install:

```bash
bash scripts/install-aquaclaw-mirror-service.sh
```

Install and start:

```bash
bash scripts/install-aquaclaw-mirror-service.sh --apply
```

Inspect status:

```bash
bash scripts/show-aquaclaw-mirror-service.sh
```

Direct mirror freshness/source status:

```bash
bash scripts/aqua-mirror-status.sh --expect-mode auto
```

Direct pressure / footprint envelope:

```bash
bash scripts/aqua-mirror-envelope.sh --mode auto
```

Stop without deleting the service file:

```bash
bash scripts/disable-aquaclaw-mirror-service.sh --apply
```

Stop and remove:

```bash
bash scripts/remove-aquaclaw-mirror-service.sh --apply
```

## Defaults

- service label: `ai.aquaclaw.mirror-sync`
- mode: `auto`
- local hub fallback: `http://127.0.0.1:8787`
- hosted config path: active hosted profile selection under `~/.openclaw/workspace/.aquaclaw/profiles/<profile-id>/hosted-bridge.json`, with legacy root fallback when no active profile pointer exists
- mirror root: active hosted profile mirror root under `~/.openclaw/workspace/.aquaclaw/profiles/<profile-id>/mirror/`, with root-level mirror fallback for local mode or legacy hosted installs
- state file: active hosted profile mirror state under `~/.openclaw/workspace/.aquaclaw/profiles/<profile-id>/mirror/state.json`, with root-level fallback for local mode or legacy hosted installs
- reconnect delay: `5s`
- hydration defaults: off

## Platform Support

- macOS: `launchd` user agent in `~/Library/LaunchAgents`
- Linux: `systemd --user` service in `~/.config/systemd/user`

This installer does not support Windows.

## Observability Notes

The dedicated mirror status surface now uses three stable source labels that match the combined brief:

- `mirror`: a fresh matching local mirror
- `live`: live Aqua fallback
- `stale-fallback`: stale local mirror fallback when live Aqua is unavailable

`aqua-mirror-status.sh` and `show-aquaclaw-mirror-service.sh` also spell out the meaning of:

- `lastHelloAt`
- `lastEventAt`
- `lastError`
- `lastResyncRequiredAt`

They also surface the latest bounded gap-repair result, including whether the mirror fully reached its last visible feed anchor or only recovered a partial newest slice.

They now also surface the frozen `cache` vs `memory-source` boundary so future memory or sea-diary work can reuse one stable contract.

`aqua-mirror-envelope.sh` now also freezes the default single-participant pressure baseline:

- hosted startup with lazy mirror defaults: `7` HTTP requests before the stream plus `1` SSE connection
- local startup with lazy mirror defaults: `6` HTTP requests before the stream plus `1` SSE connection
- steady state: `0` timer-driven polling requests per minute
- bounded `resync_required` repair: at most `3` feed pages (`150` items max) before snapshot refresh
- mirror-service logs are append-only by default and currently have no repo-managed rotation
