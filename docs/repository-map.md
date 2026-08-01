# Mapa do repositório

Documento vivo: atualizar sempre que uma pasta ou ferramenta for adicionada.

## Pastas

| Pasta | Propósito | Quando usar | Status |
|-------|-----------|-------------|--------|
| `.cursor/skills/` | Skills do agente (agile-pipeline) | Gerar Epics/Stories/Tasks | Ativo |
| `.github/workflows/` | Workflows reutilizáveis de CD | Deploy WebGL/Docker | Ativo |
| `scripts/deploy/` | Scripts de deploy no servidor | Docker Compose, migrações | Ativo |
| `scripts/health/` | Health checks | Pós-deploy / verificação | Ativo |
| `scripts/rollback/` | Rollback manual | Recuperação | Scaffold |
| `scripts/setup/` | Bootstrap GitHub Project | Seed de Issues/Project | Ativo |
| `docs/agile/` | Plano Agile deste repositório | Executar sprints do devops | Ativo |
| `docs/prompts/` | Prompt one-shot histórico | Scaffolding legado | Referência |
| `docs/specs/` | Specs do agile-pipeline | Formato Projects/roadmap | Ativo |
| `docs/COMO-CONECTAR-SEU-REPO.md` | Onboarding de repos produto | Plugar um jogo ou monorepo | Ativo |
| `docs/architecture.md` | Topologia da infra | Onboarding | Ativo |
| `docs/repository-map.md` | Este mapa | Orientar contribuidores | Ativo |
| `docs/runbooks/` | Procedimentos operacionais | Ops em produção | Ativo |
| `docs/templates/` | Callers de workflow | Copiar para repos produto | Ativo |
| `runners/` | Docs dos self-hosted runners | Instalar/diagnosticar | Scaffold |
| `monitoring/` | Observabilidade | Phase 4 | Placeholder |
| `terraform/` | IaC | Phase 5 | Placeholder |
| `ansible/` | Provisioning | Phase 6 | Placeholder |

## Como adicionar uma nova ferramenta

- [ ] Criar pasta em `scripts/{categoria}/` (ou domínio novo na raiz)
- [ ] Adicionar `README.md` na pasta
- [ ] Atualizar esta tabela
- [ ] Se for workflow: `.github/workflows/`
- [ ] Se for template de caller: `docs/templates/` + atualizar `COMO-CONECTAR-SEU-REPO.md`

## Ferramentas planejadas

| Ferramenta | Fase | Pasta |
|------------|------|-------|
| Prometheus / Grafana / Loki | Phase 4 | `monitoring/` |
| Terraform (EC2, RDS, Route53) | Phase 5 | `terraform/` |
| Ansible (provisioning) | Phase 6 | `ansible/` |
