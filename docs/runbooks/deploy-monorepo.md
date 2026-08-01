# Runbook — Deploy do monorepo (API + App)

## Secrets na organização GitHub

Em **Organization → Settings → Secrets and variables → Actions** (ou no repo do monorepo):

| Secret | Conteúdo |
|--------|----------|
| `EC2_API_HOST` | IP/hostname da EC2 API/App |
| `EC2_SSH_KEY` | Chave privada PEM (conteúdo completo) |
| `EC2_SSH_USER` | Usuário SSH (ex.: `ubuntu`) |

Garanta que o monorepo pode chamar workflows de `ciatec-org/ciatec-devops`.

## Instalar o caller

Copie [`docs/templates/monorepo-deploy-caller.yml`](../templates/monorepo-deploy-caller.yml) para o monorepo como `.github/workflows/deploy.yml`.

## Testar manualmente antes do CD

Na EC2 API/App:

```bash
export COMPOSE_DIR=/opt/ciatec
export API_HEALTH_URL=http://127.0.0.1:8000/health
export APP_HEALTH_URL=http://127.0.0.1:80

# Copiar scripts do repo devops
sudo mkdir -p /opt/ciatec/scripts
sudo cp deploy-docker.sh run-migrations.sh /opt/ciatec/scripts/
sudo chmod +x /opt/ciatec/scripts/*.sh

/opt/ciatec/scripts/deploy-docker.sh api --dry-run
/opt/ciatec/scripts/deploy-docker.sh api
```

Ou dispare o workflow reutilizável manualmente via `workflow_dispatch` (se adicionado) / Actions UI no monorepo após o primeiro push.

## Logs no servidor

```bash
tail -f /var/log/ciatec/deploys.log
tail -f /var/log/ciatec/migrations.log
docker compose -f /opt/ciatec/docker-compose.yml ps
```

## Rollback manual

```bash
cd /opt/ciatec
# listar imagens locais
docker images | head

# subir de novo um tag conhecido
docker compose pull api   # ou pin de tag anterior no compose
docker compose up -d --no-deps api
curl -fsS "$API_HEALTH_URL"
```

Exit codes do script: `0` ok · `1` falha · `2` rollback automático executado.
