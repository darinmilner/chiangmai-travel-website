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
