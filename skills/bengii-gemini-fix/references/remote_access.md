# Remote Access Reference

Remote access patterns for OpenClaw: SSH tunnels, VPNs, and Tailscale.

## The Core Idea

OpenClaw's Gateway binds to loopback by default. To access it from another machine, you need either a tunnel (SSH), a VPN/tailnet (Tailscale), or explicit network binding.

## Common VPN/Tailnet Setups

### 1) Always-On Gateway in Your Tailnet (VPS or Home Server)

The Gateway runs on a VPS or home server joined to your Tailscale tailnet. Access from any device on the tailnet.

### 2) Home Desktop Runs the Gateway, Laptop is Remote Control

Desktop runs the Gateway. Laptop connects via Tailscale or SSH tunnel.

### 3) Laptop Runs the Gateway, Remote Access from Other Machines

Laptop runs the Gateway. Access from other machines via tunnel or tailnet.

## Command Flow (What Runs Where)

- **Gateway host**: Runs the Gateway daemon, serves channels, tools, and sessions.
- **Remote client**: Runs CLI commands or the Control UI, connecting to the Gateway via WebSocket.

## SSH Tunnel (CLI + Tools)

```bash
# Forward the Gateway port to your local machine
ssh -N -L 18789:127.0.0.1:18789 user@host
```

Then access the Gateway at `http://127.0.0.1:18789` locally.

## CLI Remote Defaults

```bash
# Set remote Gateway URL for CLI
export OPENCLAW_GATEWAY_URL=ws://host:18789
export OPENCLAW_GATEWAY_TOKEN=your-token
```

## Credential Precedence

1. CLI `--gateway-url` / `--gateway-token` flags
2. Environment variables (`OPENCLAW_GATEWAY_URL`, `OPENCLAW_GATEWAY_TOKEN`)
3. Config file `gateway.url` / `gateway.auth.token`

## Chat UI over SSH

Access the Control UI via SSH tunnel for the web dashboard.

## macOS App "Remote over SSH"

The macOS OpenClaw app supports remote SSH connections for accessing a Gateway on another machine.

## Security Rules (Remote/VPN)

- Always use auth (`gateway.auth.token` or `gateway.auth.password`) when exposing non-loopback.
- Prefer Tailscale or VPN over SSH port forwarding.
- Never expose the Gateway to the public internet without auth.

---

# Tailscale (Gateway Dashboard)

Tailscale provides zero-config VPN access to your OpenClaw Gateway.

## Modes

- **Tailnet-only (Serve)**: Expose the Gateway to your Tailscale tailnet only.
- **Tailnet-only (bind to Tailnet IP)**: Bind the Gateway to your Tailscale IP.
- **Public internet (Funnel)**: Expose the Gateway to the public internet via Tailscale Funnel.

## Auth

- Tailscale provides identity headers for authentication.
- See `gateway.auth.tailscaleIdentityHeaders` for config.

## Config Examples

### Tailnet-Only (Serve)

Use `tailscale serve` to expose the Gateway to your tailnet:

```bash
tailscale serve --bg https://127.0.0.1:18789
```

### Tailnet-Only (Bind to Tailnet IP)

```json5
{
  gateway: {
    bind: "tailnet",
    auth: {
      mode: "token",
      token: "your-token",
    },
  },
}
```

### Public Internet (Funnel + Shared Password)

```json5
{
  gateway: {
    bind: "tailnet",
    auth: {
      mode: "password",
      password: "your-password",
    },
  },
}
```

Then:

```bash
tailscale funnel --bg https://127.0.0.1:18789
```

## CLI Examples

```bash
openclaw gateway --bind tailnet
openclaw gateway --bind auto
```

## Notes

- Tailscale Serve/Funnel requires Tailscale v1.50+.
- Funnel traffic is end-to-end encrypted.
- Use `gateway.auth` with Tailscale for an additional security layer.

## Browser Control (Remote Gateway + Local Browser)

When the Gateway is remote but you want browser control on the local machine, use node browser proxy or set up a remote CDP endpoint.

## Tailscale Prerequisites + Limits

- Tailscale must be installed and logged in on both the Gateway host and client.
- Tailscale free tier supports up to 100 devices.

---

# Web (Gateway Surfaces)

The Gateway serves a web dashboard (Control UI) and supports WebChat and webhooks.

## Control UI

Default: `http://127.0.0.1:18789/`

Features:
- Chat interface (WebChat)
- Configuration editor
- Session management
- Skills management
- Plugin management

## Webhooks

External systems can send messages to the Gateway via webhooks.

## Config (Default-On)

```json5
{
  web: {
    enabled: true,    // default: true
  },
}
```

## Tailscale Access

### Integrated Serve (Recommended)

```bash
tailscale serve --bg https://127.0.0.1:18789
```

### Tailnet Bind + Token

```json5
{
  gateway: {
    bind: "tailnet",
    auth: { mode: "token", token: "your-token" },
  },
}
```

### Public Internet (Funnel)

```bash
tailscale funnel --bg https://127.0.0.1:18789
```

## Security Notes

- The Control UI has full access to the Gateway (config, sessions, tools).
- Always use auth when exposing non-loopback.
- HTTPS is recommended for non-local access.

## Building the UI

The Control UI is built into the Gateway and served at the root URL. No separate build step is needed.
