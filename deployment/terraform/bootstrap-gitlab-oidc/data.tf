# Get current AWS account details
data "aws_caller_identity" "current" {}

# Get current AWS region
data "aws_region" "current" {}
