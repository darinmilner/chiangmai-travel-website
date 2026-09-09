data "terraform_remote_state" "cloudfront" {
  backend = "s3"

  config = {
    bucket = "chiangmaivilla-backendfiles-apsoutheast7-beta" # Same bucket
    key    = "cloudfront/terraform.tfstate"                  # Exact folder path to CloudFront state
    region = var.region
  }
}

data "aws_s3_bucket" "image_bucket" {
  bucket = "${local.app_name_lower}-static-files-${local.short_region}"
}
