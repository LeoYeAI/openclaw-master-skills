# Network Forensics CLI Reference

Forensic data collection commands organized by evidence type across three
vendors. Commands are read-only unless explicitly noted. All output should
be redirected to a file or captured via terminal logging for chain-of-custody
preservation.

## Terminal Session Logging

Start a terminal log before collecting any evidence to create an audit trail.

| Vendor | Command | Notes |
|--------|---------|-------|
| **[Cisco]** | `terminal length 0` then redirect via SSH client logging | Disables paging for complete output capture |
| **[JunOS]** | `set cli screen-length 0` | Disables paging; use `| save /var/tmp/<file>` to save output |
| **[EOS]** | `terminal length 0` | Disables paging; use `| redirect flash:<file>` for on-device save |

## Packet Capture

Capture live traffic on device interfaces for full-content network evidence.

| Vendor | Command | Notes |
|--------|---------|-------|
| **[Cisco]** | `monitor capture CAP1 interface Gi0/0/0 both` | Define capture point on target interface |
| **[Cisco]** | `monitor capture CAP1 match any` | Set capture filter (refine with ACL for targeted capture) |
| **[Cisco]** | `monitor capture CAP1 start` | Begin capture — impacts CPU; monitor with `show processes cpu` |
| **[Cisco]** | `monitor capture CAP1 stop` | Stop capture |
| **[Cisco]** | `monitor capture CAP1 export flash:evidence.pcap` | Export to file for offline analysis |
| **[Cisco]** | `show monitor capture CAP1` | Verify capture status and packet count |
| **[JunOS]** | `monitor traffic interface ge-0/0/0 size 1500 write-file /var/tmp/capture.pcap` | Capture to file; add `matching "host 10.1.1.1"` for filtering |
| **[JunOS]** | `monitor traffic interface ge-0/0/0 no-resolve` | Live display without DNS resolution |
| **[EOS]** | `bash tcpdump -i et1 -w /mnt/flash/evidence.pcap -c 10000` | EOS shell-based capture; `-c` limits packet count |
| **[EOS]** | `monitor session 1 source Et1 both` | ERSPAN/mirror session for span-based capture |
| **[EOS]** | `monitor session 1 destination Cpu` | Direct mirrored traffic to CPU for local capture |

## Flow Export Verification

Verify that NetFlow/sFlow/IPFIX is configured and exporting flow records
to the collection infrastructure.

| Vendor | Command | Notes |
|--------|---------|-------|
| **[Cisco]** | `show flow monitor` | Shows configured flow monitors and cache status |
| **[Cisco]** | `show flow monitor <name> cache` | Displays cached flow records — confirm active flows |
| **[Cisco]** | `show flow exporter <name> statistics` | Export statistics — verify packets sent to collector |
| **[Cisco]** | `show flow interface` | Shows which interfaces have flow monitors applied |
| **[JunOS]** | `show services flow-monitoring version-ipfix template` | IPFIX template verification |
| **[JunOS]** | `show services flow-monitoring version9 template` | NetFlow v9 template verification |
| **[JunOS]** | `show services accounting status` | Flow accounting status and record counts |
| **[JunOS]** | `show services accounting flow` | Active flow table contents |
| **[EOS]** | `show flow tracking` | Flow tracking configuration and status |
| **[EOS]** | `show flow tracking hardware` | Hardware flow table utilization |
| **[EOS]** | `show flow tracking counters` | Export counters — verify records sent |

## ARP / MAC / CAM Tables

Layer 2 and Layer 3 address mapping — critical for identifying which
hosts were connected to which ports at the time of the incident.

| Vendor | Command | Notes |
|--------|---------|-------|
| **[Cisco]** | `show arp` | Full ARP table — IP-to-MAC mappings |
| **[Cisco]** | `show arp \| include <ip>` | Filter ARP for specific IP address |
| **[Cisco]** | `show mac address-table` | Full CAM table — MAC-to-port mappings |
| **[Cisco]** | `show mac address-table address <mac>` | Locate specific MAC address |
| **[Cisco]** | `show mac address-table interface <intf>` | MACs learned on a specific port |
| **[JunOS]** | `show arp no-resolve` | ARP table without DNS resolution |
| **[JunOS]** | `show arp interface <intf>` | ARP entries on specific interface |
| **[JunOS]** | `show ethernet-switching table` | MAC address table (switching platforms) |
| **[JunOS]** | `show ethernet-switching table interface <intf>` | MACs on specific port |
| **[EOS]** | `show arp` | Full ARP table |
| **[EOS]** | `show arp <ip>` | ARP entry for specific IP |
| **[EOS]** | `show mac address-table` | Full MAC/CAM table |
| **[EOS]** | `show mac address-table address <mac>` | Locate specific MAC |

## Routing Table Snapshots

Routing state captures for path analysis — identifies how traffic was
forwarded at the time of the incident and whether routing changes occurred.

| Vendor | Command | Notes |
|--------|---------|-------|
| **[Cisco]** | `show ip route` | Full IPv4 routing table |
| **[Cisco]** | `show ip route <prefix>` | Specific route lookup |
| **[Cisco]** | `show ip route summary` | Route count by protocol — quick delta check |
| **[Cisco]** | `show ip bgp summary` | BGP peer status and prefix counts |
| **[Cisco]** | `show ip ospf neighbor` | OSPF adjacency state |
| **[JunOS]** | `show route` | Full routing table |
| **[JunOS]** | `show route <prefix> detail` | Detailed route with communities, AS path |
| **[JunOS]** | `show route summary` | Route count by protocol |
| **[JunOS]** | `show bgp summary` | BGP peer status |
| **[JunOS]** | `show ospf neighbor` | OSPF adjacency state |
| **[EOS]** | `show ip route` | Full IPv4 routing table |
| **[EOS]** | `show ip route <prefix>` | Specific route lookup |
| **[EOS]** | `show ip route summary` | Route count by protocol |
| **[EOS]** | `show ip bgp summary` | BGP peer status |
| **[EOS]** | `show ip ospf neighbor` | OSPF adjacency state |

## ACL Hit Counts (Containment Verification)

Read-only verification that containment ACLs are matching and blocking
traffic. These commands confirm that previously applied containment
measures are effective — they do not modify any device configuration.

| Vendor | Command | Notes |
|--------|---------|-------|
| **[Cisco]** | `show access-lists` | All ACLs with hit counters |
| **[Cisco]** | `show access-lists <name>` | Specific ACL with per-rule match counts |
| **[Cisco]** | `show ip access-lists <name>` | IP-specific ACL detail |
| **[JunOS]** | `show firewall` | All firewall filter counters |
| **[JunOS]** | `show firewall filter <name>` | Specific filter term counters |
| **[JunOS]** | `show firewall filter <name> counter <counter-name>` | Individual counter value |
| **[EOS]** | `show access-lists` | All ACLs with counters |
| **[EOS]** | `show access-lists <name>` | Specific ACL with per-entry match counts |
| **[EOS]** | `show ip access-lists counters` | Aggregated ACL counter summary |

## SNMP Trap and Syslog Verification

Verify logging and trap configuration to confirm that device events are
reaching the centralized logging/SIEM infrastructure.

| Vendor | Command | Notes |
|--------|---------|-------|
| **[Cisco]** | `show logging` | Syslog config: destination, severity, buffered log entries |
| **[Cisco]** | `show logging history` | Recent syslog messages sent to remote servers |
| **[Cisco]** | `show snmp` | SNMP configuration and trap destinations |
| **[Cisco]** | `show snmp host` | SNMP trap receiver list |
| **[JunOS]** | `show system syslog` | Syslog host configuration |
| **[JunOS]** | `show log messages \| last 20` | Recent syslog entries on device |
| **[JunOS]** | `show snmp statistics` | SNMP trap/inform counters |
| **[JunOS]** | `show configuration snmp` | SNMP trap target configuration |
| **[EOS]** | `show logging` | Syslog config and recent buffered entries |
| **[EOS]** | `show logging host` | Remote syslog server configuration |
| **[EOS]** | `show snmp` | SNMP configuration overview |
| **[EOS]** | `show snmp host` | SNMP trap receiver list |

## Evidence Preservation Commands

Save evidence to persistent storage — critical for chain-of-custody.
Commands below are write-to-file operations for evidence archival.

| Vendor | Command | Notes |
|--------|---------|-------|
| **[Cisco]** | `show tech-support \| redirect flash:tech-support-<date>.txt` | Comprehensive state capture |
| **[Cisco]** | `copy running-config flash:running-<date>.cfg` | Running config snapshot |
| **[JunOS]** | `request support information \| save /var/tmp/tech-support-<date>.txt` | Comprehensive state capture |
| **[JunOS]** | `show configuration \| save /var/tmp/config-<date>.txt` | Active config snapshot |
| **[EOS]** | `show tech-support \| redirect flash:tech-support-<date>.txt` | Comprehensive state capture |
| **[EOS]** | `copy running-config flash:running-<date>.cfg` | Running config snapshot |
