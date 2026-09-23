# Look up existing Route 53 Hosted Zone
data "aws_route53_zone" "primary" {
  name         = var.domain_name
  private_zone = false
}