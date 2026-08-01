# ciatec-devops

Automação de **deploy e operações** do CIATec.

Este repositório é o hub de CD: os repos de produto (jogos Unity WebGL e monorepo API/App)
chamam workflows daqui ao fazer push em `main`, e a produção na EC2 é atualizada.

---

## O que este repo faz

| Tipo | Fluxo |
|------|--------|
| **Jogos WebGL** | Caller no repo do jogo → `deploy-webgl.yml` → self-hosted runner na EC2 Games → Nginx |
| **API + App** | Caller no monorepo → `deploy-docker.yml` → SSH na EC2 API/App → Docker Compose + migrações |

---

## Começar por aqui

**Conectar um repositório ao CD:**  
[docs/COMO-CONECTAR-SEU-REPO.md](docs/COMO-CONECTAR-SEU-REPO.md)

---

## Estrutura

```
.cursor/skills/        Skills Agile (agile-pipeline, epic/story/task-breaker)
.github/workflows/     Workflows reutilizáveis (deploy-webgl, deploy-docker)
scripts/deploy/        Scripts no servidor (Docker, migrações)
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
  runbooks/                   Procedimentos
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
| [monorepo-deploy-caller.yml](docs/templates/monorepo-deploy-caller.yml) | Monorepo → `.github/workflows/deploy.yml` |

---

## Secrets (organização)

| Secret | Usado por |
|--------|-----------|
| `EC2_API_HOST` | Deploy Docker |
| `EC2_SSH_KEY` | Deploy Docker |
| `EC2_SSH_USER` | Deploy Docker |
| `DEPLOY_LOG_PATH` | WebGL (opcional) |
