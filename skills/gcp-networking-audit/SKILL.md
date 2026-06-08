---
name: gcp-networking-audit
description: >-
  GCP VPC Network audit covering global VPC design, firewall rule priority
  evaluation with hierarchical policies, Cloud NAT egress analysis, Cloud
  Interconnect and Shared VPC connectivity, Cloud Router BGP validation,
  and resource optimization using read-only gcloud CLI commands.
license: Apache-2.0
metadata:
  safety: read-only
  author: network-security-skills-suite
  version: "1.0.0"
  openclaw: '{"emoji":"☁️","safetyTier":"read-only","requires":{"bins":["gcloud"],"env":[]},"tags":["gcp","vpc","cloud"],"mcpDependencies":[],"egressEndpoints":["compute.googleapis.com:443"]}'
---

# GCP VPC Network Security Audit

Cloud resource audit for Google Cloud Platform VPC Network architecture,
firewall posture, and connectivity. This skill evaluates provider-specific
GCP networking constructs — global VPC Network design, firewall rule
priority evaluation, hierarchical firewall policies, Cloud NAT egress
control, Cloud Interconnect VLAN attachments, Shared VPC host/service
project topology, and Cloud Router BGP sessions — not generic cloud
networking advice.

Scope: auto-mode versus custom-mode VPC Networks, subnet IP ranges,
firewall rules with target tags and service accounts, Cloud NAT port
allocation, Cloud Interconnect and Cloud VPN connectivity, Shared VPC
cross-project networking, Cloud Router dynamic routing. Out of scope:
Cloud CDN, Cloud Armor WAF, load balancer URL maps, Cloud DNS.
Reference `references/cli-reference.md` for read-only gcloud commands
and `references/vpc-architecture.md` for the GCP global VPC model and
firewall rule evaluation order.

## When to Use

- VPC Network architecture review — evaluating auto-mode versus custom-mode selection, subnet IP ranges, and Private Google Access configuration
- Post-migration audit — verifying firewall rules, Cloud NAT egress, and Cloud Router routes after workload migration
- Security assessment — identifying permissive firewall rules using target tags, missing hierarchical firewall policies, or disabled VPC Flow Logs
- Connectivity troubleshooting — diagnosing Cloud Interconnect VLAN attachment failures, Cloud VPN tunnel errors, or Shared VPC permission issues
- Compliance preparation — documenting VPC Network segmentation, firewall rule justification, and VPC Flow Log retention
- Cost optimization — identifying unused external IPs, over-provisioned Cloud NAT gateways, and idle Cloud Interconnect attachments

## Prerequisites

- **gcloud CLI** authenticated (`gcloud auth list` shows active account)
- **IAM permissions** — Viewer role on target project, or granular read: `compute.networks.get`, `compute.firewalls.list`, `compute.routers.get`, `compute.interconnects.get`, `compute.subnetworks.list`, `compute.addresses.list`. Shared VPC: Viewer on host and service projects. Hierarchical firewall policies: `compute.firewallPolicies.get` at org/folder level
- **Target scope** — project ID, organization ID (for hierarchical firewall policies), Shared VPC host project if applicable
- **VPC Flow Logs** — Step 1 checks subnet-level enablement. If no subnets have VPC Flow Logs, document as Critical

## Procedure

Follow these six steps sequentially. Each builds on prior findings,
moving from inventory through security analysis to optimization.

### Step 1: VPC Network Inventory and Design Assessment

Enumerate all VPC Networks in the target project and assess design.

```
gcloud compute networks list --project <project-id>
gcloud compute networks describe <network-name> --project <project-id>
gcloud compute networks subnets list --network <network-name>
```

For each VPC Network, evaluate:

- **Auto-mode vs custom-mode:** Auto-mode VPC Networks create one subnet per region with predetermined /20 ranges from 10.128.0.0/9. Custom-mode requires explicit subnet creation. Production environments should use custom-mode. Auto-mode in production is a High finding.
- **Global scope:** GCP VPC Networks are global — subnets are regional but the network spans all regions. Unlike AWS/Azure, a single VPC Network hosts subnets in every region without peering. Verify subnet distribution matches workload regions.
- **Subnet IP ranges:** Primary ranges for VMs, secondary ranges for GKE Pod and Service CIDRs (alias IP ranges). Check for overlapping ranges and sufficient growth space.
- **Private Google Access:** Enables VMs without external IPs to reach Google APIs. Disabled Private Google Access on internal-only subnets is a Medium finding.
- **VPC Flow Logs:** Per-subnet enablement in GCP (not VPC-level like AWS). Subnets without VPC Flow Logs lack traffic visibility — flag as High for production.

### Step 2: Firewall Rule Audit

Audit VPC Network firewall rules using GCP's priority-based evaluation and hierarchical firewall policies.

```
gcloud compute firewall-rules list --filter="network:<network-name>"
gcloud compute firewall-rules describe <rule-name>
```GCP firewall rules evaluate by priority (0–65535, lowest = highest priority). First match wins.

- **Implied rules:** Every VPC Network has implied deny-all-ingress and allow-all-egress at priority 65535. Not visible in `gcloud compute firewall-rules list` but active. Custom rules at 0–65534 override them.
- **Priority conflicts:** An allow at priority 1000 overrides a deny at 2000. Verify deny rules have lower priority numbers than conflicting allows.
- **Target tags vs service accounts:** Target tags are mutable labels — any project editor can change VM tags to bypass firewall rules. Service account targets are IAM-controlled and more secure. Flag tag-based rules on sensitive workloads as Medium.
- **Source ranges:** Rules permitting ingress from `0.0.0.0/0`. SSH/RDP from 0.0.0.0/0 is Critical. Verify broad ranges are justified.
- **Disabled rules:** GCP firewall rules can be disabled without deletion. A disabled deny rule leaves a security gap.
- **Default network rules:** The `default` VPC Network includes pre-created rules allowing ICMP, SSH, RDP, and internal traffic. Audit these permissive rules.

**Hierarchical firewall policies:**

```
gcloud compute firewall-policies list --organization <org-id>
gcloud compute firewall-policies describe <policy-name>
gcloud compute firewall-policies rules list --firewall-policy <policy-name>
```

Hierarchical firewall policies apply at organization or folder level and evaluate before VPC Network firewall rules. A `deny` in a hierarchical policy blocks traffic regardless of VPC-level allows. A `goto_next` action delegates to VPC-level rules. Verify hierarchical policies enforce org-wide baselines (e.g., block SSH from internet).

### Step 3: Cloud NAT and Egress Analysis

Audit Cloud NAT gateways for egress capacity, port allocation, and logging.

```
gcloud compute routers nats list --router <router-name> --region <region>
gcloud compute routers nats describe <nat-name> --router <router-name> --region <region>
```
Cloud NAT provides outbound internet access for VMs without external IPs, configured on a Cloud Router.

- **IP allocation method:** Automatic (GCP assigns IPs) or manual (reserved IPs). Manual provides predictable egress IPs for third-party allowlisting.
- **Port allocation:** Default 64 minimum ports per VM. Port exhaustion drops connections. Check `minPortsPerVm`/`maxPortsPerVm`. High-connection workloads need increased allocations. Enable Dynamic Port Allocation for bursty workloads.
- **Endpoint-Independent Mapping:** When enabled, Cloud NAT uses consistent IP:port mappings, improving protocol compatibility. Disabled by default.
- **Cloud NAT logging:** Verify `logConfig.enable`. Options: ERRORS_ONLY, TRANSLATIONS_AND_ERRORS (recommended), ALL. Missing NAT logging reduces egress visibility.
- **Subnet coverage:** Cloud NAT applies to all subnets or specific subnets. Verify production subnets are covered.

### Step 4: Connectivity Analysis

Evaluate hybrid and cross-project connectivity via Cloud Interconnect, Cloud VPN, and Shared VPC.

**Cloud Interconnect:**

```
gcloud compute interconnects list
gcloud compute interconnects describe <interconnect-name>
gcloud compute interconnects attachments list --region <region>
gcloud compute interconnects attachments describe <attachment-name> --region <region>
```

- **VLAN attachment state:** Verify `state: ACTIVE` and `operationalStatus: OS_ACTIVE`. `UNPROVISIONED_ATTACHMENT` means partner provisioning incomplete. `OS_LACP_DOWN` indicates link aggregation failure.
- **BGP session health:** Each VLAN attachment peers with a Cloud Router via BGP. `UP` is healthy, `DOWN` indicates ASN mismatch, authentication failure, or network issue. Verify primary and redundant sessions.
- **MED values:** Multi-Exit Discriminator influences route preference across multiple Cloud Interconnect attachments. Lower MED preferred. Verify values match active/standby design.
- **Redundancy:** Production requires connections in two edge availability domains. Single-connection topology is a High finding.

**Cloud VPN:**

```
gcloud compute vpn-tunnels list
gcloud compute vpn-tunnels describe <tunnel-name> --region <region>
gcloud compute vpn-gateways list
```

- **Tunnel status:** Should show `status: ESTABLISHED`. `FIRST_HANDSHAKE` indicates IKE negotiation in progress. `NO_INCOMING_PACKETS` suggests on-premises misconfiguration.
- **HA VPN:** High Availability VPN provides two tunnels for 99.99% SLA. Use HA VPN for production (Classic VPN offers no redundancy SLA).

**Shared VPC:**

```
gcloud compute shared-vpc get-host-project <service-project-id>
gcloud compute shared-vpc list-associated-resources <host-project-id>
gcloud compute networks subnets get-iam-policy <subnet> --region <region> --project <host-project>
```

- **Host/service project model:** Shared VPC lets a host project share VPC Network subnets with service projects. Verify host project designation and service project associations.
- **Subnet-level IAM:** Shared VPC permissions granted per subnet via `compute.networkUser` role. Verify service accounts access only intended subnets.
- **Private Google Access inheritance:** Service projects inherit settings from host project subnets. Verify enablement.

### Step 5: Cloud Router and Routing Validation

Audit Cloud Router configuration for route advertisements, BGP settings, and dynamic routing mode.

```
gcloud compute routers list --project <project-id>
gcloud compute routers describe <router-name> --region <region>
gcloud compute routers get-status <router-name> --region <region>
```

- **Dynamic routing mode:** `regional` or `global`. Regional: Cloud Routers advertise/learn routes only within their region. Global: routes propagate across all regions. Multi-region workloads accessing on-premises via single-region Cloud Interconnect require global mode.
- **Custom route advertisements:** Default: advertise all subnets. Custom mode overrides — verify no subnets are accidentally excluded from advertisements.
- **Graceful restart:** Preserves forwarding during Cloud Router updates. Enable for production routers.
- **AS path analysis:** Review `get-status` learned routes and AS paths. Unexpected paths indicate route leaks or suboptimal selection.
- **Route priorities:** Custom routes use priority 0–65535 (default 1000). Lower preferred. Verify priorities create intended active/standby or ECMP behavior.
- **Learned route limits:** Cloud Router has per-region learned route limits. Approaching limits causes drops — check `get-status` for count versus limits.

### Step 6: Report and Optimization

Compile findings and identify optimization opportunities.

```
gcloud compute addresses list --filter="status=RESERVED" --project <project-id>
gcloud compute instances list --filter="networkInterfaces[].accessConfigs[].natIP:*"
gcloud compute firewall-rules list --filter="disabled=true"
```

- **Unused static IPs:** Reserved external IPs not associated with resources incur charges. Release unused addresses.
- **Disabled firewall rules:** Create audit confusion. Delete or document justification.
- **Over-permissive tag-based rules:** Firewall rules targeting broad tags on high-privilege workloads should migrate to service account targets.
- **IP address utilization:** GCP reserves 4 addresses per subnet. Subnets with <10% available are exhaustion risks. Over-provisioned subnets waste space in Shared VPC.
- **Cloud NAT consolidation:** Multiple gateways per region unnecessary unless subnets need different configs.

Compile the findings report using the Report Template section.

## Threshold Tables

### Firewall Rule Severity

| Finding | Severity | Rationale |
|---------|----------|-----------|
| Firewall rule allows SSH (22) from 0.0.0.0/0 | Critical | Shell access from internet |
| Firewall rule allows RDP (3389) from 0.0.0.0/0 | Critical | Remote desktop from internet |
| Firewall rule allows all ports from 0.0.0.0/0 | Critical | No port restriction on ingress |
| Target tag on sensitive workload instead of service account | High | Tags mutable by project editors |
| Hierarchical firewall policy missing at org level | High | No organization-wide baseline |
| VPC Flow Logs disabled on production subnet | High | No traffic visibility |
| Firewall rule with priority 0 | High | Audit for broad scope |
| Disabled firewall rule undocumented | Medium | Audit confusion risk |
| Auto-mode VPC Network in production | Medium | Uncontrolled IP allocation |
| Firewall rule with >20 source ranges | Medium | Excessive complexity |

### Cloud Interconnect Health

| Metric | Severity | Action |
|--------|----------|--------|
| VLAN attachment state not ACTIVE | Critical | No traffic flow — engage provider |
| BGP session DOWN | High | Check ASN, authentication, link |
| Single edge availability domain | High | No redundancy — add second |
| Learned route count >80% limit | Medium | Approaching route capacity |

### Cloud NAT Port Utilization

| Available Ports (%) | Severity | Action |
|---------------------|----------|--------|
| <10% | Critical | Connection drops — increase allocation |
| 10–25% | High | Enable Dynamic Port Allocation |
| 25–50% | Medium | Monitor trend |
| >50% | Low | Healthy |

## Decision Trees

### Is This Firewall Rule Overly Permissive?

```
Firewall rule under review
├── Source range is 0.0.0.0/0?
│   ├── Yes
│   │   ├── Port = 22 (SSH) or 3389 (RDP)?
│   │   │   ├── Yes → CRITICAL: Use IAP tunnel instead
│   │   │   └── No
│   │   │       ├── Port = 443 on load balancer backend?
│   │   │       │   ├── Yes → Acceptable for public services
│   │   │       │   └── No → HIGH: Review necessity
│   │   │       └── All ports (all protocols)?
│   │   │           └── CRITICAL: Unrestricted ingress
│   │   └── Is rule disabled?
│   │       ├── Yes → LOW: Verify it should remain disabled
│   │       └── No → Classify severity by port scope
│   └── No (specific CIDR or service account source)
│       ├── Target uses service account? → Stronger binding
│       └── Target uses network tag?
│           ├── Tag on sensitive workload? → MEDIUM: Migrate to service account
│           └── Tag on dev/test? → LOW: Acceptable
```

### Is This VPC Network Design Following GCP Best Practices?

```
VPC Network under review
├── Custom-mode?
│   ├── No (auto-mode) → MEDIUM for production
│   └── Yes
│       ├── Subnets in required regions? → Verify
│       ├── VPC Flow Logs on production subnets?
│       │   ├── No → HIGH: No traffic visibility
│       │   └── Yes → Check aggregation and sampling
│       └── Private Google Access?
│           ├── No → MEDIUM: Internal VMs cannot reach APIs
│           └── Yes → Good
├── Shared VPC?
│   ├── Yes → Audit host designation, subnet IAM, associations
│   └── No → OK for single-project
├── Hierarchical firewall policy?
│   ├── No → HIGH: No org-wide baseline
│   └── Yes → Audit goto_next vs deny
└── Dynamic routing mode?
    ├── Regional + multi-region → Switch to global
    └── Global → Verify cross-region propagation
```

## Report Template

```
GCP VPC NETWORK AUDIT REPORT
================================
Project: [project-id] ([project-name])
Organization: [org-id or N/A]
VPC Network: [network-name]
Routing Mode: [regional/global]
Network Type: [auto-mode/custom-mode]
Audit Date: [timestamp]
Performed By: [operator/agent]

VPC NETWORK ARCHITECTURE:
Subnets: [total] across [n] regions
Type: [auto-mode/custom-mode]
Private Google Access: [enabled on n/total subnets]
VPC Flow Logs: [enabled on n/total subnets]

FIREWALL RULES:
Total: [n] | With 0.0.0.0/0 ingress: [n] | Disabled: [n]
Target type: tag-based:[n] service-account:[n] all-instances:[n]
Hierarchical policies: [n at org] [n at folder]

CLOUD NAT:
Gateways: [n] | Covered subnets: [n]
IP allocation: [automatic/manual] | Port min: [n]
NAT logging: [enabled/disabled]

CONNECTIVITY:
Cloud Interconnect: [n attachments] | BGP: [UP/DOWN]
Cloud VPN: [n tunnels] | Status: [ESTABLISHED/other]
Shared VPC: [host-project or N/A] | Service projects: [n]

CLOUD ROUTER:
Routers: [n] | Dynamic mode: [regional/global]
Custom advertisements: [yes/no]
Graceful restart: [enabled/disabled]
Learned routes: [n] / [limit]

OPTIMIZATION:
Unused static IPs: [n] | Disabled firewall rules: [n]
Tag-based rules on sensitive workloads: [n]
Cloud NAT port utilization: [assessment]

FINDINGS:
1. [Severity] [Category] — [Description]
   Resource: [resource-name] → Recommendation: [action]

RECOMMENDATIONS: [prioritized by severity]
NEXT AUDIT: [CRITICAL: 30d, HIGH: 90d, clean: 180d]
```

## Troubleshooting

### VPC Flow Logs Not Enabled on Subnets

VPC Flow Logs in GCP are subnet-level, not VPC-level. Each subnet must
be individually enabled. Enabling is non-disruptive. Missing VPC Flow
Logs on production subnets is a High finding.

### Firewall Rule Not Applied to Expected VMs

Verify the target: if using a target tag, confirm the tag is on the VM
(tags are case-sensitive). If using a service account target, verify the
VM runs with that account. Firewall rules with no target apply to all
VMs in the VPC Network.

### Cloud Interconnect VLAN Attachment Not Active

Check `state` and `operationalStatus`. `UNPROVISIONED_ATTACHMENT` means
partner provisioning incomplete. `OS_LACP_DOWN` indicates Layer 2
failure. Verify Cloud Router BGP session has correct ASN and IP pair.

### Shared VPC Service Project Cannot Deploy to Subnet

Verify the deploying service account has `compute.networkUser` on the
specific subnet in the host project. Subnet-level IAM is required even
if the service project is associated with the host project.

### Cloud Router BGP Session Flapping

Check Cloud Logging with `resource.type="gce_router"`. Common causes:
on-premises router exceeding learned route limit, authentication key
mismatch, or MTU issues on the Cloud Interconnect link. Enable graceful
restart to preserve forwarding during brief flaps.
