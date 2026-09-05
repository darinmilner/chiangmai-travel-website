output "cloudfront_domain" {
  description = "CloudFront distribution domain name"
  value       = aws_cloudfront_distribution.images.domain_name
}

output "cloudfront_distribution_id" {
  description = "CloudFront distribution ID"
  value       = aws_cloudfront_distribution.images.id
}

output "cloudfront_url" {
  description = "CloudFront distribution URL (https://domain)"
  value       = "https://${aws_cloudfront_distribution.images.domain_name}"
}

output "cloudfront_arn" {
  description = "CloudFront distribution ARN"
  value       = aws_cloudfront_distribution.images.arn
}

output "cloudfront_hosted_zone_id" {
  description = "CloudFront distribution hosted zone ID"
  value       = aws_cloudfront_distribution.images.hosted_zone_id
}

output "cache_policy_id" {
  description = "CloudFront cache policy ID"
  value       = aws_cloudfront_cache_policy.images.id
}

output "response_headers_policy_id" {
  description = "CloudFront response headers policy ID"
  value       = aws_cloudfront_response_headers_policy.security.id
}
