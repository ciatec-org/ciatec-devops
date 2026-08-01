---
name: story-breaker
description: >
  Quebra um Epic em User Stories completas com critérios de aceite (BDD), estimativas
  em story points e metadados para GitHub Projects. Use este skill quando o usuário
  pedir para "detalhar um Epic", "criar as User Stories", "escrever as histórias de usuário",
  "quebrar o Epic em stories", ou quiser os critérios de aceite de uma entrega.
  Também dispara quando o usuário tiver um Epic já definido e quiser o próximo nível
  de detalhamento do backlog. Produz saída no formato CIATec/GitHub Projects.
---

# Story Breaker

## Objetivo
Transformar um Epic em User Stories bem formadas, com critérios de aceite em formato
BDD (Gherkin simplificado), estimativas em story points e metadados para GitHub Issues.

---

## Entradas esperadas

Fornecer ao menos:

| Campo | Obrigatório | Observação |
|---|---|---|
| Epic (título + descrição) | ✅ | Pode ser a saída do epic-generator |
| DoD do Epic | ✅ | Critérios de conclusão do Epic |
| Stack técnico relevante | ✅ | Para formular tasks técnicas adequadas |
| Perfis de usuário envolvidos | ⚠️ opcional | Se não fornecido, infere do contexto |
| Restrições técnicas específicas | ⚠️ opcional | Ex: "offline-first", "acessibilidade AA" |

---

## Anatomia de uma User Story (padrão CIATec)

```
Como [PERFIL DE USUÁRIO],
Quero [AÇÃO / FUNCIONALIDADE],
Para que [BENEFÍCIO / OBJETIVO].
```

**Regras do "Como"**: usar perfis reais do sistema (terapeuta, pesquisador, paciente,
administrador, IC) — nunca "usuário genérico".

**Regras do "Quero"**: verbo de ação concreto (visualizar, cadastrar, exportar, filtrar,
receber, configurar) — nunca "poder fazer algo".

**Regras do "Para que"**: benefício observável, não técnico.

---

## Processo de geração

### 1. Decomposição do Epic

Para cada Epic, identifique:
- **Happy paths**: fluxos principais que entregam valor direto
- **Edge cases críticos**: erros esperados, estados vazios, limites de dados
- **Perfis distintos**: se o mesmo fluxo tem comportamento diferente por perfil → stories separadas
- **Gatilhos de notificação/integração**: e-mails, webhooks, eventos que merecem story própria

**Tamanho ideal de uma story**: completável em **1–3 dias** por uma pessoa.
Se parecer maior → quebrar. Se parecer menor → agrupar com outra relacionada.

### 2. Estrutura completa de cada User Story

```markdown
## US-XX: [TÍTULO CONCISO]

**Epic:** EP-XX — [Título do Epic]
**Perfil:** [Terapeuta | Pesquisador | Paciente | Admin | Sistema]
**Story Points:** [1 | 2 | 3 | 5 | 8 | 13] — usar Fibonacci
**Prioridade:** [P1 | P2 | P3 | P4]
**Sprint sugerido:** [S1 | S2 | S3 | ...] (baseado na ordem lógica)

### História
Como [perfil],
Quero [ação],
Para que [benefício].

### Contexto / notas de UX
[Informações que ajudam o dev a entender o contexto sem ambiguidade.
Mockups, fluxos relacionados, regras de negócio implícitas.]

### Critérios de aceite

**Cenário 1: [Nome do cenário — happy path]**
- **Dado** [pré-condição]
- **Quando** [ação do usuário]
- **Então** [resultado esperado]
- **E** [resultado adicional, se houver]

**Cenário 2: [Nome do cenário — validação / erro]**
- **Dado** [pré-condição]
- **Quando** [ação inválida ou erro]
- **Então** [comportamento do sistema]

**Cenário 3: [Nome do cenário — edge case]**
[Repetir formato acima]

### Definition of Ready (antes de entrar no sprint)
- [ ] Mockup ou wireframe aprovado (se UI)
- [ ] Regras de negócio confirmadas com PO/pesquisador
- [ ] Dependências técnicas identificadas
- [ ] Story points estimados em refinamento

### Labels GitHub sugeridas
`user-story` + `domain:[domínio]` + `priority:[p1|p2|p3|p4]` + `sp:[pontos]`
```

---

## Tabela de referência: Story Points (CIATec)

| Points | Complexidade | Tempo estimado | Exemplos |
|--------|-------------|----------------|---------|
| 1 | Trivial | 2–4h | Alterar texto de label, adicionar validação simples |
| 2 | Simples | 4–8h | CRUD de um campo, página estática com dados |
| 3 | Moderada | 1–2 dias | Fluxo completo de cadastro, integração simples |
| 5 | Complexa | 2–3 dias | Upload + processamento de arquivo, relatório com filtros |
| 8 | Alta | 3–5 dias | Integração com serviço externo, algoritmo complexo |
| 13 | Muito alta | 1 semana+ | **Sinal de alerta: considerar quebrar a story** |

---

## Regras de qualidade

- **Mínimo 2 cenários BDD** por story (happy path + ao menos 1 erro/validação)
- **Máximo 8 stories por Epic** em primeira estimativa — se precisar de mais, reavalie se o Epic deveria ser dividido
- **Nunca** misturar 2 perfis de usuário distintos na mesma story
- Stories com SP ≥ 8 devem ter justificativa explícita ou ser marcadas com `needs-split`
- Para projetos de pesquisa: incluir story de **exportação de dados** e **auditoria** em Epics de coleta
- Stories de **acessibilidade** e **internacionalização** não são tasks — são critérios de aceite dentro das stories funcionais

---

## Saída final

1. **Lista completa de User Stories** com o formato acima
2. **Tabela de velocidade estimada**: total de story points por sprint sugerido
3. **Mapa de dependências entre stories** (qual story bloqueia qual)
4. **Riscos identificados**: stories com incerteza técnica alta (marcar com `needs-spike`)

---

## Quando criar um Spike ao invés de uma Story

Crie um **Spike** (investigação técnica) quando:
- A estimativa variar mais de 3× dependendo da abordagem
- A stack não foi validada para o caso de uso
- Há dependência de decisão de arquitetura ainda em aberto

```markdown
## SPIKE-XX: [TÍTULO]
**Time-box:** [2h | 4h | 1 dia]
**Objetivo:** [Pergunta específica a responder]
**Saída esperada:** [Decisão documentada / PoC / ADR]
```

---

## Próximos passos

Informe o usuário que pode:
1. Usar o skill **task-breaker** (`.cursor/skills/task-breaker/SKILL.md`) para detalhar qualquer User Story em Tasks técnicas
2. Consultar `docs/specs/spec-github-projects.md` para estrutura de importação em CSV/JSON
