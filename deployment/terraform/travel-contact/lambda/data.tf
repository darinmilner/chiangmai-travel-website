data "aws_lambda_layer_version" "shared" {
  layer_name = "${var.layer_name}-${local.environment}-${local.short_region}"
  version    = 1 # Increment to the new version
}
