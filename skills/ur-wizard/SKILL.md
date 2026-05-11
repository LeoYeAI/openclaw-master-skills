---
name: ur-wizard
description: URnetwork Wizard - Complete decentralized privacy network skill for creating HTTPS/SOCKS/WireGuard proxies (consumer mode) and earning rewards by providing egress bandwidth (provider mode). Use when needing anonymous internet access, setting up VPN connections, scraping through proxies, or running a provider node to earn USDC. Formerly proxy-vpn, now enriched with full official documentation.
---

# URnetwork (proxy-vpn) Skill

URnetwork is a decentralized privacy network where users can either:
1. **Consume** - Use the network for secure, anonymous internet access via HTTPS/SOCKS/WireGuard proxies
2. **Provide** - Share egress bandwidth and earn rewards (USDC payouts)

**Official Docs:** https://docs.ur.io

## Endpoints

| Service | URL |
|---------|-----|
| API | https://api.bringyour.com |
| MCP Server | https://mcp.bringyour.com |
| API Spec | https://github.com/urnetwork/connect/blob/main/api/bringyour.yml |
| Web UI | https://ur.io |

---

## Authentication

All API calls require a JWT token in the Authorization header:

```bash
# Get auth code from human (from https://ur.io web UI)
# Then exchange for JWT:
curl -X POST https://api.bringyour.com/auth/code-login \
  -d '{"auth_code": "<AUTH CODE>"}' | jq ".by_jwt"
```

Store the JWT and reuse. To refresh, get a new auth code and repeat.

---

## Consumer Mode: Creating Proxies

### Proxy Types

| Use Case | Protocol | Config Source |
|----------|----------|---------------|
| **Web Scraping/Browsing** | HTTPS | `proxy_config_result.https_proxy_url` |
| **Low-level Sockets/UDP** | SOCKS5 | `proxy_config_result.socks_proxy_url` |
| **System-wide/OS Level** | WireGuard | `proxy_config_result.wg_config.config` |

**SOCKS5 Note:** Use `access_token` as username, empty password. Supports SOCKS5H (remote DNS resolution).

**WireGuard Note:** Must set `proxy_config.enable_wg: true` in the auth-client request.

### Method 1: MCP Skill (Recommended)

The MCP skill simplifies location search and proxy creation:

1. Ask user for desired location (country/region/city)
2. Search and create proxy via MCP
3. If no matches, broaden search (city → region → country)
4. If still no matches, show top 10 available countries

### Method 2: API - By Country

```bash
# Step 1: Find locations
curl -X POST -H 'Authorization: Bearer <JWT>' \
  https://api.bringyour.com/network/find-locations \
  -d '{"query": "Germany"}' | jq '.locations'

# Step 2: Note country_code (e.g., "DE")

# Step 3: Create proxy
curl -X POST -H 'Authorization: Bearer <JWT>' \
  https://api.bringyour.com/network/auth-client \
  -d '{
    "proxy_config": {
      "initial_device_state": {
        "country_code": "DE"
      }
    }
  }'
```

### Method 3: API - By Location ID

```bash
# Step 1: Find locations
curl -X POST -H 'Authorization: Bearer <JWT>' \
  https://api.bringyour.com/network/find-locations \
  -d '{"query": "Berlin"}' | jq '.locations'

# Step 2: Note location_id

# Step 3: Create proxy with specific location
curl -X POST -H 'Authorization: Bearer <JWT>' \
  https://api.bringyour.com/network/auth-client \
  -d '{
    "proxy_config": {
      "initial_device_state": {
        "location": {
          "connect_location_id": {
            "location_id": "<LOCATION_ID>"
          }
        }
      }
    }
  }'
```

### Method 4: API - Enumerate Egress IPs

For rotating through multiple providers in a location:

```bash
# Step 1-2: Get location_id as above

# Step 3: Find providers (egress IPs) for location
curl -X POST -H 'Authorization: Bearer <JWT>' \
  https://api.bringyour.com/network/find-providers2 \
  -d '{
    "specs": [{"client_id": "<CLIENT_ID>"}],
    "count": 10
  }' | jq '.providers'

# Step 4: Create proxy for each client_id
curl -X POST -H 'Authorization: Bearer <JWT>' \
  https://api.bringyour.com/network/auth-client \
  -d '{
    "proxy_config": {
      "initial_device_state": {
        "location": {
          "connect_location_id": {
            "client_id": "<CLIENT_ID>"
          }
        }
      }
    }
  }'
```

### Location Types

When searching, filter by `location_type`:

| Type | Description |
|------|-------------|
| `country` | Countries |
| `region` | States, provinces, metro areas |
| `city` | Cities |

---

## Provider Mode: Earning by Sharing Bandwidth

### Advanced: Providers Through Shadowsocks Proxy

### Advanced: Providers Through SOCKS5 Proxy (Transparent Routing)

Run URnetwork providers through an upstream SOCKS5 proxy for added anonymity or to match specific egress IPs.

**Architecture:**
```
┌─────────────────────────────────────────┐
│        URnetwork Provider Container     │
│  ┌──────────────┐  ┌──────────────┐    │
│  │ Provider     │──│ Redsocks     │────┼───▶ Upstream SOCKS5
│  │ (egress)     │  │ (iptables)   │    │    (residential/datacenter)
│  └──────────────┘  └──────────────┘    │
└─────────────────────────────────────────┘
```

**Dockerfile Setup:**

```dockerfile
FROM bringyour/community-provider:g4-latest

USER root
RUN apt-get update && apt-get install -y redsocks iptables supervisor curl

# Copy configs
COPY redsocks.conf /etc/redsocks/redsocks.conf
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf
COPY start-proxied.sh /usr/local/bin/start-proxied.sh
RUN chmod +x /usr/local/bin/start-proxied.sh

EXPOSE 80
ENTRYPOINT ["/usr/local/bin/start-proxied.sh"]
```

**redsocks.conf:**
```
base {
    log_debug = off;
    log_info = on;
    daemon = off;
    redirector = iptables;
}

redsocks {
    local_ip = 0.0.0.0;
    local_port = 12345;
    ip = <SOCKS5_PROXY_IP>;
    port = <SOCKS5_PROXY_PORT>;
    type = socks5;
    login = "<USERNAME>";
    password = "<PASSWORD>";
}
```

**start-proxied.sh:**
```bash
#!/bin/bash
set -e

# Configure iptables to redirect all TCP through redsocks
iptables -t nat -N REDSOCKS 2>/dev/null || true
iptables -t nat -F REDSOCKS 2>/dev/null || true

# Exclude local networks and proxy server
iptables -t nat -A REDSOCKS -d <SOCKS5_PROXY_IP> -j RETURN
iptables -t nat -A REDSOCKS -d 0.0.0.0/8 -j RETURN
iptables -t nat -A REDSOCKS -d 10.0.0.0/8 -j RETURN
iptables -t nat -A REDSOCKS -d 127.0.0.0/8 -j RETURN
iptables -t nat -A REDSOCKS -d 172.16.0.0/12 -j RETURN
iptables -t nat -A REDSOCKS -d 192.168.0.0/16 -j RETURN

# Redirect to redsocks
iptables -t nat -A REDSOCKS -p tcp -j REDIRECT --to-ports 12345
iptables -t nat -A OUTPUT -p tcp -j REDSOCKS

# Start supervisor (manages redsocks + provider)
exec /usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf
```

**Run Container:**
```bash
docker run --name urnetwork-proxied \
  --cap-add=NET_ADMIN \
  --mount type=bind,source=$HOME/.urnetwork,target=/root/.urnetwork \
  --restart always \
  -d urnetwork-proxied:latest
```

**Requirements:**
- `--cap-add=NET_ADMIN` (required for iptables)
- Same JWT file mounted at `/root/.urnetwork/jwt`
- Container uses supervisor to manage redsocks + provider

**Verification:**
```bash
# Check egress IP from inside container
docker exec urnetwork-proxied curl -s http://ipinfo.io/ip
# Should match your SOCKS5 proxy IP
```

**Resilience:**
- Provider auto-restarts on failure
- Redsocks auto-restarts via supervisor
- Container `--restart always` for boot persistence
- Retry wrapper handles proxy outages gracefully

---

### Standard Provider Mode: Earning by Sharing Bandwidth

### What is a Provider?

A provider shares egress capacity (internet connection) with the URnetwork. Users connect through providers to access the internet securely. Providers earn USDC payouts for participating.

**Payout Structure:**
- 10% of premium revenue + $0.10 minimum per MAU (Monthly Active User)
- Referral bonus: 50% of referred user's earnings + 50% of their referral bonus
- Payouts in USDC on Polygon or Solana
- Weekly payout sweeps

### Installation Methods

#### Option 1: One-line Install (Linux)

```bash
curl -fSsL https://raw.githubusercontent.com/urnetwork/connect/refs/heads/main/scripts/Provider_Install_Linux.sh | sh
```

Uninstall:
```bash
curl -fSsL https://raw.githubusercontent.com/urnetwork/connect/refs/heads/main/scripts/Provider_Uninstall_Linux.sh | sh
```

#### Option 2: Windows (PowerShell)

```powershell
powershell -c "irm https://raw.githubusercontent.com/urnetwork/connect/refs/heads/main/scripts/Provider_Install_Win32.ps1 | iex"
```

Uninstall:
```powershell
powershell -c "irm https://raw.githubusercontent.com/urnetwork/connect/refs/heads/main/scripts/Provider_Uninstall_Win32.ps1 | iex"
```

#### Option 3: Build from Source

```bash
mkdir urnetwork && cd urnetwork
git clone https://github.com/urnetwork/connect
git clone https://github.com/urnetwork/protocol
cd connect/provider
go build  # Binary at ./provider
```

#### Option 4: Docker Container

Images: `bringyour/community-provider:g1-latest` through `g4-latest` (g4 = most stable)

```bash
# Initialize (first time)
docker run --mount type=bind,source=$HOME/.urnetwork,target=/root/.urnetwork \
  bringyour/community-provider:g4-latest auth

# Run provider
docker run --mount type=bind,source=$HOME/.urnetwork,target=/root/.urnetwork \
  --restart no -d bringyour/community-provider:g4-latest provide
```

### Setting Up a Provider

1. **Get auth code:**
   - Visit https://ur.io
   - Create/login to network
   - Click "Copy an Auth Code"

2. **Authenticate:**
   ```bash
   ./provider auth
   # Paste auth code when prompted
   # Saved to ~/.urnetwork/jwt
   ```

3. **Run provider:**
   ```bash
   ./provider provide
   # "Provider XXX started"
   ```

4. **Set up wallet in app** for payouts (USDC on Polygon/Solana)

### Running as Background Service

**Linux (systemd):**
```bash
systemctl --user start urnetwork    # Start
systemctl --user stop urnetwork     # Stop
systemctl --user enable urnetwork   # Auto-start on login
systemctl --user disable urnetwork  # Disable auto-start
```

**macOS (launchd):**
```bash
# Download launchd template from GitHub
# Edit paths and user
sudo cp urnetwork-provider.plist /Library/LaunchAgents/
sudo launchctl load /Library/LaunchAgents/urnetwork-provider.plist
sudo launchctl start /Library/LaunchAgents/urnetwork-provider.plist

# Check logs
tail -f /var/log/system.log | grep -i provider
```

**Windows:**
- Installer asks about startup programs
- Or run manually in background:
```powershell
powershell -NoProfile -WindowStyle Hidden -Command \
  "Start-Process urnetwork.exe -ArgumentList 'provide' -WindowStyle Hidden"
```

### Multi-Platform Builds

Build for multiple architectures:

```bash
cd connect/provider
make build

# Outputs to:
# build/darwin/amd64/provider
# build/darwin/arm64/provider
# build/linux/amd64/provider
# build/linux/arm64/provider
# build/linux/arm/provider
# build/linux/386/provider
# build/windows/amd64/provider
# build/windows/arm64/provider
```

Or download pre-built binaries from nightly releases.

---

## Additional CLIs

| CLI | Purpose |
|-----|---------|
| `provider` | Run egress provider (earn rewards) |
| `tether` | Network interfaces and protocol servers (packet routing) |
| `bringyourctl` | Manage your own network space deployment |
| `warpctl` | Continuous deployment into network space |

---

## Trust and Safety

- Providers follow trust and safety rules
- Network is free with data cap
- Supporters get higher data cap + priority speeds
- Supports email, SMS, Google, Apple auth
- Aggressive deletion of user info after payout (1 week retention)

---

## Economic Model Summary

**For Users:**
- Free tier with data cap
- Premium: ~$5/month for higher cap + priority

**For Providers:**
- 10% of premium revenue + $0.10/MAU minimum
- Up to 20% of premium revenue paid to community
- 50% referral bonus on referred users
- Target margins: 70-80% at scale

**Company Phases:**
1. Phase 0: Build scalable network
2. Phase 1: Break-even at 4% premium conversion
3. Phase 2: Scale with fixed costs
4. Phase 3: Profitable expansion

---

## Quick Reference

**Get JWT:**
```bash
curl -X POST https://api.bringyour.com/auth/code-login \
  -d '{"auth_code": "<CODE>"}' | jq ".by_jwt"
```

**Find Locations:**
```bash
curl -X POST -H 'Authorization: Bearer <JWT>' \
  https://api.bringyour.com/network/find-locations \
  -d '{"query": "Germany"}' | jq '.locations'
```

**Create Proxy:**
```bash
curl -X POST -H 'Authorization: Bearer <JWT>' \
  https://api.bringyour.com/network/auth-client \
  -d '{"proxy_config": {"initial_device_state": {"country_code": "DE"}}}'
```

**Install Provider:**
```bash
curl -fSsL https://raw.githubusercontent.com/urnetwork/connect/refs/heads/main/scripts/Provider_Install_Linux.sh | sh
```

---

## Router/IoT Platforms

- **Raspberry Pi:** See docs
- **Ubiquiti EdgeOS:** See docs  
- **MikroTik RouterOS:** See docs

All support provider binary deployment.

### Advanced: Providers Through Shadowsocks Proxy

Run URnetwork providers through a Shadowsocks proxy for enhanced privacy or specific egress routing.

**Shadowsocks vs SOCKS5:**
- Shadowsocks uses encryption (AES-256-GCM, etc.) — harder to detect/block
- Better for bypassing firewalls (e.g., China, corporate networks)
- Slightly more overhead than plain SOCKS5

**Architecture:**
```
┌─────────────────────────────────────────┐
│        URnetwork Provider Container     │
│  ┌──────────────┐  ┌──────────────┐    │
│  │ Provider     │──│ ss-local     │────┼───▶ Shadowsocks Server
│  │ (egress)     │  │ (SOCKS5:1080)│    │    (encrypted tunnel)
│  └──────────────┘  └──────────────┘    │
└─────────────────────────────────────────┘
```

**Shadowsocks Config Format:**
```
Shadowsocks/proxy/server/port/method/country/password

Example:
Shadowsocks/proxy/138.249.106.2/64619/aes-256-gcm/France/NedyYDqp
```

**Dockerfile Setup:**

```dockerfile
FROM bringyour/community-provider:g4-latest

# Install shadowsocks-libev
RUN apt-get update && apt-get install -y \
    shadowsocks-libev \
    && rm -rf /var/lib/apt/lists/*

# Copy config
COPY shadowsocks.json /etc/shadowsocks-libev/config.json

# Copy startup script
COPY start-shadowsocks.sh /start-shadowsocks.sh
RUN chmod +x /start-shadowsocks.sh

EXPOSE 1080

ENTRYPOINT ["/start-shadowsocks.sh"]
```

**shadowsocks.json:**
```json
{
    "server": "YOURIP",
    "server_port": YOURPORT,
    "local_port": YOURPORT,
    "local_address": "YOURIP",
    "password": "YOURpass",
    "timeout": 300,
    "method": "YOURMETHOD"
}
```

**start-shadowsocks.sh:**
```bash
#!/bin/bash
set -e

# Start shadowsocks client
ss-local -c /etc/shadowsocks-libev/config.json &
SS_PID=$!
echo "Shadowsocks client started (PID: $SS_PID)"

# Wait for shadowsocks to be ready
sleep 3

# Verify shadowsocks is listening
if ! netstat -tlnp 2>/dev/null | grep -q ':1080' && \
   ! ss -tlnp 2>/dev/null | grep -q ':1080'; then
    if ! pgrep -x "ss-local" > /dev/null; then
        echo "ERROR: Shadowsocks not running"
        exit 1
    fi
fi
echo "Shadowsocks proxy ready on 127.0.0.1:1080"

# Start URnetwork provider with proxy environment
export HTTP_PROXY="socks5://127.0.0.1:1080"
export HTTPS_PROXY="socks5://127.0.0.1:1080"
export ALL_PROXY="socks5://127.0.0.1:1080"

exec /usr/local/sbin/bringyour-provider provide
```

**Build Image:**
```bash
docker build -t urnetwork-shadowsocks:latest .
```

**Run Shadowsocks Provider:**
```bash
# Create JWT directory
mkdir -p ~/.urnetwork-ss-1
echo "<JWT>" > ~/.urnetwork-ss-1/jwt

# Run container
docker run -d \
  --name urnetwork-shadowsocks-1 \
  --restart always \
  -v ~/.urnetwork-ss-1:/root/.urnetwork \
  -e WARP_ENV=community \
  urnetwork-shadowsocks:latest
```

**Scale to Multiple Providers:**
```bash
JWT="<YOUR_JWT>"

for i in $(seq 1 10); do
  mkdir -p ~/.urnetwork-ss-$i
  echo "$JWT" > ~/.urnetwork-ss-$i/jwt
  
  docker run -d \
    --name urnetwork-shadowsocks-$i \
    --restart always \
    -v ~/.urnetwork-ss-$i:/root/.urnetwork \
    -e WARP_ENV=community \
    urnetwork-shadowsocks:latest
done
```

**Verification:**
```bash
# Check container status
docker ps --filter "name=urnetwork-shadowsocks"

# Check shadowsocks logs
docker logs urnetwork-shadowsocks-1 | grep "listening"
# Should show: "listening at 0.0.0.0:1080"

# Check provider logs
docker logs urnetwork-shadowsocks-1 | grep "Provider"
# Should show: "Provider XXX started"
```

**Common Shadowsocks Methods:**
| Method | Description |
|--------|-------------|
| `aes-256-gcm` | Recommended, hardware-accelerated |
| `aes-128-gcm` | Faster, slightly less secure |
| `chacha20-ietf-poly1305` | Good for mobile/ARM devices |

**Troubleshooting:**
- **401 Unauthorized:** URnetwork API issue (not Shadowsocks-related)
- **Connection refused:** Check Shadowsocks server IP/port
- **Method not supported:** Ensure method matches server config

---

## Quick Reference: Proxied Provider

**Build Image:**
```bash
docker build -t urnetwork-proxied:latest .
```

**Run Proxied Provider:**
```bash
docker run --name urnetwork-proxied \
  --cap-add=NET_ADMIN \
  --mount type=bind,source=$HOME/.urnetwork,target=/root/.urnetwork \
  --restart always \
  -d urnetwork-proxied:latest
```

**Verify Egress IP:**
```bash
docker exec urnetwork-proxied curl -s http://ipinfo.io/ip
```

**Files Needed:**
- `Dockerfile` - extends provider image with redsocks/iptables
- `redsocks.conf` - SOCKS5 proxy configuration
- `start-proxied.sh` - iptables setup + supervisor launch
- `supervisord.conf` - manages redsocks + provider

**Proxy Format:**
```
socks5/45.91.198.75:7778/username/password
```

---

**Quick Reference: Shadowsocks Provider**

**Build Image:**
```bash
docker build -t urnetwork-shadowsocks:latest .
```

**Run Shadowsocks Provider:**
```bash
docker run -d \
  --name urnetwork-shadowsocks-1 \
  --restart always \
  -v ~/.urnetwork-ss-1:/root/.urnetwork \
  -e WARP_ENV=community \
  urnetwork-shadowsocks:latest
```

**Shadowsocks Config Format:**
```
Shadowsocks/proxy/server/port/method/country/password

Example:
Shadowsocks/proxy/138.249.106.2/64619/aes-256-gcm/France/NedyYDqp
```

**Files Needed:**
- `Dockerfile` - extends provider image with shadowsocks-libev
- `shadowsocks.json` - Shadowsocks client config
- `start-shadowsocks.sh` - starts ss-local + provider

---

## Provider Monitoring

### Quick Status Check

```bash
# All URnetwork containers
docker ps --format "table {{.Names}}\t{{.Status}}" | grep urnetwork

# Count by type
docker ps --format "{{.Names}}" | grep -c "urnetwork-provider"
docker ps --format "{{.Names}}" | grep -c "urnetwork-proxied"
docker ps --format "{{.Names}}" | grep -c "urnetwork-shadowsocks"
```

### Verify Actually Providing vs Restarting

**Check for authentication errors:**
```bash
# Count "Unauthorized" errors in logs
docker logs urnetwork-provider-1 2>&1 | grep -c "Unauthorized"

# Check recent restarts
docker ps --format "table {{.Names}}\t{{.Status}}" | grep urnetwork-provider

# "Up X minutes" = healthy, "Restarting" = auth/connection issues
```

**Check provider logs for success:**
```bash
# Good: "Provider XXX started" without errors
docker logs urnetwork-proxied-1 2>&1 | grep "Provider.*started"

# Bad: Stack traces with "401 Unauthorized"
docker logs urnetwork-provider-1 2>&1 | tail -20
```

### Provider Health Summary Script

```bash
#!/bin/bash
echo "=== URnetwork Provider Health ==="
for container in $(docker ps -a --format "{{.Names}}" | grep urnetwork | sort); do
  status=$(docker ps --filter "name=$container" --format "{{.Status}}")
  errors=$(docker logs $container 2>&1 | grep -c "Unauthorized" || echo "0")
  if echo "$status" | grep -q "Restarting"; then
    echo "❌ $container: $status (Errors: $errors)"
  else
    echo "✅ $container: $status"
  fi
done
```

---

## Multi-VPS Deployment

### Architecture Pattern

```
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│   VPS 1 (Host)  │  │   VPS 2 (DE)    │  │   VPS 3 (US)    │
│  ┌───────────┐  │  │  ┌───────────┐  │  │  ┌───────────┐  │
│  │ Providers │  │  │  │ Providers │  │  │  │ Providers │  │
│  │ (10 reg)  │  │  │  │ (10 reg)  │  │  │  │ (10 reg)  │  │
│  └───────────┘  │  │  └───────────┘  │  │  └───────────┘  │
│  ┌───────────┐  │  │                 │  │                 │
│  │ Proxied   │  │  │                 │  │                 │
│  │ (10 sock) │  │  │                 │  │                 │
│  └───────────┘  │  │                 │  │                 │
└─────────────────┘  └─────────────────┘  └─────────────────┘
         │                    │                    │
         └────────────────────┴────────────────────┘
                              │
                    Single JWT on each VPS
                    /root/.urnetwork/jwt
```

### Deployment Steps

**1. Prepare JWT on Host VPS:**
```bash
# Host VPS (source of truth)
mkdir -p /root/.urnetwork
echo "<VALID_JWT>" > /root/.urnetwork/jwt
```

**2. Deploy to Remote VPS:**
```bash
VPS_IP="YOURIP"
VPS_USER="YOURuser"
VPS_PASS="YOURpassword"

# Copy JWT to remote
sshpass -p "$VPS_PASS" scp /root/.urnetwork/jwt $VPS_USER@$VPS_IP:/home/$VPS_USER/.urnetwork/jwt

# SSH and create /root/.urnetwork (if needed)
sshpass -p "$VPS_PASS" ssh $VPS_USER@$VPS_IP 'sudo mkdir -p /root/.urnetwork && sudo cp /home/'$VPS_USER'/.urnetwork/jwt /root/.urnetwork/jwt'

# Launch providers on remote
sshpass -p "$VPS_PASS" ssh $VPS_USER@$VPS_IP '
  for i in $(seq 1 10); do
    docker run -d --name urnetwork-provider-vps-$i \
      -v /root/.urnetwork:/root/.urnetwork \
      --restart always \
      bringyour/community-provider:g4-latest provide
  done
'
```

**3. Scale Pattern:**
```bash
# Launch N providers on current host
launch_providers() {
  local count=$1
  local prefix=$2
  for i in $(seq 1 $count); do
    docker run -d --name ${prefix}-$i \
      -v /root/.urnetwork:/root/.urnetwork \
      --restart always \
      bringyour/community-provider:g4-latest provide
  done
}

# Usage
launch_providers 10 "urnetwork-provider"
launch_providers 10 "urnetwork-proxied"
```

---

## Troubleshooting Guide

### 401 Unauthorized Errors

**Symptoms:**
- Container status shows "Restarting"
- Logs contain: `"401 Unauthorized: Not authorized"`
- Provider never stays up for more than a few seconds

**Causes & Fixes:**

| Cause | Fix |
|-------|-----|
| JWT expired | Get fresh auth code from https://ur.io |
| JWT malformed | Re-copy JWT, ensure no extra whitespace |
| Wrong JWT location | Verify mounted at `/root/.urnetwork/jwt` |
| JWT permissions | Ensure readable: `chmod 644 /root/.urnetwork/jwt` |

**Quick Fix:**
```bash
# 1. Get new auth code from https://ur.io
# 2. Exchange for JWT
curl -X POST https://api.bringyour.com/auth/code-login \
  -d '{"auth_code": "YOUR_CODE"}' | jq -r ".by_jwt" > /root/.urnetwork/jwt

# 3. Restart all providers
docker restart $(docker ps -q --filter "name=urnetwork")
```

### Restart Loops

**Check restart count:**
```bash
docker ps --format "table {{.Names}}\t{{.Status}}" | grep urnetwork
```

**Common causes:**

| Pattern | Likely Cause | Solution |
|---------|--------------|----------|
| Restarting every 5-10s | 401 Unauthorized | Refresh JWT |
| Restarting every 30s | Proxy connection issue | Check SOCKS5/Shadowsocks server |
| Up for hours then restart | Network instability | Check `--restart always` is set |

**Debug restart loop:**
```bash
# Watch real-time logs
docker logs -f urnetwork-provider-1

# Check exit code
docker inspect urnetwork-provider-1 --format='{{.State.ExitCode}}'
```

### Proxy Connection Issues (Proxied Providers)

**Symptoms:**
- Shadowsocks logs show connection refused
- Redsocks can't connect to upstream
- Egress IP doesn't match expected proxy IP

**Diagnose:**
```bash
# Test SOCKS5 proxy manually
curl -x socks5://username:password@proxy_ip:port http://ipinfo.io/ip

# Check shadowsocks is listening
docker exec urnetwork-shadowsocks-1 ss -tlnp | grep 1080

# Verify iptables rules (for proxied containers)
docker exec urnetwork-proxied-1 iptables -t nat -L REDSOCKS
```

**Fix proxy config:**
```bash
# Update shadowsocks.json and rebuild
docker build -t urnetwork-shadowsocks:latest .
docker restart urnetwork-shadowsocks-{1..10}
```

### Container Won't Start

**Check:**
```bash
# Port conflicts
docker logs urnetwork-provider-1 2>&1 | grep "bind"

# Mount issues
docker logs urnetwork-provider-1 2>&1 | grep "mount"

# Disk space
df -h

# Docker daemon
docker system info
```

### Mass Operations

**Restart all providers:**
```bash
docker restart $(docker ps -q --filter "name=urnetwork")
```

**Stop all providers:**
```bash
docker stop $(docker ps -q --filter "name=urnetwork")
```

**Remove all providers (destructive):**
```bash
docker rm -f $(docker ps -aq --filter "name=urnetwork")
```

**View all logs:**
```bash
for c in $(docker ps --format "{{.Names}}" | grep urnetwork); do
  echo "=== $c ==="
  docker logs $c 2>&1 | tail -5
done
```

---

**Full docs:** https://docs.ur.io
