# SES Module (Singapore region)
module "ses" {
  source = "./ses"
  providers = {
    aws = aws.singapore
  }

  project_name          = var.project_name
  singapore_region      = var.singapore_region
  ses_domain            = var.ses_domain
  ses_source_email      = var.ses_source_email
  ses_destination_email = var.ses_destination_email

  create_receipt_rules   = false
  create_route53_records = var.create_route53_records
  route53_zone_id        = var.route53_zone_id

  tags = var.tags
}

# Lambda Module (Bangkok region)
module "lambda" {
  source = "./lambda"
  providers = {
    aws = aws.bangkok
  }

  project_name    = var.project_name
  bangkok_region  = var.bangkok_region
  lambda_zip_path = var.lambda_zip_path

  ses_source_email      = module.ses.ses_source_email
  ses_destination_email = module.ses.ses_destination_email
  ses_region            = var.singapore_region
  ses_iam_policy_arn    = module.ses.ses_iam_policy_arn

  max_email_size_kb     = var.max_email_size_kb
  rate_limit_per_minute = var.rate_limit_per_minute
  log_retention_days    = var.log_retention_days

  s3_bucket = data.aws_s3_bucket.notifications_bucket.bucket
}

# API Gateway Module (Bangkok region)
module "api_gateway" {
  source = "./api-gateway"
  providers = {
    aws = aws.bangkok
  }

  project_name         = var.project_name
  environment          = var.environment
  lambda_arn           = module.lambda.lambda_function_arn
  lambda_function_name = module.lambda.lambda_function_name
  allowed_origins      = var.allowed_origins
  log_retention_days   = var.log_retention_days

  tags = var.tags
}
