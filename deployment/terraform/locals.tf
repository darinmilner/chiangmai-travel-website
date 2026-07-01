locals {
  app_name       = "RoofInLeaf"
  app_name_lower = lower(local.app_name)
  short_region   = replace(var.region, "-", "")
  common_tags = {
    Environment = var.environment
    CreatedBy   = "Terraform"
    AppName     = local.app_name
    Region      = local.short_region
  }
}
