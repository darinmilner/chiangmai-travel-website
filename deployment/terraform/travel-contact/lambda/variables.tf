variable "bangkok_region" {
  description = "AWS Bangkok region"
  type        = string
  default     = "ap-southeast-7"
}

variable "lambda_zip_path" {
  description = "Path to Lambda deployment zip file"
  type        = string
  default     = "build/travel-contact.zip"
}

variable "layer_name" {
  description = "Name of the Lambda layer"
  type        = string
  default     = "chiangmai-villa-shared-layer"
}

variable "ses_source_email" {
  description = "SES source email (from Singapore region)"
  type        = string
}

variable "ses_destination_email" {
  description = "SES destination email (from Singapore region)"
  type        = string
}

variable "ses_region" {
  description = "SES region (Singapore)"
  type        = string
  default     = "ap-southeast-1"
}

variable "ses_iam_policy_arn" {
  description = "ARN of IAM policy for SES access"
  type        = string
  default     = ""
}

variable "max_email_size_kb" {
  description = "Maximum email size in KB"
  type        = number
  default     = 10240
}

variable "rate_limit_per_minute" {
  description = "Rate limit per minute for contact form"
  type        = number
  default     = 10
}

variable "log_retention_days" {
  description = "CloudWatch log retention in days"
  type        = number
  default     = 14
}

variable "log_level" {
  description = "Logging Level"
  default     = "Debug"
}

variable "create_s3_notification" {
  description = "Create S3 Notification"
  type        = bool
  default     = false
}

variable "s3_bucket" {
  description = "S3 Bucket for notifications"
  type        = string
}

variable "s3_notification_prefix" {
  description = "S3 Notification prefix"
  type        = string
  default     = "notifications"
}
