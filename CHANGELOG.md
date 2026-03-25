# 📜 Changelog – Braziliation

All notable changes to this project will be documented in this file.

## [Unreleased]
### Added
- `Braziliation.CI.sln` e `tests/Braziliation.Game.Tests/`: projeto de testes **NUnit** (.NET 8) que valida layout do repositório (Unity 6, `ProjectVersion.txt`, `GameInitializer`, solution Unity).
### Changed
- **CI (GitHub Actions)**: `dotnet restore/build/test` passam a usar `tests/Braziliation.Game.Tests/Braziliation.Game.Tests.csproj` (evita MSB1009 se `Braziliation.CI.sln` não existir no clone); passo explícito de verificação do `.csproj`.
- **CI (GitLab)**: adicionado `.gitlab-ci.yml` com imagem `mcr.microsoft.com/dotnet/sdk:8.0` e o mesmo projeto de testes.
- `Braziliation.CI.sln`: caminho do projeto com barras `/` para compatibilidade Linux.
- `Braziliation.sln`: cabeçalho atualizado para Visual Studio 2022 (`# Visual Studio Version 17`).
- `.gitignore`: `tests/**/bin/` e `tests/**/obj/`; já ignorava `Logs/`, `Braziliation/Logs/`, `.plastic/` e `ignore.conf`.
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
