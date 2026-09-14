variable "ses_domain" {
  description = "Domain for the application"
  type        = string
  default     = ""
}

variable "ses_source_email" {
  type        = string
  description = "Optional source email address for testing"
}

variable "ses_destination_email" {
  type        = string
  description = "Optional destination email address for testing"
}

variable "singapore_region" {
  type        = string
  default     = "ap-southeast-1"
  description = "AWS region hosting SES resources"
}

variable "bangkok_region" {
  type        = string
  default     = "ap-southeast-7"
  description = "AWS region hosting primary workload and state bucket"
}

variable "create_receipt_rules" {
  type        = bool
  default     = false
  description = "Whether to create SES receipt rules"
}

variable "s3_bucket_name" {
  type        = string
  default     = "chiangmai-villa-static-files"
  description = "S3 bucket name for receipt rule storage action"
}

variable "lambda_arn" {
  type        = string
  default     = ""
  description = "Lambda function ARN for receipt rule action"
}

variable "create_route53_records" {
  type        = bool
  default     = false
  description = "Whether to create Route53 records for domain verification and DKIM"
}

variable "route53_zone_id" {
  type        = string
  default     = ""
  description = "Route53 Hosted Zone ID"
}
