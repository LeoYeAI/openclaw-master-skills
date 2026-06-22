# Change Verification CLI Reference

Multi-vendor command reference for change verification operations across Cisco
IOS-XE/NX-OS, Juniper JunOS, and Arista EOS. Commands are organized by change
lifecycle phase.

## Architecture Differences — Change Management

Each vendor handles change execution and rollback differently:

- **Cisco (IOS-XE/NX-OS):** Changes apply immediately in config mode — no
  native commit-confirm on IOS-XE (NX-OS has `checkpoint`/`rollback`). Rollback
  uses `configure replace` with a previously saved config file. Requires the
  `archive` feature for config replace on IOS-XE.
- **JunOS:** Candidate-commit model with native `commit confirmed [minutes]`
  for auto-rollback. Supports `rollback N` to any of the last 50 commits. The
  strongest native rollback capability of the three vendors.
- **EOS:** Supports `configure session` for atomic staged changes and
  `configure replace` for full config rollback. `commit timer` provides
  commit-confirm-like behavior within sessions.

## Pre-Change Baseline Capture (Read-Only)

### Routing State

| Operation | Cisco | JunOS | EOS |
|-----------|-------|-------|-----|
| Route summary | `show ip route summary` | `show route summary` | `show ip route summary` |
| BGP peer summary | `show ip bgp summary` | `show bgp summary` | `show ip bgp summary` |
| BGP neighbor detail | `show ip bgp neighbors [peer]` | `show bgp neighbor [peer]` | `show ip bgp neighbors [peer]` |
| OSPF neighbors | `show ip ospf neighbor` | `show ospf neighbor` | `show ip ospf neighbor` |
| OSPF database summary | `show ip ospf database database-summary` | `show ospf database summary` | `show ip ospf database database-summary` |
| EIGRP topology | `show ip eigrp topology summary` | N/A | N/A |
| Static routes | `show ip route static` | `show route protocol static` | `show ip route static` |
| VRF route tables | `show ip route vrf [name] summary` | `show route table [instance] summary` | `show ip route vrf [name] summary` |

### Interface and Adjacency State

| Operation | Cisco | JunOS | EOS |
|-----------|-------|-------|-----|
| Interface summary | `show interfaces summary` | `show interfaces terse` | `show interfaces status` |
| Interface counters | `show interfaces [intf] counters` | `show interfaces [intf] statistics` | `show interfaces [intf] counters` |
| Interface errors | `show interfaces [intf] \| include errors` | `show interfaces [intf] \| match error` | `show interfaces [intf] counters errors` |
| CDP/LLDP neighbors | `show cdp neighbors` | `show lldp neighbors` | `show lldp neighbors` |
| ARP table | `show ip arp` | `show arp no-resolve` | `show ip arp` |
| MAC address table | `show mac address-table count` | `show ethernet-switching table summary` | `show mac address-table count` |
| VLAN status | `show vlan brief` | `show vlans` | `show vlan brief` |
| STP topology | `show spanning-tree summary` | `show spanning-tree bridge` | `show spanning-tree summary` |
| MLAG/vPC status | `show vpc brief` (NX-OS) | `show virtual-chassis` | `show mlag` |

### Hardware and Environment

| Operation | Cisco | JunOS | EOS |
|-----------|-------|-------|-----|
| Environment sensors | `show environment all` | `show chassis environment` | `show environment all` |
| Inventory | `show inventory` | `show chassis hardware` | `show inventory` |
| CPU utilization | `show processes cpu` | `show system processes extensive` | `show processes top` |
| Memory utilization | `show processes memory` | `show system memory` | `show processes top` |
| Software version | `show version` | `show version` | `show version` |
| Uptime | `show version \| include uptime` | `show system uptime` | `show uptime` |

### Configuration Archival

| Operation | Cisco | JunOS | EOS |
|-----------|-------|-------|-----|
| Show running config | `show running-config` | `show configuration` | `show running-config` |
| ⚠️ Save to flash | `copy running-config flash:[file]` | `request system configuration save /var/tmp/[file]` | `copy running-config flash:[file]` |
| ⚠️ Save to SCP | `copy running-config scp://[user]@[server]/[file]` | `request system configuration save scp://[user]@[server]/[file]` | `copy running-config scp://[user]@[server]/[file]` |
| Set terminal length | `terminal length 0` | `set cli screen-length 0` | `terminal length 0` |

## Change Execution Commands

> ⚠️ **WRITE operations** — all commands in this section modify device state.
> Confirm change ticket approval and maintenance window before executing.

### Config Mode and Commit Patterns

| Operation | Cisco | JunOS | EOS |
|-----------|-------|-------|-----|
| ⚠️ Enter config mode | `configure terminal` | `configure` | `configure terminal` |
| ⚠️ Enter session mode | N/A | N/A (single candidate) | `configure session [name]` |
| Review pending changes | N/A (applied immediately) | `show \| compare` | `show session-config [name]` |
| ⚠️ Commit changes | N/A (applied immediately) | `commit` | `commit` (in session) |
| ⚠️ Commit with auto-rollback | N/A | `commit confirmed [minutes]` | `commit timer [hh:mm:ss]` |
| ⚠️ Confirm pending commit | N/A | `commit` (after `commit confirmed`) | `commit` (after timer commit) |
| ⚠️ Abort staged changes | `end` | `rollback 0` | `abort` (in session) |

### Rollback and Recovery

| Operation | Cisco | JunOS | EOS |
|-----------|-------|-------|-----|
| ⚠️ Rollback to saved config | `configure replace flash:[file] force` | `rollback [N]` then `commit` | `configure replace flash:[file]` |
| ⚠️ Rollback to last commit | `configure replace flash:[backup] force` | `rollback 1` then `commit` | `configure replace flash:[backup]` |
| Preview rollback diff | `show archive config differences system:running-config flash:[file]` | `show \| compare rollback [N]` | `diff running-config flash:[file]` |
| Show rollback history | `show archive` | `show system commit` | `show config sessions` |
| ⚠️ Create checkpoint (NX-OS) | `checkpoint [name]` | N/A | N/A |
| ⚠️ Rollback to checkpoint (NX-OS) | `rollback running-config checkpoint [name]` | N/A | N/A |

### Vendor-Specific Rollback Notes

**JunOS — Strongest native rollback:**
- `rollback N` reverts to the Nth previous committed configuration (0 = current
  committed, 1 = previous, up to 49)
- `commit confirmed [minutes]` auto-reverts if not confirmed — ideal for remote
  changes where connectivity loss would prevent manual rollback
- `show system commit` lists all available rollback points with timestamps

**Cisco — File-based rollback:**
- IOS-XE: `configure replace` requires the `archive` feature enabled in config.
  Without it, manual line-by-line reversal is needed
- NX-OS: native `checkpoint`/`rollback` provides commit-style rollback similar
  to JunOS
- Both require pre-change config to be saved to flash before the change

**EOS — Session-based with file rollback:**
- `configure session` provides atomic changes — abort discards all session
  changes without affecting running-config
- `configure replace` works with full config files saved to flash
- `commit timer` in session mode provides time-limited commit similar to JunOS
  `commit confirmed`

## Post-Change Verification (Read-Only)

### Config Diff

| Operation | Cisco | JunOS | EOS |
|-----------|-------|-------|-----|
| Diff running vs archived | `show archive config differences flash:[file] system:running-config` | `show \| compare rollback [N]` | `diff running-config flash:[file]` |
| Diff two files | `show archive config differences flash:[file1] flash:[file2]` | `show \| compare rollback [N1] rollback [N2]` | `diff flash:[file1] flash:[file2]` |
| Show last config change | `show running-config \| include Last` | `show system commit \| head 5` | `show running-config \| include Last` |

### Service Verification

| Operation | Cisco | JunOS | EOS |
|-----------|-------|-------|-----|
| Ping test | `ping [dest] source [src]` | `ping [dest] source [src]` | `ping [dest] source [src]` |
| Traceroute | `traceroute [dest] source [src]` | `traceroute [dest] source [src]` | `traceroute [dest] source [src]` |
| Check logging for errors | `show logging \| include %` | `show log messages \| last 50` | `show logging last 50 lines` |
| Check syslog for change events | `show logging \| include CONFIG` | `show log messages \| match CHANGE` | `show logging \| include ConfigChange` |

### Counter and Metric Recapture

Use the same commands from the Pre-Change Baseline Capture section above to
recapture all metrics. Compare each metric against the pre-change baseline
values, applying the deviation thresholds from the SKILL.md Threshold Tables.
