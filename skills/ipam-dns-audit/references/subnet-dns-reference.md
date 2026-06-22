# Subnet and DNS Reference

Reference material for IPAM/DNS auditing: RFC address allocation
guidance, CIDR notation, DNS record types, DHCP scope planning,
and IPv6 addressing patterns.

## RFC 1918 / RFC 6598 Private Address Space

| Block | Range | CIDR | Usable Hosts | Typical Use |
|-------|-------|------|-------------|-------------|
| Class A | 10.0.0.0 – 10.255.255.255 | 10.0.0.0/8 | 16,777,214 | Large enterprise, data center |
| Class B | 172.16.0.0 – 172.31.255.255 | 172.16.0.0/12 | 1,048,574 | Medium enterprise, branch |
| Class C | 192.168.0.0 – 192.168.255.255 | 192.168.0.0/16 | 65,534 | Small office, lab, home |
| CGN (RFC 6598) | 100.64.0.0 – 100.127.255.255 | 100.64.0.0/10 | 4,194,302 | Carrier-grade NAT |

### Special-Use Addresses

| Block | Purpose | RFC |
|-------|---------|-----|
| 127.0.0.0/8 | Loopback | RFC 1122 |
| 169.254.0.0/16 | Link-local (APIPA) | RFC 3927 |
| 192.0.2.0/24 | Documentation (TEST-NET-1) | RFC 5737 |
| 198.51.100.0/24 | Documentation (TEST-NET-2) | RFC 5737 |
| 203.0.113.0/24 | Documentation (TEST-NET-3) | RFC 5737 |
| 198.18.0.0/15 | Benchmarking | RFC 2544 |

## CIDR Notation and Subnet Math

### Common Subnet Sizes

| CIDR | Mask | Total | Usable | Typical Use |
|------|------|-------|--------|-------------|
| /30 | 255.255.255.252 | 4 | 2 | Point-to-point link |
| /29 | 255.255.255.248 | 8 | 6 | Small management VLAN |
| /28 | 255.255.255.240 | 16 | 14 | DMZ, small server VLAN |
| /27 | 255.255.255.224 | 32 | 30 | Wireless AP management |
| /26 | 255.255.255.192 | 64 | 62 | Small user VLAN |
| /25 | 255.255.255.128 | 128 | 126 | Medium user VLAN |
| /24 | 255.255.255.0 | 256 | 254 | Standard user VLAN |
| /23 | 255.255.254.0 | 512 | 510 | Large user VLAN |
| /22 | 255.255.252.0 | 1024 | 1022 | Campus building |
| /21 | 255.255.248.0 | 2048 | 2046 | Large campus segment |
| /20 | 255.255.240.0 | 4096 | 4094 | Data center pod |
| /16 | 255.255.0.0 | 65536 | 65534 | Site aggregate |

### Utilization Calculation

```
Usable addresses = 2^(32 - prefix_length) - 2  (subtract network + broadcast)
Utilization % = (assigned_addresses / usable_addresses) × 100

Example: 10.1.1.0/24
  Total addresses: 256
  Usable addresses: 254
  Assigned in IPAM: 203
  Utilization: 203/254 = 79.9% (warning threshold)
```

### Reserved Addresses Per Subnet

- First address: Network address (not assignable)
- Second address (.1): Gateway (convention, reserved in IPAM)
- Third address (.2–.3): HSRP/VRRP VIPs (if applicable)
- Last address: Broadcast (not assignable)
- DHCP range: Typically starts after static reservations

## DNS Record Types

| Type | Purpose | Example | Audit Focus |
|------|---------|---------|-------------|
| A | IPv4 forward mapping | host.example.com → 10.1.1.50 | Forward/reverse consistency |
| AAAA | IPv6 forward mapping | host.example.com → 2001:db8::50 | IPv6 adoption tracking |
| PTR | Reverse mapping | 50.1.1.10.in-addr.arpa → host.example.com | Must match A record |
| CNAME | Canonical name alias | www → webserver.example.com | Chain length, apex violations |
| MX | Mail exchanger | example.com → mail.example.com (pri 10) | Must resolve to A, not CNAME |
| NS | Name server delegation | example.com → ns1.example.com | Must be responsive |
| SOA | Start of authority | Zone metadata, serial, refresh | Serial consistency across servers |
| SRV | Service locator | _ldap._tcp.example.com | AD/LDAP infrastructure health |
| TXT | Text record | SPF, DKIM, DMARC | Mail security configuration |

### DNS Hierarchy and Zones

```
Root (.)
├─ .com
│  └─ example.com (forward zone)
│     ├─ A records (host → IP)
│     ├─ CNAME records (alias → canonical)
│     ├─ MX records (mail routing)
│     └─ sub.example.com (delegated zone)
└─ .arpa
   └─ in-addr.arpa
      └─ 10.in-addr.arpa (reverse zone for 10.0.0.0/8)
         └─ 1.10.in-addr.arpa (/16 delegation)
            └─ 1.1.10.in-addr.arpa (/24 reverse zone)
               └─ PTR records (IP → host)
```

## DHCP Scope Planning

### Scope Sizing Guidelines

| Environment | Scope Size | Lease Time | Free Buffer |
|-------------|-----------|------------|-------------|
| Corporate wired | /24 per VLAN | 8–24 hours | 20% |
| Corporate wireless | /23 or /22 | 4–8 hours | 25% |
| Guest wireless | /22 or larger | 1–4 hours | 30% |
| IoT / BYOD | Dedicated /24 | 12–24 hours | 15% |
| VoIP phones | Dedicated VLAN /24 | 8 hours | 20% |
| Server / infra | Static only | N/A | N/A |

### Lease Time Considerations

- **Shorter leases** (1–4 hours): Higher DHCP server load, faster
  reclamation of addresses in high-turnover environments (guest WiFi,
  conference rooms)
- **Longer leases** (8–24 hours): Lower server load, risk of address
  exhaustion if many devices connect/disconnect without releasing leases
- **Infinite leases**: Avoid — creates IPAM stale entries, prevents
  address reclamation

### Scope Health Indicators

```
Free percentage = (total_scope - active_leases) / total_scope × 100

Healthy: >20% free
Warning: 10–20% free — plan expansion
Critical: <10% free — immediate action needed

Exhaustion projection:
  days_remaining = free_addresses / daily_growth_rate
  If days_remaining < 30: immediate expansion needed
```

## IPv6 Addressing Scheme Patterns

### Standard Enterprise Allocation

```
2001:db8::/32          (Provider allocation)
├─ 2001:db8:0001::/48  (Site 1 — headquarters)
│  ├─ 2001:db8:0001:0001::/64  (VLAN 1 — servers)
│  ├─ 2001:db8:0001:0002::/64  (VLAN 2 — users)
│  └─ 2001:db8:0001:000A::/64  (VLAN 10 — management)
├─ 2001:db8:0002::/48  (Site 2 — branch)
│  └─ ...
└─ 2001:db8:00FF::/48  (Infrastructure — loopbacks, p2p)
   ├─ 2001:db8:00FF:0000::/127  (P2P link — /127 per RFC 6164)
   └─ 2001:db8:00FF:FF00::1/128 (Loopback)
```

### IPv6 Audit Focus Areas

- /48 per site allocation consistency
- /64 per VLAN (never subnet smaller than /64 for SLAAC)
- Point-to-point links: /127 (RFC 6164), not /64
- Loopbacks: /128
- GUA vs ULA usage policy compliance
- Reverse DNS (ip6.arpa) zone delegation for allocated prefixes
