output "function_name" {
  description = "Lambda function name"
  value       = aws_lambda_function.image_processor.function_name
}

output "function_arn" {
  description = "Lambda function ARN"
  value       = aws_lambda_function.image_processor.arn
}

output "function_invoke_arn" {
  description = "Lambda function invoke ARN"
  value       = aws_lambda_function.image_processor.invoke_arn
}

output "function_qualified_arn" {
  description = "Lambda function qualified ARN (with version)"
  value       = aws_lambda_function.image_processor.qualified_arn
}

output "function_version" {
  description = "Lambda function version"
  value       = aws_lambda_function.image_processor.version
}

output "log_group_name" {
  description = "CloudWatch log group name"
  value       = aws_cloudwatch_log_group.lambda.name
}

output "iam_role_arn" {
  description = "IAM role ARN for the lambda"
  value       = aws_iam_role.lambda_role.arn
}

output "iam_role_name" {
  description = "IAM role name for the lambda"
  value       = aws_iam_role.lambda_role.name
}
