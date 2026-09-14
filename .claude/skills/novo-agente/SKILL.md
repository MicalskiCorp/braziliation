---
name: novo-agente
description: Cria ou atualiza um agente do Braziliation em .claude/agents/ (e o wrapper da 1ª camada) mantendo o AGENTS.md sincronizado e sem duplicar responsabilidade. Use quando o usuário pedir para criar novo agente ou refatorar um agente existente.
disable-model-invocation: true
---

# Skill: novo-agente

Protocolo executável do Papel 2 do `@AgentArchitect`. Claude Code é o único harness de agentes do projeto (ADR-008).

## Antes de criar (obrigatório)

1. Inventário: tabela de agentes do `AGENTS.md` + `Grep "^description:" .claude/agents`. Abrir o corpo de um agente só se ele for vizinho direto da proposta.
2. Se a responsabilidade proposta estiver ≥50% coberta por agente existente: reportar o conflito e propor estender o existente ou estreitar o escopo. **Nunca criar duplicado.**
3. Definir limites: o que o agente possui e o que delega (tabela "Limites" no corpo).

## Os arquivos de um agente

| Arquivo | Camada | Conteúdo |
|---------|--------|----------|
| `.claude/agents/{nome-kebab}.md` | 2ª (funcional) | O agente completo |
| `{raiz do workspace}/.claude/agents/{nome-kebab}.md` | 1ª (persona) | Wrapper fino → "leia o agente de referência" — fora do repositório |

## Frontmatter

- `name`: kebab-case, **igual ao nome do arquivo** (invocação por `@agent-{nome}`).
- `description`: português, no padrão `"X do Braziliation. Use para: … Acionado por: '…'."` — é o que o Claude usa para delegar.
- `tools`: CSV com o mínimo necessário (`Read, Edit, Write, Grep, Glob, Bash, WebSearch, WebFetch, TodoWrite, Skill, Agent`).
- `model`: obrigatório (`sonnet` | `opus` | `haiku`).
- `skills`: só a skill usada em **toda** invocação; as demais carregam sob demanda (tabela "Situação → skill" no corpo).
- `mcpServers`: só os MCPs que o agente usa.

## Estrutura do corpo (convenção do projeto)

`## Papel` → `## Responsabilidades` → seções de domínio → `## Limites` → `## Como Responder Requisições` → `## Referências`. Português. Orçamento: 5.000 tokens por prompt (`TokenBudgetTests`) — detalhe longo ou raro vai para skill.

## Registro (obrigatório)

1. Linha do agente na tabela do `AGENTS.md` — o `AgentDefinitionTests` falha sem ela, e também sem `model:` ou com `name` diferente do arquivo.
2. Se o agente cria ou muda um processo, atualizar o arquivo da camada em `Desenvolvimento/Docs/Processos/`.
3. Reportar os caminhos criados e o resumo do escopo.
