# CIS Benchmark Control Reference — Network Device Audit Mapping

Copyright-safe reference mapping CIS benchmark control IDs and section
categories to audit areas and verification commands. This file cites CIS
control identifiers as factual references and provides independently-written
descriptions of configuration areas to audit.

**Copyright notice:** CIS benchmark documents are commercially licensed by
the Center for Internet Security. This reference does NOT reproduce benchmark
text, remediation instructions, rationale, or scoring methodology. Operators
must obtain their own licensed copy of the applicable CIS benchmark for full
control descriptions. Control IDs below are factual references for
traceability.

## Cisco IOS

### Management Plane

| CIS Section | Category | Config Area to Check | Audit CLI |
|-------------|----------|---------------------|-----------|
| 1.1.1 | AAA Services | Whether AAA is globally enabled for authentication | `show running-config \| include aaa new-model` |
| 1.1.2 | AAA Services | Whether AAA authentication is configured for login sessions | `show running-config \| section aaa authentication` |
| 1.1.3 | AAA Services | Whether AAA authorization is active for exec and command levels | `show running-config \| section aaa authorization` |
| 1.1.4 | AAA Services | Whether AAA accounting records login and command events | `show running-config \| section aaa accounting` |
| 1.2.1 | Access Rules | Whether only SSH (no Telnet) is permitted on VTY lines | `show running-config \| section line vty` |
| 1.2.2 | Access Rules | Whether ACLs restrict VTY access to authorized management hosts | `show running-config \| section line vty` |
| 1.2.3 | Access Rules | Whether auxiliary port is disabled | `show running-config \| section line aux` |
| 1.3.1 | Banner | Whether a login warning banner is configured | `show running-config \| include banner` |
| 1.4.1 | Password Management | Whether local user passwords use strong hashing | `show running-config \| include username` |
| 1.4.2 | Password Management | Whether enable secret uses type 9 (scrypt) hashing | `show running-config \| include enable` |
| 1.5.1 | SNMP | Whether SNMP community strings are non-default and access-restricted | `show snmp community` |
| 1.5.2 | SNMP | Whether SNMPv3 with auth and encryption is used instead of v1/v2c | `show snmp group` |
| 1.6.1 | Logging | Whether syslog is configured to send events to a remote server | `show running-config \| include logging host` |
| 1.6.2 | Logging | Whether logging includes timestamps with millisecond precision | `show running-config \| include service timestamps` |
| 1.7.1 | NTP | Whether NTP uses authenticated trusted sources | `show ntp associations` |

### Control Plane

| CIS Section | Category | Config Area to Check | Audit CLI |
|-------------|----------|---------------------|-----------|
| 2.1.1 | Routing Authentication | Whether OSPF neighbor authentication is configured per area | `show ip ospf interface \| include authentication` |
| 2.1.2 | Routing Authentication | Whether BGP neighbors require TCP MD5 or AO authentication | `show ip bgp neighbors \| include password` |
| 2.2.1 | Control Plane Protection | Whether CoPP policy is applied to the control plane | `show policy-map control-plane` |
| 2.3.1 | ARP Security | Whether Dynamic ARP Inspection is enabled on access VLANs | `show ip arp inspection vlan` |
| 2.3.2 | DHCP Security | Whether DHCP snooping is active on access VLANs | `show ip dhcp snooping` |

### Data Plane

| CIS Section | Category | Config Area to Check | Audit CLI |
|-------------|----------|---------------------|-----------|
| 3.1.1 | IP Filtering | Whether explicit deny with logging exists at ACL boundaries | `show ip access-lists` |
| 3.2.1 | uRPF | Whether unicast RPF is enabled on external-facing interfaces | `show ip interface \| include verify` |
| 3.3.1 | Storm Control | Whether broadcast storm control thresholds are set on access ports | `show storm-control broadcast` |
| 3.3.2 | Port Security | Whether 802.1X or port security limits MAC addresses on edge ports | `show dot1x all summary` |

## PAN-OS

### Management Plane

| CIS Section | Category | Config Area to Check | Audit CLI |
|-------------|----------|---------------------|-----------|
| 1.1.1 | Admin Access | Whether management interface access is restricted by source IP | `show running management-profile` |
| 1.1.2 | Admin Access | Whether idle timeout is configured for administrative sessions | `show config running \| match idle-timeout` |
| 1.2.1 | Authentication | Whether authentication profile is bound to admin accounts with external auth | `show config running \| match authentication-profile` |
| 1.2.2 | Authentication | Whether password complexity requirements are configured | `show config running \| match password-complexity` |
| 1.3.1 | Logging | Whether syslog forwarding is configured to a remote collector | `show config running \| match syslog` |
| 1.3.2 | Logging | Whether system, config, and traffic logs are forwarded | `show logging-status` |
| 1.4.1 | SNMP | Whether SNMPv3 is used with authPriv security level | `show config running \| match snmp` |
| 1.5.1 | Banner | Whether a login banner is configured on management interfaces | `show config running \| match login-banner` |

### Control Plane

| CIS Section | Category | Config Area to Check | Audit CLI |
|-------------|----------|---------------------|-----------|
| 2.1.1 | Routing Authentication | Whether OSPF area authentication is enabled | `show routing protocol ospf area` |
| 2.1.2 | Routing Authentication | Whether BGP peer authentication is configured | `show routing protocol bgp peer` |
| 2.2.1 | Session Protection | Whether DoS protection profiles are applied to critical zones | `show running dos-policy` |

### Data Plane

| CIS Section | Category | Config Area to Check | Audit CLI |
|-------------|----------|---------------------|-----------|
| 3.1.1 | Security Policy | Whether security policy has explicit deny-all at bottom with logging | `show running security-policy` |
| 3.1.2 | Security Policy | Whether allow rules bind Security Profile Groups for threat inspection | `show running profile-group` |
| 3.2.1 | Zone Protection | Whether zone protection profiles are assigned to all active L3 zones | `show running zone-protection-profile` |
| 3.3.1 | Decryption | Whether SSL decryption is enabled for internet-bound traffic | `show running ssl-decryption-policy` |

## JunOS

### Management Plane

| CIS Section | Category | Config Area to Check | Audit CLI |
|-------------|----------|---------------------|-----------|
| 1.1.1 | System Access | Whether TACACS+/RADIUS is configured as primary authentication source | `show configuration system authentication-order` |
| 1.1.2 | System Access | Whether root login is restricted to console only | `show configuration system root-authentication` |
| 1.2.1 | SSH | Whether only SSHv2 is enabled (no Telnet, no SSHv1) | `show configuration system services ssh` |
| 1.2.2 | SSH | Whether SSH rate limits and connection limits are configured | `show configuration system services ssh rate-limit` |
| 1.3.1 | Logging | Whether syslog targets include a remote host at appropriate severity | `show configuration system syslog` |
| 1.3.2 | SNMP | Whether SNMPv3 with USM authentication is configured | `show configuration snmp v3` |
| 1.4.1 | NTP | Whether NTP uses authentication keys for all configured servers | `show configuration system ntp` |
| 1.5.1 | Login | Whether login message/banner is configured | `show configuration system login message` |

### Control Plane

| CIS Section | Category | Config Area to Check | Audit CLI |
|-------------|----------|---------------------|-----------|
| 2.1.1 | Routing Authentication | Whether OSPF interfaces require authentication | `show ospf interface detail` |
| 2.1.2 | Routing Authentication | Whether BGP peers have authentication keys configured | `show bgp neighbor \| match AuthKey` |
| 2.2.1 | RE Protection | Whether firewall filter on lo0 protects the routing engine | `show configuration firewall filter` |
| 2.3.1 | ICMP Control | Whether ICMP rate limiting is configured | `show configuration firewall policer` |

### Data Plane

| CIS Section | Category | Config Area to Check | Audit CLI |
|-------------|----------|---------------------|-----------|
| 3.1.1 | Filtering | Whether firewall filters include discard with logging as final term | `show configuration firewall family inet` |
| 3.2.1 | uRPF | Whether RPF check is enabled on upstream interfaces | `show configuration interfaces \| match rpf-check` |
| 3.3.1 | Storm Control | Whether storm control is enabled on access-facing interfaces | `show configuration ethernet-switching-options storm-control` |

## Check Point

### Management Plane

| CIS Section | Category | Config Area to Check | Audit CLI |
|-------------|----------|---------------------|-----------|
| 1.1.1 | Admin Access | Whether management GUI access is restricted by source IP | `show web ssl-port` and `show allowed-client` |
| 1.1.2 | Admin Access | Whether session timeout is configured for GUI and CLI | `show inactivity-timeout` |
| 1.2.1 | Authentication | Whether RADIUS/TACACS+ is configured for administrator authentication | `show configuration aaa` |
| 1.2.2 | Password Policy | Whether password complexity and history rules are enforced | `show password-controls` |
| 1.3.1 | Logging | Whether logs are forwarded to a remote log server (SmartLog/syslog) | `show logging` |
| 1.3.2 | SNMP | Whether SNMPv3 is configured with authentication and privacy | `show snmp agent-version` |
| 1.4.1 | NTP | Whether NTP servers are configured with authentication | `show ntp servers` |
| 1.5.1 | Banner | Whether a warning message is configured for login | `show message banner` |

### Control Plane

| CIS Section | Category | Config Area to Check | Audit CLI |
|-------------|----------|---------------------|-----------|
| 2.1.1 | Routing Authentication | Whether OSPF authentication is enabled on routing interfaces | `show route ospf` and `show configuration ospf` |
| 2.2.1 | Connection Limits | Whether connection rate limiting is configured for the management plane | `show connections limit` |
| 2.3.1 | ARP Protection | Whether anti-spoofing is enabled on gateway interfaces | `fwaccel stat` and `fw ctl get int fw_antispoofing` |

### Data Plane

| CIS Section | Category | Config Area to Check | Audit CLI |
|-------------|----------|---------------------|-----------|
| 3.1.1 | Security Policy | Whether an explicit drop-all cleanup rule with logging exists at rulebase bottom | `fw stat -l` |
| 3.1.2 | Security Policy | Whether implied rules are reviewed and unnecessary ones disabled | `fw ctl get int implied_rules` |
| 3.2.1 | IPS | Whether IPS/Threat Prevention blade is enabled on security gateway | `enabled_blades` |
| 3.3.1 | HTTPS Inspection | Whether HTTPS inspection is enabled for outbound traffic | `show https-inspection policy` |
