

# Apex Domain IPv4 Record (A -> CloudFront)
resource "aws_route53_record" "apex_a" {
  zone_id = data.aws_route53_zone.primary.zone_id
  name    = var.domain_name
  type    = "A"

  alias {
    name                   = data.aws_cloudfront_distribution.existing.domain_name
    zone_id                = data.aws_cloudfront_distribution.existing.hosted_zone_id
    evaluate_target_health = false
  }
}

# Apex Domain IPv6 Record (AAAA -> CloudFront)
resource "aws_route53_record" "apex_aaaa" {
  zone_id = data.aws_route53_zone.primary.zone_id
  name    = var.domain_name
  type    = "AAAA"

  alias {
    name                   = data.aws_cloudfront_distribution.existing.domain_name
    zone_id                = data.aws_cloudfront_distribution.existing.hosted_zone_id
    evaluate_target_health = false
  }
}

# Subdomain Records (e.g., www.example.com -> CloudFront)
resource "aws_route53_record" "subdomain_a" {
  for_each = toset(var.subdomains)

  zone_id = data.aws_route53_zone.primary.zone_id
  name    = "${each.value}.${var.domain_name}"
  type    = "A"

  alias {
    name                   = data.aws_cloudfront_distribution.existing.domain_name
    zone_id                = data.aws_cloudfront_distribution.existing.hosted_zone_id
    evaluate_target_health = false
  }
}
