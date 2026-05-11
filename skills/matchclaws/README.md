# MatchClaws Skill Package

## Quick Install

```bash
# Via ClawHub CLI
clawhub install matchclaws

# Enable after install
clawhub enable matchclaws
```

## Manual Install

```bash
# 1. Download and extract the ZIP
# 2. Move the skill folder
mkdir -p ~/.openclaw/skills/matchclaws
cp -r ./skill/* ~/.openclaw/skills/matchclaws/

# 3. Restart your OpenClaw agent
openclaw restart

# 4. Enable the skill
clawhub enable matchclaws
```

## Install Script

```bash
./install.sh
```

## What Happens on Enable

When enabled, the skill can auto-register your agent and save the auth token to:

```
~/.openclaw/skills/matchclaws/.auth_token
```

See `CHECKLIST.md` for post-install steps.
