# CLI Reference — Cloud Security Posture Assessment

Multi-provider CLI commands organized by assessment domain. All commands
are read-only — no state modifications.

## IAM Assessment Commands

### [AWS] IAM CLI

| Command | Purpose |
|---------|---------|
| `aws iam get-account-authorization-details` | Full IAM inventory (users, roles, groups, policies) |
| `aws iam list-policies --scope Local` | Customer-managed policies only |
| `aws iam get-policy-version --policy-arn <arn> --version-id <v>` | Policy document for specific version |
| `aws iam generate-credential-report` | Trigger credential report generation |
| `aws iam get-credential-report` | Download credential report (MFA, key age, last login) |
| `aws iam list-attached-user-policies --user-name <user>` | Policies attached to a specific user |
| `aws iam list-attached-role-policies --role-name <role>` | Policies attached to a specific role |
| `aws iam simulate-principal-policy --policy-source-arn <arn> --action-names <action>` | Test effective permissions |
| `aws organizations list-policies --filter SERVICE_CONTROL_POLICY` | List SCPs |
| `aws organizations describe-policy --policy-id <id>` | SCP document content |

### [Azure] IAM CLI

| Command | Purpose |
|---------|---------|
| `az role assignment list --all` | All RBAC role assignments |
| `az role assignment list --assignee <principal-id>` | Assignments for specific principal |
| `az role definition list --custom-role-only` | Custom role definitions |
| `az ad user list --query "[?userType=='Member']"` | Member users (excludes guests) |
| `az ad app list --all` | Application registrations |
| `az ad sp list --all` | Service principals |
| `az account management-group list` | Management group hierarchy |
| `az policy assignment list` | Azure Policy assignments |

### [GCP] IAM CLI

| Command | Purpose |
|---------|---------|
| `gcloud projects get-iam-policy <project-id>` | IAM bindings for project |
| `gcloud organizations get-iam-policy <org-id>` | Organization-level bindings |
| `gcloud iam roles list --project=<project-id>` | Custom roles |
| `gcloud iam service-accounts list --project=<project-id>` | Service accounts |
| `gcloud iam service-accounts keys list --iam-account=<email>` | Service account keys (check age) |
| `gcloud resource-manager org-policies list --project=<project-id>` | Organization Policy constraints |
| `gcloud asset search-all-iam-policies --scope=projects/<project>` | Asset Inventory IAM search |

## Encryption Audit Commands

### [AWS] KMS and Encryption CLI

| Command | Purpose |
|---------|---------|
| `aws kms list-keys` | All KMS keys in region |
| `aws kms describe-key --key-id <key-id>` | Key metadata (state, origin, manager) |
| `aws kms get-key-rotation-status --key-id <key-id>` | Rotation enabled check |
| `aws kms get-key-policy --key-id <key-id> --policy-name default` | Key resource policy |
| `aws s3api get-bucket-encryption --bucket <bucket>` | S3 bucket encryption config |
| `aws ec2 describe-volumes --query 'Volumes[?!Encrypted]'` | Unencrypted EBS volumes |
| `aws rds describe-db-instances --query 'DBInstances[*].[DBInstanceIdentifier,StorageEncrypted]'` | RDS encryption status |
| `aws acm list-certificates` | ACM certificate inventory |
| `aws acm describe-certificate --certificate-arn <arn>` | Certificate details and expiry |

### [Azure] Key Vault and Encryption CLI

| Command | Purpose |
|---------|---------|
| `az keyvault list` | All Key Vaults |
| `az keyvault show --name <vault>` | Vault configuration and access policies |
| `az keyvault key list --vault-name <vault>` | Keys in vault |
| `az keyvault certificate list --vault-name <vault>` | Certificates in vault |
| `az disk list --query "[].{name:name, encryption:encryption}"` | Disk encryption status |
| `az webapp list --query "[].{name:name, minTlsVersion:siteConfig.minTlsVersion}"` | App Service TLS versions |
| `az sql server list --query "[].{name:name, minTlsVersion:minimalTlsVersion}"` | SQL Server TLS config |

### [GCP] Cloud KMS and Encryption CLI

| Command | Purpose |
|---------|---------|
| `gcloud kms keyrings list --location=<location>` | Key rings in location |
| `gcloud kms keys list --keyring=<ring> --location=<loc>` | Keys in key ring |
| `gcloud kms keys describe <key> --keyring=<ring> --location=<loc>` | Key details (rotation period) |
| `gcloud compute disks list --format="table(name,diskEncryptionKey)"` | Disk encryption config |
| `gcloud compute ssl-policies list` | SSL policy compliance |
| `gcloud compute ssl-policies describe <policy>` | SSL policy details (min TLS version, profile) |
| `gsutil encryption get gs://<bucket>` | Bucket default encryption (CMEK or Google-managed) |

## Public Exposure Detection Commands

### [AWS] Exposure CLI

| Command | Purpose |
|---------|---------|
| `aws s3api get-bucket-policy-status --bucket <bucket>` | Public access check |
| `aws s3api get-public-access-block --bucket <bucket>` | Block public access settings |
| `aws ec2 describe-security-groups --filters "Name=ip-permission.cidr,Values=0.0.0.0/0"` | SGs with public ingress |
| `aws elbv2 describe-load-balancers` | Load balancer inventory |
| `aws elbv2 describe-load-balancer-attributes --load-balancer-arn <arn>` | LB attributes (access logs) |
| `aws ec2 describe-instances --query 'Reservations[*].Instances[?PublicIpAddress!=null]'` | Instances with public IPs |

### [Azure] Exposure CLI

| Command | Purpose |
|---------|---------|
| `az network public-ip list` | All public IPs |
| `az network nsg list` | Network security groups |
| `az network nsg rule list --nsg-name <nsg> --resource-group <rg>` | NSG rules |
| `az storage account list --query "[].{name:name, publicAccess:allowBlobPublicAccess}"` | Storage public access |
| `az network application-gateway waf-config show --gateway-name <gw> --resource-group <rg>` | WAF mode check |

### [GCP] Exposure CLI

| Command | Purpose |
|---------|---------|
| `gcloud compute firewall-rules list --filter="sourceRanges:0.0.0.0/0"` | Public firewall rules |
| `gcloud compute forwarding-rules list --filter="loadBalancingScheme=EXTERNAL"` | External load balancers |
| `gcloud compute instances list --format="table(name,networkInterfaces[0].accessConfigs[0].natIP)"` | Instances with external IPs |
| `gsutil iam get gs://<bucket>` | Bucket IAM (check allUsers/allAuthenticatedUsers) |
| `gcloud compute backend-services list` | Backend service inventory |
