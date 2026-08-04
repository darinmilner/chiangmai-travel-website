
# ============================================
# IAM Policy for Reading Secrets
# ============================================

resource "aws_iam_policy" "secrets_reader" {
  count = var.create_iam_policy ? 1 : 0

  name        = "${var.environment}-secrets-reader-policy"
  description = "Policy to read secrets from AWS Secrets Manager"
  path        = var.iam_policy_path

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue",
          "secretsmanager:DescribeSecret",
          "secretsmanager:ListSecretVersionIds",
          "secretsmanager:GetResourcePolicy",
          "secretsmanager:GetSecretRotationPolicy"
        ]
        Resource = [
          for secret in aws_secretsmanager_secret.secrets : secret.arn
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetRandomPassword"
        ]
        Resource = ["*"]
      }
    ]
  })

  tags = var.tags
}

# ============================================
# IAM Role for Secret Access
# ============================================

resource "aws_iam_role" "secrets_reader_role" {
  count = var.create_iam_role ? 1 : 0

  name = "${var.environment}-secrets-reader-role"
  path = var.iam_role_path

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = var.allowed_services
        }
      }
    ]
  })

  tags = var.tags
}

# Attach the secrets reader policy to the role
resource "aws_iam_role_policy_attachment" "secrets_reader_attachment" {
  count = var.create_iam_role && var.create_iam_policy ? 1 : 0

  role       = aws_iam_role.secrets_reader_role[0].name
  policy_arn = aws_iam_policy.secrets_reader[0].arn
}

# Create instance profile for EC2
resource "aws_iam_instance_profile" "secrets_reader_profile" {
  count = var.create_iam_role && var.create_instance_profile ? 1 : 0

  name = "${var.environment}-secrets-reader-profile"
  role = aws_iam_role.secrets_reader_role[0].name

  tags = var.tags
}
