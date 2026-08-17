#!/bin/bash
# ONLY Package Lambda layer - NO DEPLOYMENT
set -e

LAYER_PATH="${1:-layers/common}"
ARTIFACTS_DIR="${2:-artifacts}"
COMMIT_SHA="${CI_COMMIT_SHORT_SHA:-local}"

echo "📦 Packaging layer from ${LAYER_PATH}"

cd "${LAYER_PATH}"

# Run package.py if it exists
if [ -f "package.py" ]; then
    python package.py
fi

# Copy layer.zip to artifacts
if [ -f "layer.zip" ]; then
    mkdir -p "${ARTIFACTS_DIR}"
    cp layer.zip "${ARTIFACTS_DIR}/layer-${COMMIT_SHA}.zip"
    echo "✅ Layer packaged: ${ARTIFACTS_DIR}/layer-${COMMIT_SHA}.zip"
else
    echo "❌ layer.zip not found"
    exit 1
fi