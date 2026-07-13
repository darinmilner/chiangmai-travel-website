# SES Domain Identity
resource "aws_ses_domain_identity" "main" {
  domain = var.ses_domain
}

# SES Domain DKIM
resource "aws_ses_domain_dkim" "main" {
  domain = aws_ses_domain_identity.main.domain
}

# SES Domain Mail From
resource "aws_ses_domain_mail_from" "main" {
  domain           = aws_ses_domain_identity.main.domain
  mail_from_domain = "bounce.${var.ses_domain}"
}

# SES Email Identity (for testing/verification)
resource "aws_ses_email_identity" "sender" {
  count = var.ses_source_email != "" ? 1 : 0
  email = var.ses_source_email
}

resource "aws_ses_email_identity" "recipient" {
  count = var.ses_destination_email != "" ? 1 : 0
  email = var.ses_destination_email
}

# SES Configuration Set (for event publishing)
resource "aws_ses_configuration_set" "main" {
  name = "${var.project_name}-config-set"

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
  count         = var.create_receipt_rules ? 1 : 0
  rule_set_name = "${var.project_name}-rules"
}

# SES Receipt Rule - Store in S3 (optional)
resource "aws_ses_receipt_rule" "store_in_s3" {
  count = var.create_receipt_rules && var.s3_bucket_name != "" ? 1 : 0

  name          = "${var.project_name}-store-in-s3"
  rule_set_name = aws_ses_receipt_rule_set.main[0].rule_set_name
  recipients    = [var.ses_domain]
  enabled       = true
  scan_enabled  = true

  s3_action {
    bucket_name = var.s3_bucket_name
    position    = 1
  }
}

# SES Receipt Rule - Lambda Action (optional)
resource "aws_ses_receipt_rule" "lambda_action" {
  count = var.create_receipt_rules && var.lambda_arn != "" ? 1 : 0

  name          = "${var.project_name}-lambda-action"
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

# SES Verified Domain SPF Record
resource "aws_route53_record" "ses_spf" {
  count = var.create_route53_records ? 1 : 0

  zone_id = var.route53_zone_id
  name    = var.ses_domain
  type    = "TXT"
  ttl     = 300
  records = [
    "v=spf1 include:amazonses.com ~all"
  ]
}

# SES DKIM Route53 Records
resource "aws_route53_record" "ses_dkim" {
  count = var.create_route53_records ? length(aws_ses_domain_dkim.main.dkim_tokens) : 0

  zone_id = var.route53_zone_id
  name    = "${element(aws_ses_domain_dkim.main.dkim_tokens, count.index)}._domainkey.${var.ses_domain}"
  type    = "CNAME"
  ttl     = 300
  records = [
    "${element(aws_ses_domain_dkim.main.dkim_tokens, count.index)}.dkim.amazonses.com"
  ]
}

# SES Mail From Route53 Record
resource "aws_route53_record" "ses_mail_from" {
  count = var.create_route53_records ? 1 : 0

  zone_id = var.route53_zone_id
  name    = "bounce.${var.ses_domain}"
  type    = "MX"
  ttl     = 300
  records = [
    "10 feedback-smtp.${var.singapore_region}.amazonses.com"
  ]
}

# SES Mail From SPF Record
resource "aws_route53_record" "ses_mail_from_spf" {
  count = var.create_route53_records ? 1 : 0

  zone_id = var.route53_zone_id
  name    = "bounce.${var.ses_domain}"
  type    = "TXT"
  ttl     = 300
  records = [
    "v=spf1 include:amazonses.com ~all"
  ]
}

# SES IAM Policy for Lambda
resource "aws_iam_policy" "ses_lambda_policy" {
  count = var.create_lambda_policy ? 1 : 0

  name        = "${var.project_name}-ses-lambda-policy"
  description = "Policy for Lambda to use SES"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "ses:SendEmail",
          "ses:SendRawEmail",
          "ses:GetSendQuota",
          "ses:GetSendStatistics"
        ]
        Resource = "*"
      }
    ]
  })
}
