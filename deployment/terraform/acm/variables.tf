variable "domain_name" {
  type = string
  default = "chiangmaihalal.com"
}

variable "subdomains" {
  type    = list(string)
  default = ["www"]
}

variable "region" {
    type = string
    default = "us-east-1"
}