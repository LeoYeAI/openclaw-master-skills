---
name: aws-networking-audit
description: >-
  AWS VPC networking audit covering CIDR architecture, Security Group and
  NACL rule analysis, Transit Gateway connectivity, VPC Flow Log forensics,
  Route Table validation, and ENI/EIP resource optimization using read-only
  AWS CLI commands.
license: Apache-2.0
metadata:
  safety: read-only
  author: network-security-skills-suite
  version: "1.0.0"
  openclaw: '{"emoji":"☁️","safetyTier":"read-only","requires":{"bins":["aws"],"env":["AWS_ACCESS_KEY_ID"]},"tags":["aws","vpc","cloud"],"mcpDependencies":["aws-network-mcp"],"egressEndpoints":["*.amazonaws.com:443"]}'
---

# AWS VPC Networking Security Audit

Cloud resource audit for AWS Virtual Private Cloud (VPC) architecture,
security posture, and connectivity. This skill evaluates provider-specific
AWS networking constructs — VPC design, Security Groups, NACLs, Transit
Gateway topologies, VPC Flow Logs, Route Tables, and ENI placement — not
generic cloud networking advice.

Scope covers VPC-layer networking: CIDR planning, subnet tier layout,
security filtering, inter-VPC connectivity, and traffic observability.
Out of scope: CloudFront distributions, WAF rules, application-layer
load balancing (ALB content routing), and DNS (Route 53) configuration.
Reference `references/cli-reference.md` for read-only AWS CLI commands
organized by audit step, and `references/vpc-architecture.md` for the
VPC packet flow model, Security Group vs NACL evaluation order, and
Transit Gateway routing architecture.

## When to Use

- VPC architecture design review — validating CIDR allocation, subnet tier layout, and AZ distribution before or after deployment
- Post-migration networking audit — verifying VPC connectivity, Security Group rules, and Route Table entries after workload migration
- Security assessment — identifying overly permissive Security Group rules, default NACL exposure, and missing VPC Flow Log coverage
- Connectivity troubleshooting — diagnosing Transit Gateway route propagation failures, VPC peering asymmetric routing, or black-hole routes
- Compliance preparation — documenting VPC segmentation, Security Group justification, and Flow Log retention for auditors
- Cost optimization review — identifying unused Elastic Network Interfaces (ENIs), unattached Elastic IPs (EIPs), and cross-AZ traffic patterns

## Prerequisites

- **AWS CLI v2** configured with valid credentials (`aws sts get-caller-identity` succeeds)
- **IAM permissions** — minimum read-only policy covering: `ec2:DescribeVpcs`, `ec2:DescribeSubnets`, `ec2:DescribeSecurityGroups`, `ec2:DescribeNetworkAcls`, `ec2:DescribeTransitGateways`, `ec2:DescribeTransitGatewayRouteTables`, `ec2:DescribeRouteTables`, `ec2:DescribeFlowLogs`, `ec2:DescribeNetworkInterfaces`, `ec2:DescribeVpcPeeringConnections`, `ec2:DescribeVpcEndpoints`, `ec2:DescribeAddresses`, `logs:FilterLogEvents`, `logs:DescribeLogGroups`
- **Target scope identified** — specific VPC ID(s), AWS account, and region. Multi-account audits require cross-account IAM roles or AWS Organizations access
- **VPC Flow Logs enabled** — Step 4 requires active Flow Logs publishing to CloudWatch Logs or S3. If Flow Logs are not enabled, document this as a Critical finding

## Procedure

Follow these six steps sequentially. Each step builds on prior findings,
moving from inventory through security analysis to optimization.

### Step 1: VPC Inventory and Design Assessment

Enumerate all VPCs in the target region and assess architectural design.

```
aws ec2 describe-vpcs --region <region> --output table
aws ec2 describe-subnets --filters "Name=vpc-id,Values=<vpc-id>" --output table
```

For each VPC, evaluate:

- **CIDR block allocation:** Primary and secondary CIDR blocks. Check for RFC 1918 compliance, overlapping CIDRs across VPCs (blocks peering), and sufficient address space for growth. VPCs support up to 5 CIDR blocks.
- **Subnet tier layout:** Identify public subnets (Route Table routes to Internet Gateway), private subnets (Route Table routes to NAT Gateway), and isolated subnets (no internet route). Verify each tier exists and workloads are placed in the correct tier.
- **Availability Zone distribution:** Subnets should span at least 2 AZs for resilience. Single-AZ VPC designs are a High finding.
- **DNS settings:** Verify `enableDnsSupport` and `enableDnsHostnames` are enabled — required for VPC endpoints and private DNS resolution.
- **Tenancy:** Default vs dedicated. Dedicated tenancy has significant cost implications; verify it is intentional.

### Step 2: Security Group and NACL Analysis

Audit stateful Security Group rules and stateless NACL rules for overly permissive access.

**Security Group analysis:**

```
aws ec2 describe-security-groups --filters "Name=vpc-id,Values=<vpc-id>"
```

For each Security Group, evaluate inbound and outbound rules:

- **0.0.0.0/0 inbound rules:** Any Security Group rule permitting inbound from `0.0.0.0/0` (or `::/0`) is a finding. Severity depends on port: SSH/RDP from 0.0.0.0/0 is Critical; HTTPS from 0.0.0.0/0 on a public ALB may be acceptable.
- **SG-to-ENI mapping on public subnets:** Cross-reference Security Groups with ENIs on public subnets. An overly permissive Security Group attached to an ENI in a public subnet with a public IP is higher risk than the same Security Group on a private subnet.
- **Default Security Group:** The VPC default Security Group allows all inbound from itself and all outbound. If any ENI uses the default Security Group, flag as Medium — workloads should use purpose-specific Security Groups.
- **Unused Security Groups:** Security Groups with no associated ENIs are cleanup candidates.

**NACL analysis:**

```
aws ec2 describe-network-acls --filters "Name=vpc-id,Values=<vpc-id>"
```

NACLs are stateless — evaluate both inbound and outbound rule sets:

- **Rule ordering:** NACLs evaluate rules by rule number (lowest first). A broad permit at rule 100 cannot be overridden by a deny at rule 200. Verify deny rules are numbered lower than corresponding permits.
- **Default NACL:** Allows all inbound and outbound traffic. Subnets using the default NACL have no network-layer filtering beyond Security Groups. Flag as Medium if used on production subnets.
- **Ephemeral port range:** Outbound NACLs must permit ephemeral ports (1024–65535) for return traffic. Missing ephemeral port rules break TCP connections.

### Step 3: Transit Gateway and Connectivity Assessment

Evaluate inter-VPC and hybrid connectivity through Transit Gateway (TGW), VPC Peering, and VPC Endpoints.

**Transit Gateway:**

```
aws ec2 describe-transit-gateways
aws ec2 describe-transit-gateway-route-tables --transit-gateway-id <tgw-id>
aws ec2 search-transit-gateway-routes --transit-gateway-route-table-id <tgw-rt-id> --filters "Name=state,Values=active"
```

- **TGW route table associations:** Each VPC attachment should be associated with the correct TGW Route Table. Misassociations cause traffic to route to wrong VPCs.
- **Route propagation:** Verify propagation is enabled for VPC attachments that need dynamic routing. Disabled propagation requires manual static routes — check for stale entries.
- **TGW peering:** For multi-region Transit Gateway peering, verify routes are propagated across regions and CIDR blocks don't overlap.

**VPC Peering:**

```
aws ec2 describe-vpc-peering-connections --filters "Name=status-code,Values=active"
```

- **Route validation:** VPC peering is non-transitive. Verify Route Tables in both VPCs contain routes pointing to the peering connection for the peer CIDR. Missing routes cause silent packet drops.
- **DNS resolution:** Check `AllowDnsResolutionFromRemoteVpc` for cross-VPC private DNS.

**VPC Endpoints:**

```
aws ec2 describe-vpc-endpoints --filters "Name=vpc-id,Values=<vpc-id>"
```

- **Gateway endpoints:** S3 and DynamoDB. Verify Route Table entries exist for gateway endpoint prefix lists.
- **Interface endpoints (PrivateLink):** Verify ENI placement in appropriate subnets and Security Group rules permit traffic from workloads.

### Step 4: VPC Flow Log Analysis

Analyze VPC Flow Logs for security events and traffic patterns.

```
aws ec2 describe-flow-logs --filter "Name=resource-id,Values=<vpc-id>"
```

Verify Flow Logs are enabled at the VPC level (not just subnet or ENI level) with REJECT and ACCEPT capture. If Flow Logs are not enabled, document as Critical and recommend enabling before further analysis.

For active Flow Logs, query CloudWatch Logs:

```
aws logs filter-log-events --log-group-name <flow-log-group> --filter-pattern "REJECT"
```

Analyze patterns:

- **Reject patterns:** High-volume REJECTs from external IPs suggest scanning or attack traffic. REJECTs between internal subnets indicate Security Group or NACL misconfigurations.
- **Cross-AZ traffic volume:** Flow Logs show source/destination AZ. Significant cross-AZ traffic incurs data transfer costs — identify top cross-AZ flows.
- **Top talkers:** Aggregate by source/destination ENI to find highest-volume flows. Unexpected top talkers may indicate compromised instances or data exfiltration.
- **SG deny correlation:** Flow Log REJECTs from specific ENIs should correlate with Security Group rules. If an ENI shows REJECTs for traffic that its Security Group should permit, investigate NACL interference.

### Step 5: Route Table Validation

Audit Route Tables for correctness, efficiency, and security.

```
aws ec2 describe-route-tables --filters "Name=vpc-id,Values=<vpc-id>"
```

For each Route Table, evaluate:

- **Main vs custom Route Tables:** The VPC main Route Table is the default for subnets without explicit association. Verify the main Route Table has restrictive routes — an overly permissive main Route Table affects all unassociated subnets.
- **Most-specific route precedence:** AWS Route Tables use longest prefix match. Verify that more-specific routes take precedence as intended and don't create unintended traffic paths.
- **Black-hole routes:** Routes with status "blackhole" indicate the target (NAT Gateway, VPC peering, TGW attachment) was deleted. Black-hole routes silently drop traffic. Remove or replace.
- **NAT Gateway routing:** Private subnets should route `0.0.0.0/0` to a NAT Gateway for outbound internet access. Verify NAT Gateway is in a public subnet with an EIP. Multi-AZ deployments should have one NAT Gateway per AZ to avoid cross-AZ traffic and single-AZ failure.
- **VPC endpoint routes:** Gateway endpoint routes (S3, DynamoDB prefix lists) should exist in Route Tables for subnets that access those services.

### Step 6: Report and Optimization

Compile findings and identify resource optimization opportunities.

**Unused resource cleanup:**

```
aws ec2 describe-network-interfaces --filters "Name=vpc-id,Values=<vpc-id>" "Name=status,Values=available"
aws ec2 describe-addresses --filters "Name=domain,Values=vpc"
```

- **Unused ENIs:** ENIs in "available" status are not attached to instances. Identify orphaned ENIs from terminated instances or failed deployments.
- **Unattached EIPs:** Elastic IPs not associated with an ENI incur hourly charges. Release or associate.
- **NAT Gateway optimization:** Consolidate NAT Gateways if traffic volume doesn't justify per-AZ deployment, or deploy per-AZ if cross-AZ data transfer costs exceed NAT Gateway costs.

Compile the findings report using the Report Template section.

## Threshold Tables

### Security Group Rule Severity

| Finding | Severity | Rationale |
|---------|----------|-----------|
| SG allows SSH (22) from 0.0.0.0/0 | Critical | Direct shell access from internet |
| SG allows RDP (3389) from 0.0.0.0/0 | Critical | Remote desktop open to internet |
| SG allows all ports from 0.0.0.0/0 | Critical | No port restriction on internet access |
| ENI on public subnet using default SG | High | Default SG permits all inbound from group members |
| SG with >50 inbound rules | High | Excessive complexity; likely over-permissive |
| SG allows database ports from non-app subnets | High | Database access not restricted to application tier |
| SG with no description on rules | Medium | Limits auditability and rule justification |
| SG with 0 associated ENIs | Medium | Unused — cleanup candidate |

### VPC Flow Log Reject Rate

| Reject Rate (per minute) | Severity | Action |
|--------------------------|----------|--------|
| >1000 external-source REJECTs | High | Active scanning or DDoS — review source IPs |
| >100 internal-to-internal REJECTs | High | Misconfigured SG or NACL — investigate rules |
| 10–100 external REJECTs | Medium | Background noise — monitor trend |
| <10 external REJECTs | Low | Normal background scanning |

### Subnet Utilization

| Available IPs (% of CIDR) | Severity | Action |
|----------------------------|----------|--------|
| <10% remaining | High | Subnet exhaustion risk — plan CIDR expansion |
| 10–25% remaining | Medium | Monitor growth — plan expansion proactively |
| >75% unused | Low | Over-provisioned — consider smaller CIDR next time |

## Decision Trees

### Is This Security Group Rule Overly Permissive?

```
Security Group rule under review
├── Source is 0.0.0.0/0 (or ::/0)?
│   ├── Yes
│   │   ├── Port = 22 (SSH) or 3389 (RDP)?
│   │   │   ├── Yes → CRITICAL: Management ports open to internet
│   │   │   │   └── Restrict to known IP ranges or use SSM/bastion
│   │   │   └── No
│   │   │       ├── Port = 443 (HTTPS) on public-facing ALB/NLB?
│   │   │       │   ├── Yes → Acceptable for public services
│   │   │       │   └── No → HIGH: Review necessity of open port
│   │   │       └── Port = ALL?
│   │   │           └── CRITICAL: All ports open to internet
│   │   └── ENI attached to public subnet instance?
│   │       ├── Yes → Risk amplified — instance directly reachable
│   │       └── No (private subnet) → Lower risk but still flag
│   └── No (specific source CIDR or SG reference)
│       ├── SG self-reference?
│       │   └── Acceptable for cluster communication
│       └── Cross-VPC or broad CIDR (/8, /16)?
│           └── Medium — verify least-privilege intent
```

### Is This VPC Design Following AWS Best Practices?

```
VPC design under review
├── Multiple AZs used?
│   ├── No → HIGH: Single point of failure
│   └── Yes
│       ├── Subnet tiers defined (public/private/isolated)?
│       │   ├── No → HIGH: Flat network — no segmentation
│       │   └── Yes
│       │       ├── Public subnets have IGW route?
│       │       │   └── Verify only intended subnets are public
│       │       ├── Private subnets route to NAT GW?
│       │       │   ├── Per-AZ NAT GW? → Best practice
│       │       │   └── Single NAT GW → Cost-optimized but AZ risk
│       │       └── Isolated subnets have no internet route?
│       │           └── Verify — should only reach VPC endpoints
│       ├── VPC Flow Logs enabled?
│       │   ├── No → CRITICAL: No traffic visibility
│       │   └── Yes → Check retention and capture scope
│       └── CIDR planning?
│           ├── Overlaps with peered VPCs? → Blocks connectivity
│           └── Sufficient for growth? → Plan secondary CIDRs
```

## Report Template

```
AWS VPC NETWORKING AUDIT REPORT
==================================
Account: [account-id] ([account-alias])
Region: [region]
VPC: [vpc-id] ([Name tag])
CIDR Blocks: [primary] [secondary if any]
Audit Date: [timestamp]
Performed By: [operator/agent]

VPC ARCHITECTURE:
Subnets: [total] (public:[n] private:[n] isolated:[n])
AZs: [list]
DNS: enableDnsSupport=[yes/no] enableDnsHostnames=[yes/no]
Tenancy: [default/dedicated]

SECURITY GROUPS:
Total: [n] | With 0.0.0.0/0 inbound: [n] | Unused (0 ENIs): [n]
Default SG in use: [yes/no — ENI count]
Rules total: [n] inbound / [n] outbound

NACLs:
Total: [n] | Using default NACL: [n subnets]
Custom NACLs: [n] | Stateless rules reviewed: [n]

CONNECTIVITY:
Transit Gateway: [tgw-id or N/A] | Attachments: [n]
VPC Peering: [n active] | Route validation: [pass/issues]
VPC Endpoints: [n] (gateway:[n] interface:[n])

FLOW LOGS:
Status: [enabled/disabled] | Capture: [ALL/ACCEPT/REJECT]
Log destination: [CloudWatch/S3] | Retention: [days]
Reject rate: [n/min avg] | Top reject sources: [list]

ROUTE TABLES:
Total: [n] | Main RT associations: [n subnets]
Black-hole routes: [n] | NAT GW routes: [n]

RESOURCE OPTIMIZATION:
Unused ENIs: [n] | Unattached EIPs: [n]
Cross-AZ traffic: [high/moderate/low]
NAT GW count: [n] across [n] AZs

FINDINGS:
1. [Severity] [Category] — [Description]
   Resource: [sg-xxx / rtb-xxx / nacl-xxx]
   Issue: [detail] → Recommendation: [action]

RECOMMENDATIONS: [prioritized by severity]
NEXT AUDIT: [CRITICAL findings: 30d, HIGH: 90d, clean: 180d]
```

## Troubleshooting

### VPC Flow Logs Not Enabled

If `aws ec2 describe-flow-logs` returns empty for the target VPC, Flow Logs
are not configured. Document as a Critical finding — no traffic visibility.
Flow Logs require an IAM role with `logs:CreateLogGroup`, `logs:CreateLogStream`,
`logs:PutLogEvents` permissions. Enabling Flow Logs is a non-disruptive operation.

### Security Group Not Attached to Expected ENI

Use `aws ec2 describe-network-interfaces --filters "Name=group-id,Values=<sg-id>"`
to find all ENIs associated with a Security Group. If the expected ENI is missing,
check whether the instance was replaced (Auto Scaling) or the SG was modified.

### Transit Gateway Route Propagation Disabled

If TGW routes are missing, verify propagation is enabled on the TGW Route Table
for the relevant VPC attachment. Use `aws ec2 get-transit-gateway-route-table-propagations`
to check. Disabled propagation requires manual static route entries.

### Black-Hole Routes in Route Tables

Routes with status "blackhole" occur when the target resource (NAT Gateway,
VPC Peering Connection, TGW Attachment) is deleted but the route entry remains.
Identify affected subnets and either remove the route or create a replacement target.

### Cross-Account VPC Audit

For multi-account environments using AWS Organizations, use `aws sts assume-role`
to obtain temporary credentials for each account. Alternatively, use AWS Config
aggregator or AWS RAM (Resource Access Manager) shared resources for centralized visibility.
