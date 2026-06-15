# Check Point R80+ Policy Architecture

Reference for Check Point R80+ management architecture, Unified Policy model,
Software Blade framework, and policy installation process. This documents
how Check Point evaluates traffic from gateway ingress through rulebase
layers — the foundation for understanding policy audit findings.

## Management Architecture

```
SmartConsole (GUI Client)
       │
       ▼ (TCP 19009 / HTTPS 443)
┌─────────────────────────────┐
│  Security Management Server │  Central policy repository
│  (SMS)                      │  Stores rulebase, objects, logs
│                             │  Runs management API (mgmt_cli)
└────────┬────────────────────┘
         │  SIC (Secure Internal Communication)
         │  Certificate-based mutual authentication
         ▼
┌─────────────────────────────┐
│  Security Gateway           │  Enforces installed policy
│  (SGW)                      │  Runs fw, fwd, cpd daemons
│                             │  Reports logs back to SMS
└─────────────────────────────┘

Multi-Domain Server (MDS) variant:
┌─────────────────────────────┐
│  Multi-Domain Server        │
│  ├── Domain 1 (SMS instance)│  Independent object/policy DB
│  │   └── Gateway A, B       │
│  ├── Domain 2 (SMS instance)│  Isolated from Domain 1
│  │   └── Gateway C          │
│  └── Global Domain          │  Global policies/objects shared
│      └── Global assignments │  across domains
└─────────────────────────────┘
```

### Key Components

| Component | Role | Port |
|-----------|------|------|
| **SmartConsole** | GUI for policy management, object definition, log review | TCP 19009 (legacy), HTTPS 443 (R81+) |
| **Security Management Server (SMS)** | Central repository for policy, objects, and certificates | TCP 18190 (SIC), 18210, 18264 |
| **Log Server** | Receives and stores logs from gateways; may be co-located with SMS | TCP 18210 |
| **Security Gateway (SGW)** | Enforces policy on traffic; inspects packets per installed rulebase | SIC to SMS |
| **SmartEvent** | Correlation engine for log-based event detection | Co-located with Log Server or separate |
| **MDS** | Multi-tenant management; each domain is an isolated SMS instance | Same as SMS per domain |

### SIC (Secure Internal Communication)

SIC provides certificate-based authentication and encrypted communication
between all Check Point components. Each component has an SIC certificate
issued by the Management Server's Internal Certificate Authority (ICA).

SIC states:

| State | Meaning | Audit Implication |
|-------|---------|-------------------|
| **Trust established** | Mutual certificate authentication succeeded | Normal — policy installation works |
| **Uninitialized** | SIC not yet initialized on the component | Component cannot communicate with SMS |
| **Trust in progress** | SIC initialization underway | Transient — wait or reinitialize |
| **Trust broken** | Certificate mismatch or revocation | CRITICAL — gateway cannot receive policy updates |

## Unified Policy Model (R80+)

R80+ replaced the legacy single-rulebase model with a Unified Policy
composed of ordered layers.

### Access Control Policy

```
Access Control Policy
├── Ordered Layer 1: "Corporate Network"
│   ├── Rule 1: Block known-bad IPs → Drop
│   ├── Rule 2: Allow DNS to DNS servers → Accept (inline layer)
│   │   └── Inline Layer: "DNS Inspection"
│   │       ├── Sub-rule 1: Allow UDP/53 → Accept
│   │       └── Sub-rule 2: Allow TCP/53 → Accept
│   ├── Rule 3: Allow web browsing → Accept
│   ├── ...
│   └── Implicit Cleanup Rule → Drop
│
├── Ordered Layer 2: "Application Control"
│   ├── Rule 1: Block risky apps → Drop
│   ├── Rule 2: Allow business apps → Accept
│   └── Implicit Cleanup Rule → Drop
│
└── Policy evaluation: ALL layers must accept.
    If any layer drops, traffic is dropped.
```

### Layer Types

| Type | Behavior | Use Case |
|------|----------|----------|
| **Ordered Layer** | Independent rulebase evaluated top-down; first match wins within layer | Primary policy enforcement — network, application, content layers |
| **Inline Layer** | Embedded within a rule in a parent layer; evaluates only when parent rule matches | Sub-dividing a broad rule into granular sub-decisions |

### Policy Evaluation Logic

Traffic must be accepted by **every ordered layer** in the policy. If any
layer drops the traffic, the overall decision is Drop — even if other layers
accept it.

Within each layer:
1. Rules evaluate top-down (first match wins)
2. If a rule's action is an inline layer, the inline layer's rules evaluate
3. If no rule matches in a layer, the implicit cleanup rule applies (Drop)

### Implicit Rules

Implicit rules are controlled by Global Properties in SmartConsole, not by
explicit rules in the rulebase. Key implicit rules:

| Implicit Rule | Default State | Function |
|--------------|---------------|----------|
| Accept Control Connections | Before Last | Allows management traffic (SIC, logging, policy install) |
| Accept Remote Access VPN | Before Last | Allows VPN connections to the gateway |
| Accept Outgoing from Gateway | Before Last | Allows gateway-initiated traffic (DNS, NTP, updates) |
| Accept ICMP | Before Last | Allows ICMP packets |
| Stealth Rule | Not automatic | Must be manually created to protect gateway from data-plane access |

The "Accept Control Connections" implicit rule is particularly important —
it ensures management connectivity even if no explicit rule permits it.
However, relying on implicit rules reduces visibility since they are not
visible in the standard rulebase view.

## Software Blade Architecture

Check Point uses a modular blade architecture. Each blade provides a
specific security function and requires both licensing and activation.

### Blade Categories

| Category | Blades |
|----------|--------|
| **Network Security** | Firewall, IPS, VPN (IPSec/SSL) |
| **Threat Prevention** | Anti-Bot, Anti-Virus, Threat Emulation, Threat Extraction |
| **Access Control** | Application Control, URL Filtering, Content Awareness, Identity Awareness |
| **Inspection** | HTTPS Inspection |
| **Compliance** | Compliance Blade (policy verification against best practices) |

### Blade Activation Model

```
License (Contract/SKU)
       │
       ▼
Blade Enabled (Gateway Object in SmartConsole)
       │
       ▼
Threat Prevention Profile (references blade in policy rule)
       │
       ▼
Policy Installed on Gateway
       │
       ▼
Blade Active (inspecting traffic)
```

A blade that is licensed and enabled but not referenced in any policy rule's
Threat Prevention profile does not inspect traffic. All four levels must be
satisfied for effective protection.

### Threat Prevention Profiles

Threat Prevention profiles bundle blade settings and are assigned to rules:

| Profile Type | Controls |
|-------------|----------|
| **Threat Prevention** | IPS, Anti-Bot, Anti-Virus protections and actions |
| **Threat Emulation** | Sandbox environments, file types, emulation scope |
| **Threat Extraction** | File reconstruction settings, extracted content types |

## NAT Policy

### NAT Types

| Type | Definition | Evaluation Order |
|------|-----------|-----------------|
| **Manual NAT** | Explicit rules in the NAT rulebase, defined by the administrator | Evaluated first (top-down) |
| **Automatic NAT** | Generated from NAT settings on network objects (hosts, networks, ranges) | Evaluated after manual rules |

### Automatic NAT Sub-types

| Sub-type | Method | Use |
|----------|--------|-----|
| **Hide NAT** | Many-to-one PAT behind a single IP or gateway interface | Outbound internet access for internal networks |
| **Static NAT** | One-to-one bidirectional address translation | Server publishing, bi-directional access |

### NAT Evaluation Order

```
1. Manual NAT rules (top-down within manual section)
2. Automatic Static NAT rules (system-generated from objects)
3. Automatic Hide NAT rules (system-generated from objects)
```

Manual rules always take precedence over automatic rules. Within the
automatic section, static NAT evaluates before hide NAT.

## Policy Installation Process

```
SmartConsole → Publish session → Install Policy
       │
       ▼
Management Server compiles policy
       │
       ▼
Compiled policy pushed to gateway(s) via SIC
       │
       ▼
Gateway loads new policy
       │
       ▼
Verification: fw stat → shows policy name + install time
```

### Installation Implications for Audit

- **Policy installation is atomic** — the gateway switches from old to new
  policy in a single operation. No partial-install state.
- **"Policy out of date"** — indicates the rulebase has been modified in
  SmartConsole but not yet installed on the gateway. The gateway runs the
  last installed policy.
- **Install policy failure** — gateway continues running the previous policy.
  A failed install does not leave the gateway unprotected, but it means
  recent rule changes are not enforced.
- **Session publishing** — R80+ uses a session model. Changes are made in
  private sessions and must be published before installation. Unpublished
  changes exist only in the session owner's view.
