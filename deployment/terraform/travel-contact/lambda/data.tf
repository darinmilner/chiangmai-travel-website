data "aws_lambda_layer_version" "shared" {
  layer_name = "villa-shared-layer"
  version    = 2 # Increment to the new version
}
