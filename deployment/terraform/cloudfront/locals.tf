locals {
  app_name       = "ChiangMaiVilla"
  lower_app_name = lower(local.app_name)
  short_region   = replace(var.region, "-", "")
  common_tags = {
    Environment = var.environment
    AppName     = local.app_name
    ManagedBy   = "Terraform"
  }
}
