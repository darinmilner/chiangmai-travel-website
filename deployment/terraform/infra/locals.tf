locals {
  azs              = data.aws_availability_zones.azs.names
  http_port        = 80
  https_port       = 443
  http_protocol    = "HTTP"
  ssh_port         = 22
  all_routes_open  = "0.0.0.0/0"
  api_service_port = 8000
  short_region     = replace(var.region, "-", "")
}