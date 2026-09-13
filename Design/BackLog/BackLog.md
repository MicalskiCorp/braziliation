---
name: BackLog
description: "Lógica de gerência de TODOs criativos do Braziliation. Lida diretamente pelo agente @GameCreative nas etapas Passo 0, Passo Final e Modo 10."
---

# BackLog — Lógica de TODOs Criativos

Documento de operações para **ler, atualizar e varrer** o arquivo `Design/Criativo/TODO.md` do projeto Braziliation.

> Este arquivo é lido diretamente pelo agente `@GameCreative` (`.claude/agents/game-creative.md` · `.github/agents/GameCreative.agent.md`).

---

## Operações

### listar
1. Ler `Design/Criativo/TODO.md`
2. Retornar resumo por seção: História, Lendas, Cidades, Estados, Ideias, Concept Art Pendente
3. Destacar itens **Alta prioridade** com status `❌ Não iniciado`

### concluído: {item}
1. Ler `Design/Criativo/TODO.md`
2. Localizar o item pelo nome
3. Remover da tabela de pendências
4. Adicionar linha em `## Concluído` com a data atual
5. Retornar confirmação

### adicionar: {descrição} — {arquivo} — {prioridade}
1. Ler `Design/Criativo/TODO.md`
2. Identificar seção correta pelo arquivo ou tipo:

| Arquivo contém | Seção |
|----------------|-------|
| `Historia/` | `### História` |
| `Lendas/` | `### Lendas` |
| `Estados/SantaCatarina/cidades/` | `### Cidades — Santa Catarina` |
| `Estados/{X}/` (novo estado) | `### Cidades — {X}` (criar se não existir) |
| `Estados/index.md` ou "Criar estado: …" | `### Estados Planejados` |
| `Ideias/` ou `Brainstorm/` | `### Ideias` |
| `Desenvolvimento/Docs/Mechanics/` (pedido do `@GameArchitect`) | `### Crafting & Build — Conteúdo Criativo` |
| Handoff do `@Historiador` (`Design/Pesquisa/…`) | `## Handoffs de Pesquisa` |
| Concept art de um asset | `### Concept Art Pendente` — usar a operação `concept-art`, não `adicionar` |

3. Adicionar linha com status `❌ Não iniciado`
4. Retornar confirmação

### atualizar-status: {item} — {novo-status}
1. Ler `Design/Criativo/TODO.md`
2. Localizar o item
3. Substituir o status atual pelo `{novo-status}`
4. Retornar confirmação

### concept-art: {asset} — {arquivo de origem} — {categoria} — {prioridade}
> Passo 1 do fluxo concept art → spec JSON → sprite (`Design/GuiasDeArte/pipeline-sprites-programaticos.md`). Usar esta operação (não `adicionar`) porque a tabela de "Concept Art Pendente" tem colunas próprias (Asset | Referência criativa | Categoria destino | Prioridade | Status).

1. Ler `Design/Criativo/TODO.md` → seção `### Concept Art Pendente`
2. Adicionar linha: `{asset} | {arquivo de origem} | {categoria} (Personagens\|Criaturas\|Props\|Cidades) | {prioridade} | ❌ Não iniciado`
3. Adicionar/atualizar a linha correspondente em `Desenvolvimento/Docs/Architecture/indices/assets.md` → seção "Backlog por Asset", com **Ideia (P1) = ✅** e as demais colunas ❌ — esta operação é o que abre a linha na tabela granular; não esperar o Passo 5 (sprite pronto) para ela existir.
4. Retornar confirmação + lembrete: "Passo 2 (gerar e aprovar concept art) é de `@SpriteArtist`; acionar manualmente quando desejar"

### varredura
1. Escanear todos os `.md` em `Design/Criativo/` buscando:
   - `*(a definir)*`, `*(Escrever aqui)*`, `{TODO}`, `*(nenhum*`
   - Status `📋 Rascunho` em tabelas de navegação
   - Tabelas com linha `*(nenhuma registrada)*`
2. Escanear personagens/cidades/criaturas com status `✅ Pronto` (ou seção "Aparência"/"Monstros" preenchida) — comparar com a tabela `### Concept Art Pendente` e com `Design/ArteConceitual/{Personagens|Criaturas|Cidades}/`: se não houver entrada pendente nem concept art aprovado, sinalizar como candidato a `concept-art: ...`
3. Comparar com `Design/Criativo/TODO.md` — identificar itens não listados
4. Retornar lista de novos itens encontrados para o agente invocador decidir

---

## Regras

- **Nunca criar conteúdo criativo** — apenas gerenciar o índice
- **Sempre ler o TODO.md** antes de qualquer escrita
- **Links no TODO.md** devem ser relativos ao arquivo `Design/Criativo/TODO.md`
- **Retornar resultado** ao agente invocador após cada operação
