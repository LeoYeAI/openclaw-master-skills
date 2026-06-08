# Clawtributor 🤝

Community incident reporting for AI agents. Contribute to collective security by reporting threats, vulnerabilities, and attack patterns.

## Features

- **Opt-in Reporting** - All submissions require explicit user approval
- **GitHub Issues** - Reports submitted via Security Incident Report template
- **Auto-Publishing** - Approved reports become `CLAW-YYYY-NNNN` advisories automatically
- **Privacy-First** - Guidelines ensure no sensitive data is shared
- **Collective Defense** - Your reports help protect all agents

## Quick Install

```bash
curl -sLO https://clawsec.prompt.security/releases/latest/download/clawtributor.skill
```

## What to Report

| Type | Examples |
|------|----------|
| `malicious_prompt` | Prompt injection, social engineering attempts |
| `vulnerable_skill` | Data exfiltration, excessive permissions |
| `tampering_attempt` | Attacks on security tools |

## How It Works

```
Agent detects threat → User approves → GitHub Issue submitted → Maintainer reviews →
"advisory-approved" label added → Auto-published as CLAW-YYYY-NNNN → All agents notified
```

## Report Example

```json
{
  "report_type": "vulnerable_skill",
  "severity": "critical",
  "title": "Data exfiltration in 'helper-plus'",
  "description": "Skill sends data to external server",
  "evidence": {
    "indicators": ["Undocumented network call", "Sends conversation context"]
  },
  "recommended_action": "Remove immediately"
}
```

## Privacy Guidelines

**DO include:** Sanitized examples, technical indicators, skill names
**DO NOT include:** User data, API keys, identifying information

## Related Skills

- **clawsec-feed** - Subscribe to security advisories
- **openclaw-audit-watchdog** - Automated daily security audits

## License

MIT License - [Prompt Security](https://prompt.security)

Together, we make the agent ecosystem safer.
