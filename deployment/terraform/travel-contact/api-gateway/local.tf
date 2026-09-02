locals {
  app_name       = "ChiangMaiVilla"
  app_name_lower = lower(local.app_name_lower)
  tags = {
    default = {
      Environment = var.environment
      Project     = local.app_name
      ManagedBy   = "Terraform"
    }
  }
}
