# Processos dos Agentes — Braziliation

> Detalhe operacional do ecossistema de agentes. O mapa curto (agentes, camadas, TODOs) está no [`AGENTS.md`](../../../AGENTS.md), que entra em toda sessão; este arquivo é lido **sob demanda** — por isso o detalhe vive aqui.

## 1. Descoberta de agentes por cwd

O Claude Code só descobre `.claude/agents/` e `.claude/skills/` relativos ao diretório aberto.

| Abrir o workspace em... | Camada ativa | O que fica disponível |
|--------------------------|---------------|------------------------|
| Raiz do workspace (pasta pai do repositório) | 1ª camada (personas: Jarvis, Computador, wrappers finos) | Só as personas — elas leem o agente de referência por caminho de arquivo |
| `Braziliation/` | 2ª camada (agentes funcionais + skills) | Tudo — **use este cwd para trabalho real** |

A 1ª camada vive **fora do repositório, por decisão do usuário (2026-09-13)**. Hoje há wrappers para 9 dos 11 agentes; `@Historiador` e `@AgentArchitect` só existem na 2ª camada. No Copilot (VS Code), `@Agente` funciona de qualquer cwd dentro do repositório.

## 2. Skills — catálogo por situação

As skills em `.claude/skills/` só existem no Claude Code. Cada agente dono tem `Skill` em `tools:` e pré-carrega suas skills pelo campo `skills:`; no Copilot o agente lê o `SKILL.md` por caminho. O `DocsConsistencyTests` falha se uma skill não aparecer nesta tabela.

| Skill | Agente(s) | Quando invocar |
|-------|-----------|-----------------|
| [`sprite-pipeline`](../../../.claude/skills/sprite-pipeline/SKILL.md) | `@SpriteArtist` | Gerar ou validar um sprite programático (spec JSON, ciclo de crítica visual, `palette_check`) |
| [`novo-asset`](../../../.claude/skills/novo-asset/SKILL.md) | `@SpriteArtist` | Asset novo sem brief/context pack |
| [`nova-cidade`](../../../.claude/skills/nova-cidade/SKILL.md) | `@GameCreative` (passos 1-3, 5-6) · `@UnityDeveloper` (passo 4) | Cidade/estado novo; o passo 4 (pastas em `Assets/Art/`) vira pendência para `@UnityDeveloper` |
| [`handoff`](../../../.claude/skills/handoff/SKILL.md) | `@Historiador`, `@GameCreative`, `@GameArchitect` | Fechar item de uma camada e escrever a entrada no TODO da seguinte |
| [`novo-agente`](../../../.claude/skills/novo-agente/SKILL.md) | `@AgentArchitect` (Papel 2) | Criar, refatorar ou sincronizar agente (2 camadas × 2 formatos, `sync_bodies.py`) |
| [`validar-todos`](../../../.claude/skills/validar-todos/SKILL.md) | `@AgentArchitect` (Papel 3) | Auditar TODOs concluídos, cobertura de testes e gaps de milestone |
| [`structure-audit`](../../../.claude/skills/structure-audit/SKILL.md) | `@AgentArchitect` (nível 4) · `@GameArchitect` (níveis 2-3) | Auditar disco × docs; só reporta, não corrige sem aprovação |
| [`hemeroteca-blumenau`](../../../.claude/skills/hemeroteca-blumenau/SKILL.md) | `@Historiador` | Fato, data ou nome de Blumenau em fonte primária ("Blumenau em Cadernos") |
| [`meta-check`](../../../.claude/skills/meta-check/SKILL.md) | `@UnityDeveloper` · `@SpriteArtist` | Pares asset/`.meta` em `Desenvolvimento/Assets/` |
| [`unity-validar`](../../../.claude/skills/unity-validar/SKILL.md) | `@UnityDeveloper` · `@GameplayEngineer` · `@TestEngineer` | Compilar o Unity em batchmode antes de commitar mudança em `Assets/`; `--testes` roda os EditMode |
| [`fechar-decisao`](../../../.claude/skills/fechar-decisao/SKILL.md) | `@GameCreative` (com `@TechLead` nos números) | Transformar pendência de design parada em DDR aprovado, com handoff |
| [`novo-adr`](../../../.claude/skills/novo-adr/SKILL.md) | `@TechLead` | Registrar decisão de arquitetura e marcar o ADR substituído |
| [`novo-inimigo`](../../../.claude/skills/novo-inimigo/SKILL.md) | `@GameplayEngineer` | Inimigo como perfil de dados + teste + linha em `InimigosIA.md` |

**Plugins habilitados** (`.claude/settings.json` → `enabledPlugins`): `unity` (skills oficiais da Unity, entre elas `2d-pixel-perfect`, `sprite-editor`, `tilemap-*`, `unity-cli`) e `skill-creator` (criar e avaliar skills).

## 3. Gestão de TODOs

| TODO | Dono | Lógica de operação |
|------|------|---------------------|
| `Design/Pesquisa/TODO.md` | `@Historiador` | No corpo do agente (Modos 1-7) |
| `Design/Criativo/TODO.md` | `@GameCreative` | [`Design/BackLog/BackLog.md`](../../../Design/BackLog/BackLog.md) — `listar` / `concluído` / `adicionar` / `atualizar-status` / `concept-art` / `varredura` |
| `Desenvolvimento/Docs/TODO.md` | `@GameArchitect` | Só itens abertos; concluído sai da tabela e o registro é o commit. `TODO-arquivo.md` é histórico congelado |

**Fonte única de status:** a pendência vive só no TODO da camada. `Roadmap/roadmap.md` e `Roadmap/backlog.md` descrevem fases e features e **linkam** o TODO — não repetem status de pendência.

## 4. Auditoria

- **Estrutura** (disco × docs, agentes, skills): skill `structure-audit`.
- **TODOs, cobertura e milestone:** skill `validar-todos` (Papel 3 do `@AgentArchitect`).

Ambas reportam antes de corrigir.

## 5. Criação e atualização de agente

`@AgentArchitect` (Papel 2) via skill `novo-agente`: inventário pela tabela do `AGENTS.md`, corpo escrito no formato Claude e propagado ao Copilot por `py .claude/skills/novo-agente/sync_bodies.py`, par registrado no `AgentParityTests` e linha no `AGENTS.md`.

## 6. Asset/sprite (5 etapas)

Ideia em `Design/Criativo/` (`@GameCreative`) → concept art aprovado em `Design/ArteConceitual/{categoria}/{asset}/` (`@SpriteArtist`, rota C) → especificação de variações (`variation-spec-template.md`, para personagens e inimigos complexos) → skill `novo-asset` (brief + context pack) → skill `sprite-pipeline` (spec JSON, geração, validação) → registro em `Docs/Architecture/indices/assets.md`, cuja seção "Backlog por Asset" rastreia as 5 etapas. Props simples pulam concept art e especificação. Guia: [`pipeline-sprites-programaticos.md`](../../../Design/GuiasDeArte/pipeline-sprites-programaticos.md).

## 7. Nova cidade/estado

Skill `nova-cidade`: scaffolding em `Design/Criativo/`, paleta em `Design/ArteConceitual/Paletas/`, pastas Unity delegadas ao `@UnityDeveloper`.

## 8. Travas automáticas

| Onde | O que roda | Pega |
|------|------------|------|
| Início de sessão (hook `SessionStart`) | `.claude/hooks/session_snapshot.py` | Injeta git, pendências Alta dos 3 TODOs e o último `unity-validar` |
| Ao editar (`PreToolUse`/`PostToolUse`) | `block_generated_dirs.py`, `build_game_core.py` | Escrita em pasta gerada; core que parou de compilar |
| Antes do commit (`.githooks/pre-commit`) | `dotnet test`, meta-check, `check_art_palettes.py` | Testes e guardas, `.meta` faltando, cor fora da paleta. Ativar por clone: `git config core.hooksPath .githooks` |
| No CI (`.github/workflows/ci.yml`) | os mesmos | O que escapou do pre-commit |
| No CI Unity (`unity-ci.yml`, GameCI) | compilação + EditMode | Ativo quando os secrets existirem ([`unity-ci.md`](unity-ci.md)) |

Guardas dentro do `dotnet test`: `GitIgnoreGuardTests`, `DocsConsistencyTests` (links, pastas documentadas, todo `.cs` numa ficha de sistema, ADR substituído, catálogo de skills), `TokenBudgetTests` (tetos de tamanho de prompt e doc), `UnityAssetConsistencyTests`, `AgentParityTests` e `RepositoryLayoutTests`.

## 9. Servidores MCP

`.mcp.json` + `enabledMcpjsonServers`: `aseprite` (pixel-mcp sobre o Aseprite local — `@SpriteArtist`), `unity` (CLI oficial; controla um Editor **aberto** com `com.unity.pipeline` — `@UnityDeveloper`) e `comfyui` (configurado no usuário; concept art da rota C). Cada agente declara só os MCPs que usa em `mcpServers:`.

## 10. Contexto de IA

| Arquivo | Conteúdo | Como é usado |
|---------|----------|--------------|
| `.github/instructions/game-vision.instructions.md` | Visão e tom do jogo | On-demand pelo Copilot |
| `.github/instructions/coding-standards.instructions.md` · `.claude/rules/csharp.md` | Convenções C# (espelhados) | Auto-injetados em `*.cs` |
| `.github/instructions/art-direction.instructions.md` · `.claude/rules/arte.md` | Direção de arte | Copilot on-demand · Claude em `Design/**` e `Assets/Art/**` |
| `Desenvolvimento/Docs/Architecture/architecture_decisions.md` | ADRs | Referenciado pelos agentes |
| `Desenvolvimento/Docs/Tech/tech_debt.md` | Dívida técnica | Referenciado pelos agentes |
