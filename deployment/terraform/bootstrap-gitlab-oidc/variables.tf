variable "project_id" {
  description = "GitLab project ID for OIDC authentication"
  type        = string

  validation {
    condition     = can(regex("^[0-9]+$", var.project_id))
    error_message = "Project ID must be a numeric value."
  }
}

variable "gitlab_audience" {
  description = "GitLab OIDC audience (issuer URL)"
  type        = string
  default     = "https://gitlab.com"

  validation {
    condition     = can(regex("^https://", var.gitlab_audience))
    error_message = "Audience must be a valid HTTPS URL."
  }
}

variable "environment" {
  description = "Environment name for naming conventions"
  type        = string
  default     = "dev"

  validation {
    condition     = contains(["dev", "staging", "prod", "beta"], var.environment)
    error_message = "Environment must be one of: dev, staging, prod, beta."
  }
}

variable "role_name" {
  description = "Name of the IAM role to create"
  type        = string
  default     = "gitlab-oidc-role"
}

variable "policy_arns" {
  description = "List of IAM policy ARNs to attach to the role"
  type        = list(string)
  default     = []
}

variable "inline_policies" {
  description = "Map of inline policy names to policy documents"
  type        = map(string)
  default     = {}
}

variable "account_id" {
  description = "AWS Account ID (optional, will use data source if not provided)"
  type        = string
  default     = null
}

variable "create_oidc_provider" {
  description = "Whether to create the OIDC provider (set to false if it already exists)"
  type        = bool
  default     = true
}

variable "max_session_duration" {
  description = "Maximum session duration for the role in seconds"
  type        = number
  default     = 3600

  validation {
    condition     = var.max_session_duration >= 3600 && var.max_session_duration <= 43200
    error_message = "Session duration must be between 3600 and 43200 seconds."
  }
}
