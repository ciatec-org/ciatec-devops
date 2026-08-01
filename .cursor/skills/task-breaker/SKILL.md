---
name: task-breaker
description: >
  Quebra uma User Story em Tasks técnicas concretas e atribuíveis, com estimativas
  em horas, camada da stack e dependências entre tasks. Use este skill quando o usuário
  pedir para "detalhar a story em tasks", "criar as tarefas técnicas", "quebrar em subtarefas",
  "o que precisa ser feito para implementar essa história" ou quiser um plano de implementação
  detalhado. Também dispara quando o usuário quiser atribuir trabalho a membros do time
  ou planejar a implementação técnica de uma feature. Produz GitHub Issues com checklist.
---

# Task Breaker

## Objetivo
Transformar uma User Story em Tasks técnicas discretas, atribuíveis a uma pessoa,
completáveis em até 1 dia, com estimativas em horas e prontas para virar sub-issues
no GitHub Projects.

---

## Entradas esperadas

| Campo | Obrigatório | Observação |
|---|---|---|
| User Story completa | ✅ | Com critérios de aceite |
| Stack técnico | ✅ | Para gerar tasks na camada correta |
| Perfis do time disponível | ⚠️ opcional | Dev, pesquisador, IC, designer |
| Padrões de código do projeto | ⚠️ opcional | Ex: "temos pattern de repository", "usamos pytest" |

---

## Camadas de Tasks (CIATec Stack)

Organize as tasks pelas camadas da stack. Sempre verificar quais são relevantes para a story:

| Camada | Tags | Quem executa |
|--------|------|-------------|
| Frontend (React/Next.js) | `layer:frontend` | Dev frontend / IC |
| Backend (FastAPI/Node) | `layer:backend` | Dev backend |
| Banco de dados | `layer:database` | Dev backend / DBA |
| Infra / AWS / IaC | `layer:infra` | Dev DevOps / Sênior |
| LangGraph / AI | `layer:ai` | Dev + Pesquisador |
| Testes | `layer:tests` | Quem implementou |
| Documentação | `layer:docs` | Quem implementou |
| Pesquisa / Protocolo | `layer:research` | Pesquisador / Mestrando |
| UX / Design | `layer:ux` | Designer / IC |

---

## Estrutura de cada Task

```markdown
### TASK-XX: [TÍTULO TÉCNICO ESPECÍFICO]

**Story:** US-XX — [Título da story]
**Camada:** [layer:frontend | layer:backend | layer:database | ...]
**Estimativa:** [1h | 2h | 4h | 8h]
**Perfil sugerido:** [Dev | IC | Pesquisador | Designer]
**Depende de:** [TASK-XX, ou "Nenhuma"]
**Bloqueia:** [TASK-XX, ou "Nenhuma"]

**Descrição técnica:**
[O que exatamente precisa ser feito, com referências à arquitetura/padrão do projeto.
Específico o suficiente para um IC conseguir executar sem precisar perguntar o quê fazer.]

**Checklist de implementação:**
- [ ] Sub-passo 1
- [ ] Sub-passo 2
- [ ] Sub-passo 3

**Critério de conclusão:**
[Como o implementador sabe que terminou? Test passa? PR aprovado? Endpoint respondendo?]

**Labels GitHub:**
`task` + `layer:[camada]` + `[perfil]`
```

---

## Processo de decomposição

### 1. Ler os critérios de aceite da story

Cada critério de aceite (cenário BDD) tende a gerar um conjunto de tasks. Percorra:
- **Cenário happy path** → tasks de implementação principal
- **Cenários de erro/validação** → tasks de tratamento de erro e feedback ao usuário
- **Edge cases** → tasks de validação e testes

### 2. Tasks obrigatórias por tipo de feature

**Feature com UI:**
- [ ] Componente React / tela
- [ ] Integração com API (service/hook)
- [ ] Tratamento de loading, erro e estado vazio
- [ ] Testes de componente (React Testing Library)
- [ ] Responsividade / acessibilidade (se aplicável)

**Endpoint de API:**
- [ ] Schema/modelo de dados (Pydantic ou equivalente)
- [ ] Lógica de negócio / service
- [ ] Rota e controller
- [ ] Testes unitários do service
- [ ] Teste de integração do endpoint
- [ ] Documentação OpenAPI (docstring ou decorator)

**Migração de banco:**
- [ ] Script de migração (Alembic ou equivalente)
- [ ] Seed de dados de teste (se necessário)
- [ ] Rollback documentado

**Integração com serviço externo (AWS, Sentry, etc.):**
- [ ] Configuração de credenciais/secrets
- [ ] Implementação do client/wrapper
- [ ] Tratamento de timeout e retry
- [ ] Mock para testes
- [ ] Documentação de configuração

**Feature com LangGraph / IA:**
- [ ] Definição do grafo de estados
- [ ] Implementação dos nós (nodes)
- [ ] Implementação das arestas/condicionais
- [ ] Prompt engineering e templates
- [ ] Testes com casos reais e sintéticos
- [ ] Logging e observabilidade (Sentry ou equivalente)

### 3. Tasks de qualidade (sempre incluir)

Para toda story com código novo:
- **Revisão de PR**: não é task — é processo. Não listar.
- **Testes**: são tasks — listar explicitamente na camada correta.
- **Documentação interna**: listar se a feature for de infraestrutura ou API pública.

---

## Regras de tamanho

| Estimativa | Critério |
|-----------|---------|
| 1h | Configuração trivial, ajuste de texto/estilo, fix de bug simples |
| 2h | Componente simples, endpoint CRUD básico |
| 4h | Feature com lógica de negócio, integração simples |
| 8h | Feature complexa, integração com serviço externo, algoritmo |
| > 8h | **Não é task** — quebrar em subtasks menores |

**Regra de ouro**: se um IC recém-chegado ao projeto não consegue completar a task
em um dia, é grande demais.

---

## Saída final

1. **Lista completa de tasks** com o formato acima
2. **Diagrama de dependências** (Mermaid) entre tasks — útil para paralelismo
3. **Distribuição por perfil**: quais tasks são para dev, IC, pesquisador
4. **Estimativa total da story**: soma em horas + conversão em dias de trabalho
5. **Tasks paralelas**: identificar quais podem ser feitas simultaneamente

---

## Exemplo de sequência (fragmento)

```
Story: US-03 — Exportar dados de sessão em CSV

TASK-01: Definir schema de exportação (layer:backend, 2h)
TASK-02: Implementar service de exportação com filtros (layer:backend, 4h) → depende de TASK-01
TASK-03: Endpoint GET /sessions/export (layer:backend, 2h) → depende de TASK-02
TASK-04: Anonimização de dados conforme LGPD (layer:backend, 4h) → depende de TASK-01
TASK-05: Botão e fluxo de download no frontend (layer:frontend, 3h) → depende de TASK-03
TASK-06: Testes do service de exportação (layer:tests, 2h) → depende de TASK-02
TASK-07: Teste E2E do download (layer:tests, 2h) → depende de TASK-05

Total: ~19h (~2,5 dias com 1 dev)
Paralelo possível: TASK-04 pode rodar junto com TASK-03
```

---

## Atenção para projetos CIATec

- **Jogos terapêuticos**: incluir tasks de acessibilidade, testes com usuários-alvo (se fase de pesquisa)
- **Coleta de dados clínicos**: incluir task de **auditoria/log** em toda feature que toca dados do paciente
- **LangGraph pipelines**: sempre incluir task de observabilidade (trace, log de erros) — integrar com Sentry
- **GitHub Actions**: tasks de CI/CD devem especificar o workflow file afetado
