locals {
  # ------------------------------------------------------------
  # Application
  # ------------------------------------------------------------

  app_name       = "ChiangMaiVilla"
  app_name_lower = lower(local.app_name)

  # ------------------------------------------------------------
  # AWS account
  # ------------------------------------------------------------

  account_id = data.aws_caller_identity.current.account_id

  # ------------------------------------------------------------
  # Naming
  # ------------------------------------------------------------

  role_name = "${local.app_name_lower}-gitlab-oidc-deploy-${var.environment}"

  # ------------------------------------------------------------
  # GitLab OIDC
  # ------------------------------------------------------------

  oidc_provider_url = replace(
    var.gitlab_audience,
    "https://",
    ""
  )

  oidc_provider_arn = (
    "arn:aws:iam::${local.account_id}:oidc-provider/${local.oidc_provider_url}"
  )

  # ------------------------------------------------------------
  # Tags
  # ------------------------------------------------------------

  common_tags = {
    Environment = var.environment
    ManagedBy   = "Terraform"
    Project     = local.app_name
  }

  # ------------------------------------------------------------
  # GitLab OIDC trust policy
  # ------------------------------------------------------------

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

          StringLike = {
            "${local.oidc_provider_url}:sub" = [
              "project_path:*:ref_type:branch:ref:main",
              "project_path:*:ref_type:branch:ref:master"
            ]
          }
        }
      }
    ]
  }
}
