variable "app_name" {
  type = string
}

variable "use_kms" {
  type    = bool
  default = false
}

variable "bucket_arn" {
  type = string
}

variable "kms_key_arn" {
  type    = string
  default = null
}

variable "github_repo" {
  description = "GitHub repository (e.g. org/repo)"
  type        = string
}

variable "environment" {
  description = "Deployment Environment"
  type        = string
}

variable "common_tags" {
  description = "Common tags for all resources"
  type        = map(string)
}

variable "github_org" {
  description = "Github Organization"
  type        = string
  default     = "sharedrive-cnx"
}
