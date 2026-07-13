terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

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

# Lambda Function
resource "aws_lambda_function" "contact_form" {
  filename      = var.lambda_zip_path
  function_name = "${var.project_name}-contact-form"
  role          = aws_iam_role.lambda_role.arn
  handler       = "handler.lambda_handler"
  runtime       = "python3.11"
  timeout       = 30
  memory_size   = 256

  environment {
    variables = {
      SES_SOURCE_EMAIL      = var.ses_source_email
      SES_DESTINATION_EMAIL = var.ses_destination_email
      SES_REGION            = var.ses_region     # Singapore region
      AWS_REGION            = var.bangkok_region # Bangkok region
      MAX_EMAIL_SIZE_KB     = var.max_email_size_kb
      RATE_LIMIT_PER_MINUTE = var.rate_limit_per_minute
    }
  }

  source_code_hash = filebase64sha256(var.lambda_zip_path)

  tags = var.tags
}

# CloudWatch Log Group
resource "aws_cloudwatch_log_group" "lambda_logs" {
  name              = "/aws/lambda/${aws_lambda_function.contact_form.function_name}"
  retention_in_days = var.log_retention_days
}
