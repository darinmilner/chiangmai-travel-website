locals {
  # Merge environment variables from secrets
  secret_vars    = var.secret_arn != "" ? jsondecode(data.aws_secretsmanager_secret_version.lambda_config[0].secret_string) : {}
  app_name       = "ChiangMaiVilla"
  app_name_lower = local.app_name_lower
  environment_variables = merge(
    {
      THUMBNAIL_SIZE = join(",", var.thumbnail_size)
      MEDIUM_SIZE    = join(",", var.medium_size)
      CAROUSEL_SIZE  = join(",", var.carousel_size)
      QUALITY        = tostring(var.image_quality)
      LOG_LEVEL      = var.log_level
    },
    local.secret_vars
  )

  tags = {
    Environment = "production"
    Service     = "villa-images"
    ManagedBy   = "terraform"
  }
}
