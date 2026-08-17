# Get current AWS account details
data "aws_caller_identity" "current" {}

# Get current AWS region
data "aws_region" "current" {}

data "aws_iam_policy_document" "terraform_deployment" {
  statement {
    effect = "Allow"

    actions = [
      "lambda:*",
      "ecr:*",
      "s3:*",
      "cloudfront:*",
      "apigateway:*",
      "ec2:*",
      "kms:*",
      "secretsmanager:*"
    ]

    resources = ["*"]
  }

  statement {
    effect = "Allow"

    actions = [
      "iam:GetRole",
      "iam:CreateRole",
      "iam:DeleteRole",
      "iam:UpdateRole",
      "iam:UpdateAssumeRolePolicy",
      "iam:AttachRolePolicy",
      "iam:DetachRolePolicy",
      "iam:PutRolePolicy",
      "iam:DeleteRolePolicy",
      "iam:GetRolePolicy",
      "iam:ListRolePolicies",
      "iam:ListAttachedRolePolicies",
      "iam:PassRole",
      "iam:TagRole",
      "iam:UntagRole"
    ]

    resources = ["*"]
  }
}

data "tls_certificate" "gitlab" {
  count = var.create_oidc_provider ? 1 : 0

  url = var.gitlab_audience
}

