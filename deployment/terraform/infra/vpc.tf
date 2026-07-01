# ------------------------------------------------------------------------------
# VPC Flow Logs (Security & Troubleshooting)
# ------------------------------------------------------------------------------
resource "aws_flow_log" "vpc" {
  count = var.enable_flow_logs ? 1 : 0

  iam_role_arn    = aws_iam_role.flow_log[0].arn
  log_destination = aws_cloudwatch_log_group.flow_log[0].arn
  traffic_type    = "ALL"
  vpc_id          = aws_vpc.main.id

  tags = merge(var.common_tags, {
    Name = "${var.app_name}-vpc-flow-logs"
  })
}

# CloudWatch Log Group for Flow Logs
resource "aws_cloudwatch_log_group" "flow_log" {
  count = var.enable_flow_logs ? 1 : 0

  name              = "/${var.app_name}/vpc-flow-logs"
  retention_in_days = 30

  tags = merge(var.common_tags, {
    Name = "${var.app_name}-flow-logs"
  })
}

# IAM Role for Flow Logs
resource "aws_iam_role" "flow_log" {
  count = var.enable_flow_logs ? 1 : 0

  name = "${var.app_name}-flow-logs-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "vpc-flow-logs.amazonaws.com"
        }
      }
    ]
  })

  tags = merge(var.common_tags, {
    Name = "${var.app_name}-flow-logs-role"
  })
}

resource "aws_iam_policy" "flow_log" {
  count = var.enable_flow_logs ? 1 : 0

  name = "${var.app_name}-flow-logs-policy"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents",
          "logs:DescribeLogGroups",
          "logs:DescribeLogStreams"
        ]
        Effect   = "Allow"
        Resource = "*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "flow_log" {
  count = var.enable_flow_logs ? 1 : 0

  role       = aws_iam_role.flow_log[0].name
  policy_arn = aws_iam_policy.flow_log[0].arn
}