# Deploy de jogos Unity WebGL na AWS EC2

## 1. Pré-requisitos
- Jogo Unity exportado para WebGL.
- Pasta `Build/` e `index.html` commitados na raiz do repositório.
- Runner self-hosted operacional na EC2.
- Subdomínio criado no DNS, apontando para o IP público da EC2.

## 2. Configurar o deploy.yml
No repositório do jogo, criar ou ajustar `.github/workflows/deploy.yml`:

```yaml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  deploy:
    uses: ciatec-org/ciatec-devops/.github/workflows/deploy-webgl.yml@main
    with:
      game_name: nome-do-jogo
      deploy_path: /var/www/games/nome-do-jogo
      environment: production
    secrets: inherit
```

Usar um nome consistente para o jogo e seu diretório. Cada jogo deve ter seu próprio diretório.

## 3. Configurar o Nginx
Criar `/etc/nginx/sites-available/subdominio.game.ciatec.org`, adaptando o `server_name` e o caminho do jogo.

Configuração HTTP inicial:

```nginx
server {
    listen 80;
    server_name subdominio.game.ciatec.org;

    root /var/www/games/nome-do-jogo;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location ~* \.wasm\.gz$ {
        gzip off;
        default_type application/wasm;
        add_header Content-Encoding gzip always;
    }

    location ~* \.(data|js|framework)\.gz$ {
        gzip off;
        default_type application/octet-stream;
        add_header Content-Encoding gzip always;
    }
}
```

Habilitar e validar:

```bash
sudo ln -s /etc/nginx/sites-available/subdominio.game.ciatec.org /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## 4. Configurar HTTPS
Depois de confirmar que o DNS aponta para a EC2 e que a porta 80 está acessível:

```bash
sudo certbot --nginx -d subdominio.game.ciatec.org
```

## 5. Executar o deploy
Fazer push para `main` e acompanhar a execução em GitHub → Actions.

O workflow compartilhado valida `Build/`, cria o diretório de destino, faz backup da publicação anterior, sincroniza os arquivos, ajusta as permissões e recarrega o Nginx.

## 6. Validar a publicação

```bash
curl -I https://subdominio.game.ciatec.org
```

Conferir também o carregamento do jogo no navegador e erros no console.

## 7. Diagnóstico

```bash
sudo nginx -t
sudo tail -n 50 /var/log/nginx/error.log
sudo tail -n 50 /var/log/ciatec/deploys.log
```

Verificar também o log da execução no GitHub Actions.

## Cuidados importantes
- Nunca reutilizar o diretório de outro jogo.
- O `rsync --delete` remove arquivos do destino que não existam na origem.
- Não apagar diretórios de backup sem verificar sua necessidade.
- Confirmar DNS, certificado e configuração antes da publicação.
- Testar o Nginx antes de recarregá-lo.
- Se o jogo não tiver sido publicado, a ausência de `index.html` pode causar erro HTTP 500 com `try_files ... /index.html`. Isso não deve ser confundido com falha do certificado HTTPS.
