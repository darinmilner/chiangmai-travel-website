# ============================================
# Variables for Secrets Manager Module
# ============================================

variable "secrets" {
  description = "Map of secrets to create in AWS Secrets Manager"
  type = map(object({
    value         = string
    description   = optional(string)
    rotation_days = optional(number, 0)
  }))
  default = {}
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "tags" {
  description = "Tags to apply to all resources"
  type        = map(string)
  default = {
    Project   = "chiang-mai-travel"
    ManagedBy = "Terraform"
    Service   = "SecretsManager"
  }
}

variable "recovery_window_days" {
  description = "Number of days to retain secrets after deletion"
  type        = number
  default     = 30
}

variable "create_iam_role" {
  description = "Whether to create an IAM role for secret access"
  type        = bool
  default     = true
}

variable "rotation_lambda_arn" {
  description = "ARN of the Lambda function for secret rotation"
  type        = string
  default     = null
}

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
