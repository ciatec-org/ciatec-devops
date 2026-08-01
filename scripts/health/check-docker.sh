#!/bin/bash
# Health check for Docker services (API + App).
set -euo pipefail

API_URL="${API_URL:-https://api.example.com/health}"
APP_URL="${APP_URL:-https://app.example.com}"

GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

ok=0
fail=0

check_api() {
  local body
  if body="$(curl -fsS --max-time 10 "$API_URL")"; then
    if echo "$body" | grep -Eqi '"status"[[:space:]]*:[[:space:]]*"ok"'; then
      echo -e "${GREEN}✅ API OK${NC} ($API_URL)"
      ok=$((ok + 1))
      return
    fi
    echo -e "${RED}❌ API FALHOU${NC} (status field missing/invalid) ($API_URL)"
  else
    echo -e "${RED}❌ API FALHOU${NC} (HTTP/network) ($API_URL)"
  fi
  fail=$((fail + 1))
}

check_app() {
  if curl -fsS --max-time 10 -o /dev/null "$APP_URL"; then
    echo -e "${GREEN}✅ App OK${NC} ($APP_URL)"
    ok=$((ok + 1))
  else
    echo -e "${RED}❌ App FALHOU${NC} ($APP_URL)"
    fail=$((fail + 1))
  fi
}

check_api
check_app

echo "Resumo Docker: $ok/$((ok + fail)) serviços saudáveis"
[[ "$fail" -eq 0 ]]
