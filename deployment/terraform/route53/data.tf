data "aws_cloudfront_distribution" "existing" {
  id = var.cloudfront_domain_id
}
