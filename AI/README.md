# AI-Assisted Development – Braziliation

Esta pasta suporta o desenvolvimento assistido por **VS Code Copilot**: contexto, templates de prompt e memoria compartilhada.

## Folder structure

| Pasta | Propósito | Copilot |
|-------|-----------|---------|
| **Context/** | Visão do jogo, direção de arte, padrões de código. Arquivos de referência bruta para agentes e contexto explícito. | — |
| **Memory/** | Documentos vivos: ADRs, roadmap, tech debt. Atualize conforme o projeto evolui. | — |
| **Prompts/** | *(Legado/referência)* Templates convertidos para `.github/prompts/`. | — |

> **Arquivos ativos para VS Code Copilot estão em `.github/`:**
> - `.github/agents/` — 10 agentes `.agent.md` (acione via `@NomeDoAgente`)
> - `.github/instructions/` — 3 instruções auto-aplicadas
> - `.github/prompts/` — 5 prompts de tarefa (acione via `/`)

## Como usar com VS Code Copilot

1. **Acione o agente** — Digite `@NomeDoAgente` no chat.
2. **Use slash prompts** — Digite `/` no chat e selecione: `create-feature`, `design-enemy`, `refactor-system`, `review-code`, `project-context`.
3. **Instruções auto-aplicadas** — `coding-standards` é injetado automaticamente em arquivos `.cs`; `game-vision` e `art-direction` são carregados sob demanda.
4. **Atualize a memoria** — Decisões em `AI/Memory/architecture_decisions.md`. Tech debt em `AI/Memory/tech_debt.md`.
5. **Um agente por thread** – Para trabalho complexo, use um agente por conversa.

## Agentes disponiveis (.github/agents/)

“”
## Agentes disponiveis (.github/agents/)

| Agente | Use quando |
|--------|------------|
| `@TechLead` | Direcao tecnica, padroes, routing entre agentes |
| `@Architect` | Limites de sistema, interfaces, ADRs |
| `@UnityEngineer` | Setup de engine: URP, Input System, camera, physics |
| `@UnityDeveloper` | UI controllers, ServiceLocator, MonoBehaviours |
| `@SystemsDeveloper` | Sistemas C# puros: save, settings, storage |
| `@GameplayEngineer` | Player, inimigos, combate, mecanicas de mundo |
| `@QAEngineer` | Revisao, edge cases, acceptance criteria |
| `@TestEngineer` | Testes xUnit automatizados |
| `@GameArquitetoMarkdown` | Estrutura de docs Markdown, indices, features, sistemas |
| `@GameCriativoMarkdown` | Lendas, brainstorm, personagens, arcos narrativos |

Para **novas features**: comece com `@TechLead` ou `@Architect`; depois `@GameplayEngineer` ou `@UnityEngineer`. Para **revisoes**: use `@QAEngineer`.









