# 📜 Changelog – Braziliation

All notable changes to this project will be documented in this file.

## [Unreleased] — rumo à v1

### Added
- **Motor de IA de inimigos** por perfil (`EnemyBrain`, C# puro, determinístico) + `EnemyProfileAsset`.
- **Save versionado com migração explícita** (ADR-007): `LoadDetailed`, `SaveLoadStatus`, degraus `ISaveMigration`.
- **Input via action map** (ADR-006): `GameInput` como única porta de leitura de input.
- Pipeline programático de sprites (ADR-004, 640×360 @ 32 PPU), assets de Blumenau (Ondas 1 e 2), placeholders CC0 do Gothicvania.
- Gerador de mapas por Wave Function Collapse e importador Unity; benches de modelo (set/2026).
- Travas automáticas: `GitIgnoreGuardTests`, `DocsConsistencyTests`, `UnityAssetConsistencyTests`, `AgentParityTests`; testes EditMode em `Assets/Tests/EditMode/`.
- Pre-commit versionado em `.githooks/`, checagem de paleta (`check_art_palettes.py`) e meta-check no CI.
- Skills `unity-validar`, `fechar-decisao`, `novo-adr`, `novo-inimigo`; MCP do Aseprite (pixel-mcp); plugin oficial da Unity.

### Changed
- CI (GitHub e GitLab) com alvo único `Desenvolvimento/Tests/Braziliation.Game.Tests/`, sem fallback.
- Layout de `Assets/Scripts/` por domínio (ADR-005, substitui o ADR-003).
- Testes só em **xUnit** (NUnit removido).

### Removed
- Pasta `Desenvolvimento/dotnet-tests/` (cópia obsoleta que o CI rodava por fallback).
- 209 artefatos de build que estavam versionados (`bin/`, `obj/`, `__pycache__/`, `Assembly-CSharp.csproj`).
- Pastas vazias do ADR-003 e o `_Recovery` do Unity.

### Fixed
- Regra `Build/` do `.gitignore` escondia código-fonte de Build: o commit publicado não compilava.
- Hook `block_generated_dirs` bloqueava o temp do sistema; meta-check reprovava `.gitkeep`.

## [0.1.0-alpha] – 2025-10-18
### Added
- Estrutura inicial do repositório
- CI/CD configurado (workflow condicional)
- Integração com ClickUp
- Regras de branches e commits
- Templates de PR e Issues
- Scripts de setup inicial
