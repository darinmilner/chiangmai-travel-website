# IAM Role for Lambda
resource "aws_iam_role" "lambda_role" {
  name = "${var.project_name}-lambda-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

# IAM Policy for Lambda (CloudWatch Logs)
resource "aws_iam_policy" "lambda_logs_policy" {
  name = "${var.project_name}-lambda-logs-policy"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "arn:aws:logs:*:*:*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_logs_attach" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = aws_iam_policy.lambda_logs_policy.arn
}

# Attach SES policy (from SES module)
resource "aws_iam_role_policy_attachment" "lambda_ses_attach" {
  count      = var.ses_iam_policy_arn != "" ? 1 : 0
  role       = aws_iam_role.lambda_role.name
  policy_arn = var.ses_iam_policy_arn
}
