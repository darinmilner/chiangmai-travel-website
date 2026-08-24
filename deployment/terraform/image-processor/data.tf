data "terraform_remote_state" "cloudfront" {
  backend = "s3"

  config = {
    bucket = var.bucket_id                  # Same bucket
    key    = "cloudfront/terraform.tfstate" # Exact folder path to CloudFront state
    region = var.region
  }
}

# Archive the Lambda code
data "archive_file" "lambda_zip" {
  type        = "zip"
  source_dir  = "${path.module}/src"
  output_path = "${path.module}/src/function.zip"

  excludes = [
    "tests/",
    "*.pyc",
    "__pycache__/",
    ".pytest_cache/",
    "*.egg-info/"
  ]
}
