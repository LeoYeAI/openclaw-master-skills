---
name: scrapeless-scraping-browser
description: Cloud browser automation CLI for AI agents powered by Scrapeless. Use when the user needs to interact with websites using cloud browsers, including navigating pages, filling forms, clicking buttons, taking screenshots, extracting data, testing web apps, or automating any browser task with residential proxies and anti-detection features. Triggers include requests to "open a website", "fill out a form", "click a button", "take a screenshot", "scrape data from a page", "test this web app", "use a proxy", "bypass detection", or any task requiring cloud browser automation.
allowed-tools: Bash(npx scrapeless-scraping-browser-skills scrapeless-scraping-browser:*), Bash(scrapeless-scraping-browser:*)
---

# Cloud Browser Automation with scrapeless-browser

## Important: Session Management with --session-id

**All browser operation commands support the `--session-id` parameter to specify which Scrapeless session to use.**

### Recommended Workflow

```bash
# Step 1: Create a session and save the session ID
SESSION_ID=$(scrapeless-scraping-browser new-session --name "workflow" --ttl 1800 --json | jq -r '.taskId')

# Step 2: Use the session ID for all operations
scrapeless-scraping-browser --session-id $SESSION_ID open https://example.com
scrapeless-scraping-browser --session-id $SESSION_ID snapshot -i
scrapeless-scraping-browser --session-id $SESSION_ID click @e1

# Step 3: Close when done
scrapeless-scraping-browser --session-id $SESSION_ID close
```

### Automatic Session Management

If you don't specify `--session-id`:
1. The CLI will query for running sessions
2. If a running session exists, it will use the latest one
3. If no running session exists, it will create a new one automatically

**For production workflows, always use `--session-id` to ensure consistency.**

## Authentication Setup

Before using scrapeless-browser, you MUST set up authentication:

```bash
# Method 1: Config file (recommended, persistent)
scrapeless-scraping-browser config set apiKey your_api_token_here

# Method 2: Environment variable
export SCRAPELESS_API_KEY=your_api_token_here

# Verify it's set
scrapeless-scraping-browser config get apiKey
```

Get your API token from https://app.scrapeless.com

## Session Management Behavior

The CLI manages Scrapeless sessions with the following behavior:

- **Session Creation**: First command creates a new Scrapeless session
- **Session Persistence**: Sessions remain active only while connection is maintained
- **Session Termination**: Sessions automatically terminate when connection closes
- **Reconnection Limitation**: Cannot reconnect to terminated sessions

**Important**: For multi-step workflows, consider using the TypeScript API to maintain persistent connections.

## Core Workflow

Every browser automation follows this pattern:

1. **Create Session**: Create a session and save the session ID
2. **Navigate**: Use `--session-id` to navigate to URL
3. **Snapshot**: Get element refs with `--session-id`
4. **Interact**: Use refs to click, fill, select with `--session-id`
5. **Re-snapshot**: After navigation or DOM changes, get fresh refs

```bash
# Set API token first
scrapeless-scraping-browser config set apiKey your_token

# Create session
SESSION_ID=$(scrapeless-scraping-browser new-session --name "form-fill" --ttl 600 --json | jq -r '.taskId')

# Start automation with session ID
scrapeless-scraping-browser --session-id $SESSION_ID open https://example.com/form
scrapeless-scraping-browser --session-id $SESSION_ID snapshot -i
# Output: @e1 [input type="email"], @e2 [input type="password"], @e3 [button] "Submit"

scrapeless-scraping-browser --session-id $SESSION_ID fill @e1 "user@example.com"
scrapeless-scraping-browser --session-id $SESSION_ID fill @e2 "password123"
scrapeless-scraping-browser --session-id $SESSION_ID click @e3
scrapeless-scraping-browser --session-id $SESSION_ID wait --load networkidle
scrapeless-scraping-browser --session-id $SESSION_ID snapshot -i  # Check result
```

## Command Chaining

Commands can be chained with `&&` in a single shell invocation:

```bash
# Chain open + wait + snapshot
scrapeless-scraping-browser open https://example.com && scrapeless-scraping-browser wait --load networkidle && scrapeless-scraping-browser snapshot -i

# Chain multiple interactions
scrapeless-scraping-browser fill @e1 "user@example.com" && scrapeless-scraping-browser fill @e2 "password123" && scrapeless-scraping-browser click @e3
```

**When to chain:** Use `&&` when you don't need to read intermediate output. Run commands separately when you need to parse output first (e.g., snapshot to discover refs, then interact).

## Essential Commands

**Note**: All commands below support the optional `--session-id <id>` parameter.

```bash
# Navigation & Session
scrapeless-scraping-browser new-session [options]              # Create new browser session
scrapeless-scraping-browser [--session-id <id>] open <url>      # Navigate to URL
scrapeless-scraping-browser [--session-id <id>] close           # Close browser session
scrapeless-scraping-browser sessions                           # List running sessions
scrapeless-scraping-browser stop <taskId>                      # Stop specific session
scrapeless-scraping-browser stop-all                           # Stop all sessions
```

### Session Creation with Advanced Options

The `new-session` command supports extensive customization options:

```bash
# Basic session creation
scrapeless-scraping-browser new-session --name "my-session" --ttl 1800

# Session with proxy settings
scrapeless-scraping-browser new-session \
  --name "proxy-session" \
  --proxy-country US \
  --proxy-state CA \
  --proxy-city "Los Angeles" \
  --ttl 3600

# Session with custom browser configuration
scrapeless-scraping-browser new-session \
  --name "mobile-session" \
  --platform iOS \
  --screen-width 375 \
  --screen-height 812 \
  --user-agent "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X)" \
  --timezone "America/Los_Angeles" \
  --languages "en,es"

# Session with recording enabled
scrapeless-scraping-browser new-session \
  --name "recorded-session" \
  --recording true \
  --ttl 7200
```

**Available Options:**
- `--name <name>`: Session name for identification
- `--ttl <seconds>`: Session timeout in seconds (default: 180)
- `--recording <true|false>`: Enable session recording
- `--proxy-country <code>`: Proxy country code (e.g., AU, US, GB, CN, JP)
- `--proxy-state <state>`: Proxy state/region (e.g., NSW, CA, NY, TX)
- `--proxy-city <city>`: Proxy city (e.g., sydney, newyork, london, tokyo)
- `--user-agent <ua>`: Custom user agent string
- `--platform <platform>`: Platform (Windows, macOS, Linux, iOS, Android)
- `--screen-width <px>`: Screen width in pixels (default: 1920)
- `--screen-height <px>`: Screen height in pixels (default: 1080)
- `--timezone <tz>`: Timezone (default: America/New_York)
- `--languages <langs>`: Comma-separated language codes (default: en)

```bash

# Snapshot
scrapeless-scraping-browser [--session-id <id>] snapshot -i             # Interactive elements with refs (recommended)
scrapeless-scraping-browser [--session-id <id>] snapshot -i -C          # Include cursor-interactive elements
scrapeless-scraping-browser [--session-id <id>] snapshot -s "#selector" # Scope to CSS selector

# Interaction (use @refs from snapshot)
scrapeless-scraping-browser [--session-id <id>] click @e1               # Click element
scrapeless-scraping-browser [--session-id <id>] fill @e2 "text"         # Clear and type text
scrapeless-scraping-browser [--session-id <id>] type @e2 "text"         # Type without clearing
scrapeless-scraping-browser [--session-id <id>] press Enter             # Press key
scrapeless-scraping-browser [--session-id <id>] scroll down 500         # Scroll page
scrapeless-scraping-browser [--session-id <id>] scroll down 500 --selector "div.content"  # Scroll within element

# Get information
scrapeless-scraping-browser [--session-id <id>] get text @e1            # Get element text
scrapeless-scraping-browser [--session-id <id>] get url                 # Get current URL
scrapeless-scraping-browser [--session-id <id>] get title               # Get page title
scrapeless-scraping-browser [--session-id <id>] screenshot              # Take screenshot
scrapeless-scraping-browser [--session-id <id>] screenshot --full       # Full page screenshot

# Wait
scrapeless-scraping-browser [--session-id <id>] wait @e1                # Wait for element
scrapeless-scraping-browser [--session-id <id>] wait --load networkidle # Wait for network idle
scrapeless-scraping-browser [--session-id <id>] wait --url "**/page"    # Wait for URL pattern
scrapeless-scraping-browser [--session-id <id>] wait 2000               # Wait milliseconds

# Cookies & Storage
scrapeless-scraping-browser [--session-id <id>] cookies                 # Get all cookies
scrapeless-scraping-browser [--session-id <id>] cookies set <name> <val> # Set cookie
scrapeless-scraping-browser [--session-id <id>] cookies clear           # Clear cookies
scrapeless-scraping-browser [--session-id <id>] storage local           # Get localStorage
scrapeless-scraping-browser [--session-id <id>] storage local set <k> <v>  # Set localStorage

# Multi-page
scrapeless-scraping-browser [--session-id <id>] pages                   # List all pages/tabs
scrapeless-scraping-browser [--session-id <id>] page <pageId>           # Switch to page
scrapeless-scraping-browser [--session-id <id>] tab new [url]           # Open new tab
scrapeless-scraping-browser [--session-id <id>] tab close [n]           # Close tab

# Live preview
scrapeless-scraping-browser live [taskId]                              # Get live preview URL
```
scrapeless-scraping-browser get url                 # Get current URL
scrapeless-scraping-browser get title               # Get page title
scrapeless-scraping-browser screenshot              # Take screenshot
scrapeless-scraping-browser screenshot --full       # Full page screenshot

# Wait
scrapeless-scraping-browser wait @e1                # Wait for element
scrapeless-scraping-browser wait --load networkidle # Wait for network idle
scrapeless-scraping-browser wait --url "**/page"    # Wait for URL pattern
scrapeless-scraping-browser wait 2000               # Wait milliseconds

# Cookies & Storage
scrapeless-scraping-browser cookies                 # Get all cookies
scrapeless-scraping-browser cookies set <name> <val> # Set cookie
scrapeless-scraping-browser cookies clear           # Clear cookies
scrapeless-scraping-browser storage local           # Get localStorage
scrapeless-scraping-browser storage local set <k> <v>  # Set localStorage

# Multi-page
scrapeless-scraping-browser pages                   # List all pages/tabs
scrapeless-scraping-browser page <pageId>           # Switch to page
scrapeless-scraping-browser tab new [url]           # Open new tab
scrapeless-scraping-browser tab close [n]           # Close tab

# Live preview
scrapeless-scraping-browser live                    # Get live preview URL
```

## Common Patterns

### Form Submission

```bash
scrapeless-scraping-browser config set apiKey your_token

scrapeless-scraping-browser open https://example.com/signup
scrapeless-scraping-browser snapshot -i
scrapeless-scraping-browser fill @e1 "Jane Doe"
scrapeless-scraping-browser fill @e2 "jane@example.com"
scrapeless-scraping-browser click @e3
scrapeless-scraping-browser wait --load networkidle
```

### Data Extraction

```bash
scrapeless-scraping-browser config set apiKey your_token

scrapeless-scraping-browser open https://example.com/products
scrapeless-scraping-browser snapshot -i --json
scrapeless-scraping-browser get text @e5 --json
```

### Common Session Configuration Scenarios

#### Mobile Device Simulation
```bash
# Simulate iPhone for mobile-specific content
SESSION_ID=$(scrapeless-scraping-browser new-session \
  --name "mobile-test" \
  --platform iOS \
  --screen-width 375 \
  --screen-height 812 \
  --user-agent "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X)" \
  --json | jq -r '.taskId')

scrapeless-scraping-browser --session-id $SESSION_ID open https://m.example.com
```

#### Geographic Content Testing
```bash
# Access content from different regions
SESSION_ID=$(scrapeless-scraping-browser new-session \
  --name "geo-test" \
  --proxy-country AU \
  --proxy-city sydney \
  --timezone "Australia/Sydney" \
  --languages "en-AU,en" \
  --json | jq -r '.taskId')

scrapeless-scraping-browser --session-id $SESSION_ID open https://example.com
```

#### High-Resolution Desktop Testing
```bash
# Test on high-resolution displays
SESSION_ID=$(scrapeless-scraping-browser new-session \
  --name "desktop-4k" \
  --platform macOS \
  --screen-width 3840 \
  --screen-height 2160 \
  --json | jq -r '.taskId')

scrapeless-scraping-browser --session-id $SESSION_ID open https://example.com
```

#### Session Recording for Debugging
```bash
# Enable recording for troubleshooting
SESSION_ID=$(scrapeless-scraping-browser new-session \
  --name "debug-session" \
  --recording true \
  --ttl 7200 \
  --json | jq -r '.taskId')

scrapeless-scraping-browser --session-id $SESSION_ID open https://example.com
# Session recording will be available for review
```

### Session Persistence

**Important**: Scrapeless sessions terminate when connections close. For persistent workflows, use the TypeScript API:

```bash
scrapeless-scraping-browser config set apiKey your_token

# Create a session for login
scrapeless-scraping-browser create --name "login-session" --ttl 1800
scrapeless-scraping-browser open https://app.example.com/login
scrapeless-scraping-browser snapshot -i
scrapeless-scraping-browser fill @e1 "username"
scrapeless-scraping-browser fill @e2 "password"
scrapeless-scraping-browser click @e3
scrapeless-scraping-browser wait --url "**/dashboard"

# For subsequent operations, create a new session
# (Cannot reuse previous session due to connection termination)
scrapeless-scraping-browser create --name "dashboard-session" --ttl 1800
scrapeless-scraping-browser open https://app.example.com/dashboard
```

**Better Alternative**: Use TypeScript API for multi-step workflows:

```typescript
import { BrowserManager } from './dist/browser.js';

const manager = new BrowserManager();
await manager.launch({ id: 'persistent-workflow', action: 'launch' });

const page = manager.getPage();
await page.goto('https://app.example.com/login');
// Login persists throughout the session
await page.fill('#username', 'user');
await page.fill('#password', 'pass');
await page.click('#login');
await page.waitForURL('**/dashboard');
await page.goto('https://app.example.com/profile');
// Session and cookies maintained

await manager.close();
```

### Using Proxies

```bash
scrapeless-scraping-browser config set apiKey your_token

# Use residential proxy from specific country
scrapeless-scraping-browser config set proxyCountry US
scrapeless-scraping-browser open https://example.com

# Use custom proxy
scrapeless-scraping-browser config set proxyUrl "http://user:pass@proxy.com:8080"
scrapeless-scraping-browser open https://example.com

# Use proxy with state and city (v2 API)
scrapeless-scraping-browser config set proxyCountry US
scrapeless-scraping-browser config set proxyState CA
scrapeless-scraping-browser config set proxyCity "Los Angeles"
scrapeless-scraping-browser open https://example.com
```

### Browser Fingerprinting

```bash
scrapeless-scraping-browser config set apiKey your_token

# Set browser fingerprint to avoid detection
scrapeless-scraping-browser config set fingerprint chrome
scrapeless-scraping-browser open https://example.com

# Customize browser fingerprint details
scrapeless-scraping-browser config set userAgent "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X)"
scrapeless-scraping-browser config set platform iOS
scrapeless-scraping-browser config set screenWidth 375
scrapeless-scraping-browser config set screenHeight 812
scrapeless-scraping-browser config set timezone "Asia/Shanghai"
scrapeless-scraping-browser config set languages "zh-CN,en"
scrapeless-scraping-browser open https://example.com
```

### Session Recording

```bash
scrapeless-scraping-browser config set apiKey your_token

# Enable session recording for debugging
scrapeless-scraping-browser config set sessionRecording true
scrapeless-scraping-browser open https://example.com
# ... perform actions ...
scrapeless-scraping-browser close
# Recording will be available in Scrapeless dashboard
```

### Multiple Sessions

**Note**: Due to session termination behavior, the `--session-id` parameter has limitations. For reliable multi-session workflows, create separate sessions for each task:

```bash
scrapeless-scraping-browser config set apiKey your_token

# Create first session for task A
scrapeless-scraping-browser create --name "task-a" --ttl 1800
scrapeless-scraping-browser open https://site-a.com
# Complete task A operations...

# Create second session for task B  
scrapeless-scraping-browser create --name "task-b" --ttl 1800
scrapeless-scraping-browser open https://site-b.com
# Complete task B operations...

# List all running sessions
scrapeless-scraping-browser sessions

# Stop specific session
scrapeless-scraping-browser stop <taskId>

# Stop all sessions
scrapeless-scraping-browser stop-all
```

**Alternative**: For complex multi-session workflows, use the TypeScript API which supports persistent connections.

## Configuration File

Configuration is managed via the `config` command. All settings are stored in `~/.scrapeless/config.json`.

**Priority**: Config file > Environment variable (only `SCRAPELESS_API_KEY` supports env var)

Available configuration options:
- `apiKey` - Your Scrapeless API token (required)
- `apiVersion` - API version (v1 or v2, default: v2)
- `sessionTtl` - Session timeout in seconds
- `sessionName` - Session name for identification
- `sessionRecording` - Enable session recording (true/false)
- `proxyUrl` - Custom proxy URL
- `proxyCountry` - Proxy country code
- `proxyState` - Proxy state/province
- `proxyCity` - Proxy city
- `fingerprint` - Browser fingerprint
- `debug` - Enable debug logging

## Agent Mode (JSON Output)

Use `--json` for machine-readable output:

```bash
scrapeless-scraping-browser snapshot -i --json
scrapeless-scraping-browser get text @e1 --json
scrapeless-scraping-browser is visible @e2 --json
```

## Ref Lifecycle (Important)

Refs (`@e1`, `@e2`, etc.) are invalidated when the page changes. Always re-snapshot after:

- Clicking links or buttons that navigate
- Form submissions
- Dynamic content loading

```bash
scrapeless-scraping-browser click @e5              # Navigates to new page
scrapeless-scraping-browser snapshot -i            # MUST re-snapshot
scrapeless-scraping-browser click @e1              # Use new refs
```

## Session Management

### Important Session Behavior

**Critical**: Scrapeless sessions have specific connection requirements:

- ✅ **Sessions work perfectly with persistent connections**
- ❌ **Sessions automatically terminate when the connection is closed**
- ❌ **Reconnecting to a terminated session will fail**

### Recommended Usage Patterns

#### For Single Operations
```bash
# Create and use a session for a single task
scrapeless-scraping-browser create --name "single-task" --ttl 600
scrapeless-scraping-browser open https://example.com
scrapeless-scraping-browser screenshot
```

#### For Multi-Step Operations
For complex workflows requiring multiple steps, use the TypeScript API instead of CLI:

```typescript
import { BrowserManager } from './dist/browser.js';

const manager = new BrowserManager();
await manager.launch({ id: 'workflow', action: 'launch' });

const page = manager.getPage();
await page.goto('https://example.com');
await page.screenshot({ path: 'step1.png' });
await page.goto('https://another-site.com');
await page.screenshot({ path: 'step2.png' });

await manager.close();
```

### Session ID Parameter Limitations

The `--session-id` parameter has limitations due to Scrapeless session behavior:

```bash
# This will fail if the session connection was previously closed
scrapeless-scraping-browser --session-id <session-id> open https://example.com
# Error: Session has been terminated and cannot be reconnected
```

**Workaround**: Create new sessions for each workflow instead of reusing session IDs.

### Session Management Commands

Always close sessions when done to avoid leaked resources:

```bash
scrapeless-scraping-browser close                    # Close current session
scrapeless-scraping-browser stop <taskId>            # Stop specific session by ID
scrapeless-scraping-browser stop-all                 # Stop all sessions
```

Check running sessions:

```bash
scrapeless-scraping-browser sessions
# Returns: sessionId, createdAt, status, sessionName
```

## Live Preview

Get a real-time preview of your browser session via WebSocket:

```bash
# Get live preview URL for current session
scrapeless-scraping-browser live

# Get live preview URL for specific session
scrapeless-scraping-browser live abc123def456

# Returns live preview URL for browser viewing
# Open this URL in your browser to view the live session
```

## Timeouts and Slow Pages

For slow websites, use explicit waits:

```bash
# Wait for network activity to settle
scrapeless-scraping-browser wait --load networkidle

# Wait for specific element
scrapeless-scraping-browser wait @e1

# Wait for URL pattern
scrapeless-scraping-browser wait --url "**/dashboard"

# Wait fixed duration (milliseconds)
scrapeless-scraping-browser wait 5000
```

## Error Handling

Common errors and solutions:

**Authentication Error:**
```bash
# Make sure API token is set
scrapeless-scraping-browser config set apiKey your_token
# Or use environment variable
export SCRAPELESS_API_KEY=your_token
```

**Session Not Found:**
```bash
# Session may have expired, create new one
scrapeless-scraping-browser open https://example.com
```

**Element Not Found:**
```bash
# Re-snapshot to get fresh refs
scrapeless-scraping-browser snapshot -i
```

**Timeout:**
```bash
# Increase session timeout (in seconds)
scrapeless-scraping-browser config set sessionTtl 600
scrapeless-scraping-browser open https://example.com
```

## Debugging

Enable debug mode for detailed logs:

```bash
scrapeless-scraping-browser config set debug true
scrapeless-scraping-browser open https://example.com
```

Or use `--debug` flag:

```bash
scrapeless-scraping-browser --debug open https://example.com
```

## Configuration Options

| Configuration | Description |
|---------------|-------------|
| `apiKey` | Your API token (required) |
| `apiVersion` | API version (v1 or v2, default: v2) |
| `sessionTtl` | Session timeout in seconds |
| `sessionName` | Session name for identification |
| `sessionRecording` | Enable session recording (true/false) |
| `proxyUrl` | Custom proxy URL |
| `proxyCountry` | Proxy country code |
| `proxyState` | Proxy state/province |
| `proxyCity` | Proxy city |
| `fingerprint` | Browser fingerprint |
| `userAgent` | Custom user agent string |
| `platform` | Platform type (Windows, Linux, macOS, iOS, Android) |
| `screenWidth` | Screen width in pixels |
| `screenHeight` | Screen height in pixels |
| `timezone` | Timezone (e.g., America/New_York, Asia/Shanghai) |
| `languages` | Comma-separated language codes (e.g., en,zh-CN) |
| `debug` | Enable debug logging |

Set configuration using:
```bash
scrapeless-scraping-browser config set <key> <value>
```

Or use environment variable for API key only:
```bash
export SCRAPELESS_API_KEY=your_token
```

## Key Differences from Local Browsers

1. **Cloud-based**: Runs on Scrapeless infrastructure, not locally
2. **Residential Proxies**: Built-in support for residential proxy rotation
3. **Anti-detection**: Automatic browser fingerprinting and stealth features
4. **Session Recording**: Optional recording of browser sessions
5. **No Installation**: No need to install Chrome/Chromium locally
6. **Scalable**: Run multiple sessions in parallel

## Limitations

- Profile management is not currently supported
- Browser extensions are not currently supported
- Requires active internet connection
- Requires valid Scrapeless API token

## Best Practices

1. **Always set API token** before running commands (via config or env var)
2. **Let automatic session management work** - the CLI will reuse sessions intelligently
3. **Use --session-id** only when you need parallel workflows
4. **Close sessions** when done to avoid charges
5. **Use config file** for persistent settings instead of environment variables
6. **Enable recording** for debugging complex flows
7. **Re-snapshot** after page changes
8. **Use --json** for programmatic access
9. **Set session timeout** appropriately for your use case (in seconds)

## Updates

Check for and install updates:

```bash
# Check version
scrapeless-scraping-browser version

# Update via npm
npm update -g scrapeless-scraping-browser-skills
```

## Support

- Documentation: https://docs.scrapeless.com
- API Reference: https://api.scrapeless.com/docs
- GitHub Issues: https://github.com/scrapeless-ai/scraping-browser-skill/issues
