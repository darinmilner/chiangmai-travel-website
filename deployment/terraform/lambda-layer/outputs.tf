output "layer_arn" {
  description = "ARN of the Lambda layer version"
  value       = aws_lambda_layer_version.shared_layer.arn
}

output "layer_version" {
  description = "Version number of the Lambda layer"
  value       = aws_lambda_layer_version.shared_layer.version
}
