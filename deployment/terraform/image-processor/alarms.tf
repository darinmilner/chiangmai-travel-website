
# CloudWatch Alarms
resource "aws_cloudwatch_metric_alarm" "lambda_errors" {
  count = var.create_alarms ? 1 : 0

  alarm_name          = "${local.app_name_lower}-lambda-errors-${var.environment}"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "Errors"
  namespace           = "AWS/Lambda"
  period              = 300
  statistic           = "Sum"
  threshold           = 5
  alarm_description   = "Lambda function has too many errors"
  treat_missing_data  = "notBreaching"

  dimensions = {
    FunctionName = aws_lambda_function.image_processor.function_name
  }

  alarm_actions = var.sns_topic_arns
}

resource "aws_cloudwatch_metric_alarm" "lambda_duration" {
  count = var.create_alarms ? 1 : 0

  alarm_name          = "${local.app_name_lower}-lambda-duration"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "Duration"
  namespace           = "AWS/Lambda"
  period              = 300
  statistic           = "Average"
  threshold           = var.lambda_timeout * 0.8 * 1000 # 80% of timeout in ms
  alarm_description   = "Lambda function is taking too long to execute"
  treat_missing_data  = "notBreaching"

  dimensions = {
    FunctionName = aws_lambda_function.image_processor.function_name
  }

  alarm_actions = var.sns_topic_arns
}
