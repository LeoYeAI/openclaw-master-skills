# NST API Reference

Complete reference for all Nstbrowser-specific API commands in nstbrowser-ai-agent.

## Table of Contents

- [Profile Management API](#profile-management-api)
- [Browser Instance API](#browser-instance-api)
- [Proxy Management API](#proxy-management-api)
- [Tag Management API](#tag-management-api)
- [Group Management API](#group-management-api)
- [Local Data Management API](#local-data-management-api)
- [Environment Variables](#environment-variables)
- [Error Codes](#error-codes)

## Profile Management API

### List Profiles

List all profiles in your Nstbrowser account.

**Command:**
```bash
nstbrowser-ai-agent profile list [--json]
```

**Options:**
- `--json`: Output in JSON format

**Example:**
```bash
nstbrowser-ai-agent profile list
```

**JSON Response:**
```json
{
  "success": true,
  "data": {
    "profiles": [
      {
        "profileId": "86581051-fb0d-4c4a-b1e3-ebc1abd17174",
        "name": "db_x",
        "platform": "Windows",
        "kernel": "124",
        "group": {
          "groupId": "group-123",
          "name": "Production"
        },
        "proxy": {
          "type": "http",
          "host": "proxy.example.com",
          "port": 8080,
          "enabled": true
        },
        "tags": ["production", "automated"]
      }
    ]
  }
}
```

### Show Profile Details

Get complete details for a specific profile.

**Command:**
```bash
nstbrowser-ai-agent profile show <name-or-id> [--json]
```

**Parameters:**
- `<name-or-id>`: Profile name or profile ID

**Options:**
- `--json`: Output in JSON format

**Example:**
```bash
# By name
nstbrowser-ai-agent profile show db_x --json

# By ID
nstbrowser-ai-agent profile show 86581051-fb0d-4c4a-b1e3-ebc1abd17174 --json
```

**JSON Response:**
```json
{
  "success": true,
  "data": {
    "profileId": "86581051-fb0d-4c4a-b1e3-ebc1abd17174",
    "name": "db_x",
    "platform": "Windows",
    "kernel": "124",
    "group": {
      "groupId": "group-123",
      "name": "Production"
    },
    "proxy": {
      "type": "http",
      "host": "proxy.example.com",
      "port": 8080,
      "username": "user",
      "enabled": true
    },
    "tags": [
      {"name": "production", "color": "blue"},
      {"name": "automated", "color": "green"}
    ],
    "fingerprint": {
      "canvas": "...",
      "webgl": "...",
      "fonts": ["Arial", "Times New Roman"]
    },
    "lastLaunchRecord": {
      "launchTime": "2026-03-06T10:00:00Z",
      "closeTime": "2026-03-06T11:00:00Z"
    }
  }
}
```

### Create Profile

Create a new profile with specified configuration.

**Command:**
```bash
nstbrowser-ai-agent profile create <name> [options]
```

**Parameters:**
- `<name>`: Profile name (required)

**Options:**
- `--proxy-host <host>`: Proxy server host
- `--proxy-port <port>`: Proxy server port
- `--proxy-type <type>`: Proxy type (http|https|socks5)
- `--proxy-username <user>`: Proxy username
- `--proxy-password <pass>`: Proxy password
- `--platform <platform>`: Platform (Windows|macOS|Linux)
- `--kernel <version>`: Browser kernel version
- `--group-id <id>`: Group ID

**Example:**
```bash
nstbrowser-ai-agent profile create my-profile \
  --proxy-host proxy.example.com \
  --proxy-port 8080 \
  --proxy-type http \
  --proxy-username user \
  --proxy-password pass \
  --platform Windows \
  --group-id group-123
```

**Response:**
```
Profile created successfully: my-profile (ID: new-profile-id)
```

### Delete Profile

Delete one or more profiles.

**Command:**
```bash
nstbrowser-ai-agent profile delete <profile-name-or-id> [profile-name-or-id...]
```

**Parameters:**
- `<profile-name-or-id>`: One or more profile names or IDs (space-separated)

**Example:**
```bash
# Delete single profile
nstbrowser-ai-agent profile delete 86581051-fb0d-4c4a-b1e3-ebc1abd17174

# Delete multiple profiles
nstbrowser-ai-agent profile delete id-1 id-2 id-3
```

**Response:**
```
Deleted 3 profile(s) successfully
```

## Browser Instance API

### List Running Browsers

List all currently running browser instances.

**Command:**
```bash
nstbrowser-ai-agent browser list
```

**Example:**
```bash
nstbrowser-ai-agent browser list
```

**Response:**
```
Running browsers:
- db_x (86581051-fb0d-4c4a-b1e3-ebc1abd17174) - Running
- test-profile (profile-id-2) - Running
```

### Start Browser

Start a browser instance for a specific profile.

**Command:**
```bash
nstbrowser-ai-agent browser start <name-or-id> [options]
```

**Parameters:**
- `<name-or-id>`: Profile name or profile ID

**Options:**
- `--headless`: Run in headless mode
- `--auto-close`: Auto-close browser when done
- `--disable-gpu`: Disable GPU acceleration

**Example:**
```bash
# By name
nstbrowser-ai-agent browser start db_x

# By ID with options
nstbrowser-ai-agent browser start 86581051-fb0d-4c4a-b1e3-ebc1abd17174 --headless
```

**Response:**
```
Browser started successfully for profile: db_x
```

### Stop Browser

Stop a running browser instance.

**Command:**
```bash
nstbrowser-ai-agent browser stop <name-or-id>
```

**Parameters:**
- `<name-or-id>`: Profile name or profile ID

**Example:**
```bash
# By name
nstbrowser-ai-agent browser stop db_x

# By ID
nstbrowser-ai-agent browser stop 86581051-fb0d-4c4a-b1e3-ebc1abd17174
```

**Response:**
```
Browser stopped successfully for profile: db_x
```

### Stop All Browsers

Stop all running browser instances.

**Command:**
```bash
nstbrowser-ai-agent browser stop-all
```

**Example:**
```bash
nstbrowser-ai-agent browser stop-all
```

**Response:**
```
Stopped 3 browser instance(s)
```

### Get Browser Pages

Get list of all pages/tabs in a running browser.

**Command:**
```bash
nstbrowser-ai-agent browser pages <name-or-id> [--json]
```

**Parameters:**
- `<name-or-id>`: Profile name or profile ID

**Options:**
- `--json`: Output in JSON format

**Example:**
```bash
nstbrowser-ai-agent browser pages db_x --json
```

**JSON Response:**
```json
{
  "success": true,
  "data": {
    "pages": [
      {
        "url": "https://example.com",
        "title": "Example Domain"
      },
      {
        "url": "https://example.com/page2",
        "title": "Page 2"
      }
    ]
  }
}
```

### Get Debugger URL

Get Chrome DevTools debugger WebSocket URL for a running browser.

**Command:**
```bash
nstbrowser-ai-agent browser debugger <name-or-id> [--json]
```

**Parameters:**
- `<name-or-id>`: Profile name or profile ID

**Options:**
- `--json`: Output in JSON format

**Example:**
```bash
nstbrowser-ai-agent browser debugger db_x --json
```

**JSON Response:**
```json
{
  "success": true,
  "data": {
    "debuggerUrl": "ws://localhost:9222/devtools/browser/abc123"
  }
}
```

## Proxy Management API

### Show Proxy Configuration

Show proxy configuration and check result for a profile.

**Command:**
```bash
nstbrowser-ai-agent profile proxy show <name-or-id> [--json]
```

**Parameters:**
- `<name-or-id>`: Profile name or profile ID

**Options:**
- `--json`: Output in JSON format

**Example:**
```bash
nstbrowser-ai-agent profile proxy show db_x --json
```

**JSON Response:**
```json
{
  "success": true,
  "data": {
    "proxy": {
      "type": "http",
      "host": "proxy.example.com",
      "port": 8080,
      "username": "user",
      "enabled": true
    },
    "proxyCheck": {
      "ip": "203.0.113.1",
      "location": "United States",
      "timezone": "America/New_York"
    }
  }
}
```

### Update Proxy

Update proxy configuration for a profile.

**Command:**
```bash
nstbrowser-ai-agent profile proxy update <name-or-id> [options]
```

**Parameters:**
- `<name-or-id>`: Profile name or profile ID

**Options:**
- `--host <host>`: Proxy server host
- `--port <port>`: Proxy server port
- `--type <type>`: Proxy type (http|https|socks5)
- `--username <user>`: Proxy username
- `--password <pass>`: Proxy password

**Example:**
```bash
nstbrowser-ai-agent profile proxy update db_x \
  --host proxy.example.com \
  --port 8080 \
  --type http \
  --username user \
  --password pass
```

**Response:**
```
Proxy updated successfully for profile: db_x
```

### Reset Proxy

Reset proxy configuration for one or more profiles.

**Command:**
```bash
nstbrowser-ai-agent profile proxy reset <profile-name-or-id> [profile-name-or-id...]
```

**Parameters:**
- `<profile-name-or-id>`: One or more profile names or IDs (space-separated)

**Example:**
```bash
# Reset single profile
nstbrowser-ai-agent profile proxy reset 86581051-fb0d-4c4a-b1e3-ebc1abd17174

# Reset multiple profiles
nstbrowser-ai-agent profile proxy reset id-1 id-2 id-3
```

**Response:**
```
Proxy reset successfully for 3 profile(s)
```

### Batch Update Proxy

Update proxy configuration for multiple profiles at once.

**Command:**
```bash
nstbrowser-ai-agent profile proxy batch-update <profile-name-or-id> [profile-name-or-id...] [options]
```

**Parameters:**
- `<profile-name-or-id>`: One or more profile names or IDs (space-separated)

**Options:**
- `--host <host>`: Proxy server host
- `--port <port>`: Proxy server port
- `--type <type>`: Proxy type (http|https|socks5)
- `--username <user>`: Proxy username
- `--password <pass>`: Proxy password

**Example:**
```bash
nstbrowser-ai-agent profile proxy batch-update id-1 id-2 id-3 \
  --host proxy.example.com \
  --port 8080 \
  --type http \
  --username user \
  --password pass
```

**Response:**
```
Proxy updated successfully for 3 profile(s)
```

### Batch Reset Proxy

Reset proxy configuration for multiple profiles at once.

**Command:**
```bash
nstbrowser-ai-agent profile proxy batch-reset <profile-name-or-id> [profile-name-or-id...]
```

**Parameters:**
- `<profile-name-or-id>`: One or more profile names or IDs (space-separated)

**Example:**
```bash
nstbrowser-ai-agent profile proxy batch-reset id-1 id-2 id-3
```

**Response:**
```
Proxy reset successfully for 3 profile(s)
```

## Tag Management API

### List Tags

List all available tags.

**Command:**
```bash
nstbrowser-ai-agent profile tags list
```

**Example:**
```bash
nstbrowser-ai-agent profile tags list
```

**Response:**
```
Available tags:
- production (blue)
- testing (green)
- staging (yellow)
- automated (purple)
```

### Create Tag

Add a tag to a profile.

**Command:**
```bash
nstbrowser-ai-agent profile tags create <profile-name-or-id> <tag-name>
```

**Parameters:**
- `<profile-name-or-id>`: Profile name or ID
- `<tag-name>`: Tag name

**Example:**
```bash
nstbrowser-ai-agent profile tags create 86581051-fb0d-4c4a-b1e3-ebc1abd17174 production
```

**Response:**
```
Tag 'production' added to profile successfully
```

### Update Tags

Update tags for a profile (replaces existing tags).

**Command:**
```bash
nstbrowser-ai-agent profile tags update <profile-name-or-id> <tag:color> [tag:color...]
```

**Parameters:**
- `<profile-name-or-id>`: Profile name or ID
- `<tag:color>`: Tag name with optional color (format: `tag-name:color` or just `tag-name`)

**Example:**
```bash
# With colors
nstbrowser-ai-agent profile tags update 86581051-fb0d-4c4a-b1e3-ebc1abd17174 \
  production:blue testing:green staging:yellow

# Without colors
nstbrowser-ai-agent profile tags update 86581051-fb0d-4c4a-b1e3-ebc1abd17174 \
  production testing staging
```

**Response:**
```
Tags updated successfully for profile
```

### Clear Tags

Clear all tags from one or more profiles.

**Command:**
```bash
nstbrowser-ai-agent profile tags clear <profile-name-or-id> [profile-name-or-id...]
```

**Parameters:**
- `<profile-name-or-id>`: One or more profile names or IDs (space-separated)

**Example:**
```bash
# Clear single profile
nstbrowser-ai-agent profile tags clear 86581051-fb0d-4c4a-b1e3-ebc1abd17174

# Clear multiple profiles
nstbrowser-ai-agent profile tags clear id-1 id-2 id-3
```

**Response:**
```
Tags cleared successfully for 3 profile(s)
```

### Batch Create Tags

Add tags to multiple profiles at once.

**Command:**
```bash
nstbrowser-ai-agent profile tags batch-create <profile-name-or-id> [profile-name-or-id...] <tag:color> [tag:color...]
```

**Parameters:**
- `<profile-id>`: One or more profile IDs (space-separated)
- `<tag:color>`: One or more tags with optional colors

**Example:**
```bash
nstbrowser-ai-agent profile tags batch-create id-1 id-2 id-3 \
  production:blue automated:green
```

**Response:**
```
Tags added successfully to 3 profile(s)
```

### Batch Update Tags

Update tags for multiple profiles at once (replaces existing tags).

**Command:**
```bash
nstbrowser-ai-agent profile tags batch-update <profile-id> [profile-id...] <tag:color> [tag:color...]
```

**Parameters:**
- `<profile-id>`: One or more profile IDs (space-separated)
- `<tag:color>`: One or more tags with optional colors

**Example:**
```bash
nstbrowser-ai-agent profile tags batch-update id-1 id-2 id-3 \
  updated:red verified:green
```

**Response:**
```
Tags updated successfully for 3 profile(s)
```

### Batch Clear Tags

Clear tags from multiple profiles at once.

**Command:**
```bash
nstbrowser-ai-agent profile tags batch-clear <profile-id> [profile-id...]
```

**Parameters:**
- `<profile-id>`: One or more profile IDs (space-separated)

**Example:**
```bash
nstbrowser-ai-agent profile tags batch-clear id-1 id-2 id-3
```

**Response:**
```
Tags cleared successfully for 3 profile(s)
```

## Group Management API

### List Groups

List all profile groups.

**Command:**
```bash
nstbrowser-ai-agent profile groups list
```

**Example:**
```bash
nstbrowser-ai-agent profile groups list
```

**Response:**
```
Available groups:
- Production (group-123)
- Testing (group-456)
- Staging (group-789)
```

### Change Group

Move one or more profiles to a different group.

**Command:**
```bash
nstbrowser-ai-agent profile groups change <group-id> <profile-id> [profile-id...]
```

**Parameters:**
- `<group-id>`: Target group ID
- `<profile-id>`: One or more profile IDs (space-separated)

**Example:**
```bash
# Move single profile
nstbrowser-ai-agent profile groups change group-123 profile-id-1

# Move multiple profiles
nstbrowser-ai-agent profile groups change group-123 id-1 id-2 id-3
```

**Response:**
```
Moved 3 profile(s) to group successfully
```

### Batch Change Group

Move multiple profiles to a different group (alias for `change` with multiple profiles).

**Command:**
```bash
nstbrowser-ai-agent profile groups batch-change <group-id> <profile-id> [profile-id...]
```

**Parameters:**
- `<group-id>`: Target group ID
- `<profile-id>`: One or more profile IDs (space-separated)

**Example:**
```bash
nstbrowser-ai-agent profile groups batch-change group-123 id-1 id-2 id-3
```

**Response:**
```
Moved 3 profile(s) to group successfully
```

## Local Data Management API

### Clear Cache

Clear browser cache for one or more profiles.

**Command:**
```bash
nstbrowser-ai-agent profile cache clear <profile-id> [profile-id...]
```

**Parameters:**
- `<profile-id>`: One or more profile IDs (space-separated)

**Example:**
```bash
# Clear single profile
nstbrowser-ai-agent profile cache clear 86581051-fb0d-4c4a-b1e3-ebc1abd17174

# Clear multiple profiles
nstbrowser-ai-agent profile cache clear id-1 id-2 id-3
```

**Response:**
```
Cache cleared successfully for 3 profile(s)
```

### Clear Cookies

Clear cookies for one or more profiles.

**Command:**
```bash
nstbrowser-ai-agent profile cookies clear <profile-id> [profile-id...]
```

**Parameters:**
- `<profile-id>`: One or more profile IDs (space-separated)

**Example:**
```bash
# Clear single profile
nstbrowser-ai-agent profile cookies clear 86581051-fb0d-4c4a-b1e3-ebc1abd17174

# Clear multiple profiles
nstbrowser-ai-agent profile cookies clear id-1 id-2 id-3
```

**Response:**
```
Cookies cleared successfully for 3 profile(s)
```

## Environment Variables

### NST API Configuration

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `NST_API_KEY` | Nstbrowser API key | - | Yes |
| `NST_HOST` | Nstbrowser API host | `localhost` | No |
| `NST_PORT` | Nstbrowser API port | `8848` | No |

### Profile Selection

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `NST_PROFILE` | Default profile name | - | No |
| `NST_PROFILE_ID` | Default profile ID | - | No |

### Agent Configuration

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `NSTBROWSER_AI_AGENT_PROVIDER` | Browser provider | `nst` | No |
| `NSTBROWSER_AI_AGENT_LOCAL` | Use local browser | `false` | No |
| `NSTBROWSER_AI_AGENT_DEBUG` | Enable debug output | `false` | No |
| `NSTBROWSER_AI_AGENT_DEFAULT_TIMEOUT` | Default timeout (ms) | `25000` | No |

### Example Configuration

```bash
# Required
export NST_API_KEY="your-api-key-here"

# Optional: Custom API endpoint
export NST_HOST="api.nstbrowser.io"
export NST_PORT="443"

# Optional: Default profile
export NST_PROFILE="my-default-profile"

# Optional: Agent configuration
export NSTBROWSER_AI_AGENT_DEBUG=1
export NSTBROWSER_AI_AGENT_DEFAULT_TIMEOUT=30000
```

## Error Codes

### Connection Errors

| Error | Description | Solution |
|-------|-------------|----------|
| `NST_API_KEY is required` | API key not set | Set `NST_API_KEY` environment variable |
| `Failed to connect to Nstbrowser` | Cannot reach NST API | Ensure Nstbrowser client is running |
| `Connection timeout` | API request timed out | Check network connectivity |
| `Invalid API key` | API key is incorrect | Verify API key in Nstbrowser dashboard |

### Profile Errors

| Error | Description | Solution |
|-------|-------------|----------|
| `Profile not found` | Profile doesn't exist | List profiles with `profile list` |
| `Profile name ambiguous` | Multiple profiles with same name | Use profile ID instead |
| `Profile creation failed` | Cannot create profile | Check API key permissions |
| `Profile already exists` | Profile name already in use | Use different name or delete existing |

### Proxy Errors

| Error | Description | Solution |
|-------|-------------|----------|
| `Proxy connection failed` | Cannot connect to proxy | Verify proxy host and port |
| `Proxy authentication failed` | Invalid credentials | Check username and password |
| `Proxy timeout` | Proxy not responding | Increase timeout or try different proxy |
| `Invalid proxy type` | Unsupported proxy type | Use http, https, or socks5 |

### Browser Errors

| Error | Description | Solution |
|-------|-------------|----------|
| `Browser start failed` | Cannot start browser | Check profile configuration |
| `Browser not running` | Browser instance not found | Start browser with `browser start` |
| `Browser crashed` | Browser instance crashed | Restart browser |
| `Browser timeout` | Browser not responding | Increase timeout or restart |

### Batch Operation Errors

| Error | Description | Solution |
|-------|-------------|----------|
| `Partial batch failure` | Some operations failed | Check individual profile errors |
| `Batch size limit exceeded` | Too many profiles | Split into smaller batches |
| `Invalid profile ID in batch` | One or more IDs invalid | Verify all profile IDs |

## Troubleshooting Tips

### Check NST Client Status

```bash
# Check if Nstbrowser client is running
curl http://localhost:8848/api/v2/profiles

# Expected response: JSON with profiles list
```

### Verify API Connectivity

```bash
# Test API connection
nstbrowser-ai-agent profile list

# If successful, API is working
```

### Debug Mode

```bash
# Enable debug output
export NSTBROWSER_AI_AGENT_DEBUG=1
nstbrowser-ai-agent profile list

# Shows detailed API requests and responses
```

### Check Profile Resolution

```bash
# Show profile details to verify name/ID resolution
nstbrowser-ai-agent profile show my-profile --json

# Verify the correct profile is selected
```

### Test Proxy Configuration

```bash
# Show proxy configuration and check result
nstbrowser-ai-agent profile proxy show my-profile --json

# Verify IP, location, and timezone
```

## See Also

- [Profile Management Guide](profile-management.md)
- [Proxy Configuration Guide](proxy-configuration.md)
- [Batch Operations Guide](batch-operations.md)
- [Troubleshooting Guide](troubleshooting.md)
