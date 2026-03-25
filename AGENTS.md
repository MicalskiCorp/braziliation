# Braziliation – Guia para agentes

Projeto **Unity 6** (2D, URP, C#): jogo plataforma pixel art, tema dieselpunk pós-apocalíptico brasileiro.

## Onde está o código
- **Core**: `Assets/Scripts/Core/` — GameInitializer, CameraScaler
- **Outros scripts**: `Assets/Scripts/` (ex.: `UI/`; ver `Docs/Architecture/AssetsStructure.md`)
- **Cenas**: `Assets/Scenes/` (SampleScene.unity, teste1.unity)
- **Configuração**: `ProjectSettings/`, `Packages/manifest.json`

## Regras do Cursor
- `.cursor/rules/braziliation-project.mdc` — contexto geral (sempre aplicada)
- `.cursor/rules/unity-csharp.mdc` — padrões para `Assets/**/*.cs`

## Docs úteis
- `README.md` — visão geral e roadmap
- `Docs/Tech/DevelopmentRules.md` — branches, commits, merge, versionamento
- `Braziliation.CI.sln` + `tests/Braziliation.Game.Tests/` — testes .NET executados no GitHub Actions (sem Unity no runner)
