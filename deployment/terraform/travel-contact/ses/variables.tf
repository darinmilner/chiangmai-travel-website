variable "project_name" {
  description = "Project name prefix for resources"
  type        = string
}

variable "singapore_region" {
  description = "AWS Singapore region for SES"
  type        = string
  default     = "ap-southeast-1"
}

variable "ses_domain" {
  description = "Domain to verify for SES"
  type        = string
}

variable "ses_source_email" {
  description = "Email address to send from (optional if domain is verified)"
  type        = string
  default     = ""
}

variable "ses_destination_email" {
  description = "Email address to receive contact form submissions"
  type        = string
  default     = ""
}

variable "create_receipt_rules" {
  description = "Whether to create SES receipt rules"
  type        = bool
  default     = false
}

variable "create_route53_records" {
  description = "Whether to create Route53 records for SES verification"
  type        = bool
  default     = false
}

variable "route53_zone_id" {
  description = "Route53 zone ID for DNS records"
  type        = string
  default     = ""
}

variable "s3_bucket_name" {
  description = "S3 bucket name for storing emails (optional)"
  type        = string
  default     = ""
}

variable "lambda_arn" {
  description = "Lambda ARN for SES receipt rule (optional)"
  type        = string
  default     = ""
}

variable "create_lambda_policy" {
  description = "Whether to create IAM policy for Lambda to use SES"
  type        = bool
  default     = true
}

variable "tags" {
  description = "Tags to apply to resources"
  type        = map(string)
  default     = {}
}
