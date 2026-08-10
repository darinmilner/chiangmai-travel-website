output "layer_arn" {
  description = "ARN of the Lambda layer version"
  value       = aws_lambda_layer_version.shared_layer.arn
}

output "layer_version" {
  description = "Version number of the Lambda layer"
  value       = aws_lambda_layer_version.shared_layer.version
}

output "layer_arn_with_version" {
  description = "ARN of the Lambda layer with version suffix"
  value       = aws_lambda_layer_version.shared_layer.layer_arn
}

output "secret_access_policy_arn" {
  description = "ARN of the secret access policy"
  value       = try(aws_iam_policy.secret_access[0].arn, null)
}
