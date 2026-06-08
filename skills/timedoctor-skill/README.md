# TimeDoctor OpenClaw Skill

A simple OpenClaw skill that provides Python scripts to interact with TimeDoctor API for time tracking, productivity monitoring, and workforce analytics.

## What is This?

This is a **simple skill** with Python scripts that you can execute directly. No MCP server, no complex setup - just:

1. **Python scripts** - Simple CLI tools that call TimeDoctor API
2. **SKILL.md** - Instructions for the agent on how to use the scripts
3. **JSON output** - Scripts return data as JSON for easy parsing

## How It Works

```
User Request → OpenClaw Agent → Executes Python Script → Gets JSON → Formats Response
```

Simple and straightforward!

## Author

**JehadurRE** (Jehadur Rahman Emran)
- Student, Developer, and Learner
- GitHub: [JehadurRE](https://github.com/JehadurRE)
- Created simple Python CLI tool for TimeDoctor API integration

## Overview

This skill wraps the TimeDoctor API (https://timedoctor.redoc.ly/) to provide comprehensive time tracking and workforce analytics capabilities through OpenClaw agents.

## Features

- **Authentication & Authorization**: Get user/company info and permissions
- **User Management**: List users, get user details, managed users
- **Activity & Worklog**: Detailed work activity logs, time usage stats, disconnectivity periods
- **Statistics**: Total stats, category stats, summary stats, work-life balance, shift stats, outliers
- **Timesheet Stats**: Timesheet totals and summaries
- **Projects & Tasks**: List and view projects and tasks
- **Groups (Tags)**: Manage user groups/teams
- **Work Schedules**: View schedules, issues, and leave stats
- **Payroll**: User and company payroll information
- **Files**: Access screenshots and screencasts
- **Categories**: Productivity ratings for apps/websites
- **Convenience Tools**: Today's worklog, this week's stats, this month's stats

## Prerequisites

1. A TimeDoctor account (Premium Plan required for API access)
2. Python 3.10+
3. A JWT authentication token from TimeDoctor

## Getting Your TimeDoctor Token

1. Use the TimeDoctor Login API endpoint to get a JWT token:
   ```bash
   curl -X POST https://api2.timedoctor.com/api/1.0/login \
     -H "Content-Type: application/json" \
     -d '{"email": "your@email.com", "password": "your-password"}'
   ```

2. The response will contain a `token` field - save this value

3. Tokens are valid for 6 months

## Installation

### Step 1: Get Your TimeDoctor Token

```bash
curl -X POST https://api2.timedoctor.com/api/1.0/login \
  -H "Content-Type: application/json" \
  -d '{"email": "your@email.com", "password": "your-password"}'
```

Save the `token` from the response (valid for 6 months).

### Step 2: Install the Skill

```bash
# Clone this repository
git clone https://github.com/JehadurRE/timedoctor-openclaw-skill
cd timedoctor-openclaw-skill

# Copy to OpenClaw skills directory
cp -r timedoctor-skill ~/.openclaw/workspace/skills/timedoctor

# Install Python dependencies
cd ~/.openclaw/workspace/skills/timedoctor
pip3 install -r requirements.txt
```

### Step 3: Set Environment Variables

```bash
export TIMEDOCTOR_TOKEN="your-jwt-token-here"
export TIMEDOCTOR_COMPANY_ID="your-company-id"  # Optional
```

Or add to your shell profile (~/.bashrc, ~/.zshrc):
```bash
echo 'export TIMEDOCTOR_TOKEN="your-token"' >> ~/.bashrc
echo 'export TIMEDOCTOR_COMPANY_ID="your-company-id"' >> ~/.bashrc
```

### Step 4: Restart OpenClaw

Restart your OpenClaw agent to load the skill.

## Configuration

Set the required environment variables:

```bash
export TIMEDOCTOR_TOKEN="your-jwt-token-here"
export TIMEDOCTOR_COMPANY_ID="your-company-id"
```

The `TIMEDOCTOR_COMPANY_ID` is optional but recommended. You can discover it by calling `get_authorization()`.

## Usage

Once installed, ask your OpenClaw agent questions like:

- "Get authorization info to find my company ID"
- "List all users in company 12345"
- "Get today's worklog for company 12345"
- "Show me this week's stats for company 12345"
- "Get activity from March 1 to March 31 for company 12345"

The agent will execute the Python scripts and format the results for you.

## Date Format

All dates should be in ISO 8601 format: `YYYY-MM-DDTHH:MM:SSZ`

Examples:
- `2024-01-15T00:00:00Z` - Start of January 15, 2024
- `2024-01-16T00:00:00Z` - Start of January 16, 2024

For a single day report, use:
- `from_date`: `2024-01-15T00:00:00Z`
- `to_date`: `2024-01-16T00:00:00Z`

## Troubleshooting

### Skill Not Loading
- Check that files are in `~/.openclaw/workspace/skills/timedoctor/`
- Restart OpenClaw or ask it to refresh skills
- Verify YAML frontmatter in SKILL.md is valid

### "TIMEDOCTOR_TOKEN environment variable not set"
- Set the environment variable: `export TIMEDOCTOR_TOKEN="your-token"`
- Add to shell profile for persistence (~/.bashrc or ~/.zshrc)

### "httpx module not found"
- Install dependencies: `cd ~/.openclaw/workspace/skills/timedoctor && pip3 install -r requirements.txt`

### "401 Unauthorized"
- Token may have expired (6-month validity)
- Get a new token using the login API

### "company_id required"
- Run `get_authorization` command first to discover your company_id
- Or set `TIMEDOCTOR_COMPANY_ID` environment variable

### "No data returned"
- Confirm the company_id is correct
- Verify users have activity in the requested date range
- Check that your account has permissions to access the requested data

## API Reference

For complete API documentation, visit: https://timedoctor.redoc.ly/

## License

MIT

## Credits

**Author**: JehadurRE (Jehadur Rahman Emran)
- Student, Developer, and Learner
- GitHub: https://github.com/JehadurRE
- Created simple Python CLI tool for TimeDoctor API integration
