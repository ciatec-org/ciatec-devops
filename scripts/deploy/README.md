# Scripts de deploy

Scripts de deploy por tipo de aplicação (WebGL via workflow, Docker Compose, migrações).

| Script | Uso |
|--------|-----|
| `deploy-docker.sh` | Deploy `api` / `app` / `all` com health check e rollback |
| `run-migrations.sh` | `alembic upgrade head` no container da API |

```bash
export COMPOSE_DIR=/opt/ciatec
./deploy-docker.sh api
./deploy-docker.sh all --dry-run
./run-migrations.sh
```
