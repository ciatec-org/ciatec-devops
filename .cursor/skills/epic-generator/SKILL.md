---
name: epic-generator
description: >
  Gera Epics Agile completos a partir de um descritivo de projeto em linguagem natural.
  Use este skill sempre que o usuário fornecer um briefing, descritivo ou escopo de projeto
  e pedir para gerar Epics, estrutura Agile, backlog inicial, ou decomposição de alto nível.
  Também dispara quando o usuário mencionar "planejar o projeto", "criar o backlog" ou
  "estruturar as entregas". Produz saída no formato compatível com GitHub Projects (CIATec).
---

# Epic Generator

## Objetivo
Transformar um descritivo livre de projeto em Epics bem definidos, com metadados prontos
para importação no GitHub Projects do CIATec.

---

## Entradas esperadas

O usuário deve fornecer (pode ser em linguagem natural, não precisa ser estruturado):

| Campo | Obrigatório | Exemplo |
|---|---|---|
| Descritivo do projeto | ✅ | "Jogo terapêutico para crianças com TDAH..." |
| Stack técnico | ✅ | "React, FastAPI, AWS Lambda, PostgreSQL" |
| Restrições / dependências | ⚠️ opcional | "Precisa de aprovação do CEP antes da coleta" |
| Prioridades iniciais | ⚠️ opcional | "MVP em 3 meses, foco na coleta de dados" |
| Tamanho do time | ⚠️ opcional | "4 pessoas: 1 dev, 2 pesquisadores, 1 IC" |

Se algum campo obrigatório estiver faltando, pergunte antes de prosseguir.

---

## Processo de geração

### 1. Análise do descritivo

Identifique e extraia:
- **Domínios funcionais**: áreas distintas de funcionalidade (ex: autenticação, coleta de dados, relatórios)
- **Stakeholders implícitos**: quem vai usar cada parte (terapeuta, paciente, pesquisador, admin)
- **Marcos de entrega naturais**: o que pode ser entregue de forma independente
- **Restrições regulatórias ou de pesquisa**: CEP, LGPD, protocolos clínicos, aprovações institucionais

### 2. Critérios para um bom Epic (CIATec)

Um Epic válido para o CIATec deve:
- Representar **2–6 semanas de trabalho** de um time misto
- Ser **independentemente demonstrável** (pode virar uma demo ou milestone)
- Ter **valor claro** para pelo menos um stakeholder
- Ser **testável** — existe algum critério observável de conclusão
- Não misturar domínios muito distintos (ex: não juntar "autenticação" com "relatórios")

### 3. Estrutura de cada Epic

Para cada Epic gerado, produza:

```markdown
## Epic: [TÍTULO EM MAIÚSCULAS]

**ID sugerido:** EP-XX
**Domínio:** [Infraestrutura | Frontend | Backend | Dados | Pesquisa | UX/Conteúdo]
**Prioridade:** [P1-Crítico | P2-Alta | P3-Média | P4-Baixa]
**Estimativa:** [S=1-2sem | M=3-4sem | L=5-6sem]
**Dependências:** [IDs de outros Epics que devem preceder este, ou "Nenhuma"]
**Milestone GitHub sugerido:** [nome do milestone]

### Descrição
[2–4 frases explicando o que este Epic entrega e por quê importa]

### Valor de negócio / pesquisa
[Para quem e qual problema resolve]

### Critérios de conclusão (DoD — Definition of Done)
- [ ] Critério observável 1
- [ ] Critério observável 2
- [ ] Critério observável 3 (mínimo 3, máximo 6)

### Labels GitHub sugeridas
`epic` + `domain:[domínio]` + `priority:[p1|p2|p3|p4]`

### User Stories estimadas
[Lista preliminar de 3–8 títulos de User Stories que compõem este Epic]
```

### 4. Saída final

Após gerar todos os Epics:

1. **Mapa de dependências**: diagrama em Mermaid mostrando a ordem de execução
2. **Tabela resumo**: todos os Epics com ID, título, domínio, prioridade, estimativa e dependências
3. **Sugestão de roadmap**: agrupamento em fases/milestones (ver spec de roadmap)
4. **Contagem de User Stories estimadas**: para dar noção do tamanho total do backlog

---

## Regras de qualidade

- **Mínimo 3, máximo 10 Epics** por projeto (se parecer mais, questione se são sub-projetos distintos)
- Sempre identificar **pelo menos 1 Epic de infraestrutura/setup** se a stack precisar ser configurada
- Para projetos com coleta de dados humanos: sempre incluir Epic de **Conformidade (CEP/LGPD)**
- Nunca criar Epic de "testes" isolado — testes fazem parte dos critérios de conclusão de cada Epic
- Se o projeto tiver componente de pesquisa científica: incluir Epic de **Análise e Publicação**

---

## Exemplo de saída (fragmento)

```markdown
## Epic: AUTENTICAÇÃO E GESTÃO DE USUÁRIOS

**ID sugerido:** EP-01
**Domínio:** Backend + Frontend
**Prioridade:** P1-Crítico
**Estimativa:** M (3–4 semanas)
**Dependências:** Nenhuma
**Milestone GitHub sugerido:** v0.1 — Fundação

### Descrição
Implementar o sistema de autenticação multi-perfil (terapeuta, pesquisador, admin)
com controle de acesso baseado em papéis (RBAC). Base para todas as funcionalidades
que exigem identidade do usuário.

### Valor de negócio / pesquisa
Terapeutas precisam acessar apenas seus pacientes. Pesquisadores precisam de dados
anonimizados. Admins precisam de visibilidade total.

### Critérios de conclusão (DoD)
- [ ] Login/logout funcional com JWT
- [ ] 3 perfis de acesso configurados e testados
- [ ] Senha segura com reset por e-mail
- [ ] Cobertura de testes ≥ 80% nos endpoints de auth
- [ ] Documentação da API de autenticação publicada

### Labels GitHub sugeridas
`epic` `domain:backend` `domain:frontend` `priority:p1`

### User Stories estimadas
- US-01: Cadastro e login de terapeuta
- US-02: Cadastro e login de pesquisador  
- US-03: Painel de administração de usuários
- US-04: Reset de senha por e-mail
- US-05: Controle de sessão e expiração de token
```

---

## Próximos passos após gerar os Epics

Informe o usuário que pode:
1. Usar o skill **story-breaker** (`.cursor/skills/story-breaker/SKILL.md`) para detalhar qualquer Epic em User Stories
2. Consultar `docs/specs/spec-github-projects.md` para formatar a importação
3. Consultar `docs/specs/spec-roadmap.md` para gerar o roadmap visual
4. Consultar `docs/specs/context-ciatec.md` para perfis e camadas CIATec
