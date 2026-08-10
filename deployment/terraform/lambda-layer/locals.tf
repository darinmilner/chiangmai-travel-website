locals {
  region       = "ap-southeast-7"
  short_region = replace(local.region, "-", "")
  environment  = "dev"
}
