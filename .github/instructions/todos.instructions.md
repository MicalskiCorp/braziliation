---
description: "Regras dos TODOs de camada do Braziliation: operações, baixa de item, seções fixas e fonte única de status. Aplicado automaticamente aos TODO.md e ao Roadmap."
applyTo: "**/TODO.md,Desenvolvimento/Docs/Roadmap/**"
---
# TODOs e status — Braziliation

Espelho de `.claude/rules/todos.md`.

- Operações nos três TODOs (listar, adicionar, status, concluir, `concept-art`, varredura): `.claude/skills/gerir-todo/SKILL.md`. Escrita no TODO da camada seguinte: `.claude/skills/handoff/SKILL.md`.
- **Baixa:** Pesquisa e Criativo movem o item para `## Concluído` com a data; no `Desenvolvimento/Docs/TODO.md` a linha sai e o registro é o commit.
- **Nunca criar seção que já existe** (ex.: `## Handoffs do @GameCreative`, `## Handoffs de Pesquisa`).
- `Desenvolvimento/Docs/TODO-arquivo.md` é histórico congelado — nunca editar.
- Status de pendência vive **só** no TODO; `roadmap.md` e `backlog.md` descrevem fase e estágio e linkam o TODO.
