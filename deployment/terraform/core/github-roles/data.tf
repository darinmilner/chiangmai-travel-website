data "aws_caller_identity" "current" {}

# --- Policy for GitHub Actions Role ---
data "aws_iam_policy_document" "github_actions_policy" {
  statement {
    sid    = "ECRPushAccess"
    effect = "Allow"
    actions = [
      "ecr:GetAuthorizationToken",
      "ecr:BatchCheckLayerAvailability",
      "ecr:PutImage",
      "ecr:InitiateLayerUpload",
      "ecr:UploadLayerPart",
      "ecr:CompleteLayerUpload"
    ]
    resources = ["*"]
  }

  statement {
    sid    = "TerraformStateAccess"
    effect = "Allow"
    actions = [
      "s3:GetObject",
      "s3:PutObject",
      "s3:DeleteObject",
      "s3:ListBucket"
    ]
    resources = ["*"]
  }

  statement {
    sid    = "KMSAccessOptional"
    effect = "Allow"
    actions = [
      "kms:Encrypt",
      "kms:Decrypt",
      "kms:ReEncrypt*",
      "kms:GenerateDataKey*",
      "kms:DescribeKey"
    ]
    resources = ["*"]
  }
}

# #Custom policy
# data "aws_iam_policy_document" "ecs_task_custom" {
#   dynamic "statement" {
#     for_each = local.ecs_task_policy_statements
#     content {
#       sid       = lookup(statement.value, "sid", null)
#       effect    = lookup(statement.value, "effect", "Allow")
#       actions   = lookup(statement.value, "actions", [])
#       resources = lookup(statement.value, "resources", [])

#       # Optional condition support (if you ever add one)
#       # condition = lookup(statement.value, "condition", null)
#     }
#   }
# }
