# --- GitHub Actions OIDC Role (for CI/CD) ---
resource "aws_iam_role" "github_actions_role" {
  name = "${local.app_name_lower}-github-actions-role-${var.environment}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Federated = aws_iam_openid_connect_provider.github.arn
        }
        Action = "sts:AssumeRoleWithWebIdentity"
        Condition = {
          StringEquals = {
            "token.actions.githubusercontent.com:aud" = "sts.amazonaws.com"
            # Only allow this specific repo to assume the role
            "token.actions.githubusercontent.com:sub" = "repo:${var.github_org}/${var.github_repo}:ref:refs/heads/main"
          }
        }
      }
    ]
  })

  tags = merge(var.common_tags, {
    Role = "GitHub Actions"
  })
}

# --- ECS Execution Role ---
# resource "aws_iam_role" "ecs_execution_role" {
#   name = "${local.app_name_lower}-ecs-execution-role-${var.environment}"

#   assume_role_policy = jsonencode({
#     Version = "2012-10-17"
#     Statement = [{
#       Effect = "Allow"
#       Principal = {
#         Service = "ecs-tasks.amazonaws.com"
#       }
#       Action = "sts:AssumeRole"
#     }]
#   })

#   tags = merge(var.common_tags, {
#     Role = "ECS Execution"
#   })
# }

# resource "aws_iam_role" "ecs_task_role" {
#   name = "${local.app_name_lower}-ecs-task-role-${var.environment}"

#   assume_role_policy = jsonencode({
#     Version = "2012-10-17"
#     Statement = [{
#       Effect = "Allow"
#       Principal = {
#         Service = "ecs-tasks.amazonaws.com"
#       }
#       Action = "sts:AssumeRole"
#     }]
#   })

#   tags = merge(var.common_tags, {
#     Role = "ECS Task"
#   })
# }

# resource "aws_iam_policy" "ecs_task_policy" {
#   name   = "${local.app_name_lower}-ecs-task-policy-${var.environment}"
#   policy = data.aws_iam_policy_document.ecs_task_custom.json
# }

# resource "aws_iam_role_policy_attachment" "ecs_task_policy_attach" {
#   role       = aws_iam_role.ecs_task_role.name
#   policy_arn = aws_iam_policy.ecs_task_policy.arn
# }

# resource "aws_iam_role_policy_attachment" "ecs_execution_policy" {
#   role       = aws_iam_role.ecs_execution_role.name
#   policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
# }

resource "aws_iam_policy" "github_actions_inline" {
  name        = "${local.app_name_lower}-github-actions-policy-${var.environment}"
  description = "Permissions for GitHub Actions CI/CD to deploy and push to ECR"
  policy      = data.aws_iam_policy_document.github_actions_policy.json
}

resource "aws_iam_role_policy_attachment" "github_actions_attachment" {
  role       = aws_iam_role.github_actions_role.name
  policy_arn = aws_iam_policy.github_actions_inline.arn
}
