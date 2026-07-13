locals {
  common_tags = {
    Environment = var.environment
    CreatedBy   = "Terraform"
    AppName     = var.app_name
  }
}

# --- Create KMS Keys Dynamically ---
resource "aws_kms_key" "kms_key" {
  for_each = var.create_keys ? var.kms_keys : {}

  description             = coalesce(each.value.description, "KMS key for ${each.key}")
  enable_key_rotation     = each.value.enable_rotation
  deletion_window_in_days = 10

  tags = merge(local.common_tags, {
    Purpose = each.key
  })
}

# --- Create Matching Aliases ---
resource "aws_kms_alias" "kms_alias" {
  for_each = var.create_keys ? var.kms_keys : {}

  name          = "alias/${var.app_name}-${each.key}-key"
  target_key_id = aws_kms_key.kms_key[each.key].key_id
}
