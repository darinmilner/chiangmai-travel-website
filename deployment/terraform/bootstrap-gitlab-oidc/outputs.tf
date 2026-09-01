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
  value       = aws_iam_openid_connect_provider.gitlab.arn
}

output "oidc_provider_url" {
  description = "URL of the OIDC provider"
  value       = local.oidc_provider_url
}

# Useful for GitLab CI configuration
output "gitlab_oidc_config" {
  description = "Configuration for GitLab CI (use in variables or directly in .gitlab-ci.yml)"
  value = {
    role_arn      = aws_iam_role.gitlab_oidc.arn
    account_id    = local.account_id
    project_path    = var.project_path
    oidc_provider = local.oidc_provider_url
  }
  sensitive = false
}
