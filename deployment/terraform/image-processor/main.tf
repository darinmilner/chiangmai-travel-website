# Lambda Function - Image Processor
resource "aws_lambda_function" "image_processor" {
  # filename         = data.archive_file.lambda_zip.output_path
  filename         = var.lambda_zip_path
  source_code_hash = filebase64sha256(var.lambda_zip_path)
  function_name    = "${local.app_name_lower}-image-processor-${var.environment}"
  role             = aws_iam_role.lambda_role.arn
  handler          = "index.lambda_handler"
  runtime          = "python3.13"
  timeout          = var.lambda_timeout
  memory_size      = var.lambda_memory
  publish          = true

  environment {
    variables = {
      S3_BUCKET      = var.bucket_id
      S3_PREFIX      = var.s3_prefix
      CLOUDFRONT_URL = "https://${data.terraform_remote_state.cloudfront.outputs.cloudfront_domain_name}"
      THUMBNAIL_SIZE = var.thumbnail_size
      MEDIUM_SIZE    = var.medium_size
      CAROUSEL_SIZE  = var.carousel_size
      QUALITY        = tostring(var.image_quality)
      LOG_LEVEL      = var.log_level
      ENVIRONMENT    = var.environment
    }
  }

  vpc_config {
    subnet_ids         = var.subnet_ids
    security_group_ids = var.security_group_ids
  }

  depends_on = [
    aws_cloudwatch_log_group.lambda,
    data.archive_file.lambda_zip
  ]

  tags = local.tags
}

# CloudWatch Logs
resource "aws_cloudwatch_log_group" "lambda" {
  name              = "/aws/lambda/${local.app_name_lower}-image-processor"
  retention_in_days = var.log_retention_days
}

# S3 Event Notification for Lambda
resource "aws_s3_bucket_notification" "images" {
  bucket = var.bucket_id

  lambda_function {
    lambda_function_arn = aws_lambda_function.image_processor.arn
    events              = ["s3:ObjectCreated:*"]
    filter_prefix       = var.s3_prefix
    filter_suffix       = var.image_extensions_filter
  }

  depends_on = [
    aws_lambda_permission.allow_s3
  ]
}

# Lambda permission for S3
resource "aws_lambda_permission" "allow_s3" {
  statement_id  = "AllowS3Invocation"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.image_processor.function_name
  principal     = "s3.amazonaws.com"
  source_arn    = data.aws_s3_bucket.image_bucket.arn
}
