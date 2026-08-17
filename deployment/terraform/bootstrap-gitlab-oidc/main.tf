# Create the OIDC provider if requested
resource "aws_iam_openid_connect_provider" "gitlab" {
  count = var.create_oidc_provider ? 1 : 0

  url             = var.gitlab_audience
  client_id_list  = [var.gitlab_audience]
  thumbprint_list = [data.tls_certificate.gitlab[0].certificates[0].sha1_fingerprint]

  tags = merge(local.common_tags, {
    Name = "gitlab-oidc-provider"
  })

  # Ensure we don't recreate provider unnecessarily
  lifecycle {
    prevent_destroy = true
  }
}

# Get GitLab's certificate for thumbprint
data "tls_certificate" "gitlab" {
  count = var.create_oidc_provider ? 1 : 0

  url = var.gitlab_audience
}

# Create the IAM role
resource "aws_iam_role" "gitlab_oidc" {
  name                 = local.role_name
  assume_role_policy   = jsonencode(local.trust_policy)
  description          = "IAM role for GitLab OIDC authentication - Project ${var.project_id}"
  max_session_duration = var.max_session_duration

  tags = merge(local.common_tags, {
    Name = local.role_name
  })

  # Prevent accidental deletion
  lifecycle {
    create_before_destroy = true
  }
}

# Attach managed policies
resource "aws_iam_role_policy_attachment" "attachments" {
  count = length(var.policy_arns)

  role       = aws_iam_role.gitlab_oidc.name
  policy_arn = var.policy_arns[count.index]

  # Ensure role is created before attaching policies
  depends_on = [aws_iam_role.gitlab_oidc]
}

# Create inline policies
resource "aws_iam_role_policy" "inline" {
  for_each = var.inline_policies

  name   = each.key
  role   = aws_iam_role.gitlab_oidc.name
  policy = each.value

  depends_on = [aws_iam_role.gitlab_oidc]
}

# Create a policy for common GitLab operations
resource "aws_iam_policy" "gitlab_oidc_default" {
  count       = length(var.policy_arns) == 0 && length(var.inline_policies) == 0 ? 1 : 0
  name        = "${local.role_name}-default-policy"
  description = "Default policy for GitLab OIDC role with minimal permissions"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "sts:GetCallerIdentity",
          "ecr:GetAuthorizationToken",
          "ecr:BatchGetImage",
          "ecr:GetDownloadUrlForLayer"
        ]
        Resource = "*"
      }
    ]
  })

  tags = local.common_tags
}

# Attach default policy if no policies are specified
resource "aws_iam_role_policy_attachment" "default_attachment" {
  count = length(var.policy_arns) == 0 && length(var.inline_policies) == 0 ? 1 : 0

  role       = aws_iam_role.gitlab_oidc.name
  policy_arn = aws_iam_policy.gitlab_oidc_default[0].arn

  depends_on = [aws_iam_role.gitlab_oidc, aws_iam_policy.gitlab_oidc_default]
}
