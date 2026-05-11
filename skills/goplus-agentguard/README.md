# GoPlus AgentGuard

AI Agent Security Guard — protect your AI agents from dangerous commands, data leaks, and malicious skills.

## Features

- **Code Scanning** — 24 detection rules covering shell injection, credential leaks, prompt injection, Web3 exploits, and more
- **Action Evaluation** — Real-time allow/deny/confirm decisions for runtime actions (network, exec, file, Web3)
- **Trust Registry** — Manage skill trust levels with capability-based access control
- **Security Patrol** — Automated daily security checks for OpenClaw environments
- **Audit Logging** — Full security event trail with reporting

## Usage

```
/agentguard scan <path>          — Scan code for security risks
/agentguard action <description> — Evaluate runtime action safety
/agentguard patrol [run|setup|status] — Daily security patrol
/agentguard trust <subcommand>   — Manage skill trust levels
/agentguard report               — View security event audit log
/agentguard config <level>       — Set protection level (strict/balanced/permissive)
```

## Requirements

- Node.js 18+
- Optional: GoPlus API credentials for enhanced Web3 transaction simulation

## Author

Built by [GoPlus Security](https://gopluslabs.io) — the leading Web3 security infrastructure provider.
