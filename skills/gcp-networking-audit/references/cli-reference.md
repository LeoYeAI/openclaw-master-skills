# GCP gcloud CLI Reference — VPC Network Audit Commands

Read-only gcloud CLI commands organized by audit step for VPC Network
assessment. All commands are non-modifying (`list`, `describe`,
`get-status`, `get-iam-policy`). No command creates, modifies, or
deletes resources.

Access method: gcloud CLI with authenticated account. Commands assume
`--project <project-id>` is set via `gcloud config set project` or
appended to each command. Output format defaults to YAML; append
`--format=table` for human-readable output during interactive audits.

## Step 1: VPC Network Inventory and Design

| Function | Command |
|----------|---------|
| List all VPC Networks | `gcloud compute networks list` |
| Describe VPC Network | `gcloud compute networks describe <network>` |
| List all subnets | `gcloud compute networks subnets list` |
| Subnets in specific network | `gcloud compute networks subnets list --network <network>` |
| Describe subnet | `gcloud compute networks subnets describe <subnet> --region <region>` |
| Check Private Google Access | `gcloud compute networks subnets describe <subnet> --region <region> --format="value(privateIpGoogleAccess)"` |
| Check VPC Flow Logs | `gcloud compute networks subnets describe <subnet> --region <region> --format="value(logConfig)"` |
| List secondary IP ranges | `gcloud compute networks subnets describe <subnet> --region <region> --format="value(secondaryIpRanges)"` |

## Step 2: Firewall Rules

| Function | Command |
|----------|---------|
| List all firewall rules | `gcloud compute firewall-rules list` |
| Filter by network | `gcloud compute firewall-rules list --filter="network:<network>"` |
| Describe firewall rule | `gcloud compute firewall-rules describe <rule-name>` |
| List disabled rules | `gcloud compute firewall-rules list --filter="disabled=true"` |
| List ingress rules | `gcloud compute firewall-rules list --filter="direction=INGRESS"` |
| List egress rules | `gcloud compute firewall-rules list --filter="direction=EGRESS"` |
| Rules allowing 0.0.0.0/0 | `gcloud compute firewall-rules list --filter="sourceRanges=0.0.0.0/0"` |

### Hierarchical Firewall Policies

| Function | Command |
|----------|---------|
| List org-level policies | `gcloud compute firewall-policies list --organization <org-id>` |
| List folder-level policies | `gcloud compute firewall-policies list --folder <folder-id>` |
| Describe policy | `gcloud compute firewall-policies describe <policy-name>` |
| List policy rules | `gcloud compute firewall-policies rules list --firewall-policy <policy>` |
| Describe policy rule | `gcloud compute firewall-policies rules describe <priority> --firewall-policy <policy>` |
| List policy associations | `gcloud compute firewall-policies associations list --firewall-policy <policy>` |

## Step 3: Cloud NAT

| Function | Command |
|----------|---------|
| List Cloud NAT gateways | `gcloud compute routers nats list --router <router> --region <region>` |
| Describe Cloud NAT | `gcloud compute routers nats describe <nat-name> --router <router> --region <region>` |
| NAT IP addresses | `gcloud compute routers nats describe <nat-name> --router <router> --region <region> --format="value(natIps)"` |
| NAT port allocation | `gcloud compute routers nats describe <nat-name> --router <router> --region <region> --format="value(minPortsPerVm,maxPortsPerVm)"` |
| NAT logging config | `gcloud compute routers nats describe <nat-name> --router <router> --region <region> --format="value(logConfig)"` |

### Cloud NAT Metrics (Cloud Monitoring)

| Function | Command |
|----------|---------|
| NAT allocation failures | `gcloud monitoring metrics list --filter="metric.type=router.googleapis.com/nat/nat_allocation_failed"` |
| Port utilization | `gcloud monitoring metrics list --filter="metric.type=router.googleapis.com/nat/open_connections"` |

## Step 4: Connectivity

### Cloud Interconnect

| Function | Command |
|----------|---------|
| List interconnects | `gcloud compute interconnects list` |
| Describe interconnect | `gcloud compute interconnects describe <interconnect-name>` |
| List VLAN attachments | `gcloud compute interconnects attachments list --region <region>` |
| Describe VLAN attachment | `gcloud compute interconnects attachments describe <attachment> --region <region>` |
| Attachment diagnostics | `gcloud compute interconnects attachments describe <attachment> --region <region> --format="value(state,operationalStatus)"` |

### Cloud VPN

| Function | Command |
|----------|---------|
| List VPN gateways | `gcloud compute vpn-gateways list` |
| Describe VPN gateway | `gcloud compute vpn-gateways describe <gw-name> --region <region>` |
| List VPN tunnels | `gcloud compute vpn-tunnels list` |
| Describe VPN tunnel | `gcloud compute vpn-tunnels describe <tunnel> --region <region>` |
| Tunnel status | `gcloud compute vpn-tunnels describe <tunnel> --region <region> --format="value(status,detailedStatus)"` |
| List Classic VPN gateways | `gcloud compute target-vpn-gateways list` |

### Shared VPC

| Function | Command |
|----------|---------|
| Get host project | `gcloud compute shared-vpc get-host-project <service-project>` |
| List associated resources | `gcloud compute shared-vpc list-associated-resources <host-project>` |
| List Shared VPC organizations | `gcloud compute shared-vpc organizations list` |
| Subnet IAM policy | `gcloud compute networks subnets get-iam-policy <subnet> --region <region> --project <host-project>` |

## Step 5: Cloud Router and Routing

| Function | Command |
|----------|---------|
| List Cloud Routers | `gcloud compute routers list` |
| Describe Cloud Router | `gcloud compute routers describe <router> --region <region>` |
| Cloud Router status | `gcloud compute routers get-status <router> --region <region>` |
| BGP peer status | `gcloud compute routers get-status <router> --region <region> --format="value(result.bgpPeerStatus)"` |
| Advertised routes | `gcloud compute routers get-status <router> --region <region> --format="value(result.bestRoutesForRouter)"` |
| Custom routes | `gcloud compute routes list --filter="network:<network>"` |
| Describe route | `gcloud compute routes describe <route-name>` |

### Routing Notes

- Cloud Router `get-status` returns learned routes, advertised routes, and BGP peer state. This single command provides the most comprehensive routing view.
- Routes with `nextHopIp` pointing to a stopped VM create silent packet drops (analogous to AWS black-hole routes).
- GCP uses a route priority system (0–65535, default 1000) for custom routes. Lower number = higher preference.
- VPC Network routing mode (regional vs global) determines whether Cloud Router learned routes propagate across regions.

## Step 6: Resource Optimization

| Function | Command |
|----------|---------|
| Unused static external IPs | `gcloud compute addresses list --filter="status=RESERVED"` |
| All external IPs | `gcloud compute addresses list --filter="addressType=EXTERNAL"` |
| Internal IPs | `gcloud compute addresses list --filter="addressType=INTERNAL"` |
| Disabled firewall rules | `gcloud compute firewall-rules list --filter="disabled=true"` |
| VMs with external IPs | `gcloud compute instances list --filter="networkInterfaces[].accessConfigs[].natIP:*"` |
| Forwarding rules | `gcloud compute forwarding-rules list` |

## Identity and Access Verification

| Function | Command |
|----------|---------|
| Current authenticated account | `gcloud auth list` |
| Active project | `gcloud config get-value project` |
| Active account details | `gcloud auth list --filter="status:ACTIVE" --format="value(account)"` |
| Test IAM permissions | `gcloud projects get-iam-policy <project-id>` |
| Organization ID | `gcloud organizations list` |
