# AWS Secrets Manager Terraform Module

A standalone Terraform module for managing AWS Secrets Manager secrets for the Chiang Mai Travel Website.

## Features

- Create and manage secrets in AWS Secrets Manager
- Optional automatic secret rotation
- IAM policy and role for secure secret access
- EC2 instance profile for EC2 instances
- CloudWatch monitoring and alerts
- SNS notifications for security events

## Current Secrets

This module is designed to manage the following secrets for the travel website:

| Secret Name | Description |
|-------------|-------------|
| `contact/config` | Contact form email configuration (recipient, sender, API URL) |
| `api/keys` | Third-party API keys (Google Maps, reCAPTCHA, etc.) |

## Usage

```hcl
module "secrets" {
  source = "./modules/secrets-manager"

  environment = var.environment
  tags        = var.tags

  secrets = {
    # Contact Form Configuration
    "contact/config" = {
      value = jsonencode({
        recipient_email = var.contact_recipient_email
        sender_email    = var.contact_sender_email
        api_url         = var.contact_api_url
      })
      description   = "Contact form email configuration"
      rotation_days = 90
    }

    # API Keys
    "api/keys" = {
      value = jsonencode({
        google_maps_key = var.google_maps_api_key
        recaptcha_key   = var.recaptcha_site_key
        recaptcha_secret = var.recaptcha_secret_key
      })
      description   = "Third-party API keys"
      rotation_days = 180
    }
  }

  alert_email       = var.alert_email
  enable_monitoring = true
}

Inputs
Name	Description	Type	Default	Required
secrets	Map of secrets to create in AWS Secrets Manager	object	{}	yes
environment	Environment name (dev, staging, prod)	string	"dev"	no
tags	Tags to apply to all resources	map(string)	{}	no
recovery_window_days	Days to retain secrets after deletion (7-30)	number	30	no
kms_key_id	KMS key ID for encryption	string	null	no
create_iam_policy	Create IAM policy for secret access	bool	true	no
create_iam_role	Create IAM role for secret access	bool	true	no
create_instance_profile	Create EC2 instance profile	bool	true	no
allowed_services	AWS services allowed to assume the IAM role	list(string)	["ec2", "lambda", "ecs"]	no
rotation_lambda_arn	ARN of Lambda function for rotation	string	null	no
enable_monitoring	Enable CloudWatch alarms	bool	false	no
alarm_threshold	Threshold for CloudWatch alarm	number	10	no
alarm_actions	Actions when alarm triggers	list(string)	[]	no
create_sns_topic	Create SNS topic for alerts	bool	false	no
alert_email	Email for alert notifications	string	""	no
Outputs
Name	Description
secret_ids	Map of secret names to their ARNs
secret_names	List of secret names
secret_arns	List of all secret ARNs
secrets_policy_arn	ARN of the IAM policy
secrets_role_arn	ARN of the IAM role
secrets_role_name	Name of the IAM role
secrets_instance_profile	EC2 instance profile name
sns_topic_arn	ARN of the SNS topic
module_info	Module information (environment, count, monitoring status)
Example with Contact Form
hcl
module "secrets" {
  source = "./modules/secrets-manager"

  environment = "prod"
  tags = {
    Project   = "chiang-mai-travel"
    ManagedBy = "Terraform"
  }

  secrets = {
    "contact/config" = {
      value = jsonencode({
        recipient_email = "admin@yourvilla.com"
        sender_email    = "noreply@yourvilla.com"
        api_url         = "https://api.yourvilla.com/contact"
      })
      description   = "Contact form configuration"
      rotation_days = 90
    }

    "api/keys" = {
      value = jsonencode({
        google_maps_key = "your-google-maps-key"
        recaptcha_key   = "your-recaptcha-key"
      })
      description   = "API keys for the website"
      rotation_days = 180
    }
  }

  create_iam_role   = true
  enable_monitoring = true
  alert_email       = "admin@yourvilla.com"
  create_sns_topic  = true
}
Adding New Secrets
To add a new secret, simply add it to the secrets map:

hcl
secrets = {
  # Existing secrets...
  "new/secret" = {
    value = jsonencode({
      key1 = "value1"
      key2 = "value2"
    })
    description   = "Description of the new secret"
    rotation_days = 30
  }
}
Accessing Secrets from AWS Lambda
python
import boto3
import json

def lambda_handler(event, context):
    client = boto3.client('secretsmanager')

    response = client.get_secret_value(
        SecretId='contact/config'
    )

    config = json.loads(response['SecretString'])
    recipient = config['value']['recipient_email']

    # Use the secret...
Accessing Secrets from Go
go
package main

import (
    "encoding/json"
    "log"

    "github.com/aws/aws-sdk-go-v2/config"
    "github.com/aws/aws-sdk-go-v2/service/secretsmanager"
)

func getSecret(secretName string) (map[string]string, error) {
    cfg, err := config.LoadDefaultConfig(context.Background())
    if err != nil {
        return nil, err
    }

    client := secretsmanager.NewFromConfig(cfg)

    input := &secretsmanager.GetSecretValueInput{
        SecretId: aws.String(secretName),
    }

    result, err := client.GetSecretValue(context.Background(), input)
    if err != nil {
        return nil, err
    }

    var secret map[string]string
    err = json.Unmarshal([]byte(*result.SecretString), &secret)
    return secret, err
}
Requirements
Terraform >= 1.0

AWS Provider >= 5.0

AWS account with permissions to create Secrets Manager resources

Development
bash
# Clone the repository
git clone https://github.com/your-org/terraform-aws-secrets-manager.git

# Run terraform validate
terraform validate

# Run terraform fmt
terraform fmt -recursive

# Test the module
cd examples/complete
terraform init
terraform plan
text
