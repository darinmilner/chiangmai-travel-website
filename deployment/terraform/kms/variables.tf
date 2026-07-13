variable "environment" {
  description = "Environment name (e.g. dev, staging, prod)"
  type        = string
}

variable "app_name" {
  description = "Application name"
  type        = string
}

variable "kms_keys" {
  description = <<EOF
A map of KMS keys to create.
Key = logical name (e.g. 'terraform', 'lambda', 'rds')
Value = object with optional fields:
{
  description = "Purpose of the key",
  enable_rotation = true|false
}
EOF
  type = map(object({
    description     = optional(string)
    enable_rotation = optional(bool, true)
  }))
}

variable "create_keys" {
  description = "Whether to create keys (set to false if keys already exist or don't need to be created)"
  type        = bool
  default     = false
}
