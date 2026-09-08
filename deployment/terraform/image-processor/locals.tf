locals {
  # Merge environment variables from secrets
  # secret_vars    = var.secret_arn != "" ? jsondecode(data.aws_secretsmanager_secret_version.lambda_config[0].secret_string) : {}
  app_name       = "ChiangMaiVilla"
  app_name_lower = lower(local.app_name)
  short_region   = replace(var.region, "-", "")

  tags = {
    Environment = var.environment
    Service     = "${local.app_name}-Image-Compression-Lambda"
    ManagedBy   = "Terraform"
  }
}
