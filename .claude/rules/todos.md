---
paths:
  - "**/TODO.md"
  - "Desenvolvimento/Docs/Roadmap/**"
---

# TODOs e status — Braziliation

Espelha `.github/instructions/todos.instructions.md` (Copilot). Carregada ao tocar um TODO,
por qualquer sessão — agente de camada ou não.

- Operações nos três TODOs (listar, adicionar, status, concluir, `concept-art`, varredura):
  skill `gerir-todo`. Escrita no TODO da camada seguinte: skill `handoff`.
- **Baixa:** Pesquisa e Criativo movem o item para `## Concluído` com a data; no
  `Desenvolvimento/Docs/TODO.md` a linha sai e o registro é o commit.
- **Nunca criar seção que já existe** (ex.: `## Handoffs do @GameCreative`, `## Handoffs de Pesquisa`).
- `Desenvolvimento/Docs/TODO-arquivo.md` é histórico congelado (há hook que bloqueia a escrita).
- Status de pendência vive **só** no TODO; `roadmap.md` e `backlog.md` descrevem fase e
  estágio e linkam o TODO.
