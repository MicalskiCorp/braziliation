# Braziliation – Guia para agentes

Projeto **Unity 6** (2D, URP, C#): jogo plataforma pixel art, tema dieselpunk pós-apocalíptico brasileiro.

## Onde está o código
- **Core**: `Desenvolvimento/Assets/Scripts/Core/` — GameInitializer, CameraScaler
- **Outros scripts**: `Desenvolvimento/Assets/Scripts/` (ex.: `UI/`; ver `Desenvolvimento/Docs/Architecture/Assets/AssetsStructure.md`)
- **Cenas**: `Desenvolvimento/Assets/Scenes/` (SampleScene.unity, teste1.unity)
- **Configuração**: `Desenvolvimento/ProjectSettings/`, `Desenvolvimento/Packages/manifest.json`
- **Sistemas C# puros**: `Desenvolvimento/src/Braziliation.Game.Core/`
- **Testes .NET**: `Desenvolvimento/dotnet-tests/Braziliation.Game.Tests/`

## Agentes disponíveis (VS Code Copilot)

Todos os agentes de 2ª camada (estrutura) estão em `Braziliation/.github/agents/`. Acione via `@NomeDoAgente`.
A 1ª camada (personas) vive em `.github/agents/` na raiz do workspace — cada persona delega para o agente de estrutura correspondente, deixado a parte do projeto para cada desenvolvedor editar de acordo com sua preferência.

| Agente | Use para |
|--------|----------|
| `@TechLead` | Direção técnica, padrões, routing, limites de sistema, interfaces, ADRs |
| `@UnityDeveloper` | Tudo Unity: setup de engine (URP, action maps, build) e wiring de runtime (UI, MonoBehaviours, ServiceLocator) |
| `@SystemsDeveloper` | Save, Settings, Storage (C# puro, sem Unity) |
| `@GameplayEngineer` | Player, inimigos, combate, mecânicas |
| `@QAEngineer` | Revisão, edge cases, acceptance criteria |
| `@TestEngineer` | Testes xUnit automatizados |
| `@GameArchitect` | Estrutura Markdown em `Desenvolvimento/Docs/`; lê `Desenvolvimento/Docs/TODO.md` no Passo 0; processa handoffs do @GameCreative — nunca invoca agentes de implementação |
| `@Historiador` | Pesquisa histórica e folclórica via web; organização em `Design/Pesquisa/`; gera TODOs em `Design/Criativo/TODO.md` — nunca invoca @GameCreative |
| `@GameCreative` | Lendas, brainstorm, personagens, lore em `Design/Criativo/`; lê `Design/Pesquisa/` como contexto; gera TODOs em `Desenvolvimento/Docs/TODO.md` — nunca invoca @GameArchitect |
| `@AgentArchitect` | **Orquestrador Swarm** — abre sessões de desenvolvimento, lê TODO.md e roadmap, classifica tarefas, distribui comandos para agentes especializados, consolida resultados e documenta decisões; também cria, refatora e valida agentes `.agent.md` |
| `@SpriteArtist` | Geração programática de sprites pixel art (specs JSON, geradores procedurais) com ciclo de crítica visual contra a style-bible; segue `Design/GuiasDeArte/pipeline-sprites-programaticos.md` — não decide direção de arte nem faz wiring Unity |

## Processos do Projeto

> Mapa de todos os fluxos operacionais do ecossistema Braziliation. Cada processo referencia seu documento canônico — este mapa não duplica o conteúdo, só conecta os pontos.

### 1. Fluxo entre Camadas (Modelo Reativo)

Cada camada é acionada **manualmente** pelo usuário. Nenhum agente invoca outro automaticamente.

```
@Historiador
  └─ Pesquisa em Design/Pesquisa/  +  Design/Pesquisa/TODO.md
  └─ Escreve handoffs em Design/Criativo/TODO.md
         ↓ (usuário aciona manualmente)
@GameCreative
  └─ Lê Design/Criativo/TODO.md  +  valida em Design/Pesquisa/
  └─ Cria/edita em Design/Criativo/
  └─ Escreve handoffs em Desenvolvimento/Docs/TODO.md
         ↓ (usuário aciona manualmente)
@GameArchitect
  └─ Lê Desenvolvimento/Docs/TODO.md (Passo 0)
  └─ Cria/edita em Desenvolvimento/Docs/
  └─ Escreve TODOs para agentes de implementação
         ↓ (usuário aciona manualmente)
@GameplayEngineer / @UnityDeveloper / @SystemsDeveloper
  └─ Implementam em Desenvolvimento/Assets/ e src/
```

### 2. Descoberta de agentes por cwd

O Claude Code só descobre `.claude/agents/` (e `.claude/skills/`) relativos ao diretório de trabalho aberto — não busca em subpastas nem acumula as duas camadas ao mesmo tempo.

| Abrir o workspace em... | Camada ativa | O que fica disponível |
|--------------------------|---------------|------------------------|
| `d:\Backup\Projetos\Games` (raiz) | 1ª camada (personas: Jarvis, Computador, wrappers finos) | Só as personas — elas leem o `.agent.md` de referência via caminho de arquivo, então funcionam mesmo sem a 2ª camada carregada |
| `Braziliation/` | 2ª camada (agentes funcionais + as 7 skills) | Agentes funcionais completos e as skills descritas na seção 3 — **use este cwd para qualquer trabalho real no projeto** |

No formato Copilot (VS Code), `@Agente` funciona a partir de qualquer cwd dentro do repositório, já que a descoberta não é escopada por diretório da mesma forma.

### 3. Skills — catálogo por situação

As 7 skills em `Braziliation/.claude/skills/` só existem no formato Claude (sem equivalente Copilot) e só são chamáveis por um agente se `Skill` estiver na lista `tools:` do seu frontmatter. Mapeamento atual — agente dono × skill × quando usar:

| Skill | Agente(s) | Quando invocar |
|-------|-----------|-----------------|
| [`sprite-pipeline`](.claude/skills/sprite-pipeline/SKILL.md) | `@SpriteArtist` | Gerar ou validar um sprite programático (spec JSON, ciclo crítica visual, `palette_check`) |
| [`novo-asset`](.claude/skills/novo-asset/SKILL.md) | `@SpriteArtist` | Pedido de asset novo sem brief/context pack ainda existente |
| [`nova-cidade`](.claude/skills/nova-cidade/SKILL.md) | `@GameCreative` (passos 1-3, 5-6) · `@UnityDeveloper` (passo 4 — pastas em `Assets/Art/`) | Criar cidade/estado novo; `@GameCreative` não executa o passo 4 (sem `Bash`, nunca toca fontes do engine) — registra pendência para `@UnityDeveloper` |
| [`handoff`](.claude/skills/handoff/SKILL.md) | `@Historiador`, `@GameCreative`, `@GameArchitect` | Fechar um item de uma camada e escrever a entrada formatada no TODO da camada seguinte |
| [`novo-agente`](.claude/skills/novo-agente/SKILL.md) | `@AgentArchitect` (Papel 2) | Criar, refatorar ou sincronizar um agente nas 2 camadas × 2 formatos |
| [`validar-todos`](.claude/skills/validar-todos/SKILL.md) | `@AgentArchitect` (Papel 3) | Auditar TODOs concluídos, cobertura de testes e gaps de milestone |
| [`structure-audit`](.claude/skills/structure-audit/SKILL.md) | `@AgentArchitect` (nível 4 — ecossistema) · `@GameArchitect` (níveis 2-3 — Design/Documentação) | Auditar disco vs. docs em qualquer nível; nunca corrige sem aprovação, só reporta |

### 4. Gestão de TODOs (3 índices vivos)

Cada camada tem seu próprio índice de pendências; nenhum agente escreve fora do seu ou do TODO da camada seguinte (handoff).

| TODO | Dono (leitura + escrita) | Lógica de operação |
|------|---------------------------|---------------------|
| `Design/Pesquisa/TODO.md` | `@Historiador` | Descrita no próprio corpo do agente (Modos 1-7) |
| `Design/Criativo/TODO.md` | `@GameCreative` | [`Design/BackLog/BackLog.md`](Design/BackLog/BackLog.md) — operações `listar` / `concluído` / `adicionar` / `atualizar-status` / `varredura` |
| `Desenvolvimento/Docs/TODO.md` | `@GameArchitect` (Passo 0 / Passo Final) | Descrita no corpo do agente; seção `## Handoffs do @GameCreative` recebe itens da camada criativa |

### 5. Processo de Handoff

Rotas válidas: Pesquisa→Criativo, Criativo→Documentação, Documentação→Implementação. Nunca pula camada sem pedido explícito. Protocolo executável: skill [`handoff`](.claude/skills/handoff/SKILL.md).

### 6. Processo de Auditoria

Duas frentes complementares, ambas reportam antes de corrigir:
- **Estrutura** (disco vs. docs, paridade de agentes, skills): skill [`structure-audit`](.claude/skills/structure-audit/SKILL.md).
- **TODOs/cobertura de testes/gaps de milestone**: skill [`validar-todos`](.claude/skills/validar-todos/SKILL.md), Papel 3 do `@AgentArchitect` em [`AgentArchitect.agent.md`](.github/agents/AgentArchitect.agent.md).

### 7. Processo de criação/atualização de agente

`@AgentArchitect` (Papel 2) via skill [`novo-agente`](.claude/skills/novo-agente/SKILL.md) — sempre varre o inventário existente antes de criar, produz os 4 arquivos (2 camadas × 2 formatos) e atualiza a tabela abaixo.

### 8. Processo de asset/sprite

`Design/Criativo/` (conceito) → skill [`novo-asset`](.claude/skills/novo-asset/SKILL.md) (brief + context pack) → skill [`sprite-pipeline`](.claude/skills/sprite-pipeline/SKILL.md) via `@SpriteArtist` (geração + validação) → registro em `Docs/Architecture/indices/assets.md`. Guia canônico completo: [`Design/GuiasDeArte/pipeline-sprites-programaticos.md`](Design/GuiasDeArte/pipeline-sprites-programaticos.md).

### 9. Processo de nova cidade/estado

`@GameCreative` (ou usuário) via skill [`nova-cidade`](.claude/skills/nova-cidade/SKILL.md) — scaffolding em `Design/Criativo/`, paleta em `Design/ArteConceitual/Paletas/`, pastas Unity delegadas a `@UnityDeveloper`.

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
