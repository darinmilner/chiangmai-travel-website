#!/bin/bash
# Package Lambda Layer into AWS-compliant python/ directory structure
set -e

LAYER_PATH="${1:-deployment/terraform/lambda-layer/shared-layer}"
ARTIFACTS_DIR="${2:-artifacts}"
LAYER_NAME="${3:-layer}"
COMMIT_SHA="${CI_COMMIT_SHORT_SHA:-local}"

if [ ! -d "${LAYER_PATH}" ]; then
    echo "❌ Error: Layer source path does not exist: ${LAYER_PATH}"
    exit 1
fi

# 1. Resolve absolute path for artifacts directory
mkdir -p "${ARTIFACTS_DIR}"
ABS_ARTIFACTS_DIR="$(cd "${ARTIFACTS_DIR}" && pwd)"

echo "📦 Packaging Layer '${LAYER_NAME}' from ${LAYER_PATH}"

cd "${LAYER_PATH}"

# 2. Prepare build directory with required AWS Lambda 'python/' subfolder
BUILD_DIR="build_layer"
rm -rf "${BUILD_DIR}"
mkdir -p "${BUILD_DIR}/python"

# Ensure temporary files are cleaned up on exit
trap 'rm -rf "${BUILD_DIR}"' EXIT

# 3. Install Python dependencies if requirements.txt exists
if [ -f "requirements.txt" ]; then
    echo "📦 Installing Layer dependencies into python/..."
    pip install -r requirements.txt -t "${BUILD_DIR}/python" --quiet
fi

# 4. Copy shared modules into python/ directory
if [ -d "python" ]; then
    echo "📄 Copying modules from python/ subfolder..."
    cp -r python/* "${BUILD_DIR}/python/"
else
    echo "📄 Copying root Python files and modules..."
    find . -maxdepth 1 ! -name '.' ! -name '..' ! -name "${BUILD_DIR}" ! -name 'requirements.txt' ! -name 'tests' ! -name '*.pyc' -exec cp -r {} "${BUILD_DIR}/python/" \;
fi

# 5. Build zip artifact directly in ARTIFACTS_DIR
cd "${BUILD_DIR}"
zip -q -r9 "${ABS_ARTIFACTS_DIR}/${LAYER_NAME}.zip" python/
cp "${ABS_ARTIFACTS_DIR}/${LAYER_NAME}.zip" "${ABS_ARTIFACTS_DIR}/${LAYER_NAME}-${COMMIT_SHA}.zip"

echo "✅ Layer successfully packaged:"
echo "   - ${ABS_ARTIFACTS_DIR}/${LAYER_NAME}.zip"
echo "   - ${ABS_ARTIFACTS_DIR}/${LAYER_NAME}-${COMMIT_SHA}.zip"
