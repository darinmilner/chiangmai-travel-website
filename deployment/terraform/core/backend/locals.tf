# Dynamically build policy
locals {
  # Base statement: allow all IAM users in your account to manage objects
  base_statement = {
    Sid    = "AllowAccountUsersFullObjectAccess"
    Effect = "Allow"
    Principal = {
      AWS = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"
    }
    Action = [
      "s3:GetObject",
      "s3:PutObject",
      "s3:DeleteObject",
      "s3:ListBucket"
    ]
    Resource = [
      aws_s3_bucket.app_bucket.arn,
      "${aws_s3_bucket.app_bucket.arn}/*"
    ]
  }

  # Optional KMS enforcement if use_kms = true
  kms_statement = var.use_kms ? [
    {
      Sid       = "RequireKMSEncryption"
      Effect    = "Deny"
      Principal = "*"
      Action    = "s3:PutObject"
      Resource  = "${aws_s3_bucket.app_bucket.arn}/*"
      Condition = {
        StringNotEqualsIfExists = {
          "s3:x-amz-server-side-encryption" = "aws:kms"
        }
      }
    }
  ] : []

  # Combine statements
  bucket_policy_statements = concat([local.base_statement], local.kms_statement)
}
