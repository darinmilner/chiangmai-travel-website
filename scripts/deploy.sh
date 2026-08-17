#!/bin/bash
# Deploy Lambda components
set -e

COMPONENT="${1:-all}"
ENVIRONMENT="${2:-dev}"
ARTIFACTS_DIR="${3:-artifacts}"
DRY_RUN="${4:-false}"

echo "🚀 Deploying ${COMPONENT} to ${ENVIRONMENT}"

# Setup OIDC auth (will use environment variables)
if [ -n "${CI_JOB_JWT_V2}" ] && [ -n "${AWS_ROLE_ARN}" ]; then
    echo "Using OIDC authentication"
    echo "${CI_JOB_JWT_V2}" > /tmp/web_identity_token
    export AWS_WEB_IDENTITY_TOKEN_FILE=/tmp/web_identity_token
    export AWS_ROLE_ARN="${AWS_ROLE_ARN}"
    export AWS_SESSION_TOKEN=""
    export AWS_ACCESS_KEY_ID=""
    export AWS_SECRET_ACCESS_KEY=""

    # Verify auth
    aws sts get-caller-identity
fi

# Function to deploy layer
deploy_layer() {
    local zip_file="${ARTIFACTS_DIR}/layer-${CI_COMMIT_SHORT_SHA:-local}.zip"

    if [ ! -f "${zip_file}" ]; then
        echo "❌ Layer zip not found: ${zip_file}"
        return 1
    fi

    if [ "${DRY_RUN}" = "true" ]; then
        echo "🔍 DRY RUN: Would publish layer common-layer"
        return 0
    fi

    echo "📤 Publishing layer..."
    aws lambda publish-layer-version \
        --layer-name common-layer \
        --zip-file "fileb://${zip_file}" \
        --compatible-runtimes python3.11 \
        --description "Layer ${CI_COMMIT_SHORT_SHA}"

    echo "✅ Layer published"
}

# Function to deploy Lambda
deploy_lambda() {
    local name="${1}"
    local zip_file="${ARTIFACTS_DIR}/${name}-${CI_COMMIT_SHORT_SHA:-local}.zip"
    local function_name="${name}-${ENVIRONMENT}"

    if [ ! -f "${zip_file}" ]; then
        echo "❌ Lambda zip not found: ${zip_file}"
        return 1
    fi

    if [ "${DRY_RUN}" = "true" ]; then
        echo "🔍 DRY RUN: Would update ${function_name}"
        return 0
    fi

    echo "📤 Updating ${function_name}..."
    aws lambda update-function-code \
        --function-name "${function_name}" \
        --zip-file "fileb://${zip_file}" \
        --publish

    echo "✅ ${function_name} updated"
}

# Deploy based on component
case "${COMPONENT}" in
    layer)
        deploy_layer
        ;;
    ses)
        deploy_lambda "ses"
        ;;
    image-processor)
        deploy_lambda "image-processor"
        ;;
    all)
        deploy_layer
        deploy_lambda "ses"
        deploy_lambda "image-processor"
        ;;
    *)
        echo "❌ Unknown component: ${COMPONENT}"
        echo "Usage: $0 {layer|ses|image-processor|all} [environment] [artifacts-dir] [dry-run]"
        exit 1
        ;;
esac

echo "✅ Deployment complete!"