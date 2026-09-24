output "ecr_repository_url" {
  value       = aws_ecr_repository.travel_api.repository_url
  description = "The URL of the ECR repository"
}
