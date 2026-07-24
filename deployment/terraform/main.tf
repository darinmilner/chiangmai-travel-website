# root main.tf
module "infra" {
  source           = "./infra"
  vpc_cidr         = var.vpc_cidr
  num_subnets      = var.num_subnets
  environment      = var.environment
  allowed_ips      = var.allowed_ips
  common_tags      = local.common_tags
  app_name         = local.app_name_lower
  region           = var.region
  short_region     = local.short_region
  enable_flow_logs = true
}
