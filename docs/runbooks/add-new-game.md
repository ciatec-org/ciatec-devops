# Runbook — Add a new Unity WebGL game

## Prerequisites

- Games EC2 with Nginx and a self-hosted GitHub Actions runner
- Game repository with a `Build/` folder at the repo root (Unity WebGL export)
- Org `ciatec-org` with access to reusable workflows in `ciatec-devops`

## Steps

### 1. Prepare the path on the server

```bash
sudo mkdir -p /var/www/NEW_GAME
sudo chown -R www-data:www-data /var/www/NEW_GAME
```

Configure the Nginx virtual host / location for that path, then:

```bash
sudo nginx -t && sudo systemctl reload nginx
```

### 2. Add the caller workflow

In the game repo, create `.github/workflows/deploy.yml` from:

[`docs/templates/game-deploy-caller.yml`](../templates/game-deploy-caller.yml)

Set:

| Input | Example |
|-------|---------|
| `game_name` | `bubbles` |
| `deploy_path` | `/var/www/bubbles` |

The reusable workflow is `deploy-webgl.yml`. On push to `main` it:

1. Checks out the **calling** repository
2. Requires `Build/` at the repo root
3. Backs up the current deploy path (if any)
4. `rsync`s the **entire repository root** to `deploy_path` (excludes `.git/` and `.github/`)
5. Sets ownership to `www-data`, runs `nginx -t`, reloads Nginx
6. Appends a line to `/var/log/ciatec/deploys.log` (or `DEPLOY_LOG_PATH`)

### 3. Secrets and access

Use `secrets: inherit`. Optional org/repo secret: `DEPLOY_LOG_PATH` (default `/var/log/ciatec/deploys.log`).

Ensure the game repo can call workflows from `ciatec-org/ciatec-devops` (Settings → Actions → General → Access).

### 4. Verify the deploy

1. Push to `main` (with `Build/` present)
2. Watch Actions in the game repo
3. On the server: `tail -n 20 /var/log/ciatec/deploys.log`
4. Open the public game URL and confirm HTTP 200
5. Or run `scripts/health/check-webgl.sh` from a machine with the game URLs set via env vars

## Manual rollback

On failure after backup, `deploy-webgl.yml` restores automatically via `trap` on `ERR`. Manually:

```bash
# list backups
ls -d /var/www/NEW_GAME.bak.*

sudo rm -rf /var/www/NEW_GAME
sudo mv /var/www/NEW_GAME.bak.TIMESTAMP /var/www/NEW_GAME
sudo nginx -t && sudo systemctl reload nginx
```
