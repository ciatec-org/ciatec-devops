# Setup — GitHub Project a partir de um plano Agile

## `setup-github-project.py`

Lê um plano markdown (ou usa fallback hardcoded) e popula um GitHub Project v2 com Issues.

### Configuração

Crie `.env` na raiz de `ciatec-agile-pipeline` (ou ao lado deste script):

```
GITHUB_TOKEN=...
GITHUB_ORG=ciatec-org
# ou GITHUB_USER=...
GITHUB_REPO=nome-do-repo
PROJECT_TITLE=Nome do Project
```

Token: escopos `repo` + `project` (classic) ou fine-grained com Organization Projects R/W + Issues Write.

### Como rodar

```bash
pip install -r requirements.txt
python setup-github-project.py --dry-run
python setup-github-project.py
python setup-github-project.py --project-number 1   # reutilizar Project existente
```

### Notas

- O campo `Status` é nativo do Projects v2 — o script reutiliza, não recria.
- Sem `--project-number`, cria um Project novo a cada execução.
