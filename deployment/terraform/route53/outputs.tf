output "acm_certificate_arn" {
  description = "The ARN of the validated ACM certificate in us-east-1"
  value       = aws_acm_certificate_validation.cert_validation.certificate_arn
}

output "zone_id" {
  description = "The Route 53 Hosted Zone ID"
  value       = data.aws_route53_zone.primary.zone_id
}

output "cloudfront_domain_name" {
  description = "Retrieved CloudFront distribution domain name"
  value       = data.aws_cloudfront_distribution.existing.domain_name
}