variable "lambda_zip_path" {
  description = "Path to Lambda deployment zip file"
  type        = string
  default     = "build/image-processor.zip"
}

variable "environment" {
  description = "Deployment Environment"
  default     = "dev"

  validation {
    condition     = contains(["dev", "staging", "beta", "prod"], var.environment)
    error_message = "Environment must be one of: dev, staging, beta or prod"
  }
}

variable "input_prefix" {
  description = "S3 prefix/folder for images"
  type        = string
  default     = "uploads/"
}

variable "output_prefix" {
  description = "s3 output prefix for satic images"
  type        = string
  default     = "static/"
}

variable "lambda_timeout" {
  description = "Lambda function timeout in seconds"
  type        = number
  default     = 30
}

variable "lambda_memory" {
  description = "Lambda function memory in MB"
  type        = number
  default     = 1024
}

variable "image_quality" {
  description = "JPEG image quality (1-100)"
  type        = number
  default     = 85

  validation {
    condition     = var.image_quality >= 1 && var.image_quality <= 100
    error_message = "Image quality must be between 1 and 100."
  }
}
variable "thumbnail_size" {
  type    = string
  default = "150,150"
}

variable "medium_size" {
  type    = string
  default = "600,600"
}

variable "carousel_size" {
  type    = string
  default = "1200,800"
}

variable "log_level" {
  description = "Lambda log level"
  type        = string
  default     = "INFO"

  validation {
    condition     = contains(["DEBUG", "INFO", "WARNING", "ERROR"], var.log_level)
    error_message = "Log level must be DEBUG, INFO, WARNING, or ERROR."
  }
}

variable "log_retention_days" {
  description = "CloudWatch log retention in days"
  type        = number
  default     = 30
}

# variable "subnet_ids" {
#   description = "Subnet IDs for Lambda VPC (empty for no VPC)"
#   type        = list(string)
#   default     = []
# }

# variable "security_group_ids" {
#   description = "Security group IDs for Lambda VPC"
#   type        = list(string)
#   default     = []
# }

variable "create_alarms" {
  description = "Create CloudWatch alarms"
  type        = bool
  default     = false
}

variable "sns_topic_arns" {
  description = "SNS topic ARNs for alarms"
  type        = list(string)
  default     = []
}

variable "region" {
  description = "AWS Region"
  type        = string
  default     = "ap-southeast-7"
}
