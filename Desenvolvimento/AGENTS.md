# Braziliation – Guia para agentes

Projeto **Unity 6** (2D, URP, C#): jogo plataforma pixel art, tema dieselpunk pós-apocalíptico brasileiro.

## Onde está o código
- **Core**: `Desenvolvimento/Assets/Scripts/Core/` — GameInitializer, CameraScaler
- **Outros scripts**: `Desenvolvimento/Assets/Scripts/` (ex.: `UI/`; ver `Desenvolvimento/Docs/Architecture/AssetsStructure.md`)
- **Cenas**: `Desenvolvimento/Assets/Scenes/` (SampleScene.unity, teste1.unity)
- **Configuração**: `Desenvolvimento/ProjectSettings/`, `Desenvolvimento/Packages/manifest.json`
- **Sistemas C# puros**: `Desenvolvimento/src/Braziliation.Game.Core/`
- **Testes .NET**: `Desenvolvimento/dotnet-tests/Braziliation.Game.Tests/`

## Agentes disponíveis (VS Code Copilot)

Todos os agentes estão em `.github/agents/` na raiz do workspace. Acione via `@NomeDoAgente`.

| Agente | Use para |
|--------|----------|
| `@TechLead` | Direção técnica, padrões, routing |
| `@Architect` | Limites de sistema, interfaces, ADRs |
| `@UnityEngineer` | Setup de engine: URP, Input System, câmera |
| `@UnityDeveloper` | UI controllers, ServiceLocator, MonoBehaviours |
| `@SystemsDeveloper` | Save, Settings, Storage (C# puro, sem Unity) |
| `@GameplayEngineer` | Player, inimigos, combate, mecânicas |
| `@QAEngineer` | Revisão, edge cases, acceptance criteria |
| `@TestEngineer` | Testes xUnit automatizados |
| `@GameArquitetoMarkdown` | Estrutura Markdown, índices, features, sistemas |
| `@GameCriativoMarkdown` | Lendas, brainstorm, personagens, lore |

## Contexto de IA

| Arquivo | Conteúdo | Como é usado |
|---------|----------|--------------|
| `.github/instructions/game-vision.instructions.md` | Visão e tom do jogo | On-demand pelo Copilot |
| `.github/instructions/coding-standards.instructions.md` | Convenções de código C# | Auto-injetado em `*.cs` |
| `.github/instructions/art-direction.instructions.md` | Direção de arte | On-demand pelo Copilot |
| `Desenvolvimento/Docs/Architecture/architecture_decisions.md` | ADRs | Referenciado pelos agentes |
| `Desenvolvimento/Docs/Tech/tech_debt.md` | Tech debt | Referenciado pelos agentes |
| `Desenvolvimento/Docs/Roadmap/roadmap.md` | Roadmap | Referenciado pelos agentes |

## Docs úteis
- `Desenvolvimento/README.md` — visão geral e roadmap
- `Desenvolvimento/Docs/Tech/DevelopmentRules.md` — branches, commits, merge, versionamento
- `Desenvolvimento/Braziliation.CI.slnx` + `Desenvolvimento/dotnet-tests/` — testes .NET no CI (sem Unity no runner)
