---
paths:
  - "**/TODO.md"
  - "Desenvolvimento/Docs/Roadmap/**"
---

# TODOs e status — Braziliation

Carregada ao tocar um TODO, por qualquer sessão — agente de camada ou não.

- Operações nos três TODOs (listar, adicionar, status, concluir, `concept-art`, varredura):
  skill `gerir-todo`. Escrita no TODO da camada seguinte: skill `handoff`.
- **Baixa:** Pesquisa e Criativo movem o item para `## Concluído` com a data; no
  `Desenvolvimento/Docs/TODO.md` a linha sai e o registro é o commit.
- **Nunca criar seção que já existe** (ex.: `## Handoffs do @GameCreative`, `## Handoffs de Pesquisa`).
- `Desenvolvimento/Docs/TODO-arquivo.md` é histórico congelado (há hook que bloqueia a escrita).
- Status de pendência vive **só** no TODO; `roadmap.md` e `backlog.md` descrevem fase e
  estágio e linkam o TODO.
- **Parser único** (ADR-012): `.claude/skills/gerir-todo/todo_md.py` — hook de sessão, skill,
  pre-commit e Central leem por ele. `py .claude/skills/gerir-todo/todo.py validar` roda no
  pre-commit e recusa TODO malformado.

## Vocabulário de status

O primeiro símbolo da célula Status decide; o texto depois dele é livre.

| Símbolo | Significa | Aberto? |
|---|---|---|
| ❌ | não iniciado | sim |
| 📋 | rascunho | sim |
| 🔨 | em andamento | sim |
| ⏸ | bloqueado ou aguardando (dizer o quê) | sim |
| 🟡 | confirmação fraca ou divergência — só em Pendências de Checagem | sim |
| 🎙️ | relato oral não confirmado — só em Pendências de Checagem | sim |
| ✅ | concluído — **nunca fica fora de `## Concluído`** (no Desenvolvimento, a linha sai) | não |

## Esquema de tabela

- Cabeçalho, linha separadora e linhas de dados **sem nada no meio** — citação ou linha em
  branco entre elas parte a tabela em duas e esconde itens.
- A primeira coluna é sempre o título do item. As outras, pelo nome: `Arquivo`, `Referência`,
  `Referência Técnica`, `Referência Criativa`, `Referência criativa (lore/ideia)` e
  `Arquivo Handoff` (referência) · `Tema`, `Descrição`, `Observação` (descrição) ·
  `Categoria destino em ArteConceitual` · `Responsável` · `Prioridade` (Alta, Média, Baixa) ·
  `Status` · `Data` (AAAA-MM-DD na tabela `## Concluído`). Coluna nova = adicionar em
  `todo_md.CAMPOS` antes.
- Uma tabela por seção: cada seção é uma fila da Central (`Central/filas.json`).
