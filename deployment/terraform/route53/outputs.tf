output "zone_id" {
  description = "The Route 53 Hosted Zone ID"
  value       = aws_route53_zone.primary.zone_id
}

output "cloudfront_domain_name" {
  description = "Retrieved CloudFront distribution domain name"
  value       = data.aws_cloudfront_distribution.existing.domain_name
}

output "route53_nameservers" {
  value = aws_route53_zone.primary.name_servers
}