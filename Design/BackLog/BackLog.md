---
name: BackLog
description: "Lógica de gerência de TODOs criativos do Braziliation. Lida diretamente pelo agente @GameCreative (.github/agents/GameCreative.agent.md) nas etapas Passo 0, Passo Final e Modo 10."
---

# BackLog — Lógica de TODOs Criativos

Documento de operações para **ler, atualizar e varrer** o arquivo `Design/Criativo/TODO.md` do projeto Braziliation.

> Este arquivo é lido diretamente pelo agente `@GameCreative` (`.github/agents/GameCreative.agent.md`).

---

## Operações

### listar
1. Ler `Design/Criativo/TODO.md`
2. Retornar resumo por seção: História, Lendas, Cidades, Estados, Ideias
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
| `Estados/index.md` | `### Estados Planejados` |
| `Ideias/` ou `Brainstorm/` | `### Ideias` |

3. Adicionar linha com status `❌ Não iniciado`
4. Retornar confirmação

### atualizar-status: {item} — {novo-status}
1. Ler `Design/Criativo/TODO.md`
2. Localizar o item
3. Substituir o status atual pelo `{novo-status}`
4. Retornar confirmação

### varredura
1. Escanear todos os `.md` em `Design/Criativo/` buscando:
   - `*(a definir)*`, `*(Escrever aqui)*`, `{TODO}`, `*(nenhum*`
   - Status `📋 Rascunho` em tabelas de navegação
   - Tabelas com linha `*(nenhuma registrada)*`
2. Comparar com `Design/Criativo/TODO.md` — identificar itens não listados
3. Retornar lista de novos itens encontrados para o agente invocador decidir

---

## Regras

- **Nunca criar conteúdo criativo** — apenas gerenciar o índice
- **Sempre ler o TODO.md** antes de qualquer escrita
- **Links no TODO.md** devem ser relativos ao arquivo `Design/Criativo/TODO.md`
- **Retornar resultado** ao agente invocador após cada operação
