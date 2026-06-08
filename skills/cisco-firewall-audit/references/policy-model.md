# Cisco ASA and FTD Policy Models

Reference for the ASA security-level model, Modular Policy Framework,
multi-context architecture, and FTD Access Control Policy evaluation chain.
This documents how each platform evaluates traffic — the foundation for
understanding policy audit findings.

## ASA Security-Level Model

ASA uses security levels (0–100) on named interfaces to establish a trust
hierarchy. The security level determines the default traffic flow behavior
before ACLs are applied.

### Default Traffic Flow

```
Higher Security Level (e.g., inside = 100)
       │
       │  Permitted by default (higher → lower)
       ▼
Lower Security Level (e.g., outside = 0)
       │
       │  Denied by default (lower → higher)
       ▼
Higher Security Level
```

| Direction | Default Behavior | Override |
|-----------|-----------------|----------|
| Higher → Lower | Permitted (implicit allow) | ACL can deny specific traffic |
| Lower → Higher | Denied (implicit deny) | ACL must explicitly permit |
| Same → Same | Denied by default | `same-security-traffic permit inter-interface` enables |

### Interface ACL Processing

```
Packet arrives on interface
       │
       ▼
┌─────────────────────────┐
│  Input ACL              │  Interface-bound ACL (access-group in)
│  Top-down, first match  │  Explicit permit/deny entries
│  Implicit deny at end   │  
└────────┬────────────────┘
         │ (permitted)
         ▼
┌─────────────────────────┐
│  NAT Translation        │  Section 1 → Section 2 → Section 3
│  (if applicable)        │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│  Security Level Check   │  Higher-to-lower: allowed
│  (if no ACL override)   │  Lower-to-higher: denied
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│  Inspection Engine      │  Modular Policy Framework
│  (MPF)                  │  Protocol inspection, conn limits
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│  Output ACL             │  Interface-bound ACL (access-group out)
│  (if configured)        │  Less common than input ACL
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│  Egress Interface       │  Forward to destination
└─────────────────────────┘
```

### Global ACL

A global ACL applies to all interfaces. Interface-specific ACLs are
evaluated before the global ACL. If an interface ACL exists and matches
(permit or deny), the global ACL is not consulted for that traffic.

## Modular Policy Framework (MPF)

MPF provides application-layer inspection on ASA. It uses a three-tier
model: classify, apply policy, activate.

### MPF Hierarchy

```
class-map (classify traffic)
       │
       ▼
policy-map (bind inspections/actions to classified traffic)
       │
       ▼
service-policy (apply policy-map to interface or globally)
```

### MPF Components

| Component | Purpose | Example |
|-----------|---------|---------|
| **class-map** | Matches traffic by protocol, ACL, port, or any | `class-map inspection_default` → matches default inspection ports |
| **policy-map** | Binds actions (inspect, police, set connection) to class | `policy-map global_policy` → `inspect http`, `inspect dns` |
| **service-policy** | Applies policy-map to interface or globally | `service-policy global_policy global` |

### Default Inspection Policy

ASA ships with a default global policy (`global_policy`) that inspects
common protocols via `inspection_default` class-map:

| Protocol | Default Inspect | Notes |
|----------|----------------|-------|
| DNS | Yes | Length enforcement, dynamic DNS rewrite |
| FTP | Yes | Command inspection, active/passive mode |
| H.323 (H225/RAS) | Yes | Signaling/media pinhole |
| HTTP | No (optional) | Must add `inspect http` for app inspection |
| ICMP | No | ICMP inspection must be explicitly added |
| SIP | Yes | Signaling/media pinhole |
| SMTP/ESMTP | Yes | Command filtering |
| SNMP | Yes | Version enforcement |
| SQL*Net | Yes | Oracle protocol inspection |
| TFTP | Yes | Dynamic pinhole for data channel |

Protocols not in the `inspection_default` class-map receive no
application-layer inspection. They are still subject to ACL enforcement
and stateful connection tracking.

## ASA Multi-Context Architecture

Multi-context mode partitions a single ASA into multiple virtual firewalls.

```
┌──────────────────────────────┐
│  System Context              │  Hardware management, context allocation
│  (admin context)             │  Cannot process transit traffic
├──────────────────────────────┤
│  Context A                   │  Independent firewall instance
│  - Own interfaces            │  Own ACLs, NAT, routing
│  - Own security policy       │  Own admin credentials
├──────────────────────────────┤
│  Context B                   │  Independent firewall instance
│  - Own interfaces            │  Isolated from Context A
│  - Own security policy       │  Own resource allocation
└──────────────────────────────┘
```

### Multi-Context Considerations

| Aspect | Implication |
|--------|-------------|
| **Interface allocation** | Physical interfaces are assigned to contexts; shared interfaces use VLAN sub-interfaces |
| **Resource classes** | Define per-context limits (connections, routes, NAT translations) |
| **Failover** | Active/standby operates at the context level — individual contexts can fail over independently (with ASA clustering) |
| **No inter-context routing** | Traffic between contexts must traverse an external device (router/switch) |

## ASA NAT Order of Operations

```
Packet arrives
       │
       ▼
┌─────────────────────────────────────────────┐
│  Section 1: Manual NAT (Twice NAT)          │
│  - Explicit rules in `nat` command          │
│  - Evaluated top-down                       │
│  - Can match source AND destination         │
│  - Highest priority                         │
└────────┬────────────────────────────────────┘
         │ (no match)
         ▼
┌─────────────────────────────────────────────┐
│  Section 2: Auto NAT (Object NAT)          │
│  - Defined on network objects               │
│  - Internal ordering:                       │
│    1. Static rules (longest prefix first)   │
│    2. Dynamic rules (longest prefix first)  │
│  - Cannot match both source and dest        │
└────────┬────────────────────────────────────┘
         │ (no match)
         ▼
┌─────────────────────────────────────────────┐
│  Section 3: Manual NAT (after-auto)         │
│  - Manual rules placed after auto NAT       │
│  - Lowest priority                          │
│  - Used for catch-all translations          │
└─────────────────────────────────────────────┘
```

## FTD Access Control Policy (ACP) Evaluation Chain

FTD uses a multi-stage evaluation pipeline. Traffic passes through several
policy stages in order. Each stage can take action (allow, block, trust,
decrypt) or pass the traffic to the next stage.

### ACP Evaluation Flow

```
Packet arrives on FTD interface
       │
       ▼
┌─────────────────────────────────────────────┐
│  Stage 1: Prefilter Policy                  │
│  Actions: Fastpath / Block / Analyze        │
│  - Fastpath: bypass Snort entirely          │
│  - Block: drop immediately                  │
│  - Analyze: continue to next stages         │
│  Uses: L3/L4 criteria, tunnel rules         │
│  No application awareness                   │
└────────┬────────────────────────────────────┘
         │ (Analyze or no match)
         ▼
┌─────────────────────────────────────────────┐
│  Stage 2: SSL / TLS Policy                  │
│  Actions: Decrypt / Do Not Decrypt / Block  │
│  - Decrypt (Known Key): inbound server      │
│  - Decrypt (Resign): outbound client        │
│  - Do Not Decrypt: pass encrypted           │
│  - Block: terminate TLS connection          │
│  Determines what Snort can see              │
└────────┬────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────┐
│  Stage 3: Access Control Rules              │
│  Evaluated top-down, first match            │
│  Actions per rule:                          │
│  - Allow: permit + optional inspection      │
│  - Trust: permit, bypass ALL further stages │
│  - Block: deny (with or without reset)      │
│  - Monitor: log and continue evaluating     │
│  - Interactive Block: user warning page     │
│                                             │
│  Match criteria:                            │
│  - Zones, Networks, VLAN tags               │
│  - Ports, Protocols                         │
│  - Applications (OpenAppID)                 │
│  - URLs (category/reputation)               │
│  - Users/Groups (via Realm/AD)              │
│  - SGT/ISE attributes                       │
└────────┬────────────────────────────────────┘
         │ (Allow action)
         ▼
┌─────────────────────────────────────────────┐
│  Stage 4: Intrusion Policy (Snort IPS)      │
│  Applied only if rule action = Allow AND    │
│  an Intrusion Policy is bound to the rule   │
│  - Snort 2 or Snort 3 rule engine           │
│  - Preprocessor + detection engine          │
│  - Actions: Drop/Alert/Pass per rule        │
└────────┬────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────┐
│  Stage 5: File / Malware Policy             │
│  Applied if bound to the rule               │
│  - File type detection and blocking         │
│  - Malware cloud lookup (AMP for Networks)  │
│  - Dynamic analysis (Threat Grid sandbox)   │
│  - Local malware detection (custom sigs)    │
└────────┬────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────┐
│  Stage 6: Default Action                    │
│  Applied when no Access Control rule matches│
│  Options:                                   │
│  - Block All Traffic                        │
│  - Network Discovery Only (no IPS)          │
│  - Intrusion Prevention (IPS on unmatched)  │
│  Recommended: Block All Traffic             │
└─────────────────────────────────────────────┘
```

### Trust vs Allow Actions

| Action | Snort Inspection | File/Malware | SSL Decrypt | Logging |
|--------|-----------------|--------------|-------------|---------|
| **Trust** | Bypassed | Bypassed | Bypassed | Connection only |
| **Allow** | Applied (if bound) | Applied (if bound) | Respected | Full |
| **Block** | N/A | N/A | N/A | Connection only |
| **Monitor** | Continues to next rule | Continues | Continues | Logged |

Trust should be reserved for flows that are verified safe and high-volume
(e.g., backup replication between known servers). Using Trust broadly
creates inspection-free paths through the firewall.

### Snort Deployment Modes

| Mode | Behavior | Use Case |
|------|----------|----------|
| **Inline** | Snort sits in the traffic path; can drop/modify packets | Production IPS — active prevention |
| **Inline Tap** | Copy of traffic sent to Snort; original traffic passes unmodified | Testing IPS policy before enabling inline |
| **Passive** | Snort receives mirrored traffic only; no blocking capability | Monitoring and detection only |

### Snort Base Policies

| Policy | Posture | Description |
|--------|---------|-------------|
| **Connectivity Over Security** | Least restrictive | Fewest rules enabled; minimal performance impact |
| **Balanced Security and Connectivity** | Moderate | Recommended baseline; balances detection and performance |
| **Security Over Connectivity** | Restrictive | More rules; higher CPU; more false positives |
| **Maximum Detection** | Most restrictive | All applicable rules; highest resource usage; tuning required |

## FMC Management Model

```
Firepower Management Center (FMC)
       │
       │  Management channel (sftunnel, TCP 8305)
       ▼
┌─────────────────────────────┐
│  FTD Device 1               │  Receives deployed policy
│  (Snort + ASA data plane)   │  Reports events to FMC
├─────────────────────────────┤
│  FTD Device 2               │  Independent policy possible
│  (Snort + ASA data plane)   │  or shared ACP
└─────────────────────────────┘
```

FMC is the canonical policy source. The FTD device enforces the deployed
policy. Changes made via the FTD diagnostic CLI do not persist across
policy deployments from FMC.

### FDM (Local Management)

FTD devices not managed by FMC can use Firepower Device Manager (FDM) —
an on-device web interface. FDM supports basic ACP, NAT, VPN, and
Intrusion Policy configuration but lacks FMC's advanced features (custom
Snort rules, multi-device management, advanced event correlation).
