# Deployment Reference: OpenClaw + n8n

Detailed deployment topologies, Docker Compose templates, and infrastructure configuration.

---

## Table of Contents

1. [Co-located Docker Stack](#co-located-docker-stack)
2. [Standalone + External n8n](#standalone-external-n8n)
3. [Managed Platform Convergence](#managed-platform-convergence)
4. [Distributed Remote Access (Tunneling)](#distributed-remote-access)
5. [Environment Variables Reference](#environment-variables)
6. [Network Security Checklist](#network-security-checklist)

---

## Prerequisites

- **Node.js 22+** — required for all OpenClaw installations
- **Docker** — recommended for production deployment
- OpenClaw installed via `npm install -g openclaw@latest` or `curl -fsSL https://openclaw.ai/install.sh | bash`
- Windows users: use WSL (native PowerShell is unstable per core maintainers)

## Co-located Docker Stack

Both OpenClaw and n8n share a Docker network. Internal communication on private ports with no public exposure.

### Docker Compose Template

```yaml
version: "3.8"

services:
  openclaw:
    image: openclaw/openclaw:latest
    container_name: openclaw-agent
    restart: unless-stopped
    ports:
      - "127.0.0.1:18789:18789"  # Gateway — localhost only!
    volumes:
      - openclaw-data:/app/workspace
      - ./openclaw.json:/app/openclaw.json:ro
    environment:
      - OPENCLAW_GATEWAY_TOKEN=${GATEWAY_TOKEN}
      - OPENCLAW_DEFAULT_MODEL=${DEFAULT_MODEL:-claude-sonnet-4-20250514}
    networks:
      - openclaw-n8n

  n8n:
    image: docker.n8n.io/n8nio/n8n:latest
    container_name: n8n-orchestrator
    restart: unless-stopped
    ports:
      - "127.0.0.1:5678:5678"  # n8n UI — localhost only!
    volumes:
      - n8n-data:/home/node/.n8n
    environment:
      - N8N_ENCRYPTION_KEY=${N8N_ENCRYPTION_KEY}
      - WEBHOOK_URL=http://n8n:5678
      - N8N_DEFAULT_BINARY_DATA_MODE=filesystem
      - EXECUTIONS_DATA_PRUNE=true
      - EXECUTIONS_DATA_MAX_AGE=168
      - GENERIC_TIMEZONE=${TIMEZONE:-America/New_York}
    networks:
      - openclaw-n8n

volumes:
  openclaw-data:
  n8n-data:

networks:
  openclaw-n8n:
    driver: bridge
    internal: false  # Set to true if no external access needed
```

### Key Configuration Notes

**Internal DNS Resolution**: Within the Docker network, services reference each other by container name. OpenClaw reaches n8n at `http://n8n:5678/webhook/...` and n8n reaches the Gateway at `http://openclaw-agent:18789/v1/responses`.

**Port Binding**: Both services bind to `127.0.0.1` only. This prevents external network access. Use a reverse proxy (Traefik/Nginx) for any external access requirements.

**The `.env` file** for the above compose template:

```env
# Generate these values before first run
GATEWAY_TOKEN=<openssl rand -hex 32>
N8N_ENCRYPTION_KEY=<openssl rand -hex 32>
TIMEZONE=America/New_York
DEFAULT_MODEL=claude-sonnet-4-20250514

# If using Anthropic API directly
ANTHROPIC_API_KEY=sk-ant-...
```

**Critical**: Back up `N8N_ENCRYPTION_KEY` securely. If lost, all API credentials stored in n8n become permanently inaccessible.

### openclaw.json for Co-located Mode

```json
{
  "gateway": {
    "host": "0.0.0.0",
    "port": 18789,
    "auth": {
      "mode": "token",
      "token": "${OPENCLAW_GATEWAY_TOKEN}"
    },
    "http": {
      "endpoints": {
        "responses": {
          "enabled": true
        }
      }
    }
  }
}
```

---

## Standalone + External n8n

OpenClaw runs on local hardware (Mac Mini, workstation, homelab server). n8n runs on a cloud VPS or managed platform.

### Architecture Diagram

```
┌────────────────────┐          HTTPS          ┌────────────────────┐
│  Local Machine     │ ──────────────────────▶ │  Cloud VPS         │
│                    │    Egress (webhook)      │                    │
│  OpenClaw Agent    │                          │  n8n Instance      │
│  Gateway :18789    │ ◀────────────────────── │  :5678 (proxied)   │
│  (localhost only)  │    Ingress (tunnel)      │  SSL via Nginx     │
└────────────────────┘                          └────────────────────┘
        │                                               │
        └───────── SSH Tunnel / WireGuard ──────────────┘
```

### n8n Cloud VPS Setup

Standard n8n Docker deployment on the VPS with Nginx reverse proxy and Let's Encrypt SSL:

```yaml
# docker-compose.yml on cloud VPS
version: "3.8"

services:
  n8n:
    image: docker.n8n.io/n8nio/n8n:latest
    restart: unless-stopped
    ports:
      - "127.0.0.1:5678:5678"
    volumes:
      - n8n-data:/home/node/.n8n
    environment:
      - N8N_ENCRYPTION_KEY=${N8N_ENCRYPTION_KEY}
      - WEBHOOK_URL=https://n8n.yourdomain.com
      - N8N_DEFAULT_BINARY_DATA_MODE=filesystem
      - EXECUTIONS_DATA_PRUNE=true
      - GENERIC_TIMEZONE=${TIMEZONE}

  nginx:
    image: nginx:alpine
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/conf.d/default.conf:ro
      - certbot-data:/etc/letsencrypt:ro

volumes:
  n8n-data:
  certbot-data:
```

### Secure Tunnel for Ingress

The Gateway must **never** be exposed to the public internet. For n8n to push data back to OpenClaw:

**Option A: SSH Tunnel** (simplest)
```bash
# From the cloud VPS, tunnel to local machine's Gateway
ssh -R 18789:127.0.0.1:18789 user@local-machine-ip -N

# n8n HTTP Request node targets: http://127.0.0.1:18789/v1/responses
```

**Option B: WireGuard/Tailscale** (persistent, survives reboots)
```bash
# After Tailscale setup on both machines:
# n8n HTTP Request node targets: http://<tailscale-ip>:18789/v1/responses
```

**Option C: Cloudflare Tunnel** (zero-config, no port forwarding)
```bash
cloudflared tunnel --url http://localhost:18789 --name openclaw-gateway
# n8n targets the generated Cloudflare tunnel URL
```

---

## Managed Platform Convergence

For organizations without dedicated DevOps. Managed providers handle SSL, backups, and version updates.

### xCloud
- Managed OpenClaw instances with n8n integration
- Automatic SSL provisioning
- Both services co-located on managed infrastructure
- Webhook communication via internal network

### Tencent Cloud (Enterprise Scale)
- User queries via web forms trigger webhooks
- Tencent Serverless Cloud Functions (SCF) + API Gateway as intermediary
- SCF sanitizes payloads and manages burst rate-limiting
- Forwards to n8n, which queries OpenClaw agent
- Responses delivered via enterprise email gateways

This topology adds a serverless sanitization layer between the public internet and the agent, suitable for regulated environments.

---

## Distributed Remote Access

### Zero-Trust Mesh Networks

For persistent, team-wide access that survives reboots:

```bash
# Install Tailscale on both OpenClaw host and n8n host
curl -fsSL https://tailscale.com/install.sh | sh
tailscale up

# OpenClaw Gateway stays bound to localhost
# n8n references the Tailscale IP for ingress:
# http://100.x.x.x:18789/v1/responses
```

### SSH Tunnel with Autossh (Persistent)

```bash
# Install autossh for automatic reconnection
apt install autossh

# Create persistent tunnel
autossh -M 0 -f -N \
  -R 18789:127.0.0.1:18789 \
  -o "ServerAliveInterval=30" \
  -o "ServerAliveCountMax=3" \
  user@vps-ip
```

---

## Environment Variables

### OpenClaw Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENCLAW_GATEWAY_TOKEN` | Yes (if auth mode = token) | Bearer token for Gateway API authentication |
| `OPENCLAW_DEFAULT_MODEL` | No | Default LLM model identifier |
| `OPENCLAW_GATEWAY_HOST` | No | Gateway bind address (default: `127.0.0.1`) |
| `OPENCLAW_GATEWAY_PORT` | No | Gateway port (default: `18789`) |
| `ANTHROPIC_API_KEY` | Yes (if using Claude) | Anthropic API key for the cognitive engine |

### n8n Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `N8N_ENCRYPTION_KEY` | **Critical** | Encrypts all stored credentials. Back up immediately. |
| `WEBHOOK_URL` | Yes | Public-facing URL for OAuth callbacks and webhook triggers |
| `N8N_DEFAULT_BINARY_DATA_MODE` | Recommended | Set to `filesystem` for production (prevents RAM exhaustion) |
| `EXECUTIONS_DATA_PRUNE` | Recommended | Set to `true` to auto-delete old execution logs |
| `EXECUTIONS_DATA_MAX_AGE` | Optional | Hours to retain execution data (default: 168 = 7 days) |
| `GENERIC_TIMEZONE` | Recommended | Default timezone for scheduled workflows |
| `NODES_EXCLUDE` | Optional | Comma-separated list of disabled node types (security hardening) |

### Shared Variables

| Variable | Purpose |
|----------|---------|
| `WEBHOOK_SECRET` | Shared secret for x-webhook-secret header authentication between OpenClaw skills and n8n webhook nodes |

---

## Network Security Checklist

### Before Going Live

- [ ] Gateway bound to `127.0.0.1` only (never `0.0.0.0` on public interfaces)
- [ ] n8n behind reverse proxy with SSL termination
- [ ] `N8N_ENCRYPTION_KEY` generated and backed up to secure vault
- [ ] `OPENCLAW_GATEWAY_TOKEN` generated with sufficient entropy (`openssl rand -hex 32`)
- [ ] Webhook secret shared only between OpenClaw skill files and n8n credentials
- [ ] SSH tunnel or zero-trust mesh established for cross-network ingress
- [ ] n8n `NODES_EXCLUDE` configured to disable `Execute Command` node if shell access not needed
- [ ] Firewall rules: only webhook ports (443 via proxy) exposed publicly
- [ ] Docker network set to `internal: true` if no external API calls needed from containers
- [ ] NTP synchronized across all hosts (prevents `DEVICE_AUTH_SIGNATURE_EXPIRED` errors)

### Ongoing Operations

- [ ] Monitor n8n execution logs for failed webhook authentications
- [ ] Rotate `WEBHOOK_SECRET` and `GATEWAY_TOKEN` quarterly
- [ ] Prune n8n execution history (`EXECUTIONS_DATA_PRUNE=true`)
- [ ] Review OpenClaw skill directory for unauthorized `.mmd` files
- [ ] Audit n8n workflow locks — ensure agent cannot modify locked workflows
