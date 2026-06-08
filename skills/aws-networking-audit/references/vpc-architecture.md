# AWS VPC Architecture Reference

Reference for VPC packet processing, Security Group and NACL evaluation
order, Transit Gateway routing model, VPC peering constraints, and subnet
tier patterns. This documents how AWS evaluates and routes traffic — the
foundation for understanding networking audit findings.

## VPC Packet Flow Model

When a packet enters or exits an EC2 instance within a VPC, AWS evaluates
multiple networking constructs in a defined order. Understanding this order
is essential for diagnosing Security Group, NACL, and Route Table findings.

### Outbound Packet Flow (Instance → Network)

```
EC2 Instance sends packet
       │
       ▼
┌─────────────────────────┐
│  Security Group (SG)    │  Stateful — outbound rules evaluated
│  Outbound Rules         │  If denied → packet dropped (no Flow Log REJECT
│                         │  for SG — SG drops are silent in v2 Flow Logs)
└─────────────────────────┘
       │ Permitted
       ▼
┌─────────────────────────┐
│  Network ACL (NACL)     │  Stateless — outbound rules evaluated
│  Outbound Rules         │  Rules evaluated by number (lowest first)
│                         │  First match wins; default deny at end
└─────────────────────────┘
       │ Permitted
       ▼
┌─────────────────────────┐
│  Route Table            │  Longest prefix match determines next hop
│  Route Selection        │  Local route handles intra-VPC
│                         │  Other targets: IGW, NAT GW, TGW, VPC peering,
│                         │  VPC endpoint, etc.
└─────────────────────────┘
       │
       ▼
  Packet exits subnet
```

### Inbound Packet Flow (Network → Instance)

```
Packet arrives at subnet
       │
       ▼
┌─────────────────────────┐
│  Network ACL (NACL)     │  Stateless — inbound rules evaluated
│  Inbound Rules          │  Must explicitly permit return traffic
│                         │  (unlike stateful SG)
└─────────────────────────┘
       │ Permitted
       ▼
┌─────────────────────────┐
│  Security Group (SG)    │  Stateful — if outbound was allowed,
│  Inbound Rules          │  return traffic auto-permitted
│                         │  New connections: inbound rules evaluated
└─────────────────────────┘
       │ Permitted
       ▼
  Packet delivered to instance ENI
```

### Key Implication for Auditing

Security Groups and NACLs are evaluated independently. A packet can be
permitted by the Security Group but denied by the NACL (or vice versa).
When troubleshooting connectivity, check both. VPC Flow Logs record the
final ACCEPT/REJECT decision after both layers evaluate.

## Security Group vs NACL Comparison

| Property | Security Group | Network ACL |
|----------|---------------|-------------|
| Statefulness | Stateful — return traffic auto-allowed | Stateless — both directions require rules |
| Scope | ENI-level (attached to instances, ALBs, etc.) | Subnet-level (applies to all traffic in/out of subnet) |
| Rule evaluation | All rules evaluated; permit if any rule matches | Rules evaluated by number; first match wins |
| Default behavior | Default SG: allow all inbound from self, all outbound | Default NACL: allow all inbound and outbound |
| Deny rules | Not supported — rules are permit-only | Supported — explicit deny rules by number |
| Rule limit | 60 inbound + 60 outbound per SG (adjustable) | 20 inbound + 20 outbound per NACL (adjustable) |

### Audit Implications

- **Security Groups alone are usually sufficient** for instance-level access control. NACLs add subnet-level defense-in-depth.
- **NACL deny rules** can block traffic that Security Groups permit. Use NACLs for broad subnet-level blocks (e.g., known malicious CIDRs).
- **Stateless NACL pitfall:** Permitting inbound TCP 443 in the NACL without permitting outbound ephemeral ports (1024–65535) breaks HTTPS connections. Security Groups handle this automatically via statefulness.

## Transit Gateway Routing Model

AWS Transit Gateway (TGW) is a regional hub that connects VPCs, VPN
connections, and Direct Connect gateways through a central routing domain.

### TGW Architecture

```
        VPC-A ──── TGW Attachment ────┐
                                      │
        VPC-B ──── TGW Attachment ────┼──── Transit Gateway
                                      │       │
        VPC-C ──── TGW Attachment ────┘       │
                                              │
        VPN Connection ── TGW Attachment ─────┘
```

### TGW Route Tables

Each TGW has one or more route tables. Each attachment (VPC, VPN, peering)
is **associated** with exactly one route table and can **propagate** routes
to one or more route tables.

- **Association:** Determines which route table is used to route traffic
  originating from the attachment. A VPC attachment associated with
  Route Table A uses Table A's routes for outbound traffic.
- **Propagation:** When enabled, the attachment's CIDR is automatically
  added to the target route table. VPC-A's CIDR propagated to Table B
  means Table B has a route directing VPC-A traffic to VPC-A's attachment.
- **Static routes:** Manually added routes. Override propagated routes if
  more specific. Used for default routes (0.0.0.0/0 → VPN) or aggregation.

### TGW Routing Audit Checks

- **Missing propagation:** If VPC-B cannot reach VPC-A, check that VPC-A's
  attachment propagates to the route table associated with VPC-B's attachment.
- **Overlapping CIDRs:** Two VPCs with overlapping CIDRs attached to the
  same TGW cause ambiguous routing. TGW uses longest prefix match but
  overlapping /16 CIDRs result in unpredictable behavior.
- **Black-hole routes:** TGW routes become black holes when the target
  attachment is deleted. Check route status = "active" vs "blackhole".
- **Multi-region TGW peering:** Routes do not auto-propagate across TGW
  peering connections. Static routes are required in each region's TGW
  route table pointing to the peering attachment.

## VPC Peering Constraints

VPC peering creates a direct networking link between two VPCs. Key
constraints for audit:

| Constraint | Detail |
|------------|--------|
| Non-transitive | VPC-A↔VPC-B and VPC-B↔VPC-C does NOT allow VPC-A↔VPC-C |
| No overlapping CIDRs | Peering fails if VPC CIDRs overlap |
| Cross-region supported | Inter-region peering incurs data transfer charges |
| Route required in both VPCs | Each VPC needs a Route Table entry pointing to the peering connection for the peer's CIDR |
| No edge-to-edge routing | Cannot route through a peer VPC to access its IGW, NAT GW, or VPN |
| DNS resolution opt-in | `AllowDnsResolutionFromRemoteVpc` must be enabled for cross-VPC private DNS |

### Peering vs Transit Gateway

| Criterion | VPC Peering | Transit Gateway |
|-----------|------------|-----------------|
| Topology | Point-to-point (N×(N-1)/2 connections for N VPCs) | Hub-and-spoke (N connections for N VPCs) |
| Transitivity | Non-transitive | Transitive via route tables |
| Cost | Data transfer only | Hourly per attachment + data transfer |
| Scale | Up to 125 peering connections per VPC | Up to 5,000 attachments per TGW |
| Use case | Few VPCs, direct low-latency links | Many VPCs, centralized routing, VPN integration |

## Subnet Types and Routing Patterns

AWS does not formally label subnets as "public" or "private" — the
distinction is determined by Route Table entries.

### Public Subnet

- Route Table contains `0.0.0.0/0 → Internet Gateway (igw-xxx)`
- Instances can have public IPs or Elastic IPs
- Use for: load balancers, bastion hosts, NAT Gateways

### Private Subnet

- Route Table contains `0.0.0.0/0 → NAT Gateway (nat-xxx)`
- Instances reach internet through NAT Gateway (outbound only)
- Use for: application servers, databases, backend services

### Isolated Subnet

- Route Table contains NO route to 0.0.0.0/0
- No internet access in either direction
- May have routes to VPC endpoints (S3, DynamoDB gateway endpoints)
- Use for: sensitive databases, compliance-restricted workloads

### Routing Pattern Audit

```
For each subnet in VPC:
  1. Find associated Route Table (or main RT if no explicit association)
  2. Check for 0.0.0.0/0 route:
     - Target = igw-xxx → Public subnet
     - Target = nat-xxx → Private subnet
     - No 0.0.0.0/0 route → Isolated subnet
  3. Verify subnet type matches workload requirements
  4. Check for black-hole routes (deleted targets)
```
