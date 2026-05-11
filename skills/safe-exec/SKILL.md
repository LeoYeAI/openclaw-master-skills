---
name: safe-exec
description: Safe command execution for OpenClaw Agents with automatic danger pattern detection, risk assessment, user approval workflow, and audit logging. Use when agents need to execute shell commands that may be dangerous (rm -rf, dd, fork bombs, system directory modifications) or require human oversight. Provides multi-level risk assessment (CRITICAL/HIGH/MEDIUM/LOW), in-session notifications, pending request management, and non-interactive environment support for agent automation.
metadata:
  {
    "openclaw":
      {
        "env": ["SAFE_EXEC_DISABLE", "OPENCLAW_AGENT_CALL", "SAFE_EXEC_AUTO_CONFIRM"],
        "writes": ["~/.openclaw/safe-exec/", "~/.openclaw/safe-exec-audit.log"],
        "network": false,
        "monitoring": false,
        "credentials": []
      },
      "requires": { "bins": ["jq"] },
      "install":
        [
          {
            "id": "git",
            "kind": "git",
            "url": "https://github.com/OTTTTTO/safe-exec.git",
            "label": "Clone from GitHub",
          },
        ],
  }
---

# SafeExec - Safe Command Execution

Provides secure command execution capabilities for OpenClaw Agents with automatic interception of dangerous operations and approval workflow.

## Features

- 🔍 **Automatic danger pattern detection** - Identifies risky commands before execution
- 🚨 **Risk-based interception** - Multi-level assessment (CRITICAL/HIGH/MEDIUM/LOW)
- 💬 **In-session notifications** - Real-time alerts in your current terminal/session
- ✅ **User approval workflow** - Commands wait for explicit confirmation
- 📊 **Complete audit logging** - Full traceability of all operations
- 🤖 **Agent-friendly** - Non-interactive mode support for automated workflows
- 🔧 **Platform-agnostic** - Works independently of communication tools (webchat, Feishu, Telegram, etc.)
- 🔐 **Security-focused** - No monitoring, no external notifications, no network calls

## Agent Mode

When called by OpenClaw agents in non-interactive environments:

- **Automatic bypass of confirmation prompts** - Prevents agent hanging
- **Full audit logging** - All executions recorded with mode label (agent_auto vs user_approved)
- **Safety preserved** - Danger pattern detection and risk assessment remain active
- **Intended use case** - Automated workflows with human oversight via audit logs

**Environment variables:**
- `OPENCLAW_AGENT_CALL` - Set by OpenClaw when agent executes commands
- `SAFE_EXEC_AUTO_CONFIRM` - Manual override to auto-approve LOW/MEDIUM risk commands

**Security Note:** Agent mode does not disable safety checks. CRITICAL and HIGH risk commands are still intercepted, logged, and can be reviewed in audit trail.

## Quick Start

### Installation (One Command)

**The easiest way to install SafeExec:**

Just say in your OpenClaw chat:
```
Help me install SafeExec skill from ClawdHub
```

OpenClaw will automatically download, install, and configure SafeExec for you!

### Alternative: Manual Installation

If you prefer manual installation:

```bash
# Clone from GitHub
git clone https://github.com/OTTTTTO/safe-exec.git ~/.openclaw/skills/safe-exec

# Make scripts executable
chmod +x ~/.openclaw/skills/safe-exec/safe-exec*.sh

# Create symlinks to PATH (optional)
ln -s ~/.openclaw/skills/safe-exec/safe-exec.sh ~/.local/bin/safe-exec
ln -s ~/.openclaw/skills/safe-exec/safe-exec-*.sh ~/.local/bin/
```

### Enable SafeExec

After installation, simply say:
```
Enable SafeExec
```

SafeExec will start monitoring all shell commands automatically!

## How It Works

Once enabled, SafeExec automatically monitors all shell command executions. When a potentially dangerous command is detected, it intercepts the execution and requests your approval through **in-session terminal notifications**.

**Architecture:**
- Requests stored in: `~/.openclaw/safe-exec/pending/`
- Audit log: `~/.openclaw/safe-exec-audit.log`
- Rules config: `~/.openclaw/safe-exec-rules.json`
- No external network calls
- No background monitoring processes

## Usage

**Enable SafeExec:**
```
Enable SafeExec
```

```
Turn on SafeExec
```

```
Start SafeExec
```

Once enabled, SafeExec runs transparently in the background. Agents can execute commands normally, and SafeExec will automatically intercept dangerous operations:

```
Delete all files in /tmp/test
```

```
Format the USB drive
```

SafeExec detects the risk level and displays an in-session prompt for approval.

## Risk Levels

**CRITICAL**: System-destructive commands (rm -rf /, dd, mkfs, fork bombs)
**HIGH**: User data deletion or significant system changes (chmod 777, curl | bash)
**MEDIUM**: Service operations or configuration changes (sudo, firewall modifications)
**LOW**: Read operations and safe file manipulations

## Approval Workflow

1. Agent executes a command
2. SafeExec analyzes the risk level
3. **In-session notification displayed** in your terminal
4. Approve or reject via:
   - Terminal: `safe-exec-approve <request_id>`
   - List pending: `safe-exec-list`
   - Reject: `safe-exec-reject <request_id>`
5. Command executes or is cancelled

**Example notification:**
```
🚨 **Dangerous Operation Detected - Command Intercepted**

**Risk Level:** CRITICAL
**Command:** `rm -rf /tmp/test`
**Reason:** Recursive deletion with force flag

**Request ID:** `req_1769938492_9730`

ℹ️  This command requires user approval to execute.

**Approval Methods:**
1. In terminal: `safe-exec-approve req_1769938492_9730`
2. Or: `safe-exec-list` to view all pending requests

**Rejection Method:**
 `safe-exec-reject req_1769938492_9730`
```

## Configuration

Environment variables for customization:

- `SAFE_EXEC_DISABLE` - Set to '1' to globally disable safe-exec
- `OPENCLAW_AGENT_CALL` - Automatically enabled in agent mode (non-interactive)
- `SAFE_EXEC_AUTO_CONFIRM` - Auto-approve LOW/MEDIUM risk commands

## Examples

**Enable SafeExec:**
```
Enable SafeExec
```

**After enabling, agents work normally:**
```
Delete old log files from /var/log
```

SafeExec automatically detects this is HIGH risk (deletion) and displays an in-session approval prompt.

**Safe operations pass through without interruption:**
```
List files in /home/user/documents
```

This is LOW risk and executes without approval.

## Global Control

**Check status:**
```
safe-exec-list
```

**View audit log:**
```bash
cat ~/.openclaw/safe-exec-audit.log
```

**Disable SafeExec globally:**
```
Disable SafeExec
```

Or set environment variable:
```bash
export SAFE_EXEC_DISABLE=1
```

## Reporting Issues

**Found a bug? Have a feature request?**

Please report issues at:
🔗 **https://github.com/OTTTTTO/safe-exec/issues**

We welcome community feedback, bug reports, and feature suggestions!

When reporting issues, please include:
- SafeExec version (run: `grep "VERSION" ~/.openclaw/skills/safe-exec/safe-exec.sh`)
- OpenClaw version
- Steps to reproduce
- Expected vs actual behavior
- Relevant logs from `~/.openclaw/safe-exec-audit.log`

## Audit Log

All command executions are logged with:
- Timestamp
- Command executed
- Risk level
- Execution mode (user_approved / agent_auto)
- Approval status
- Execution result
- Request ID for traceability

Log location: `~/.openclaw/safe-exec-audit.log`

## Security & Privacy

**What SafeExec does:**
- ✅ Intercepts shell commands before execution
- ✅ Detects dangerous patterns using regex matching
- ✅ Requests user approval for risky commands
- ✅ Logs all executions to local audit file
- ✅ Works entirely locally on your machine

**What SafeExec does NOT do:**
- ❌ No monitoring of chat sessions or conversation history
- ❌ No reading of OpenClaw session data
- ❌ No external network requests (except git clone during installation)
- ❌ No sending data to external services
- ❌ No background monitoring processes or cron jobs
- ❌ No integration with external notification services (Feishu, webhooks, etc.)

## Integration

SafeExec integrates seamlessly with OpenClaw agents. Once enabled, it works transparently without requiring changes to agent behavior or command structure. The approval workflow is entirely local and independent of any external communication platform.

## Platform Independence

SafeExec operates at the **session level**, working with any communication channel your OpenClaw instance supports (webchat, Feishu, Telegram, Discord, etc.). The approval workflow happens through your terminal, ensuring you maintain control regardless of how you're interacting with your agent.

## Support & Community

- **GitHub Repository:** https://github.com/OTTTTTO/safe-exec
- **Issue Tracker:** https://github.com/OTTTTTO/safe-exec/issues
- **Documentation:** [README.md](https://github.com/OTTTTTO/safe-exec/blob/master/README.md)
- **ClawdHub:** https://www.clawhub.ai/skills/safe-exec

## License

MIT License - See [LICENSE](https://github.com/OTTTTTO/safe-exec/blob/master/LICENSE) for details.
