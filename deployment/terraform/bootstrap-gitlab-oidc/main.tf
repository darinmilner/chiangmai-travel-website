# Create the OIDC provider if requested
resource "aws_iam_openid_connect_provider" "gitlab" {
  url             = var.gitlab_audience
  client_id_list  = [var.gitlab_audience]
  thumbprint_list = [data.tls_certificate.gitlab.certificates[0].sha1_fingerprint]

  tags = local.common_tags

  # Ensure we don't recreate provider unnecessarily
  lifecycle {
    prevent_destroy = true
  }
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

resource "aws_iam_role_policy" "terraform_deployment" {
  name = "${local.role_name}-terraform"
  role = aws_iam_role.gitlab_oidc.id

  policy = jsonencode({
    Version = "2012-10-17"

    Statement = [

      # ----------------------------------------------------------
      # Terraform / STS
      # ----------------------------------------------------------

      {
        Effect = "Allow"

        Action = [
          "sts:GetCallerIdentity"
        ]

        Resource = "*"
      },

      # ----------------------------------------------------------
      # Lambda
      # ----------------------------------------------------------

      {
        Effect = "Allow"

        Action = [
          "lambda:CreateFunction",
          "lambda:UpdateFunctionCode",
          "lambda:UpdateFunctionConfiguration",
          "lambda:DeleteFunction",
          "lambda:GetFunction",
          "lambda:GetFunctionConfiguration",

          "lambda:PublishVersion",
          "lambda:CreateAlias",
          "lambda:UpdateAlias",
          "lambda:DeleteAlias",

          "lambda:PublishLayerVersion",
          "lambda:GetLayerVersion",
          "lambda:DeleteLayerVersion",

          "lambda:CreateEventSourceMapping",
          "lambda:UpdateEventSourceMapping",
          "lambda:DeleteEventSourceMapping",
          "lambda:GetEventSourceMapping",

          "lambda:AddPermission",
          "lambda:RemovePermission",

          "lambda:TagResource",
          "lambda:UntagResource",
          "lambda:ListTags"
        ]

        Resource = "*"
      },

      # ----------------------------------------------------------
      # ECR
      # ----------------------------------------------------------

      {
        Effect = "Allow"

        Action = [
          "ecr:GetAuthorizationToken",
          "ecr:CreateRepository",
          "ecr:DeleteRepository",
          "ecr:DescribeRepositories",
          "ecr:PutImage",
          "ecr:BatchCheckLayerAvailability",
          "ecr:InitiateLayerUpload",
          "ecr:UploadLayerPart",
          "ecr:CompleteLayerUpload",
          "ecr:BatchGetImage",
          "ecr:DescribeImages",
          "ecr:ListImages",
          "ecr:DeleteRepositoryPolicy",
          "ecr:SetRepositoryPolicy",
          "ecr:TagResource"
        ]

        Resource = "*"
      },

      # ----------------------------------------------------------
      # S3
      # ----------------------------------------------------------

      {
        Effect = "Allow"

        Action = [
          "s3:CreateBucket",
          "s3:DeleteBucket",
          "s3:GetBucketLocation",
          "s3:GetBucketVersioning",
          "s3:PutBucketVersioning",
          "s3:GetBucketEncryption",
          "s3:PutBucketEncryption",
          "s3:GetBucketPolicy",
          "s3:PutBucketPolicy",
          "s3:DeleteBucketPolicy",
          "s3:GetBucketPublicAccessBlock",
          "s3:PutBucketPublicAccessBlock",
          "s3:GetBucketTagging",
          "s3:PutBucketTagging",
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject",
          "s3:ListBucket"
        ]

        Resource = "*"
      },

      # ----------------------------------------------------------
      # CloudFront
      # ----------------------------------------------------------

      {
        Effect = "Allow"

        Action = [
          "cloudfront:CreateDistribution",
          "cloudfront:GetDistribution",
          "cloudfront:UpdateDistribution",
          "cloudfront:DeleteDistribution",
          "cloudfront:CreateOriginAccessControl",
          "cloudfront:GetOriginAccessControl",
          "cloudfront:UpdateOriginAccessControl",
          "cloudfront:DeleteOriginAccessControl",
          "cloudfront:ListTagsForResource",
          "cloudfront:TagResource",
          "cloudfront:UntagResource"
        ]

        Resource = "*"
      },

      # ----------------------------------------------------------
      # API Gateway
      # ----------------------------------------------------------

      {
        Effect = "Allow"

        Action = [
          "apigateway:GET",
          "apigateway:POST",
          "apigateway:PUT",
          "apigateway:PATCH",
          "apigateway:DELETE"
        ]

        Resource = "*"
      },

      # ----------------------------------------------------------
      # VPC / EC2 networking
      # ----------------------------------------------------------

      {
        Effect = "Allow"

        Action = [
          "ec2:CreateVpc",
          "ec2:DeleteVpc",
          "ec2:DescribeVpcs",

          "ec2:CreateSubnet",
          "ec2:DeleteSubnet",
          "ec2:DescribeSubnets",

          "ec2:CreateRouteTable",
          "ec2:DeleteRouteTable",
          "ec2:DescribeRouteTables",
          "ec2:CreateRoute",
          "ec2:DeleteRoute",

          "ec2:CreateInternetGateway",
          "ec2:AttachInternetGateway",
          "ec2:DetachInternetGateway",
          "ec2:DeleteInternetGateway",

          "ec2:CreateNatGateway",
          "ec2:DeleteNatGateway",
          "ec2:DescribeNatGateways",

          "ec2:CreateSecurityGroup",
          "ec2:DeleteSecurityGroup",
          "ec2:DescribeSecurityGroups",
          "ec2:AuthorizeSecurityGroupIngress",
          "ec2:AuthorizeSecurityGroupEgress",
          "ec2:RevokeSecurityGroupIngress",
          "ec2:RevokeSecurityGroupEgress",

          "ec2:DescribeAvailabilityZones",
          "ec2:DescribeNetworkInterfaces",
          "ec2:DescribeAddresses",
          "ec2:AllocateAddress",
          "ec2:ReleaseAddress",
          "ec2:AssociateAddress",
          "ec2:DisassociateAddress",

          "ec2:CreateTags",
          "ec2:DeleteTags"
        ]

        Resource = "*"
      },

      # ----------------------------------------------------------
      # KMS
      # ----------------------------------------------------------

      {
        Effect = "Allow"

        Action = [
          "kms:CreateKey",
          "kms:DescribeKey",
          "kms:EnableKey",
          "kms:DisableKey",
          "kms:ScheduleKeyDeletion",
          "kms:CancelKeyDeletion",
          "kms:CreateAlias",
          "kms:UpdateAlias",
          "kms:DeleteAlias",
          "kms:ListAliases",
          "kms:TagResource",
          "kms:UntagResource",
          "kms:GetKeyPolicy",
          "kms:PutKeyPolicy"
        ]

        Resource = "*"
      },

      # ----------------------------------------------------------
      # Secrets Manager
      # ----------------------------------------------------------

      {
        Effect = "Allow"

        Action = [
          "secretsmanager:CreateSecret",
          "secretsmanager:DeleteSecret",
          "secretsmanager:DescribeSecret",
          "secretsmanager:GetSecretValue",
          "secretsmanager:PutSecretValue",
          "secretsmanager:UpdateSecret",
          "secretsmanager:UpdateSecretVersionStage",
          "secretsmanager:TagResource",
          "secretsmanager:UntagResource"
        ]

        Resource = "*"
      },

      # ----------------------------------------------------------
      # IAM
      #
      # Terraform needs this because it will create the execution
      # roles used by Lambda / EC2 / ECS etc.
      # ----------------------------------------------------------

      {
        Effect = "Allow"

        Action = [
          "iam:CreateRole",
          "iam:DeleteRole",
          "iam:GetRole",
          "iam:UpdateRole",
          "iam:UpdateAssumeRolePolicy",

          "iam:AttachRolePolicy",
          "iam:DetachRolePolicy",

          "iam:PutRolePolicy",
          "iam:DeleteRolePolicy",
          "iam:GetRolePolicy",

          "iam:CreatePolicy",
          "iam:DeletePolicy",
          "iam:GetPolicy",
          "iam:GetPolicyVersion",
          "iam:CreatePolicyVersion",
          "iam:DeletePolicyVersion",

          "iam:PassRole",

          "iam:TagRole",
          "iam:UntagRole"
        ]

        Resource = "*"
      }
    ]
  })
}
