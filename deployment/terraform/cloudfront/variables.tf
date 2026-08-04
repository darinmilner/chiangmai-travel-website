variable "name_prefix" {
  description = "Prefix for resource names"
  type        = string
  default     = "villa"
}

variable "bucket_domain_name" {
  description = "S3 bucket domain name (bucket_regional_domain_name)"
  type        = string
}

variable "bucket_id" {
  description = "S3 bucket ID"
  type        = string
}

variable "s3_prefix" {
  description = "S3 prefix/folder for images"
  type        = string
  default     = "villa"
}

variable "custom_domains" {
  description = "Custom domain names for CloudFront"
  type        = list(string)
  default     = []
}

variable "certificate_arn" {
  description = "ACM certificate ARN for CloudFront (required for custom domains)"
  type        = string
  default     = ""
}

variable "price_class" {
  description = "CloudFront price class"
  type        = string
  default     = "PriceClass_100"

  validation {
    condition     = contains(["PriceClass_100", "PriceClass_200", "PriceClass_All"], var.price_class)
    error_message = "Invalid price class. Must be PriceClass_100, PriceClass_200, or PriceClass_All."
  }
}

variable "geo_restriction_type" {
  description = "Geo restriction type for CloudFront"
  type        = string
  default     = "none"

  validation {
    condition     = contains(["none", "whitelist", "blacklist"], var.geo_restriction_type)
    error_message = "Invalid geo restriction type. Must be none, whitelist, or blacklist."
  }
}

variable "geo_restriction_locations" {
  description = "List of country codes for geo restriction"
  type        = list(string)
  default     = []
}

variable "min_ttl" {
  description = "Minimum TTL for cache"
  type        = number
  default     = 0
}

variable "default_ttl" {
  description = "Default TTL for cache"
  type        = number
  default     = 86400
}

variable "max_ttl" {
  description = "Maximum TTL for cache"
  type        = number
  default     = 31536000
}

variable "web_acl_id" {
  description = "WAF Web ACL ID (optional)"
  type        = string
  default     = ""
}

variable "enable_logging" {
  description = "Enable CloudFront access logging"
  type        = bool
  default     = false
}

variable "log_bucket" {
  description = "S3 bucket for CloudFront logs"
  type        = string
  default     = ""
}

variable "log_prefix" {
  description = "Prefix for CloudFront logs"
  type        = string
  default     = "cloudfront/"
}

variable "tags" {
  description = "Resource tags"
  type        = map(string)
  default = {
    Environment = "production"
    Service     = "villa-images"
    ManagedBy   = "terraform"
  }
}
