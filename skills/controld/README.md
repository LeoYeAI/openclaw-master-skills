# Control D Skill for OpenClaw

An OpenClaw skill for managing Control D DNS filtering service via API.

## Features

- Full API coverage: profiles, devices, filters, services, rules
- Organization and billing management
- Mobile config generation
- Analytics and statistics

## Installation

Clone this repo to your OpenClaw skills folder:

```bash
cd ~/.openclaw/workspace/skills
git clone https://github.com/AustinGarrod/openclaw-skill-controld.git controld
```

Or copy the files manually to `~/.openclaw/workspace/skills/controld/`

## Configuration

Set your Control D API token:

```bash
export CONTROLD_API_TOKEN="your-api-token"
```

Get your token from: https://controld.com/dashboard (Account Settings > API)

## Usage

Once installed, the skill triggers when you mention Control D, DNS filtering, DNS blocking, or device DNS setup.

Examples:
- "Show my Control D profiles"
- "Add a custom DNS rule to block example.com"
- "List devices on my Control D account"

## License

MIT
