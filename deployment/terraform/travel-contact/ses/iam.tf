# SES IAM Policy for Lambda
resource "aws_iam_policy" "ses_lambda_policy" {
  count = var.create_lambda_policy ? 1 : 0

  name        = "${local.app_name_lower}-ses-lambda-policy"
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