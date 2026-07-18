# ============================================
# Outputs for Secrets Manager Module
# ============================================

output "secret_ids" {
  description = "Map of secret names to their ARNs"
  value = {
    for k, v in aws_secretsmanager_secret.secrets : k => v.arn
  }
}

output "secret_names" {
  description = "List of secret names"
  value       = [for k, v in aws_secretsmanager_secret.secrets : k]
}

output "secrets_policy_arn" {
  description = "ARN of the IAM policy for reading secrets"
  value       = aws_iam_policy.secrets_reader.arn
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
  value       = var.create_iam_role ? aws_iam_instance_profile.secrets_reader_profile[0].name : null
}

output "secret_arns" {
  description = "Map of secret names to their ARNs"
  value       = aws_secretsmanager_secret.secrets
}
