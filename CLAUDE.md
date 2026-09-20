@AGENTS.md

# Claude Code — Braziliation

O arquivo importado acima (`AGENTS.md`) é o mapa de agentes, camadas e handoffs. Skills,
travas e processos detalhados ficam em `Desenvolvimento/Docs/Tech/processos.md` — ler sob
demanda. Claude Code é o único harness de agentes do projeto (ADR-008).

> Por que este arquivo existe: o Claude Code lê `CLAUDE.md`, **não** `AGENTS.md`.
> Sem este import, todo o mapa de processo do projeto ficava invisível nas sessões.

## Onde rodar

Abra o workspace em `Braziliation/` (esta pasta). A descoberta de `.claude/agents/` e
`.claude/skills/` é relativa ao cwd — abrir a pasta pai carrega só as personas da 1ª
camada, sem os agentes funcionais nem as skills.

## Comandos

| O quê | Comando |
|-------|---------|
| Testes .NET (~1s) | `dotnet test Desenvolvimento/Tests/Braziliation.Game.Tests/Braziliation.Game.Tests.csproj` |
| Build do core puro | `dotnet build Desenvolvimento/src/Braziliation.Game.Core/Braziliation.Game.Core.csproj` |
| Compilar Unity (Editor fechado) | `py .claude/skills/unity-validar/scripts/validar.py` · `--testes` roda também os EditMode (licença ativa desde 2026-09-20; 9/9) |
| Meta-check / paletas | `py .claude/skills/meta-check/check_meta_pairs.py` · `py Design/ArteFonte/Ferramentas/check_art_palettes.py` |
| Ativar o pre-commit (uma vez por clone) | `git config core.hooksPath .githooks` |
| Ferramentas de arte | `py Design/ArteFonte/Ferramentas/<script>.py` — **use `py`, não `python`** |

O build do Core copia as DLLs para `Desenvolvimento/Assets/Plugins/Braziliation/`
automaticamente (target `CopyToUnityPlugins`, desativado quando `CI=true`). **Essa pasta
é saída de build e não é versionada** — num clone novo, rode o build do core antes de
abrir o Unity, ou o projeto não compila.

## Regras de ouro

- **Nunca edite** `Library/`, `Temp/`, `obj/`, `bin/` — gerados. Há um hook `PreToolUse`
  que bloqueia isso, e também o histórico congelado `Desenvolvimento/Docs/TODO-arquivo.md`.
- **Nunca edite a DLL** em `Assets/Plugins/Braziliation/` — edite a fonte em
  `Desenvolvimento/src/Braziliation.Game.Core/` e deixe o build copiar.
- **Todo asset novo em `Assets/` precisa do `.meta`** correspondente, ou o GUID muda a
  cada reimport e quebra referências de cena/prefab. Skill: `meta-check`.
- **Lógica de jogo nunca vive em MonoBehaviour de UI** — UI chama serviço; serviço vive
  em `Braziliation.Game.Core`.
- Testes usam **xUnit**. NUnit foi removido do projeto.

## Estado conhecido (revisar quando mudar)

- **Layout de `Assets/Scripts/` é por domínio (ADR-005, substitui o ADR-003):**
  `Core/`, `Gameplay/`, `Build/`, `Crafting/`, `Enemies/`, `UI/`. Script novo vai para
  a pasta do domínio.
- **Todo input passa por `Braziliation.Core.GameInput` (ADR-006)**, sobre o action map
  project-wide `Assets/InputSystem_Actions.inputactions`. Ação nova = binding no asset
  primeiro, propriedade em `GameInput` depois. Polling de `Keyboard.current`/`Gamepad.current`
  em gameplay é proibido.
- **Pastas chamadas `Build/` são código** (`src/.../Build/`, `Assets/Scripts/Build/`). A
  regra de saída de player build no `.gitignore` é ancorada em `/Desenvolvimento/Build/`;
  nunca a desancore. `GitIgnoreGuardTests` falha se algum `.cs` cair numa regra de ignore.
- **O projeto Unity compila e roda os testes EditMode em batchmode** — licença ativada na
  máquina em 2026-09-20 (`unity auth login` + `unity license activate --personal
  --accept-eula`); `unity-validar --testes` passou 9/9. Mudou algo em `Assets/`? Rode a
  skill `unity-validar` antes de commitar — **é a única checagem do lado Unity**, e o
  pre-commit a exige. O CI do Unity está desligado por decisão (ADR-010): a Unity encerrou
  a ativação de Personal em CI, e o job aparece como `skipped`, nunca como verde.
- Commits vão direto no `main` até a v1 estar consolidada; o fluxo com PR vem depois.
- Dívida técnica vive em `Desenvolvimento/Docs/Tech/tech_debt.md`. Se você encontrar
  dívida durante uma tarefa, registre lá — não só no TODO.
