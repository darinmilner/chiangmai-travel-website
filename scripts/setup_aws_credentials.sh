#!/usr/bin/env bash
set -e

if [ -z "$AWS_JWT_TOKEN" ]; then
  echo "❌ Error: AWS_JWT_TOKEN is not defined in the environment."
  exit 1
fi

# Write JWT token to file for AWS SDK / Terraform
TOKEN_DIR="/tmp/aws"
mkdir -p "$TOKEN_DIR"
echo "$AWS_JWT_TOKEN" > "$TOKEN_DIR/token"

# Export standard AWS SDK variables
export AWS_WEB_IDENTITY_TOKEN_FILE="$TOKEN_DIR/token"
export AWS_ROLE_ARN="${AWS_ROLE_ARN}"
export AWS_DEFAULT_REGION="${AWS_REGION:-ap-southeast-7}"
export AWS_REGION="${AWS_REGION:-ap-southeast-7}"

echo "✅ AWS OIDC environment configured for role: ${AWS_ROLE_ARN}"