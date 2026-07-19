# ============================================
# Outputs for Secrets Manager Module
# ============================================

output "secret_ids" {
  description = "Map of secret names to their ARNs"
  value = {
    for k, v in aws_secretsmanager_secret.secrets : k => v.arn
  }
  sensitive = true
}

output "secret_names" {
  description = "List of secret names"
  value       = [for k, v in aws_secretsmanager_secret.secrets : k]
}

output "secret_arns" {
  description = "List of all secret ARNs"
  value       = [for k, v in aws_secretsmanager_secret.secrets : v.arn]
}

output "secrets_policy_arn" {
  description = "ARN of the IAM policy for reading secrets"
  value       = var.create_iam_policy ? aws_iam_policy.secrets_reader[0].arn : null
}

output "secrets_role_arn" {
  description = "ARN of the IAM role for reading secrets"
  value       = var.create_iam_role ? aws_iam_role.secrets_reader_role[0].arn : null
}

output "secrets_role_name" {
  description = "Name of the IAM role for reading secrets"
  value       = var.create_iam_role ? aws_iam_role.secrets_reader_role[0].name : null
}

output "secrets_instance_profile" {
  description = "Instance profile name for EC2"
  value       = var.create_iam_role && var.create_instance_profile ? aws_iam_instance_profile.secrets_reader_profile[0].name : null
}

output "sns_topic_arn" {
  description = "ARN of the SNS topic for alerts"
  value       = var.create_sns_topic ? aws_sns_topic.secrets_alerts[0].arn : null
}

output "module_info" {
  description = "Information about the secrets manager module"
  value = {
    environment        = var.environment
    secret_count       = length(aws_secretsmanager_secret.secrets)
    iam_role_arn       = var.create_iam_role ? aws_iam_role.secrets_reader_role[0].arn : null
    monitoring_enabled = var.enable_monitoring
    rotation_enabled   = length(aws_secretsmanager_secret_rotation.rotation) > 0
    sns_topic_created  = var.create_sns_topic
  }
}
