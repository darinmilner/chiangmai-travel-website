# SES Configuration Set (for event publishing)
resource "aws_ses_configuration_set" "main" {
  provider = aws.singapore
  name     = "${local.app_name_lower}-config-set"

  delivery_options {
    tls_policy = "Require"
  }

  reputation_metrics_enabled = true

  tracking_options {
    custom_redirect_domain = var.ses_domain
  }
}

# SES Event Destination (CloudWatch)
resource "aws_ses_event_destination" "cloudwatch" {
  provider               = aws.singapore
  name                   = "${var.project_name}-cloudwatch"
  configuration_set_name = aws_ses_configuration_set.main.name

  cloudwatch_destination {
    default_value  = "default"
    dimension_name = "ses:from-domain"
    value_source   = "emailHeader"
  }

  enabled = true
  matching_types = [
    "send",
    "reject",
    "bounce",
    "complaint",
    "delivery",
    "open",
    "click"
  ]
}

# SES Receipt Rule Set
resource "aws_ses_receipt_rule_set" "main" {
  provider      = aws.singapore
  count         = var.create_receipt_rules ? 1 : 0
  rule_set_name = "${local.app_name_lower}-rules"
}

# SES Receipt Rule - Store in S3 (optional)
resource "aws_ses_receipt_rule" "store_in_s3" {
  provider = aws.singapore
  count    = var.create_receipt_rules && var.s3_bucket_name != "" ? 1 : 0

  name          = "${local.app_name_lower}-store-in-s3"
  rule_set_name = aws_ses_receipt_rule_set.main[0].rule_set_name
  recipients    = [var.ses_domain]
  enabled       = true
  scan_enabled  = true

  s3_action {
    bucket_name = "${var.s3_bucket_name}-${local.short_bangkok_region}"
    position    = 1
  }
}

# SES Receipt Rule - Lambda Action (optional)
resource "aws_ses_receipt_rule" "lambda_action" {
  provider = aws.singapore
  count    = var.create_receipt_rules && var.lambda_arn != "" ? 1 : 0

  name          = "${local.app_name_lower}-lambda-action"
  rule_set_name = aws_ses_receipt_rule_set.main[0].rule_set_name
  recipients    = [var.ses_domain]
  enabled       = true
  scan_enabled  = true

  lambda_action {
    function_arn    = var.lambda_arn
    invocation_type = "Event"
    position        = 2
  }
}