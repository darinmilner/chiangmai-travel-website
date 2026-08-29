#!/bin/bash
# ONLY Package Lambda layer - NO DEPLOYMENT
set -e

LAYER_PATH="${1:-layers/common}"
ARTIFACTS_DIR="${2:-artifacts}"
COMMIT_SHA="${CI_COMMIT_SHORT_SHA:-local}"

# Resolve ARTIFACTS_DIR to absolute path BEFORE changing directories
mkdir -p "${ARTIFACTS_DIR}"
ABS_ARTIFACTS_DIR="$(cd "${ARTIFACTS_DIR}" && pwd)"

echo "📦 Packaging layer from ${LAYER_PATH}"

cd "${LAYER_PATH}"

# Option 1: Custom python packaging script if provided
if [ -f "package.py" ]; then
    python package.py

# Option 2: Build standard Lambda layer structure (python/ directory)
elif [ -f "requirements.txt" ]; then
    echo "📦 Installing layer dependencies from requirements.txt..."
    rm -rf python layer.zip
    mkdir -p python
    pip install -r requirements.txt -t python/ --quiet

    echo "🤐 Zipping layer contents..."
    zip -q -r layer.zip python/
    rm -rf python
fi

# Copy layer.zip to artifacts directory
if [ -f "layer.zip" ]; then
    cp layer.zip "${ABS_ARTIFACTS_DIR}/layer.zip"
    cp layer.zip "${ABS_ARTIFACTS_DIR}/layer-${COMMIT_SHA}.zip"
    echo "✅ Layer successfully packaged: ${ABS_ARTIFACTS_DIR}/layer.zip"
else
    echo "❌ layer.zip not found and could not be built (missing requirements.txt or package.py)"
    exit 1
fi