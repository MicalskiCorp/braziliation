---
description: "Carregar contexto completo do projeto Braziliation: stack, estrutura de repositório, estado atual do roadmap, ADRs, convenções e pipeline de agentes. Use no início de uma nova sessão de trabalho para calibrar o modelo."
argument-hint: "Branch atual (ex: 'develop', 'feature/player-movement')"
agent: agent
tools: [read, search]
---
Leia os arquivos de contexto abaixo e absorva o estado atual do projeto **Braziliation** antes de qualquer outra tarefa. Confirme que entendeu listando: stack, fase atual do roadmap, e próximos 3 itens pendentes.

## Arquivos a ler (em ordem)

1. `.github/instructions/game-vision.instructions.md` — visão, pilares, experiência-alvo
2. `.github/instructions/coding-standards.instructions.md` — padrões de código C# e Unity
3. `.github/instructions/art-direction.instructions.md` — direção de arte e restrições técnicas
4. `Desenvolvimento/Docs/Architecture/architecture_decisions.md` — ADRs aceitos
5. `Desenvolvimento/Docs/Roadmap/roadmap.md` — fases e itens pendentes
6. `Desenvolvimento/Docs/Tech/tech_debt.md` — tech debt conhecido
7. `Desenvolvimento/AGENTS.md` — guia de agentes disponíveis

## Contexto resumido (para referência rápida)

| Dado | Valor |
|------|-------|
| Engine | Unity 6 (6000.2) + URP 2D |
| Linguagem | C# (.NET no Unity / .NET 8 nos testes .NET) |
| Resolução | 320×180 @ 16 PPU (Pixel Perfect) |
| Input | com.unity.inputsystem (New Input System) |
| Estilo visual | Pixel Art, paleta restrita estilo SNES |
| Tema | Plataforma/ação 2D, Brasil pós-apocalíptico dieselpunk |
| Branch atual | [preencha antes de enviar] |

## Estrutura do repositório

```
Braziliation/                  ← repositório Unity
├── Assets/Scripts/        → Código Unity (Core, Player, Enemies, Combat, UI, etc.)
├── src/                   → Braziliation.Game.Core (C# puro, sem Unity)
├── dotnet-tests/          → Testes xUnit .NET
├── Docs/Architecture/     → architecture_decisions (ADRs), AssetsStructure
├── Docs/Roadmap/          → roadmap
├── Docs/Tech/             → tech_debt, DevelopmentRules
├── Docs/                  → GDD, Architecture, Mechanics, Tech
└── .github/
    ├── agents/            → 10 agentes .agent.md
    ├── instructions/      → 3 instruções auto-aplicadas
    └── prompts/           → templates de prompt (este arquivo incluído)

Design/                        ← camada criativa (pasta irmã ao repo)
├── Criativo/
│   ├── Lendas/            → catálogo + mapeamento de lendas brasileiras
│   ├── Historia/          → premissa, arcos narrativos, personagens
│   ├── Ideias/            → pool de ideias brutas
│   └── Brainstorm/        → sessões de brainstorm
└── Arts Conceituas/       → arte conceitual (cidades, monstros)
```

## Pipeline de agentes (VS Code Copilot)

| Agente | Responsabilidade |
|--------|-----------------|
| `@TechLead` | Direção técnica, routing, padrões |
| `@Architect` | Limites de sistema, interfaces, ADRs |
| `@UnityEngineer` | Setup engine: URP, Input System, câmera |
| `@UnityDeveloper` | UI controllers, ServiceLocator, MonoBehaviours |
| `@SystemsDeveloper` | Save/Settings/Storage (C# puro) |
| `@GameplayEngineer` | Player, inimigos, combate, mecânicas |
| `@QAEngineer` | Revisão, edge cases, acceptance criteria |
| `@TestEngineer` | Testes xUnit automatizados |
| `@GameArchitect` | Estrutura Markdown, índices, features |
| `@GameCreative` | Lendas, brainstorm, lore |

## Scripts implementados até agora

- `Assets/Scripts/Core/GameInitializer.cs` — targetFrameRate=60, vSyncCount=0
- `Assets/Scripts/Core/CameraScaler.cs` — PixelPerfectCamera 16 PPU, 320×180

---

Após ler os arquivos, confirme o estado atual e pergunte qual tarefa iniciar.
