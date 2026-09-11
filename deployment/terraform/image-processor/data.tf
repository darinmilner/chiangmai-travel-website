data "terraform_remote_state" "cloudfront" {
  backend = "s3"

  config = {
    bucket = "chiangmaivilla-backendfiles-apsoutheast7-beta" # Same bucket
    key    = "statefiles/cloudfront/terraform.tfstate"       # Exact folder path to CloudFront state
    region = var.region
  }
}

data "aws_s3_bucket" "image_bucket" {
  bucket = "${local.app_name_lower}-static-files-${local.short_region}"
}

data "aws_lambda_layer_version" "shared_layer" {
  layer_name = "${var.layer_name}-${var.environment}-${local.short_region}"
  version    = 1
}
