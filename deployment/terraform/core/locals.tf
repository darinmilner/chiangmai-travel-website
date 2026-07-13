locals {
  app_name     = "ShareDrive"
  short_region = replace(var.region, "-", "")
  bucket_name  = lower("${var.app_name}-cnx-backendfiles-${local.short_region}-${var.environment}")
  use_kms      = false
  common_tags = {
    Environment = var.environment
    CreatedBy   = "Terraform"
    AppName     = local.app_name
    Region      = local.short_region
  }
}
