# ---------------------------
# ALB Security Group
# ---------------------------
resource "aws_security_group" "alb_sg" {
  name   = "alb-security-group-${var.environment}-${var.short_region}"
  vpc_id = aws_vpc.main.id

  tags = merge(var.common_tags, {
    Name = "alb-security-group-${var.environment}-${var.short_region}"
  })
}

resource "aws_vpc_security_group_ingress_rule" "alb_ingress_http" {
  security_group_id = aws_security_group.alb_sg.id
  cidr_ipv4         = local.all_routes_open
  from_port         = local.http_port
  to_port           = local.http_port
  ip_protocol       = "tcp"
}

resource "aws_vpc_security_group_egress_rule" "alb_egress" {
  security_group_id = aws_security_group.alb_sg.id
  ip_protocol       = "-1"
  cidr_ipv4         = local.all_routes_open
}

# ---------------------------
# EC2 Security Group (App Servers)
# ---------------------------
resource "aws_security_group" "ec2_sg" {
  name        = "${var.app_name}-ec2-sg-${var.environment}-${var.short_region}"
  description = "Security group for EC2 app servers"
  vpc_id      = aws_vpc.main.id

  tags = merge(var.common_tags, {
    Name = "${var.app_name}-ec2-sg-${var.environment}-${var.short_region}"
  })
}

# Inbound: Allow HTTP traffic ONLY from the ALB (not the internet directly!)
resource "aws_vpc_security_group_ingress_rule" "ec2_ingress_http_from_alb" {
  security_group_id            = aws_security_group.ec2_sg.id
  referenced_security_group_id = aws_security_group.alb_sg.id # CRITICAL: Only ALB can talk to EC2
  from_port                    = local.http_port
  to_port                      = local.http_port
  ip_protocol                  = "tcp"
  description                  = "Allow HTTP from ALB only"
}

# Inbound: Allow SSH from trusted IPs (for debugging)
resource "aws_vpc_security_group_ingress_rule" "ec2_ingress_ssh" {
  count = var.ssh_allowed_cidrs != null ? 1 : 0

  security_group_id = aws_security_group.ec2_sg.id
  cidr_ipv4         = var.ssh_allowed_cidrs[0] # Restrict to your IP
  from_port         = local.ssh_port
  to_port           = local.ssh_port
  ip_protocol       = "tcp"
  description       = "Allow SSH from trusted IPs"
}

# Inbound: Allow health check traffic from ALB (if using a separate health check port)
resource "aws_vpc_security_group_ingress_rule" "ec2_ingress_health_check" {
  security_group_id            = aws_security_group.ec2_sg.id
  referenced_security_group_id = aws_security_group.alb_sg.id
  from_port                    = local.api_service_port
  to_port                      = local.api_service_port
  ip_protocol                  = "tcp"
  description                  = "Allow health checks from ALB"
}

# Outbound: Allow EC2 instances to talk to the internet (for updates, API calls, etc.)
resource "aws_vpc_security_group_egress_rule" "ec2_egress_all" {
  security_group_id = aws_security_group.ec2_sg.id
  ip_protocol       = "-1"
  cidr_ipv4         = local.all_routes_open
  description       = "Allow all outbound traffic"
}

# Outbound: Allow HTTPS for external API calls (e.g., AWS services, third-party APIs)
resource "aws_vpc_security_group_egress_rule" "ec2_egress_https" {
  security_group_id = aws_security_group.ec2_sg.id
  ip_protocol       = "tcp"
  from_port         = 443
  to_port           = 443
  cidr_ipv4         = local.all_routes_open
  description       = "Allow HTTPS outbound"
}

# ---------------------------
# Security Group for Lambda functions
# ---------------------------
resource "aws_security_group" "lambda" {
  name        = "${var.app_name}-lambda-sg-${var.environment}-${var.short_region}"
  description = "Security group for Lambda functions"
  vpc_id      = aws_vpc.main.id

  # Egress to everywhere (for initial setup)
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Allow HTTPS outbound for SES API calls"
  }

  tags = merge(var.common_tags, {
    Name = "${var.app_name}-lambda-sg-${var.environment}-${var.short_region}"
  })
}