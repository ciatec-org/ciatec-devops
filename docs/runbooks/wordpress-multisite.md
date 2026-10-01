# Runbook: rede WordPress multisite

Deploy da rede `ciatec-wordpress-network` e dos sites (um repositório por site) na EC2 institucional (`3.150.28.236`, Nginx no host, stack em `127.0.0.1:8082`).

Definição da rede (compose, `mu-plugins`, `plugins.txt`, docs): repositório `ciatec-wordpress-network`. Tudo que executa no servidor: este repositório.

## Workflows

| Workflow | Chamado por | O que faz |
|---|---|---|
| `deploy-wordpress-site.yml` | repo do site, push em `main` | Sincroniza `themes/<tema>` para `site_dir` (o que a rede monta). Não reinicia nada |
| `deploy-wordpress-network.yml` | repo da rede, push em `main` | Preflight, backup (banco + arquivos), `compose pull` + `up -d`, health check, smoke do WP-CLI |

Callers prontos em `docs/templates/wordpress-*-deploy-caller.yml`.

## Layout no servidor

```
/home/ubuntu/wordpress-multisite/   stack da rede (compose, .env só aqui, mu-plugins)
/home/ubuntu/ciatec-wordpress/      árvore do site ciatec.org (só o tema é sincronizado)
/home/ubuntu/backups/wordpress-multisite/   backups pré-deploy (retenção 14 dias)
```

O `.env` (`DB_PASSWORD`, `DB_ROOT_PASSWORD`) existe só no servidor, com `chmod 600`. Nenhum workflow o lê ou imprime.

## Aplicar pela primeira vez (mexe em produção, com um humano acompanhando)

Risco: o `create_host_path: false` do compose nunca foi exercitado, então o primeiro `up` é o teste real. Não pule o backup nem a reversão.

1. Backup manual do banco e dos arquivos (comandos em `ciatec-wordpress-network/docs/wordpress-multisite/deploy-e-backup.md`).
2. Registrar o runner `ciatec-wordpress-production` (site) e `ciatec-wordpress-network-production` (rede), usuário `ubuntu` na EC2, no nível da organização, num grupo de runners restrito aos repositórios `ciatec-wordpress-network` e `ciatec-wordpress`. Não compartilhar com outros stacks.
3. Fazer o deploy do **site** primeiro (Actions, `workflow_dispatch` no repo do site): cria `site_dir` com o tema.
4. Confirmar que `/home/ubuntu/wordpress-multisite/.env` existe (copiado da pasta antiga, `chmod 600`). Sem ele o compose sobe com senhas vazias.
5. Deploy da **rede** (`workflow_dispatch` no repo da rede). Só o WordPress é recriado, com alguns segundos fora do ar. Volumes intactos.
6. Verificar: `docker compose ps`, `https://ciatec.org` e `docker compose run --rm wpcli wp theme list --url=ciatec.org` mostrando `ciatec`.
7. Só depois, ativar o tema: `docker compose run --rm wpcli wp theme activate ciatec --url=ciatec.org`.

`/home/ubuntu/wordpress-multisite` é a pasta atual do stack **e** o destino do deploy: não arquivar nem apagar. Só garanta que o `.env` dela continua lá.

Reversão: restaurar o compose anterior na mesma pasta e `docker compose up -d` (mesmos volumes). Se o tema foi ativado, `wp theme activate twentytwentyfive --url=ciatec.org`. Restauração de banco e arquivos: mesmo documento do passo 1.

## Segurança do runner

Runner com acesso ao Docker equivale a root na EC2, que também hospeda DIIA, HINT e outros stacks.

- Os callers disparam só em `push` para `main` e `workflow_dispatch`, nunca em `pull_request`.
- Só repositórios privados com `main` protegido podem usar o runner (grupo restrito da organização).
- Se o plano da organização permitir, usar um Environment `production` com aprovação obrigatória antes do deploy (não está configurado nos workflows).
- Deploys são serializados por `concurrency` (por repositório) e por um lock no host (`/home/ubuntu/.locks/wordpress-deploy.lock`) que impede site e rede de rodarem juntos, mesmo com dois runners. Se um runner morrer com o lock, ele expira em 60 min.

## Cuidados no primeiro deploy

- Fazer o backup manual antes: o backup do workflow ainda não foi testado num servidor real.
- O primeiro deploy é um `workflow_dispatch` supervisionado.
- Disco: a EC2 tem cerca de 12 GB livres. Acompanhar o tamanho de `/home/ubuntu/backups/wordpress-multisite` nos primeiros dias (retenção de 14 dias).
- O `rsync --delete` da rede preserva `.env` e `backups/`, e o workflow recusa um `backup_dir` dentro de `deploy_path`.

## Regras

- Nunca `docker compose down -v`, `docker system prune` nem `docker volume prune` neste servidor. Os outros stacks (`hintconference`, `ciatec-ht`, `diia-*`) estão fora do escopo.
- Mudança na rede afeta todos os sites: PR dedicado, com impacto e reversão.
- O workflow do site nunca toca em pastas de outros sites, plugins do painel, uploads nem no banco.

## Ainda não existe

- Backup agendado para o S3 (hoje só o backup pré-deploy, 14 dias, no disco da EC2).
- Staging (`staging.ciatec.org`, porta reservada `127.0.0.1:8083`).
- Blocos do Nginx e certbot versionados. Hoje são aplicados à mão por um humano (`docs/wordpress-multisite/adicionar-site.md` na rede).
- Instalação dos plugins da rede por workflow (`scripts/install-plugins.sh` da rede roda à mão).
