# Exec Tool — Detailed Reference

The `exec` tool executes shell commands on behalf of the AI agent. It supports sandbox, gateway, and node hosts, with configurable security policies and approval flows.

## Parameters

| Parameter | Default | Description |
|---|---|---|
| `command` | (required) | Shell command to execute |
| `workdir` | cwd | Working directory |
| `env` | — | Key/value env overrides |
| `yieldMs` | 10000 | Auto-background after this delay |
| `background` | false | Background immediately |
| `timeout` | 1800 (seconds) | Kill on expiry |
| `pty` | false | Run in pseudo-terminal (TTY-only CLIs, terminal UIs) |
| `host` | sandbox | Where to execute: `sandbox \| gateway \| node` |
| `security` | deny (sandbox) | Enforcement mode: `deny \| allowlist \| full` |
| `ask` | on-miss | Approval prompts: `off \| on-miss \| always` |
| `node` | — | Node id/name for `host=node` |
| `elevated` | false | Request elevated mode (gateway host) |

### Host Behavior

- `host` defaults to `sandbox`.
- `elevated` is ignored when sandboxing is off (exec already runs on the host).
- `gateway`/`node` approvals are controlled by `~/.openclaw/exec-approvals.json`.
- `node` requires a paired node (companion app or headless node host).
- If multiple nodes are available, set `exec.node` or `tools.exec.node` to select one.

### Shell Selection

- **Non-Windows**: Uses `SHELL` when set. If `SHELL` is `fish`, prefers `bash` (or `sh`) from `PATH` to avoid fish-incompatible scripts, falls back to `SHELL` if neither exists.
- **Windows**: Prefers PowerShell 7 (`pwsh`) discovery (Program Files, ProgramW6432, then PATH), falls back to Windows PowerShell 5.1.

### Security Notes

- Host execution (`gateway`/`node`) rejects `env.PATH` and loader overrides (`LD_*`/`DYLD_*`) to prevent binary hijacking.
- **Sandboxing off + `host=sandbox`**: Exec fails closed (does not silently run on gateway). Enable sandboxing or use `host=gateway` with approvals.
- Script preflight checks only inspect files inside the effective `workdir` boundary.

## Config

```json5
{
  tools: {
    exec: {
      notifyOnExit: true,                  // Enqueue system event on bg exit (default: true)
      approvalRunningNoticeMs: 10000,      // "Running" notice for long approval-gated exec
      host: "sandbox",                     // Default host
      security: "deny",                    // Default: deny for sandbox, allowlist for gateway+node
      ask: "on-miss",                      // Default approval prompt mode
      node: "node-id-or-name",            // Pin exec to a specific node
      pathPrepend: ["~/bin", "/opt/oss/bin"], // Prepend to PATH (gateway+sandbox only)
      safeBins: ["jq", "cat", "head"],     // stdin-only safe binaries
      safeBinTrustedDirs: ["/usr/local/bin"], // Extra trusted dirs for safeBins
      safeBinProfiles: { ... },            // Custom argv policy per safe bin
    },
  },
}
```

### PATH Handling

- **`host=gateway`**: Merges login-shell `PATH` into exec environment. `env.PATH` overrides rejected.
  - macOS: `/opt/homebrew/bin`, `/usr/local/bin`, `/usr/bin`, `/bin`
  - Linux: `/usr/local/bin`, `/usr/bin`, `/bin`
- **`host=sandbox`**: Runs `sh -lc` (login shell) inside the container. `tools.exec.pathPrepend` applies.
- **`host=node`**: `env.PATH` overrides rejected and ignored by node hosts. Configure node host service environment for additional entries.

## Session Overrides (/exec)

Use `/exec` slash command to override exec settings for the current session:

```
/exec host=gateway security=allowlist ask=on-miss node=mac-1
```

Overridable: `host`, `security`, `ask`, `node`.

## Authorization Model

- `/exec` overrides share the agent's trust level.
- `commands.useAccessGroups` can restrict who uses `/exec`.
- `tools.deny: ["exec"]` completely disables the exec tool.
- `security=full` + `ask=off` allows unrestricted execution (dangerous).

## Exec Approvals

Gateway and node execution uses approval flow. See [Exec Approvals](exec_approvals.md) for details.

- Returns `status: "approval-pending"` while waiting.
- Returns `Exec finished` or `Exec denied` on completion.
- `tools.exec.approvalRunningNoticeMs` emits an `Exec running` notice after delay.

## Allowlist + Safe Bins

When `security=allowlist`:
- Commands are checked against the allowlist.
- Compound commands (`;`, `&&`, `||`) are checked per segment.
- `autoAllowSkills` can auto-approve skill CLIs.

Safe bins:
- `tools.exec.safeBins` — small, stdin-only stream filters (e.g., `jq`, `cat`, `head`).
- `tools.exec.safeBinTrustedDirs` — explicit extra trusted dirs for safe-bin executable paths. Default: `/bin`, `/usr/bin`.
- `tools.exec.safeBinProfiles` — explicit argv policy per safe bin (`minPositional`, `maxPositional`, `allowedValueFlags`, `deniedFlags`).

See [Exec approvals: safe bins](exec_approvals.md).

## Process Tool (Background Sessions)

The `process` tool manages backgrounded exec sessions:

| Action | Description |
|---|---|
| `list` | List background sessions |
| `poll` | Get new output and exit status |
| `log` | View output with `offset`/`limit` |
| `write` | Write to stdin |
| `send-keys` | Send key sequences (Enter, C-c, Up, etc.) |
| `submit` | Submit current input |
| `paste` | Paste text to stdin |
| `kill` | Kill a session |
| `clear` | Clear session output |
| `remove` | Remove session |

Sessions are scoped per agent; other agents' sessions are not visible.

## Examples

Basic:

```json5
{ "tool": "exec", "command": "ls -la" }
```

Background + poll:

```json5
{"tool":"exec","command":"npm run build","yieldMs":1000}
{"tool":"process","action":"poll","sessionId":"<id>"}
```

Interactive (send keys):

```json5
{"tool":"process","action":"send-keys","sessionId":"<id>","keys":["Enter"]}
{"tool":"process","action":"send-keys","sessionId":"<id>","keys":["C-c"]}
{"tool":"process","action":"send-keys","sessionId":"<id>","keys":["Up","Up","Enter"]}
```

Submit / paste:

```json5
{ "tool": "process", "action": "submit", "sessionId": "<id>" }
{ "tool": "process", "action": "paste", "sessionId": "<id>", "text": "line1\nline2\n" }
```

## apply_patch (Experimental)

`apply_patch` is tied to the `exec` tool. Only available for OpenAI/OpenAI Codex models.

```json5
{
  tools: {
    exec: {
      applyPatch: {
        enabled: true,
        workspaceOnly: true,        // Default: true
        allowModels: ["gpt-5.2"],
      },
    },
  },
}
```

- `allow: ["exec"]` implicitly allows `apply_patch`.
- Config lives under `tools.exec.applyPatch`.
- `workspaceOnly` defaults to `true`. Set to `false` only to intentionally write outside workspace.
