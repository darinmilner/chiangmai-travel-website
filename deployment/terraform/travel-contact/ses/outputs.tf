# Outputs
output "ses_domain_identity_arn" {
  value = aws_ses_domain_identity.main.arn
}

output "ses_dkim_tokens" {
  value = aws_ses_domain_dkim.main.dkim_tokens
}

output "ses_configuration_set_name" {
  value = aws_ses_configuration_set.main.name
}

output "ses_iam_policy_arn" {
  value = aws_iam_policy.ses_lambda_policy.arn
}

output "ses_source_email" {
  value = aws_ses_email_identity.sender
}
