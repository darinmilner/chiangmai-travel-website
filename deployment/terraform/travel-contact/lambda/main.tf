# Lambda Function
resource "aws_lambda_function" "contact_form" {
  filename      = var.lambda_zip_path
  function_name = "${local.app_name_lower}-contact-form"
  role          = aws_iam_role.lambda_role.arn
  handler       = "handler.lambda_handler"
  runtime       = "python3.13"
  timeout       = 30
  memory_size   = 256

  environment {
    variables = {
      SES_SOURCE_EMAIL      = var.ses_source_email
      SES_REGION            = var.ses_region     # Singapore region
      AWS_REGION            = var.bangkok_region # Bangkok region
      MAX_EMAIL_SIZE_KB     = var.max_email_size_kb
      RATE_LIMIT_PER_MINUTE = var.rate_limit_per_minute
      LOG_LEVEL             = var.log_level
      ENVIRONMENT           = var.environment
      APP_NAME              = local.app_name
    }
  }

  source_code_hash = filebase64sha256(var.lambda_zip_path)
  layers = [
    data.aws_lambda_layer_version.shared.arn
  ]

  tags = local.tags
}

# CloudWatch Log Group
resource "aws_cloudwatch_log_group" "lambda_logs" {
  name              = "/aws/lambda/${aws_lambda_function.contact_form.function_name}"
  retention_in_days = var.log_retention_days
}

# S3 Event Notification for Image Processor
resource "aws_s3_bucket_notification" "images" {
  count = var.create_s3_notification ? 1 : 0

  bucket = data.aws_s3_bucket.static_bucket.bucket

  lambda_function {
    lambda_function_arn = aws_lambda_function.image_processor.arn
    events              = ["s3:ObjectCreated:*"]
    filter_prefix       = var.s3_notification_prefix
    filter_suffix       = var.environment
  }

  depends_on = [
    aws_lambda_permission.allow_s3
  ]
}

# Lambda permission for S3
resource "aws_lambda_permission" "allow_s3" {
  count = var.create_s3_notification ? 1 : 0

  statement_id  = "AllowS3Invocation"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.contact_form.function_name
  principal     = "s3.amazonaws.com"
  source_arn    = data.aws_s3_bucket.static_bucket.arn
}
