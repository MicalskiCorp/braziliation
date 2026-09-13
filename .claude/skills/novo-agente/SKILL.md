---
name: novo-agente
description: Cria ou atualiza um agente do Braziliation nas 2 camadas e nos 2 formatos (Copilot .agent.md + Claude .md) mantendo AGENTS.md sincronizado e sem duplicar responsabilidade. Use quando o usuário pedir para criar novo agente, refatorar agente ou sincronizar os formatos Copilot/Claude.
disable-model-invocation: true
---

# Skill: novo-agente

Protocolo executável do Papel 2 do `@AgentArchitect` para o formato duplo Copilot+Claude.

## Antes de criar (obrigatório)

1. Inventário: tabela de agentes do `AGENTS.md` + `Grep "^description:" .claude/agents`. Abrir o corpo de um agente só se ele for vizinho direto da proposta.
2. Se a responsabilidade proposta estiver ≥50% coberta por agente existente: reportar o conflito e propor estender o existente ou estreitar o escopo. **Nunca criar duplicado.**
3. Definir limites: o que o agente possui e o que delega (tabela "Limites" no corpo).

## Os 4 arquivos de um agente

| Arquivo | Camada | Formato | Conteúdo |
|---------|--------|---------|----------|
| `.claude/agents/{nome-kebab}.md` | 2ª (funcional) | Claude | **Onde se edita o corpo** |
| `.github/agents/{Nome}.agent.md` | 2ª (funcional) | Copilot | Mesmo corpo (propagado pelo script), frontmatter Copilot |
| `{raiz do workspace}/.claude/agents/{nome-kebab}.md` | 1ª (persona) | Claude | Wrapper fino → "leia o agente de referência" — fora do repositório |
| `{raiz do workspace}/.github/agents/{Nome}.agent.md` | 1ª (persona) | Copilot | Wrapper fino — fora do repositório |

## Sincronizar o corpo

Editar só o arquivo Claude e rodar:

```
py .claude/skills/novo-agente/sync_bodies.py          # propaga o corpo para o .agent.md
py .claude/skills/novo-agente/sync_bodies.py --check  # só lista divergências
```

O script preserva o frontmatter Copilot, o BOM UTF-8 e o CRLF dos `.agent.md`. No Claude Code ele roda sozinho: o hook `PostToolUse` `sync_agent_bodies.py` dispara a cada edição em `.claude/agents/`. Rodar à mão só fora de sessão (edição no editor, no Copilot). O `AgentParityTests` compara os corpos normalizados e falha na divergência.

## Conversão de frontmatter Claude → Copilot

- `name`: kebab-case → PascalCase; acrescentar `argument-hint` em português;
- `tools`: CSV → lista YAML com o mapeamento `Read→read` · `Edit, Write→edit` · `Grep, Glob→search` · `Bash→execute` · `WebSearch, WebFetch→web` · `TodoWrite→todo` · `Task, Agent→agent`; `Skill`, `model:`, `skills:` e `mcpServers:` não existem no Copilot;
- `model`: obrigatório no Claude (`sonnet`|`opus`|`haiku`), verificado pelo `AgentParityTests`;
- `description`: idêntica nos dois (serve de auto-delegação no Claude).

## Estrutura do corpo (convenção do projeto)

`## Papel` → `## Responsabilidades` → seções de domínio → `## Limites` → `## Como Responder Requisições` → `## Referências`. Português, padrão de description `"X do Braziliation. Use para: … Acionado por: '…'."`. Orçamento: 5.000 tokens por prompt (`TokenBudgetTests`).

## Registro (obrigatório)

1. Par novo no dicionário `AgentPairs` do `AgentParityTests` e no `PARES` do `sync_bodies.py`.
2. Linha do agente na tabela do `AGENTS.md`.
3. Reportar os caminhos criados + resumo do escopo.
