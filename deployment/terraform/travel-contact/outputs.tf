output "api_endpoint" {
  description = "API Gateway endpoint URL"
  value       = module.api_gateway.api_endpoint
}

output "lambda_function_name" {
  description = "Lambda function name"
  value       = module.lambda.lambda_function_name
}

output "ses_domain" {
  description = "SES verified domain"
  value       = module.ses.ses_domain_identity_arn
}

output "ses_source_email" {
  description = "SES source email"
  value       = var.ses_source_email
  sensitive   = true
}

output "ses_destination_email" {
  description = "SES destination email"
  value       = var.ses_destination_email
  sensitive   = true
}

output "ses_configuration_set" {
  description = "SES configuration set name"
  value       = module.ses.ses_configuration_set_name
}

# DKIM tokens for manual DNS setup
output "ses_dkim_tokens" {
  description = "DKIM tokens for manual DNS setup"
  value       = module.ses.ses_dkim_tokens
}
