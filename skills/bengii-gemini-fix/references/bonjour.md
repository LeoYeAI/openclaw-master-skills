# Bonjour / mDNS Discovery Reference

> Source: https://docs.openclaw.ai/gateway/bonjour

## Overview

OpenClaw uses Bonjour (mDNS/DNS-SD) to let companion apps (macOS, iOS, Android) discover the Gateway on the LAN automatically. The Gateway advertises a `_openclaw-gw._tcp` service.

## Service Types

| Service | Purpose |
|---|---|
| `_openclaw-gw._tcp` | Gateway transport beacon (used by macOS/iOS/Android nodes) |

## TXT Keys (Non-Secret Hints)

| Key | Value | Notes |
|---|---|---|
| `role` | `gateway` | Always |
| `displayName` | `<friendly name>` | Human-readable |
| `lanHost` | `<hostname>.local` | LAN hostname |
| `gatewayPort` | `<port>` | Gateway WS + HTTP port |
| `gatewayTls` | `1` | Only when TLS enabled |
| `gatewayTlsSha256` | `<sha256>` | Only when TLS + fingerprint available |
| `canvasPort` | `<port>` | Currently same as gatewayPort |
| `sshPort` | `<port>` | Default 22 |
| `transport` | `gateway` | Always |
| `cliPath` | `<path>` | Optional: abs path to openclaw |
| `tailnetDns` | `<magicdns>` | Optional: when Tailnet available |

### Security Notes
- TXT records are **unauthenticated**. Clients must not treat TXT as authoritative routing.
- Route using resolved SRV + A/AAAA records. Treat `lanHost`, `tailnetDns`, `gatewayPort`, `gatewayTlsSha256` as **hints only**.
- TLS pinning must never allow advertised `gatewayTlsSha256` to override a previously stored pin.
- iOS/Android nodes should treat discovery-based connects as TLS-only with user confirmation for first-time fingerprints.

## Wide-Area Bonjour (Unicast DNS-SD over Tailscale)

For cross-network discovery (beyond LAN):

1. Run a DNS server on the gateway host (reachable over Tailnet).
2. Publish DNS-SD records under a dedicated zone (e.g., `openclaw.internal.`).
3. Configure Tailscale split DNS to resolve via that DNS server.

### Gateway Config (Recommended)
```json5
{
  gateway: {
    bonjour: {
      domain: "openclaw.internal.",  // zone for wide-area DNS-SD
    },
  },
}
```

## Debugging

### On macOS
```bash
# Browse instances
dns-sd -B _openclaw-gw._tcp local.

# Resolve one instance
dns-sd -L "<instance>" _openclaw-gw._tcp local.
```

### In Gateway Logs
Filter log file for `bonjour:`:
- `bonjour: advertise failed ...`
- `bonjour: ... name conflict resolved`
- `bonjour: watchdog detected non-announced service ...`

### On iOS Node
- Settings → Gateway → Advanced → Discovery Debug Logs
- Settings → Gateway → Advanced → Discovery Logs → reproduce → Copy

## Common Failure Modes

| Problem | Cause | Fix |
|---|---|---|
| Bonjour doesn't work across networks | mDNS is LAN-only | Use Tailnet or SSH |
| Multicast blocked | Some Wi-Fi networks disable mDNS | Switch network or use SSH |
| Sleep / interface churn | macOS may temporarily drop mDNS results | Retry or restart Gateway |
| Browse works but resolve fails | Complex machine names (emojis/punctuation) | Simplify hostname, restart Gateway |
| Escaped `\032` in names | Normal RFC encoding for spaces | UIs decode (iOS: `BonjourEscapes.decode`) |

## Disabling / Configuration

```json5
{
  gateway: {
    bonjour: {
      enabled: false,  // disable entirely
    },
  },
}
```

## See Also

- [presence_discovery.md](presence_discovery.md) — Overview of presence + discovery
- [remote_access.md](remote_access.md) — SSH, Tailscale remote access
- [gateway_internals.md](gateway_internals.md) — Network model
