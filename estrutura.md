# Estrutura do repositório — mapa de navegação

> **Leia antes de buscar.** Cada linha diz onde fica uma coisa: vá direto ao arquivo, sem `Glob` nem
> `Grep` para descobrir caminho. Este mapa é a porta de entrada dos índices que o projeto já tem; o
> detalhe continua neles. Skill que traz a sessão até aqui: `estrutura`. Todo link deste arquivo é
> verificado pelo `DocsConsistencyTests`, e caminho que mudar sem atualizar o mapa quebra o build.

## 1. Como buscar sem gastar

Cada chamada de ferramenta relê o contexto inteiro da sessão: em 2026-11-05, uma execução da Central
fez 31 buscas às cegas e leu 2,4 M tokens em 30 requisições. Para gastar menos, faça menos rodadas e leia menos texto em cada uma.
A versão curta destas regras, carregada em toda sessão, é a [busca-com-filtro.md](.claude/rules/busca-com-filtro.md).

1. **Caminho no mapa, no pedido ou no `CLAUDE.md` → `Read` direto.** Não use `Glob` para "confirmar" que existe.
2. **Caminho desconhecido → o `index.md` da área** (§2). Cada roteador lista todos os arquivos da pasta (o teste cobra).
3. **`Grep` sempre com `path` da área**, e com `glob` ou `type` quando der. **Nunca na raiz**: ela varre
   `Library/`, `.venv/` e cenas YAML. Use `files_with_matches` para achar e `content` com `-n` e `head_limit` para ler.
   **`Glob` com `path` não aceita `/` no padrão** neste Windows (volta "No files found" para arquivo
   que existe): a pasta vai no `path` e o padrão é só o nome, `**/*Save*Tests.cs`. `Glob` não acha pasta, só arquivo.
4. **Arquivo grande** (TODOs, `tech_debt.md`, ADRs, `CREDITS.md`): `Grep` pelo termo e `Read` com
   `offset`/`limit`. Cena, prefab e `.asset` nunca se leem inteiros: busque o GUID ou o `m_Name`.
5. **Chamadas independentes saem juntas**, no mesmo turno. Busca que já respondeu não se repete.
6. **Script `.cs`:** a ficha do sistema lista todos ("Fontes Técnicas"). Domínio Unity →
   `Assets/Scripts/{Domínio}/`; lógica pura → `src/Braziliation.Game.Core/{Sistema}/`.
7. Achou fora do mapa um caminho estável (pasta ou arquivo canônico)? Acrescente a linha na §2.

## 2. Onde está

### Processo, agentes e regras

| Preciso de… | Vá em |
|-------------|-------|
| Agente (`--agent`, `@Nome`) | `.claude/agents/{nome-kebab}.md` · lista e camadas no [AGENTS.md](AGENTS.md) |
| Skill e quando usar | `.claude/skills/{nome}/SKILL.md` · catálogo em [processos.md §2](Desenvolvimento/Docs/Tech/processos.md) |
| Regra por caminho (C#, arte, TODO) | [.claude/rules/](.claude/rules/) |
| Hooks e permissões do Claude Code | [.claude/hooks/](.claude/hooks/) · [settings.json](.claude/settings.json) · MCPs em [.mcp.json](.mcp.json) |
| Pre-commit e CI | [.githooks/pre-commit](.githooks/pre-commit) · [ci.yml](.github/workflows/ci.yml) |
| Formato de commit, branches, versão | [DevelopmentRules.md](Desenvolvimento/Docs/Tech/DevelopmentRules.md): `tipo(escopo): descrição` em português |
| Passo a passo por camada (humanos) | [Processos/](Desenvolvimento/Docs/Processos/index.md) |
| Barreiras do @Historiador · memória dele | [historian-guardrails.md](memories/repo/historian-guardrails.md) · [agent-memory/historiador/](.claude/agent-memory/historiador/MEMORY.md) |
| Visão geral e setup (humanos) | [README.md](README.md) · [Desenvolvimento/README.md](Desenvolvimento/README.md) |

### Pendências e decisões

| Preciso de… | Vá em |
|-------------|-------|
| Pendência de Pesquisa · Criativo · Dev | [Pesquisa](Design/Pesquisa/TODO.md) · [Criativo](Design/Criativo/TODO.md) · [Dev](Desenvolvimento/Docs/TODO.md), operados pela skill `gerir-todo` |
| Dívida técnica | [tech_debt.md](Desenvolvimento/Docs/Tech/tech_debt.md): item pago sai do arquivo e o registro é o commit |
| Decisão de arquitetura (ADR) | [architecture_decisions.md](Desenvolvimento/Docs/Architecture/architecture_decisions.md): `Grep "^## ADR-0NN"` |
| Decisão de design (DDR) | [GDD/Decisoes/](Desenvolvimento/Docs/GDD/Decisoes/index.md) |
| Fase e backlog | [roadmap.md](Desenvolvimento/Docs/Roadmap/roadmap.md) · [backlog.md](Desenvolvimento/Docs/Roadmap/backlog.md) |

### Código

| Preciso de… | Vá em |
|-------------|-------|
| Que script faz X / onde está o `.cs` | [Sistemas/](Desenvolvimento/Docs/Architecture/Sistemas/index.md): uma ficha por sistema |
| Scripts Unity por domínio (ADR-005) | [Assets/Scripts/](Desenvolvimento/Assets/Scripts/): `Core/`, `Gameplay/`, `Build/`, `Crafting/`, `Enemies/`, `UI/` |
| Ferramentas do Editor | [Assets/Editor/](Desenvolvimento/Assets/Editor/): `Art/`, `Enemies/`, `Gameplay/`, `Interactables/`, `Menu/` |
| Escala de placeholders (32 PPU) | [PixelScale.cs](Desenvolvimento/Assets/Editor/Art/Escala/PixelScale.cs) |
| Input | [GameInput.cs](Desenvolvimento/Assets/Scripts/Core/GameInput.cs) · [action map](Desenvolvimento/Assets/InputSystem_Actions.inputactions) |
| Serviços na cena | [GameServiceLocator.cs](Desenvolvimento/Assets/Scripts/Core/GameServiceLocator.cs) |
| Core C# puro | [src/Braziliation.Game.Core/](Desenvolvimento/src/Braziliation.Game.Core/): `Build/`, `Crafting/`, `Enemies/`, `SaveSystem/`, `Serialization/`, `Settings/`, `Storage/` |
| Testes xUnit e guardas do repositório | [Tests/Braziliation.Game.Tests/](Desenvolvimento/Tests/Braziliation.Game.Tests/): `{Sistema}Tests.cs`, `TestDoubles.cs`, `DocsConsistencyTests`, `TokenBudgetTests` |
| Testes EditMode | [Assets/Tests/EditMode/](Desenvolvimento/Assets/Tests/EditMode/) |
| Inimigo como dado | [InimigosIA.md](Desenvolvimento/Docs/Mechanics/InimigosIA.md) · [ScriptableObjects/](Desenvolvimento/Assets/ScriptableObjects/) |
| Pacotes e versão do Unity | [manifest.json](Desenvolvimento/Packages/manifest.json) · [ProjectVersion.txt](Desenvolvimento/ProjectSettings/ProjectVersion.txt) |

### Assets Unity

| Preciso de… | Vá em |
|-------------|-------|
| O que vai em cada pasta de `Assets/` | [AssetsStructure.md](Desenvolvimento/Docs/Architecture/Assets/AssetsStructure.md) |
| Estado de um asset (5 etapas) e páginas publicadas | [indices/assets.md](Desenvolvimento/Docs/Architecture/indices/assets.md) |
| Cenas | [MainMenu](Desenvolvimento/Assets/Scenes/Menus/MainMenu.unity) (primeira do build) · [DemoGameplay](Desenvolvimento/Assets/Scenes/DemoGameplay.unity) |
| Arte importada · terceiros | [Assets/Art/](Desenvolvimento/Assets/Art/) · licenças em [CREDITS.md](Desenvolvimento/CREDITS.md) |

### Documentação técnica e de jogo

| Preciso de… | Vá em |
|-------------|-------|
| Entrada da documentação técnica | [Docs/index.md](Desenvolvimento/Docs/index.md) |
| Arquitetura e metodologia de indexação | [Architecture/](Desenvolvimento/Docs/Architecture/index.md) · [motor/](Desenvolvimento/Docs/Architecture/motor/index.md) |
| Visão, pilares, features | [visao.md](Desenvolvimento/Docs/GDD/visao.md) · [GDD/Features/](Desenvolvimento/Docs/GDD/Features/index.md) |
| Mecânicas (build, crafting, IA) | [Mechanics/](Desenvolvimento/Docs/Mechanics/index.md) |
| Sincronizar código, ficha e feature | [protocolo-comunicacao.md](Desenvolvimento/Docs/Architecture/indices/protocolo-comunicacao.md) |
| Templates (ficha, feature, cidade) | [Docs/Models/](Desenvolvimento/Docs/Models/index.md) · [Design/Models/](Design/Models/index.md) |

### Design: pesquisa, criativo e arte

| Preciso de… | Vá em |
|-------------|-------|
| Pesquisa com fonte, por cidade | [SantaCatarina/](Design/Pesquisa/Estados/SantaCatarina/index.md) lista as cidades → `cidades/{Cidade}/index.md` · [Pesquisa/](Design/Pesquisa/index.md) |
| Entrevistas (WhatsApp) | [Entrevistas/](Design/Pesquisa/Entrevistas/index.md) |
| Ficha criativa de cidade | [cidades/](Design/Criativo/Estados/SantaCatarina/cidades/index.md) → `{Cidade}/index.md` · estados em [Estados/](Design/Criativo/Estados/index.md). Pasta = nome sem espaço nem acento: `SantaCatarina/cidades/SaoFranciscoDoSul/` |
| Lendas | [catalogo.md](Design/Criativo/Lendas/catalogo.md) · [mapeamento.md](Design/Criativo/Lendas/mapeamento.md) |
| Premissa, arcos, personagens | [Historia/](Design/Criativo/Historia/index.md) |
| Direção de arte, escala, paletas, pipelines | [GuiasDeArte/](Design/GuiasDeArte/index.md): comece por `style-bible.md` |
| Paleta de cidade | [Paletas/](Design/ArteConceitual/Paletas/): `{cidade}.json` |
| Concept art aprovado | [ArteConceitual/](Design/ArteConceitual/index.md): `{Categoria}/{asset}/` |
| Script de arte (render, paleta, mock) | [catalogo.md](Design/ArteFonte/Ferramentas/catalogo.md) · motor [pxfx/](Design/ArteFonte/Ferramentas/pxfx/index.md) |
| Context pack, lotes, página de personagem | [IA/ContextPacks/](Design/ArteFonte/IA/ContextPacks/) · [IA/Paginas/](Design/ArteFonte/IA/Paginas/) |

### Central

| Preciso de… | Vá em |
|-------------|-------|
| Como funciona · filas | [README](Central/README.md) · [filas.json](Central/filas.json) |
| Contrato e pedido enviados ao agente | [conversa.py](Central/central/conversa.py) (`CONTRATO`) · [app.py](Central/central/app.py) (`montar_pedido`) |
| Módulos (`Central/central/`) | `app` rotas · `execucoes` ciclo item → sessão → validação → commit · `filas` · `agente` sessão `claude -p` · `conversa` stream-json e contrato · `tokens` · `gitops` worktree e commit · `fontes` dívida, entrevistas e saúde · `config` · `seguranca` |
| Testes da Central | [Central/tests/](Central/tests/): `test_{módulo}.py` |

## 3. Não ler

| O quê | Por quê |
|-------|---------|
| `Desenvolvimento/Library/`, `Temp/`, `Logs/`, `obj/`, `bin/`, `.vs/` | Gerados pelo Unity e pelo .NET |
| `Desenvolvimento/Assets/Plugins/Braziliation/` | DLL do core, saída de build |
| `Desenvolvimento/Docs/TODO-arquivo.md` | Histórico congelado: a pendência viva está no `TODO.md`. Só por `Grep`, e só quando o pedido for sobre histórico |
| `Design/ArteFonte/Ferramentas/vendor/pixelfx/` | Gabarito de paridade (ADR-016) |
| `Central/.venv/`, `Central/.estado/` | Dependências e estado das execuções |
| `Design/ArteFonte/IA/Outputs/`, `Rejected/` | Saída bruta de geração |
| `.unity`, `.prefab`, `.asset`, `.meta` | YAML grande: só `Grep` (GUID, `m_Name`) |

## 4. Onde criar

| Vai criar… | Onde e o que mais |
|------------|-------------------|
| Script Unity | Pasta do domínio + linha na ficha de `Sistemas/` + `.meta` + skill `unity-validar` |
| Tipo do core puro | `src/.../{Sistema}/` + teste xUnit (happy path, edge case, falha) + linha na ficha |
| Sistema novo | Ficha pelo [ModelSistema.md](Desenvolvimento/Docs/Models/ModelSistema.md), listada no índice de `Sistemas/` |
| `.md` em `Desenvolvimento/Docs/` ou `Design/` | Linha no `index.md` da pasta. Pasta nova tem `index.md`. Teto de ~1.500 tokens para roteador e ~5.000 para documento |
| Feature | `GDD/Features/` + linha no índice e no `backlog.md` |
| Asset em `Assets/` | `.meta` no mesmo commit (skill `meta-check`); arte respeita a paleta |
| ADR · cidade · asset · inimigo · agente | Skills `novo-adr` · `nova-cidade` · `novo-asset` · `novo-inimigo` · `novo-agente` |
| Skill | `.claude/skills/{nome}/SKILL.md` + linha no catálogo de `processos.md` §2 |
| Pendência · handoff | Skills `gerir-todo` · `handoff` |
| Pasta nova de 1º ou 2º nível | Linha na §2 deste mapa |

Auditoria de disco × docs: skill `structure-audit`.
