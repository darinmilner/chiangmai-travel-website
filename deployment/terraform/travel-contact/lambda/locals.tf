locals {
  environment = "dev"
  app_name    = "ChiangMaiVilla"
  tags = {
    "CreatedBy" = "Terraform"
    "AppName"   = local.app_name
  }
}
