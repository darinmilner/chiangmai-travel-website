locals {
  region         = "ap-southeast-7"
  app_name       = "ChiangMaiHalal"
  app_name_lower = lower(local.app_name)
  environment    = "beta"
  short_region   = replace(local.region, "-", "")
}
