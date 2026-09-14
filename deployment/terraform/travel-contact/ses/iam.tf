# SES IAM Policy for Lambda
resource "aws_iam_policy" "ses_lambda_policy" {
  name        = "${local.app_name_lower}-ses-lambda-policy-${local.bucket_short_region}"
  description = "Policy for Lambda to send emails using SES"

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