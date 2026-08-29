#!/bin/bash
# ONLY Package Lambda function - NO DEPLOYMENT
set -e

LAMBDA_NAME="${1}"
LAMBDA_PATH="${2:-lambdas/${1}}"
ARTIFACTS_DIR="${3:-artifacts}"
COMMIT_SHA="${CI_COMMIT_SHORT_SHA:-local}"

if [ -z "${LAMBDA_NAME}" ]; then
    echo "❌ Error: Lambda name required as first argument."
    exit 1
fi

# 1. Convert ARTIFACTS_DIR to an absolute path BEFORE changing directories
mkdir -p "${ARTIFACTS_DIR}"
ABS_ARTIFACTS_DIR="$(cd "${ARTIFACTS_DIR}" && pwd)"

echo "📦 Packaging Lambda: ${LAMBDA_NAME} from ${LAMBDA_PATH}"

cd "${LAMBDA_PATH}"

# Ensure package directory is clean
rm -rf package
mkdir -p package

# Ensure cleanup on exit or error
trap 'rm -rf package' EXIT

# 2. Install dependencies if requirements.txt exists
if [ -f "requirements.txt" ]; then
    echo "📦 Installing dependencies from requirements.txt..."
    pip install -r requirements.txt -t package/ --quiet
fi

# 3. Copy source files (handles both nested src/ and flat directory layouts)
if [ -d "src" ]; then
    echo "📄 Copying source files from src/..."
    cp -r src/* package/
else
    echo "📄 Copying root Python files and modules..."
    # Copy all files/folders except 'package' and hidden files
    find . -maxdepth 1 ! -name '.' ! -name '..' ! -name 'package' ! -name 'requirements.txt' ! -name 'tests' ! -name '*.pyc' -exec cp -r {} package/ \;
fi

# 4. Create zip archive
cd package
zip -q -r9 "${ABS_ARTIFACTS_DIR}/${LAMBDA_NAME}.zip" .
cp "${ABS_ARTIFACTS_DIR}/${LAMBDA_NAME}.zip" "${ABS_ARTIFACTS_DIR}/${LAMBDA_NAME}-${COMMIT_SHA}.zip"

echo "✅ Lambda successfully packaged:"
echo "   - ${ABS_ARTIFACTS_DIR}/${LAMBDA_NAME}.zip"
echo "   - ${ABS_ARTIFACTS_DIR}/${LAMBDA_NAME}-${COMMIT_SHA}.zip"