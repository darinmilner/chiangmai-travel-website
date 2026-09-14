locals {
  app_name       = "ChiangMaiVilla"
  app_name_lower = lower(local.app_name)
  short_region   = replace(var.region, "-", "")
  tags = {
    Environment = var.environment
    Project     = local.app_name
    ManagedBy   = "Terraform"
  }
}
