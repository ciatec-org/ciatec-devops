---
name: agile-pipeline
description: >
  Pipeline completo que transforma um descritivo de projeto em toda a estrutura Agile:
  Epics, User Stories, Tasks, critérios de aceite, estimativas e roadmap — no formato
  GitHub Projects do CIATec. Use este skill quando o usuário fornecer um briefing de
  projeto e pedir para "gerar a estrutura Agile", "criar o backlog completo", "planejar
  o projeto", "gerar Epics e stories", "estruturar o projeto no GitHub Projects" ou
  qualquer variação. Orquestra os skills epic-generator, story-breaker e task-breaker,
  e os specs spec-github-projects e spec-roadmap em sequência coesa.
---

# Agile Pipeline — Orquestrador

## O que este pipeline produz

A partir de um descritivo em linguagem natural, gera:

1. **Epics** com DoD, estimativas e prioridades
2. **User Stories** com critérios de aceite BDD e story points
3. **Tasks técnicas** com estimativas em horas e camadas da stack
4. **Roadmap** com milestones, diagrama Gantt e gestão de capacidade
5. **Artefatos de importação** para GitHub Projects (labels, milestones, Issues)

---

## Entradas que o usuário deve fornecer

Antes de começar, confirme que tem:

```
✅ Descritivo do projeto (linguagem livre, pode ser longo)
✅ Stack técnico ("React + FastAPI + AWS" etc.)
⚠️  Restrições e dependências (CEP, datas, integrações externas)
⚠️  Prioridades iniciais ("MVP em 3 meses, foco em X")
⚠️  Composição do time (quantas pessoas, quais perfis)
```

Se algum item obrigatório faltar, pergunte antes de prosseguir.

---

## Fluxo do pipeline

```
[Descritivo] 
    ↓
[Etapa 1] epic-generator     → Lista de Epics com DoD e estimativas
    ↓ (aprovação do usuário)
[Etapa 2] story-breaker      → User Stories com critérios de aceite BDD
    ↓ (por Epic ou tudo de uma vez)
[Etapa 3] task-breaker       → Tasks técnicas com horas e dependências
    ↓
[Etapa 4] spec-roadmap       → Roadmap com milestones e Gantt
    ↓
[Etapa 5] spec-github-projects → Artefatos de importação (labels, CSV)
```

---

## Modo de operação

### Modo Completo (padrão)
Executa todas as etapas em sequência, pedindo aprovação entre Epics e Stories.
Ideal para projetos novos ou grandes reestruturações.

### Modo por Etapa
O usuário pode invocar cada etapa individualmente:
- "Gera só os Epics" → usar skill epic-generator diretamente
- "Detalha este Epic em stories" → usar skill story-breaker
- "Quebra esta story em tasks" → usar skill task-breaker
- "Gera o roadmap" → usar spec-roadmap

### Modo Incremental
Para projetos existentes, o usuário pode fornecer Epics já definidos
e pedir só stories, ou stories já definidas e pedir só tasks.

---

## Passo 1: Executar epic-generator

Ler e seguir `.cursor/skills/epic-generator/SKILL.md`.
Também ler `docs/specs/context-ciatec.md` quando o projeto for do CIATec.

Ao final, apresentar a lista de Epics e perguntar:
- "Os Epics fazem sentido? Algum para ajustar, dividir ou remover?"
- "Quer que eu detalhe todos em stories, ou começamos por algum específico?"

---

## Passo 2: Executar story-breaker

Para cada Epic aprovado, ler e seguir `.cursor/skills/story-breaker/SKILL.md`.

Ao final de cada Epic, apresentar as stories e perguntar:
- "As stories cobrem todos os critérios de aceite do Epic?"
- "Alguma story parece grande demais (SP ≥ 8) que deveria ser dividida?"

---

## Passo 3: Executar task-breaker

Para cada story prioritária (P1 e P2 no mínimo), ler e seguir `.cursor/skills/task-breaker/SKILL.md`.

Foco: stories do primeiro sprint ou as desbloqueadoras de outras.
Para stories P3/P4, tasks podem ser geradas sob demanda depois.

---

## Passo 4: Gerar roadmap

Ler e seguir `docs/specs/spec-roadmap.md`.

Produzir:
- Diagrama Mermaid gantt
- Tabela de Epics por fase
- Cálculo de capacidade se o time foi informado
- CSV de milestones

---

## Passo 5: Gerar artefatos de importação

Ler e seguir `docs/specs/spec-github-projects.md`.

Produzir:
- Lista de labels para criar (com cores)
- CSV de Issues prontas para importação
- Instruções de configuração do GitHub Project v2

---

## Saída final consolidada

Organizar toda a saída em seções claras:

```markdown
# [Nome do Projeto] — Estrutura Agile

## Sumário executivo
- N Epics | N User Stories | N Tasks
- Total: ~X story points | ~Y horas de desenvolvimento
- Prazo estimado: Z semanas com o time informado

## Epics
[...]

## User Stories por Epic
[...]

## Tasks por Story (Sprints 1–2)
[...]

## Roadmap
[Diagrama Mermaid]
[Tabela de Milestones]

## Instruções de importação no GitHub
[...]
```

---

## Referências

- Skills de geração: `.cursor/skills/epic-generator/SKILL.md`, `.cursor/skills/story-breaker/SKILL.md`, `.cursor/skills/task-breaker/SKILL.md`
- Specs de formato: `docs/specs/spec-github-projects.md`, `docs/specs/spec-roadmap.md`, `docs/specs/context-ciatec.md`
- Stacks: `docs/specs/stack-fastapi.md`, `docs/specs/stack-react.md`, `docs/specs/spec-design.md`
