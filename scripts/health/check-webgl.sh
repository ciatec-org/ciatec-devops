#!/bin/bash
# Health check for Unity WebGL games (HTTP 200).
set -euo pipefail

TRUNKTILT_URL="${TRUNKTILT_URL:-https://trunktilt.example.com}"
BUBBLES_URL="${BUBBLES_URL:-https://bubbles.example.com}"
DOWNHILL_URL="${DOWNHILL_URL:-https://downhill.example.com}"

GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

ok=0
fail=0

check() {
  local name="$1" url="$2"
  if curl -fsS --max-time 10 -o /dev/null -w '' "$url"; then
    echo -e "${GREEN}✅ ${name} OK${NC} ($url)"
    ok=$((ok + 1))
  else
    echo -e "${RED}❌ ${name} FALHOU${NC} ($url)"
    fail=$((fail + 1))
  fi
}

check "TrunkTilt" "$TRUNKTILT_URL"
check "Bubbles" "$BUBBLES_URL"
check "Downhill" "$DOWNHILL_URL"

echo "Resumo WebGL: $ok/$((ok + fail)) serviços saudáveis"
[[ "$fail" -eq 0 ]]
