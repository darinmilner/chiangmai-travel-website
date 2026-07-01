variable "region" {
  description = "Region to deploy resources"
  type        = string
  default     = "ap-southeast-7"
}

variable "num_subnets" {
  description = "Number of subnets to deploy"
  type        = number
  default     = 2
}

variable "environment" {
  description = "Deployment environment"
  type        = string
  default     = "beta"
}

variable "allowed_ips" {
  description = "Allowed IPs to access the network"
  type        = list(string)
  default     = ["0.0.0.0/0"]
}

variable "vpc_cidr" {
  description = "Main VPC cidr block"
  type        = string
  default     = "10.0.0.0/16"
}
