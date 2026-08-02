# GitHub Workflows

Workflows reutilizáveis (`workflow_call`) do CIATec.

| Workflow | Runner | Uso |
|----------|--------|-----|
| `build-push-ghcr.yml` | GitHub-hosted | Build Docker + push GHCR (`:main`, `:sha-*`) |
| `deploy-compose.yml` | Self-hosted | `compose pull/up` + health (+ smoke opcional) |
| `deploy-docker.yml` | GitHub-hosted + SSH | Legado (SSH + scripts em `/opt/ciatec`) |
| `deploy-webgl.yml` | Self-hosted (Games) | Deploy Unity WebGL |

Monorepo actual (`ciatec-core`): preferir `build-push-ghcr` + `deploy-compose`. Ver [docs/runbooks/deploy-monorepo.md](../docs/runbooks/deploy-monorepo.md).
