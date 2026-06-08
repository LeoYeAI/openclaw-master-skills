# OpenClaw Web Surfaces Reference (Dashboard, Control UI, WebChat)

## Table of Contents

- [Overview](#overview)
- [Dashboard (Control UI)](#dashboard-control-ui)
- [WebChat](#webchat)
- [Tailscale Access](#tailscale-access)
- [Building the UI](#building-the-ui)
- [Configuration](#configuration)

## Overview

OpenClaw serves web surfaces from the Gateway. Three main surfaces:

| Surface | URL | Purpose |
|---|---|---|
| Dashboard | `http://127.0.0.1:18789/` | Main control interface |
| Control UI | Same as dashboard | Full chat + configuration |
| WebChat | Embedded in Control UI | Direct chat with agent |

```bash
# Open in browser
openclaw dashboard
```

## Dashboard (Control UI)

### Quick Open

```bash
openclaw dashboard         # Opens http://127.0.0.1:18789/ in browser
```

For local Gateway on default port, the dashboard is available without authentication.

### Token Basics (Local vs Remote)

| Scenario | Auth Required |
|---|---|
| Local (127.0.0.1) | No (loopback exempt) |
| Remote / Tailscale | Yes (gateway.auth.token or .password) |

### Device Pairing (First Connection)

When accessing the Control UI for the first time:
1. The UI shows a pairing challenge
2. Confirm on the gateway host (CLI or notification)
3. Once paired, the browser remembers the device

### Capabilities

The Control UI can:
- Chat with your agent (WebChat)
- View and manage sessions
- Configure agent settings
- View connected channels and their status
- Manage tools and skills
- View cron jobs and automation
- Monitor gateway health
- Manage nodes and devices

### Chat Behavior

- Messages typed in WebChat are processed as regular chat turns
- Slash commands work (e.g., `/new`, `/status`, `/model`)
- Media attachments supported
- Streaming responses displayed in real-time

### Unauthorized / 1008 Errors

If you see "unauthorized" or WebSocket close code 1008:
1. Check `gateway.auth.token` matches what the UI is sending
2. Try clearing browser storage and re-pairing
3. Verify Gateway is running: `openclaw gateway status`

## WebChat

WebChat is a Gateway WebSocket UI for direct agent interaction.

### What It Is

A browser-based chat interface that connects to the Gateway via WebSocket. No external services required — everything runs locally.

### Quick Start

```bash
openclaw dashboard    # Opens the Control UI with WebChat
```

Or navigate to `http://127.0.0.1:18789/` in your browser.

### Behavior

- Uses the Gateway's WebSocket protocol (JSON text frames)
- Messages are processed as regular agent turns
- Supports streaming responses
- Supports media (images, audio, documents)
- Slash commands work

### Control UI Agents Tools Panel

The Control UI includes an agents/tools panel for managing:
- Active tools and their settings
- Skills configuration
- Agent profiles

### Remote Use

For remote access, configure Tailscale Serve or SSH tunnels:

```json5
{
  gateway: {
    tailscale: {
      serve: { enabled: true },
    },
  },
}
```

### WebChat Configuration

```json5
{
  gateway: {
    webchat: {
      enabled: true,        // Default: true
    },
  },
}
```

## Tailscale Access

### Integrated Tailscale Serve (Recommended)

```json5
{
  gateway: {
    tailscale: {
      serve: {
        enabled: true,
        // hostname: "my-openclaw",  // Optional custom hostname
      },
    },
  },
}
```

Exposes the Gateway over HTTPS on your tailnet with automatic TLS.

### Tailnet Bind + Token

For non-Serve setups, bind directly to your tailnet IP:

```json5
{
  gateway: {
    bind: "100.x.y.z",        // Tailnet IP
    auth: {
      token: "your-token",    // Required for non-loopback
    },
  },
}
```

### Public Internet (Funnel)

⚠️ Not recommended for most users. Only if you need public access:

```json5
{
  gateway: {
    tailscale: {
      funnel: { enabled: true },
    },
  },
}
```

## Building the UI

If building from source:

```bash
pnpm ui:build    # Build the Control UI
```

The built UI is served by the Gateway's HTTP server.

## Configuration

```json5
{
  gateway: {
    // Web surfaces (default on)
    webchat: { enabled: true },
    
    // Webhooks
    webhooks: { enabled: true },
    
    // Tailscale
    tailscale: {
      serve: { enabled: true },
    },
  },
}
```

### Security Notes

- Local loopback access is exempt from auth
- Remote access always requires `gateway.auth.token` or `gateway.auth.password`
- Use Tailscale Serve for secure remote access (automatic TLS)
- Avoid exposing Gateway directly to the public internet
- Control UI inherits agent permissions — anyone with access can interact as the agent
