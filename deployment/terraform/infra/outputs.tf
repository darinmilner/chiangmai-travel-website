output "vpc_id" {
  value = aws_vpc.main.id
}

output "subnet_ids" {
  value = [for i in aws_subnet.public_subnet : i.id]
}

output "alb_dns" {
  value = aws_lb.app_alb.dns_name
}
