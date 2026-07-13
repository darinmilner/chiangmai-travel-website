# Region Configuration
variable "bangkok_region" {
  description = "AWS Bangkok region for Lambda and API Gateway"
  type        = string
  default     = "ap-southeast-7"
}

variable "singapore_region" {
  description = "AWS Singapore region for SES"
  type        = string
  default     = "ap-southeast-1"
}

variable "project_name" {
  description = "Project name prefix for resources"
  type        = string
  default     = "travel-contact"
}

variable "environment" {
  description = "Environment (dev/staging/prod)"
  type        = string
  default     = "prod"
}

# Lambda Configuration
variable "lambda_zip_path" {
  description = "Path to Lambda deployment zip file"
  type        = string
  default     = "../lambda/dist/lambda-function.zip"
}

# SES Configuration
variable "ses_domain" {
  description = "Domain to verify for SES"
  type        = string
}

variable "ses_source_email" {
  description = "Email address to send from (must be verified in SES)"
  type        = string
  sensitive   = true
}

variable "ses_destination_email" {
  description = "Email address to receive contact form submissions"
  type        = string
  sensitive   = true
}

variable "create_route53_records" {
  description = "Whether to create Route53 records for SES verification"
  type        = bool
  default     = false
}

variable "route53_zone_id" {
  description = "Route53 zone ID for DNS records (required if create_route53_records is true)"
  type        = string
  default     = ""
}

# API Gateway Configuration
variable "allowed_origins" {
  description = "CORS allowed origins"
  type        = list(string)
  default = [
    "https://your-travel-website.com",
    "https://www.your-travel-website.com",
    "http://localhost:8080"
  ]
}

# Application Configuration
variable "max_email_size_kb" {
  description = "Maximum email size in KB"
  type        = number
  default     = 10240
}

variable "rate_limit_per_minute" {
  description = "Rate limit per IP per minute"
  type        = number
  default     = 10
}

variable "log_retention_days" {
  description = "CloudWatch log retention in days"
  type        = number
  default     = 14
}

variable "tags" {
  description = "Resource tags"
  type        = map(string)
  default = {
    Environment = "production"
    Project     = "travel-website"
    ManagedBy   = "terraform"
    Region      = "multi-region"
  }
}
