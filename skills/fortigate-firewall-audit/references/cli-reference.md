# FortiOS CLI Reference — Audit Commands

Read-only commands organized by audit category for FortiGate firewall
security policy assessment. All commands are non-modifying (`get`, `show`,
`diagnose`). Validated against FortiOS 7.0+ and 7.4.x.

Three command types in FortiOS:
- **`get`:** Display running configuration summary (compact output)
- **`show`:** Display full configuration with all settings (verbose, scriptable)
- **`diagnose`:** Display runtime state, counters, and operational data

All commands below are read-only and safe for production use. No `set`,
`config ... end` (with modifications), or `execute` commands that alter state
are included.

## VDOM and System

| Function | CLI Command |
|----------|-------------|
| System status (version, serial, VDOM mode) | `get system status` |
| List all VDOMs | `diagnose sys vd list` |
| Enter a specific VDOM context | `config vdom` then `edit <vdom-name>` then `end` |
| Enter global context (multi-VDOM) | `config global` |
| VDOM resource limits | `get system vdom-property` |
| Inter-VDOM links | `show system vdom-link` |
| Interface list with VDOM assignments | `get system interface physical` |
| Interface status and counters | `diagnose hardware deviceinfo nic <port>` |
| System hostname and aliases | `get system global \| grep hostname` |
| DNS configuration | `get system dns` |
| Admin accounts and access profiles | `show system admin` |
| Admin access profile permissions | `show system accprofile` |

### VDOM Notes

- `diagnose sys vd list` shows all VDOMs with their index number, name, and operational status. This is the definitive command for VDOM inventory.
- When connected to a multi-VDOM system, you start in the `root` VDOM or the VDOM assigned to your admin account. Use `config vdom` / `edit <name>` to switch VDOM context for per-VDOM commands.
- `get system status` in global context shows FortiOS version, serial number, VDOM mode (enabled/disabled), and HA status — the baseline system identification command.

## Firewall Policy

| Function | CLI Command |
|----------|-------------|
| Full policy table (current VDOM) | `show firewall policy` |
| Policy summary (compact) | `get firewall policy` |
| Specific policy by ID | `show firewall policy <policy-id>` |
| Policy hit counts | `diagnose firewall iprope show 100004 <policy-id>` |
| IPv6 policy table | `show firewall policy6` |
| Multicast policy | `show firewall multicast-policy` |
| Local-in policy (traffic to FortiGate) | `show firewall local-in-policy` |
| DoS policy | `show firewall DoS-policy` |
| Shaping policy | `show firewall shaping-policy` |
| Central NAT table | `show firewall central-snat-map` |
| VIP (destination NAT) objects | `show firewall vip` |
| Address objects | `show firewall address` |
| Address groups | `show firewall addrgrp` |
| Service objects | `show firewall service custom` |
| Service groups | `show firewall service group` |
| Schedule objects | `show firewall schedule recurring` |
| Policy sequence (evaluation order) | `diagnose firewall iprope show 100004 <policy-id>` |

### Firewall Policy Notes

- `show firewall policy` outputs the full configuration of every policy in the current VDOM, including UTM profile bindings, NAT settings, and schedules. This is the primary audit command.
- `get firewall policy` provides a compact summary — policy ID, name, srcintf, dstintf, srcaddr, dstaddr, action, and status. Useful for quick inventory.
- Policy evaluation is by sequence number, not policy ID. The sequence number determines the order; policy ID is an immutable identifier. Use the GUI or `diagnose firewall iprope` to confirm evaluation order.
- `show firewall policy` output includes `utm-status`, `av-profile`, `webfilter-profile`, `application-list`, `ips-sensor`, and `ssl-ssh-profile` — the UTM binding fields critical for the audit.

## UTM Profiles

| Function | CLI Command |
|----------|-------------|
| Antivirus profiles | `show antivirus profile` |
| Web filter profiles | `show webfilter profile` |
| Application control lists | `show application list` |
| IPS sensors | `show ips sensor` |
| Email filter profiles | `show emailfilter profile` |
| DLP sensors | `show dlp sensor` |
| File filter profiles | `show file-filter profile` |
| SSL/SSH inspection profiles | `show firewall ssl-ssh-profile` |
| Web filter FortiGuard settings | `show webfilter fortiguard` |
| Inspection mode (VDOM-level) | `get system settings \| grep inspection-mode` |
| Proxy settings | `show firewall proxy-policy` |

### UTM Profile Notes

- `show antivirus profile` lists all AV profiles with their actions per protocol (HTTP, SMTP, IMAP, POP3, FTP, CIFS). Cross-reference with policy bindings to verify appropriate profile is assigned.
- `show firewall ssl-ssh-profile` reveals the SSL inspection mode per profile — `certificate-inspection` (metadata only) vs `deep-inspection` (full decrypt). Without deep-inspection, AV and IPS cannot inspect HTTPS content.
- `get system settings | grep inspection-mode` shows the VDOM-level inspection mode. In flow-based mode, some proxy-only UTM features are unavailable.

## FortiGuard Status

| Function | CLI Command |
|----------|-------------|
| FortiGuard service status | `get system fortiguard-service status` |
| All signature versions and dates | `diagnose autoupdate versions` |
| FortiGuard connectivity test | `diagnose debug rating` |
| Web filter rating connectivity | `get webfilter status` |
| Update schedule configuration | `show system autoupdate schedule` |
| Update channel settings | `show system autoupdate tunneling` |
| FortiGuard server list | `diagnose autoupdate status` |
| License status | `get system license status` |
| License entitlement details | `diagnose hardware sysinfo vm full` (VM only) |

### FortiGuard Notes

- `diagnose autoupdate versions` is the single most important command for signature freshness — it shows version and last-update timestamp for AV, IPS, Application Control, and Industrial DB.
- `diagnose debug rating` tests connectivity to FortiGuard web filter rating servers. Output shows latency and reachability to each server. Failure here means web filter uses cached ratings only.
- `get system fortiguard-service status` shows which FortiGuard services are licensed and their expiration dates.

## SD-WAN

| Function | CLI Command |
|----------|-------------|
| SD-WAN configuration | `show system sdwan` |
| SD-WAN member status | `diagnose sys sdwan member` |
| SD-WAN health check results | `diagnose sys sdwan health-check` |
| SD-WAN service rules | `diagnose sys sdwan service` |
| SD-WAN internet service DB | `diagnose sys sdwan internet-service-id-summary` |
| SD-WAN route table | `diagnose firewall proute list` |
| SD-WAN SLA log | `diagnose sys sdwan sla-log <health-check-name>` |
| SD-WAN neighbor info | `diagnose sys sdwan neighbor` |

### SD-WAN Notes

- `diagnose sys sdwan health-check` shows real-time SLA measurements (latency, jitter, packet loss) for each health check on each member link. Compare against SLA targets to identify links in violation.
- `diagnose sys sdwan service` shows how SD-WAN rules are mapping traffic to members. Check whether rule priorities and tie-break settings match design intent.
- `diagnose firewall proute list` shows the policy routing table including SD-WAN-derived routes. Verify that SD-WAN steering does not bypass security inspection paths.

## High Availability

| Function | CLI Command |
|----------|-------------|
| HA status summary | `get system ha status` |
| HA configuration | `show system ha` |
| HA checksum comparison | `diagnose sys ha checksum cluster` |
| HA peer status | `diagnose sys ha status` |
| HA history (failover events) | `diagnose sys ha history read` |
| HA management interfaces | `show system ha \| grep ha-mgmt` |
| HA heartbeat status | `diagnose sys ha heartbeat` |
| HA session sync status | `diagnose sys ha session-table-check` |

### HA Notes

- `get system ha status` provides a quick summary — HA mode (a-p / a-a), cluster role (primary/secondary), uptime, and priority. Always audit both members.
- `diagnose sys ha checksum cluster` compares configuration checksums between members. Mismatched checksums indicate configuration drift — the secondary may be enforcing different policies.
- `diagnose sys ha history read` shows failover events with timestamps. Frequent failovers may indicate instability.
- `show system ha` reveals session-pickup and session-pickup-connectionless settings — these control whether sessions survive failover.

## Session and Traffic

| Function | CLI Command |
|----------|-------------|
| Session table summary | `diagnose sys session stat` |
| Session count by VDOM | `diagnose sys session full-stat` |
| Session list (filtered) | `diagnose sys session filter src <IP>` then `diagnose sys session list` |
| Clear session filter | `diagnose sys session filter clear` |
| Session by policy | `diagnose sys session filter policy <id>` then `diagnose sys session list` |
| Top sessions by bandwidth | `diagnose sys top-session` |
| Traffic statistics per interface | `get system interface physical` |
| Routing table | `get router info routing-table all` |
| ARP table | `get system arp` |
| DNS cache | `diagnose test application dnsproxy 7` |

### Session and Traffic Notes

- `diagnose sys session stat` shows aggregate session counts (TCP, UDP, ICMP, other) and setup/teardown rates. Use for capacity baseline.
- `diagnose sys session list` with filters is the runtime session inspection tool. Always set filters first (`diagnose sys session filter`) to avoid dumping the entire session table.
- `diagnose sys top-session` shows the highest-bandwidth sessions — useful for identifying unexpected high-volume flows during audit.

## Logging and Monitoring

| Function | CLI Command |
|----------|-------------|
| Log settings | `show log setting` |
| Log to FortiAnalyzer config | `show log fortianalyzer setting` |
| Syslog configuration | `show log syslogd setting` |
| Disk log status | `diagnose log device-status` |
| Traffic log (recent) | `execute log filter category traffic` then `execute log display` |
| Event log (recent) | `execute log filter category event` then `execute log display` |
| UTM log (recent) | `execute log filter category utm` then `execute log display` |

### Logging Notes

- `execute log display` with appropriate filters shows recent log entries directly on CLI. Set category, subcategory, and time range with `execute log filter` before displaying.
- Verify that logging is enabled on the implicit deny policy (policy ID 0) — by default it logs nothing, leaving denied traffic invisible.
- For large-scale log analysis, FortiAnalyzer or syslog export is preferred over CLI log viewing.
