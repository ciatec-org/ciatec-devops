# Runbook — Monorepo deploy (API + App via GHCR)

Current model: **CI/build on GitHub-hosted** → push to GHCR (`:main` + `:sha-XXXXXXX`) → **deploy on the self-hosted runner** on EC2 (`docker compose pull` / `up`).

No SSH secrets and no PAT. GHCR auth uses `GITHUB_TOKEN` only.

## Prerequisites (one-time)

### GitHub

1. `ciatec-devops` → Settings → Actions → General → **Accessible from repositories in the organization**
2. `ciatec-core` → Settings → Actions → General → allow Actions / reusable workflows
3. Self-hosted runner registered on `ciatec-core` with label `ec2-ciatec-core` (Idle)

### EC2

1. Runner installed as a service (`~/actions-runner`, `svc.sh install/start`)
2. Runner user in the `docker` group (`docker ps` without sudo)
3. Permanent monorepo clone at `/home/ubuntu/ciatec-core` with compose images pointing at `:main`
4. Nginx unchanged: `api.ciatec.org → :8000`, `research.ciatec.org → :8081`
5. API `.env` stays at `src/api/.env` on the host (never in CI)

## Workflows

| Repo | File | Role |
|------|------|------|
| `ciatec-devops` | `build-push-ghcr.yml` | Reusable: build + push GHCR |
| `ciatec-devops` | `deploy-compose.yml` | Reusable: `git pull` + `compose pull/up` + health (+ optional smoke) |
| `ciatec-core` | `deploy-api.yml` | Caller for API |
| `ciatec-core` | `deploy-app.yml` | Caller for App |

Reference caller shape: [`docs/templates/monorepo-deploy-caller.yml`](../templates/monorepo-deploy-caller.yml).

### What `deploy-compose.yml` does

1. Login to GHCR with `GITHUB_TOKEN`
2. `git pull --ff-only` from the repo root that owns `compose_dir`
3. `docker compose pull <service>` then `up -d --no-deps --force-recreate`
4. Poll `health_url` (default: 12 attempts, 15s apart)
5. Optional `smoke_cmd`
6. `docker image prune -f` on success

Default runner labels: `self-hosted`, `Linux`, `X64`, `ec2-ciatec-core`.

Example API caller inputs (from the template):

| Input | Value |
|-------|-------|
| `service` | `api` |
| `compose_dir` | `/home/ubuntu/ciatec-core/src/api` |
| `health_url` | `http://127.0.0.1:8000/health` |

## GHCR tags

Published by `build-push-ghcr.yml` (owner lowercased):

- `ghcr.io/ciatec-org/ciatec-api:main` — production (compose)
- `ghcr.io/ciatec-org/ciatec-api:sha-<7>` — history / manual rollback
- Same pattern for `ciatec-app`

## Manual rollback

```bash
cd /home/ubuntu/ciatec-core/src/api
docker pull ghcr.io/ciatec-org/ciatec-api:sha-ABCDEF0
docker tag ghcr.io/ciatec-org/ciatec-api:sha-ABCDEF0 ghcr.io/ciatec-org/ciatec-api:main
docker compose up -d --no-deps --force-recreate api
curl -fsS http://127.0.0.1:8000/health
```

## Publish order

1. Push reusable workflows on `ciatec-devops` (`main`)
2. Push callers + compose on `ciatec-core` (`main`)
3. Trigger `workflow_dispatch` on Deploy API / Deploy App, or push under `src/api/**` / `src/app/**`

## Logs

- Actions on `ciatec-core`
- On EC2: `docker compose -f ~/ciatec-core/src/api/docker-compose.yml logs --tail=80 api`
