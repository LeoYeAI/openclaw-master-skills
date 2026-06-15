# Azure VNet Architecture Reference

Reference for VNet packet processing, NSG evaluation order, Azure Firewall
processing pipeline, ExpressRoute routing model, and VNet Peering topology
constraints. This documents how Azure evaluates and routes traffic — the
foundation for understanding networking audit findings.

## VNet Packet Flow Model

When a packet enters or exits a VM within a VNet, Azure evaluates multiple
networking constructs in a defined order. Understanding this order is
essential for diagnosing NSG, UDR, and Azure Firewall findings.

### Inbound Packet Flow (Network → VM)

```
Packet arrives at subnet
       │
       ▼
┌─────────────────────────┐
│  UDR / Route Table      │  If UDR exists on subnet, route evaluation
│  (if applicable)        │  determines next-hop before NSG processing
└─────────────────────────┘
       │
       ▼
┌─────────────────────────┐
│  Subnet NSG             │  Priority-based — lowest number evaluated first
│  Inbound Rules          │  First match wins (Allow or Deny)
│                         │  Default: AllowVNetInBound (65000),
│                         │  DenyAllInBound (65500)
└─────────────────────────┘
       │ Permitted
       ▼
┌─────────────────────────┐
│  NIC NSG                │  Second layer — evaluated after subnet NSG
│  Inbound Rules          │  Same priority-based evaluation
│                         │  Traffic must pass BOTH NSGs
└─────────────────────────┘
       │ Permitted
       ▼
  Packet delivered to VM NIC
```

### Outbound Packet Flow (VM → Network)

```
VM sends packet
       │
       ▼
┌─────────────────────────┐
│  NIC NSG                │  Outbound rules evaluated first (NIC level)
│  Outbound Rules         │  Default: AllowVNetOutBound (65000),
│                         │  AllowInternetOutBound (65001),
│                         │  DenyAllOutBound (65500)
└─────────────────────────┘
       │ Permitted
       ▼
┌─────────────────────────┐
│  Subnet NSG             │  Outbound rules evaluated second (subnet level)
│  Outbound Rules         │  Same priority-based evaluation
└─────────────────────────┘
       │ Permitted
       ▼
┌─────────────────────────┐
│  Route Table            │  UDR routes > BGP routes > system routes
│  Route Selection        │  Longest prefix match within each category
│                         │  Next-hop: VNet, Internet, Virtual Appliance,
│                         │  VNet Gateway, VNet Peering, None
└─────────────────────────┘
       │
       ▼
  Packet exits subnet
```

### Key Difference from AWS

In Azure, NSG evaluation order reverses between inbound and outbound:

- **Inbound:** Subnet NSG → NIC NSG (outside-in)
- **Outbound:** NIC NSG → Subnet NSG (inside-out)

Traffic must pass BOTH NSGs. A Deny in either NSG blocks the traffic
regardless of the other NSG's rules. This differs from AWS where Security
Groups (instance-level) and NACLs (subnet-level) evaluate independently
with different statefulness models.

## NSG Rule Evaluation Model

Azure NSG rules use a priority-based first-match model, fundamentally
different from AWS Security Groups (which evaluate all rules and permit
if any match).

### Priority System

- Priority range: 100–4096 (custom rules) and 65000–65500 (default rules)
- **Lower number = higher priority** — rule at priority 100 is evaluated before priority 200
- First matching rule determines action (Allow or Deny) — subsequent rules not evaluated
- Default rules (65000+) cannot be deleted but are overridden by any custom rule

### Default Rules (Always Present)

**Inbound defaults:**

| Priority | Name | Source | Destination | Action |
|----------|------|--------|-------------|--------|
| 65000 | AllowVNetInBound | VirtualNetwork | VirtualNetwork | Allow |
| 65001 | AllowAzureLoadBalancerInBound | AzureLoadBalancer | * | Allow |
| 65500 | DenyAllInBound | * | * | Deny |

**Outbound defaults:**

| Priority | Name | Source | Destination | Action |
|----------|------|--------|-------------|--------|
| 65000 | AllowVNetOutBound | VirtualNetwork | VirtualNetwork | Allow |
| 65001 | AllowInternetOutBound | * | Internet | Allow |
| 65500 | DenyAllOutBound | * | * | Deny |

### Service Tags

Azure NSG rules support service tags as source or destination instead of
IP ranges. Key service tags for audit:

| Service Tag | Scope |
|-------------|-------|
| VirtualNetwork | VNet address space + peered VNets + on-prem (VPN/ER) |
| AzureLoadBalancer | Azure health probes |
| Internet | All public IP space (excludes VNet/peered/on-prem) |
| AzureCloud | All Azure datacenter IPs |
| Storage | Azure Storage service IPs (region-specific available) |
| Sql | Azure SQL Database service IPs |
| AzureActiveDirectory | Azure AD authentication endpoints |

### Effective Security Rules Resolution

When both subnet NSG and NIC NSG exist, Azure computes effective rules:

```
For inbound traffic:
  1. Evaluate subnet NSG rules by priority → Allow or Deny
  2. If subnet NSG allows, evaluate NIC NSG rules by priority → Allow or Deny
  3. Traffic reaches VM only if BOTH NSGs allow

For outbound traffic:
  1. Evaluate NIC NSG rules by priority → Allow or Deny
  2. If NIC NSG allows, evaluate subnet NSG rules by priority → Allow or Deny
  3. Traffic exits only if BOTH NSGs allow
```

Use `az network nic show-effective-nsg` to see the computed effective
rules for a NIC, combining both NSG layers with resolved priorities.

## Azure Firewall Processing Pipeline

Azure Firewall processes traffic through rule collections in a strict
priority and type order.

### Processing Order

```
Traffic arrives at Azure Firewall
       │
       ▼
┌─────────────────────────┐
│  DNAT Rule Collections  │  Processed first (inbound only)
│  (priority order)       │  Translates destination IP/port to private IP
│                         │  If matched → implicitly allows via network rule
└─────────────────────────┘
       │ No DNAT match
       ▼
┌─────────────────────────┐
│  Network Rule           │  Processed second
│  Collections            │  L3/L4 rules (IP, port, protocol)
│  (priority order)       │  Allow or Deny
└─────────────────────────┘
       │ No network rule match
       ▼
┌─────────────────────────┐
│  Application Rule       │  Processed last
│  Collections            │  L7 rules (FQDN, URL, web categories)
│  (priority order)       │  Allow or Deny
└─────────────────────────┘
       │ No match in any collection
       ▼
  Default action: DENY (implicit deny-all)
```

### Rule Collection Groups

Rule collection groups provide hierarchical organization:

- **Rule Collection Group** (has priority) → contains Rule Collections
- **Rule Collection** (has priority and action: Allow/Deny) → contains Rules
- Groups are processed by priority (lowest first)
- Within a group, collections are processed by priority
- Within a collection, rules are processed sequentially

### Azure Firewall Premium Features

| Feature | Standard | Premium |
|---------|----------|---------|
| L3/L4 network rules | ✓ | ✓ |
| FQDN application rules | ✓ | ✓ |
| Threat intelligence | ✓ | ✓ |
| TLS inspection | ✗ | ✓ |
| IDPS | ✗ | ✓ (signature-based) |
| URL filtering | ✗ | ✓ (full URL path) |
| Web categories | ✗ | ✓ (expanded set) |

## ExpressRoute Routing Model

ExpressRoute provides private connectivity from on-premises networks to
Azure VNets through connectivity providers or direct connections.

### ExpressRoute Circuit Architecture

```
On-Premises Router ──── Provider Edge ──── Microsoft Edge (MSEE)
                              │                    │
                     Primary Connection    Secondary Connection
                              │                    │
                              └────────────────────┘
                                       │
                              ExpressRoute Circuit
                                       │
                              ┌────────┴────────┐
                              │                 │
                      Azure Private      Microsoft Peering
                        Peering           (Microsoft 365,
                      (VNets)             Azure PaaS public)
```

### BGP Route Exchange

- **Azure Private Peering:** On-premises advertises on-prem routes; Azure advertises VNet address spaces. Routes are exchanged via BGP over the primary and secondary connections.
- **Route propagation to VNets:** ExpressRoute Gateway in the GatewaySubnet receives BGP routes and injects them into VNet route tables (unless UDR disables BGP propagation).
- **AS path and MED:** When multiple circuits or paths exist, BGP AS path length and MED values determine route preference. Shorter AS path wins.

### ExpressRoute and VNet Peering Integration

```
On-Premises ──── ExpressRoute ──── Hub VNet (Gateway)
                                       │
                                  VNet Peering
                                  (Gateway Transit)
                                       │
                                  Spoke VNet
```

- **Gateway Transit:** Hub VNet peering must set `AllowGatewayTransit: true`. Spoke VNet peering must set `UseRemoteGateways: true`. This enables spoke VNets to use the hub's ExpressRoute Gateway.
- **Route injection:** ExpressRoute-learned routes propagate through the hub VNet to spoke VNets via peering when gateway transit is configured.
- **Maximum prefixes:** ExpressRoute Standard supports 4,000 routes for Azure Private Peering. Premium supports 10,000. Exceeding the limit causes BGP session drops.

## VNet Peering Topology Constraints

VNet Peering creates a direct networking link between two VNets using
Azure backbone infrastructure (no public internet, no encryption needed).

### Peering Properties

| Property | Setting | Impact |
|----------|---------|--------|
| AllowVirtualNetworkAccess | true (default) | VNet address space included in VirtualNetwork service tag |
| AllowForwardedTraffic | false (default) | If false, blocks traffic forwarded by NVA in peer VNet |
| AllowGatewayTransit | false (default) | If true on hub, allows peers to use this VNet's gateway |
| UseRemoteGateways | false (default) | If true on spoke, uses peer VNet's gateway for on-prem routes |

### Topology Constraints

| Constraint | Detail |
|------------|--------|
| Non-transitive | VNet-A↔VNet-B and VNet-B↔VNet-C does NOT allow VNet-A↔VNet-C |
| No overlapping address spaces | Peering fails if VNet address spaces overlap |
| Cross-region supported | Global VNet Peering supported (cross-region data transfer charges apply) |
| Bi-directional creation required | Both VNets must create peering links; one-sided = "Initiated" state |
| No edge-to-edge routing (by default) | Cannot use peer's gateway or NVA without explicit settings |
| Maximum peerings per VNet | 500 (default limit, adjustable via support) |

### Hub-Spoke Topology Pattern

```
                    Spoke VNet A ── Peering ──┐
                                              │
On-Premises ── ER/VPN ── Hub VNet ─── Azure Firewall
                                              │
                    Spoke VNet B ── Peering ──┘

Hub VNet settings:
  - AllowGatewayTransit: true (share ER/VPN gateway)
  - Azure Firewall or NVA for inter-spoke inspection

Spoke VNet settings:
  - UseRemoteGateways: true (use hub's gateway)
  - AllowForwardedTraffic: true (accept NVA-forwarded traffic)
  - UDR: 0.0.0.0/0 → Azure Firewall private IP (forced tunneling)
```

### Spoke-to-Spoke Communication

Spoke VNets cannot communicate directly through the hub without explicit
configuration. Two approaches:

1. **Azure Firewall / NVA routing:** UDRs on each spoke route inter-spoke traffic to the hub's Azure Firewall. Firewall inspects and forwards. Requires `AllowForwardedTraffic: true` on both peering links.
2. **Direct spoke-to-spoke peering:** Creates additional peering links between spokes. Bypasses hub inspection — not recommended for security-sensitive environments.

## Route Evaluation Priority

Azure resolves routing decisions using a defined priority order when
multiple route sources exist:

```
Route evaluation priority (highest to lowest):
  1. UDR (User-Defined Routes) on the subnet
  2. BGP routes (from ExpressRoute or VPN Gateway)
  3. System routes (auto-created for VNet, Internet, etc.)

Within each category:
  - Longest prefix match wins (a /24 beats a /16)
  - If same prefix length and category: system routes use built-in priority
```

### System Routes (Auto-Created)

| Destination | Next-Hop | Notes |
|-------------|----------|-------|
| VNet address space | VirtualNetwork | Intra-VNet routing |
| 0.0.0.0/0 | Internet | Default internet route |
| 10.0.0.0/8 | None | Drop if not in VNet address space |
| 172.16.0.0/12 | None | Drop if not in VNet address space |
| 192.168.0.0/16 | None | Drop if not in VNet address space |

### UDR Override Behavior

- UDR with next-hop "Virtual Appliance" overrides system route for same prefix — forces traffic through NVA or Azure Firewall
- UDR with next-hop "None" drops traffic matching the prefix — creates explicit block
- UDR with next-hop "VirtualNetworkGateway" forces traffic to VPN/ExpressRoute Gateway
- UDR does NOT override the local VNet route for VNet address space — intra-VNet traffic always routes locally
