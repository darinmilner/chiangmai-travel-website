# ============================================
# AWS Secrets Manager Module
# Standalone module for managing secrets
# ============================================

# Create secrets in AWS Secrets Manager
resource "aws_secretsmanager_secret" "secrets" {
  for_each = var.secrets

  name                    = each.key
  description             = lookup(each.value, "description", "Secret for ${each.key}")
  recovery_window_in_days = var.recovery_window_days
  kms_key_id              = var.kms_key_id

  # Enable automatic rotation if specified
  dynamic "rotation_rules" {
    for_each = lookup(each.value, "rotation_days", 0) > 0 ? [1] : []
    content {
      automatically_after_days = lookup(each.value, "rotation_days", 0)
      schedule_expression      = lookup(each.value, "schedule_expression", null)
    }
  }

  tags = merge(var.tags, {
    Name        = each.key
    Environment = var.environment
    ManagedBy   = "Terraform"
    Module      = "secrets-manager"
  })

  lifecycle {
    ignore_changes = [
      tags["LastUpdated"],
    ]
  }
}

# Store secret values
resource "aws_secretsmanager_secret_version" "secret_values" {
  for_each = var.secrets

  secret_id = aws_secretsmanager_secret.secrets[each.key].id

  # Convert the secret value to JSON string
  secret_string = jsonencode({
    value       = each.value.value
    created_at  = timestamp()
    environment = var.environment
  })

  lifecycle {
    ignore_changes = [
      secret_string,
    ]
  }
}

# In your secrets manager module
resource "aws_secretsmanager_secret" "lambda_config" {
  name        = "${local.app_name}-lambda-config"
  description = "Configuration for villa image processor lambda"
}

resource "aws_secretsmanager_secret_version" "lambda_config" {
  secret_id = aws_secretsmanager_secret.lambda_config.id
  secret_string = jsonencode({
    CLOUDFRONT_URL    = module.image_cdn.cloudfront_url
    CLOUDFRONT_DOMAIN = module.image_cdn.cloudfront_domain
    S3_BUCKET         = aws_s3_bucket.images.id
    REGION            = data.aws_region.current.name
    # Other config
    MAX_IMAGE_SIZE     = 10485760 # 10MB
    ALLOWED_EXTENSIONS = "jpg,jpeg,png,webp,gif"
  })
}

# ============================================
# Secret Rotation
# ============================================

resource "aws_secretsmanager_secret_rotation" "rotation" {
  for_each = {
    for k, v in var.secrets : k => v
    if lookup(v, "rotation_days", 0) > 0 && var.rotation_lambda_arn != null
  }

  secret_id = aws_secretsmanager_secret.secrets[each.key].id

  rotation_lambda_arn = var.rotation_lambda_arn

  rotation_rules {
    automatically_after_days = lookup(each.value, "rotation_days", 0)
    schedule_expression      = lookup(each.value, "schedule_expression", null)
  }
}

# ============================================
# SNS Topic for Alerts (Optional)
# ============================================

resource "aws_sns_topic" "secrets_alerts" {
  count = var.create_sns_topic ? 1 : 0

  name = "${var.environment}-secrets-alerts"

  tags = var.tags
}

resource "aws_sns_topic_subscription" "email_alerts" {
  count = var.create_sns_topic && var.alert_email != "" ? 1 : 0

  topic_arn = aws_sns_topic.secrets_alerts[0].arn
  protocol  = "email"
  endpoint  = var.alert_email
}
