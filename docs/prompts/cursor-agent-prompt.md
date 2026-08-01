# Cursor Agent Prompt — ciatec-devops Scaffolding

Cole este prompt no chat do Cursor com o repositório `ciatec-devops` aberto.

---

## Prompt

Você é um agente DevOps trabalhando no repositório `ciatec-devops` do CIATec.

Sua tarefa é criar a estrutura completa do repositório em três etapas sequenciais. Execute cada etapa antes de passar para a próxima.

---

### Etapa 1 — Estrutura de pastas

Crie a seguinte estrutura de diretórios. Todo diretório vazio deve ter um `README.md` mínimo explicando seu propósito e quando será usado:

```
.github/workflows/
scripts/
  deploy/
  health/
  rollback/
  setup/
runners/
docs/
  runbooks/
monitoring/
terraform/
ansible/
```

Regras:
- `.gitignore` cobrindo: `.env`, `*.pem`, `*.key`, `*.log`, `__pycache__`, `node_modules`
- Todos os arquivos: UTF-8, LF line endings
- `README.md` raiz atualizado com a estrutura real e link para `docs/repository-map.md`

---

### Etapa 2 — Mapa do repositório (autodocumentação)

Crie o arquivo `docs/repository-map.md`.

Este documento descreve o propósito de cada pasta e deve ser atualizado sempre que uma nova pasta ou ferramenta for adicionada ao repositório.

O arquivo deve ter:
1. Tabela com colunas: Pasta | Propósito | Quando usar | Status
2. Seção "Como adicionar uma nova ferramenta" com checklist:
   - Criar pasta em `scripts/{categoria}/`
   - Adicionar README.md na pasta
   - Atualizar esta tabela
   - Se for workflow GitHub Actions: adicionar em `.github/workflows/`
   - Se for script de setup único: adicionar em `scripts/setup/`
3. Seção "Ferramentas planejadas" listando o backlog futuro (Terraform, Ansible, Prometheus, Grafana)

Preencha a tabela com o estado atual do repositório após a Etapa 1.

---

### Etapa 3 — Script de setup do GitHub Projects

Crie o arquivo `scripts/setup/setup-github-project.py`.

Este script lê `docs/agile-plan.md` (se existir) ou usa dados hardcoded como fallback, e popula um GitHub Project via API GraphQL.

**Dependências:** `requests`, `python-dotenv`

**Configuração via `.env`:**
```
GITHUB_TOKEN=ghp_...
GITHUB_ORG=nome-da-org        # ou GITHUB_USER para conta pessoal
GITHUB_REPO=ciatec-devops
PROJECT_TITLE=CIATec DevOps
```

**O script deve:**

1. Criar um Project (Projects V2) na organização/usuário
2. Criar campos customizados no Project:
   - `Sprint` (tipo: iteration)
   - `Epic` (tipo: single_select com as opções do plano)
   - `Status` (tipo: single_select: Backlog | In Progress | Done)
   - `Priority` (tipo: single_select: High | Medium | Low)
3. Para cada story do plano, criar uma Issue no repositório com:
   - Título: `[Epic ID] Story title`
   - Body: acceptance criteria formatados como checklist GitHub (`- [ ] item`)
   - Label: nome do épico (criar a label se não existir)
4. Adicionar cada Issue ao Project com os campos preenchidos
5. Ao final, imprimir URL do Project criado

**Estrutura do script:**
- Funções separadas por responsabilidade: `create_project()`, `create_fields()`, `create_issue()`, `add_to_project()`
- Tratamento de erro com mensagens claras
- Flag `--dry-run` que imprime o que seria criado sem chamar a API
- Log de cada operação com ✅ ou ❌

**Dados hardcoded de fallback** (usar se `agile-plan.md` não existir):

```python
EPICS = [
    {"id": "E1", "name": "Estrutura base do repositório"},
    {"id": "E2", "name": "Pipeline Unity WebGL"},
    {"id": "E3", "name": "Pipeline Docker"},
    {"id": "E4", "name": "Migrações e banco"},
    {"id": "E5", "name": "Health checks e rollback"},
]

STORIES = [
    {"epic": "E1", "sprint": 1, "title": "Estrutura de diretórios", "priority": "High"},
    {"epic": "E1", "sprint": 1, "title": "Documentação de arquitetura", "priority": "Medium"},
    {"epic": "E2", "sprint": 2, "title": "Workflow deploy-webgl.yml", "priority": "High"},
    {"epic": "E2", "sprint": 2, "title": "Caller workflow para cada jogo", "priority": "High"},
    {"epic": "E3", "sprint": 3, "title": "Script deploy-docker.sh", "priority": "High"},
    {"epic": "E3", "sprint": 3, "title": "Workflow deploy-docker.yml", "priority": "High"},
    {"epic": "E3", "sprint": 3, "title": "Caller workflow monorepo", "priority": "Medium"},
    {"epic": "E4", "sprint": 4, "title": "Script run-migrations.sh", "priority": "High"},
    {"epic": "E5", "sprint": 4, "title": "Scripts de health check", "priority": "Medium"},
]
```

Após criar o script, crie também `scripts/setup/README.md` explicando:
- O que o script faz
- Como configurar o `.env`
- Como rodar: `python setup-github-project.py` e `python setup-github-project.py --dry-run`
- Como obter o `GITHUB_TOKEN` (link para docs GitHub)

---

### Validação final

Após as 3 etapas, execute:
```bash
find . -name "*.md" | head -20
find . -name "*.py" | head -10
find . -name "*.yml" | head -10
```

E confirme que a estrutura está completa listando todos os arquivos criados.
