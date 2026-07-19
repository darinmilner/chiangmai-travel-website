# ============================================
# Variables for Secrets Manager Module
# ============================================

variable "secrets" {
  description = "Map of secrets to create in AWS Secrets Manager"
  type = map(object({
    value               = string
    description         = optional(string)
    rotation_days       = optional(number, 0)
    schedule_expression = optional(string)
  }))
  default   = {}
  sensitive = true

  validation {
    condition     = alltrue([for k, v in var.secrets : length(k) > 0])
    error_message = "Secret names cannot be empty."
  }
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  default     = "dev"

  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be one of: dev, staging, prod."
  }
}

variable "tags" {
  description = "Tags to apply to all resources"
  type        = map(string)
  default = {
    Project   = "default-project"
    ManagedBy = "Terraform"
    Service   = "SecretsManager"
  }
}

variable "recovery_window_days" {
  description = "Number of days to retain secrets after deletion (7-30)"
  type        = number
  default     = 30

  validation {
    condition     = var.recovery_window_days >= 7 && var.recovery_window_days <= 30
    error_message = "Recovery window days must be between 7 and 30."
  }
}

variable "kms_key_id" {
  description = "KMS key ID or ARN to use for encryption. If not provided, AWS managed key is used."
  type        = string
  default     = null
}

# IAM Configuration
variable "create_iam_policy" {
  description = "Whether to create an IAM policy for secret access"
  type        = bool
  default     = true
}

variable "create_iam_role" {
  description = "Whether to create an IAM role for secret access"
  type        = bool
  default     = true
}

variable "create_instance_profile" {
  description = "Whether to create an EC2 instance profile"
  type        = bool
  default     = true
}

variable "iam_policy_path" {
  description = "Path for the IAM policy"
  type        = string
  default     = "/"
}

variable "iam_role_path" {
  description = "Path for the IAM role"
  type        = string
  default     = "/"
}

variable "allowed_services" {
  description = "List of AWS services allowed to assume the IAM role"
  type        = list(string)
  default = [
    "ec2.amazonaws.com",
    "lambda.amazonaws.com",
    "ecs-tasks.amazonaws.com",
    "eks.amazonaws.com"
  ]
}

# Rotation Configuration
variable "rotation_lambda_arn" {
  description = "ARN of the Lambda function for secret rotation"
  type        = string
  default     = null
}

# Monitoring Configuration
variable "enable_monitoring" {
  description = "Enable CloudWatch alarms for secret access"
  type        = bool
  default     = false
}

variable "alarm_threshold" {
  description = "Threshold for CloudWatch alarm"
  type        = number
  default     = 10
}

variable "alarm_period" {
  description = "Period for CloudWatch alarm in seconds"
  type        = number
  default     = 300
}

variable "alarm_evaluation_periods" {
  description = "Number of evaluation periods for CloudWatch alarm"
  type        = number
  default     = 2
}

variable "alarm_comparison_operator" {
  description = "Comparison operator for CloudWatch alarm"
  type        = string
  default     = "GreaterThanThreshold"
}

variable "alarm_actions" {
  description = "List of actions to take when alarm triggers (e.g., SNS topics)"
  type        = list(string)
  default     = []
}

variable "ok_actions" {
  description = "List of actions to take when alarm recovers"
  type        = list(string)
  default     = []
}

variable "insufficient_data_actions" {
  description = "List of actions to take when alarm has insufficient data"
  type        = list(string)
  default     = []
}

# SNS Configuration
variable "create_sns_topic" {
  description = "Whether to create an SNS topic for alerts"
  type        = bool
  default     = false
}

variable "alert_email" {
  description = "Email address for alert notifications"
  type        = string
  default     = ""
}
