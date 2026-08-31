#!/bin/bash
# Setup AWS OIDC credentials for Terraform and AWS SDKs
set -e

if [ -z "${AWS_JWT_TOKEN}" ]; then
    echo "❌ Error: AWS_JWT_TOKEN is not set. Ensure id_tokens is configured in GitLab CI."
    exit 1
fi

if [ -z "${AWS_ROLE_ARN}" ]; then
    echo "❌ Error: AWS_ROLE_ARN is not set. Please define AWS_ROLE_ARN in your CI variables."
    exit 1
fi

# Write JWT token to a secure temporary file
TOKEN_FILE="/tmp/aws_jwt_token"
echo "${AWS_JWT_TOKEN}" > "${TOKEN_FILE}"
chmod 600 "${TOKEN_FILE}"

# Export AWS Web Identity environment variables for Terraform backend & provider
export AWS_WEB_IDENTITY_TOKEN_FILE="${TOKEN_FILE}"
export AWS_ROLE_ARN="${AWS_ROLE_ARN}"
export AWS_REGION="${AWS_REGION:-ap-southeast-7}"
export AWS_DEFAULT_REGION="${AWS_REGION:-ap-southeast-7}"

echo "✅ AWS OIDC environment configured for role: ${AWS_ROLE_ARN}"
