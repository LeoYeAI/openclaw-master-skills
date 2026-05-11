# Health Management Skill - Permissions Declaration

## Overview

This document explains all permissions requested by the Health Management skill and why each is necessary for its functionality.

## Requested Permissions

### 🔧 Tools

| Tool | Purpose | Justification |
|------|---------|---------------|
| `exec` | Run backup scripts | Execute shell scripts for automated data backup to GitHub |
| `read` | Read user health data | Load historical health records and user profiles |
| `write` | Save health data | Store daily diet records, analysis reports, and user configurations |
| `web_search` | Nutritional research | Search for evidence-based information on food defense systems |
| `web_fetch` | Retrieve research papers | Fetch nutritional data from scientific sources |

### 📁 Filesystem Paths

| Path | Purpose |
|------|---------|
| `~/.openclaw/workspace/memory/health-users/` | Store user-specific health tracking data (diet records, profiles, reports) |
| `~/.openclaw/workspace/skills/health-management/` | Access skill scripts, templates, and reference materials |
| `~/Documents/health-backup/` | Local backup location before GitHub sync |

### 🌐 Network Access

| Domain | Purpose |
|--------|---------|
| `api.tavily.com` | Search API for nutritional information and health research |

### 📜 Executable Scripts

All scripts are human-readable and auditable. No obfuscated code.

| Script | Purpose | Trigger |
|--------|---------|---------|
| `scripts/backup_health_data.sh` | Backup user data to GitHub repository | Automatic (after database changes) or manual (user request) |
| `scripts/check_git_config.sh` | Verify Git configuration for backup | During initial setup |
| `scripts/configure_backup.sh` | Set up GitHub backup repository | First-time setup wizard |
| `scripts/manage_backup.sh` | Manage backup settings and scheduling | Configuration changes |
| `scripts/language_utils.sh` | Multi-language support utilities | When outputting content in user's language |
| `scripts/timezone_utils.sh` | Timezone conversion utilities | When processing dates/times |

### ⚙️ Capabilities

| Capability | Description |
|------------|-------------|
| `filesystem` | Read/write access to declared paths only |
| `network` | Outbound HTTP requests to declared domains only |

## External Actions

### 1. Backup Action

- **Name**: `backup`
- **Description**: Backup health data to GitHub repository
- **Trigger**: 
  - Automatic: After any database modification
  - Manual: User requests "备份数据" or "backup data"
- **Script**: `scripts/backup_health_data.sh`
- **What it does**:
  1. Creates timestamped backup of user data
  2. Commits to user's GitHub repository
  3. Provides backup status feedback
- **Data flow**: Local files → User's GitHub repo (user owns the repo)

### 2. Search Action

- **Name**: `search`
- **Description**: Search for nutritional information using Tavily API
- **Trigger**: When analyzing food defense systems or nutritional content
- **API**: Tavily Search API
- **What it does**:
  1. Searches for scientific research on food health benefits
  2. Extracts defense system information (angiogenesis, regeneration, etc.)
  3. Provides evidence-based recommendations
- **Data flow**: Query → Tavily API → Structured results → Analysis

## Security Guarantees

### ✅ Data Privacy

- All user health data stored in `memory/health-users/{username}/`
- Each user's data isolated in their own directory
- No cross-user data access
- Data never leaves user's machine except via user-controlled GitHub backup

### ✅ No Data Exfiltration

- Scripts only write to:
  - Local directories (declared paths)
  - User's own GitHub repository (user provides repo URL)
- No third-party servers
- No telemetry or analytics

### ✅ API Key Security

- Tavily API key stored in OpenClaw config (`~/.openclaw/openclaw.json`)
- NOT stored in skill directory
- Skill references key from environment, never hardcodes it

### ✅ Script Transparency

- All scripts are plain Bash, human-readable
- No obfuscated code
- No binary executables
- Users can audit scripts before running

### ✅ Least Privilege

- Only requests permissions actually used
- No unnecessary network access
- No access to sensitive system paths (`.ssh`, `.aws`, etc.)
- Filesystem access limited to declared directories

## User Control

Users can:

1. **Review scripts** before execution
2. **Decline backup** if they don't want GitHub sync
3. **Disable network search** by not configuring Tavily API key
4. **Inspect all data** stored in `memory/health-users/{username}/`
5. **Delete data** at any time by removing the directory

## Audit Trail

All actions are logged:

- Script executions: Logged in OpenClaw gateway logs
- Data modifications: Timestamped in user data files
- API calls: Logged with query and results summary

## Compliance

This skill follows:

- [OpenClaw Security Model](https://docs.openclaw.dev/security)
- [ClawHub Permission Manifest RFC #10890](https://github.com/openclaw/openclaw/issues/10890)
- Least privilege principle
- Transparency-first approach

## Questions?

If you have concerns about any permission:

1. Review the scripts in `scripts/` directory
2. Check your data in `memory/health-users/{username}/`
3. Inspect network traffic (all calls to `api.tavily.com` are visible)
4. Disable specific features by not configuring related settings

---

**Last Updated**: 2026-03-15
**Manifest Version**: 1.0.0
