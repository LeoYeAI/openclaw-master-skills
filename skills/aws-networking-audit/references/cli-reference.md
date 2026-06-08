# AWS CLI Reference — VPC Networking Audit Commands

Read-only AWS CLI commands organized by audit step for VPC networking
assessment. All commands are non-modifying (`describe`, `get`, `list`,
`search`, `filter`). No command creates, modifies, or deletes resources.

Access method: AWS CLI v2 with configured credentials. Commands assume
`--region <region>` is set via environment variable or appended to each
command. Output format defaults to JSON; append `--output table` for
human-readable output during interactive audits.

## Step 1: VPC Inventory and Design

| Function | Command |
|----------|---------|
| List all VPCs in region | `aws ec2 describe-vpcs` |
| Single VPC details | `aws ec2 describe-vpcs --vpc-ids <vpc-id>` |
| VPC CIDR associations | `aws ec2 describe-vpcs --query "Vpcs[].CidrBlockAssociationSet"` |
| All subnets in VPC | `aws ec2 describe-subnets --filters "Name=vpc-id,Values=<vpc-id>"` |
| Subnets by AZ | `aws ec2 describe-subnets --filters "Name=vpc-id,Values=<vpc-id>" --query "Subnets[].{ID:SubnetId,AZ:AvailabilityZone,CIDR:CidrBlock}"` |
| Internet Gateways | `aws ec2 describe-internet-gateways --filters "Name=attachment.vpc-id,Values=<vpc-id>"` |
| NAT Gateways | `aws ec2 describe-nat-gateways --filter "Name=vpc-id,Values=<vpc-id>"` |
| VPC attributes (DNS) | `aws ec2 describe-vpc-attribute --vpc-id <vpc-id> --attribute enableDnsSupport` |
| VPC DNS hostnames | `aws ec2 describe-vpc-attribute --vpc-id <vpc-id> --attribute enableDnsHostnames` |

## Step 2: Security Groups and NACLs

| Function | Command |
|----------|---------|
| All Security Groups in VPC | `aws ec2 describe-security-groups --filters "Name=vpc-id,Values=<vpc-id>"` |
| Single Security Group rules | `aws ec2 describe-security-groups --group-ids <sg-id>` |
| SGs with 0.0.0.0/0 inbound | `aws ec2 describe-security-groups --filters "Name=vpc-id,Values=<vpc-id>" "Name=ip-permission.cidr,Values=0.0.0.0/0"` |
| Default Security Group | `aws ec2 describe-security-groups --filters "Name=vpc-id,Values=<vpc-id>" "Name=group-name,Values=default"` |
| All NACLs in VPC | `aws ec2 describe-network-acls --filters "Name=vpc-id,Values=<vpc-id>"` |
| NACL entries (rules) | `aws ec2 describe-network-acls --query "NetworkAcls[].Entries"` |
| NACL-to-subnet associations | `aws ec2 describe-network-acls --query "NetworkAcls[].Associations"` |

### Security Group Cross-Reference

| Function | Command |
|----------|---------|
| ENIs using a specific SG | `aws ec2 describe-network-interfaces --filters "Name=group-id,Values=<sg-id>"` |
| SGs used by an ENI | `aws ec2 describe-network-interfaces --network-interface-ids <eni-id> --query "NetworkInterfaces[].Groups"` |
| ENIs in a subnet | `aws ec2 describe-network-interfaces --filters "Name=subnet-id,Values=<subnet-id>"` |

## Step 3: Transit Gateway and Connectivity

| Function | Command |
|----------|---------|
| All Transit Gateways | `aws ec2 describe-transit-gateways` |
| TGW attachments | `aws ec2 describe-transit-gateway-attachments --filters "Name=transit-gateway-id,Values=<tgw-id>"` |
| TGW VPC attachments | `aws ec2 describe-transit-gateway-vpc-attachments` |
| TGW route tables | `aws ec2 describe-transit-gateway-route-tables --transit-gateway-id <tgw-id>` |
| Search TGW routes | `aws ec2 search-transit-gateway-routes --transit-gateway-route-table-id <rt-id> --filters "Name=state,Values=active"` |
| TGW route propagations | `aws ec2 get-transit-gateway-route-table-propagations --transit-gateway-route-table-id <rt-id>` |
| TGW route associations | `aws ec2 get-transit-gateway-route-table-associations --transit-gateway-route-table-id <rt-id>` |
| VPC peering connections | `aws ec2 describe-vpc-peering-connections --filters "Name=status-code,Values=active"` |
| VPC endpoints | `aws ec2 describe-vpc-endpoints --filters "Name=vpc-id,Values=<vpc-id>"` |
| VPC endpoint services | `aws ec2 describe-vpc-endpoint-services` |
| Prefix lists (for endpoints) | `aws ec2 describe-managed-prefix-lists` |

## Step 4: VPC Flow Logs

| Function | Command |
|----------|---------|
| Flow Logs for VPC | `aws ec2 describe-flow-logs --filter "Name=resource-id,Values=<vpc-id>"` |
| All Flow Logs in region | `aws ec2 describe-flow-logs` |
| Flow Log log groups | `aws logs describe-log-groups --log-group-name-prefix <prefix>` |
| Query reject events | `aws logs filter-log-events --log-group-name <group> --filter-pattern "REJECT"` |
| Query specific source IP | `aws logs filter-log-events --log-group-name <group> --filter-pattern "<source-ip> REJECT"` |
| Flow Log log streams | `aws logs describe-log-streams --log-group-name <group> --order-by LastEventTime --descending` |

### Flow Log Notes

- CloudWatch Logs queries are bounded by `--start-time` and `--end-time` (epoch ms). Always scope queries to avoid scanning the entire log group.
- For S3-based Flow Logs, use Athena queries instead of `aws logs` commands. The S3 path structure is `{bucket}/{prefix}/AWSLogs/{account-id}/vpcflowlogs/{region}/{year}/{month}/{day}/`.
- Flow Log v2 (default) records: version, account-id, interface-id, srcaddr, dstaddr, srcport, dstport, protocol, packets, bytes, start, end, action, log-status.

## Step 5: Route Tables

| Function | Command |
|----------|---------|
| All Route Tables in VPC | `aws ec2 describe-route-tables --filters "Name=vpc-id,Values=<vpc-id>"` |
| Main Route Table | `aws ec2 describe-route-tables --filters "Name=vpc-id,Values=<vpc-id>" "Name=association.main,Values=true"` |
| Route Table associations | `aws ec2 describe-route-tables --query "RouteTables[].Associations"` |
| Routes in a table | `aws ec2 describe-route-tables --route-table-ids <rtb-id> --query "RouteTables[].Routes"` |

### Route Table Notes

- Routes with `State: blackhole` indicate deleted target resources. These routes silently drop matching traffic.
- The local route (VPC CIDR → local) cannot be removed and handles intra-VPC routing.
- Longest prefix match determines route selection — a /24 route takes precedence over a /16 for matching traffic.

## Step 6: Resource Optimization

| Function | Command |
|----------|---------|
| Unused ENIs (available status) | `aws ec2 describe-network-interfaces --filters "Name=vpc-id,Values=<vpc-id>" "Name=status,Values=available"` |
| All Elastic IPs | `aws ec2 describe-addresses --filters "Name=domain,Values=vpc"` |
| Unattached EIPs | `aws ec2 describe-addresses --query "Addresses[?AssociationId==null]"` |
| NAT Gateway status | `aws ec2 describe-nat-gateways --filter "Name=vpc-id,Values=<vpc-id>" --query "NatGateways[].{ID:NatGatewayId,State:State,AZ:SubnetId}"` |

## Identity and Access Verification

| Function | Command |
|----------|---------|
| Current caller identity | `aws sts get-caller-identity` |
| List attached IAM policies | `aws iam list-attached-user-policies --user-name <user>` |
| Simulate IAM permissions | `aws iam simulate-principal-policy --policy-source-arn <arn> --action-names ec2:DescribeVpcs ec2:DescribeSecurityGroups` |
