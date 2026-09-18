data "aws_caller_identity" "current" {}

resource "aws_kms_key_policy" "s3_kms_policy" {
  for_each = var.create_keys ? var.kms_keys : {}
  key_id   = aws_kms_key.kms_key[each.key].id

  policy = jsonencode({
    Version = "2012-10-17"
    Id      = "kms-key-policy"
    Statement = [
      # 1. Enable IAM User & Role Permissions Delegation (CRITICAL)
      {
        Sid    = "Enable IAM User Permissions"
        Effect = "Allow"
        Principal = {
          AWS = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"
        }
        Action   = "kms:*"
        Resource = "*"
      },
      # 2. Allow S3 Service to encrypt/decrypt objects
      {
        Sid    = "Allow S3 Service Use of the Key"
        Effect = "Allow"
        Principal = {
          Service = "s3.amazonaws.com"
        }
        Action = [
          "kms:GenerateDataKey*",
          "kms:Decrypt"
        ]
        Resource = "*"
      }
    ]
  })
}