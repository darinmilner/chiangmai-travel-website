locals {
  common_tags = {
    Environment = var.environment
    CreatedBy   = "Terraform"
    AppName     = var.app_name
  }
  app_name_lower = lower(var.app_name)
}
