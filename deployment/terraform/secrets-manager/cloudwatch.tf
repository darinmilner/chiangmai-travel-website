# ============================================
# CloudWatch Monitoring
# ============================================
resource "aws_cloudwatch_metric_alarm" "secret_access_alarm" {
  count = var.enable_monitoring ? length(aws_secretsmanager_secret.secrets) : 0

  alarm_name          = "${var.environment}-secret-access-${values(aws_secretsmanager_secret.secrets)[count.index].name}"
  comparison_operator = var.alarm_comparison_operator
  evaluation_periods  = var.alarm_evaluation_periods
  metric_name         = "GetSecretValue"
  namespace           = "AWS/SecretsManager"
  period              = var.alarm_period
  statistic           = "Sum"
  threshold           = var.alarm_threshold
  alarm_description   = "Secret access alarm for ${values(aws_secretsmanager_secret.secrets)[count.index].name}"
  treat_missing_data  = "notBreaching"

  dimensions = {
    SecretName = values(aws_secretsmanager_secret.secrets)[count.index].name
  }

  alarm_actions             = var.alarm_actions
  ok_actions                = var.ok_actions
  insufficient_data_actions = var.insufficient_data_actions

  tags = var.tags
}
