---
name: novo-agente
description: Cria ou atualiza um agente do Braziliation nas 2 camadas e nos 2 formatos (Copilot .agent.md + Claude .md) mantendo AGENTS.md sincronizado e sem duplicar responsabilidade. Use quando o usuário pedir para criar novo agente, refatorar agente ou sincronizar os formatos Copilot/Claude.
disable-model-invocation: true
---

# Skill: novo-agente

Segue o protocolo do `@AgentArchitect` (Papel 2, em `Braziliation/.github/agents/AgentArchitect.agent.md`) estendido para o formato duplo Copilot+Claude.

## Antes de criar (obrigatório)

1. Varrer TODOS os agentes existentes em `Braziliation/.github/agents/` e ler a tabela do `Braziliation/AGENTS.md`.
2. Se a responsabilidade proposta estiver ≥50% coberta por agente existente: reportar o conflito e propor estender o existente ou estreitar o escopo. **Nunca criar duplicado.**
3. Definir limites: o que o agente possui e o que delega (tabela "Limites" no corpo).

## Os 4 arquivos de um agente

| Arquivo | Camada | Formato | Conteúdo |
|---------|--------|---------|----------|
| `Braziliation/.github/agents/{Nome}.agent.md` | 2ª (funcional) | Copilot | **Fonte de verdade** — corpo completo |
| `Braziliation/.claude/agents/{nome-kebab}.md` | 2ª (funcional) | Claude | Mesmo corpo, frontmatter Claude |
| `{raiz}/.github/agents/{Nome}.agent.md` | 1ª (persona) | Copilot | Wrapper fino → "leia o agente de referência" |
| `{raiz}/.claude/agents/{nome-kebab}.md` | 1ª (persona) | Claude | Wrapper fino, frontmatter Claude |

## Conversão de frontmatter Copilot → Claude

- `name`: PascalCase → kebab-case; `argument-hint`: remover;
- `tools`: lista YAML → string CSV com mapeamento `read→Read` · `edit→Edit, Write` · `search→Grep, Glob` · `execute→Bash` · `web→WebSearch, WebFetch` · `todo→TodoWrite` · `agent→Task` · `vscode/browser/mermaid→remover`;
- `model`: nomes longos → `sonnet`|`opus`|`haiku` (só na 1ª camada);
- `description`: manter idêntica (serve de auto-delegação no Claude);
- **Corpo: idêntico nos dois formatos** — sem BOM UTF-8.

## Estrutura do corpo (convenção do projeto)

`## Papel` → `## Responsabilidades` → seções de domínio → `## Limites` → `## Como Responder Requisições` → `## Referências`. Português, padrão de description `"X do Braziliation. Use para: … Acionado por: '…'."`.

## Registro (obrigatório)

Adicionar/atualizar a linha do agente na tabela do `Braziliation/AGENTS.md`. Reportar os 4 caminhos criados + resumo do escopo.
