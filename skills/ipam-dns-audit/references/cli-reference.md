# IPAM/DNS Audit CLI Reference

Commands and API patterns for IP address management auditing, DNS
record validation, and subnet discovery. Organized by function.

## DNS Query Tools

### dig (Domain Information Groper)

```bash
# Forward lookup — A record
dig +short example.com A

# Forward lookup against specific authoritative server
dig @ns1.example.com example.com A +norecurse

# Reverse lookup — PTR record
dig +short -x 10.1.1.50

# Zone transfer (requires AXFR permission)
dig @ns1.example.com example.com AXFR

# Check SOA serial for replication status
dig @ns1.example.com example.com SOA +short
dig @ns2.example.com example.com SOA +short

# MX record lookup
dig +short example.com MX

# NS delegation check
dig +short example.com NS

# CNAME chain trace
dig +trace +nodnssec www.example.com

# Batch forward/reverse consistency check
dig +short host1.example.com A | xargs -I{} dig +short -x {}
```

### nslookup

```bash
# Forward lookup
nslookup example.com

# Reverse lookup
nslookup 10.1.1.50

# Query specific server
nslookup example.com ns1.example.com

# Set record type
nslookup -type=MX example.com
nslookup -type=PTR 50.1.1.10.in-addr.arpa
```

### host

```bash
# Simple forward lookup
host example.com

# Reverse lookup
host 10.1.1.50

# Specific record type
host -t MX example.com
host -t NS example.com

# Verbose output with TTL
host -v example.com
```

## ARP / Neighbor Table Commands

### [Cisco IOS/IOS-XE]

```
show ip arp
show ip arp vrf <vrf-name>
show ip arp <interface>
show ip arp summary
show mac address-table
show mac address-table vlan <id>
```

### [Juniper JunOS]

```
show arp
show arp interface <interface>
show arp no-resolve
show ethernet-switching table
show ethernet-switching table vlan-name <name>
```

### [Arista EOS]

```
show ip arp
show ip arp vrf <vrf-name>
show ip arp summary
show mac address-table
show mac address-table vlan <id>
```

### Linux / Generic

```bash
# ARP table
ip neigh show
arp -an

# Specific subnet
ip neigh show dev eth0 | grep "10.1.1."

# IPv6 neighbor table
ip -6 neigh show
```

## DHCP Inspection Commands

### [Cisco IOS] — DHCP Server

```
show ip dhcp binding
show ip dhcp pool
show ip dhcp server statistics
show ip dhcp conflict
```

### [Cisco IOS] — DHCP Relay

```
show ip dhcp relay statistics
show ip helper-address
```

### ISC DHCP (Linux)

```bash
# Active leases
cat /var/lib/dhcpd/dhcpd.leases | grep -A5 "^lease"

# Scope utilization
dhcp-lease-list --parsable

# Configuration review
cat /etc/dhcp/dhcpd.conf | grep -E "^subnet|range"
```

### Windows DHCP Server (PowerShell)

```powershell
Get-DhcpServerv4Scope | Select-Object ScopeId, SubnetMask, State
Get-DhcpServerv4ScopeStatistics | Select-Object ScopeId, Free, InUse, PercentageInUse
Get-DhcpServerv4Lease -ScopeId 10.1.1.0
```

## Subnet Discovery Tools

```bash
# Ping sweep — identify active hosts
nmap -sn 10.1.1.0/24
fping -g 10.1.1.0/24 -a 2>/dev/null

# ARP scan (local subnet only)
arp-scan --localnet
arp-scan 10.1.1.0/24

# Subnet calculator
ipcalc 10.1.1.0/24
sipcalc 10.1.1.0/24
```

## IPAM API Patterns

### NetBox IPAM Module

```bash
# List prefixes in a VRF
curl -s -H "Authorization: Token <token>" \
  "https://<netbox>/api/ipam/prefixes/?vrf_id=<id>&limit=1000"

# List IP addresses in a prefix
curl -s -H "Authorization: Token <token>" \
  "https://<netbox>/api/ipam/ip-addresses/?parent=<prefix>&limit=1000"

# List VLANs
curl -s -H "Authorization: Token <token>" \
  "https://<netbox>/api/ipam/vlans/?site_id=<id>"

# Prefix utilization (built-in)
curl -s -H "Authorization: Token <token>" \
  "https://<netbox>/api/ipam/prefixes/<id>/available-ips/"

# Available prefixes within an aggregate
curl -s -H "Authorization: Token <token>" \
  "https://<netbox>/api/ipam/prefixes/<id>/available-prefixes/"
```

### Infoblox WAPI

```bash
# List networks in a view
curl -s -k -u "<user>:<pass>" \
  "https://<infoblox>/wapi/v2.12/network?network_view=default&_return_fields=network,comment,extattrs"

# List host records
curl -s -k -u "<user>:<pass>" \
  "https://<infoblox>/wapi/v2.12/record:host?zone=example.com&_return_fields=name,ipv4addrs"

# List A records
curl -s -k -u "<user>:<pass>" \
  "https://<infoblox>/wapi/v2.12/record:a?zone=example.com"

# Network utilization
curl -s -k -u "<user>:<pass>" \
  "https://<infoblox>/wapi/v2.12/network?network=10.1.0.0/16&_return_fields=network,utilization"

# DHCP range listing
curl -s -k -u "<user>:<pass>" \
  "https://<infoblox>/wapi/v2.12/range?network=10.1.1.0/24&_return_fields=start_addr,end_addr"
```

### BlueCat Address Manager REST v2

```bash
# List IPv4 networks in a block
curl -s -H "Authorization: Bearer <token>" \
  "https://<bluecat>/api/v2/ipv4Networks?containerId=<block-id>"

# List IPv4 addresses in a network
curl -s -H "Authorization: Bearer <token>" \
  "https://<bluecat>/api/v2/ipv4Addresses?networkId=<net-id>"

# DNS resource records
curl -s -H "Authorization: Bearer <token>" \
  "https://<bluecat>/api/v2/resourceRecords?zoneId=<zone-id>"
```

## Batch Validation Scripts

```bash
# Forward/reverse consistency check for a zone
dig @ns1.example.com example.com AXFR | \
  awk '/\tA\t/{print $1, $NF}' | \
  while read name ip; do
    ptr=$(dig +short -x "$ip" @ns1.example.com)
    if [ "$ptr" != "${name}" ]; then
      echo "MISMATCH: $name -> $ip -> PTR: $ptr"
    fi
  done

# IPAM vs ARP comparison (pseudocode pattern)
# 1. Export IPAM IPs: curl IPAM API → ipam_ips.txt
# 2. Collect ARP: show ip arp → arp_ips.txt
# 3. Compare:
comm -23 <(sort ipam_ips.txt) <(sort arp_ips.txt)  # IPAM-only (stale?)
comm -13 <(sort ipam_ips.txt) <(sort arp_ips.txt)  # ARP-only (undocumented)
comm -12 <(sort ipam_ips.txt) <(sort arp_ips.txt)  # Matched (verified)
```
