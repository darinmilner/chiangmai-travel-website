resource "aws_lb" "app_alb" {
  name               = lower("${var.app_name}-app-alb-${var.short_region}")
  internal           = false
  load_balancer_type = "application"
  subnets            = [for subnet in aws_subnet.public_subnet : subnet.id]
  security_groups    = [aws_security_group.alb_sg.id]

  # TODO: Add Access Logs
  tags = merge(var.common_tags, {
    Name = "RoofInLeaf ALB"
  })
}

resource "aws_lb_listener" "alb_listener" {
  load_balancer_arn = aws_lb.app_alb.arn
  port              = local.http_port
  protocol          = local.http_protocol

  # for testing if ALB Works
  default_action {
    type = "fixed-response"

    fixed_response {
      status_code  = "200"
      content_type = "text/plain"
      message_body = "ALB is working"
    }
  }
}
