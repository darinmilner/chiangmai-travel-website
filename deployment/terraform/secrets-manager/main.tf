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

# ============================================
# IAM Policy for Reading Secrets
# ============================================

resource "aws_iam_policy" "secrets_reader" {
  count = var.create_iam_policy ? 1 : 0

  name        = "${var.environment}-secrets-reader-policy"
  description = "Policy to read secrets from AWS Secrets Manager"
  path        = var.iam_policy_path

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue",
          "secretsmanager:DescribeSecret",
          "secretsmanager:ListSecretVersionIds",
          "secretsmanager:GetResourcePolicy",
          "secretsmanager:GetSecretRotationPolicy"
        ]
        Resource = [
          for secret in aws_secretsmanager_secret.secrets : secret.arn
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetRandomPassword"
        ]
        Resource = ["*"]
      }
    ]
  })

  tags = var.tags
}

# ============================================
# IAM Role for Secret Access
# ============================================

resource "aws_iam_role" "secrets_reader_role" {
  count = var.create_iam_role ? 1 : 0

  name = "${var.environment}-secrets-reader-role"
  path = var.iam_role_path

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = var.allowed_services
        }
      }
    ]
  })

  tags = var.tags
}

# Attach the secrets reader policy to the role
resource "aws_iam_role_policy_attachment" "secrets_reader_attachment" {
  count = var.create_iam_role && var.create_iam_policy ? 1 : 0

  role       = aws_iam_role.secrets_reader_role[0].name
  policy_arn = aws_iam_policy.secrets_reader[0].arn
}

# Create instance profile for EC2
resource "aws_iam_instance_profile" "secrets_reader_profile" {
  count = var.create_iam_role && var.create_instance_profile ? 1 : 0

  name = "${var.environment}-secrets-reader-profile"
  role = aws_iam_role.secrets_reader_role[0].name

  tags = var.tags
}

# ============================================
# Secret Rotation (Optional)
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
# CloudWatch Monitoring
# ============================================

resource "aws_cloudwatch_metric_alarm" "secret_access_alarm" {
  count = var.enable_monitoring ? length(aws_secretsmanager_secret.secrets) : 0

  alarm_name          = "${var.environment}-secret-access-${values(aws_secretsmanager_secret.secrets)[count.index].name}"
  comparison_operator = var.alarm_comparison_operator
  evaluation_periods  = var.alarm_evaluation_periods
  metric_name         = "GetSecretValue"
  namespace           = "AWS/SecretsManager"
  period              = var.alarm_period
  statistic           = "Sum"
  threshold           = var.alarm_threshold
  alarm_description   = "Secret access alarm for ${values(aws_secretsmanager_secret.secrets)[count.index].name}"
  treat_missing_data  = "notBreaching"

  dimensions = {
    SecretName = values(aws_secretsmanager_secret.secrets)[count.index].name
  }

  alarm_actions             = var.alarm_actions
  ok_actions                = var.ok_actions
  insufficient_data_actions = var.insufficient_data_actions

  tags = var.tags
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
