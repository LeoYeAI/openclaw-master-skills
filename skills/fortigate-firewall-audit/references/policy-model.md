# FortiOS Policy Evaluation and VDOM Architecture

Reference for the FortiOS packet processing pipeline, VDOM segmentation
model, policy matching logic, and UTM inspection chain. This documents
how FortiOS evaluates traffic from ingress through VDOM policy to UTM
processing — the foundation for understanding audit findings.

## VDOM Architecture

### VDOM Concepts

A Virtual Domain (VDOM) is an independent firewall instance within a single
FortiGate appliance. Each VDOM has its own:

- Routing table and routing configuration
- Firewall policy table
- UTM profiles and profile assignments
- Interface assignments
- NAT configuration
- Administrator access (per-VDOM admin roles)

VDOMs provide multi-tenant segmentation on a single physical appliance.
Traffic between VDOMs must traverse inter-VDOM links and is subject to
the receiving VDOM's firewall policies.

### VDOM Types

| VDOM Type | Function | Typical Use |
|-----------|----------|-------------|
| **root** | Default VDOM — management traffic, FortiGuard updates, logging | Administrative access, update connectivity |
| **Traffic VDOM** | Carries production traffic — LAN, WAN, DMZ segmentation | Per-tenant or per-function security policy |
| **Management VDOM** | Dedicated management plane (when root is repurposed) | Separation of management and data planes |

### Inter-VDOM Links

Inter-VDOM links are virtual point-to-point interfaces connecting two VDOMs.
Each link creates a pair of virtual interfaces (e.g., `npu0_vlink0` and
`npu0_vlink1`), one in each VDOM.

```
VDOM-A                    VDOM-B
┌────────────┐            ┌────────────┐
│            │  vlink0    │            │
│  Policy    ├───────────►│  Policy    │
│  Table A   │            │  Table B   │
│            │◄───────────┤            │
│            │  vlink1    │            │
└────────────┘            └────────────┘
```

Traffic from VDOM-A to VDOM-B egresses through VDOM-A's vlink interface
(subject to VDOM-A's egress policy) and ingresses into VDOM-B's vlink
interface (subject to VDOM-B's ingress policy). Both VDOM policy tables
must permit the traffic.

### VDOM Resource Limits

In multi-VDOM deployments, resource limits prevent a single VDOM from
monopolizing system resources:

| Resource | Default | Impact if Exceeded |
|----------|---------|-------------------|
| Session count | Unlimited | VDOM can consume all session table entries |
| CPU quota | Unlimited | VDOM can starve other VDOMs of processing |
| Custom service | Varies by model | Limits UTM processing capacity per VDOM |

Best practice: set explicit limits on all traffic VDOMs; allow the
management VDOM to use remaining resources.

## Packet Processing Pipeline

```
Ingress Interface (assigned to VDOM)
         │
         ▼
┌──────────────────┐
│  VDOM Context     │  Determine which VDOM owns this interface
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  DoS Policy       │  Rate-based DoS protection (per-policy or global)
│  Evaluation       │  Applied before firewall policy lookup
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  Session Lookup   │  Existing session? → Fast-path (skip policy lookup)
└────────┬─────────┘
         │ (new session)
         ▼
┌──────────────────────────────────────────────┐
│  Firewall Policy Lookup                       │
│                                               │
│  Match criteria (by sequence number, top-down)│
│  - Incoming Interface (srcintf)               │
│  - Outgoing Interface (dstintf)               │
│  - Source Address/Group (srcaddr)              │
│  - Destination Address/Group (dstaddr)        │
│  - Service (port/protocol)                    │
│  - Schedule (time-based match)                │
│  - User/Group (if FSSO/LDAP authenticated)    │
│  - Application (if application-control set)   │
│                                               │
│  First matching policy wins (top-down by seq) │
└────────┬─────────────────────────────────────┘
         │
         ▼
┌──────────────────┐
│  Action           │
│  accept / deny /  │
│  learn / ipsec    │
└────────┬─────────┘
         │ (if accept)
         ▼
┌──────────────────────────────────────────────┐
│  NAT Processing                               │
│                                               │
│  Central NAT mode: separate NAT table         │
│  Per-policy NAT: NAT config on the policy     │
│  - SNAT (source NAT for outbound)             │
│  - DNAT (VIP / destination NAT for inbound)   │
└────────┬─────────────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────────────┐
│  SSL/SSH Inspection                           │
│                                               │
│  ssl-ssh-profile on the policy determines:    │
│  - certificate-inspection: inspect metadata   │
│  - deep-inspection: full decrypt/re-encrypt   │
│  - no-inspection: skip SSL processing         │
│                                               │
│  Deep inspection required for UTM to see      │
│  encrypted payload content                    │
└────────┬─────────────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────────────┐
│  UTM Inspection Chain                         │
│  (profiles bound to the matching policy)      │
│                                               │
│  ┌──────────────────────────────────────────┐ │
│  │ Flow-Based Mode (single-pass engine)     │ │
│  │ All UTM engines process simultaneously   │ │
│  │ Lower latency, slightly less thorough    │ │
│  └──────────────────────────────────────────┘ │
│  OR                                           │
│  ┌──────────────────────────────────────────┐ │
│  │ Proxy-Based Mode (buffered inspection)   │ │
│  │ Content fully buffered before inspection │ │
│  │ Higher accuracy, more resource intensive │ │
│  └──────────────────────────────────────────┘ │
│                                               │
│  Profile types applied (if bound):            │
│  1. Antivirus (av-profile)                    │
│     → File-based malware scanning             │
│     → Heuristic detection, sandboxing link    │
│                                               │
│  2. Web Filter (webfilter-profile)            │
│     → URL categorization (FortiGuard ratings) │
│     → Category allow/block/monitor actions    │
│     → Safe search enforcement                 │
│                                               │
│  3. Application Control (application-list)    │
│     → L7 application identification           │
│     → Per-application allow/block/monitor     │
│     → Application categories                  │
│                                               │
│  4. IPS (ips-sensor)                          │
│     → Exploit signature matching              │
│     → Protocol anomaly detection              │
│     → Rate-based detection                    │
│                                               │
│  5. Email Filter (emailfilter-profile)        │
│     → Anti-spam for SMTP/IMAP/POP3            │
│     → Phishing URL detection in email         │
│                                               │
│  6. DLP Sensor (dlp-sensor)                   │
│     → Data pattern matching (SSN, CC, custom) │
│     → Fingerprint-based document matching     │
│                                               │
│  7. File Filter (file-filter-profile)         │
│     → File type enforcement by direction      │
│     → Block specific file types               │
└────────┬─────────────────────────────────────┘
         │
         ▼
┌──────────────────┐
│  FortiSandbox     │  Unknown files submitted for analysis
│  (if configured)  │  Verdict: clean/suspicious/malicious
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  Egress Interface │  Forward per VDOM routing table
│  Forwarding       │
└──────────────────┘
```

## Policy Matching Details

### Sequence Number Ordering

FortiOS evaluates policies by sequence number, not by policy ID. Sequence
numbers determine the visual order in the GUI and the evaluation priority
in the engine. Policy IDs are auto-assigned and immutable identifiers.

Key implications:
- Moving a policy in the GUI changes its sequence number
- A policy with a lower sequence number is evaluated before a higher one
- Policy ID has no bearing on evaluation order

### Interface-Based Matching

FortiOS policies match on specific interfaces (srcintf/dstintf), not on
abstract zones (unlike PAN-OS). This means:

- Policies referencing interface `port1` only match traffic entering `port1`
- `any` interface matching is available but overly broad
- Zone objects group interfaces but are still interface-based under the hood
- SD-WAN interface selection happens before policy matching — policies must
  cover all SD-WAN member interfaces

### Implicit Deny (Policy ID 0)

Every VDOM has an implicit deny policy at the bottom of the policy table
(Policy ID 0). This policy:
- Matches all traffic not matched by any explicit policy
- Action: deny
- Logging: disabled by default (enable for visibility)
- Cannot be deleted or reordered

### Policy Types

| Type | Function |
|------|----------|
| **IPv4 Policy** | Standard firewall policy for IPv4 traffic |
| **IPv6 Policy** | Firewall policy for IPv6 traffic (separate table) |
| **Multicast Policy** | Policy for multicast traffic |
| **Local-In Policy** | Controls traffic destined to the FortiGate itself (management, routing protocols) |
| **DoS Policy** | Rate-based protection applied before firewall policy |
| **Shaping Policy** | Traffic shaping and QoS |

## FortiGuard Integration

### Service Architecture

FortiGuard provides cloud-based intelligence for UTM profiles:

| Service | Function | Update Frequency |
|---------|----------|-----------------|
| **AntiVirus** | Malware signatures, heuristics | Every 1–4 hours |
| **IPS** | Exploit signatures, protocol decoders | Daily |
| **Web Filtering** | URL categorization database | Real-time rating queries |
| **Application Control** | Application signatures | Daily |
| **Anti-Spam** | Spam signatures, IP reputation | Real-time queries |
| **Outbreak Prevention** | Zero-day threat intelligence | Real-time queries |

### Fail-Open vs Fail-Close

When FortiGuard is unreachable:

- **Web Filter:** Defaults to allow (fail-open) or block (fail-close) per
  configuration. Default is fail-open — all URLs allowed when rating
  service is unreachable.
- **Antivirus:** Uses cached signatures. New malware not in cache is missed.
- **IPS:** Uses cached signatures. Same limitation as AV.
- **Application Control:** Uses cached signatures.

The fail-open/fail-close behavior for web filtering is configurable:
```
config webfilter fortiguard
  set close-ports {enable|disable}
end
```

## NAT Architecture

### Central NAT vs Per-Policy NAT

FortiOS supports two NAT architectures:

| Mode | Behavior | Audit Implication |
|------|----------|-------------------|
| **Per-Policy NAT** | NAT configured on each firewall policy individually | Audit must check NAT on every policy; inconsistencies likely |
| **Central NAT** | Separate NAT table independent of firewall policy | Cleaner separation; NAT audit is separate from policy audit |

Central NAT is recommended for complex deployments. When enabled, firewall
policies match on pre-NAT addresses and the central NAT table handles
address translation independently.

### VIP (Virtual IP) for Destination NAT

Inbound traffic to published services uses VIP objects. VIPs are matched
before firewall policy lookup — the policy sees the post-DNAT address.

```
Inbound Packet (dst = VIP external IP)
       │
       ▼
VIP DNAT (translate to internal IP)
       │
       ▼
Firewall Policy (matches on internal IP as dstaddr)
```

This ordering means firewall policies for inbound services reference the
VIP object, not the external IP address.
