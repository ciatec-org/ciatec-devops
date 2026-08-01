#!/bin/bash
# Run Alembic migrations inside the API container before promoting a new API deploy.
#
# Env:
#   COMPOSE_DIR         — directory with docker-compose.yml (default: /opt/ciatec)
#   DB_HOST             — RDS/Postgres host for connectivity check (optional)
#   DB_PORT             — default 5432
#   MIGRATIONS_LOG_PATH — default /var/log/ciatec/migrations.log
#
# Exit: 0 ok | 1 fail

set -euo pipefail

COMPOSE_DIR="${COMPOSE_DIR:-/opt/ciatec}"
DB_HOST="${DB_HOST:-}"
DB_PORT="${DB_PORT:-5432}"
MIGRATIONS_LOG_PATH="${MIGRATIONS_LOG_PATH:-/var/log/ciatec/migrations.log}"

GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

ok() { echo -e "${GREEN}✅ $*${NC}"; }
err() { echo -e "${RED}❌ $*${NC}"; }

ts="$(date -u +%Y%m%dT%H%M%SZ)"
mkdir -p "$(dirname "$MIGRATIONS_LOG_PATH")" 2>/dev/null || true

log_line() {
  local msg="$1"
  echo "[$ts] $msg" | tee -a "$MIGRATIONS_LOG_PATH" >/dev/null 2>&1 \
    || echo "[$ts] $msg" | sudo tee -a "$MIGRATIONS_LOG_PATH" >/dev/null
}

cd "$COMPOSE_DIR"

if [[ -n "$DB_HOST" ]]; then
  if command -v pg_isready >/dev/null 2>&1; then
    if ! pg_isready -h "$DB_HOST" -p "$DB_PORT" -t 10; then
      err "Database not ready at $DB_HOST:$DB_PORT"
      log_line "FAIL db not ready $DB_HOST:$DB_PORT"
      exit 1
    fi
  else
    # TCP fallback
    if ! timeout 10 bash -c "cat < /dev/null > /dev/tcp/${DB_HOST}/${DB_PORT}" 2>/dev/null; then
      err "Cannot reach database TCP $DB_HOST:$DB_PORT"
      log_line "FAIL db tcp $DB_HOST:$DB_PORT"
      exit 1
    fi
  fi
  ok "Database reachable"
fi

ok "Running alembic upgrade head"
set +e
output="$(docker compose run --rm api alembic upgrade head 2>&1)"
rc=$?
set -e

echo "$output"
echo "$output" | tee -a "$MIGRATIONS_LOG_PATH" >/dev/null 2>&1 \
  || echo "$output" | sudo tee -a "$MIGRATIONS_LOG_PATH" >/dev/null

if [[ $rc -ne 0 ]]; then
  err "Migration failed"
  log_line "FAIL alembic upgrade head"
  exit 1
fi

ok "Migrations applied"
log_line "OK alembic upgrade head"
exit 0
