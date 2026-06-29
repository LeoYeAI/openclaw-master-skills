---
name: infra-as-code
description: Define and manage cloud infrastructure with code. Use when writing Terraform, CloudFormation, or Pulumi configs, managing state, planning deployments, setting up networking/compute/storage resources, or debugging infrastructure drift.
metadata: {"clawdbot":{"emoji":"🏗️","requires":{"anyBins":["terraform","aws","pulumi"]},"os":["linux","darwin","win32"]}}
---

# Infrastructure as Code

Define, deploy, and manage cloud infrastructure using declarative configuration. Covers Terraform (multi-cloud), AWS CloudFormation, and Pulumi (code-first), with patterns for compute, networking, storage, databases, and state management.

## When to Use

- Setting up cloud infrastructure (VPCs, EC2, Lambda, S3, RDS, etc.)
- Writing or modifying Terraform configurations
- Managing Terraform state (remote backends, workspaces, imports)
- Creating CloudFormation templates
- Using Pulumi for infrastructure in TypeScript/Python/Go
- Planning and previewing infrastructure changes safely
- Debugging drift between declared state and actual resources
- Setting up multi-environment deployments (dev/staging/prod)

## Terraform

### Quick Start

```bash
# Install: https://developer.hashicorp.com/terraform/install

# Initialize a project
mkdir infra && cd infra
terraform init

# Core workflow
terraform plan        # Preview changes (safe, read-only)
terraform apply       # Apply changes (creates/modifies resources)
terraform destroy     # Tear down all resources

# Format and validate
terraform fmt -recursive    # Auto-format all .tf files
terraform validate          # Check syntax and config validity
```

### Project Structure

```
infra/
  main.tf              # Primary resources
  variables.tf         # Input variable declarations
  outputs.tf           # Output values
  providers.tf         # Provider configuration
  terraform.tfvars     # Variable values (don't commit secrets)
  backend.tf           # Remote state configuration
  modules/
    vpc/
      main.tf
      variables.tf
      outputs.tf
    compute/
      main.tf
      variables.tf
      outputs.tf
```

### Provider Configuration

```hcl
# providers.tf
terraform {
  required_version = ">= 1.5"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = var.project_name
      Environment = var.environment
      ManagedBy   = "terraform"
    }
  }
}
```

### Variables and Outputs

```hcl
# variables.tf
variable "aws_region" {
  type        = string
  default     = "us-east-1"
  description = "AWS region for all resources"
}

variable "environment" {
  type        = string
  description = "Deployment environment"
  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be dev, staging, or prod."
  }
}

variable "instance_type" {
  type    = string
  default = "t3.micro"
}

variable "db_password" {
  type      = string
  sensitive = true
  description = "Database password (pass via TF_VAR_db_password env var)"
}

# outputs.tf
output "vpc_id" {
  value       = aws_vpc.main.id
  description = "VPC ID"
}

output "api_endpoint" {
  value = aws_lb.api.dns_name
}
```

### VPC + Networking

```hcl
# Networking module
resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_support   = true
  enable_dns_hostnames = true

  tags = { Name = "${var.project_name}-vpc" }
}

resource "aws_subnet" "public" {
  count             = 2
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.${count.index + 1}.0/24"
  availability_zone = data.aws_availability_zones.available.names[count.index]

  map_public_ip_on_launch = true
  tags = { Name = "${var.project_name}-public-${count.index + 1}" }
}

resource "aws_subnet" "private" {
  count             = 2
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.${count.index + 10}.0/24"
  availability_zone = data.aws_availability_zones.available.names[count.index]

  tags = { Name = "${var.project_name}-private-${count.index + 1}" }
}

resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id
}

resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }
}

resource "aws_route_table_association" "public" {
  count          = 2
  subnet_id      = aws_subnet.public[count.index].id
  route_table_id = aws_route_table.public.id
}

resource "aws_security_group" "web" {
  name_prefix = "${var.project_name}-web-"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

data "aws_availability_zones" "available" {
  state = "available"
}
```

### Compute (EC2)

```hcl
resource "aws_instance" "app" {
  ami                    = data.aws_ami.ubuntu.id
  instance_type          = var.instance_type
  subnet_id              = aws_subnet.public[0].id
  vpc_security_group_ids = [aws_security_group.web.id]
  key_name               = var.key_pair_name

  user_data = <<-EOF
    #!/bin/bash
    apt-get update
    apt-get install -y docker.io
    systemctl start docker
    docker run -d -p 80:8080 ${var.docker_image}
  EOF

  tags = { Name = "${var.project_name}-app" }
}

data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"] # Canonical

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-*-24.04-amd64-server-*"]
  }
}
```

### S3 + Static Website

```hcl
resource "aws_s3_bucket" "website" {
  bucket = "${var.project_name}-website"
}

resource "aws_s3_bucket_website_configuration" "website" {
  bucket = aws_s3_bucket.website.id

  index_document { suffix = "index.html" }
  error_document { key = "error.html" }
}

resource "aws_s3_bucket_public_access_block" "website" {
  bucket = aws_s3_bucket.website.id

  block_public_acls       = false
  block_public_policy     = false
  ignore_public_acls      = false
  restrict_public_buckets = false
}

resource "aws_s3_bucket_policy" "website" {
  bucket = aws_s3_bucket.website.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Sid       = "PublicRead"
      Effect    = "Allow"
      Principal = "*"
      Action    = "s3:GetObject"
      Resource  = "${aws_s3_bucket.website.arn}/*"
    }]
  })

  depends_on = [aws_s3_bucket_public_access_block.website]
}
```

### RDS Database

```hcl
resource "aws_db_subnet_group" "main" {
  name       = "${var.project_name}-db"
  subnet_ids = aws_subnet.private[*].id
}

resource "aws_security_group" "db" {
  name_prefix = "${var.project_name}-db-"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.web.id]
  }
}

resource "aws_db_instance" "main" {
  identifier        = "${var.project_name}-db"
  engine            = "postgres"
  engine_version    = "16.1"
  instance_class    = "db.t3.micro"
  allocated_storage = 20

  db_name  = var.db_name
  username = var.db_username
  password = var.db_password

  db_subnet_group_name   = aws_db_subnet_group.main.name
  vpc_security_group_ids = [aws_security_group.db.id]

  backup_retention_period = 7
  skip_final_snapshot     = var.environment != "prod"
  deletion_protection     = var.environment == "prod"
}
```

### Lambda Function

```hcl
data "archive_file" "lambda_zip" {
  type        = "zip"
  source_dir  = "${path.module}/lambda"
  output_path = "${path.module}/lambda.zip"
}

resource "aws_lambda_function" "api" {
  function_name    = "${var.project_name}-api"
  filename         = data.archive_file.lambda_zip.output_path
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256
  handler          = "index.handler"
  runtime          = "nodejs20.x"
  timeout          = 30

  role = aws_iam_role.lambda_exec.arn

  environment {
    variables = {
      DB_HOST     = aws_db_instance.main.endpoint
      ENVIRONMENT = var.environment
    }
  }
}

resource "aws_iam_role" "lambda_exec" {
  name = "${var.project_name}-lambda-exec"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = { Service = "lambda.amazonaws.com" }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_basic" {
  role       = aws_iam_role.lambda_exec.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}
```

### State Management

```hcl
# backend.tf - Remote state in S3
terraform {
  backend "s3" {
    bucket         = "my-terraform-state"
    key            = "project/terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "terraform-locks"
    encrypt        = true
  }
}
```

```bash
# State operations
terraform state list                    # List all resources in state
terraform state show aws_instance.app   # Show resource details
terraform state mv aws_instance.app aws_instance.web  # Rename resource
terraform state rm aws_instance.old     # Remove from state (doesn't destroy)

# Import existing resource into Terraform
terraform import aws_instance.app i-1234567890abcdef0

# Workspaces (multiple environments, same config)
terraform workspace new dev
terraform workspace new staging
terraform workspace new prod
terraform workspace select dev
terraform workspace list
```

### Multi-Environment Pattern

```hcl
# Use workspaces + tfvars files
# terraform.tfvars (default)
# env/dev.tfvars
# env/staging.tfvars
# env/prod.tfvars

# Apply for specific environment
# terraform apply -var-file=env/prod.tfvars
```

```bash
# Environment-specific apply
ENV=${1:-dev}
terraform workspace select "$ENV" || terraform workspace new "$ENV"
terraform apply -var-file="env/$ENV.tfvars"
```

## AWS CloudFormation

### Template Structure

```yaml
# cloudformation.yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: My application stack

Parameters:
  Environment:
    Type: String
    AllowedValues: [dev, staging, prod]
    Default: dev
  InstanceType:
    Type: String
    Default: t3.micro

Conditions:
  IsProd: !Equals [!Ref Environment, prod]

Resources:
  VPC:
    Type: AWS::EC2::VPC
    Properties:
      CidrBlock: 10.0.0.0/16
      EnableDnsSupport: true
      EnableDnsHostnames: true
      Tags:
        - Key: Name
          Value: !Sub "${AWS::StackName}-vpc"

  PublicSubnet:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref VPC
      CidrBlock: 10.0.1.0/24
      MapPublicIpOnLaunch: true
      Tags:
        - Key: Name
          Value: !Sub "${AWS::StackName}-public"

  AppInstance:
    Type: AWS::EC2::Instance
    Properties:
      InstanceType: !Ref InstanceType
      SubnetId: !Ref PublicSubnet
      ImageId: !FindInMap [RegionAMI, !Ref "AWS::Region", ubuntu]

  Database:
    Type: AWS::RDS::DBInstance
    Condition: IsProd
    DeletionPolicy: Snapshot
    Properties:
      Engine: postgres
      DBInstanceClass: db.t3.micro
      AllocatedStorage: 20
      MasterUsername: admin
      MasterUserPassword: !Ref DBPassword

Outputs:
  VpcId:
    Value: !Ref VPC
    Export:
      Name: !Sub "${AWS::StackName}-VpcId"
  InstanceIP:
    Value: !GetAtt AppInstance.PublicIp
```

### CloudFormation CLI

```bash
# Validate template
aws cloudformation validate-template --template-body file://cloudformation.yaml

# Create stack
aws cloudformation create-stack \
  --stack-name myapp-dev \
  --template-body file://cloudformation.yaml \
  --parameters ParameterKey=Environment,ParameterValue=dev \
  --capabilities CAPABILITY_IAM

# Update stack
aws cloudformation update-stack \
  --stack-name myapp-dev \
  --template-body file://cloudformation.yaml \
  --parameters ParameterKey=Environment,ParameterValue=dev

# Preview changes (changeset)
aws cloudformation create-change-set \
  --stack-name myapp-dev \
  --change-set-name update-1 \
  --template-body file://cloudformation.yaml

aws cloudformation describe-change-set \
  --stack-name myapp-dev \
  --change-set-name update-1

# Delete stack
aws cloudformation delete-stack --stack-name myapp-dev

# List stacks
aws cloudformation list-stacks --stack-status-filter CREATE_COMPLETE UPDATE_COMPLETE

# Stack events (debugging)
aws cloudformation describe-stack-events --stack-name myapp-dev | head -50
```

## Pulumi (Code-First IaC)

### Quick Start (TypeScript)

```bash
# Install: https://www.pulumi.com/docs/install/
pulumi new aws-typescript

# Core workflow
pulumi preview    # Preview changes
pulumi up         # Apply changes
pulumi destroy    # Tear down
pulumi stack ls   # List stacks
```

### TypeScript Example

```typescript
// index.ts
import * as pulumi from "@pulumi/pulumi";
import * as aws from "@pulumi/aws";

const config = new pulumi.Config();
const environment = config.require("environment");

// VPC
const vpc = new aws.ec2.Vpc("main", {
  cidrBlock: "10.0.0.0/16",
  enableDnsSupport: true,
  enableDnsHostnames: true,
  tags: { Name: `myapp-${environment}-vpc` },
});

// Public subnet
const publicSubnet = new aws.ec2.Subnet("public", {
  vpcId: vpc.id,
  cidrBlock: "10.0.1.0/24",
  mapPublicIpOnLaunch: true,
  tags: { Name: `myapp-${environment}-public` },
});

// S3 bucket
const bucket = new aws.s3.Bucket("data", {
  bucket: `myapp-${environment}-data`,
  versioning: { enabled: true },
});

// Lambda function
const lambdaRole = new aws.iam.Role("lambda-role", {
  assumeRolePolicy: JSON.stringify({
    Version: "2012-10-17",
    Statement: [{
      Action: "sts:AssumeRole",
      Effect: "Allow",
      Principal: { Service: "lambda.amazonaws.com" },
    }],
  }),
});

const lambdaFunc = new aws.lambda.Function("api", {
  runtime: "nodejs20.x",
  handler: "index.handler",
  role: lambdaRole.arn,
  code: new pulumi.asset.FileArchive("./lambda"),
  environment: {
    variables: {
      BUCKET_NAME: bucket.id,
      ENVIRONMENT: environment,
    },
  },
});

// Outputs
export const vpcId = vpc.id;
export const bucketName = bucket.id;
export const lambdaArn = lambdaFunc.arn;
```

### Python Example

```python
# __main__.py
import pulumi
import pulumi_aws as aws

config = pulumi.Config()
environment = config.require("environment")

vpc = aws.ec2.Vpc("main",
    cidr_block="10.0.0.0/16",
    enable_dns_support=True,
    enable_dns_hostnames=True,
    tags={"Name": f"myapp-{environment}-vpc"})

bucket = aws.s3.Bucket("data",
    bucket=f"myapp-{environment}-data",
    versioning=aws.s3.BucketVersioningArgs(enabled=True))

pulumi.export("vpc_id", vpc.id)
pulumi.export("bucket_name", bucket.id)
```

### Pulumi State and Stacks

```bash
# Create per-environment stacks
pulumi stack init dev
pulumi stack init staging
pulumi stack init prod

# Switch stack
pulumi stack select dev

# Set config per stack
pulumi config set environment dev
pulumi config set aws:region us-east-1
pulumi config set --secret dbPassword 'my-secret-pass'

# Stack references (cross-stack)
# In consuming stack:
const infra = new pulumi.StackReference("org/infra/prod");
const vpcId = infra.getOutput("vpcId");
```

## Debugging Infrastructure

### Terraform plan issues

```bash
# Detailed plan output
terraform plan -out=plan.tfplan
terraform show plan.tfplan
terraform show -json plan.tfplan | jq '.resource_changes[] | {address, change: .change.actions}'

# Debug mode
TF_LOG=DEBUG terraform plan 2> debug.log

# Check for drift
terraform plan -refresh-only

# Force refresh state
terraform apply -refresh-only
```

### Common issues

```bash
# Resource stuck in "tainted" state
terraform untaint aws_instance.app

# State locked (another apply running or crashed)
terraform force-unlock LOCK_ID

# Provider version conflict
terraform providers lock    # Generate lock file
terraform init -upgrade     # Upgrade providers

# Circular dependency
# Error: "Cycle" in terraform plan
# Fix: use depends_on explicitly, or break the cycle with data sources
```

### Cost estimation

```bash
# Infracost (estimates monthly cost from Terraform plans)
# Install: https://www.infracost.io/docs/
infracost breakdown --path .
infracost diff --path . --compare-to infracost-base.json
```

## Tips

- Always run `terraform plan` before `apply`. Read the plan output carefully — especially lines showing `destroy` or `replace`.
- Use remote state from day one. Local state files get lost, can't be shared, and have no locking.
- Tag everything. At minimum: Project, Environment, ManagedBy. Tags make cost tracking and cleanup possible.
- Never store secrets in `.tf` files or `terraform.tfvars`. Use environment variables (`TF_VAR_name`), secrets managers, or Vault.
- Use `prevent_destroy` lifecycle rules on stateful resources (databases, S3 buckets with data) to prevent accidental deletion.
- Pin provider versions (`~> 5.0` not `>= 5.0`) to avoid surprise breaking changes.
- For multi-environment setups, prefer workspaces + var files over duplicated configurations.
- CloudFormation change sets are the equivalent of `terraform plan` — always create one before updating a stack.
- Pulumi's advantage is using real programming languages (loops, conditionals, type checking). Use it when Terraform's HCL feels limiting.
