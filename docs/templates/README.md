# Templates

Templates de workflows caller para copiar nos repositórios de produto (jogos, monorepo).

| Template | Quando |
|----------|--------|
| `game-deploy-caller.yml` | Jogo WebGL |
| `node-service-deploy-caller.yml` | Serviço Node.js com WebSocket (`deploy-node-service`) |
| `nginx-node-websocket.conf` | Vhost Nginx do serviço Node (copiar para a EC2, uma vez) |
| `monorepo-deploy-caller.yml` | Clone permanente no host (`deploy-compose`) |
| `compose-checkout-deploy-caller.yml` | Sem clone permanente (`deploy-compose-checkout`) |

Usar quando: conectar um novo repositório ao CD centralizado deste repo.
