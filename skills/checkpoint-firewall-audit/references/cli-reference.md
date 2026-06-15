# Check Point CLI and API Reference — Audit Commands

Read-only commands organized by audit category for Check Point Security
Gateway and Management Server assessment. All commands are non-modifying
(`show`, `stat`, diagnostic queries). Validated against R80.40 and R81.x.

Four access methods are available:
- **Clish:** Check Point CLI shell on the gateway (restricted command set)
- **Expert mode:** Full Linux shell on the gateway (fw, cpstat, cpview)
- **mgmt_cli:** Management API CLI on the Management Server (policy/object queries)
- **Web API:** HTTPS REST API on Management Server (same as mgmt_cli, JSON)

## System and SIC Status

| Function | Command | Context |
|----------|---------|---------|
| System version and build | `clish -c "show version all"` | Gateway/SMS |
| Hostname and platform | `clish -c "show hostname"` | Gateway/SMS |
| Uptime | `clish -c "show uptime"` | Gateway/SMS |
| CPU and memory summary | `cpview` (interactive) | Gateway |
| CPU utilization | `cpstat os -f cpu` | Gateway |
| Memory utilization | `cpstat os -f memory` | Gateway |
| Disk space | `cpstat os -f disk` | Gateway/SMS |
| SIC status | `cpstat sic` | Gateway |
| SIC certificate details | `cpconfig` → option 7 (view) | Gateway |
| Firewall status (policy name, install time) | `fw stat` | Gateway |
| All CP processes status | `cpwd_admin list` | Gateway/SMS |
| Management Server status | `cpstat mg` | SMS |
| MDS domain status | `mdsstat` | MDS |

### System Notes

- `fw stat` is the quickest way to verify the installed policy name and installation timestamp. Compare with SmartConsole to detect policy drift.
- `cpview` provides a real-time dashboard of CPU, memory, network, and blade status. Use it for quick health assessment.
- `cpwd_admin list` shows all Check Point watchdog-managed processes and their PID/status. Crashed processes appear as "down."

## Policy and Rulebase

| Function | Command | Context |
|----------|---------|---------|
| List access layers | `mgmt_cli show access-layers --format json -r true` | SMS |
| Show rulebase (layer) | `mgmt_cli show access-rulebase name "<layer>" --format json -r true` | SMS |
| Show rulebase (full detail) | `mgmt_cli show access-rulebase name "<layer>" details-level full --format json -r true` | SMS |
| Show NAT rulebase | `mgmt_cli show nat-rulebase --format json -r true` | SMS |
| Show HTTPS inspection rulebase | `mgmt_cli show https-rulebase --format json -r true` | SMS |
| List threat prevention profiles | `mgmt_cli show threat-profiles --format json -r true` | SMS |
| Show threat prevention rulebase | `mgmt_cli show threat-rulebase --format json -r true` | SMS |
| Show gateways and servers | `mgmt_cli show gateways-and-servers --format json -r true` | SMS |
| Show access roles | `mgmt_cli show access-roles --format json -r true` | SMS |
| Installed policy on gateway | `fw stat` | Gateway |
| Connection table summary | `fw tab -t connections -s` | Gateway |
| Active connections count | `cpstat fw -f policy` | Gateway |

### Policy Notes

- `mgmt_cli` commands with `-r true` use the last published session (read-only mode). Without `-r true`, a new session is created (unnecessary for audit).
- `details-level full` returns complete object data (IP addresses, names) inline rather than just UIDs. Required for meaningful audit analysis.
- `fw tab -t connections -s` shows connection table utilization. Near-capacity tables cause new connection drops.

## Blade Status

| Function | Command | Context |
|----------|---------|---------|
| All blade status summary | `cpstat blades` | Gateway |
| Firewall blade statistics | `cpstat fw` | Gateway |
| IPS blade status | `cpstat ips` | Gateway |
| Application Control status | `cpstat appi` | Gateway |
| URL Filtering status | `cpstat urlf` | Gateway |
| Anti-Bot status | `cpstat antimalware -f ab` | Gateway |
| Anti-Virus status | `cpstat antimalware -f av` | Gateway |
| Threat Emulation status | `cpstat threat_emulation` | Gateway |
| Content Awareness status | `cpstat content_awareness` | Gateway |
| HTTPS Inspection statistics | `cpstat https_inspection` | Gateway |
| Identity Awareness status | `pdp status stat` | Gateway |
| VPN tunnel status | `cpstat vpn` | Gateway |

### Blade Notes

- `cpstat blades` provides a single-command overview of all enabled blades and their status. Use this for initial blade inventory.
- Each blade-specific `cpstat` command provides counters (inspected, detected, prevented). Zero counters on an enabled blade may indicate misconfiguration or no matching traffic.
- Anti-Bot and Anti-Virus share the `antimalware` category; use the `-f ab` or `-f av` flag to query each independently.

## NAT and Connections

| Function | Command | Context |
|----------|---------|---------|
| NAT rulebase (API) | `mgmt_cli show nat-rulebase --format json -r true` | SMS |
| NAT translation table | `fw tab -t fwx_alloc -s` | Gateway |
| Connection table (summary) | `fw tab -t connections -s` | Gateway |
| Connection table (detail) | `fw tab -t connections -u` | Gateway |
| Active connections count | `cpstat fw -f policy` | Gateway |
| Session rate | `cpstat fw -f policy` (inspected/sec field) | Gateway |
| ARP table | `clish -c "show arp dynamic all"` | Gateway |

### NAT Notes

- `fw tab -t fwx_alloc -s` shows the NAT allocation table size and usage. High utilization may indicate NAT pool exhaustion for hide NAT.
- Cross-reference NAT table entries with security policy findings to identify static NAT objects that may need tighter access control.

## Sessions and Logging

| Function | Command | Context |
|----------|---------|---------|
| Log file list | `ls -la $FWDIR/log/` | Gateway/SMS |
| Recent log entries | `fw log -t` | Gateway |
| Log status (forwarding) | `cpstat logging` | Gateway |
| SmartLog query (API) | `mgmt_cli show logs filter "<query>" --format json -r true` | SMS |
| Audit log (admin actions) | `mgmt_cli show sessions --format json -r true` | SMS |
| Published sessions | `mgmt_cli show sessions --format json -r true` | SMS |

### Logging Notes

- `cpstat logging` shows log forwarding status and queue size. A growing queue indicates the gateway cannot forward logs fast enough — logs may be dropped.
- `fw log -t` tails the local log file. Useful for real-time verification that specific rules are generating log entries.
- SmartLog queries via API support the same filter syntax as the SmartConsole SmartLog view.

## Cluster and High Availability

| Function | Command | Context |
|----------|---------|---------|
| Cluster status | `cphaprob stat` | Gateway |
| Cluster members and state | `cphaprob -a if` | Gateway |
| Cluster sync status | `cphaprob syncstat` | Gateway |
| Interface status per member | `cphaprob -ia list` | Gateway |
| Failover history | `cphaprob -f list` | Gateway |
| VSX virtual systems | `vsx stat -v` | VSX Gateway |

### Cluster Notes

- `cphaprob stat` shows the HA state (Active/Standby/Down) and cluster member health. Both members should be visible.
- `cphaprob syncstat` reveals whether state synchronization (session table, policy) is functioning between members. Sync failures mean failover may drop sessions.

## Performance and Acceleration

| Function | Command | Context |
|----------|---------|---------|
| SecureXL status | `fwaccel stat` | Gateway |
| SecureXL template count | `fwaccel templates -S` | Gateway |
| CoreXL CPU allocation | `cpstat os -f multi_cpu` | Gateway |
| CoreXL SND/FW worker split | `fw ctl multik stat` | Gateway |
| Connection table capacity | `fw tab -t connections -s` | Gateway |
| Packet buffer utilization | `cpstat os -f memory` | Gateway |

### Performance Notes

- `fwaccel stat` shows SecureXL acceleration status and counters. "Accept templates" accelerate established sessions past the firewall kernel — verify that security-sensitive traffic is not being over-accelerated (bypassing blade inspection).
- `fw ctl multik stat` shows the CoreXL worker distribution. Uneven distribution can cause CPU bottlenecks on specific workers.

## Management API (Web API) Examples

For programmatic audit, the Management API is preferred over CLI scraping.
All `mgmt_cli` commands have equivalent HTTPS API calls.

| Function | API Call |
|----------|---------|
| Login (get session token) | `POST /web_api/login {"user":"<user>","password":"<pass>"}` |
| Show access layers | `POST /web_api/show-access-layers {}` |
| Show rulebase | `POST /web_api/show-access-rulebase {"name":"<layer>","details-level":"full"}` |
| Show NAT rulebase | `POST /web_api/show-nat-rulebase {}` |
| Show gateways | `POST /web_api/show-gateways-and-servers {}` |
| Show threat profiles | `POST /web_api/show-threat-profiles {}` |
| Show logs | `POST /web_api/show-logs {"filter":"<query>"}` |
| Logout | `POST /web_api/logout {}` |

### API Notes

- All API calls require a session token from `/web_api/login`. The token is passed in the `X-chkp-sid` header.
- For audit, use read-only credentials. The API enforces the same RBAC as SmartConsole.
- API calls use POST with JSON body, even for read operations. The base URL is `https://<sms-ip>/web_api/`.
- Use `"details-level": "full"` to get resolved object details instead of UIDs.
