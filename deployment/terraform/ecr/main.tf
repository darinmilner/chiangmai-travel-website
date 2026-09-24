resource "aws_ecr_repository" "travel_api" {
  name                 = "${local.app_name_lower}-app-${local.environment}-${local.short_region}"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  tags = {
    Environment = local.environment
    Project     = local.app_name
  }
}

# Optional: Automatically cleanup untagged or old images to save storage costs
resource "aws_ecr_lifecycle_policy" "travel_api_policy" {
  repository = aws_ecr_repository.travel_api.name

  policy = jsonencode({
    rules = [
      {
        rulePriority = 1
        description  = "Keep last 10 images"
        selection = {
          tagStatus   = "any"
          countType   = "imageCountMoreThan"
          countNumber = 10
        }
        action = {
          type = "expire"
        }
      }
    ]
  })
}
