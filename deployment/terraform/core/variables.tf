variable "environment" {
  description = "Environment name (e.g. dev, staging, beta, prod)"
  type        = string
  default     = "beta"
  validation {
    condition     = contains(["dev", "staging", "beta", "prod"], var.environment)
    error_message = "Environment must be one of: dev, staging, beta, prod"
  }
}

variable "app_name" {
  description = "Application name"
  type        = string
  default     = "ChiangmaiVilla"
}

variable "region" {
  description = "AWS Region for deployment"
  type        = string
  default     = "ap-southeast-7"
}

variable "github_repo_name" {
  description = "Role for Github Actions"
  type        = string
  default     = "darinmilner/chiangmai-travel-website"
}
