variable "layer_name" {
  description = "Name of the Lambda layer"
  type        = string
  default     = "chiangmai-villa-shared-layer"
}

variable "description" {
  description = "Description of the Lambda layer"
  type        = string
  default     = "Shared utilities for Villa Lambdas"
}

variable "filename" {
  description = "Path to the layer ZIP file"
  type        = string
  default     = "dist/villa-shared-layer.zip"
}

variable "compatible_runtimes" {
  description = "List of compatible runtimes"
  type        = list(string)
  default     = ["python3.13", "python3.14"]
}

variable "compatible_architectures" {
  description = "List of compatible architectures"
  type        = list(string)
  default     = ["x86_64", "arm64"]
}

variable "license_info" {
  description = "License information"
  type        = string
  default     = "MIT"
}

variable "skip_destroy" {
  description = "Skip destroying the layer version"
  type        = bool
  default     = false
}
