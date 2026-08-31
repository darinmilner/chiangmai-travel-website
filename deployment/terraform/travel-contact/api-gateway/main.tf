# HTTP API Gateway
resource "aws_apigatewayv2_api" "http_api" {
  name          = "${local.app_name_lower}-api"
  protocol_type = "HTTP"
  description   = "Contact form API for travel website"

  cors_configuration {
    allow_origins = var.allowed_origins
    allow_methods = ["POST", "OPTIONS"]
    allow_headers = ["Content-Type", "X-Requested-With"]
    max_age       = 300
  }
}

# API Stage
resource "aws_apigatewayv2_stage" "api_stage" {
  api_id      = aws_apigatewayv2_api.http_api.id
  name        = var.environment
  auto_deploy = true

  default_route_settings {
    detailed_metrics_enabled = true
    logging_level            = "INFO"
    throttling_burst_limit   = 20
    throttling_rate_limit    = 10
  }

  access_log_settings {
    destination_arn = aws_cloudwatch_log_group.api_gateway_logs.arn
    format = jsonencode({
      requestId      = "$context.requestId"
      ip             = "$context.identity.sourceIp"
      requestTime    = "$context.requestTime"
      httpMethod     = "$context.httpMethod"
      routeKey       = "$context.routeKey"
      status         = "$context.status"
      protocol       = "$context.protocol"
      responseLength = "$context.responseLength"
    })
  }
}

# CloudWatch Log Group for API Gateway
resource "aws_cloudwatch_log_group" "api_gateway_logs" {
  name              = "/aws/apigateway/${local.app_name_lower}-api"
  retention_in_days = var.log_retention_days
}

# Lambda Integration
resource "aws_apigatewayv2_integration" "lambda_integration" {
  api_id           = aws_apigatewayv2_api.http_api.id
  integration_type = "AWS_PROXY"
  integration_uri  = var.lambda_arn
  description      = "Contact form Lambda integration"
}

# Route: POST /contact
resource "aws_apigatewayv2_route" "contact_route" {
  api_id    = aws_apigatewayv2_api.http_api.id
  route_key = "POST /contact"
  target    = "integrations/${aws_apigatewayv2_integration.lambda_integration.id}"
}

# Route: OPTIONS (for CORS preflight)
resource "aws_apigatewayv2_route" "options_route" {
  api_id    = aws_apigatewayv2_api.http_api.id
  route_key = "OPTIONS /contact"
  target    = "integrations/${aws_apigatewayv2_integration.lambda_integration.id}"
}

# Lambda Permission for API Gateway
resource "aws_lambda_permission" "api_gateway" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = var.lambda_function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.http_api.execution_arn}/*/*"
}
