#!/bin/bash
# ONLY Package Lambda function - NO DEPLOYMENT
set -e

LAMBDA_NAME="${1}"
LAMBDA_PATH="${2:-lambdas/${1}}"
ARTIFACTS_DIR="${3:-artifacts}"
COMMIT_SHA="${CI_COMMIT_SHORT_SHA:-local}"

echo "📦 Packaging Lambda: ${LAMBDA_NAME}"

cd "${LAMBDA_PATH}"

# Create package directory
mkdir -p package

# Install dependencies
if [ -f "requirements.txt" ]; then
    echo "Installing dependencies..."
    pip install -r requirements.txt -t package/
fi

# Copy source code
if [ -d "src" ]; then
    echo "Copying source code..."
    cp -r src/* package/
fi

# Create zip
mkdir -p "${ARTIFACTS_DIR}"
cd package
zip -r9 "${ARTIFACTS_DIR}/${LAMBDA_NAME}-${COMMIT_SHA}.zip" .
cd ..

echo "✅ Lambda packaged: ${ARTIFACTS_DIR}/${LAMBDA_NAME}-${COMMIT_SHA}.zip"

# Cleanup
rm -rf package