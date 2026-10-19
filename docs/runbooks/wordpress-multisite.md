# Runbook: rede WordPress multisite

Deploy da rede `ciatec-wordpress-network` e dos sites (um repositório por site) na EC2 institucional (`3.150.28.236`, Nginx no host, stack em `127.0.0.1:8082`).

**Estado: em produção desde 01/10/2026.** O `ciatec.org` roda o tema `ciatec` sobre o `hello-elementor`, publicado por estes workflows. Em migração: o site `hint.ciatec.org` (tema `hint`, repositório `hint-wordpress`), vindo do stack standalone `hintconference`.

Definição da rede (compose, `mu-plugins`, `plugins.txt`, docs): repositório `ciatec-wordpress-network`. Tudo que executa no servidor: este repositório.

## Workflows

| Workflow | Chamado por | O que faz |
|---|---|---|
| `deploy-wordpress-site.yml` | repo do site, push em `main` | Sincroniza `themes/<tema>` para `site_dir` (o que a rede monta). Não reinicia nada |
| `deploy-wordpress-network.yml` | repo da rede, push em `main` | Preflight, backup (banco + arquivos), `rsync`, checagem de que o compose monta o tema, `compose pull` + `up -d`, health check, smoke do WP-CLI, habilitar e ativar o tema (idempotente) |

Callers prontos em `docs/templates/wordpress-*-deploy-caller.yml`.

## Layout no servidor

```
/home/ubuntu/wordpress-multisite/   stack da rede (compose, .env só aqui, mu-plugins)
/home/ubuntu/ciatec-wordpress/      árvore do site ciatec.org (só o tema é sincronizado)
/home/ubuntu/hint-wordpress/        árvore do site hint.ciatec.org (só o tema é sincronizado)
/home/ubuntu/backups/wordpress-multisite/   backups pré-deploy (retenção 14 dias)
/home/ubuntu/.locks/                lock de deploy (site e rede nunca rodam juntos)
```

O `.env` (`DB_PASSWORD`, `DB_ROOT_PASSWORD`) existe só no servidor, com `chmod 600`. Nenhum workflow o lê ou imprime.

## Como foi aplicado (e como repetir para outro site ou para reconstruir)

Feito em 01/10/2026, com um humano acompanhando. Os passos valem para um site novo ou para reconstruir a rede:

1. Backup manual do banco e dos arquivos (comandos em `ciatec-wordpress-network/docs/wordpress-multisite/deploy-e-backup.md`).
2. Runner registrado, usuário `ubuntu`. **O label precisa existir de fato**: o `runs-on` casa com labels, não com o nome do runner. Labels em uso: `ciatec-wordpress-production` (site ciatec.org) e `ciatec-wordpress-network-production` (rede), registrados no nível da organização num grupo restrito aos repositórios da rede e do site. Exceção: `hint-wordpress-production` (site hint.ciatec.org) está registrado **no próprio repositório** `hint-wordpress`, não no grupo da organização — mesma EC2 e mesmo usuário `ubuntu`, só o nível de registro muda.
3. `.env` em `/home/ubuntu/wordpress-multisite` (`chmod 600`). Sem ele o compose sobe com senhas vazias.
4. Deploy do **site** primeiro: cria `site_dir` com o tema. O preflight da rede exige `themes/ciatec/style.css` lá.
5. Deploy da **rede**: recria só o WordPress (alguns segundos fora do ar, **para todos os sites**), volumes intactos, e habilita e ativa o tema no fim.
6. Verificar: `docker compose ps`, o site no navegador e `docker compose run --rm wpcli wp theme list --url=<site>`.

`/home/ubuntu/wordpress-multisite` é a pasta do stack **e** o destino do deploy: não arquivar nem apagar. Só garanta que o `.env` dela continua lá.

Reversão: restaurar o compose anterior na mesma pasta e `docker compose up -d` (mesmos volumes). Se o tema foi ativado, `wp theme activate twentytwentyfive --url=ciatec.org`. Restauração de banco e arquivos: mesmo documento do passo 1.

## Segurança do runner

Runner com acesso ao Docker equivale a root na EC2, que também hospeda DIIA, HINT e outros stacks.

- Os callers disparam só em `push` para `main` e `workflow_dispatch`, nunca em `pull_request`.
- Só repositórios privados com `main` protegido podem usar o runner (grupo restrito da organização, ou, no caso do `hint-wordpress`, o runner de repositório próprio).
- Se o plano da organização permitir, usar um Environment `production` com aprovação obrigatória antes do deploy (não está configurado nos workflows).
- Deploys são serializados por `concurrency` (por repositório) e por um lock no host (`/home/ubuntu/.locks/wordpress-deploy.lock`) que impede site e rede de rodarem juntos, mesmo com dois runners. Se um runner morrer com o lock, ele expira em 60 min.

## Lições e cuidados

- **Ordem dos merges importa.** Cada merge no `main` da rede dispara um deploy com o que estiver no `main` naquele instante. Em 01/10/2026 o caller foi mergeado 11 s antes da mudança de compose com os mounts: o primeiro run recriou o WordPress com o compose antigo (sem mounts) e falhou no passo do tema; o run seguinte, já com os mounts, passou. Por isso o workflow agora recusa o `up -d` se o compose não montar o tema, e a regra é: mergear o compose antes do caller.
- O deploy da rede **não instala plugins**: `plugins.txt` e `scripts/install-plugins.sh` da rede são rodados à mão por um humano. Mexer em `plugins.txt` ainda dispara um deploy (recria o WordPress).
- O `rsync --delete` da rede apaga qualquer arquivo solto em `/home/ubuntu/wordpress-multisite` que não esteja no repositório; preserva `.env` e `backups/`, e o workflow recusa um `backup_dir` dentro de `deploy_path`.
- Disco: a EC2 tem cerca de 12 GB livres. Acompanhar o tamanho de `/home/ubuntu/backups/wordpress-multisite` (retenção de 14 dias).
- Todo deploy novo de um tipo que ainda não rodou: usar `workflow_dispatch` e acompanhar o log.

## Regras

- Nunca `docker compose down -v`, `docker system prune` nem `docker volume prune` neste servidor. Os outros stacks (`hintconference`, `ciatec-ht`, `diia-*`) estão fora do escopo.
- Mudança na rede afeta todos os sites: PR dedicado, com impacto e reversão.
- O workflow do site nunca toca em pastas de outros sites, plugins do painel, uploads nem no banco.

## Ainda não existe

- Backup agendado para o S3 (hoje só o backup pré-deploy, 14 dias, no disco da EC2).
- Staging (`staging.ciatec.org`, porta reservada `127.0.0.1:8083`).
- Blocos do Nginx e certbot versionados. Hoje são aplicados à mão por um humano (`docs/wordpress-multisite/adicionar-site.md` na rede).
- Instalação dos plugins da rede por workflow (`scripts/install-plugins.sh` da rede roda à mão).
