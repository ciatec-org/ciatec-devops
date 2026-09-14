# GitHub Workflows

Reusable workflows to **update CIATec EC2 hosts**. Product repos call these files via `workflow_call` (push to `main`).

| Workflow | Runner | What it does on EC2 |
|----------|--------|---------------------|
| `build-push-ghcr.yml` | GitHub-hosted | Build Docker image + push to GHCR (`:main`, `:sha-*`) — prepares the image for deploy |
| `deploy-compose.yml` | Self-hosted | Permanent clone: `git pull` + `compose pull/up` + health |
| `deploy-compose-checkout.yml` | Self-hosted | No permanent clone: `actions/checkout` + `compose pull/up` + health |
| `deploy-webgl.yml` | Self-hosted (Games) | Sync Unity WebGL → Nginx path on Games EC2 |
| `deploy-ai-project.yml` | Self-hosted (AI Research) | Create or update a Python project (clone, systemd, Nginx, health) |
| `deploy-docker.yml` | GitHub-hosted + SSH | Legacy: SSH + scripts under `/opt/ciatec` |

`deploy-ai-project.yml` also supports `workflow_dispatch` (Actions → **Deploy AI Project**).

---

## EC2 and stacks

### Games (`ciatec-games-prod`)
- Unity WebGL → `deploy-webgl.yml`
- Docker/Compose → `build-push-ghcr` + `deploy-compose`

### Core / API (`ec2-ciatec-core` and similar)
- Permanent host clone → `build-push-ghcr` + `deploy-compose`
- Host secrets only (no permanent clone) → `build-push-ghcr` + `deploy-compose-checkout`

### AI Research (`ciatec-ai-prod`)
- Python + Uvicorn + FastAPI → `deploy-ai-project.yml` (create **or** update)
- Runner labels: `self-hosted`, `Linux`, `X64`, `ai-research`
- URL: `ai.research.ciatec.org/<project_name>`
- Path: `/opt/ciatec-ai/<project_name>/`

---

## Connect a Python repo (AI Research)

### 1. First deploy (or update)

In `ciatec-devops`: Actions → **Deploy AI Project** → `project_name` + `port`.

Or on the EC2:

```bash
sudo ./scripts/setup/new-ai-project.sh <project_name> <port> ciatec-org/<repo>
```

Creates/updates the clone at `/opt/ciatec-ai/<project_name>`, the systemd unit, and the Nginx block.

### 2. Caller in the product repo

```yaml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  deploy:
    uses: ciatec-org/ciatec-devops/.github/workflows/deploy-ai-project.yml@main
    with:
      project_name: project-name
      port: 8001  # unique port per project
```

### 3. Expected layout

```
my-project/
├── main.py              # entry point: app = FastAPI()
├── requirements.txt
└── .github/
    └── workflows/
        └── deploy.yml
```

Required endpoint:

```python
@app.get("/health")
def health():
    return {"status": "ok"}
```

---

## References

- General onboarding: [docs/COMO-CONECTAR-SEU-REPO.md](../../docs/COMO-CONECTAR-SEU-REPO.md)
- Monorepo (`ciatec-core`): [docs/runbooks/deploy-monorepo.md](../../docs/runbooks/deploy-monorepo.md)
- AI Research: [docs/runbooks/ec2-ai-research-runbook.md](../../docs/runbooks/ec2-ai-research-runbook.md)
- Caller templates: [docs/templates/](../../docs/templates/)
