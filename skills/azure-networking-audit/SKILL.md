---
name: azure-networking-audit
description: >-
  Azure VNet networking audit covering address space design, NSG rule
  evaluation, Azure Firewall policy analysis, ExpressRoute and VPN Gateway
  connectivity, VNet Peering topology, and UDR validation using read-only
  Azure CLI commands.
license: Apache-2.0
metadata:
  safety: read-only
  author: network-security-skills-suite
  version: "1.0.0"
  openclaw: '{"emoji":"☁️","safetyTier":"read-only","requires":{"bins":["az"],"env":[]},"tags":["azure","vnet","cloud"],"mcpDependencies":[],"egressEndpoints":["management.azure.com:443"]}'
---

# Azure VNet Networking Security Audit

Cloud resource audit for Azure Virtual Network (VNet) architecture,
network security posture, and hybrid connectivity. This skill evaluates
provider-specific Azure networking constructs — VNet design, NSG priority-
based rules, Azure Firewall rule collection groups, ExpressRoute circuits,
VNet Peering topology, UDR forced tunneling, and Application Gateway
placement — not generic cloud networking advice.

Scope covers VNet-layer networking: address space planning, subnet
delegation, NSG filtering, Azure Firewall inspection, hybrid connectivity
via ExpressRoute and VPN Gateway, and route management. Out of scope:
Azure Front Door CDN policies, Azure WAF custom rule authoring,
application-layer routing in Application Gateway path rules, and Azure
DNS zone management. Reference `references/cli-reference.md` for read-only
Azure CLI commands organized by audit step, and `references/vnet-architecture.md`
for the VNet packet flow model, NSG evaluation order, and ExpressRoute
routing architecture.

## When to Use

- VNet architecture design review — validating address space allocation, subnet delegation, and service endpoint configuration
- Post-migration networking audit — verifying VNet connectivity, NSG rules, and UDR entries after workload migration
- Security assessment — identifying overly permissive NSG rules, default NSG exposure, and missing Azure Firewall policies
- Connectivity troubleshooting — diagnosing ExpressRoute BGP peering failures, VPN Gateway tunnel drops, or VNet Peering asymmetric routing
- Compliance preparation — documenting VNet segmentation, NSG justification, and Azure Firewall logging for auditors
- Cost optimization review — identifying unused public IPs, orphaned NICs, and underutilized Application Gateway instances

## Prerequisites

- **Azure CLI** authenticated (`az account show` succeeds)
- **RBAC permissions** — Reader role on target subscription, or granular read permissions: `Microsoft.Network/virtualNetworks/read`, `Microsoft.Network/networkSecurityGroups/read`, `Microsoft.Network/azureFirewalls/read`, `Microsoft.Network/expressRouteCircuits/read`, `Microsoft.Network/virtualNetworkGateways/read`, `Microsoft.Network/routeTables/read`, `Microsoft.Network/networkInterfaces/read`
- **Target scope identified** — specific subscription, resource group(s), and VNet name(s). Multi-subscription audits require `az account set` per subscription
- **Network Watcher enabled** — NSG Flow Logs and effective security rules require Network Watcher in the target region. If disabled, document as Critical

## Procedure

Follow these six steps sequentially. Each step builds on prior findings,
moving from inventory through security analysis to optimization.

### Step 1: VNet Inventory and Design Assessment

Enumerate all VNets in the target subscription and assess architectural design.

```
az network vnet list --output table
az network vnet show --name <vnet-name> --resource-group <rg>
az network vnet subnet list --vnet-name <vnet-name> --resource-group <rg>
```

For each VNet, evaluate:

- **Address space allocation:** Primary and additional address spaces. Check RFC 1918 compliance, overlapping address spaces across peered VNets (blocks VNet Peering), and sufficient space for growth.
- **Subnet layout:** Identify subnets by purpose — workload subnets, AzureFirewallSubnet (required name for Azure Firewall), GatewaySubnet (required for VPN Gateway and ExpressRoute Gateway), AzureBastionSubnet. Verify required named subnets exist for deployed services.
- **Subnet delegation:** Check delegations to Azure services (`Microsoft.Sql/managedInstances`, `Microsoft.Web/serverFarms`). Delegated subnets restrict which resources can deploy — a subnet delegated to SQL Managed Instance cannot host VMs or other services.
- **Service endpoints vs Private Endpoints:** Service endpoints route PaaS traffic over Azure backbone but don't remove public endpoints on the PaaS resource. Private Endpoints create a private IP within the VNet for the PaaS service, removing public exposure entirely. Audit whether data services (Storage, SQL, Key Vault) use Private Endpoints (preferred for zero-trust) or service endpoints (legacy approach with broader exposure).
- **DDoS Protection:** Verify whether DDoS Protection Standard is enabled on the VNet. Basic DDoS protection is automatic for all Azure resources; Standard adds volumetric attack mitigation, cost protection guarantees, and access to the DDoS Rapid Response team.

### Step 2: NSG Rule Audit

Audit Network Security Groups using Azure's priority-based evaluation model.

```
az network nsg list --output table
az network nsg rule list --nsg-name <nsg-name> --resource-group <rg> --include-default --output table
```

NSG rules evaluate by priority (lowest number = highest priority, range 100–4096). First match wins.

- **Priority ordering conflicts:** An Allow at priority 200 cannot be overridden by a Deny at 300. Verify Deny rules have lower priority numbers than conflicting Allows — inverse of AWS NACL logic.
- **Default NSG rules:** Azure creates three default inbound rules (AllowVNetInBound 65000, AllowAzureLoadBalancerInBound 65001, DenyAllInBound 65500) and three outbound defaults (AllowVNetOutBound, AllowInternetOutBound, DenyAllOutBound). These cannot be deleted but are overridden by any custom rule with lower priority number.
- **Internet inbound:** NSG rules permitting inbound from `*` or the `Internet` service tag. SSH/RDP from Internet is Critical; HTTPS on an Application Gateway subnet may be acceptable. The `Internet` service tag covers all public IP space excluding VNet, peered VNet, and on-premises address ranges.
- **Effective security rules:** NSGs apply at both subnet and NIC level. Azure evaluates subnet NSG first (inbound), then NIC NSG — traffic must pass both. Use `az network nic show-effective-nsg` to see the combined effective rules with resolved priorities. A rule allowed by subnet NSG but denied by NIC NSG is effectively denied.
- **Application Security Groups (ASGs):** ASGs group NICs for use as source/destination in NSG rules instead of IP ranges. Audit ASG membership for correctness.
- **Unused NSGs:** NSGs not associated with any subnet or NIC are cleanup candidates.

### Step 3: Azure Firewall and Network Security

Evaluate Azure Firewall policies, rule collection groups, and threat intelligence.

```
az network firewall list --output table
az network firewall policy rule-collection-group list --policy-name <policy> --resource-group <rg>
```

- **Rule collection group priority:** Azure Firewall processes rule collection groups by priority (lowest first). DNAT rules process first, then Network rules, then Application rules.
- **DNAT rules:** Translate inbound traffic to private IPs. Verify each DNAT rule maps to a valid backend. Stale DNAT rules pointing to decommissioned hosts create exposure.
- **Network rules:** Permit/deny by IP, port, protocol. Audit for overly broad rules (`*` source/destination, wide port ranges).
- **Application rules:** Filter outbound by FQDN/URL. Verify application rules enforce FQDN restrictions for workload internet access.
- **Threat intelligence mode:** Azure Firewall supports threat intelligence filtering in Alert or Deny mode. Verify production firewalls use Deny mode.
- **IDPS:** Azure Firewall Premium supports signature-based IDPS. Verify mode (Alert vs Alert and Deny) and that bypass rules are justified.
- **Azure Firewall subnet:** AzureFirewallSubnet must be /26 or larger with a public IP and UDRs routing traffic through it.

### Step 4: Connectivity Analysis

Evaluate hybrid and inter-VNet connectivity through ExpressRoute, VPN Gateway, and VNet Peering.

**ExpressRoute:**

```
az network express-route show --name <circuit> --resource-group <rg>
az network express-route peering list --circuit-name <circuit> --resource-group <rg>
```

- **Circuit status:** Verify ExpressRoute circuit shows "Provisioned" (provider side) and "Enabled" (Azure side). "NotProvisioned" means the provider has not completed circuit setup — no traffic will flow.
- **BGP peering state:** Check Azure Private Peering and Microsoft Peering BGP session state. State should be "Connected" — "Idle" or "Active" without "Connected" indicates peering negotiation failure (ASN mismatch, VLAN ID mismatch, or provider issue).
- **Advertised routes:** Verify on-premises routes are visible in Azure via `az network express-route list-route-tables` and Azure VNet routes are advertised back to on-premises. Missing routes cause silent traffic drops.

**VPN Gateway:**

```
az network vpn-connection show --name <conn> --resource-group <rg>
```

- **Connection status:** Should show "Connected". "Connecting" indicates IKE/IPsec parameter mismatch.
- **Gateway SKU:** Basic SKU lacks BGP and zone-redundancy. VpnGw2+ recommended for production.

**VNet Peering:**

```
az network vnet peering list --vnet-name <vnet> --resource-group <rg> --output table
```

- **Peering state:** Both sides must show "Connected". "Initiated" means reciprocal peering missing.
- **Transit settings:** `AllowGatewayTransit` on hub and `UseRemoteGateways` on spoke enable shared ExpressRoute/VPN. Verify settings match hub-spoke intent.
- **Address space overlap:** VNet Peering requires non-overlapping address spaces. Compare both VNets.
- **Forwarded traffic:** `AllowForwardedTraffic` must be enabled on both peering links for transit routing through Azure Firewall in the hub.

### Step 5: UDR and Routing Validation

Audit User-Defined Routes for correctness, forced tunneling, and conflicts.

```
az network route-table list --output table
az network route-table route list --route-table-name <rt> --resource-group <rg>
az network nic show-effective-route-table --name <nic> --resource-group <rg>
```

- **Forced tunneling:** UDRs with `0.0.0.0/0` next-hop to Azure Firewall or NVA force internet traffic through inspection. Verify forced tunneling is NOT applied to AzureFirewallSubnet, GatewaySubnet, or AzureBastionSubnet.
- **Asymmetric routing:** Inbound via ExpressRoute but return via Azure Firewall UDR causes asymmetry. Verify UDR next-hop addresses match expected traffic paths in both directions.
- **Effective routes per NIC:** Azure resolves UDR > BGP > system routes. Use `az network nic show-effective-route-table` for final effective routes.
- **BGP route propagation:** UDR tables can disable BGP propagation (`disableBgpRoutePropagation`). When disabled, ExpressRoute/VPN routes are not injected. Verify this matches routing design.
- **Next-hop validation:** UDR routes to virtual appliance IPs must reference running, healthy NVAs or Azure Firewall. A stopped VM next-hop creates a silent black hole.

### Step 6: Report and Optimization

Compile findings and identify resource optimization opportunities.

```
az network nic list --query "[?virtualMachine==null]" --output table
az network public-ip list --query "[?ipConfiguration==null]" --output table
```

- **Orphaned NICs:** NICs not attached to a VM — common after deletions. Each may have NSG rules and private IPs consuming address space.
- **Unassociated public IPs:** Standard SKU public IPs incur charges when unassociated. Release or associate.
- **Application Gateway optimization:** Application Gateway v2 runs continuously. Verify autoscale min/max matches traffic patterns.
- **Azure Advisor recommendations:** Check `az advisor recommendation list --category Cost` for networking optimization opportunities.

Compile the findings report using the Report Template section.

## Threshold Tables

### NSG Rule Severity

| Finding | Severity | Rationale |
|---------|----------|-----------|
| NSG allows SSH (22) from Internet | Critical | Direct shell access from internet |
| NSG allows RDP (3389) from Internet | Critical | Remote desktop open to internet |
| NSG allows all ports from * source | Critical | No port or source restriction |
| NIC with no NSG, subnet NSG allows broad access | High | No NIC-level filtering |
| Allow rule at lower priority than conflicting Deny | High | Priority ordering undermines deny intent |
| NSG allows database ports from non-app subnets | High | Database access not restricted to app tier |
| NSG with >50 custom rules | Medium | Excessive complexity |
| NSG not associated with any subnet or NIC | Medium | Unused — cleanup candidate |

### ExpressRoute Circuit Health

| Metric | Severity | Action |
|--------|----------|--------|
| Circuit status NotProvisioned | Critical | No connectivity — engage provider |
| BGP peering state Idle | High | Negotiation failure — check ASN and VLAN |
| Learned routes missing expected prefixes | High | On-prem routes not advertised |
| Circuit utilization >80% sustained | Medium | Plan upgrade or second circuit |

### Subnet Utilization

| Available IPs (% of address space) | Severity | Action |
|-------------------------------------|----------|--------|
| <10% remaining | High | Exhaustion risk — plan expansion |
| 10–25% remaining | Medium | Monitor growth proactively |
| >75% unused | Low | Over-provisioned |

## Decision Trees

### Is This NSG Rule Overly Permissive?

```
NSG rule under review
├── Source is * or Internet service tag?
│   ├── Yes
│   │   ├── Port = 22 (SSH) or 3389 (RDP)?
│   │   │   ├── Yes → CRITICAL: Use Azure Bastion instead
│   │   │   └── No
│   │   │       ├── Port = 443 on Application Gateway subnet?
│   │   │       │   ├── Yes → Acceptable for public services
│   │   │       │   └── No → HIGH: Review necessity
│   │   │       └── Port = * (all)?
│   │   │           └── CRITICAL: All ports open
│   │   └── Higher-priority Deny covering same traffic?
│   │       ├── Yes → Verify Deny priority < Allow priority
│   │       └── No → Classify severity by port
│   └── No (specific CIDR or ASG)
│       ├── ASG? → Review ASG membership scope
│       └── Broad CIDR (/8, /16)? → Medium — verify intent
```

### Is This VNet Design Following Azure Best Practices?

```
VNet under review
├── Hub-spoke topology?
│   ├── No → Acceptable for small deployments
│   └── Yes
│       ├── Hub has Azure Firewall? → Verify UDRs route spoke traffic through hub
│       ├── VNet Peering correct?
│       │   ├── AllowGatewayTransit on hub? → Required for shared gateway
│       │   ├── UseRemoteGateways on spokes? → Required for hub gateway
│       │   └── AllowForwardedTraffic on both? → Required for transit
│       └── Spoke-to-spoke via Azure Firewall? → Best practice
├── NSGs on all workload subnets?
│   ├── No → HIGH: No network filtering
│   └── Yes → Audit rules per Step 2
├── Network Watcher enabled?
│   ├── No → CRITICAL: No diagnostics
│   └── Yes → Verify NSG Flow Logs
└── Address space overlaps peered VNets? → Blocks VNet Peering
```

## Report Template

```
AZURE VNET NETWORKING AUDIT REPORT
======================================
Subscription: [id] ([name])
Resource Group(s): [list]
VNet: [name] ([resource-id])
Address Spaces: [list]
Audit Date: [timestamp]  Performed By: [operator]

VNET ARCHITECTURE:
Subnets: [total] (workload:[n] gateway:[n] firewall:[n] bastion:[n])
DDoS Protection: [Basic/Standard]
Private Endpoints: [n] | Service Endpoints: [n]

NSGs:
Total: [n] | Internet inbound: [n] | Unused: [n]
Effective rule conflicts: [n]

AZURE FIREWALL:
Deployed: [yes/no] | SKU: [Standard/Premium]
Threat intelligence: [Alert/Deny] | IDPS: [on/off]
Rule collections: DNAT:[n] Network:[n] Application:[n]

CONNECTIVITY:
ExpressRoute: [circuit or N/A] | BGP: [Connected/Idle]
VPN Gateway: [name or N/A] | Connections: [n]
VNet Peering: [n] | Gateway transit: [yes/no]

ROUTING:
UDR Tables: [n] | Forced tunneling: [n subnets]
BGP propagation disabled: [n tables]

OPTIMIZATION:
Orphaned NICs: [n] | Unassociated public IPs: [n]
Application Gateway utilization: [assessment]

FINDINGS:
1. [Severity] [Category] — [Description]
   Resource: [id] → Recommendation: [action]

NEXT AUDIT: [CRITICAL: 30d, HIGH: 90d, clean: 180d]
```

## Troubleshooting

### NSG Flow Logs Not Enabled

If Network Watcher NSG Flow Logs are not configured, traffic visibility is
limited to NSG hit counts. NSG Flow Logs require Network Watcher enabled
and a storage account. Version 2 includes throughput data. Document
missing Flow Logs as High.

### Effective Security Rules Show Unexpected Allows

Use `az network nic show-effective-nsg` for combined subnet and NIC NSG
rules. Check for: higher-priority Allow in NIC NSG overriding subnet Deny,
default rules (65000+) permitting VNet-to-VNet traffic, or ASG membership
including unintended NICs.

### ExpressRoute BGP Session Not Established

Verify VLAN ID matches between Azure and provider. Check BGP ASN matches
on-premises router. Use `az network express-route peering show` to compare
settings. Both primary and secondary should show "Connected".

### VNet Peering Shows Initiated But Not Connected

Both peering links must be created. "Initiated" means only one side is
configured. Create the reciprocal link. Cross-subscription peering requires
RBAC on both subscriptions.

### UDR Causing Asymmetric Routing

When ExpressRoute delivers inbound traffic directly but UDR routes return
traffic through Azure Firewall, asymmetric routing occurs — the firewall
drops return packets with no session state. Ensure UDR routes both
directions through the firewall, or configure Azure Firewall SNAT.
