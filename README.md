# ciatec-devops

Automação de **deploy e operações** do CIATec.

Este repositório é o hub de CD: os repos de produto (jogos Unity WebGL e monorepo API/App)
chamam workflows daqui ao fazer push em `main`, e a produção na EC2 é atualizada.

---

## O que este repo faz

| Tipo | Fluxo |
|------|--------|
| **Jogos WebGL** | Caller no repo do jogo → `deploy-webgl.yml` → self-hosted runner na EC2 Games → Nginx |
| **API + App** | Caller no `ciatec-core` → `build-push-ghcr.yml` + `deploy-compose.yml` → GHCR → self-hosted na EC2 |

---

## Começar por aqui

**Conectar um repositório ao CD:**  
[docs/COMO-CONECTAR-SEU-REPO.md](docs/COMO-CONECTAR-SEU-REPO.md)

**Monorepo (API/App):**  
[docs/runbooks/deploy-monorepo.md](docs/runbooks/deploy-monorepo.md)

---

## Estrutura

```
.cursor/skills/        Skills Agile (agile-pipeline, epic/story/task-breaker)
.github/workflows/     Reusáveis: build-push-ghcr, deploy-compose, deploy-webgl (+ legado deploy-docker)
scripts/deploy/        Scripts SSH legado (/opt/ciatec)
scripts/health/        Health checks
scripts/rollback/      Placeholder
scripts/setup/         Bootstrap GitHub Project
docs/
  agile/                      Plano Agile deste repositório
  prompts/                    Prompt one-shot histórico
  specs/                      Specs do agile-pipeline
  COMO-CONECTAR-SEU-REPO.md   Guia de onboarding
  architecture.md
  repository-map.md
  runbooks/                   Procedimentos (incl. deploy-monorepo)
  templates/                  Callers para copiar nos repos produto
runners/               Notas do self-hosted runner
monitoring/            Placeholder (Phase 4)
terraform/             Placeholder (Phase 5)
ansible/               Placeholder (Phase 6)
```

Mapa: [docs/repository-map.md](docs/repository-map.md)

---

## Templates

| Template | Destino |
|----------|---------|
| [game-deploy-caller.yml](docs/templates/game-deploy-caller.yml) | Repo de jogo → `.github/workflows/deploy.yml` |
| [monorepo-deploy-caller.yml](docs/templates/monorepo-deploy-caller.yml) | Referência; no `ciatec-core` usam-se `deploy-api.yml` / `deploy-app.yml` |

---

## Secrets (organização)

| Secret | Usado por |
|--------|-----------|
| *(nenhum para monorepo GHCR)* | `GITHUB_TOKEN` com `packages: write` / `read` |
| `EC2_API_HOST` / `EC2_SSH_*` | Só fluxo SSH legado (`deploy-docker.yml`) |
| `DEPLOY_LOG_PATH` | WebGL (opcional) |
