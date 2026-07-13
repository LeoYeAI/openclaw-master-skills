# CIS Benchmark Audit CLI Reference — Read-Only Commands

Read-only verification commands organized by CIS benchmark category
(Management Plane, Control Plane, Data Plane) for each supported platform.
All commands are non-modifying — suitable for production audit without
change risk.

## Cisco IOS

### Management Plane

| Function | CLI Command |
|----------|-------------|
| AAA configuration status | `show running-config \| section aaa` |
| Authentication methods for login | `show running-config \| include aaa authentication` |
| Authorization configuration | `show running-config \| include aaa authorization` |
| Accounting configuration | `show running-config \| include aaa accounting` |
| VTY line access settings | `show running-config \| section line vty` |
| Console line settings | `show running-config \| section line con` |
| Auxiliary port status | `show running-config \| section line aux` |
| SSH version and settings | `show ip ssh` |
| SSH active sessions | `show ssh` |
| User accounts and privilege levels | `show running-config \| include username` |
| Enable secret hash type | `show running-config \| include enable` |
| SNMP community strings | `show snmp community` |
| SNMP group and security model | `show snmp group` |
| SNMP v3 users | `show snmp user` |
| Syslog configuration | `show running-config \| include logging` |
| Logging buffer and severity | `show logging` |
| NTP server associations | `show ntp associations` |
| NTP authentication status | `show ntp status` |
| Service timestamps configuration | `show running-config \| include service timestamps` |
| Banner configuration | `show running-config \| include banner` |
| HTTP/HTTPS server status | `show running-config \| include ip http` |

### Control Plane

| Function | CLI Command |
|----------|-------------|
| OSPF interface authentication | `show ip ospf interface` |
| OSPF neighbor status | `show ip ospf neighbor` |
| BGP neighbor summary and auth | `show ip bgp neighbors` |
| IS-IS adjacency status | `show isis neighbors` |
| CoPP policy on control plane | `show policy-map control-plane` |
| ARP inspection status per VLAN | `show ip arp inspection vlan` |
| ARP inspection statistics | `show ip arp inspection statistics` |
| DHCP snooping status | `show ip dhcp snooping` |
| DHCP snooping binding table | `show ip dhcp snooping binding` |
| ICMP redirects setting | `show running-config \| include ip redirects` |
| IP source guard bindings | `show ip source binding` |
| CDP/LLDP neighbor status | `show cdp neighbors` |

### Data Plane

| Function | CLI Command |
|----------|-------------|
| All IP access lists | `show ip access-lists` |
| ACL hit counts | `show access-lists` |
| uRPF status per interface | `show ip interface \| include verify` |
| Storm control settings | `show storm-control broadcast` |
| Port security status | `show port-security` |
| 802.1X authentication status | `show dot1x all summary` |
| Spanning tree status | `show spanning-tree summary` |
| IP CEF status | `show ip cef` |
| Interface error counters | `show interfaces counters errors` |

## PAN-OS

### Management Plane

| Function | CLI Command |
|----------|-------------|
| System version and platform info | `show system info` |
| Management interface access profile | `show running management-profile` |
| Admin session idle timeout | `show config running \| match idle-timeout` |
| Authentication profiles | `show config running \| match authentication-profile` |
| Password complexity settings | `show config running \| match password-complexity` |
| SNMP configuration | `show config running \| match snmp` |
| Syslog forwarding configuration | `show config running \| match syslog` |
| Log forwarding status | `show logging-status` |
| NTP server configuration | `show ntp` |
| Login banner setting | `show config running \| match login-banner` |
| Admin account list | `show admins all` |
| Content update versions | `show system info \| match version` |
| License status | `show system license` |

### Control Plane

| Function | CLI Command |
|----------|-------------|
| OSPF area configuration | `show routing protocol ospf area` |
| OSPF neighbor status | `show routing protocol ospf neighbor` |
| BGP peer configuration | `show routing protocol bgp peer` |
| BGP peer status | `show routing protocol bgp summary` |
| DoS protection policies | `show running dos-policy` |
| Session table summary | `show session info` |
| HA status | `show high-availability all` |
| Panorama connection status | `show panorama-status` |

### Data Plane

| Function | CLI Command |
|----------|-------------|
| Full security policy (effective) | `show running security-policy` |
| Security policy hit counts | `show rule-hit-count vsys vsys1 security rules all` |
| Security Profile Groups | `show running profile-group` |
| Zone configuration and assignments | `show running zone` |
| Zone protection profiles | `show running zone-protection-profile` |
| NAT policy | `show running nat-policy` |
| Decryption policy | `show running ssl-decryption-policy` |
| Active sessions by zone pair | `show session all filter from <zone> to <zone>` |
| Policy match test | `test security-policy-match source <IP> destination <IP> protocol <num> destination-port <port> from <zone> to <zone>` |

## JunOS

### Management Plane

| Function | CLI Command |
|----------|-------------|
| Authentication order | `show configuration system authentication-order` |
| Login user accounts | `show configuration system login` |
| Root authentication settings | `show configuration system root-authentication` |
| SSH service configuration | `show configuration system services ssh` |
| SSH rate limit settings | `show configuration system services ssh rate-limit` |
| Telnet service status | `show configuration system services telnet` |
| RADIUS server configuration | `show configuration system radius-server` |
| TACACS+ server configuration | `show configuration system tacplus-server` |
| Syslog configuration | `show configuration system syslog` |
| SNMPv3 configuration | `show configuration snmp v3` |
| SNMP community settings | `show configuration snmp community` |
| NTP configuration | `show configuration system ntp` |
| NTP association status | `show ntp associations` |
| Login banner/message | `show configuration system login message` |
| Web management status | `show configuration system services web-management` |
| System services summary | `show configuration system services` |

### Control Plane

| Function | CLI Command |
|----------|-------------|
| OSPF interface detail and auth | `show ospf interface detail` |
| OSPF neighbor status | `show ospf neighbor` |
| BGP neighbor authentication | `show bgp neighbor` |
| IS-IS adjacency detail | `show isis adjacency detail` |
| Routing engine firewall filter | `show configuration firewall filter` |
| Loopback filter application | `show configuration interfaces lo0` |
| Policer configuration | `show configuration firewall policer` |
| Routing table summary | `show route summary` |

### Data Plane

| Function | CLI Command |
|----------|-------------|
| Firewall filter families | `show configuration firewall family inet` |
| Firewall filter counters | `show firewall` |
| RPF check configuration | `show configuration interfaces \| match rpf-check` |
| Storm control settings | `show configuration ethernet-switching-options storm-control` |
| 802.1X configuration | `show configuration protocols dot1x` |
| Interface filter assignments | `show interfaces filters` |
| Flow session table | `show security flow session summary` |

## Check Point

### Management Plane

| Function | CLI Command |
|----------|-------------|
| Gaia OS version | `show version all` |
| Firewall version | `fw ver` |
| Platform info | `cpinfo -y all` |
| Web interface SSL port | `show web ssl-port` |
| Allowed management clients | `show allowed-client` |
| Session inactivity timeout | `show inactivity-timeout` |
| AAA configuration | `show configuration aaa` |
| Password policy controls | `show password-controls` |
| SNMP agent version | `show snmp agent-version` |
| SNMP configuration | `show snmp` |
| Syslog/log forwarding | `show logging` |
| NTP servers configured | `show ntp servers` |
| NTP current status | `show ntp current` |
| Login banner | `show message banner` |
| Active administrators | `show users` |
| Interface configuration | `show interfaces all` |

### Control Plane

| Function | CLI Command |
|----------|-------------|
| OSPF routing configuration | `show route ospf` |
| OSPF config detail | `show configuration ospf` |
| BGP summary | `show route bgp` |
| Connection rate limits | `show connections limit` |
| Anti-spoofing status | `fwaccel stat` |
| Cluster status (HA) | `cphaprob stat` |
| SecureXL acceleration status | `fwaccel stat` |

### Data Plane

| Function | CLI Command |
|----------|-------------|
| Firewall policy status | `fw stat -l` |
| Security policy rule count | `fw stat` |
| Active connections table | `fw tab -t connections -s` |
| Implied rules status | `fw ctl get int implied_rules` |
| Enabled software blades | `enabled_blades` |
| IPS/Threat Prevention status | `cpstat -f all threat_prevention` |
| HTTPS inspection policy | `show https-inspection policy` |
| Interface statistics | `show interfaces all` |
| Routing table | `show route` |
