# Proxy Configuration Guide

Detailed guide for configuring and managing proxies in Nstbrowser profiles.

## Table of Contents

- [Proxy Types](#proxy-types)
- [Proxy Configuration](#proxy-configuration)
- [Proxy Testing](#proxy-testing)
- [Rotating Proxies](#rotating-proxies)
- [Common Issues](#common-issues)

## Proxy Types

### HTTP Proxies

HTTP proxies are the most common type, suitable for web browsing.

**Characteristics:**
- Protocol: HTTP/1.1
- Port: Usually 8080, 3128, or 80
- Authentication: Basic auth (username/password)
- Encryption: No (traffic is not encrypted)
- Use case: General web browsing, scraping

**Example:**
```bash
nstbrowser-ai-agent profile proxy update my-profile \
  --host proxy.example.com \
  --port 8080 \
  --type http \
  --username user \
  --password pass
```

### HTTPS Proxies

HTTPS proxies provide encrypted connections.

**Characteristics:**
- Protocol: HTTP/1.1 over TLS
- Port: Usually 443 or 8443
- Authentication: Basic auth (username/password)
- Encryption: Yes (traffic is encrypted)
- Use case: Secure browsing, sensitive data

**Example:**
```bash
nstbrowser-ai-agent profile proxy update my-profile \
  --host secure-proxy.example.com \
  --port 443 \
  --type https \
  --username user \
  --password pass
```

### SOCKS5 Proxies

SOCKS5 proxies support any protocol (HTTP, HTTPS, FTP, etc.).

**Characteristics:**
- Protocol: SOCKS5
- Port: Usually 1080
- Authentication: Username/password or no auth
- Encryption: Optional (depends on implementation)
- Use case: Advanced use cases, UDP support

**Example:**
```bash
nstbrowser-ai-agent profile proxy update my-profile \
  --host socks-proxy.example.com \
  --port 1080 \
  --type socks5 \
  --username user \
  --password pass
```

## Proxy Configuration

### Setting Proxy for Single Profile

Update proxy configuration for one profile:

```bash
nstbrowser-ai-agent profile proxy update <name-or-id> \
  --host proxy.example.com \
  --port 8080 \
  --type http \
  --username user \
  --password pass
```

**Parameters:**
- `--host`: Proxy server hostname or IP address (required)
- `--port`: Proxy server port (required)
- `--type`: Proxy type - http, https, or socks5 (required)
- `--username`: Authentication username (optional)
- `--password`: Authentication password (optional)

### Batch Proxy Updates

Update proxy for multiple profiles at once:

```bash
nstbrowser-ai-agent profile proxy batch-update id-1 id-2 id-3 \
  --host proxy.example.com \
  --port 8080 \
  --type http \
  --username user \
  --password pass
```

**Benefits:**
- Faster than updating profiles individually
- Consistent configuration across profiles
- Atomic operation (all or nothing)

### Proxy Authentication

#### With Username and Password

```bash
nstbrowser-ai-agent profile proxy update my-profile \
  --host proxy.example.com \
  --port 8080 \
  --type http \
  --username myuser \
  --password mypass
```

#### Without Authentication

```bash
nstbrowser-ai-agent profile proxy update my-profile \
  --host proxy.example.com \
  --port 8080 \
  --type http
```

#### Using Environment Variables

Store credentials securely:

```bash
# Set environment variables
export PROXY_USERNAME="myuser"
export PROXY_PASSWORD="mypass"

# Use in command
nstbrowser-ai-agent profile proxy update my-profile \
  --host proxy.example.com \
  --port 8080 \
  --type http \
  --username "$PROXY_USERNAME" \
  --password "$PROXY_PASSWORD"
```

### Resetting Proxy

Remove proxy configuration from profiles:

```bash
# Reset single profile
nstbrowser-ai-agent profile proxy reset <profile-name-or-id>

# Reset multiple profiles (batch)
nstbrowser-ai-agent profile proxy batch-reset id-1 id-2 id-3
```

## Proxy Testing

### Viewing Proxy Configuration

Check current proxy settings:

```bash
nstbrowser-ai-agent profile proxy show my-profile --json
```

**Response includes:**
- Proxy configuration (type, host, port, credentials)
- Proxy check result (IP, location, timezone)

### Verifying Proxy Connection

The `proxy show` command automatically tests the proxy:

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

### Manual Proxy Testing

Test proxy manually before assigning to profile:

```bash
# Test HTTP proxy
curl -x http://user:pass@proxy.example.com:8080 https://api.ipify.org

# Test HTTPS proxy
curl -x https://user:pass@proxy.example.com:443 https://api.ipify.org

# Test SOCKS5 proxy
curl --socks5 user:pass@proxy.example.com:1080 https://api.ipify.org
```

### Checking IP and Location

Verify the proxy is working correctly:

```bash
# Launch browser with profile
nstbrowser-ai-agent --profile my-profile open https://api.ipify.org

# Get the displayed IP
nstbrowser-ai-agent get text body

# Should show proxy IP, not your real IP
```

## Rotating Proxies

### Strategy 1: Profile-Based Rotation

Use different profiles with different proxies:

```bash
# Create profiles with different proxies
nstbrowser-ai-agent profile create profile-1
nstbrowser-ai-agent profile proxy update profile-1 --host proxy1.com --port 8080 --type http

nstbrowser-ai-agent profile create profile-2
nstbrowser-ai-agent profile proxy update profile-2 --host proxy2.com --port 8080 --type http

nstbrowser-ai-agent profile create profile-3
nstbrowser-ai-agent profile proxy update profile-3 --host proxy3.com --port 8080 --type http

# Rotate by switching profiles
nstbrowser-ai-agent --profile profile-1 open https://example.com
nstbrowser-ai-agent close

nstbrowser-ai-agent --profile profile-2 open https://example.com
nstbrowser-ai-agent close

nstbrowser-ai-agent --profile profile-3 open https://example.com
nstbrowser-ai-agent close
```

### Strategy 2: Batch Update Rotation

Update proxies for multiple profiles:

```bash
# Get profile IDs
PROFILE_IDS=$(nstbrowser-ai-agent profile list --json | jq -r '.data.profiles | map(.profileId) | join(" ")')

# Update all profiles to proxy 1
nstbrowser-ai-agent profile proxy batch-update $PROFILE_IDS \
  --host proxy1.com --port 8080 --type http

# Later, update all profiles to proxy 2
nstbrowser-ai-agent profile proxy batch-update $PROFILE_IDS \
  --host proxy2.com --port 8080 --type http
```

### Strategy 3: Script-Based Rotation

Automate proxy rotation with a script:

```bash
#!/bin/bash

PROXIES=(
  "proxy1.com:8080"
  "proxy2.com:8080"
  "proxy3.com:8080"
)

PROFILES=(
  "profile-name-1"
  "profile-name-2"  
  "profile-name-3"
)

# Assign proxies to profiles in round-robin
for i in "${!PROFILES[@]}"; do
  PROXY="${PROXIES[$i % ${#PROXIES[@]}]}"
  HOST="${PROXY%:*}"
  PORT="${PROXY#*:}"
  
  nstbrowser-ai-agent profile proxy update "${PROFILES[$i]}" \
    --host "$HOST" \
    --port "$PORT" \
    --type http
done
```

### Performance Considerations

**Batch Operations:**
- Use batch commands for multiple profiles
- Reduces API calls and improves speed
- Atomic operations ensure consistency

**Proxy Pool Size:**
- Larger pool = better distribution
- Smaller pool = easier management
- Balance based on your needs

**Rotation Frequency:**
- Rotate per request (most aggressive)
- Rotate per session (balanced)
- Rotate per day (conservative)

## Common Issues

### Connection Failures

**Symptom:** Cannot connect to proxy server

**Causes:**
- Incorrect host or port
- Proxy server is down
- Firewall blocking connection
- Network connectivity issues

**Solutions:**
```bash
# Test proxy manually
curl -x http://proxy.example.com:8080 https://api.ipify.org

# Check proxy status
ping proxy.example.com

# Verify port is open
nc -zv proxy.example.com 8080

# Try different proxy
nstbrowser-ai-agent profile proxy update my-profile \
  --host backup-proxy.com --port 8080 --type http
```

### Authentication Errors

**Symptom:** 407 Proxy Authentication Required

**Causes:**
- Incorrect username or password
- Credentials not provided
- Proxy requires different auth method

**Solutions:**
```bash
# Verify credentials
nstbrowser-ai-agent profile proxy show my-profile --json

# Update with correct credentials
nstbrowser-ai-agent profile proxy update my-profile \
  --host proxy.example.com \
  --port 8080 \
  --type http \
  --username correct-user \
  --password correct-pass

# Test manually
curl -x http://user:pass@proxy.example.com:8080 https://api.ipify.org
```

### Timeout Issues

**Symptom:** Proxy connection times out

**Causes:**
- Slow proxy server
- Network latency
- Proxy overloaded
- Default timeout too short

**Solutions:**
```bash
# Increase timeout
export NSTBROWSER_AI_AGENT_DEFAULT_TIMEOUT=45000

# Test proxy speed
time curl -x http://proxy.example.com:8080 https://api.ipify.org

# Try faster proxy
nstbrowser-ai-agent profile proxy update my-profile \
  --host faster-proxy.com --port 8080 --type http
```

### IP Leaks

**Symptom:** Real IP is exposed instead of proxy IP

**Causes:**
- WebRTC leak
- DNS leak
- Proxy not properly configured
- Browser fingerprint mismatch

**Solutions:**
```bash
# Verify proxy is working
nstbrowser-ai-agent --profile my-profile open https://api.ipify.org
nstbrowser-ai-agent get text body

# Check for leaks
nstbrowser-ai-agent --profile my-profile open https://browserleaks.com/ip

# Verify proxy configuration
nstbrowser-ai-agent profile proxy show my-profile --json
```

### Proxy Blocked

**Symptom:** Target website blocks proxy IP

**Causes:**
- Proxy IP is blacklisted
- Too many requests from proxy
- Proxy is known datacenter IP
- Website has strict anti-bot measures

**Solutions:**
```bash
# Rotate to different proxy
nstbrowser-ai-agent profile proxy update my-profile \
  --host different-proxy.com --port 8080 --type http

# Use residential proxy instead of datacenter
nstbrowser-ai-agent profile proxy update my-profile \
  --host residential-proxy.com --port 8080 --type http

# Reduce request rate
# Add delays between requests in your automation script
```

## See Also

- [NST API Reference](nst-api-reference.md)
- [Profile Management Guide](profile-management.md)
- [Batch Operations Guide](batch-operations.md)
- [Troubleshooting Guide](troubleshooting.md)
