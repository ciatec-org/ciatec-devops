# Runbook — Serviço Node.js (HTTP + WebSocket) na EC2 Games

Para jogos e serviços que precisam de um processo rodando (ex.: salas multiplayer por WebSocket), e não só de arquivos estáticos. Para Unity WebGL, use [add-new-game.md](add-new-game.md).

Workflow: [`deploy-node-service.yml`](../../.github/workflows/deploy-node-service.yml)

## O que o workflow faz

1. **GitHub-hosted:** `npm ci` → `npm test` → `npm run build` → empacota `artifact_paths` + a unit systemd.
2. **Self-hosted (`ciatec-games-prod`):**
   1. `npm ci --omit=dev` no workspace do runner (falha aqui não toca a produção)
   2. Backup de `/opt/<service>` em `/opt/<service>.bak.<timestamp>` (+ unit anterior)
   3. `rsync --delete` para `/opt/<service>` (dono `root`, leitura para todos)
   4. Instala `deploy/<service>.service` em `/etc/systemd/system/`, `daemon-reload`, `enable`, `restart`
   5. Health: `http://127.0.0.1:<port><health_path>` até responder 2xx
   6. Smoke de WebSocket (se `ws_path`): conecta, envia `ws_message`, espera `ws_expect`
   7. Log em `/var/log/ciatec/deploys.log` e mantém só os últimos `keep_backups` backups
3. **Em falha depois do backup:** restaura arquivos e unit, reinicia a versão anterior. No primeiro deploy (sem backup), para o serviço.

O Nginx **não** é tocado pelo workflow: o vhost é configurado uma vez, à mão, porque o certbot edita esse arquivo.

## Pré-requisitos (uma vez)

### Na EC2 Games

- Node.js instalado no sistema (`/usr/bin/node`, não `nvm` de um usuário): o runner e o `www-data` da unit precisam achá-lo. A versão precisa atender o `engines` do `package.json` do serviço; não precisa ser a mesma do build.
  ```bash
  which node && node -v
  ```
- `rsync`, `curl` e sudo sem senha para o usuário do runner (mesmo requisito do `deploy-webgl.yml`).
- Porta livre e registrada em [architecture.md](../architecture.md#portas-locais-na-ec2-games):
  ```bash
  sudo ss -ltnp | grep ':PORTA '
  ```

### No repositório do serviço

| Arquivo | Conteúdo |
|---------|----------|
| `deploy/<service>.service` | Unit systemd (exemplo abaixo) |
| `.github/workflows/deploy.yml` | Caller: [`node-service-deploy-caller.yml`](../templates/node-service-deploy-caller.yml) |
| `package.json` + `package-lock.json` | `npm test`, `npm run build`; dependências de runtime em `dependencies`; `engines.node` com o mínimo para rodar |
| `.nvmrc` | Versão do Node do build e do dev (ex.: `22`) |
| Rota de health | `GET /health` → 200, sem tocar em banco ou estado |

Exemplo de unit (o processo só escuta em `127.0.0.1`; quem atende a internet é o Nginx):

```ini
[Unit]
Description=Meu serviço
After=network-online.target
Wants=network-online.target

[Service]
WorkingDirectory=/opt/meu-servico
ExecStart=/usr/bin/env node /opt/meu-servico/server/index.mjs
Environment=HOST=127.0.0.1
Environment=PORT=8790
Restart=always
RestartSec=2
User=www-data
NoNewPrivileges=true

[Install]
WantedBy=multi-user.target
```

Os arquivos ficam com dono `root`: o processo (`www-data`) lê, mas não altera o próprio código.

### No GitHub

- O repo pode chamar workflows de `ciatec-org/ciatec-devops` (Settings → Actions → General → Access).
- O runner `ciatec-games-prod` atende o repo. Se for runner da organização, confira o **runner group**: repositórios privados ou fora da lista não recebem o job e ele fica em "Waiting for a runner".

## Passo a passo

### 1. DNS

Criar `SUBDOMINIO.game.ciatec.org` apontando para o IP público da EC2 Games.

### 2. Nginx (uma vez)

Copiar [`nginx-node-websocket.conf`](../templates/nginx-node-websocket.conf) para `/etc/nginx/sites-available/SUBDOMINIO.game.ciatec.org`, trocar `SUBDOMINIO`, `PORTA` e o caminho do WebSocket, e então:

```bash
sudo ln -s /etc/nginx/sites-available/SUBDOMINIO.game.ciatec.org /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
sudo certbot --nginx -d SUBDOMINIO.game.ciatec.org
```

Sem `Upgrade`/`Connection` no `location` do WebSocket, a página abre mas o cliente nunca conecta.

### 3. Caller

```yaml
jobs:
  deploy:
    uses: ciatec-org/ciatec-devops/.github/workflows/deploy-node-service.yml@main
    with:
      service_name: meu-servico
      port: 8790
      health_path: /health
      ws_path: /ws
    secrets: inherit
```

Inputs opcionais mais usados:

| Input | Default | Quando mudar |
|-------|---------|--------------|
| `ws_message` / `ws_expect` | vazio | Validar o protocolo, não só o handshake (ex.: `'{"type":"ping"}'` / `pong`) |
| `artifact_paths` | `dist`, `server`, `package.json`, `package-lock.json` | Outra estrutura de pastas |
| `deploy_path` | `/opt/<service_name>` | Raramente |
| `test_command` / `build_command` | `npm test` / `npm run build` | Vazio para pular |
| `node_version` | vazio: lê `.nvmrc` / `.node-version`, senão `22` | Só para forçar uma versão diferente da do repo |
| `keep_backups` | `3` | Mais histórico de rollback |

### 4. Primeiro deploy

Push em `main` (ou Actions → Deploy → Run workflow). Se já existe um serviço com o mesmo nome instalado à mão, o workflow assume o controle: faz backup de `/opt/<service>` e da unit, e sobrescreve.

## Verificar

```bash
systemctl status meu-servico --no-pager
curl -fsS http://127.0.0.1:PORTA/health
tail -n 20 /var/log/ciatec/deploys.log
curl -I https://SUBDOMINIO.game.ciatec.org
```

No navegador: DevTools → Network → WS, a conexão em `/ws` deve ficar com status 101.

## Cuidados

- **Estado em memória some a cada deploy.** O `restart` derruba conexões e salas abertas. Em dia de evento, evite push em `main` ou troque o gatilho do caller para só `workflow_dispatch`.
- O smoke de WebSocket conversa com a produção de verdade: escolha uma mensagem sem efeito colateral relevante.
- Deploys do mesmo serviço são serializados (`concurrency`); um segundo push espera o primeiro terminar.

## Rollback manual

```bash
ls -d /opt/meu-servico.bak.*
sudo rsync -a --delete /opt/meu-servico.bak.TIMESTAMP/ /opt/meu-servico/
sudo install -m 0644 /opt/meu-servico.bak.TIMESTAMP.service /etc/systemd/system/meu-servico.service  # se existir
sudo systemctl daemon-reload && sudo systemctl restart meu-servico
```
