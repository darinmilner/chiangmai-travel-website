data "aws_lambda_layer_version" "shared" {
  layer_name = "${var.layer_name}-${local.environment}-${local.short_region}"
  version    = 1 # Increment to the new version
}

data "aws_s3_bucket" "static_bucket" {
  bucket = "${local.app_name_lower}-static-file-${local.short_region}"
}
