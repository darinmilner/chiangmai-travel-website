output "oidc_provider_arn" {
  # value       = local.github_oidc_arn
  value       = aws_iam_openid_connect_provider.github.arn
  description = "ARN of the GitHub OIDC provider"
}

output "ecs_execution_role_arn" {
  value       = aws_iam_role.ecs_execution_role.arn
  description = "ECS execution role ARN"
}

output "ecs_task_role" {
  value       = aws_iam_role.ecs_task_role.arn
  description = "ECS task role ARN"
}

output "github_actions_role_arn" {
  value       = aws_iam_role.github_actions_role.arn
  description = "GitHub Actions role ARN"
}
