# GCP VPC Network Architecture Reference

Reference for the GCP global VPC Network model, firewall rule evaluation
order with hierarchical policies, Cloud Interconnect topology, Shared VPC
architecture, and Cloud Router dynamic routing. This documents how GCP
evaluates and routes traffic — the foundation for understanding
networking audit findings.

## GCP Global VPC Network Model

GCP VPC Networks are fundamentally global resources — a single VPC Network
spans all GCP regions. Subnets are regional but belong to the global VPC
Network. This differs from AWS (VPC is regional) and Azure (VNet is
regional).

### Key Implications for Auditing

| Property | GCP | AWS | Azure |
|----------|-----|-----|-------|
| VPC/VNet scope | Global | Regional | Regional |
| Subnet scope | Regional | AZ-specific | Regional |
| Cross-region within VPC | Native (one VPC) | Requires TGW or peering | Requires VNet Peering |
| Firewall scope | VPC Network-wide | Security Group per ENI | NSG per subnet/NIC |
| Default network | Created automatically (deletable) | Created per region (deletable) | None |

### Auto-Mode vs Custom-Mode VPC Networks

**Auto-mode:** Automatically creates one subnet per GCP region using
predetermined IP ranges from 10.128.0.0/9. New regions get subnets
automatically. Suitable for development but problematic in production:
- IP ranges are predetermined and may conflict with on-premises networks
- Cannot control which regions get subnets
- Subnets are /20 — may not match capacity requirements
- Auto-mode networks can be converted to custom-mode (one-way, irreversible)

**Custom-mode:** No automatic subnets. All subnets explicitly defined with
chosen IP ranges in chosen regions. Required for production:
- Full control over IP allocation — avoids conflicts with Cloud
  Interconnect or Cloud VPN peer networks
- Subnets sized to workload requirements
- Regions selected intentionally

### Audit Decision: Network Mode

```
VPC Network mode assessment
├── Auto-mode?
│   ├── Production workloads → MEDIUM: Convert to custom-mode
│   ├── Development/test only → Acceptable
│   └── Connected to on-premises? → HIGH: IP conflicts likely
└── Custom-mode?
    ├── All required regions have subnets → Good
    ├── IP ranges non-overlapping → Required for peering/VPN
    └── Secondary ranges for GKE → Required if running GKE
```

## Firewall Rule Evaluation Order

GCP evaluates firewall rules in a specific order. Understanding this
order is critical for audit — a rule at one level can override rules
at lower levels.

### Evaluation Hierarchy

```
Packet arrives at VM
       │
       ▼
┌──────────────────────────────┐
│  Hierarchical Firewall       │  Organization-level policies
│  Policy (Org Level)          │  evaluated first
│                              │  Actions: allow, deny, goto_next
└──────────────────────────────┘
       │ goto_next (or no match)
       ▼
┌──────────────────────────────┐
│  Hierarchical Firewall       │  Folder-level policies
│  Policy (Folder Level)       │  evaluated second
│                              │  Actions: allow, deny, goto_next
└──────────────────────────────┘
       │ goto_next (or no match)
       ▼
┌──────────────────────────────┐
│  VPC Network Firewall Rules  │  Project-level rules
│  (Priority 0–65534)          │  evaluated by priority number
│                              │  Lowest number = highest priority
└──────────────────────────────┘
       │ No match in custom rules
       ▼
┌──────────────────────────────┐
│  Implied Rules               │  Deny all ingress (priority 65535)
│  (Priority 65535)            │  Allow all egress (priority 65535)
└──────────────────────────────┘
```

### Hierarchical Firewall Policy Actions

| Action | Effect |
|--------|--------|
| `allow` | Permit traffic — skips VPC-level rules entirely |
| `deny` | Block traffic — skips VPC-level rules entirely |
| `goto_next` | Delegate decision to the next level (folder or VPC rules) |
| No match | Implicitly delegates to next level (same as `goto_next`) |

### Key Audit Implications

- A `deny` in an org-level hierarchical firewall policy overrides any
  VPC-level `allow`. Use for organization-wide blocks (e.g., block SSH
  from internet globally).
- A `goto_next` at org level delegates to folder level, then to VPC rules.
  This is the typical pattern for rules that should be overridable by
  project teams.
- VPC firewall rules with priority 0 override all other VPC-level rules
  but cannot override hierarchical policy `deny` actions.
- Implied rules (65535) are the final fallback — deny ingress, allow
  egress. Custom VPC rules at any priority override implied rules.

## Cloud Interconnect Topology

Cloud Interconnect provides dedicated physical connectivity between
on-premises networks and GCP VPC Networks.

### Architecture Components

```
On-Premises      │    Colocation    │         GCP
Router            │    Facility      │
                  │                  │
┌──────────┐     │  ┌───────────┐  │  ┌──────────────┐
│ Customer │─────┼──│ Cross-    │──┼──│ Google Edge  │
│ Router   │     │  │ Connect   │  │  │ POP          │
│ (BGP)    │     │  └───────────┘  │  │              │
└──────────┘     │                  │  └──────┬───────┘
                  │                  │         │
                  │                  │  ┌──────┴───────┐
                  │                  │  │ VLAN         │
                  │                  │  │ Attachment   │
                  │                  │  └──────┬───────┘
                  │                  │         │
                  │                  │  ┌──────┴───────┐
                  │                  │  │ Cloud Router │
                  │                  │  │ (BGP peer)   │
                  │                  │  └──────┬───────┘
                  │                  │         │
                  │                  │  ┌──────┴───────┐
                  │                  │  │ VPC Network  │
                  │                  │  └──────────────┘
```

### Redundancy Model

GCP recommends Cloud Interconnect connections in at least two edge
availability domains for production. Each edge availability domain
(e.g., `zone1`, `zone2`) is an independent failure domain.

| Topology | SLA | Use Case |
|----------|-----|----------|
| Single connection, single domain | No SLA | Development/test only |
| Dual connections, two domains | 99.9% | Standard production |
| 4 connections, two domains | 99.99% | Mission-critical |

### VLAN Attachment States

| State | Meaning |
|-------|---------|
| ACTIVE | Fully operational |
| UNPROVISIONED_ATTACHMENT | Partner has not completed setup |
| PENDING_PARTNER | Waiting for partner-side configuration |
| DEFUNCT | Attachment no longer functional |

## Shared VPC Architecture

Shared VPC enables centralized network management where a host project
owns the VPC Network and service projects deploy workloads into shared
subnets.

### Architecture

```
┌─────────────────────────────────────────┐
│           Host Project                   │
│                                          │
│  ┌─────────────────────────────────────┐│
│  │         VPC Network (global)        ││
│  │                                     ││
│  │  ┌──────────┐    ┌──────────┐      ││
│  │  │ Subnet A │    │ Subnet B │      ││
│  │  │ us-east1 │    │ eu-west1 │      ││
│  │  └────┬─────┘    └────┬─────┘      ││
│  │       │               │             ││
│  └───────┼───────────────┼─────────────┘│
│          │               │               │
└──────────┼───────────────┼───────────────┘
           │               │
    ┌──────┴──────┐ ┌──────┴──────┐
    │  Service    │ │  Service    │
    │  Project A  │ │  Project B  │
    │  (VMs in    │ │  (GKE in    │
    │  Subnet A)  │ │  Subnet B)  │
    └─────────────┘ └─────────────┘
```

### IAM Model

- **Host project admin:** `compute.xpnAdmin` role — can share subnets
  and manage host project designation
- **Service project users:** `compute.networkUser` on specific subnets —
  can deploy resources into shared subnets
- **Scoping:** Grant `compute.networkUser` at the subnet level, not
  project level, for least-privilege access

### Audit Checks for Shared VPC

| Check | How |
|-------|-----|
| Host project designation correct | `gcloud compute shared-vpc get-host-project <service-project>` |
| Service projects associated | `gcloud compute shared-vpc list-associated-resources <host-project>` |
| Subnet IAM not over-broad | `get-iam-policy` per subnet — verify no wildcard principals |
| Firewall rules in host project | Firewall rules live in the host project, not service projects |
| Cloud NAT in host project | Cloud NAT must be configured in the host project's Cloud Router |

## Cloud Router Dynamic Routing

Cloud Router provides BGP-based dynamic routing for Cloud Interconnect,
Cloud VPN, and Router appliances.

### Routing Mode Impact

| Mode | Subnet Advertisement | Learned Route Scope |
|------|---------------------|---------------------|
| Regional | Subnets in same region only | Applied to same region only |
| Global | All subnets in VPC Network | Applied to all regions |

### Route Priority and Selection

GCP selects routes using this precedence:

1. **Most specific prefix** — /24 beats /16 for matching traffic
2. **Route type** — subnet routes > peering routes > Cloud Router routes > static routes > default internet route
3. **Priority value** — lower number preferred (0–65535, default 1000)
4. **ECMP** — equal-priority, equal-prefix routes are load-balanced

### BGP Session States

| State | Meaning |
|-------|---------|
| UP | BGP session established, routes exchanged |
| DOWN | No BGP session — check configuration |
| MD5_AUTH_INTERNAL_PROBLEM | Authentication key mismatch |

### Custom Route Advertisements

By default, Cloud Router advertises all VPC Network subnets. Custom
mode overrides this:

- **Custom with advertised groups:** Still advertise all subnets plus
  additional custom prefixes
- **Custom without advertised groups:** Only advertise explicitly listed
  prefixes — subnets are NOT automatically included

Audit check: if custom advertisements are configured, verify all required
subnets are still reachable from on-premises by checking learned routes
on the on-premises router.
