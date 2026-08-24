resource "aws_s3_bucket" "static_bucket" {
  bucket = "${var.bucket_name}-${local.short_region}"

  force_destroy = true

  tags = merge(local.common_tags, {
    Purpose = "Cloudfront static files bucket"
    Name    = "${var.bucket_name}-${local.short_region}"
  })
}

resource "aws_s3_bucket_ownership_controls" "static_files" {
  bucket = aws_s3_bucket.static_bucket.id

  rule {
    object_ownership = "BucketOwnerPreferred"
  }
}

resource "aws_s3_bucket_cors_configuration" "static_images" {
  bucket = aws_s3_bucket.static_bucket.id

  cors_rule {
    allowed_headers = ["*"]
    allowed_methods = ["GET", "HEAD"]
    allowed_origins = ["*"] # Replace with your app domain (e.g., https://app.yourdomain.com)
    expose_headers  = ["ETag"]
    max_age_seconds = 3000
  }
}
