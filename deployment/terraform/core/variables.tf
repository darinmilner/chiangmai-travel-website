variable "environment" {
  description = "Environment name (e.g. dev, staging, prod)"
  type        = string
  default     = "beta"
}

variable "app_name" {
  description = "Application name"
  type        = string
  default     = "ShareDrive"
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
