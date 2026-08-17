output "role_arn" {
  description = "ARN of the IAM role for GitLab OIDC"
  value       = aws_iam_role.gitlab_oidc.arn
}

output "role_name" {
  description = "Name of the IAM role for GitLab OIDC"
  value       = aws_iam_role.gitlab_oidc.name
}

output "oidc_provider_arn" {
  description = "ARN of the OIDC provider"
  value       = var.create_oidc_provider ? aws_iam_openid_connect_provider.gitlab[0].arn : local.oidc_provider_arn
}

output "oidc_provider_url" {
  description = "URL of the OIDC provider"
  value       = local.oidc_provider_url
}

output "trust_policy" {
  description = "Trust policy document for the IAM role"
  value       = local.trust_policy
  sensitive   = true
}

output "account_id" {
  description = "AWS Account ID"
  value       = local.account_id
}

output "project_id" {
  description = "GitLab project ID"
  value       = var.project_id
}

output "environment" {
  description = "Environment name"
  value       = var.environment
}

# Useful for GitLab CI configuration
output "gitlab_oidc_config" {
  description = "Configuration for GitLab CI (use in variables or directly in .gitlab-ci.yml)"
  value = {
    role_arn      = aws_iam_role.gitlab_oidc.arn
    region        = data.aws_region.current.name
    account_id    = local.account_id
    project_id    = var.project_id
    oidc_provider = local.oidc_provider_url
  }
  sensitive = false
}
