# AWS Secrets Manager Terraform Module

A standalone Terraform module for managing AWS Secrets Manager secrets.

## Features

- Create and manage secrets in AWS Secrets Manager
- Optional automatic secret rotation
- IAM policy and role for secret access
- EC2 instance profile for EC2 instances
- CloudWatch monitoring and alerts
- SNS notifications for security events

## Usage

```hcl
module "secrets" {
  source = "path/to/module"

  environment = "dev"
  tags = {
    Project = "my-project"
  }

  secrets = {
    "app/config" = {
      value = jsonencode({
        database_url = "postgresql://user:pass@host:5432/db"
        api_key      = "your-api-key"
      })
      description   = "Application configuration"
      rotation_days = 90
    }
  }

  alert_email = "admin@example.com"
  enable_monitoring = true
}