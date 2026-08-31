variable "vpc_cidr" {
  type        = string
  description = "VPC Cidr Block"
}

variable "num_subnets" {
  type        = number
  description = "Num subnets"
}

variable "environment" {
  description = "Deployment environment"
  type        = string
}

variable "allowed_ips" {
  description = "Allowed IP addresses"
  type        = set(string)
}

variable "common_tags" {
  description = "Common tags for all resources"
  type        = map(string)
}


variable "app_name" {
  description = "App name"
  type        = string
}

variable "region" {
  description = "Deployment region"
  type        = string
}

variable "short_region" {
  description = "Deployment region short name"
  type        = string
}

variable "ssh_allowed_cidrs" {
  description = "List of CIDR blocks allowed to SSH into EC2 instances"
  type        = list(string)
  default     = null
}

variable "health_check_port" {
  description = "Port used for ALB health checks"
  type        = number
  default     = 8080
}

variable "ssh_allowed_cidrs" {
  description = "List of CIDR blocks allowed to SSH into EC2 instances"
  type        = list(string)
  default     = null
}

variable "health_check_port" {
  description = "Port used for ALB health checks"
  type        = number
  default     = 8080
}

variable "enable_flow_logs" {
  description = "Enable VPC flow logs"
  type        = bool
  default     = True
}