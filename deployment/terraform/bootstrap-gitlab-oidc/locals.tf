locals {
  account_id     = data.aws_caller_identity.current.account_id
  app_name       = "ChiangMaiVilla"
  app_name_lower = lower(local.app_name)

  common_tags = {
    Environment = var.environment
    ManagedBy   = "Terraform"
    Project     = "GitLab-OIDC-${local.app_name}"
  }

  role_name = "${local.app_name_lower}-gitlab-oidc-deploy-${var.environment}"

  oidc_provider_url = replace(var.gitlab_audience, "https://", "")

  trust_policy = {
    Version = "2012-10-17"

    Statement = [
      {
        Effect = "Allow"

        Principal = {
          Federated = aws_iam_openid_connect_provider.gitlab.arn
        }

        Action = "sts:AssumeRoleWithWebIdentity"

        Condition = {
          StringEquals = {
            "${local.oidc_provider_url}:aud" = var.gitlab_audience
          }

          StringLike = {
            "${local.oidc_provider_url}:sub" = "project:${var.project_id}:ref_type:branch:ref:master"
          }
        }
      }
    ]
  }
}