# Runbook — Adicionar um novo jogo Unity WebGL

## Pré-requisitos

- EC2 Games com Nginx e self-hosted GitHub runner
- Repositório do jogo com pasta `Build/` na raiz (artefato Unity WebGL)
- Org GitHub `ciatec-org` com acesso ao workflow reutilizável em `ciatec-devops`

## Passos

### 1. Preparar caminho no servidor

```bash
sudo mkdir -p /var/www/NOVO_JOGO
sudo chown -R www-data:www-data /var/www/NOVO_JOGO
```

Configure o virtual host / location no Nginx apontando para esse path e rode `sudo nginx -t && sudo systemctl reload nginx`.

### 2. Copiar o template de caller

No repositório do jogo, crie `.github/workflows/deploy.yml` a partir de:

[`docs/templates/game-deploy-caller.yml`](../templates/game-deploy-caller.yml)

Altere:

| Input | Exemplo |
|-------|---------|
| `game_name` | `bubbles` |
| `deploy_path` | `/var/www/bubbles` |

### 3. Secrets

Use `secrets: inherit`. Opcional na org/repo: `DEPLOY_LOG_PATH` (default `/var/log/ciatec/deploys.log`).

Garanta que o repo do jogo pode usar workflows de `ciatec-org/ciatec-devops` (Settings → Actions → General → Access).

### 4. Verificar o deploy

1. Push na branch `main` (com `Build/` presente)
2. Acompanhe o Actions no repo do jogo
3. No servidor: `tail -n 20 /var/log/ciatec/deploys.log`
4. Abra a URL pública do jogo e confira HTTP 200
5. Ou rode `scripts/health/check-webgl.sh` a partir de uma máquina com as URLs configuradas

## Rollback manual

Se o workflow falhar após o backup, ele tenta restaurar automaticamente. Manualmente:

```bash
# listar backups
ls -d /var/www/NOVO_JOGO.bak.*

sudo rm -rf /var/www/NOVO_JOGO
sudo mv /var/www/NOVO_JOGO.bak.TIMESTAMP /var/www/NOVO_JOGO
sudo nginx -t && sudo systemctl reload nginx
```
