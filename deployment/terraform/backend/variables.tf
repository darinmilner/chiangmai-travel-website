variable "aws_region" {
  description = "Region to deploy the bucket"
  type        = string
}

variable "app_name" {
  description = "App name"
  type        = string
}

variable "use_kms" {
  description = "Whether to use a customer-managed KMS key for S3 encryption"
  type        = bool
}

variable "environment" {
  description = "Deployment environment"
  type        = string
}

variable "bucket_name" {
  description = "Name of Bucket to store state and .env files"
  type        = string
}

variable "common_tags" {
  description = "Common tags for all resources"
  type        = map(string)
}
