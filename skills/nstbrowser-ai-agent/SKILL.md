---
name: nstbrowser-ai-agent
description: Browser automation CLI with Nstbrowser integration for AI agents. Use when the user needs advanced browser fingerprinting, profile management, proxy configuration, batch operations on multiple browser profiles, or cursor-based pagination for large datasets. Triggers include requests to "use NST profile", "configure proxy for profile", "manage browser profiles", "batch update profiles", "start multiple browsers", "list profiles with pagination", or any task requiring Nstbrowser's anti-detection features.
allowed-tools: Bash(npx nstbrowser-ai-agent:*), Bash(nstbrowser-ai-agent:*)
---

# Browser Automation with nstbrowser-ai-agent

## Overview

This skill enables AI agents to control browsers using nstbrowser-ai-agent CLI with Nstbrowser integration. Nstbrowser provides advanced browser fingerprinting, profile management, and anti-detection capabilities for professional browser automation.

**This tool requires Nstbrowser service to function.** All browser operations are performed through Nstbrowser profiles, which provide:
- Advanced browser fingerprinting and anti-detection
- Profile management with persistent sessions
- Proxy configuration per profile
- Batch operations on multiple profiles
- Tag and group organization for profile management

## Prerequisites

Before using this tool, ensure you have the following:

### 1. Nstbrowser Client Installation

Nstbrowser client must be installed and running on your system.

- Download from: https://www.nstbrowser.io/
- Install the client application
- Launch the Nstbrowser client

### 2. Nstbrowser Service Running

The Nstbrowser API service must be accessible:

- Default endpoint: `http://127.0.0.1:8848`
- Verify service is running using the CLI:
  ```bash
  nstbrowser-ai-agent profile list
  ```
- Expected response: List of profiles or empty list

### 3. API Key Configuration

Obtain your API key from the Nstbrowser dashboard and configure it:

**Method 1: Config File (Recommended)**
```bash
nstbrowser-ai-agent config set key YOUR_API_KEY
```

**Method 2: Environment Variable**

Set the NST_API_KEY environment variable in your shell configuration file.

### 4. CLI Tool Installation

Install the nstbrowser-ai-agent CLI:

```bash
# Using npx (no installation required)
npx nstbrowser-ai-agent --help

# Or install globally
npm install -g nstbrowser-ai-agent
```

### 5. Verify Installation

Test your setup:

```bash
# Check CLI version
nstbrowser-ai-agent --version

# List profiles (verifies API connection)
nstbrowser-ai-agent profile list
```

If you see your profiles or an empty list, your environment is configured correctly.

## Quick Start

Get started in 5 minutes with these examples:

### Option 1: Using Temporary Browser (Fastest)

For quick tests or one-time tasks:

```bash
# 1. Start temporary browser
nstbrowser-ai-agent browser start-once

# 2. Open a website
nstbrowser-ai-agent open https://example.com

# 3. Take a snapshot
nstbrowser-ai-agent snapshot -i

# 4. Close browser (auto-cleanup)
nstbrowser-ai-agent close
```

**Note:** Temporary browsers don't save session state and are cleaned up after use.


### Option 2: Using Profile (Recommended for Persistent Sessions)

For tasks that require saved sessions, cookies, or login state:

```bash
# 1. List available profiles
nstbrowser-ai-agent profile list

# 2. Create a new profile (if needed)
nstbrowser-ai-agent profile create my-profile

# 3. Open browser with profile (auto-starts if not running)
nstbrowser-ai-agent open https://example.com

# 4. Interact with page
nstbrowser-ai-agent snapshot -i
nstbrowser-ai-agent click @e1

# 5. Close browser (session saved to profile)
nstbrowser-ai-agent close
```

**Expected Output:**
- Profile list shows your profiles with IDs and names
- Browser opens in headless mode
- Snapshot shows page structure with element refs (@e1, @e2, etc.)
- Session state persists across browser restarts

## Core Concepts

### Profiles

**Profiles are the foundation of Nstbrowser automation.** Each profile is an isolated browser environment that stores:

- **Browser Fingerprints**: Canvas, WebGL, fonts, screen resolution, timezone
- **Session Data**: Cookies, localStorage, sessionStorage
- **Login State**: Persistent authentication across sessions
- **Proxy Settings**: Per-profile proxy configuration
- **Browser Configuration**: User agent, platform, language settings

**Why use profiles?**
- Maintain separate identities for different tasks
- Preserve login sessions between automation runs
- Isolate cookies and data between different websites
- Configure different proxies for different regions

### Profile Name vs ID

All profile commands support both profile NAME and profile ID:

**Profile Name:**
- User-friendly, easier to remember
- Example: `my-profile`, `test-account`, `production-bot`
- Use when: Working interactively or in scripts with descriptive names

**Profile ID:**
- UUID format, guaranteed uniqueness
- Example: `86581051-fb0d-4c4a-b1e3-ebc1abd17174`
- Use when: Scripting with multiple profiles or ensuring exact profile match

**UUID Format Auto-Detection:**
- The system automatically detects UUID format in profile names
- If you provide a UUID-formatted string to `--profile`, it's treated as a profile ID
- This prevents accidental profile creation when you meant to use an ID
- Example: `--profile "86581051-fb0d-4c4a-b1e3-ebc1abd17174"` is treated as profile ID

**Resolution Priority:**
1. `--profile` flag (profile name or UUID auto-detected as ID)
2. Use once browser if no profile specified

**Profile Resolution Logic:**
When you specify a profile for a browser action:
1. **Check running browsers** - Uses existing browser if already running (earliest if multiple)
2. **Start browser** - Starts the profile if it exists but isn't running
3. **Create profile** - If profile NAME doesn't exist, creates it automatically
4. **Error** - If profile ID doesn't exist, returns an error
5. **Once browser** - If no profile specified, uses or creates temporary browser

**Important:** If multiple profiles have the same name, the earliest started browser will be used.

### Sticky Sessions

Once you start a session with a profile, that session "locks" to that browser instance. Subsequent commands automatically reuse the same browser without repeating the `--profile` flag.

```bash
# First command: link session to profile
nstbrowser-ai-agent --profile my-profile open https://example.com

# Subsequent commands: Stays in 'my-profile' automatically
nstbrowser-ai-agent snapshot -i
nstbrowser-ai-agent click @e1
nstbrowser-ai-agent fill @e2 "data"
```

This makes automation scripts cleaner and reduces the need to specify the profile repeatedly.

### Refs

Elements are identified by refs (e.g., @e1, @e2) from snapshots, making automation more reliable than CSS selectors.

```bash
# Get snapshot with refs
nstbrowser-ai-agent snapshot -i

# Output shows elements with refs:
# @e1 button "Submit"
# @e2 textbox "Email"
# @e3 textbox "Password"

# Use refs to interact
nstbrowser-ai-agent fill @e2 "user@example.com"
nstbrowser-ai-agent fill @e3 "password"
nstbrowser-ai-agent click @e1
```

**Note:** For modern web frameworks (React, Vue, Angular), CSS selectors may be more reliable than refs.

## Configuration

### Config File (Recommended)

Store configuration persistently in `~/.nst-ai-agent/config.json`:

```bash
# Set API key (required)
nstbrowser-ai-agent config set key YOUR_API_KEY

# Optional: Set custom host
nstbrowser-ai-agent config set host api.example.com

# Optional: Set custom port
nstbrowser-ai-agent config set port 9000

# View all configuration
nstbrowser-ai-agent config show

# Get specific value
nstbrowser-ai-agent config get key
```

Configuration persists across sessions and takes priority over environment variables.

### Environment Variables

Alternative to config file:

```bash
# Nstbrowser API credentials (required if not using config)
# Set NST_API_KEY in your environment

# Optional: Nstbrowser API endpoint
# Set NST_HOST and NST_PORT if using custom endpoint

# Optional: Specify profile for each command
# nstbrowser-ai-agent open https://example.com --profile "my-profile"
```

**Priority:** Config file > Environment variables > Defaults

## Common Commands

### Profile Management

**List Profiles**
```bash
# List all profiles
nstbrowser-ai-agent profile list

# List with JSON output
nstbrowser-ai-agent profile list --json

# List with pagination (for large datasets)
nstbrowser-ai-agent profile list-cursor --page-size 50
```

**Show Profile Details**
```bash
# Show by name or ID
nstbrowser-ai-agent profile show my-profile --json
nstbrowser-ai-agent profile show 86581051-fb0d-4c4a-b1e3-ebc1abd17174 --json
```

**Create Profile**
```bash
nstbrowser-ai-agent profile create my-profile \
  --proxy-host proxy.example.com \
  --proxy-port 8080 \
  --proxy-type http \
  --platform Windows
```

**Delete Profile**
```bash
# Delete single profile
nstbrowser-ai-agent profile delete <profile-name-or-id>

# Delete multiple profiles
nstbrowser-ai-agent profile delete id-1 id-2 id-3
```

### Browser Control

**Start Browser**
```bash
# Start with profile name
nstbrowser-ai-agent browser start my-profile

# Start with profile ID
nstbrowser-ai-agent browser start 86581051-fb0d-4c4a-b1e3-ebc1abd17174

# Start temporary browser
nstbrowser-ai-agent browser start-once

# Start temporary browser
nstbrowser-ai-agent browser start-once
```

**Stop Browser**
```bash
# Stop specific browser
nstbrowser-ai-agent browser stop my-profile

# Stop all browsers
nstbrowser-ai-agent browser stop-all
```

**List Running Browsers**
```bash
nstbrowser-ai-agent browser list
```

### Page Navigation

**Open URL**
```bash
# Auto-launches browser if not running
nstbrowser-ai-agent open https://example.com
```

**Navigate**
```bash
nstbrowser-ai-agent back
nstbrowser-ai-agent forward
nstbrowser-ai-agent reload
```

### Page Inspection

**Get Snapshot**
```bash
# Accessibility snapshot with refs (best for AI)
nstbrowser-ai-agent snapshot -i

# Compact snapshot
nstbrowser-ai-agent snapshot -c

# Custom depth
nstbrowser-ai-agent snapshot -d 3
```

**Get Page Info**
```bash
nstbrowser-ai-agent get title
nstbrowser-ai-agent get url
```

**Take Screenshot**
```bash
nstbrowser-ai-agent screenshot output.png

# Annotated screenshot with element labels
nstbrowser-ai-agent screenshot --annotate output.png
```

### Element Interaction

**Click**
```bash
# Click by ref
nstbrowser-ai-agent click @e1

# Click by CSS selector
nstbrowser-ai-agent click 'button[type="submit"]'
```

**Fill Input**
```bash
# Fill by ref
nstbrowser-ai-agent fill @e2 "text"

# Fill by CSS selector
nstbrowser-ai-agent fill 'input[name="email"]' "user@example.com"
```

**Type Text**
```bash
nstbrowser-ai-agent type @e3 "text"
```

**Get Element Text**
```bash
nstbrowser-ai-agent get text @e4
nstbrowser-ai-agent get text '.product-price'
```

### Wait Commands

**Wait for Element**
```bash
nstbrowser-ai-agent wait 'button.submit'
```

**Wait for Time**
```bash
# Wait 3 seconds
nstbrowser-ai-agent wait 3000
```

**Wait for Page Load**
```bash
nstbrowser-ai-agent wait --load networkidle
```

### JavaScript Execution

**Execute JavaScript**
```bash
nstbrowser-ai-agent eval "document.title"
nstbrowser-ai-agent eval "document.querySelectorAll('a').length"

# Execute from stdin
echo "document.body.innerHTML" | nstbrowser-ai-agent eval --stdin
```

### Proxy Management

**Show Proxy**
```bash
nstbrowser-ai-agent profile proxy show my-profile --json
```

**Update Proxy**
```bash
nstbrowser-ai-agent profile proxy update my-profile \
  --host proxy.example.com \
  --port 8080 \
  --type http \
  --username proxyuser \
  --password proxypass
```

**Reset Proxy**
```bash
nstbrowser-ai-agent profile proxy reset <profile-name-or-id>
```

**Batch Proxy Operations**
```bash
# Batch update
nstbrowser-ai-agent profile proxy batch-update id-1 id-2 id-3 \
  --host proxy.example.com \
  --port 8080 \
  --type http

# Batch reset
nstbrowser-ai-agent profile proxy batch-reset id-1 id-2 id-3
```

## Workflow Examples

### Pattern 1: Profile-based Automation

**Use Case:** Automate tasks that require persistent login sessions or cookies.

```bash
# 1. List profiles to verify connection
nstbrowser-ai-agent profile list

# 2. Set profile by name
nstbrowser-ai-agent config set profile my-profile

# 3. List profiles to find target
nstbrowser-ai-agent profile list

# 4. Open browser with profile (auto-starts if not running)
nstbrowser-ai-agent open https://example.com --profile "my-profile"
nstbrowser-ai-agent open https://example.com

# 6. Get snapshot
nstbrowser-ai-agent snapshot -i

# 7. Interact with page
nstbrowser-ai-agent click @e1
nstbrowser-ai-agent fill @e2 "data"

# 8. Close (session saved to profile)
nstbrowser-ai-agent close
```

### Pattern 2: Batch Profile Management

**Use Case:** Manage multiple profiles efficiently (update proxies, add tags, organize).

```bash
# Get multiple profile IDs
PROFILE_IDS=$(nstbrowser-ai-agent profile list --json | jq -r '.data.profiles[0:3] | map(.profileId) | join(" ")')

# Batch update proxy
nstbrowser-ai-agent profile proxy batch-update $PROFILE_IDS \
  --host proxy.example.com \
  --port 8080 \
  --type http

# Batch add tags
nstbrowser-ai-agent profile tags batch-create $PROFILE_IDS \
  automated:blue batch-updated:green

# Batch move to group
GROUP_ID=$(nstbrowser-ai-agent profile groups list --json | jq -r '.data.groups[0].groupId')
nstbrowser-ai-agent profile groups batch-change $GROUP_ID $PROFILE_IDS
```

### Pattern 3: Login and Scrape

**Use Case:** Log in to a website, navigate to data pages, and extract information.

```bash
# 1. Open login page
nstbrowser-ai-agent --profile my-profile open https://site.com/login

# 2. Wait for page to load
nstbrowser-ai-agent wait --load networkidle

# 3. Fill and submit using CSS selectors
nstbrowser-ai-agent fill 'input[placeholder="Email"]' "user@example.com"
nstbrowser-ai-agent fill 'input[type="password"]' "userpassword"
nstbrowser-ai-agent click 'button[type="submit"]'

# 4. Wait for navigation
nstbrowser-ai-agent wait --load networkidle

# 5. Navigate to target page
nstbrowser-ai-agent open https://site.com/data

# 6. Extract data
nstbrowser-ai-agent snapshot -i > data.txt
nstbrowser-ai-agent eval "document.querySelector('.info')?.textContent"

# 7. Close (session saved to profile)
nstbrowser-ai-agent close
```

## Error Handling

### Common Errors (by frequency)

#### 1. "NST_API_KEY is required"

**Cause:** API key not configured.

**Solution:**
```bash
# Method 1: Config file (recommended)
nstbrowser-ai-agent config set key YOUR_API_KEY

# Method 2: Set environment variable in your shell
```

**Verify:**
```bash
nstbrowser-ai-agent config get key
```

#### 2. "Failed to connect to Nstbrowser"

**Cause:** Nstbrowser service not running or wrong endpoint.

**Solution:**
1. Check if NST agent is running:
   ```bash
   nstbrowser-ai-agent nst status
   ```
2. Ensure Nstbrowser client is running
3. If using custom host/port, configure:
   ```bash
   nstbrowser-ai-agent config set host YOUR_HOST
   nstbrowser-ai-agent config set port YOUR_PORT
   ```

**Verify:**
```bash
# Should show "NST agent is running and responsive"
nstbrowser-ai-agent nst status

# Should return list of profiles
nstbrowser-ai-agent profile list
```

#### 3. "Profile not found"

**Cause:** Specified profile doesn't exist.

**Solution:**
1. List available profiles:
   ```bash
   nstbrowser-ai-agent profile list
   ```
2. Create a new profile:
   ```bash
   nstbrowser-ai-agent profile create my-profile
   ```
3. Or use temporary browser:
   ```bash
   nstbrowser-ai-agent browser start-once
   ```

**Verify:**
```bash
# Should show your profile
nstbrowser-ai-agent profile show my-profile
```

#### 4. "Element not found" or "Action timed out"

**Cause:** Element ref is stale or page structure changed.

**Solution:**
1. Get fresh snapshot:
   ```bash
   nstbrowser-ai-agent snapshot -i
   ```
2. Use CSS selectors instead of refs:
   ```bash
   # Instead of: nstbrowser-ai-agent click @e1
   # Use: nstbrowser-ai-agent click 'button[type="submit"]'
   ```
3. Inspect page elements:
   ```bash
   nstbrowser-ai-agent eval "Array.from(document.querySelectorAll('input')).map(el => ({type: el.type, placeholder: el.placeholder}))"
   ```

**Verify:**
```bash
# Element should be visible
nstbrowser-ai-agent is visible 'button[type="submit"]'
```

### Ref System Limitations

The ref system (`@e1`, `@e2`, etc.) may not work reliably with modern web frameworks (Vue.js, React, Angular) due to dynamic DOM updates.

**Workaround - Use CSS Selectors:**

```bash
# 1. Inspect page elements
nstbrowser-ai-agent eval "Array.from(document.querySelectorAll('input')).map(el => ({type: el.type, placeholder: el.placeholder}))"

# 2. Use CSS selectors directly
nstbrowser-ai-agent fill 'input[placeholder="Email"]' "user@example.com"
nstbrowser-ai-agent fill 'input[type="password"]' "password"
nstbrowser-ai-agent click 'button[type="submit"]'
```

## Command Reference

### Profile Commands
- `profile list` - List all profiles
- `profile list-cursor` - List profiles with cursor pagination
- `profile show <name-or-id>` - Show profile details
- `profile create <name>` - Create new profile
- `profile delete <name-or-id> [name-or-id...]` - Delete profile(s)
- `profile groups list` - List all groups
- `profile groups change <group-id> <profile-name-or-id> [...]` - Move profile(s) to group
- `profile groups batch-change <group-id> <id> [...]` - Batch change group
- `profile cache clear <id> [id...]` - Clear profile cache
- `profile cookies clear <id> [id...]` - Clear profile cookies

### Proxy Commands
- `profile proxy show <name-or-id>` - Show proxy configuration
- `profile proxy update <name-or-id>` - Update proxy settings
- `profile proxy reset <id> [id...]` - Reset proxy settings
- `profile proxy batch-update <id> [id...]` - Batch update proxy
- `profile proxy batch-reset <id> [id...]` - Batch reset proxy

### Tag Commands
- `profile tags list` - List all tags
- `profile tags create <id> <tag>` - Add tag to profile
- `profile tags update <id> <tag:color> [...]` - Update profile tags
- `profile tags clear <id> [id...]` - Clear profile tags
- `profile tags batch-create <id> [id...] <tag:color>` - Batch create tags
- `profile tags batch-update <id> [id...] <tag:color>` - Batch update tags
- `profile tags batch-clear <id> [id...]` - Batch clear tags

### Browser Commands
- `browser list` - List running browsers
- `browser start <name-or-id>` - Start browser with profile
- `browser start-once` - Start temporary browser
- `browser stop <name-or-id>` - Stop browser
- `browser stop-all` - Stop all browsers
- `browser pages <name-or-id>` - Get browser pages list
- `browser debugger <name-or-id>` - Get debugger URL
- `browser cdp-url <name-or-id>` - Get CDP WebSocket URL
- `browser cdp-url-once` - Get CDP URL for temporary browser
- `browser connect <name-or-id>` - Connect and get CDP URL
- `browser connect-once` - Connect to temporary browser and get CDP URL

### Navigation Commands
- `open <url>` - Navigate to URL
- `back` - Go back
- `forward` - Go forward
- `reload` - Reload page

### Inspection Commands
- `snapshot [-i] [-c] [-d <depth>]` - Get page snapshot
- `get title` - Get page title
- `get url` - Get current URL
- `get text <sel>` - Get element text
- `screenshot [path]` - Take screenshot
- `is visible <sel>` - Check if element is visible

### Interaction Commands
- `click <sel>` - Click element
- `fill <sel> <text>` - Fill input
- `type <sel> <text>` - Type into element
- `press <key>` - Press key
- `wait <sel|ms>` - Wait for element or time

### Utility Commands
- `eval <js>` - Execute JavaScript
- `close` - Close browser
- `session list` - List active sessions
- `update check` - Check for available updates
- `nst status` - Check if NST agent is running
- `config set <key> <value>` - Set configuration
- `config get <key>` - Get configuration value
- `config show` - Show all configuration

## JSON Output

All commands support `--json` flag for machine-readable output:

```bash
nstbrowser-ai-agent profile list --json
nstbrowser-ai-agent snapshot -i --json
nstbrowser-ai-agent get text @e1 --json
```

## Best Practices

1. **Use Profile Names**: More readable than IDs for most use cases
2. **Leverage Sticky Sessions**: No need to repeat `--profile` flag once browser is running
3. **Use Batch Operations**: More efficient for multiple profiles
5. **Organize with Groups and Tags**: Keep profiles organized
6. **Prefer CSS Selectors for Modern Apps**: Refs may not work with Vue/React/Angular
7. **Wait Appropriately**: Use `wait --load networkidle` after navigation
8. **Close Cleanly**: Always close browser to save session state
9. **Handle Errors**: Check command output and retry if needed
10. **Use Proxies Per Profile**: Configure proxies for geo-targeting or privacy
11. **Keep Updated**: Run `nstbrowser-ai-agent update check` periodically

## Updates

### Automatic Update Checks

The CLI automatically checks for updates once every 24 hours and notifies you when a new version is available.

**Disable automatic checks:**
```bash
# Set environment variable
NSTBROWSER_AI_AGENT_NO_UPDATE_CHECK=1
```

### Manual Update Check

```bash
# Check for updates
nstbrowser-ai-agent update check

# JSON output
nstbrowser-ai-agent update check --json
```

### Updating to Latest Version

```bash
# If installed globally
npm install -g nstbrowser-ai-agent@latest

# If using npx
npx nstbrowser-ai-agent@latest

# If installed locally in project
npm install nstbrowser-ai-agent@latest
```

## Deep-Dive Documentation

For more detailed information, see:

| Reference | When to Use |
|-----------|-------------|
| [references/nst-api-reference.md](references/nst-api-reference.md) | Complete NST API reference with all commands |
| [references/profile-management.md](references/profile-management.md) | Profile creation, organization, and lifecycle |
| [references/proxy-configuration.md](references/proxy-configuration.md) | Proxy setup, testing, and troubleshooting |
| [references/batch-operations.md](references/batch-operations.md) | Efficient batch operations on multiple profiles |
| [references/troubleshooting.md](references/troubleshooting.md) | Common issues and diagnostic commands |

## Ready-to-Use Templates

| Template | Description |
|----------|-------------|
| [templates/profile-setup.sh](templates/profile-setup.sh) | Profile initialization with proxy and tags |
| [templates/batch-proxy-update.sh](templates/batch-proxy-update.sh) | Batch proxy update for multiple profiles |
| [templates/automated-workflow.sh](templates/automated-workflow.sh) | Complete automation workflow example |

```bash
./templates/profile-setup.sh my-profile --proxy-host proxy.com --proxy-port 8080
./templates/batch-proxy-update.sh "id1 id2 id3" --proxy-host proxy.com --proxy-port 8080
./templates/automated-workflow.sh my-profile https://example.com
```

## Notes

- **Nstbrowser is required**: This tool only works with Nstbrowser service
- **Profile name/ID support**: All commands accept both names and IDs
- **Auto-start**: Browser automatically starts when using profile if not running
- **Name resolution**: Profile names are resolved to IDs automatically via API
- **Sticky sessions**: Profile persists across commands in the same session
- **Profiles managed by Nstbrowser**: Profiles are created and stored by Nstbrowser client
- **Daemon auto-starts**: Daemon starts on first command and persists between commands
- **Session persistence**: Session state is automatically saved to profiles when browser closes
- **Temporary browsers**: Use `browser start-once` for disposable sessions that don't save state

## CDP Integration

Get Chrome DevTools Protocol (CDP) WebSocket URLs to connect external tools:

```bash
# Get CDP URL for existing browser
nstbrowser-ai-agent browser cdp-url my-profile

# Get CDP URL for temporary browser
nstbrowser-ai-agent browser cdp-url-once

# Connect to browser and get CDP URL (starts if not running)
nstbrowser-ai-agent browser connect my-profile

# Connect to temporary browser and get CDP URL
nstbrowser-ai-agent browser connect-once
```

**Use cases:**
- Connect Puppeteer/Playwright to Nstbrowser-managed browsers
- Attach Chrome DevTools for debugging
- Integrate with custom CDP-based automation tools
- Monitor browser activity with external tools
