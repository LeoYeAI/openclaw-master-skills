# Arista EOS CLI Reference

Commands organized by subsystem. All commands are read-only (show only). Validated
against EOS 4.30+. Linux-native alternatives noted where they provide additional
granularity.

## System

| Subsystem | Command | Key Output |
|-----------|---------|------------|
| Version/model | `show version` | EOS version, model, memory, uptime |
| Uptime | `show uptime` | System uptime |
| Reload cause | `show reload cause` | Last reload/reboot reason |
| Processes | `show processes top once` | Per-process CPU and memory |
| Inventory | `show inventory` | Hardware model, serial, FRUs |
| Boot config | `show boot` | Boot image, startup config |

### Linux-Native System Commands

| Command | EOS Equivalent | Additional Value |
|---------|---------------|-----------------|
| `bash timeout 5 top -bn1 \| head 20` | `show processes top once` | Per-thread detail, real-time memory |
| `bash free -m` | `show version` (memory section) | Buffer/cache/available breakdown |
| `bash df -h` | *(no direct equivalent)* | Filesystem usage for /mnt/flash, /var/log |
| `bash uptime` | `show uptime` | Load averages |
| `bash dmesg \| tail 30` | *(no direct equivalent)* | Kernel messages, driver errors |
| `bash cat /proc/meminfo` | *(no direct equivalent)* | Detailed memory breakdown |

### System Notes

- `show processes top once` runs a single snapshot (non-interactive). Use this
  for scripted collection rather than interactive `show processes top`.
- EOS memory reporting in `show version` includes Linux page cache as "used."
  True available memory is higher — use `bash free -m` `available` column.
- `show reload cause` shows the last reboot trigger. "User reloaded" is expected;
  "Kernel panic," "Software exception," or "Power loss" require investigation.

## Agent and Daemon Health

| Subsystem | Command | Key Output |
|-----------|---------|------------|
| Agent summary | `show agent` | PID, state, uptime per agent |
| Agent logs | `show agent [name] logs \| tail 20` | Recent log output for one agent |
| Agent detail | `show agent [name] detail` | Extended agent information |
| Syslog agents | `show logging last 50 \| include AGENT\|agent\|crash\|restart` | Agent events in syslog |
| Linux journal | `bash journalctl -u [name] --no-pager \| tail 20` | Systemd service logs |

### Agent Notes

- Every EOS subsystem runs as an independent agent (process). Key agents:
  `Stp`, `Rib`, `IpRib`, `Bgp`, `Ebra`, `Arp`, `Fap-sobek` / `Sand` (ASIC).
- Healthy: all agents `running`, uptime matches device uptime.
- An agent with shorter uptime than the device crashed and restarted.
- `show agent [name] logs` is the first place to look after an agent restart.
- EOS agents are managed by ProcMgr — it auto-restarts crashed agents.
  Multiple restarts indicate a persistent problem, not self-healing.

## Interfaces

| Subsystem | Command | Key Output |
|-----------|---------|------------|
| Interface status | `show interfaces status` | Speed, duplex, state per port |
| Error counters | `show interfaces counters errors` | Per-interface error counts |
| Discard counters | `show interfaces counters discards` | Per-interface discard counts |
| Interface detail | `show interfaces [name]` | Full counters, rates, stats |
| Optics DOM | `show interfaces [name] transceiver` | Tx/Rx power, temp, voltage |
| All optics | `show interfaces transceiver` | DOM for all interfaces |
| IP brief | `show ip interface brief` | IP address and status per interface |
| Port-channel | `show port-channel summary` | LAG member status |

### Interface Notes

- EOS interface naming: `Ethernet1`, `Ethernet1/1` (modular), `Management1`.
- `show interfaces counters errors` is the best single command for error overview.
- Separate `show interfaces counters discards` for drop/discard counters —
  these are not always in the errors output.
- Optics DOM: most 10G SFP+ expect Rx power above -10 dBm. Below -14 dBm
  is typically below receiver sensitivity. Check per-optic spec.
- Port-channel: `show port-channel summary` shows member state. All members
  should show `(P)` for bundled. `(s)` means standby, `(D)` means down.

## MLAG

| Subsystem | Command | Key Output |
|-----------|---------|------------|
| MLAG summary | `show mlag` | State, peer-link, domain-id |
| MLAG detail | `show mlag detail` | Heartbeat, timers, extended state |
| MLAG interfaces | `show mlag interfaces` | Per-MLAG interface state |
| Config sanity | `show mlag config-sanity` | Configuration consistency check |
| MLAG counters | `show mlag detail \| include Heartbeat\|Sent\|Received` | Control plane traffic stats |

### MLAG Notes

- MLAG state must be `active` with negotiation `connected` for healthy operation.
- Peer-link is the data path between MLAG peers. It carries BUM traffic and
  orphaned unicast. Peer-link down = MLAG degraded.
- Config-sanity checks: VLAN membership, STP priority, trunk allowed VLANs,
  and other parameters that must match between peers.
- `show mlag interfaces` state meanings:
  - `active-full` — both peers have their member up (healthy)
  - `active-partial` — one peer's member is down (reduced redundancy)
  - `disabled` — MLAG interface is down on this peer
- Heartbeat: separate from peer-link, typically via management VRF. Lost
  heartbeats with peer-link up → management network issue, not a data path failure.
- Reload-delay timers: ensure traffic doesn't black-hole during peer boot.
  Verify `reload-delay mlag` and `reload-delay non-mlag` are configured.

## VXLAN / EVPN

| Subsystem | Command | Key Output |
|-----------|---------|------------|
| VTEP list | `show vxlan vtep` | Remote VTEP IP addresses |
| VXLAN interface | `show interfaces vxlan 1` | VTEP source, flood list, VNIs |
| VXLAN address table | `show vxlan address-table` | MAC-to-VTEP mappings |
| BGP EVPN summary | `show bgp evpn summary` | EVPN peer state and route count |
| BGP EVPN routes | `show bgp evpn` | EVPN route table |
| EVPN type-2 (MAC/IP) | `show bgp evpn route-type mac-ip` | MAC/IP advertisements |
| EVPN type-5 (IP prefix) | `show bgp evpn route-type ip-prefix` | Inter-VRF IP routes |
| VRF route summary | `show ip route vrf [name] summary` | Per-VRF route counts |

### VXLAN/EVPN Notes

- `show vxlan vtep` — the expected VTEP count should match the number of remote
  leaf/border switches. Missing VTEPs indicate underlay routing or EVPN peering issues.
- `show interfaces vxlan 1` — the source interface (usually a Loopback) must be
  up and reachable from all remote VTEPs via the underlay IGP.
- BGP EVPN peering: all peers must be in `Established` state. Peers in `Active`
  or `Connect` have transport or configuration issues (ASN, route-map, peer-group).
- VXLAN flood list vs ingress replication: with BGP EVPN, flood list should be
  empty (BUM uses ingress replication). Non-empty flood list in an EVPN
  deployment suggests misconfiguration.
- Type-2 routes: MAC/IP bindings. Missing type-2s = hosts not advertised.
- Type-5 routes: IP prefix routes for inter-VRF (symmetric IRB). Missing type-5s
  = inter-VRF routing broken.

## Environment

| Subsystem | Command | Key Output |
|-----------|---------|------------|
| Environment summary | `show environment all` | Temp, power, fans — comprehensive |
| Temperature | `show environment temperature` | Per-sensor readings and thresholds |
| Cooling | `show environment cooling` | Fan speed, status, airflow direction |
| Power | `show environment power` | PSU status, input/output wattage |
| Logging | `show logging last 30` | Recent syslog messages |
| Crash data | `bash ls -la /var/log/qt/` | Core dump and crash files |

### Environment Notes

- `show environment all` is the single comprehensive environment command.
  Use specific sub-commands (temperature, cooling, power) for detail.
- Temperature: thresholds are per-sensor and shown in the command output.
  Arista switches typically have inlet, outlet, and per-ASIC sensors.
- Airflow direction matters: `show environment cooling` shows front-to-back
  or back-to-front. Mismatched airflow in a rack causes hot spots.
- Power: `show environment power` reports per-PSU input/output. Compare
  total output to rated capacity. Redundancy loss is a warning.
- Core dumps: EOS stores crash data under `/var/log/qt/`. Presence of
  recent `.core` files indicates agent crashes — collect before cleanup.
