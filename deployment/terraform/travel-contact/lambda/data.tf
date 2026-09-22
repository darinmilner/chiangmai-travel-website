data "aws_lambda_layer_version" "shared" {
  layer_name = "${var.layer_name}-${var.environment}-${local.short_region}"
  version    = 3 # Increment to the new version
}

data "aws_s3_bucket" "static_bucket" {
  bucket = "${local.app_name_lower}-static-files-${local.short_region}"
}
