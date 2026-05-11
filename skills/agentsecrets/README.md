# AgentSecrets — OpenClaw Integration

> Native zero-knowledge credential resolution for OpenClaw via the built-in exec provider

AgentSecrets ships as a native exec provider for OpenClaw's SecretRef system. Your agent resolves credentials at execution time without storing them anywhere OpenClaw can read — no plaintext config, no env block, no values in agent context.

## Setup

### From ClawHub
```bash
openclaw skill install agentsecrets
```

### Manual
```bash
cp -r integrations/openclaw ~/.openclaw/skills/agentsecrets
```

## Prerequisites

Install the AgentSecrets CLI:

```bash
brew install The-17/tap/agentsecrets
# or
npm install -g @the-17/agentsecrets
# or
pip install agentsecrets-cli
```

Then initialise and configure:

```bash
agentsecrets init
agentsecrets secrets set STRIPE_KEY=sk_live_...
agentsecrets workspace allowlist add api.stripe.com
```

## How the Exec Provider Works

AgentSecrets registers itself as an exec provider in OpenClaw's SecretRef system (shipped in v2026.2.26). When your agent references a secret, OpenClaw calls the AgentSecrets binary directly to resolve it. The value is injected into the process at execution time and never written to any OpenClaw config file.

```bash
# OpenClaw resolves this via the AgentSecrets exec provider
# The agent never sees the value — only the response
agentsecrets exec
```

This means you do not need to configure credentials in `~/.openclaw/.env` or any OpenClaw config. The SecretRef system handles the resolution, and AgentSecrets handles the zero-knowledge guarantee.

## What the Agent Can Do

Once installed, your OpenClaw agent can manage the full credentials workflow autonomously:

```bash
agentsecrets status                          # check workspace, project, and active environment
agentsecrets environment switch production   # switch to the correct environment
agentsecrets secrets diff                    # detect any drift between local and cloud
agentsecrets secrets pull                    # sync if needed
agentsecrets call \
  --url https://api.stripe.com/v1/balance \
  --bearer STRIPE_KEY                        # make the authenticated call
agentsecrets proxy logs                      # audit what happened
```

The agent passes key names. It never sees values. Every call is logged against the active environment.

## Environment Variable Injection

For processes that need credentials as environment variables:

```bash
agentsecrets env -- npm run dev
agentsecrets env -- python script.py
```

Values are injected into the child process at spawn time. Nothing is written to disk.

## Links

- [Official Website](https://agentsecrets.theseventeen.co)
- [Engineering Blog](https://engineering.theseventeen.co/series/building-agentsecrets)
- [GitHub](https://github.com/The-17/agentsecrets)
- [Security Docs](https://github.com/The-17/agentsecrets/blob/main/docs/PROXY.md)