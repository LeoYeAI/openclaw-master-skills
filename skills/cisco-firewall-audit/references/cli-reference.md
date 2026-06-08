# Cisco ASA and FTD CLI Reference — Audit Commands

Read-only commands organized by audit category for Cisco ASA and Firepower
Threat Defense (FTD) firewall assessment. All commands are non-modifying
(`show`, `display`, diagnostic queries). Commands are labeled **[ASA]**,
**[FTD]**, or **[Both]** to indicate platform applicability.

Access methods:
- **[ASA]** SSH/console to ASA CLI (privilege level 5+ for `show` commands)
- **[FTD]** SSH/console to FTD CLI → `system support diagnostic-cli` for ASA-style commands
- **[FTD]** FMC REST API for policy and event queries
- **[Both]** ASDM (ASA) or FDM (FTD) web UI for visual inspection

## System and Platform Identification

| Function | Command | Platform |
|----------|---------|----------|
| Software version, model, uptime | `show version` | Both |
| Running configuration | `show running-config` | Both |
| Hardware and serial number | `show inventory` | Both |
| License status | `show license` | ASA |
| License status | `show license status` | FTD |
| Feature license summary | `show license usage` | FTD |
| Routed vs transparent mode | `show firewall` | Both |
| Multi-context mode | `show mode` | ASA |
| Context list | `show context` | ASA |
| Management model (FMC/FDM) | `show managers` | FTD |
| Enter diagnostic CLI | `system support diagnostic-cli` | FTD |

### System Notes

- **[FTD]** `system support diagnostic-cli` enters an ASA-compatible CLI. Most `show` commands work here but reflect the deployed policy, not FMC pending changes.
- **[ASA]** `show mode` confirms single vs multi-context. In multi-context, use `changeto context <name>` to audit each context separately.

## Interface and Security Level Inventory

| Function | Command | Platform |
|----------|---------|----------|
| Interface summary (IP, status) | `show interface ip brief` | Both |
| Interface names and security levels | `show nameif` | ASA |
| Interface detail (counters, errors) | `show interface <name>` | Both |
| Interface security zones | Via FMC UI → Devices → Interfaces | FTD |
| VLAN sub-interfaces | `show running-config interface` | Both |
| Same-security-traffic setting | `show running-config same-security-traffic` | ASA |

### Interface Notes

- **[ASA]** Security levels are the foundation of ASA access control. Document each interface's level — it determines default traffic flow behavior.
- **[FTD]** FTD uses security zones instead of security levels. Zone assignments are visible in FMC UI or via `show running-config interface` on the diagnostic CLI.

## Access Policy

| Function | Command | Platform |
|----------|---------|----------|
| All ACLs with hit counts | `show access-list` | ASA |
| Specific ACL | `show access-list <name>` | ASA |
| ACL-to-interface bindings | `show running-config access-group` | ASA |
| Global ACL | `show running-config access-list` (grep for global) | ASA |
| Access Control Policy summary | `show access-control-config` | FTD |
| ACP rule details (diagnostic CLI) | `show access-list` (deployed ACLs) | FTD |
| Object groups | `show running-config object-group` | Both |
| Network objects | `show running-config object network` | Both |

### Access Policy Notes

- **[ASA]** `show access-list` includes `hitcnt=N` per ACE. Zero-hitcount ACEs over 90 days are cleanup candidates.
- **[FTD]** `show access-control-config` in the diagnostic CLI shows the deployed ACP as ACL-like entries. The authoritative policy view is in FMC.
- **[Both]** Object groups consolidate addresses and services. Review object-group membership to understand ACE scope — an ACE referencing a broad object group may be more permissive than it appears.

## NAT Policy

| Function | Command | Platform |
|----------|---------|----------|
| NAT rules (all sections) | `show nat` | Both |
| NAT rules with detail | `show nat detail` | Both |
| NAT configuration | `show running-config nat` | Both |
| Active translations | `show xlate` | Both |
| Translation count | `show xlate count` | Both |
| NAT by interface pair | `show nat interface <iface>` | ASA |

### NAT Notes

- `show nat` displays rules in evaluation order: Section 1 (manual) → Section 2 (auto) → Section 3 (after-auto). Each rule shows translated and untranslated addresses.
- `show xlate` shows active translation slots. High counts near the xlate limit may indicate NAT pool exhaustion.
- Cross-reference static NAT entries with ACL entries to verify that published servers are restricted to necessary ports.

## Inspection and IPS

| Function | Command | Platform |
|----------|---------|----------|
| Service-policy (applied MPF) | `show service-policy` | ASA |
| Service-policy configuration | `show running-config service-policy` | ASA |
| Class-map configuration | `show running-config class-map` | ASA |
| Policy-map configuration | `show running-config policy-map` | ASA |
| Inspection counters | `show service-policy inspect <protocol>` | ASA |
| Connection limits | `show service-policy | include conns` | ASA |
| Snort statistics | `show snort statistics` | FTD |
| Snort counters | `show snort counters` | FTD |
| Intrusion event summary | Via FMC UI → Analysis → Intrusions | FTD |
| File/Malware events | Via FMC UI → Analysis → Files | FTD |
| Deployed intrusion policy | Via FMC REST API: `/api/fmc_config/v1/domain/{domainUUID}/policy/intrusionpolicies` | FTD |

### Inspection Notes

- **[ASA]** `show service-policy` shows which inspections are active and their counters. A missing global service-policy means no application-layer inspection.
- **[FTD]** `show snort statistics` on the FTD CLI shows Snort engine performance: packets inspected, alerts, drops, and pass verdicts.
- **[FTD]** Intrusion event review is best done via FMC UI or API — the FTD CLI has limited event visibility.

## VPN

| Function | Command | Platform |
|----------|---------|----------|
| IPSec SA summary | `show crypto ipsec sa` | Both |
| IKEv2 SA summary | `show crypto ikev2 sa` | Both |
| IKEv1 SA summary | `show crypto ikev1 sa` | Both |
| VPN session database | `show vpn-sessiondb` | Both |
| AnyConnect sessions | `show vpn-sessiondb anyconnect` | Both |
| Tunnel group configuration | `show running-config tunnel-group` | Both |
| Group policy configuration | `show running-config group-policy` | Both |
| Crypto map configuration | `show running-config crypto map` | ASA |
| Certificate trustpoints | `show running-config crypto ca trustpoint` | Both |
| Certificate details | `show crypto ca certificates` | Both |

### VPN Notes

- `show crypto ipsec sa` shows each tunnel's encryption algorithm, packet counters, and SA lifetime. Check for DES/3DES or weak DH groups.
- `show vpn-sessiondb` provides active VPN session count and type (IPSec, AnyConnect, clientless). High session counts may indicate capacity issues.
- **[FTD]** Site-to-site VPN is configured via FMC (Devices → VPN → Site to Site). The diagnostic CLI shows the deployed result.

## Failover and High Availability

| Function | Command | Platform |
|----------|---------|----------|
| Failover status | `show failover` | Both |
| Failover state | `show failover state` | Both |
| Failover history | `show failover history` | Both |
| Failover interface | `show failover | include interface` | Both |
| Configuration sync status | `show failover | include Config` | Both |
| Cluster status (4100/9300) | `show cluster info` | Both |

### Failover Notes

- `show failover state` reveals Active/Standby/Failed status for each unit. Both units should show healthy state.
- `show failover history` shows recent failover events and reasons. Frequent failovers indicate stability issues.
- Configuration sync: verify "Last Failover" timestamps and config sync status. Mismatched configs between active/standby are a risk.

## Connections and Sessions

| Function | Command | Platform |
|----------|---------|----------|
| Connection summary | `show conn count` | Both |
| Connection detail (filtered) | `show conn address <IP>` | Both |
| Connection by interface | `show conn state <state>` | Both |
| Connection rate | `show perfmon` | ASA |
| Top talkers | `show local-host | include host` | Both |
| Session table utilization | `show resource usage` | ASA |
| CPU utilization | `show cpu usage` | Both |
| Memory utilization | `show memory` | Both |
| Process status | `show process cpu-usage sorted non-zero` | Both |

### Connection Notes

- `show conn count` provides current and peak connection counts. Compare against platform limits to assess headroom.
- `show perfmon` (ASA) shows connection rates per second — useful for capacity planning.

## Logging and Monitoring

| Function | Command | Platform |
|----------|---------|----------|
| Logging configuration | `show logging` | Both |
| Logging configuration detail | `show running-config logging` | Both |
| Log buffer (recent messages) | `show logging | tail 50` | Both |
| SNMP configuration | `show running-config snmp-server` | Both |
| SNMP statistics | `show snmp-server statistics` | Both |
| AAA server status | `show aaa-server` | Both |
| eStreamer status | Via FMC UI → System → Integration | FTD |
| Connection events | Via FMC UI → Analysis → Connections | FTD |

### Logging Notes

- `show logging` displays current logging configuration: buffer size, console level, syslog servers, and trap level.
- Verify at least one syslog destination is configured with level "informational" (6) or higher for audit trail.
- **[FTD]** Connection event logging is configured per ACP rule in FMC. Rules without connection logging produce no audit trail.

## FMC REST API Examples

For programmatic audit of FTD environments, the FMC REST API provides
comprehensive policy and event access.

| Function | API Endpoint |
|----------|-------------|
| Authentication | `POST /api/fmc_platform/v1/auth/generatetoken` |
| List devices | `GET /api/fmc_config/v1/domain/{domainUUID}/devices/devicerecords` |
| Access policies | `GET /api/fmc_config/v1/domain/{domainUUID}/policy/accesspolicies` |
| ACP rules | `GET /api/fmc_config/v1/domain/{domainUUID}/policy/accesspolicies/{policyId}/accessrules` |
| NAT policies | `GET /api/fmc_config/v1/domain/{domainUUID}/policy/ftdnatpolicies` |
| Intrusion policies | `GET /api/fmc_config/v1/domain/{domainUUID}/policy/intrusionpolicies` |
| Connection events | `GET /api/fmc_config/v1/domain/{domainUUID}/health/alerts` |
| System status | `GET /api/fmc_platform/v1/domain/{domainUUID}/deployment/deployabledevices` |

### API Notes

- Authentication returns a token in the `X-auth-access-token` header. Pass this header on subsequent requests.
- API supports pagination (`offset`, `limit`) for large result sets.
- Use `expanded=true` query parameter to get full object details instead of summary references.
- For audit, create a read-only API user role in FMC (Analysis → Read Only).
