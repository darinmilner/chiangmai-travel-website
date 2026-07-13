locals {
  # github_oidc_url = "https://token.actions.githubusercontent.com"
  # # oidc_provider_arn = coalesce(
  # #   try(data.aws_iam_openid_connect_provider.github.arn, null),
  # #   try(aws_iam_openid_connect_provider.github[0].arn, null)
  # # )
  # github_oidc_exists = length([
  #   for arn in data.aws_iam_openid_connect_providers.all.arns :
  #   arn if can(regex("token.actions.githubusercontent.com", arn))
  # ]) > 0
  # existing_github_oidc_arns = [
  #   for arn in data.aws_iam_openid_connect_providers.all.arns :
  #   arn if can(regex("token.actions.githubusercontent.com", arn))
  # ]
  # github_oidc_arn = (
  #   local.github_oidc_exists ?
  #   local.existing_github_oidc_arns[0] :
  #   aws_iam_openid_connect_provider.github[0].arn
  # )
  app_name_lower = lower(var.app_name)
  ecs_task_policy_statements = [
    {
      sid    = "ReadFromS3"
      effect = "Allow"
      actions = [
        "s3:GetObject",
        "s3:ListBucket"
      ]
      resources = [
        var.bucket_arn,
        "${var.bucket_arn}/*"
      ]
    },
    # TODO: Add S3 Key Arn
    # {
    #   sid    = "DecryptSecrets"
    #   effect = "Allow"
    #   actions = [
    #     "kms:Decrypt"
    #   ]
    #   resources = ["arn:aws:kms:us-east-1:123456789012:key/abc12345-..."]
    # }
  ]

  tags = merge(var.common_tags, {
    Policy = "Custom ECS Policy"
  })
}
