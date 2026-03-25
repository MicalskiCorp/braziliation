# 📜 Changelog – Braziliation

All notable changes to this project will be documented in this file.

## [Unreleased]
### Added
- `dotnet-tests/Braziliation.Game.Tests/`: testes **NUnit** (.NET 8) para CI, **fora** de `Tests/` na raiz (essa pasta costuma ser Unity ou ficar sem o `.csproj` no Git).
### Changed
- **CI (GitHub Actions / GitLab)**: preferência `dotnet-tests/…`, depois `Tests/…` e `tests/…`, mais `find` como último recurso; mensagens de diagnóstico se faltar o `.csproj`.
- `Braziliation.CI.sln`: referencia `dotnet-tests/Braziliation.Game.Tests/Braziliation.Game.Tests.csproj`.
- `Braziliation.sln`: cabeçalho Visual Studio 2022 (`# Visual Studio Version 17`).
- `.gitignore`: `dotnet-tests/**/bin/` e `dotnet-tests/**/obj/`.
### Removed
- Metadados locais do Plastic em `.plastic/` (projeto usa Git).
- `ignore.conf` (configuração Plastic).
- `CONTRIBUTING_EXTRA.md` (conteúdo incorporado em `CONTRIBUTING.md`).
- Relatório em `Braziliation/Logs/` e pasta aninhada `Braziliation/` quando vazia.
- Pastas vazias redundantes no Unity: `Assets/UI.meta`, `Assets/Scripts/Tools.meta`, `Assets/Scripts/Systems.meta`.

> **Nota:** A pasta `Logs/` na raiz pode permanecer localmente se o Unity mantiver arquivos abertos; ela está ignorada pelo Git. Apague manualmente com o editor fechado, se desejar.

## [0.1.0-alpha] – 2025-10-18
### Added
- Estrutura inicial do repositório
- CI/CD configurado (workflow condicional)
- Integração com ClickUp
- Regras de branches e commits
- Templates de PR e Issues
- Scripts de setup inicial

### Next
- Prototipagem do mapa base
- Sistema de movimentação e colisão em C#
- Pipeline de builds para Unity/MonoGame
