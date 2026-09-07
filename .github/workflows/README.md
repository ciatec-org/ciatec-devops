# GitHub Workflows

Workflows reutilizáveis (`workflow_call`) do CIATec.

| Workflow | Runner | Uso |
|----------|--------|-----|
| `build-push-ghcr.yml` | GitHub-hosted | Build Docker + push GHCR (`:main`, `:sha-*`) |
| `deploy-compose.yml` | Self-hosted | Clone permanente no host: `git pull` + `compose pull/up` + health |
| `deploy-compose-checkout.yml` | Self-hosted | Sem clone permanente: `actions/checkout` + `compose pull/up` + health |
| `deploy-docker.yml` | GitHub-hosted + SSH | Legado (SSH + scripts em `/opt/ciatec`) |
| `deploy-webgl.yml` | Self-hosted (Games) | Deploy Unity WebGL |

- Monorepo com clone no host (`ciatec-core`): `build-push-ghcr` + `deploy-compose`. Ver [docs/runbooks/deploy-monorepo.md](../docs/runbooks/deploy-monorepo.md).
- App só com secrets no host (`ciatec-ht`): `build-push-ghcr` + `deploy-compose-checkout`. Template: [docs/templates/compose-checkout-deploy-caller.yml](../docs/templates/compose-checkout-deploy-caller.yml).
