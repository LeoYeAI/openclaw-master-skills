# Exec Approvals Reference

Exec approvals control whether and how shell commands run on the gateway host or a node. This page covers the approval flow, allowlists, safe bins, and forwarding.

## Where It Applies

Exec approvals apply when `host=gateway` or `host=node` (not sandbox).

## Settings and Storage

- Stored in `~/.openclaw/exec-approvals.json`.
- Config keys under `tools.exec.*`.

## Policy Knobs

### Security (`exec.security`)

| Mode | Behavior |
|---|---|
| `deny` | Block all exec (default for sandbox) |
| `allowlist` | Only allowlisted commands (default for gateway+node when unset) |
| `full` | Allow all commands |

### Ask (`exec.ask`)

| Mode | Behavior |
|---|---|
| `off` | Never prompt |
| `on-miss` | Prompt only when command not in allowlist (default) |
| `always` | Always prompt, even for allowlisted commands |

### Ask Fallback (`askFallback`)

Controls what happens when no approval UI is available (e.g., headless gateway).

## Allowlist (Per Agent)

Commands approved via the approval flow are stored per-agent in `~/.openclaw/exec-approvals.json`.

## Auto-Allow Skill CLIs

`autoAllowSkills` can auto-approve commands from installed skills' CLIs.

## Safe Bins (stdin-only)

Safe bins are small, stdin-only stream filters that can run without explicit allowlist entries:

- Configured via `tools.exec.safeBins` (e.g., `jq`, `cat`, `head`).
- `tools.exec.safeBinTrustedDirs` — additional trusted directories. Built-in defaults: `/bin`, `/usr/bin`.
- `tools.exec.safeBinProfiles` — custom argv policy per safe bin:
  - `minPositional` — minimum positional args
  - `maxPositional` — maximum positional args
  - `allowedValueFlags` — allowed flags
  - `deniedFlags` — denied flags

Interpreters like `python3`, `node`, `ruby`, `bash` are **not** safe bins — they can execute arbitrary code.

Run `openclaw security audit` to check `safeBins` config. Run `openclaw doctor --fix` to apply fixes.

### Safe Bins versus Allowlist

- **Safe bins**: Implicit trust for simple stdin→stdout filters. No storage needed.
- **Allowlist**: Explicit trust for specific executable paths. Stored per-agent.

## Control UI Editing

The Control UI provides a visual editor for the exec approvals allowlist.

## Approval Flow

1. Agent calls `exec` with `host=gateway` or `host=node`.
2. If the command is not allowlisted and `ask != off`:
   - Returns `status: "approval-pending"`.
   - Approval prompt is sent to the companion app, node host, or chat channel.
3. User approves or denies.
4. Returns `Exec finished` or `Exec denied`.

`tools.exec.approvalRunningNoticeMs` (default 10000) — emits `Exec running` notice for long-running approvals.

## Approval Forwarding to Chat Channels

Exec approval prompts can be forwarded to chat channels for remote approval.

### macOS IPC Flow

Uses macOS IPC to forward approval prompts between the gateway and companion app.

## System Events

Exec completions generate system events that can trigger heartbeat wakes.

## Implications

- Keep the allowlist minimal.
- Use `security=allowlist` + `ask=on-miss` for a balanced security posture.
- Use `security=deny` for maximum restriction.
- Review `~/.openclaw/exec-approvals.json` regularly.
