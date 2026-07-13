# Data lookup for existing KMS key
data "aws_kms_key" "terraform_s3_key" {
  count  = var.use_kms ? 1 : 0
  key_id = "alias/${var.app_name}-terraform-key"
}

data "aws_caller_identity" "current" {}
