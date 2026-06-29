# ACL and Firewall Rule Analysis — Multi-Vendor CLI Reference

Read-only commands for retrieving ACLs, firewall rulebases, and hit counts
across 6 platforms. All commands are non-modifying. Organized by audit
function with per-vendor sections.

## Cisco IOS / IOS-XE

| Function | CLI Command |
|----------|-------------|
| All ACLs (numbered and named) | `show access-lists` |
| IPv4 ACLs only | `show ip access-lists` |
| Specific ACL | `show ip access-lists [name\|number]` |
| ACL with hit counts | `show ip access-lists` (counts shown per entry by default) |
| Clear hit counts (pre-audit baseline) | `clear access-list counters [name\|number]` |
| ACL applied to interface | `show ip interface [intf] \| include access list` |
| Running config ACLs | `show running-config \| section access-list` |
| Object groups | `show object-group` |
| Device uptime (counter validity) | `show version \| include uptime` |

### Cisco IOS Notes

- Hit counts are displayed inline with each ACE (Access Control Entry) in
  `show access-lists` output as `(N matches)`.
- Counters reset on device reload. Verify uptime before using hit counts
  for unused rule determination.
- Extended ACLs show source, destination, protocol, and port. Standard ACLs
  show source only.

## Cisco ASA

| Function | CLI Command |
|----------|-------------|
| All access lists | `show access-list` |
| Specific access list | `show access-list [name]` |
| Access list hit counts | `show access-list [name]` (hitcnt shown per ACE) |
| Clear hit counts | `clear access-list [name] counters` |
| Access groups (ACL-to-interface binding) | `show running-config access-group` |
| Object groups | `show running-config object-group` |
| Network objects | `show running-config object network` |
| Service objects | `show running-config object service` |
| NAT rules | `show running-config nat` |
| Device uptime | `show version \| include up` |

### Cisco ASA Notes

- ASA ACLs display `hitcnt=N` per ACE, providing built-in usage tracking.
- `access-group` binds ACLs to interfaces with direction (in/out) — check
  both to understand effective filtering on an interface.
- Object groups and network objects expand to individual ACEs at evaluation
  time — expand groups before shadow analysis.

## Juniper JunOS

| Function | CLI Command |
|----------|-------------|
| Firewall filter configuration | `show configuration firewall family inet filter` |
| Firewall filter counters | `show firewall filter [name]` |
| Specific filter term counters | `show firewall filter [name] counter [term]` |
| Policer statistics | `show policer` |
| Filter applied to interface | `show configuration interfaces [intf] unit [n] family inet filter` |
| Prefix lists | `show configuration policy-options prefix-list` |
| Security policies (SRX) | `show security policies` |
| Security policy hit counts (SRX) | `show security policies hit-count` |
| Device uptime | `show system uptime` |

### JunOS Notes

- JunOS firewall filters use `term` entries, each with `from` (match) and
  `then` (action) clauses. Counters must be explicitly configured per term
  with the `count` action.
- Terms without an explicit `count` action will not have hit count data —
  counters are not automatic on JunOS firewall filters.
- SRX security policies (`show security policies`) have automatic hit
  counting and display format similar to stateful firewall platforms.
- Implicit discard at the end of the term list unless a final `then accept`
  term is present.

## Arista EOS

| Function | CLI Command |
|----------|-------------|
| All IPv4 ACLs | `show ip access-lists` |
| Specific ACL | `show ip access-lists [name]` |
| ACL counters | `show access-lists counters` |
| ACL applied to interface | `show ip interface [intf]` |
| Running config ACLs | `show running-config \| section access-list` |
| Device uptime | `show uptime` |
| Hardware TCAM utilization | `show platform trident tcam` |

### EOS Notes

- `show access-lists counters` provides per-entry match counts separately
  from the ACL display — use this command specifically for hit count analysis.
- EOS ACL syntax closely mirrors Cisco IOS. Most Cisco ACL analysis logic
  applies directly to EOS.
- TCAM utilization (`show platform trident tcam`) indicates hardware ACL
  capacity — relevant for large ACL optimization efforts.

## Palo Alto PAN-OS

| Function | CLI Command |
|----------|-------------|
| Running security policy | `show running security-policy` |
| Rule hit counts | `show rule-hit-count vsys vsys1 security rules all` |
| Specific rule hit count | `show rule-hit-count vsys vsys1 security rules rule-name [name]` |
| Test policy match | `test security-policy-match source [IP] destination [IP] protocol [num] application [app] destination-port [port] from [zone] to [zone]` |
| NAT policy | `show running nat-policy` |
| Address objects | `show running address` |
| Address groups | `show running address-group` |
| Service objects | `show running service` |
| Service groups | `show running service-group` |
| Application details | `show running application [name]` |
| Device uptime | `show system info \| match uptime` |

### PAN-OS Notes

- `show rule-hit-count` provides first-hit, last-hit, and total count per
  rule — last-hit timestamp is especially useful for identifying stale rules.
- The `test security-policy-match` command is the definitive tool for
  validating which rule matches specific traffic.
- PAN-OS rules evaluate: pre-rules → local rules → post-rules (Panorama).
  Shadow analysis must consider rule scope (pre/local/post).

### PAN-OS XML API

| Function | API Call |
|----------|---------|
| Full security rulebase | `GET /api/?type=config&action=get&xpath=/config/devices/entry/vsys/entry[@name='vsys1']/rulebase/security` |
| Address objects | `GET /api/?type=config&action=get&xpath=/config/devices/entry/vsys/entry[@name='vsys1']/address` |
| Rule hit counts | `GET /api/?type=op&cmd=<show><rule-hit-count><vsys><vsys-name><entry name='vsys1'><rule-base><entry name='security'><rules><all/></rules></entry></rule-base></entry></vsys-name></vsys></rule-hit-count></show>` |

## Fortinet FortiGate (FortiOS)

| Function | CLI Command |
|----------|-------------|
| All firewall policies | `get firewall policy` |
| Specific policy | `get firewall policy [id]` |
| Policy hit counts (packets/bytes) | `diagnose firewall iprope list` |
| Policy lookup for specific traffic | `diagnose firewall iprope lookup [src-ip] [dst-ip] [proto] [src-port] [dst-port]` |
| Address objects | `show firewall address` |
| Address groups | `show firewall addrgrp` |
| Service objects | `show firewall service custom` |
| Service groups | `show firewall service group` |
| Device uptime | `get system performance status` |

### FortiGate Notes

- `diagnose firewall iprope list` displays per-policy packet and byte
  counters. Zero counters indicate unused policies.
- FortiGate policies use numeric IDs and display in order of evaluation.
  The `policyid` is the unique identifier for each rule.
- Implicit deny is the last policy (ID 0, not displayed in `get firewall
  policy` — visible via `diagnose firewall iprope list`).

### FortiGate REST API

| Function | API Call |
|----------|---------|
| All firewall policies | `GET /api/v2/cmdb/firewall/policy` |
| Specific policy | `GET /api/v2/cmdb/firewall/policy/[id]` |
| Address objects | `GET /api/v2/cmdb/firewall/address` |

## Check Point

| Function | CLI Command |
|----------|-------------|
| Firewall status and policy name | `fw stat` |
| Policy statistics | `cpstat fw -f policy` |
| Installed policy details | `fw stat -l` |
| Connection table | `fw tab -t connections -s` |
| Rule hit counts | SmartConsole → Policy → right-click column header → enable Hit Count |
| Exported rulebase | SmartConsole → File → Export Policy (CSV/HTML) |
| Management API: list access rules | `mgmt_cli show access-rulebase name [policy-name]` |
| Management API: specific rule | `mgmt_cli show access-rule layer [layer] rule-number [n]` |
| Device uptime | `cpstat os -f ifconfig` |

### Check Point Notes

- Check Point hit count data is stored in SmartConsole, not on the gateway
  CLI. Use the Management API (`mgmt_cli`) for programmatic access.
- `mgmt_cli show access-rulebase` returns rules as JSON, suitable for
  automated shadow and redundancy analysis.
- Check Point uses layers (ordered and inline) — shadow analysis must
  account for layer evaluation order.
- The implicit drop rule (Cleanup Rule) is the last rule in the policy
  and is configurable in SmartConsole.
