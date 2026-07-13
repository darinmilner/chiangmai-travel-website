# Outputs
output "api_endpoint" {
  value = "${aws_apigatewayv2_api.http_api.api_endpoint}/${var.environment}/contact"
}

output "api_id" {
  value = aws_apigatewayv2_api.http_api.id
}

output "api_arn" {
  value = aws_apigatewayv2_api.http_api.arn
}
