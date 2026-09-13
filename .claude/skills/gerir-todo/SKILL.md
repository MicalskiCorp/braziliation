---
name: gerir-todo
description: Opera os três TODOs de camada do Braziliation (Pesquisa, Criativo, Desenvolvimento) — listar, adicionar na seção certa, atualizar status, concluir com a regra de baixa de cada arquivo, abrir pendência de concept art e varrer lacunas. Use no Passo 0 e no Passo Final dos agentes de camada, ou quando o usuário pedir "listar TODOs", "adicionar pendência", "concluir item", "varredura de TODOs" ou "varredura criativa".
---

# Skill: gerir-todo

Uma lógica para os três índices de pendência. Antes, cada agente descrevia a sua — e as regras de baixa divergiram (uma mandava mover para "Concluído" num arquivo que não tem essa seção). Escrever no TODO da **camada seguinte** não é desta skill: é a skill `handoff`.

## Os três TODOs

| TODO | Dono | Seções | Item concluído |
|------|------|--------|----------------|
| `Design/Pesquisa/TODO.md` | `@Historiador` | Estados a Pesquisar · Temas Transversais · Handoffs Pendentes para @GameCreative · Concluído | Sai da tabela e entra em `## Concluído` com a data |
| `Design/Criativo/TODO.md` | `@GameCreative` | História · Lendas · Cidades — {Estado} · Estados Planejados · Crafting & Build · Ideias · Concept Art Pendente · Handoffs de Pesquisa · Concluído | Sai da tabela e entra em `## Concluído` com a data (e o link, se houver DDR ou concept aprovado) |
| `Desenvolvimento/Docs/TODO.md` | `@GameArchitect` | Handoffs do @GameCreative · Decisões de design · Unity · Gameplay · UI e arte · Ecossistema e processo | **A linha sai.** O registro é o commit. `TODO-arquivo.md` é histórico congelado — nunca editar |

Status: ❌ não iniciado · 📋 rascunho · 🔨 em andamento · ⏸ bloqueado (sempre dizer do quê).

## Operações

### listar
1. Ler o TODO da camada.
2. Resumir por seção; destacar Alta com ❌ e os itens ⏸ com o bloqueio.

### adicionar: {descrição} — {arquivo de referência} — {prioridade}
1. Ler o TODO e escolher a seção pelo roteamento abaixo. **Nunca criar seção que já existe** — seção nova só para estado novo (`### Cidades — {Estado}`).
2. Seguir o formato das linhas vizinhas; links relativos ao próprio TODO.
3. Status inicial ❌.

Roteamento do TODO criativo:

| Referência contém | Seção |
|-------------------|-------|
| `Historia/` | `### História` |
| `Lendas/` | `### Lendas` |
| `Estados/{Estado}/cidades/` | `### Cidades — {Estado}` |
| `Estados/index.md` ou "Criar estado" | `### Estados Planejados` |
| `Ideias/` ou `Brainstorm/` | `### Ideias` |
| `Desenvolvimento/Docs/Mechanics/` | `### Crafting & Build — Conteúdo Criativo` |
| Concept art de um asset | `### Concept Art Pendente` — operação `concept-art` |

TODO de Pesquisa: estado → "Estados a Pesquisar"; tema → "Temas Transversais". TODO de Dev: seção da área (Unity, Gameplay, UI e arte, Ecossistema) com a coluna Responsável preenchida.

### atualizar-status: {item} — {status}
Localizar o item e trocar o status.

### concluído: {item}
Aplicar a regra da coluna "Item concluído" daquele TODO.

### concept-art: {asset} — {arquivo de origem} — {categoria} — {prioridade}
*(só no TODO criativo)*
1. Linha em `### Concept Art Pendente`: `{asset} | {arquivo de origem} | {Personagens|Criaturas|Props|Cidades}/ | {prioridade} | ❌`.
2. Abrir ou atualizar a linha do asset em "Backlog por Asset" de `Desenvolvimento/Docs/Architecture/indices/assets.md`, com Ideia ✅ e as demais etapas ❌.
3. Lembrar ao usuário: a etapa 2 é do `@SpriteArtist` (skill `concept-art`).

### varredura
Rodar sem confirmar passo a passo e devolver a lista — o usuário decide o que entra no TODO.

- **Criativo** (`Design/Criativo/`): marcadores abertos (`{TODO}`, `*(a definir)*`, `*(Escrever aqui)*`, `*(nenhum…*`); lendas ❌ no catálogo sem mapeamento; ideias 💡 paradas desde a sessão anterior; arcos e personagens sem lenda associada; cidades 📋 com Características vazias; personagens ou criaturas com Aparência preenchida sem linha em Concept Art Pendente nem concept aprovado em `Design/ArteConceitual/`. Comparar com o TODO e listar o que falta nele.
- **Pesquisa**: estados e temas de `Design/Criativo/Estados/index.md` sem cobertura em `Design/Pesquisa/index.md`.
- **Desenvolvimento**: `dotnet test` (guardas de docs e de orçamento) e features de `GDD/Features/index.md` sem linha no `Roadmap/backlog.md`. Item dado como feito sem implementação e `// TODO` inline são da skill `validar-todos`.

## Regras

- Ler o TODO antes de qualquer escrita.
- Cada agente escreve no TODO da própria camada; no da seguinte, só pela skill `handoff`.
- Pendência vive só no TODO — roadmap e backlog apenas linkam.
