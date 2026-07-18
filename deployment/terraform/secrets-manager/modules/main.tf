# ============================================
# AWS Secrets Manager Module
# For Golang Travel Website Application
# ============================================

# Create secrets in AWS Secrets Manager
resource "aws_secretsmanager_secret" "secrets" {
  for_each = var.secrets

  name        = each.key
  description = lookup(each.value, "description", "Secret for ${each.key}")

  # Enable automatic rotation if specified
  rotation_rules {
    automatically_after_days = lookup(each.value, "rotation_days", 0)
  }

  # Tags for identification
  tags = merge(var.tags, {
    Name        = each.key
    Environment = var.environment
    ManagedBy   = "Terraform"
    Service     = "SecretsManager"
  })

  # Recovery window in days
  recovery_window_in_days = var.recovery_window_days

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

# Create IAM policy for reading secrets
resource "aws_iam_policy" "secrets_reader" {
  name        = "${var.environment}-secrets-reader-policy"
  description = "Policy to read secrets from AWS Secrets Manager"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue",
          "secretsmanager:DescribeSecret",
          "secretsmanager:ListSecretVersionIds"
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

# Create IAM role for EC2/Lambda to read secrets
resource "aws_iam_role" "secrets_reader_role" {
  count = var.create_iam_role ? 1 : 0

  name = "${var.environment}-secrets-reader-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = [
            "ec2.amazonaws.com",
            "lambda.amazonaws.com",
            "ecs-tasks.amazonaws.com"
          ]
        }
      }
    ]
  })

  tags = var.tags
}

# Attach the secrets reader policy to the role
resource "aws_iam_role_policy_attachment" "secrets_reader_attachment" {
  count = var.create_iam_role ? 1 : 0

  role       = aws_iam_role.secrets_reader_role[0].name
  policy_arn = aws_iam_policy.secrets_reader.arn
}

# Create instance profile for EC2
resource "aws_iam_instance_profile" "secrets_reader_profile" {
  count = var.create_iam_role ? 1 : 0

  name = "${var.environment}-secrets-reader-profile"
  role = aws_iam_role.secrets_reader_role[0].name
}

# Enable automatic rotation for secrets (if specified)
resource "aws_secretsmanager_secret_rotation" "rotation" {
  for_each = {
    for k, v in var.secrets : k => v
    if lookup(v, "rotation_days", 0) > 0
  }

  secret_id = aws_secretsmanager_secret.secrets[each.key].id

  rotation_lambda_arn = var.rotation_lambda_arn

  rotation_rules {
    automatically_after_days = lookup(each.value, "rotation_days", 0)
  }
}

# CloudWatch alarms for secret access monitoring
resource "aws_cloudwatch_metric_alarm" "secret_access_alarm" {
  count = var.enable_monitoring ? length(aws_secretsmanager_secret.secrets) : 0

  alarm_name          = "${var.environment}-secret-access-${values(aws_secretsmanager_secret.secrets)[count.index].name}"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "GetSecretValue"
  namespace           = "AWS/SecretsManager"
  period              = 300
  statistic           = "Sum"
  threshold           = var.alarm_threshold
  alarm_description   = "This metric monitors secret access for ${values(aws_secretsmanager_secret.secrets)[count.index].name}"
  treat_missing_data  = "notBreaching"

  dimensions = {
    SecretName = values(aws_secretsmanager_secret.secrets)[count.index].name
  }

  alarm_actions = var.alarm_actions
  ok_actions    = var.ok_actions
}
