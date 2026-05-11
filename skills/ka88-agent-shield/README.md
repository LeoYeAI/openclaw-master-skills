# ka88-agent-shield

Professional security audit skill for AI agents.

## Description

ka88-agent-shield is a skill for AI agents providing comprehensive protection against:
- Prompt Injection
- SSRF Attacks
- Credential Exfiltration
- Malicious JavaScript
- Phishing Patterns
- Obfuscation (hidden code)

## Features

### 🔍 4-Phase Audit System

1. **Pre-Visit Scan** — Check URL before visiting
2. **Content Analysis** — Analyze content for threats
3. **Command Safety** — Validate commands before execution
4. **Self-Audit** — Periodic self-monitoring

### 📊 216 Detection Patterns

Complete pattern set for threat detection, based on ClawGuard and OWASP Agentic AI Top 10.

### 🔧 Tools

| Script | Description | Requirements |
|--------|-------------|---------------|
| `quick-scan.sh` | Fast scan without LLM | bash/grep only |
| `scan-skill-scanner.sh` | Full scan with LLM | skill-scanner + LM Studio |

## Installation

### Via OpenSkills (recommended)

```bash
git clone <repo-url> ka88-agent-shield
cd ka88-agent-shield
openskills install ./ --global
openskills sync --yes
```

### Manual

```bash
git clone <repo-url> ka88-agent-shield
mkdir -p ~/.claude/skills
ln -s $(pwd)/ka88-agent-shield ~/.claude/skills/ka88-agent-shield
```

## Usage

### Activation

Skill activates automatically when agent:
- Visits websites
- Analyzes URL content
- Executes commands (curl, wget, pip, npm)
- Processes HTML/JS/CSS

### Quick Scan

```bash
./scripts/quick-scan.sh <path> [--dry-run] [--verbose] [--help]
```

### Full Scan

```bash
./scripts/scan-skill-scanner.sh <path> [--install] [--force] [--help]
```

## Project Structure

```
ka88-agent-shield/
├── SKILL.md
├── LICENSE
├── README.md
├── config/
├── scripts/
├── procedures/
└── templates/
```

## License

MIT

## Version

1.0.0

## Author

[Danilka88](https://github.com/Danilka88)