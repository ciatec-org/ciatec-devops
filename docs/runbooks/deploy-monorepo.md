# Runbook — Deploy do monorepo (API + App via GHCR)

Modelo actual: **CI e build no GitHub-hosted** → push para GHCR (`:main` + `:sha-XXXXXXX`) → **deploy no self-hosted runner** da EC2 (`docker compose pull` / `up`).

Não usa SSH secrets nem PAT. Autenticação GHCR via `GITHUB_TOKEN`.

## Pré-requisitos (uma vez)

### GitHub

1. `ciatec-devops` → Settings → Actions → General → **Accessible from repositories in the organization**
2. `ciatec-core` → Settings → Actions → General → permitir Actions / reusable workflows
3. Self-hosted runner registado em `ciatec-core` com label `ec2-ciatec-core` (Idle)

### EC2

1. Runner instalado como serviço (`~/actions-runner`, `svc.sh install/start`)
2. User do runner no grupo `docker` (`docker ps` sem sudo)
3. Clone do monorepo em `/home/ubuntu/ciatec-core` com compose a apontar para `:main`
4. Nginx inalterado: `api.ciatec.org → :8000`, `research.ciatec.org → :8081`
5. `.env` da API permanece em `src/api/.env` (nunca no CI)

## Workflows

| Repo | Ficheiro | Papel |
|------|----------|-------|
| `ciatec-devops` | `build-push-ghcr.yml` | Reusável: build + push GHCR |
| `ciatec-devops` | `deploy-compose.yml` | Reusável: pull/up/health/smoke no runner |
| `ciatec-core` | `deploy-api.yml` | Caller API |
| `ciatec-core` | `deploy-app.yml` | Caller App |

## Tags GHCR

- `ghcr.io/ciatec-org/ciatec-api:main` — produção (compose)
- `ghcr.io/ciatec-org/ciatec-api:sha-<7>` — histórico / rollback manual
- Idem para `ciatec-app`

## Rollback manual

```bash
cd /home/ubuntu/ciatec-core/src/api
docker pull ghcr.io/ciatec-org/ciatec-api:sha-ABCDEF0
docker tag ghcr.io/ciatec-org/ciatec-api:sha-ABCDEF0 ghcr.io/ciatec-org/ciatec-api:main
docker compose up -d --no-deps --force-recreate api
curl -fsS http://127.0.0.1:8000/health
```

## Ordem de publicação dos repos

1. Push dos reusáveis em `ciatec-devops` (`main`)
2. Push dos callers + compose em `ciatec-core` (`main`)
3. Disparar `workflow_dispatch` em Deploy API / Deploy App, ou push em `src/api/**` / `src/app/**`

## Logs

- Actions no `ciatec-core`
- Na EC2: `docker compose -f ~/ciatec-core/src/api/docker-compose.yml logs --tail=80 api`
