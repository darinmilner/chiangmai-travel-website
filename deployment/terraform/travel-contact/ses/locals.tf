locals {
  app_name            = "ChiangMaiVilla"
  app_name_lower      = lower(local.app_name)
  bucket_short_region = replace(var.bangkok_region, "-", "")
}