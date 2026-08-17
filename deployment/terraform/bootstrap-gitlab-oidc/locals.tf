locals {
  account_id     = var.account_id != null ? var.account_id : data.aws_caller_identity.current.account_id
  app_name       = "ChiangMaiVilla"
  app_name_lower = lower(local.app_name)
  # Standard tags that will be applied to all resources
  common_tags = {
    Environment = var.environment
    ManagedBy   = "Terraform"
    Project     = "GitLab-OIDC-${local.app_name}"
    CreatedAt   = timestamp()
  }

  # Role name with environment prefix
  role_name = "${var.environment}-${var.role_name}"

  # OIDC provider ARN
  oidc_provider_arn = "arn:aws:iam::${local.account_id}:oidc-provider/${replace(var.gitlab_audience, "https://", "")}"

  # OIDC provider URL without protocol
  oidc_provider_url = replace(var.gitlab_audience, "https://", "")

  # Trust policy for GitLab OIDC
  trust_policy = {
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Federated = var.create_oidc_provider ? aws_iam_openid_connect_provider.gitlab[0].arn : local.oidc_provider_arn
        }
        Action = "sts:AssumeRoleWithWebIdentity"
        Condition = {
          StringEquals = {
            "${local.oidc_provider_url}:project_id" = var.project_id
          }
          # Optional: Add additional conditions for extra security
          # StringLike = {
          #   "${local.oidc_provider_url}:ref_type" = "branch"
          # }
        }
      }
    ]
  }
}
