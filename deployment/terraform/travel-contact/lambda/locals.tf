locals {
  environment    = "dev"
  app_name       = "ChiangMaiVilla"
  app_name_lower = lower(local.app_name)
  short_region = replace(var.bangkok_region, "-", "")
  tags = {
    "CreatedBy" = "Terraform"
    "AppName"   = local.app_name
  }
}
