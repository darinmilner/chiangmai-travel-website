#!/usr/bin/env bash
set -euo pipefail

ACTION="${PIPELINE_ACTION:-deploy}"
TARGET="${DEPLOY_TARGET:-all}"

if [ "$ACTION" = "destroy" ]; then
  echo "🔥 Running DESTROY action for target: ${TARGET}"
  python "${SCRIPTS_DIR}/deploy.py" \
    --command destroy \
    --component "${TARGET}" \
    --config "${COMPONENTS_CONFIG}"

elif [ "$TARGET" = "all" ]; then
  echo "🚀 Running DEPLOY ALL action"
  python "${SCRIPTS_DIR}/deploy.py" \
    --command all \
    --config "${COMPONENTS_CONFIG}"

else
  echo "📤 Running DEPLOY action for target: ${TARGET}"
  python "${SCRIPTS_DIR}/deploy.py" \
    --command component \
    --component "${TARGET}" \
    --config "${COMPONENTS_CONFIG}"
fi