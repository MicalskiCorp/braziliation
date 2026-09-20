# Documentação

> Camada 3 · Desenvolvimento · Fonte canônica: [`game-architect.md`](../../../.claude/agents/game-architect.md) · skills [`gerir-todo`](../../../.claude/skills/gerir-todo/SKILL.md), [`handoff`](../../../.claude/skills/handoff/SKILL.md), [`novo-adr`](../../../.claude/skills/novo-adr/SKILL.md). Este manual resume; em divergência, vale a fonte.

Dono **@GameArchitect** (+ **@TechLead** nos ADRs) · Pasta **Desenvolvimento/Docs/** · TODO **Desenvolvimento/Docs/TODO.md** · skill **gerir-todo** (pré-carregada)

Traduz o que o Criativo aprovou em documentação técnica navegável — features, fichas de sistema, mecânicas — e mantém índices e código sincronizados. Não edita fonte do engine. Quatro modos: análise de arquivo e de pasta eram o mesmo procedimento; sincronização era um pedaço da varredura.

## Passo 0

- Ler `Docs/TODO.md` (seção `## Handoffs do @GameCreative`) e `Docs/index.md`.
- Se houver handoff, ler só o arquivo criativo referenciado.
- Grep pelo nome antes de abrir qualquer outro arquivo.

## Passo Final

- Item concluído sai do TODO (`gerir-todo`); o commit é o registro.
- Trabalho para implementação entra pela skill `handoff`.

## Onde cada coisa mora

- `GDD/Features/{Contexto}-{Nome}.md` · `Mechanics/{Nome}.md`
- `Architecture/Sistemas/{Sistema}.md` — índice de scripts
- `Roadmap/` · `Tech/`

## D1 — Nova feature (e handoff do Criativo)

**Quem:** @GameArchitect · Modo 1
**Aciona:** `@GameArchitect Nova feature: {Nome}` · `@GameArchitect Processar handoff: {item}`

1. Handoff? Ler o material criativo indicado.
2. Grep em `GDD/Features/` — já existe?
3. Criar `GDD/Features/{Contexto}-{Nome}.md` pelo `ModelFeature.md`.
4. Linha em `GDD/Features/index.md` e no `backlog.md`.
5. Linkar as fichas de sistema usadas.
6. Tirar o handoff do TODO e abrir as tarefas de implementação (D6).

- **Entrada:** C10
- **Orçamento:** Feature até ~3 mil tokens

## D2 — Novo sistema

**Quem:** @GameArchitect · Modo 2
**Aciona:** `@GameArchitect Novo sistema: {Nome}`

1. Criar `Architecture/Sistemas/{Sistema}.md` pelo `ModelSistema.md`.
2. "Fontes Técnicas" com cada script, ``Nome.cs`` entre crases.
3. Linha em `Sistemas/index.md`.

- **Gate:** `DocsConsistencyTests` falha com `.cs` fora das fichas ou pasta do core sem ficha

## D3 — Análise de tokens

**Quem:** @GameArchitect · Modo 3
**Aciona:** `@GameArchitect Analisar {arquivo ou pasta}`

1. Estimar tokens (bytes ÷ 4) do arquivo ou de cada `.md` da pasta.
2. Classificar pelo orçamento; apontar boilerplate, duplicação, pasta sem `index.md`.
3. Propor divisão com a economia estimada.
4. Executar só após confirmação.

- **Tetos:** Roteador 1,5 mil · agente 5 mil · sessão 2,5 mil · documento 5 mil
- **Unificou:** "Análise de arquivo" e "Análise de pasta"

## D4 — Sincronização e varredura

**Quem:** @GameArchitect · Modo 4
**Aciona:** `@GameArchitect Sincronizar camadas` · `@GameArchitect Varredura automática`

1. `dotnet test` — falhas de `DocsConsistencyTests` e `TokenBudgetTests` viram correção.
2. Pastas de `Docs/` sem `index.md` → criar pelo `ModelIndice.md`.
3. `GDD/Features/index.md` × `backlog.md`.
4. Relatório: item, ação, arquivo, e o que pede decisão.

- **Unificou:** "Sincronização" (já contida na varredura) e "Varredura"
- **Disco × docs:** Skill `structure-audit` (O3)

## D5 — Decisão de arquitetura (ADR)

**Quem:** @TechLead · skill `novo-adr` (sob demanda)

1. Próximo número = maior ADR + 1.
2. Confirmar contexto, decisão, consequências e se substitui algum ADR.
3. Escrever antes da linha final do arquivo; marcar o substituído como `Superseded por ADR-NNN`.
4. Atualizar `CLAUDE.md` e `.claude/rules/` se repetem o tema.
5. Rodar `dotnet test`.

- **Gate:** ADR substituído sem substituto quebra o teste
- **Vigentes:** 002, 004, 005, 006, 007, 008, 009 · substituídos: 001 (→004) e 003 (→005). Lista conferida em 19 set 2026; a fonte é [`architecture_decisions.md`](../Architecture/architecture_decisions.md) e a skill `novo-adr` manda atualizar esta linha ao registrar um ADR novo.

## D6 — Handoff para a Implementação

**Quem:** @GameArchitect · skill `handoff`

1. Confirmar spec pronta em `GDD/Features/` ou `Mechanics/`.
2. Linha na seção da área do TODO de Dev com responsável e prioridade.
3. Avisar o usuário qual agente acionar.

- **Próximo:** I2 a I5

## D7 — TODO de Desenvolvimento

**Quem:** @GameArchitect · skill `gerir-todo`

1. Só itens abertos, por área: handoffs, decisões de design, Unity, Gameplay, UI e arte, ecossistema.
2. Concluído: a linha sai; o commit é o registro.
3. `TODO-arquivo.md` é histórico congelado.

- **Por que é skill:** A mesma lógica serve aos 3 TODOs e a 4 agentes — antes estava descrita em 4 lugares e divergiu

---

[← Manual de processos](index.md)
