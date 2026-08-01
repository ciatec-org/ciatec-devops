#!/bin/bash
# Aggregate health checks for all CIATec services.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

rc=0

echo "=== WebGL ==="
if ! bash "$SCRIPT_DIR/check-webgl.sh"; then
  rc=1
fi

echo
echo "=== Docker ==="
if ! bash "$SCRIPT_DIR/check-docker.sh"; then
  rc=1
fi

echo
echo "=== Database ==="
if ! bash "$SCRIPT_DIR/check-db.sh"; then
  rc=1
fi

echo
if [[ "$rc" -eq 0 ]]; then
  echo -e "${GREEN}✅ Todos os checks passaram${NC}"
else
  echo -e "${RED}❌ Um ou mais checks falharam${NC}"
fi
exit "$rc"
