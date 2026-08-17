locals {
  app_name = "ChiangMaiVilla"
  common_tags = {
    Environment = var.environment
    AppName     = local.app_name
    ManagedBy   = "Terraform"
  }
}
