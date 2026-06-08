# Presence & Discovery

> Sources:
> - https://docs.openclaw.ai/concepts/presence
> - https://docs.openclaw.ai/gateway/discovery
> - https://docs.openclaw.ai/gateway/bonjour

## Presence

### Presence Fields

Each presence entry contains information about a connected client, node, or the gateway itself.

### Producers (Where Presence Comes From)

1. **Gateway self entry**: Gateway publishes its own presence on start.
2. **WebSocket connect**: Each WS client registers presence on connect.
3. **system-event beacons**: Periodic beacons from clients.
4. **Node connects (`role: node`)**: Nodes register with device info and capabilities.

### Merge + Dedupe Rules

- `instanceId` is the dedup key to prevent duplicate entries.
- Multiple connections from the same instance are merged.

### TTL and Bounded Size

- Entries have a configurable TTL and are pruned when expired.
- Max entries are bounded to prevent memory issues.

### Consumers

- macOS app Instances tab shows connected clients.
- Control UI shows connected clients and nodes.
- CLI: `openclaw system presence`.

---

## Discovery & Transports

### Discovery Inputs

How clients learn where the Gateway is:

#### 1. Bonjour / mDNS (LAN Only)

- Gateway advertises itself on the local network via Bonjour/mDNS.
- macOS and iOS clients auto-discover Gateway on the same LAN.

#### 2. Tailnet (Cross-Network)

- Gateway registers with Tailscale for cross-network access.
- Clients discover Gateway via Tailscale MagicDNS.

#### 3. Manual / SSH Target

- Users manually configure the Gateway address.
- SSH tunnel can be used as transport.

### Transport Selection (Client Policy)

- Clients choose between direct WS and SSH-tunneled WS.
- Direct is preferred when available (LAN/Tailnet).
- SSH fallback for remote access without Tailscale.

### Pairing + Auth (Direct Transport)

- All transports require the standard WS handshake.
- Auth tokens apply regardless of transport type.

### Responsibilities by Component

| Component | Responsibility |
|---|---|
| Gateway | Advertise via Bonjour, accept WS connections |
| macOS App | Discover via Bonjour/Tailnet, connect via WS |
| iOS App | Discover via Bonjour, connect via WS |
| CLI | Manual config, connect via WS |
