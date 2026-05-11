# Changelog

All notable changes to this skill will be documented in this file.

The format is based on Keep a Changelog, and this project adheres to Semantic Versioning.

## [2.5.0] - 2026-02-14

### Added
- `handoff` command to run human-in-the-loop steps with completion checks (selector/text/url/cookie/storage), including `check` and `wait` modes.
- `--match all|any` for handoff checks (AND vs OR).
- `suggested_user_message` output to provide a consistent, ready-to-send “hey human do this” message with the Live Debugger URL.
- `get-downloads` command to download the session downloads archive.
- `--no-logs` option to disable Browserbase session logging separately from recording.
- MIT `LICENSE`.

### Changed
- Session creation now controls `log_session` independently (recording and logs are no longer coupled).
- `start-workspace` now returns `human_handoff` when it reconnects to an already-running workspace session (instead of returning without a debugger link).
- `get-session` and `live-url` now include `pending_handoff` so the agent can detect and prioritize outstanding human steps.
- Error JSON now includes `"status": "error"` for more consistent machine parsing.
- `human_handoff` now includes fullscreen share variants (`share_text_fullscreen`, `share_markdown_fullscreen`).
- Documentation expanded to describe the golden-path handover process and the full tool surface.

