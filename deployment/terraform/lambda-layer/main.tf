# Lambda Layer Version
resource "aws_lambda_layer_version" "shared_layer" {
  layer_name               = "${var.layer_name}-${local.environment}-${local.short_region}"
  description              = var.description
  compatible_runtimes      = var.compatible_runtimes
  compatible_architectures = var.compatible_architectures
  license_info             = var.license_info
  source_code_hash         = filebase64sha256(var.filename)
  filename                 = var.filename
  skip_destroy             = var.skip_destroy
}
