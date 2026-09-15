#!/bin/bash
# new-ai-project.sh — provision or update a Python AI project on the EC2
#
# Usage: sudo ./new-ai-project.sh <project_name> <port> <github_org/repo>
#
# Creates / updates:
#   - /opt/ciatec-ai/<project_name>/   (git clone or pull)
#   - /etc/nginx/sites-available/ai-projects/<project_name>.conf
#   - /etc/systemd/system/<project_name>.service
#
# Convention:
#   - URL: ai.research.ciatec.org/<project_name>
#   - Health: http://127.0.0.1:<port>/health

set -euo pipefail

PROJECT_NAME="${1:?Usage: $0 <project_name> <port> <github_org/repo>}"
PORT="${2:?Usage: $0 <project_name> <port> <github_org/repo>}"
GITHUB_REPO="${3:?Usage: $0 <project_name> <port> <github_org/repo>}"

DEPLOY_PATH="/opt/ciatec-ai/${PROJECT_NAME}"
SERVICE_FILE="/etc/systemd/system/${PROJECT_NAME}.service"
NGINX_DIR="/etc/nginx/sites-available/ai-projects"
NGINX_CONF="${NGINX_DIR}/${PROJECT_NAME}.conf"

echo "========================================="
echo "  Provisioning: ${PROJECT_NAME}"
echo "  Port:         ${PORT}"
echo "  Repo:         ${GITHUB_REPO}"
echo "  Deploy path:  ${DEPLOY_PATH}"
echo "========================================="

mkdir -p /opt/ciatec-ai

# --- 1. Clone or update repository ---
if [ -d "${DEPLOY_PATH}/.git" ]; then
  echo "${DEPLOY_PATH} already exists — pulling latest from main"
  git -C "${DEPLOY_PATH}" fetch origin
  git -C "${DEPLOY_PATH}" checkout main
  git -C "${DEPLOY_PATH}" pull --ff-only origin main
  echo "Updated — commit: $(git -C "${DEPLOY_PATH}" rev-parse --short HEAD)"
else
  echo "Cloning https://github.com/${GITHUB_REPO}..."
  git clone "https://github.com/${GITHUB_REPO}.git" "${DEPLOY_PATH}"
  echo "Cloned"
fi

chown -R ubuntu:ubuntu "${DEPLOY_PATH}"

# --- 2. Install dependencies ---
if [ -f "${DEPLOY_PATH}/requirements.txt" ]; then
  echo "Installing dependencies..."
  pip install -r "${DEPLOY_PATH}/requirements.txt" --quiet
  echo "Dependencies installed"
else
  echo "No requirements.txt found — skipping"
fi

# --- 3. Create systemd service ---
echo "Creating systemd service: ${PROJECT_NAME}"
cat > "${SERVICE_FILE}" <<EOF
[Unit]
Description=CIATec AI — ${PROJECT_NAME}
After=network.target

[Service]
User=ubuntu
WorkingDirectory=${DEPLOY_PATH}
ExecStart=uvicorn main:app --host 127.0.0.1 --port ${PORT}
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable "${PROJECT_NAME}"
systemctl restart "${PROJECT_NAME}"
echo "Systemd service enabled and restarted"

# --- 4. Create Nginx vhost config ---
echo "Creating Nginx config for /${PROJECT_NAME}"
mkdir -p "${NGINX_DIR}"
cat > "${NGINX_CONF}" <<EOF
# ${PROJECT_NAME} — ai.research.ciatec.org/${PROJECT_NAME}
location /${PROJECT_NAME}/ {
    proxy_pass         http://127.0.0.1:${PORT}/;
    proxy_set_header   Host \$host;
    proxy_set_header   X-Real-IP \$remote_addr;
    proxy_set_header   X-Forwarded-For \$proxy_add_x_forwarded_for;
    proxy_set_header   X-Forwarded-Proto \$scheme;
}
EOF

nginx -t
systemctl reload nginx
echo "Nginx configured: ai.research.ciatec.org/${PROJECT_NAME}"

# --- 5. Summary ---
echo ""
echo "========================================="
echo "  ${PROJECT_NAME} provisioned"
echo "  URL:    https://ai.research.ciatec.org/${PROJECT_NAME}"
echo "  Health: http://127.0.0.1:${PORT}/health"
echo "  Logs:   journalctl -u ${PROJECT_NAME} -f"
echo "========================================="
