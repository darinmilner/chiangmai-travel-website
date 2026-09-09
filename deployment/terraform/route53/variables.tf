variable "domain_name" {
  description = "The primary domain name (e.g., chiangmaivilla.com)"
  type        = string
}

variable "subdomains" {
  description = "List of subdomains to route to CloudFront (e.g., ['www'])"
  type        = list(string)
  default     = ["www"]
}

variable "cloudfront_domain_id" {
  description = "The domain id of the CloudFront distribution"
  type        = string
  default     = "E22QJO9YU3VDIS"
}

variable "cloudfront_hosted_zone_id" {
  description = "CloudFront hosted zone ID (Always Z2FDTNDATAQYW2 for CloudFront)"
  type        = string
  default     = "Z2FDTNDATAQYW2"
}
