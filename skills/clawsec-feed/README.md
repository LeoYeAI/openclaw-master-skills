# ClawSec Feed 📡

Security advisory feed monitoring for AI agents. Subscribe to community-driven threat intelligence and stay informed about emerging threats.

## Features

- **Real-time Advisories** - Get notified about malicious skills, vulnerabilities, and attack patterns
- **Cross-Reference Detection** - Automatically checks if your installed skills are affected
- **Community-Driven** - Advisories contributed and reviewed by the security community
- **Heartbeat Integration** - Seamlessly integrates with your agent's routine checks

## Quick Install

```bash
curl -sLO https://github.com/prompt-security/clawsec/releases/latest/download/clawsec-feed.skill
```

## Advisory Types

| Type | Description |
|------|-------------|
| `malicious_skill` | Skills identified as intentionally harmful |
| `vulnerable_skill` | Skills with security vulnerabilities |
| `prompt_injection` | Known prompt injection patterns |
| `attack_pattern` | Observed attack techniques |

## Feed Structure

```json
{
  "version": "1.0",
  "updated": "2026-02-02T12:00:00Z",
  "advisories": [
    {
      "id": "GA-2026-001",
      "severity": "critical",
      "type": "malicious_skill",
      "title": "Data exfiltration in 'helper-plus'",
      "affected": ["helper-plus@1.0.0"],
      "action": "Remove immediately"
    }
  ]
}
```

## Response Example

```
📡 ClawSec Feed: 2 new advisories

CRITICAL - GA-2026-015: Malicious prompt pattern
  → Update your system prompt defenses.

HIGH - GA-2026-016: Vulnerable skill "data-helper"
  → You have this installed! Update to v1.2.1
```

## Related Skills

- **openclaw-audit-watchdog** - Automated daily security audits
- **clawtributor** - Report vulnerabilities to the community

## License

GNU AGPL v3.0 or later - [Prompt Security](https://prompt.security)
