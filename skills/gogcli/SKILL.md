---
name: gogcli
description: Google Workspace CLI for Gmail, Calendar, Drive, Sheets, Docs, Slides, Contacts, Tasks, People, Groups, Keep. Use when user asks to interact with Google services.

# gogcli - Google Workspace CLI

## Overview

gogcli is a CLI tool for managing Google Workspace services from the terminal. Supports Gmail, Calendar, Drive, Sheets, Docs, Slides, Contacts, Tasks, People, Groups, and Keep.

## Installation

### Quick Install (if you have brew):
```bash
brew install steipete/tap/gogcli
```

### Build from Source (no brew):
```bash
# 1. Clone repository
git clone https://github.com/steipete/gogcli.git

# 2. Navigate to directory
cd gogcli

# 3. Build
make

# 4. (Optional) Make available globally
sudo make install
```

## First Time Setup

Before using gogcli, set up OAuth credentials:

**Step 1: Get OAuth Client Credentials**
1. Go to Google Cloud Console APIs & Services
2. Create project or use existing one
3. Go to OAuth consent screen
4. Create OAuth 2.0 client with these settings:
   - Application type: "Desktop app"
   - Name: "gogcli for Clawdbot"
   - Authorized redirect URIs: `http://localhost:8085/callback`
5. Enable APIs you need
6. Download OAuth client credentials JSON file
7. Copy to `~/Downloads/`

**Step 2: Authorize Your Account**
```bash
cd gogcli
./bin/gog auth add you@gmail.com ~/Downloads/client_secret_....json
```

**Step 3: Verify**
```bash
./bin/gog auth list
./bin/gog gmail search 'is:unread' --max 5
```

## Common Commands

### Gmail
```bash
# Search
./bin/gog gmail search 'query' --max 20

# Send
./bin/gog gmail send 'recipient@gmail.com' --subject 'Hello' --body 'Message'

# Labels
./bin/gog gmail labels list
```

### Calendar
```bash
# List events
./bin/gog calendar events list --max 50

# Create event
./bin/gog calendar events create 'Meeting' --start '2026-01-30T10:00'
```

### Drive
```bash
# List files
./bin/gog drive ls --query 'pdf' --max 20

# Upload file
./bin/gog drive upload ~/Documents/file.pdf
```

### Sheets
```bash
# List sheets
./bin/gog sheets list

# Export sheet
./bin/gog sheets export <spreadsheet-id> --format pdf
```

### Contacts
```bash
./bin/gog contacts search 'John Doe'
```

### Tasks
```bash
# List tasklists
./bin/gog tasks list

# Add task
./bin/gog tasks add --title 'Task' --due '2026-01-30'
```

## Notes

- Use `--json` flag for scripting
- Credentials stored in `~/.config/gog/`
- Use `gog auth list` to check authentication status
