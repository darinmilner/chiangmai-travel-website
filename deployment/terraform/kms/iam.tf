data "aws_caller_identity" "current" {}

resource "aws_kms_key_policy" "s3_kms_policy" {
  for_each = var.create_keys ? var.kms_keys : {}
  key_id   = aws_kms_key.kms_key[each.key].id

  policy = jsonencode({
    Version = "2012-10-17"
    Id      = "kms-key-policy"
    Statement = [
      {
        Sid    = "Enable IAM User Permissions"
        Effect = "Allow"
        Principal = {
          AWS = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"
        }
        Action   = "kms:*"
        Resource = "*"
      },
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