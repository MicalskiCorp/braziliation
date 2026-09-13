---
description: "Carregar contexto completo do projeto Braziliation: stack, estrutura de repositório, estado atual do roadmap, ADRs, convenções e pipeline de agentes. Use no início de uma nova sessão de trabalho para calibrar o modelo."
argument-hint: "Branch atual (ex: 'main')"
agent: agent
tools: [read, search]
---
Leia os arquivos de contexto abaixo e absorva o estado atual do projeto **Braziliation** antes de qualquer outra tarefa. Confirme que entendeu listando: stack, fase atual do roadmap, e próximos 3 itens pendentes.

> No Claude Code este prompt não é necessário: o hook `SessionStart` (`.claude/hooks/session_snapshot.py`) injeta a foto do projeto no início de cada sessão.

## Arquivos a ler (em ordem)

1. `AGENTS.md` — agentes, skills e processos (fonte canônica)
2. `.github/instructions/game-vision.instructions.md` — visão, pilares, experiência-alvo
3. `.github/instructions/coding-standards.instructions.md` — padrões de código C# e Unity
4. `.github/instructions/art-direction.instructions.md` — direção de arte e restrições técnicas
5. `Desenvolvimento/Docs/Architecture/architecture_decisions.md` — ADRs aceitos
6. `Desenvolvimento/Docs/Roadmap/roadmap.md` — fases e itens pendentes
7. `Desenvolvimento/Docs/TODO.md` — pendências vivas
8. `Desenvolvimento/Docs/Tech/tech_debt.md` — tech debt conhecido

## Contexto resumido (para referência rápida)

| Dado | Valor |
|------|-------|
| Engine | Unity 6 (6000.2) + URP 2D |
| Linguagem | C# (Unity) · C# puro netstandard2.1 no core · .NET 8 nos testes |
| Resolução | 640×360 @ 32 PPU (Pixel Perfect, ADR-004) |
| Input | `GameInput` sobre o action map project-wide (ADR-006) |
| Tema | Plataforma/ação 2D, Brasil pós-apocalíptico dieselpunk |
| Branch atual | [preencha antes de enviar] |

## Estrutura do repositório

```
Braziliation/
├── Desenvolvimento/                 ← projeto Unity
│   ├── Assets/Scripts/              → Core, Gameplay, Build, Crafting, Enemies, UI (ADR-005)
│   ├── Assets/Tests/EditMode/       → testes EditMode do Unity
│   ├── src/Braziliation.Game.Core/  → C# puro, sem Unity
│   ├── Tests/Braziliation.Game.Tests/ → testes xUnit (rodam no CI)
│   └── Docs/                        → GDD, Architecture, Mechanics, Roadmap, Tech
├── Design/                          ← Pesquisa, Criativo, ArteConceitual, ArteFonte, GuiasDeArte
├── personas/                        ← cópia versionada da 1ª camada de agentes
└── .github/                         → 11 agentes, 3 instruções, prompts, workflows
```

## Pipeline de agentes (VS Code Copilot)

| Agente | Responsabilidade |
|--------|-----------------|
| `@TechLead` | Direção técnica, limites de sistema, interfaces, ADRs |
| `@UnityDeveloper` | Tudo Unity: setup de engine e wiring de runtime |
| `@SystemsDeveloper` | Save/Settings/Storage e demais sistemas C# puros |
| `@GameplayEngineer` | Player, inimigos, combate, mecânicas |
| `@QAEngineer` | Revisão, edge cases, acceptance criteria |
| `@TestEngineer` | Testes xUnit automatizados |
| `@GameArchitect` | Estrutura Markdown, índices, features |
| `@GameCreative` | Lendas, brainstorm, lore |
| `@Historiador` | Pesquisa histórica e folclórica com fonte |
| `@SpriteArtist` | Sprites programáticos e ciclo de crítica visual |
| `@AgentArchitect` | Orquestração, criação e auditoria de agentes |

---

Após ler os arquivos, confirme o estado atual e pergunte qual tarefa iniciar.
