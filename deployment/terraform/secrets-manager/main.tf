# ============================================
# Root Terraform Configuration
# For Chiang Mai Travel Website
# ============================================

terraform {
  required_version = ">= 1.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region

  # For production, use named profiles
  # profile = var.aws_profile
}

# Backend configuration (using S3 for state storage)
terraform {
  backend "s3" {
    bucket         = "chiang-mai-travel-terraform-state"
    key            = "terraform.tfstate"
    region         = "ap-southeast-1"
    encrypt        = true
    dynamodb_table = "terraform-state-lock"
  }
}

# Local variables for common tags
locals {
  common_tags = {
    Project     = "chiang-mai-travel"
    Environment = var.environment
    ManagedBy   = "Terraform"
    Repository  = "chiang-mai-travel-website"
  }
}

# ============================================
# Secrets Manager Module
# ============================================

module "secrets" {
  source = "./modules/secrets-manager"

  environment = var.environment
  tags        = local.common_tags

  # Enable monitoring for production
  enable_monitoring = var.environment == "prod" ? true : false

  # Alarm actions (SNS topics)
  alarm_actions = var.environment == "prod" ? [aws_sns_topic.alerts[0].arn] : []
  ok_actions    = var.environment == "prod" ? [aws_sns_topic.alerts[0].arn] : []

  secrets = {
    # Database secrets
    "db/credentials" = {
      value = jsonencode({
        username = var.db_username
        password = var.db_password
        host     = var.db_host
        port     = var.db_port
        database = var.db_name
      })
      description   = "Database credentials for the travel website"
      rotation_days = 30
    }

    # API Keys
    "api/keys" = {
      value = jsonencode({
        google_maps_key   = var.google_maps_api_key
        stripe_secret_key = var.stripe_secret_key
        sendgrid_api_key  = var.sendgrid_api_key
      })
      description   = "API keys for third-party services"
      rotation_days = 90
    }

    # Email configuration
    "email/config" = {
      value = jsonencode({
        smtp_host     = var.smtp_host
        smtp_port     = var.smtp_port
        smtp_username = var.smtp_username
        smtp_password = var.smtp_password
        from_email    = var.from_email
        admin_email   = var.admin_email
      })
      description   = "Email configuration for the website"
      rotation_days = 90
    }

    # JWT secrets
    "jwt/secrets" = {
      value = jsonencode({
        secret_key     = var.jwt_secret_key
        refresh_key    = var.jwt_refresh_key
        issuer         = "chiang-mai-travel-website"
        expiry_minutes = 1440
      })
      description   = "JWT authentication secrets"
      rotation_days = 180
    }

    # AWS credentials for application
    "aws/credentials" = {
      value = jsonencode({
        access_key_id     = var.aws_access_key_id
        secret_access_key = var.aws_secret_access_key
        region            = var.aws_region
        s3_bucket         = var.s3_bucket_name
      })
      description   = "AWS credentials for the application"
      rotation_days = 90
    }
  }
}

# ============================================
# SNS Topic for Alerts
# ============================================

resource "aws_sns_topic" "alerts" {
  count = var.environment == "prod" ? 1 : 0

  name = "chiang-mai-travel-alerts-${var.environment}"

  tags = local.common_tags
}

# Optional: SNS subscription for email alerts
resource "aws_sns_topic_subscription" "email_alerts" {
  count = var.environment == "prod" && var.admin_email != "" ? 1 : 0

  topic_arn = aws_sns_topic.alerts[0].arn
  protocol  = "email"
  endpoint  = var.admin_email
}

# ============================================
# Outputs
# ============================================

output "secrets_info" {
  description = "Information about the created secrets"
  value = {
    secret_names  = module.secrets.secret_names
    secret_arns   = module.secrets.secret_arns
    iam_role_arn  = module.secrets.secrets_role_arn
    iam_role_name = module.secrets.secrets_role_name
  }
  sensitive = true
}

# ============================================
# Golang Application IAM Policy (Example)
# ============================================

resource "aws_iam_policy" "app_secrets_policy" {
  name = "chiang-mai-travel-app-secrets-${var.environment}"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue",
          "secretsmanager:DescribeSecret"
        ]
        Resource = module.secrets.secret_arns[*].arn
      }
    ]
  })

  tags = local.common_tags
}
