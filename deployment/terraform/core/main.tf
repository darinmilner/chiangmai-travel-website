module "backend" {
  source      = "./modules/backend"
  aws_region  = var.region
  common_tags = local.common_tags
  bucket_name = local.bucket_name
  use_kms     = local.use_kms
  app_name    = local.app_name
  environment = var.environment
}

module "github_role" {
  source      = "./modules/github-roles"
  app_name    = local.app_name
  github_repo = var.github_repo_name
  use_kms     = local.use_kms
  bucket_arn  = module.backend.s3_bucket_arn
  kms_key_arn = null
  common_tags = local.common_tags
  environment = var.environment
}
