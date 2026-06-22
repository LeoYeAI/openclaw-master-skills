# Change Verification Checklist Templates

Pre/post verification checklists organized by change type with a rollback
decision matrix. Use these templates to ensure comprehensive baseline capture
and post-change validation.

## Generic Pre-Change Checklist

Run before **any** change, regardless of type. Captures the minimum baseline
needed for post-change comparison.

| # | Check | Command(s) | Capture |
|---|-------|-----------|---------|
| 1 | Archive running config | See cli-reference.md Config Archival | Save to flash with ticket ID |
| 2 | Route table summary | `show ip route summary` / `show route summary` | Total route count per protocol |
| 3 | BGP peer states | `show ip bgp summary` / `show bgp summary` | Peer count, Established count, prefix counts |
| 4 | OSPF adjacency states | `show ip ospf neighbor` / `show ospf neighbor` | Neighbor count, all in Full state |
| 5 | Interface summary | `show interfaces summary` / `show interfaces terse` | Up/down counts, error counters |
| 6 | CDP/LLDP neighbors | `show cdp neighbors` / `show lldp neighbors` | Neighbor count and identities |
| 7 | Hardware environment | `show environment all` / `show chassis environment` | PSU, fan, temperature status |
| 8 | CPU and memory | `show processes cpu` / `show system processes extensive` | Baseline utilization |
| 9 | Uptime | `show version` | Confirm no recent unexpected reload |
| 10 | Document timestamp | Note wall-clock time of baseline capture | Correlate with syslog later |

## Generic Post-Change Checklist

Run after **any** change to compare against the pre-change baseline.

| # | Check | Compare Against | Pass Criteria |
|---|-------|----------------|---------------|
| 1 | Config diff | Archived pre-change config | Only intended lines changed |
| 2 | Route count | Pre-change route summary | Within ±2% (see Threshold Tables) |
| 3 | BGP peers | Pre-change BGP summary | Same Established count (unless planned) |
| 4 | OSPF adjacencies | Pre-change OSPF neighbors | Same Full count (unless planned) |
| 5 | Interface states | Pre-change interface summary | No new down interfaces (unless planned) |
| 6 | Interface errors | Pre-change error counters | No new sustained errors |
| 7 | Neighbor count | Pre-change CDP/LLDP | Same neighbor count |
| 8 | Hardware health | Pre-change environment | No new alarms |
| 9 | Syslog review | N/A | No unexpected error messages |
| 10 | Service ping tests | N/A | Critical paths reachable |

## Change-Type-Specific Checklists

### Routing Changes (BGP / OSPF / EIGRP)

**Additional pre-change captures:**

| # | Check | Command(s) | Why |
|---|-------|-----------|-----|
| 1 | BGP neighbor detail | `show ip bgp neighbors [peer]` | Capture timers, capabilities, prefix counts |
| 2 | BGP received routes | `show ip bgp neighbors [peer] received-routes` | Know exactly which prefixes come from affected peer |
| 3 | BGP advertised routes | `show ip bgp neighbors [peer] advertised-routes` | Know what the peer sees from us |
| 4 | OSPF database summary | `show ip ospf database database-summary` | LSA counts by type for comparison |
| 5 | OSPF interface detail | `show ip ospf interface [intf]` | Cost, timers, area, network type |
| 6 | Routing policy (route-maps, prefix-lists) | `show route-map [name]` / `show ip prefix-list [name]` | Document current policy for diff |

**Additional post-change checks:**

| # | Check | Look For |
|---|-------|---------|
| 1 | BGP best path for changed prefixes | Verify new path selection matches intent |
| 2 | BGP community/MED/local-pref on affected routes | Verify policy attributes applied correctly |
| 3 | OSPF SPF run count | Compare to baseline — should show incremental SPF only |
| 4 | Route table for specific affected prefixes | Verify each prefix uses intended next-hop |
| 5 | Traceroute to key destinations | Verify traffic path matches intended design |
| 6 | BGP update message log | Check for unexpected withdrawals or announcements |

### Switching Changes (VLAN / STP / MLAG)

**Additional pre-change captures:**

| # | Check | Command(s) | Why |
|---|-------|-----------|-----|
| 1 | VLAN database | `show vlan brief` / `show vlans` | Full VLAN membership before changes |
| 2 | STP root status | `show spanning-tree root` | Know current root bridges |
| 3 | STP port states | `show spanning-tree [vlan]` | Identify forwarding/blocking ports |
| 4 | MLAG/vPC status | `show mlag` / `show vpc brief` | Peer status, consistency state |
| 5 | MAC table count | `show mac address-table count` | Baseline MAC count per VLAN |
| 6 | Port-channel summary | `show etherchannel summary` / `show port-channel summary` | Bundle member states |

**Additional post-change checks:**

| # | Check | Look For |
|---|-------|---------|
| 1 | VLAN membership | Intended VLANs added/removed, no unintended changes |
| 2 | STP root unchanged (or changed per plan) | Root bridge election stable |
| 3 | STP topology change count | Compare to baseline — minimize TCNs |
| 4 | MLAG consistency | No config-sanity errors between peers |
| 5 | MAC table learning | MACs appearing on correct ports in changed VLANs |
| 6 | Trunk allowed VLANs | New VLANs appearing on intended trunks only |

### Security Changes (ACL / Firewall / AAA)

**Additional pre-change captures:**

| # | Check | Command(s) | Why |
|---|-------|-----------|-----|
| 1 | ACL hit counters | `show access-list [name]` | Baseline hit counts for diff |
| 2 | ACL interface bindings | `show ip interface [intf]` | Know where ACLs are applied |
| 3 | AAA config | `show aaa sessions` / `show aaa` | Current auth method chains |
| 4 | SNMP community/user list | `show snmp community` / `show snmp v3` | Current SNMP access config |
| 5 | SSH session test | Verify SSH login works | Baseline access validation |
| 6 | Control plane policy | `show policy-map control-plane` (Cisco) | CoPP baseline |

**Additional post-change checks:**

| # | Check | Look For |
|---|-------|---------|
| 1 | ACL hit counters (new entries) | New deny entries not getting unexpected hits |
| 2 | SSH access test | Verify management access still works after AAA change |
| 3 | SNMP polling test | Verify monitoring still receives data |
| 4 | Console access test | Verify console login if AAA was changed |
| 5 | Traffic flow test | Verify permitted traffic passes through new ACLs |
| 6 | Syslog for deny messages | Check for unexpected ACL deny logs |

> **Critical safety note for security changes:** Always verify management
> access (SSH, console) immediately after committing AAA or ACL changes. Loss
> of management access is the highest-risk outcome and may not be reversible
> without physical console access. Use `commit confirmed` (JunOS) or prepare
> a console session before applying AAA changes.

### Software Upgrades (ISSU / Non-Disruptive / Full Reboot)

**Additional pre-change captures:**

| # | Check | Command(s) | Why |
|---|-------|-----------|-----|
| 1 | Current software version | `show version` | Document exact version string |
| 2 | Boot variable | `show boot` / `show boot-config` | Know current boot image |
| 3 | File system free space | `dir flash:` / `file list detail` | Ensure space for new image |
| 4 | Redundancy status (if HA) | `show redundancy` / `show virtual-chassis` | SSO/NSR state before upgrade |
| 5 | ISSU compatibility | Vendor-specific ISSU pre-check | Confirm upgrade is non-disruptive |
| 6 | License status | `show license` / `show system license` | Verify licenses survive upgrade |

**Additional post-change checks:**

| # | Check | Look For |
|---|-------|---------|
| 1 | New software version | `show version` matches target version |
| 2 | Uptime confirms reload | Uptime reflects expected reload time |
| 3 | All linecards online | `show module` / `show chassis fpc` — all operational |
| 4 | Process health | No crashed or restarting processes |
| 5 | License still valid | All licensed features operational |
| 6 | HA status restored | Redundancy back to SSO/NSR if applicable |
| 7 | Config persistence | Running config matches pre-upgrade archive |
| 8 | Control plane convergence | All BGP/OSPF adjacencies restored |
| 9 | Data plane forwarding | Ping/traceroute to critical destinations |

## Rollback Decision Matrix

Use this matrix when deviations are detected. Cross-reference **severity** of
the deviation against **scope** (inside/outside change plan) and **timing**
(within/beyond convergence window).

### Severity × Scope

| | In Change Scope | Outside Change Scope |
|---|----------------|---------------------|
| **Expected — Intended** | ✅ Accept — this is the goal | N/A — by definition, intended changes are in scope |
| **Expected — Side Effect** | ✅ Accept — document the side effect | ⚠️ Investigate — why is an out-of-scope device affected? |
| **Unexpected — Minor** | ⚠️ Investigate — may be benign but needs explanation | ⚠️ Investigate — could indicate broader issue |
| **Unexpected — Critical** | 🔴 Evaluate rollback — check if recoverable | 🔴 Immediate rollback — collateral damage detected |

### Severity × Timing

| | Within Convergence Window | Beyond Convergence Window |
|---|--------------------------|--------------------------|
| **Expected — Intended** | ✅ Normal convergence | ✅ Accept |
| **Expected — Side Effect** | ✅ Wait for stabilization | ⚠️ Investigate if still fluctuating |
| **Unexpected — Minor** | ⚠️ Monitor — may self-resolve | ⚠️ Investigate — should have resolved by now |
| **Unexpected — Critical** | 🔴 Start rollback preparation | 🔴 Execute rollback — not recovering |

### Escalation Triggers

These conditions require **immediate escalation** regardless of other matrix
outcomes:

1. **Total management access loss** to any device in the change scope
2. **Customer-affecting outage** detected or reported during the change window
3. **Cascading failures** — deviations spreading to devices outside change scope
4. **Hardware alarms** (temperature, PSU, fan) that were not present in baseline
5. **Rollback failure** — rollback command does not restore pre-change state
6. **Change window expiry** with unresolved critical deviations
