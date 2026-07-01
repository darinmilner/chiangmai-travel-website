# 🌐 AWS VPC Module

A production-ready Terraform module for deploying a highly available AWS VPC with public and private subnets, NAT gateways, Application Load Balancer (ALB), and EC2 security groups following AWS Well-Architected Framework best practices.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Features](#features)
- [Folder Structure](#folder-structure)
- [Usage](#usage)
- [Module Design: Best Practices](#module-design-best-practices)
- [Security Groups](#security-groups)
- [Variables](#variables)
- [Outputs](#outputs)
- [Interview Talking Points](#interview-talking-points)
- [License](#license)

---

## 🎯 Overview

This Terraform module provisions a complete VPC environment on AWS, designed for web applications like a travel blog. It follows **production-grade best practices** including:

- **High Availability**: Multi-AZ deployment across 2+ Availability Zones
- **Defense in Depth**: Public and private subnets with NAT gateways
- **Security**: ALB + EC2 security groups with least privilege
- **Observability**: VPC Flow Logs with CloudWatch integration
- **Maintainability**: DRY code with locals, variables, and consistent tagging

---

## 🏗️ Architecture
┌─────────────────────────────────────────────────────────────────────────────┐
│ AWS VPC (10.0.0.0/16) │
├─────────────────────────────────────────────────────────────────────────────┤
│ │
│ ┌─────────────────────────────┐ ┌─────────────────────────────────┐ │
│ │ Availability Zone A │ │ Availability Zone B │ │
│ │ ┌───────────────────────┐ │ │ ┌─────────────────────────┐ │ │
│ │ │ Public Subnet A │ │ │ │ Public Subnet B │ │ │
│ │ │ ┌─────────────────┐ │ │ │ │ ┌─────────────────┐ │ │ │
│ │ │ │ NAT Gateway │ │ │ │ │ │ NAT Gateway │ │ │ │
│ │ │ └─────────────────┘ │ │ │ │ └─────────────────┘ │ │ │
│ │ │ ┌─────────────────┐ │ │ │ │ ┌─────────────────┐ │ │ │
│ │ │ │ ALB (Public) │──┼──│────│──┼──│ ALB (Public) │ │ │ │
│ │ │ └─────────────────┘ │ │ │ │ └─────────────────┘ │ │ │
│ │ └───────────────────────┘ │ │ └─────────────────────────┘ │ │
│ │ ┌───────────────────────┐ │ │ ┌─────────────────────────┐ │ │
│ │ │ Private Subnet A │ │ │ │ Private Subnet B │ │ │
│ │ │ ┌─────────────────┐ │ │ │ │ ┌─────────────────┐ │ │ │
│ │ │ │ EC2 App Server │ │ │ │ │ │ EC2 App Server │ │ │ │
│ │ │ └─────────────────┘ │ │ │ │ └─────────────────┘ │ │ │
│ │ └───────────────────────┘ │ │ └─────────────────────────┘ │ │
│ └─────────────────────────────┘ └─────────────────────────────────┘ │
│ │
│ ┌─────────────────────────────────────────────────────────────────────┐ │
│ │ VPC Flow Logs → CloudWatch Logs │ │
│ └─────────────────────────────────────────────────────────────────────┘ │
│ │
└─────────────────────────────────────────────────────────────────────────────┘

---

## ✨ Features

| Feature | Description |
| :--- | :--- |
| **Multi-AZ VPC** | Deployed across 2+ Availability Zones for high availability |
| **Public Subnets** | For ALB, NAT Gateways, and Bastion hosts |
| **Private Subnets** | For EC2 app servers, databases, and internal services |
| **NAT Gateways** | One per AZ for highly available outbound internet access |
| **Internet Gateway** | For public subnet internet access |
| **ALB Security Group** | Allows HTTP/HTTPS from the internet |
| **EC2 Security Group** | Allows traffic **only** from the ALB (least privilege) |
| **VPC Flow Logs** | Enables network traffic monitoring and troubleshooting |
| **Consistent Tagging** | All resources tagged for easy identification and cost tracking |

---

## 📁 Folder Structure
terraform-aws-vpc/
├── main.tf # VPC, subnets, route tables, gateways
├── security_group.tf # ALB, EC2, and Lambda security groups
├── variables.tf # Input variables with descriptions
├── outputs.tf # Outputs for use in other modules
├── locals.tf # Local values (ports, CIDRs, etc.)
├── terraform.tfvars.example # Example variable values
├── README.md # This file
└── .terraform-version # Terraform version constraint


---

## 🚀 Usage

### Prerequisites

- Terraform >= 1.5.0
- AWS Provider >= 5.0.0
- AWS CLI configured with appropriate credentials

### Quick Start

```hcl
# main.tf
module "vpc" {
  source = "./modules/vpc"

  project_name        = "travel-blog"
  environment         = "prod"
  short_region        = "use1"
  vpc_cidr            = "10.0.0.0/16"
  public_subnet_count = 2
  private_subnet_count = 2
  ssh_allowed_cidrs   = ["203.0.113.0/24"]  # Your IP only!

  common_tags = {
    Environment = "prod"
    Project     = "travel-blog"
    Terraform   = "true"
  }
}

Run Terraform
bash
terraform init
terraform plan
terraform apply
🧠 Module Design: Best Practices
This module was built with production readiness and maintainability in mind. Here are the key design decisions:

1. DRY (Don't Repeat Yourself) with Locals
hcl
locals {
  all_routes_open   = "0.0.0.0/0"
  http_port         = 80
  https_port        = 443
  ssh_port          = 22
  health_check_port = 8080
}
Why this matters: Instead of hardcoding ports like 443 multiple times, we define them once. If we need to change a port, we update it in one place—reducing errors and making the code more maintainable.

2. Variables with Descriptions and Validation
hcl
variable "vpc_cidr" {
  description = "CIDR block for the VPC"
  type        = string
  default     = "10.0.0.0/16"

  validation {
    condition     = can(cidrnetmask(var.vpc_cidr))
    error_message = "Must be a valid CIDR block."
  }
}
Why this matters: Variables with descriptions serve as self-documenting code. Validation blocks catch errors early (during plan), preventing deployment failures.

3. Consistent Tagging with merge()
hcl
tags = merge(var.common_tags, {
  Name = "${var.project_name}-vpc"
})
Why this matters: All resources inherit a common set of tags (Environment, Project, Terraform), making it easy to track costs, identify resources, and manage permissions via tag-based policies.

4. Dynamic Subnet Creation with for_each and cidrsubnet
hcl
resource "aws_subnet" "public" {
  for_each = { for i in range(var.public_subnet_count) : "public${i}" => i }

  vpc_id            = aws_vpc.main.id
  cidr_block        = cidrsubnet(var.vpc_cidr, 8, each.value)
  availability_zone = data.aws_availability_zones.available.names[each.value % length(local.azs)]
}
Why this matters: This pattern automatically calculates subnet CIDRs based on the VPC CIDR and distributes subnets across availability zones. Adding more subnets is as simple as changing a variable.

5. Modern Security Group Resources
hcl
resource "aws_vpc_security_group_ingress_rule" "ec2_ingress_http_from_alb" {
  security_group_id           = aws_security_group.ec2_sg.id
  referenced_security_group_id = aws_security_group.alb_sg.id
  from_port                   = local.http_port
  to_port                     = local.http_port
  ip_protocol                 = "tcp"
}
Why this matters: Using aws_vpc_security_group_ingress_rule (the modern AWS provider resource) instead of inline ingress blocks prevents rule conflicts, supports full tagging, and gives better state management than the older aws_security_group_rule resource.

6. Least Privilege Security
Security Group	Inbound Source	Purpose
ALB SG	0.0.0.0/0	Allow internet traffic to ALB
EC2 SG	ALB Security Group ID	Allow traffic only from ALB (not the internet!)
EC2 SG	Your IP (via variable)	Allow SSH for debugging (restricted!)
Why this matters: EC2 instances can only be reached via the ALB—the internet cannot bypass the load balancer. This is a critical security best practice for web applications.

7. VPC Flow Logs for Observability
hcl
resource "aws_flow_log" "vpc" {
  count = var.enable_flow_logs ? 1 : 0

  iam_role_arn    = aws_iam_role.flow_log[0].arn
  log_destination = aws_cloudwatch_log_group.flow_log[0].arn
  traffic_type    = "ALL"
  vpc_id          = aws_vpc.main.id
}
Why this matters: VPC Flow Logs provide visibility into network traffic, which is essential for troubleshooting connectivity issues and detecting security incidents.

🔒 Security Groups
ALB Security Group
Rule	Source	Port	Description
Ingress	0.0.0.0/0	80	Allow HTTP from anywhere
Ingress	0.0.0.0/0	443	Allow HTTPS from anywhere
Egress	0.0.0.0/0	All	Allow all outbound traffic
EC2 Security Group
Rule	Source	Port	Description
Ingress	ALB SG ID	80	Allow HTTP only from ALB
Ingress	ALB SG ID	8080	Allow health checks from ALB
Ingress	Your IP (variable)	22	Allow SSH for debugging
Egress	0.0.0.0/0	All	Allow all outbound traffic
Lambda Security Group
Rule	Source	Port	Description
Egress	0.0.0.0/0	443	Allow HTTPS outbound to external APIs
📝 Variables
Variable	Description	Type	Default
project_name	Name of the project	string	"travel-blog"
environment	Deployment environment (dev, staging, prod)	string	"dev"
vpc_cidr	CIDR block for the VPC	string	"10.0.0.0/16"
public_subnet_count	Number of public subnets (matches AZs)	number	2
private_subnet_count	Number of private subnets (matches AZs)	number	2
ssh_allowed_cidrs	IPs allowed to SSH into EC2 instances	list(string)	["0.0.0.0/0"]
enable_flow_logs	Enable VPC Flow Logs	bool	true
common_tags	Tags applied to all resources	map(string)	{ Environment = "dev" }
📤 Outputs
Output	Description
vpc_id	ID of the VPC
vpc_cidr	CIDR block of the VPC
public_subnet_ids	IDs of the public subnets
private_subnet_ids	IDs of the private subnets
web_security_group_id	ID of the web (EC2) security group
alb_security_group_id	ID of the ALB security group
nat_gateway_ids	IDs of the NAT gateways
