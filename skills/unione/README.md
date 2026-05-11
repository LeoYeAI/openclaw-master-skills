# UniOne Email API — OpenClaw Skill

📧 Send transactional and marketing emails via [UniOne](https://unione.io) directly from your AI assistant.

## What this skill does

This skill teaches your AI agent to work with the UniOne Email API. It can:

- **Send emails** — transactional, marketing, personalized with templates
- **Validate email addresses** — check deliverability before sending
- **Manage templates** — create, update, list, delete email templates
- **Track delivery** — set up webhooks for real-time event notifications
- **Manage suppressions** — handle bounces, unsubscribes, complaints
- **Domain management** — check DNS records, verify DKIM
- **Export analytics** — create event dumps for detailed delivery reports
- **Manage projects** — separate environments with independent API keys

## Quick Start

### 1. Get your UniOne API key

Sign up at [cp.unione.io](https://cp.unione.io/en/user/registration/) and get your API key from [account settings](https://cp.unione.io/en/user/info/api).

### 2. Install the skill

**From ClawHub:**
```bash
clawhub install @unione/unione
```

**Manual install:**
```bash
mkdir -p ~/.openclaw/skills/unione
cp SKILL.md ~/.openclaw/skills/unione/
```

### 3. Configure

Add to your `~/.openclaw/openclaw.json`:

```json
{
  "skills": {
    "entries": {
      "unione": {
        "enabled": true,
        "apiKey": "YOUR_UNIONE_API_KEY"
      }
    }
  }
}
```

Or set the environment variable:
```bash
export UNIONE_API_KEY="your-api-key-here"
```

### 4. Use it

Just talk to your AI assistant:

- *"Send a test email to john@example.com"*
- *"Validate this email address: user@domain.com"*
- *"List my email templates"*
- *"Show my domain verification status"*
- *"Set up a webhook for delivery tracking"*
- *"Create an order confirmation template"*

## Requirements

- A [UniOne account](https://cp.unione.io/en/user/registration/) (free plan: 100 emails/day)
- A verified sending domain in UniOne
- `curl` available on your system

## API Endpoint

`https://api.unione.io/en/transactional/api/v1/`

## Compatibility

This skill follows the [AgentSkills](https://docs.openclaw.ai/tools/skills) specification and works with:

- ✅ OpenClaw
- ✅ Claude Code
- ✅ Cursor
- ✅ VS Code (with AgentSkills extensions)
- ✅ Gemini CLI
- ✅ GitHub Copilot

## Security

- This is an **official skill** from UniOne
- No executable scripts — only API documentation in Markdown
- Requires only your API key — no other system access needed
- The agent always asks for confirmation before sending emails

## Links

- [UniOne Website](https://unione.io/en/)
- [API Documentation](https://docs.unione.io/en/web-api-ref)
- [Getting Started Guide](https://docs.unione.io/en/)
- [Support](https://unione.io/en/contacts)

## License

MIT
