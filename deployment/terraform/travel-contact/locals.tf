locals {
  app_name = "ChiangMaiVilla"
  tags = {
    default = {
      Environment = var.environment
      Project     = lower(local.app_name)
      ManagedBy   = "Terraform"
    }
  }
}
