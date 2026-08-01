#!/bin/bash
# Deploy Docker Compose services (api | app | all) on EC2 API/App.
#
# Env:
#   COMPOSE_DIR      — directory with docker-compose.yml (default: /opt/ciatec)
#   API_HEALTH_URL   — health URL for API (default: http://127.0.0.1:8000/health)
#   APP_HEALTH_URL   — health URL for App (default: http://127.0.0.1:80)
#   DEPLOY_LOG_PATH  — deploy log (default: /var/log/ciatec/deploys.log)
#   SKIP_MIGRATIONS  — set to 1 to skip Alembic on api deploy
#
# Exit codes: 0 success | 1 failure | 2 rollback executed

set -euo pipefail

COMPOSE_DIR="${COMPOSE_DIR:-/opt/ciatec}"
API_HEALTH_URL="${API_HEALTH_URL:-http://127.0.0.1:8000/health}"
APP_HEALTH_URL="${APP_HEALTH_URL:-http://127.0.0.1:80}"
DEPLOY_LOG_PATH="${DEPLOY_LOG_PATH:-/var/log/ciatec/deploys.log}"
SKIP_MIGRATIONS="${SKIP_MIGRATIONS:-0}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

ok() { echo -e "${GREEN}✅ $*${NC}"; }
warn() { echo -e "${YELLOW}⚠️  $*${NC}"; }
err() { echo -e "${RED}❌ $*${NC}"; }

SERVICE="all"
DRY_RUN=0

usage() {
  echo "Usage: $0 [api|app|all] [--dry-run]"
  echo "       $0 --service api|app|all [--dry-run]"
  exit 1
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    api|app|all) SERVICE="$1"; shift ;;
    --dry-run) DRY_RUN=1; shift ;;
    --service)
      [[ $# -ge 2 ]] || usage
      SERVICE="$2"
      shift 2
      ;;
    -h|--help) usage ;;
    *) err "Unknown argument: $1"; usage ;;
  esac
done

if [[ ! "$SERVICE" =~ ^(api|app|all)$ ]]; then
  err "Invalid service: $SERVICE"
  usage
fi

append_log() {
  local line="$1"
  mkdir -p "$(dirname "$DEPLOY_LOG_PATH")" 2>/dev/null || true
  if ! echo "$line" >> "$DEPLOY_LOG_PATH" 2>/dev/null; then
    echo "$line" | sudo tee -a "$DEPLOY_LOG_PATH" >/dev/null
  fi
}

health_url_for() {
  case "$1" in
    api) echo "$API_HEALTH_URL" ;;
    app) echo "$APP_HEALTH_URL" ;;
  esac
}

check_health() {
  local svc="$1"
  local url
  url="$(health_url_for "$svc")"
  local i
  for i in 1 2 3 4 5 6; do
    if curl -fsS --max-time 10 "$url" >/dev/null 2>&1; then
      ok "Health OK: $svc ($url)"
      return 0
    fi
    sleep 5
  done
  err "Health FAILED: $svc ($url)"
  return 1
}

current_image_id() {
  local svc="$1"
  local cid
  cid="$(docker compose ps -q "$svc" 2>/dev/null || true)"
  if [[ -n "$cid" ]]; then
    docker inspect --format='{{.Image}}' "$cid" 2>/dev/null || true
  fi
}

compose_image_ref() {
  local svc="$1"
  # Best-effort: first image listed for the project; callers also tag ciatec-$svc:rollback
  docker compose config --images 2>/dev/null | head -n 1 || true
}

rollback_service() {
  local svc="$1"
  local prev_id="$2"
  local image_ref
  image_ref="$(compose_image_ref "$svc" | tail -n 1)"
  if [[ -z "$prev_id" ]]; then
    err "No previous image to rollback for $svc"
    return 1
  fi
  warn "Rolling back $svc to image id $prev_id"
  if [[ -n "$image_ref" ]]; then
    docker tag "$prev_id" "$image_ref" || true
  fi
  docker tag "$prev_id" "ciatec-${svc}:rollback" || true
  docker compose up -d --no-deps --force-recreate "$svc"
  sleep 10
  check_health "$svc"
}

deploy_one() {
  local svc="$1"
  local ts prev_id new_id
  ts="$(date -u +%Y%m%dT%H%M%SZ)"

  cd "$COMPOSE_DIR"

  if [[ "$svc" == "api" && "$SKIP_MIGRATIONS" != "1" ]]; then
    if [[ -x "$SCRIPT_DIR/run-migrations.sh" ]]; then
      ok "Running migrations before api deploy"
      if [[ "$DRY_RUN" -eq 1 ]]; then
        echo "[dry-run] $SCRIPT_DIR/run-migrations.sh"
      else
        "$SCRIPT_DIR/run-migrations.sh"
      fi
    else
      warn "run-migrations.sh not found or not executable; skipping migrations"
    fi
  fi

  prev_id="$(current_image_id "$svc")"
  ok "Previous image for $svc: ${prev_id:-none}"

  if [[ "$DRY_RUN" -eq 1 ]]; then
    echo "[dry-run] docker compose pull $svc"
    echo "[dry-run] docker compose up -d --no-deps $svc"
    echo "[dry-run] health-check $svc"
    return 0
  fi

  docker compose pull "$svc"
  docker compose up -d --no-deps "$svc"
  sleep 15

  if ! check_health "$svc"; then
    if rollback_service "$svc" "$prev_id"; then
      append_log "[$ts] ROLLBACK $svc previous=$prev_id"
      return 2
    fi
    append_log "[$ts] FAIL $svc (rollback failed) previous=$prev_id"
    return 1
  fi

  new_id="$(current_image_id "$svc")"
  append_log "[$ts] OK deployed $svc image=${new_id:-unknown}"
  ok "Deployed $svc"
  return 0
}

mkdir -p "$(dirname "$DEPLOY_LOG_PATH")" 2>/dev/null || true

OVERALL=0
ROLLBACK=0

if [[ "$SERVICE" == "all" ]]; then
  TARGETS=(api app)
else
  TARGETS=("$SERVICE")
fi

for svc in "${TARGETS[@]}"; do
  set +e
  deploy_one "$svc"
  rc=$?
  set -e
  if [[ $rc -eq 2 ]]; then
    ROLLBACK=1
  elif [[ $rc -ne 0 ]]; then
    OVERALL=1
  fi
done

if [[ $OVERALL -ne 0 ]]; then
  err "Deploy finished with failures"
  exit 1
fi
if [[ $ROLLBACK -ne 0 ]]; then
  warn "Deploy finished with rollback"
  exit 2
fi
ok "Deploy finished successfully"
exit 0
