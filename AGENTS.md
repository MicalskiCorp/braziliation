# Braziliation – Guia para agentes

Projeto **Unity 6** (2D, URP, C#): plataforma pixel art, dieselpunk pós-apocalíptico brasileiro. Este arquivo entra em toda sessão — é só o mapa. Catálogo de skills, travas automáticas, MCPs e processos detalhados: [`Desenvolvimento/Docs/Tech/processos.md`](Desenvolvimento/Docs/Tech/processos.md) (ler sob demanda).

## Onde está o código
- **Scripts Unity**: `Desenvolvimento/Assets/Scripts/` por domínio (ADR-005) — `Core/`, `Gameplay/`, `Build/`, `Crafting/`, `Enemies/`, `UI/` · editor tools em `Assets/Editor/`
- **C# puro**: `Desenvolvimento/src/Braziliation.Game.Core/` · **testes xUnit**: `Desenvolvimento/Tests/Braziliation.Game.Tests/`
- **Cenas**: `Assets/Scenes/Menus/MainMenu.unity` (primeira do build), `DemoGameplay.unity`
- **Índice de scripts**: fichas em `Desenvolvimento/Docs/Architecture/Sistemas/`

## Agentes

Mesmo corpo em dois formatos: `.claude/agents/{nome}.md` (Claude Code) e `.github/agents/{Nome}.agent.md` (Copilot). Acione via `@Nome`.

| Agente | Use para |
|--------|----------|
| `@TechLead` | Direção técnica, padrões, limites de sistema, interfaces, ADRs |
| `@UnityDeveloper` | Setup do engine e wiring de runtime (UI, MonoBehaviours, ServiceLocator) |
| `@SystemsDeveloper` | Save, Settings, Storage (C# puro) |
| `@GameplayEngineer` | Player, inimigos, combate, mecânicas |
| `@QAEngineer` | Revisão, edge cases, acceptance criteria |
| `@TestEngineer` | Testes xUnit |
| `@GameArchitect` | Docs técnicos em `Desenvolvimento/Docs/`; processa handoffs do `@GameCreative` |
| `@Historiador` | Pesquisa com fonte em `Design/Pesquisa/`; handoff para `Design/Criativo/TODO.md` |
| `@GameCreative` | Lore, lendas, cidades, personagens em `Design/Criativo/`; handoff para `Desenvolvimento/Docs/TODO.md` |
| `@SpriteArtist` | Sprites programáticos e ciclo de crítica visual (não decide direção de arte nem faz wiring Unity) |
| `@AgentArchitect` | Orquestração de sessão, auditoria e criação de agentes |

## Fluxo entre Camadas (Modelo Reativo)

Cada camada é acionada **manualmente** pelo usuário. Nenhum agente invoca outro.

```
@Historiador     Design/Pesquisa/        → handoff em Design/Criativo/TODO.md
      ↓
@GameCreative    Design/Criativo/        → handoff em Desenvolvimento/Docs/TODO.md
      ↓
@GameArchitect   Desenvolvimento/Docs/   → itens para implementação no mesmo TODO
      ↓
@GameplayEngineer · @UnityDeveloper · @SystemsDeveloper   Assets/ e src/

Lateral: @SpriteArtist   Design/ArteConceitual + ArteFonte → Assets/Art/
         (concept art pedido em Design/Criativo/TODO.md; entrega rastreada em indices/assets.md)
```

Rotas de handoff válidas: Pesquisa→Criativo, Criativo→Documentação, Documentação→Implementação — nunca pular camada sem pedido explícito. Protocolo: skill `handoff`.

## TODOs — um por camada

| TODO | Dono |
|------|------|
| `Design/Pesquisa/TODO.md` | `@Historiador` |
| `Design/Criativo/TODO.md` | `@GameCreative` (operações em `Design/BackLog/BackLog.md`) |
| `Desenvolvimento/Docs/TODO.md` | `@GameArchitect` — handoffs chegam em `## Handoffs do @GameCreative` |

Status de pendência vive **só** no TODO da camada; roadmap e backlog apenas linkam.

## Docs úteis
- `Desenvolvimento/Docs/index.md` — entrada da documentação técnica
- `Desenvolvimento/Docs/Tech/DevelopmentRules.md` — branches, commits, versionamento
- `Desenvolvimento/Docs/Architecture/architecture_decisions.md` · `Desenvolvimento/Docs/Tech/tech_debt.md` · `Desenvolvimento/Docs/Roadmap/roadmap.md`
