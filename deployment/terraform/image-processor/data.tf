# Data source for Secrets Manager
data "aws_secretsmanager_secret" "lambda_config" {
  count = var.secret_arn != "" ? 1 : 0
  arn   = var.secret_arn
}

data "aws_secretsmanager_secret_version" "lambda_config" {
  count     = var.secret_arn != "" ? 1 : 0
  secret_id = data.aws_secretsmanager_secret.lambda_config[0].id
}
