provider "aws" {
  region = var.aws_region
}

resource "aws_s3_bucket" "app_bucket" {
  bucket = var.bucket_name

  force_destroy = true

  tags = merge(var.common_tags, {
    Purpose = "Terraform state and app config file"
    Name    = var.bucket_name
  })
}

resource "aws_s3_bucket_ownership_controls" "secret_files" {
  bucket = aws_s3_bucket.app_bucket.id

  rule {
    object_ownership = "BucketOwnerPreferred"
  }
}

# resource "aws_s3_bucket_policy" "enforce_kms" {
#   count  = var.use_kms ? 1 : 0
#   bucket = aws_s3_bucket.app_bucket.bucket

#   policy = jsonencode({
#     Version = "2012-10-17"
#     Statement = [
#       {
#         Sid : "RequireKMSEncryption",
#         Effect : "Deny",
#         Principal : "*",
#         Action : "s3:PutObject",
#         Resource : "${aws_s3_bucket.app_bucket.arn}/*",
#         Condition : {
#           StringNotEquals : {
#             "s3:x-amz-server-side-encryption" : "aws:kms"
#           }
#         }
#       }
#     ]
#   })
# }

resource "aws_s3_bucket_cors_configuration" "bucketcors" {
  bucket = aws_s3_bucket.app_bucket.bucket

  cors_rule {
    allowed_headers = ["*"]
    allowed_methods = ["GET"]
    allowed_origins = ["*"]
  }
}

# Apply server-side encryption configuration (conditional)
resource "aws_s3_bucket_server_side_encryption_configuration" "encryption" {
  bucket = aws_s3_bucket.app_bucket.bucket

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = var.use_kms ? "aws:kms" : "AES256"
      kms_master_key_id = var.use_kms ? data.aws_kms_key.terraform_s3_key[0].arn : null
    }
  }
}

resource "aws_s3_bucket_policy" "enforce_encryption" {
  count  = length(local.bucket_policy_statements) > 0 ? 1 : 0
  bucket = aws_s3_bucket.app_bucket.id

  policy = jsonencode({
    Version   = "2012-10-17"
    Statement = local.bucket_policy_statements
  })

  # policy = templatefile("${path.module}/templates/s3_policy.json.tpl", {
  #   bucket_arn = aws_s3_bucket.app_bucket.arn
  #   use_kms     = var.use_kms
  # })

  depends_on = [
    aws_s3_bucket_server_side_encryption_configuration.encryption
  ]
}
