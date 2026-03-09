# Architecture

This skill follows a simple split:

- event adapter: convert engine completion events into a normalized payload
- message formatter: turn raw task state into natural language
- transport adapter: deliver through OpenClaw or another channel

## Current choices

- runtime shape: lightweight shell script
- engine adapter: Claude Code hook
- transport: OpenClaw-configured outbound message
- policy: optional self-only guard when configured

## Why this shape

- keeps Claude-specific logic thin
- keeps notification transport swappable
- fits a broader OpenClaw-style agent OS where engines are adapters

## Future work

- Codex completion adapter
- OpenClaw node notify adapter for direct macOS notifications
- webhook transport for cloud execution
- richer recipient profiles and per-project voice/tone
