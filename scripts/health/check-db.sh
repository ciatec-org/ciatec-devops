#!/bin/bash
# Check PostgreSQL/RDS connectivity via pg_isready or TCP.
set -euo pipefail

DB_HOST="${DB_HOST:-}"
DB_PORT="${DB_PORT:-5432}"

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

if [[ -z "$DB_HOST" ]]; then
  echo -e "${YELLOW}⚠️  DB_HOST não definido — pulando check-db${NC}"
  exit 0
fi

if command -v pg_isready >/dev/null 2>&1; then
  if pg_isready -h "$DB_HOST" -p "$DB_PORT" -t 10; then
    echo -e "${GREEN}✅ DB OK${NC} ($DB_HOST:$DB_PORT)"
    exit 0
  fi
elif timeout 10 bash -c "cat < /dev/null > /dev/tcp/${DB_HOST}/${DB_PORT}" 2>/dev/null; then
  echo -e "${GREEN}✅ DB TCP OK${NC} ($DB_HOST:$DB_PORT)"
  exit 0
fi

echo -e "${RED}❌ DB FALHOU${NC} ($DB_HOST:$DB_PORT)"
exit 1
