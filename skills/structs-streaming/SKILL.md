---
name: structs-streaming
description: Connects to the GRASS real-time event system via NATS WebSocket. Use when you need real-time game updates, want to react to events as they happen, need to monitor raids or attacks, watch for player creation, track fleet movements, or build event-driven tools. GRASS is the fastest way to know what's happening in the galaxy.
---

# Structs Streaming (GRASS)

GRASS (Game Real-time Application Streaming Service) delivers real-time game events over NATS. Instead of polling queries repeatedly, subscribe to GRASS and react to events the moment they happen.

## When to Use GRASS

| Situation | Use GRASS | Use Polling |
|-----------|-----------|-------------|
| Detect incoming raid | Yes — instant alert | Too slow |
| Wait for player creation after guild signup | Yes — listen for `address_register` | Polling every 10s works too |
| Monitor fleet arriving at your planet | Yes — `fleet_arrive` event | Might miss it |
| Track struct health during combat | Yes — `planet_activity` with `struct_health` | Too slow |
| Check your own resource balance | No | Yes — one-off query |
| Read struct type stats | No | Yes — static data |

**Rule of thumb**: If you need to *react* to something, use GRASS. If you need to *read* something, use a query.

---

## Finding Your GRASS Endpoint

The GRASS WebSocket URL is **not hardcoded** — it comes from the guild configuration.

1. Query the guild list: `curl http://reactor.oh.energy:1317/structs/guild`
2. Follow the guild's `endpoint` URL to get its config
3. Look for `services.grass_nats_websocket`

Example (Orbital Hydro guild):

```json
{
  "services": {
    "grass_nats_websocket": "ws://crew.oh.energy:1443",
    "guild_api": "http://crew.oh.energy/api/",
    "reactor_api": "http://reactor.oh.energy:1317/"
  }
}
```

The `grass_nats_websocket` value is your NATS WebSocket endpoint. Not all guilds provide this service — check before relying on it.

A reliable reference endpoint: **`ws://crew.oh.energy:1443`** (Orbital Hydro / Slow Ninja).

---

## Discovery First

Before subscribing to specific subjects, **subscribe to the `>` wildcard** to see all traffic flowing through the GRASS server. This reveals the actual subject patterns in use, which may differ from documentation.

```javascript
const sub = nc.subscribe(">");
for await (const msg of sub) {
  console.log(`[${msg.subject}]`, new TextDecoder().decode(msg.data));
}
```

Watch the output for 30-60 seconds. You will see subjects like `structs.planet.2-1`, `consensus`, `healthcheck`, etc. Once you know what subjects carry the events you need, narrow your subscriptions to those specific subjects.

**Important**: Struct events (attacks, builds, status changes) often arrive on the **planet subject** rather than the struct subject. If you are not receiving expected struct events, subscribe to the struct's planet subject instead.

---

## Subject Patterns

Subscribe to subjects matching the entities you care about:

| Entity | Wildcard | Specific | Example |
|--------|----------|----------|---------|
| Player | `structs.player.*` | `structs.player.{guild_id}.{player_id}` | `structs.player.0-1.1-11` |
| Planet | `structs.planet.*` | `structs.planet.{planet_id}` | `structs.planet.2-1` |
| Guild | `structs.guild.*` | `structs.guild.{guild_id}` | `structs.guild.0-1` |
| Struct | `structs.struct.*` | `structs.struct.{struct_id}` | `structs.struct.5-1` |
| Fleet | `structs.fleet.*` | `structs.fleet.{fleet_id}` | `structs.fleet.9-1` |
| Address | `structs.address.register.*` | `structs.address.register.{code}` | -- |
| Inventory | `structs.inventory.>` | `structs.inventory.{denom}.{guild_id}.{player_id}.{address}` | Token movements |
| Grid | `structs.grid.*` | `structs.grid.{object_id}` | Attribute changes (ore, power, load, etc.) |
| Global | `structs.global` | `structs.global` | Block updates |
| Consensus | `consensus` | `consensus` | Chain consensus events |
| Healthcheck | `healthcheck` | `healthcheck` | Node health status |

Use wildcards (`*`) to discover what events exist. Narrow to specific subjects once you know what you need. Use `>` to see everything (see "Discovery First" above).

---

## Event Types

### Planet Events

| Event | Description | React By |
|-------|-------------|----------|
| `raid_status` | Raid started/completed on planet | Activate defenses, alert |
| `planet_activity` | Activity log including `struct_health` changes | Track combat damage |
| `fleet_arrive` | Fleet arrived at planet | Prepare defense or welcome |
| `fleet_depart` | Fleet left planet | Update threat assessment |

### Struct Events

**Note**: Struct events frequently arrive on the **planet subject** (`structs.planet.{id}`) rather than the struct subject. Subscribe to both if you need complete coverage.

| Event | Description | React By |
|-------|-------------|----------|
| `struct_attack` | Struct was attacked | Counter-attack, repair |
| `struct_status` | Struct status changed (online/offline/destroyed) | Rebuild, reallocate power |
| `struct_defense_add` / `struct_defense_remove` | Defense assignments changed | Update defense map |
| `struct_defender_clear` | All defense relationships cleared | Re-assign defenders |
| `struct_block_build_start` | Build operation initiated | Track in job list |
| `struct_block_ore_mine_start` | Mine operation initiated | Track in job list |
| `struct_block_ore_refine_start` | Refine operation initiated | Track in job list |

### Player Events

| Event | Description | React By |
|-------|-------------|----------|
| `player_consensus` | Player chain data updated | Update intel |
| `player_meta` | Player metadata changed | Update intel |

### Guild Events

| Event | Description | React By |
|-------|-------------|----------|
| `guild_consensus` | Guild chain data updated | Update guild status |
| `guild_membership` | Member joined/left guild | Update relationship map |

### Inventory Events

Subject: `structs.inventory.{denom}.{guild_id}.{player_id}.{address}`

Track token movements — Alpha Matter, guild tokens, ore, etc.

| Category | Description | React By |
|----------|-------------|----------|
| `sent` | Tokens sent from this player | Update balance tracking |
| `received` | Tokens received by this player | Update balance tracking |
| `seized` | Tokens seized via raid | Trigger counter-raid or refine alert |
| `mined` | Ore mined | Start refining immediately |
| `refined` | Ore refined into Alpha | Update wealth tracking |
| `minted` | Guild tokens minted | Track guild economy |
| `infused` | Alpha infused into reactor/generator | Update capacity tracking |
| `forfeited` | Tokens lost (penalties, etc.) | Investigate cause |

### Grid Events

Subject: `structs.grid.{object_id}`

Track attribute changes on any game object (players, structs, planets).

| Category | Description | React By |
|----------|-------------|----------|
| `capacity` | Power capacity changed | Check if approaching offline |
| `connectionCapacity` | Connection capacity changed | Update power routing |
| `connectionCount` | Connection count changed | Update power routing |
| `fuel` | Fuel level changed | Monitor generator/reactor |
| `lastAction` | Last action timestamp updated | Track activity |
| `load` | Power load changed | Check if approaching offline |
| `nonce` | Player nonce incremented | Detect activity (useful for scouting) |
| `ore` | Ore balance changed | **Refine immediately** if yours; raid target if theirs |
| `player_consensus` | Player consensus data updated | Update intel |
| `power` | Power level changed | Monitor energy infrastructure |
| `proxyNonce` | Proxy nonce changed | Detect proxy activity |
| `structsLoad` | Structs load changed | Assess fleet strength changes |

### Combat Event Payloads

`struct_attack` events include detailed shot-by-shot resolution. Example payload (observed on planet subject):

```json
{
  "category": "struct_attack",
  "attackingStructId": "5-100",
  "targetStructId": "5-200",
  "weaponSystem": "primary",
  "eventAttackShotDetail": [
    {
      "shotIndex": 0,
      "damage": 2,
      "evaded": false,
      "blocked": false,
      "blockerStructId": "",
      "counterAttackDamage": 1,
      "counterAttackerStructId": "5-200"
    }
  ],
  "attackerHealthRemaining": 2,
  "targetHealthRemaining": 1,
  "targetDestroyed": false,
  "attackerDestroyed": false
}
```

Key fields in `eventAttackShotDetail`:
- `evaded` -- true if the shot missed (defense type interaction)
- `blocked` -- true if a defender intercepted
- `blockerStructId` -- which struct blocked (if any)
- `counterAttackDamage` / `counterAttackerStructId` -- counter-attack info per shot

`struct_health` events track HP changes:

```json
{
  "category": "struct_health",
  "structId": "5-200",
  "health": 1,
  "maxHealth": 3,
  "destroyed": false
}
```

### Noise Filtering

The `consensus` and `healthcheck` subjects fire constantly (every few seconds). When using the `>` wildcard for discovery, filter these out to see actual game events:

```javascript
const sub = nc.subscribe(">");
for await (const msg of sub) {
  if (msg.subject === "consensus" || msg.subject === "healthcheck") continue;
  console.log(`[${msg.subject}]`, new TextDecoder().decode(msg.data));
}
```

### Global Events

| Event | Description | React By |
|-------|-------------|----------|
| `block` | New block produced | Tick game loop, update charge calculations |

---

## Building Event Listener Tools

Agents should build custom tools that connect to GRASS when they need event-driven behavior. Here are patterns to follow.

### Minimal Node.js Listener

Install the NATS WebSocket client:

```bash
npm install nats.ws
```

```javascript
import { connect } from "nats.ws";

const nc = await connect({ servers: "ws://crew.oh.energy:1443" });

const sub = nc.subscribe("structs.planet.2-1");
for await (const msg of sub) {
  const event = JSON.parse(new TextDecoder().decode(msg.data));
  console.log(JSON.stringify(event));
}
```

### Minimal Python Listener

Install the NATS client:

```bash
pip install nats-py
```

```python
import asyncio, json, nats

async def main():
    nc = await nats.connect("ws://crew.oh.energy:1443")
    sub = await nc.subscribe("structs.planet.2-1")
    async for msg in sub.messages:
        event = json.loads(msg.data.decode())
        print(json.dumps(event))

asyncio.run(main())
```

### Raid Alert Tool (example pattern)

A tool that watches for raids on your planet and outputs an alert:

```javascript
import { connect } from "nats.ws";

const PLANET_ID = process.argv[2]; // e.g. "2-1"
const nc = await connect({ servers: "ws://crew.oh.energy:1443" });
const sub = nc.subscribe(`structs.planet.${PLANET_ID}`);

for await (const msg of sub) {
  const event = JSON.parse(new TextDecoder().decode(msg.data));
  if (event.category === "raid_status") {
    console.log(JSON.stringify({ alert: "RAID", planet: PLANET_ID, data: event }));
  }
  if (event.category === "fleet_arrive") {
    console.log(JSON.stringify({ alert: "FLEET_ARRIVAL", planet: PLANET_ID, data: event }));
  }
}
```

### Player Creation Watcher (example pattern)

Instead of polling `structsd query structs address` after guild signup, watch for the address registration event:

```javascript
import { connect } from "nats.ws";

const nc = await connect({ servers: "ws://crew.oh.energy:1443" });
const sub = nc.subscribe("structs.address.register.*");

for await (const msg of sub) {
  const event = JSON.parse(new TextDecoder().decode(msg.data));
  console.log(JSON.stringify(event));
  break; // exit after first match
}
await nc.close();
```

---

## When to Build a Custom Tool

Build a GRASS listener tool when:

- **You need to wait for an event** — guild signup completion, fleet arrival, raid detection
- **You need continuous monitoring** — threat detection during vulnerable ore window, combat tracking
- **You want an event-driven game loop** — react to block events instead of polling on a timer
- **You're managing multiple players** — one GRASS connection can monitor all your entities simultaneously

Store custom tools in your workspace (e.g., `scripts/` or alongside the relevant skill).

---

## Connection Best Practices

- **Use specific subjects** once you know what you need. Wildcards are for discovery.
- **Limit to 10-20 subscriptions** per connection to avoid overwhelming the client.
- **Implement reconnection** with exponential backoff — NATS connections can drop.
- **Parse JSON defensively** — not all messages may match expected schema.
- **Close connections** when done. Don't leave idle GRASS connections open.

---

## Procedure

### Quick Setup

1. Get the GRASS endpoint from your guild config (or use `ws://crew.oh.energy:1443`)
2. Record the endpoint in [TOOLS.md](https://structs.ai/TOOLS) under Servers
3. Choose your language (Node.js or Python)
4. Install the NATS client library (`nats.ws` for Node, `nats-py` for Python)
5. Write a listener script for your specific use case
6. Run it in a background terminal

### For Ongoing Monitoring

1. Subscribe to your planet(s): `structs.planet.{id}` — raid alerts, fleet arrivals
2. Subscribe to your structs: `structs.struct.{id}` — attack/status alerts
3. Subscribe to global: `structs.global` — block tick for game loop timing
4. Log events to [memory/](https://structs.ai/memory) for cross-session awareness

---

## Automation Patterns (Defence Contractor)

The Structs permission system and GRASS event stream were designed for AI agents to automate game responses. The design docs call this the "Defence Contractor" pattern — an agent that monitors events and acts on behalf of players within scoped permissions.

### Common Automation Triggers

| Event | Action | Permission Needed |
|-------|--------|-------------------|
| `struct_ore_mine_complete` on your extractor | Immediately start `struct-ore-refine-compute` | Signer key for the player |
| `struct_ore_refine_complete` on your refinery | Immediately start next `struct-ore-mine-compute` | Signer key for the player |
| `planet_raid_start` on your planet | Alert, activate stealth, reposition defenders | Signer key or delegated permission |
| `struct_attack` targeting your struct | Log attacker, assess threat, counter-attack if able | Signer key or delegated permission |
| `struct_health` showing HP drop | Prioritize defense, consider fleet retreat | Signer key for fleet-move |
| `fleet_move` to your planet from unknown fleet | Identify incoming player, assess threat level | Read-only (query) |

### Permission Scoping for Automated Agents

When delegating actions to an automation agent (separate key or service):

1. **Grant minimal permissions**: Use `permission-grant-on-object` to allow specific actions on specific structs, not blanket access.
2. **Separate keys**: The automation agent should use its own signing key, registered as a secondary address on the player via `address-register`.
3. **Scope by struct**: Grant mine/refine permissions on extractors and refineries only. Grant defense permissions on fleet structs only.
4. **Revoke when not needed**: Use `permission-revoke-on-object` to remove automation access during sensitive operations.

### Example: Refine-on-Mine-Complete Loop

```
Subscribe to: structs.struct.{extractor-id}
On event: struct_ore_mine_complete
  → Run: structsd tx structs struct-ore-refine-compute -D 1 --from [key] --gas auto -y -- [refinery-id]

Subscribe to: structs.struct.{refinery-id}
On event: struct_ore_refine_complete
  → Run: structsd tx structs struct-ore-mine-compute -D 1 --from [key] --gas auto -y -- [extractor-id]
```

This creates a continuous mine-refine loop that runs unattended. Ore is never left unrefined.

### Example: Defend-on-Raid-Detected

```
Subscribe to: structs.planet.{planet-id}
On event: planet_raid_start
  → Activate stealth on vulnerable structs
  → Set defenders on high-value structs
  → Log raid to memory/intel/threats.md
  → Alert commander if available
```

### Safe Boundaries

- **Never auto-spend Alpha** without commander approval (infusion, guild-bank operations)
- **Never auto-move fleets** away from defended planets without threat assessment
- **Always log actions** to `memory/` for cross-session audit trail
- **Rate-limit reactions** — one transaction per ~6 seconds per key (sequence number constraint)

---

## See Also

- [protocols/streaming](https://structs.ai/protocols/streaming) — Full GRASS/NATS protocol specification
- [api/streaming/event-types](https://structs.ai/api/streaming/event-types) — Complete event type catalog
- [api/streaming/event-schemas](https://structs.ai/api/streaming/event-schemas) — JSON schema definitions for event payloads
- [api/streaming/subscription-patterns](https://structs.ai/api/streaming/subscription-patterns) — Subscription patterns and examples
- [awareness/async-operations](https://structs.ai/awareness/async-operations) — Background operations and pipeline strategy
- [awareness/threat-detection](https://structs.ai/awareness/threat-detection) — Using GRASS for early warning
