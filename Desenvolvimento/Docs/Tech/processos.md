# Processos dos Agentes — Braziliation

> Detalhe operacional do ecossistema de agentes. O mapa curto (agentes, camadas, TODOs) está no [`AGENTS.md`](../../../AGENTS.md), que entra em toda sessão; este arquivo é lido **sob demanda** — por isso o detalhe vive aqui. O passo a passo de cada processo, camada por camada, está no [manual de processos](../Processos/index.md).

## 1. Descoberta de agentes por cwd

O Claude Code só descobre `.claude/agents/` e `.claude/skills/` relativos ao diretório aberto.

| Abrir o workspace em... | Camada ativa | O que fica disponível |
|--------------------------|---------------|------------------------|
| Raiz do workspace (pasta pai do repositório) | 1ª camada (personas: Jarvis, Computador, wrappers finos) | Só as personas — elas leem o agente de referência por caminho de arquivo |
| `Braziliation/` | 2ª camada (agentes funcionais + skills) | Tudo — **use este cwd para trabalho real** |

A 1ª camada vive **fora do repositório, por decisão do usuário (2026-09-13)**. Hoje há wrappers para 9 dos 11 agentes; `@Historiador` e `@AgentArchitect` só existem na 2ª camada.

## 2. Skills — catálogo por situação

As skills vivem em `.claude/skills/`. Cada agente dono tem `Skill` em `tools:` e uma tabela "Situação → skill" no corpo. **Pré-carregamento (`skills:` no frontmatter) só para a skill que o agente usa em toda invocação** — `gerir-todo` no GameArchitect e no GameCreative, `sprite-pipeline` no SpriteArtist, `unity-validar` no UnityDeveloper e no GameplayEngineer, `validar-todos` e `structure-audit` no AgentArchitect (são forks dele). As demais carregam sob demanda: pré-carregar skill situacional põe o texto dela em toda execução do agente. O `DocsConsistencyTests` falha se uma skill não aparecer nesta tabela.

| Skill | Agente(s) | Quando invocar |
|-------|-----------|-----------------|
| [`gerir-todo`](../../../.claude/skills/gerir-todo/SKILL.md) | `@GameArchitect`, `@GameCreative`, `@Historiador`, `@AgentArchitect` | Operar o TODO da própria camada: listar, adicionar, status, concluir (regra de baixa de cada TODO), `concept-art`, varredura |
| [`concept-art`](../../../.claude/skills/concept-art/SKILL.md) | `@SpriteArtist` | Etapa 2 (rota C): concept de personagem, criatura ou cena no ComfyUI, com log de lote, gate e aprovação |
| [`sprite-pipeline`](../../../.claude/skills/sprite-pipeline/SKILL.md) | `@SpriteArtist` | Gerar ou validar um sprite programático (spec JSON, ciclo de crítica visual, `palette_check`) |
| [`novo-asset`](../../../.claude/skills/novo-asset/SKILL.md) | `@SpriteArtist` | Asset novo sem brief/context pack |
| [`nova-cidade`](../../../.claude/skills/nova-cidade/SKILL.md) | `@GameCreative` (Modo 6) · `@UnityDeveloper` (passo 5) | Estrutura de cidade ou estado novo; o passo das pastas em `Assets/Art/` vira pendência para `@UnityDeveloper` |
| [`handoff`](../../../.claude/skills/handoff/SKILL.md) | `@Historiador`, `@GameCreative`, `@GameArchitect` | Escrever no TODO da camada seguinte — inclui o briefing da rota Pesquisa→Criativo (processar, brainstorm, revisão) |
| [`novo-agente`](../../../.claude/skills/novo-agente/SKILL.md) | `@AgentArchitect` (Papel 2) | Criar ou refatorar agente (arquivo em `.claude/agents/`, wrapper da 1ª camada, registro no `AGENTS.md`) |
| [`validar-todos`](../../../.claude/skills/validar-todos/SKILL.md) | `@AgentArchitect` (Papel 3) | Auditar TODOs concluídos, cobertura de testes e gaps de milestone |
| [`structure-audit`](../../../.claude/skills/structure-audit/SKILL.md) | `@AgentArchitect` (nível 4) · `@GameArchitect` (níveis 2-3) | Auditar disco × docs; só reporta, não corrige sem aprovação |
| [`hemeroteca-blumenau`](../../../.claude/skills/hemeroteca-blumenau/SKILL.md) | `@Historiador` | Fato, data ou nome de Blumenau em fonte primária ("Blumenau em Cadernos") |
| [`processar-entrevistas`](../../../.claude/skills/processar-entrevistas/SKILL.md) | `@Historiador` | Curar entrevistas/conversas de pesquisa capturadas via WhatsApp (ADR-009) — áudio, texto, foto e documento — em `Design/Pesquisa/Entrevistas/_pendente-curadoria/` |
| [`meta-check`](../../../.claude/skills/meta-check/SKILL.md) | `@UnityDeveloper` · `@SpriteArtist` | Pares asset/`.meta` em `Desenvolvimento/Assets/` |
| [`unity-validar`](../../../.claude/skills/unity-validar/SKILL.md) | `@UnityDeveloper` · `@GameplayEngineer` · `@TestEngineer` | Compilar o Unity em batchmode antes de commitar mudança em `Assets/`; `--testes` roda os EditMode |
| [`fechar-decisao`](../../../.claude/skills/fechar-decisao/SKILL.md) | `@GameCreative` (com `@TechLead` nos números) | Transformar pendência de design parada em DDR aprovado, com handoff |
| [`novo-adr`](../../../.claude/skills/novo-adr/SKILL.md) | `@TechLead` | Registrar decisão de arquitetura e marcar o ADR substituído |
| [`novo-inimigo`](../../../.claude/skills/novo-inimigo/SKILL.md) | `@GameplayEngineer` | Inimigo como perfil de dados + teste + linha em `InimigosIA.md` |

**Plugins habilitados** (`.claude/settings.json` → `enabledPlugins`): `unity` (skills oficiais da Unity, entre elas `2d-pixel-perfect`, `sprite-editor`, `tilemap-*`, `unity-cli`) e `skill-creator` (criar e avaliar skills).

## 3. Gestão de TODOs

| TODO | Dono | Item concluído |
|------|------|----------------|
| `Design/Pesquisa/TODO.md` | `@Historiador` | Vai para `## Concluído` com a data |
| `Design/Criativo/TODO.md` | `@GameCreative` | Vai para `## Concluído` com a data |
| `Desenvolvimento/Docs/TODO.md` | `@GameArchitect` | A linha sai; o registro é o commit. `TODO-arquivo.md` é histórico congelado |

Operações nos três (`listar`, `adicionar`, `atualizar-status`, `concluído`, `concept-art`, `varredura`): skill `gerir-todo`. Escrita no TODO da camada seguinte: skill `handoff`.

**Fonte única de status:** a pendência vive só no TODO da camada. `Roadmap/roadmap.md` e `Roadmap/backlog.md` descrevem fases e features e **linkam** o TODO — não repetem status de pendência.

## 4. Auditoria

- **Estrutura** (disco × docs, agentes, skills): skill `structure-audit`.
- **TODOs, cobertura e milestone:** skill `validar-todos` (Papel 3 do `@AgentArchitect`).

Ambas reportam antes de corrigir.

## 5. Criação e atualização de agente

`@AgentArchitect` (Papel 2) via skill `novo-agente`: inventário pela tabela do `AGENTS.md`, agente escrito em `.claude/agents/{nome}.md` e linha no `AGENTS.md` (o `AgentDefinitionTests` cobra). Mudou um modo ou uma skill? Atualizar o arquivo da camada em `Desenvolvimento/Docs/Processos/`.

## 6. Asset/sprite (5 etapas)

Ideia em `Design/Criativo/` (`@GameCreative`) → concept art aprovado em `Design/ArteConceitual/{categoria}/{asset}/` (`@SpriteArtist`, rota C) → especificação de variações (`variation-spec-template.md`, para personagens e inimigos complexos) → skill `novo-asset` (brief + context pack) → skill `sprite-pipeline` (spec JSON, geração, validação) → registro em `Docs/Architecture/indices/assets.md`, cuja seção "Backlog por Asset" rastreia as 5 etapas. Props simples pulam concept art e especificação. Guia: [`pipeline-sprites-programaticos.md`](../../../Design/GuiasDeArte/pipeline-sprites-programaticos.md).

## 7. Nova cidade/estado

Skill `nova-cidade`: scaffolding em `Design/Criativo/`, paleta em `Design/ArteConceitual/Paletas/`, pastas Unity delegadas ao `@UnityDeveloper`.

## 8. Travas automáticas

| Onde | O que roda | Pega |
|------|------------|------|
| Início de sessão (hook `SessionStart`) | `.claude/hooks/session_snapshot.py` | Injeta git, pendências Alta dos 3 TODOs e o último `unity-validar` |
| Ao editar (`PreToolUse`/`PostToolUse`) | `block_generated_dirs.py`, `build_game_core.py` | Escrita em pasta gerada ou em arquivo congelado (`TODO-arquivo.md`, DLL do core); core que parou de compilar |
| Antes do commit (`.githooks/pre-commit`) | `dotnet test`, `meta-check/check_clean_checkout.py`, `unity-validar/scripts/check_state.py` | Testes e guardas, `.meta` faltando, cor fora da paleta, script Unity em stage sem validação OK posterior à edição. Os gates de `.meta` e paleta rodam contra o **índice** desde 2026-09-19, não contra o disco — ver §8.1. Ativar por clone: `git config core.hooksPath .githooks` |
| No push e no checkout (`.githooks/post-checkout`, `post-commit`, `post-merge`, `pre-push`) | Hooks do Git LFS | Objetos LFS baixados e enviados. Versionados desde 2026-09-19: como o `core.hooksPath` aponta para uma pasta do repositório, o `git lfs install` os deposita ali, e sem o `pre-push` um push publica ponteiros sem os binários (218 arquivos em LFS). Por isso o **git-lfs virou requisito rígido**: sem ele instalado, os quatro saem com código 2 e o git aborta a operação |
| No CI (`.github/workflows/ci.yml`) | os mesmos | O que escapou do pre-commit |
| No CI Unity (`unity-ci.yml`, GameCI) | nada — job `skipped` | **Desligado por decisão (ADR-010):** a Unity encerrou a ativação de Personal em CI. A cobertura do lado Unity é a skill `unity-validar`, exigida pelo pre-commit ([`unity-ci.md`](unity-ci.md)) |

Guardas dentro do `dotnet test`: `GitIgnoreGuardTests`, `DocsConsistencyTests` (links, pastas documentadas, todo `.cs` numa ficha de sistema, roteadores completos, feature no índice e no backlog, ADR substituído, catálogo de skills), `TokenBudgetTests` (tetos de tamanho de prompt e doc), `ConventionGuardTests` (serviço com teste dedicado, paleta com status), `UnityAssetConsistencyTests`, `AgentDefinitionTests` (nome = arquivo, `model:`, registro no `AGENTS.md`, `.github/` só com CI e templates) e `RepositoryLayoutTests`.

Scripts que as skills chamam para a parte mecânica: `gerir-todo/todo.py` (listar, varredura), `validar-todos/todos_inline.py` (`// TODO` classificados), `unity-validar/scripts/check_state.py` (gate do commit), `meta-check/check_meta_pairs.py`, `unity-validar/scripts/validar.py`, `meta-check/check_clean_checkout.py`.

### 8.1 Disco × checkout limpo

O ponto cego estrutural do projeto: o que existe na máquina de quem trabalha não é o que o CI recebe. Pasta vazia (o git não versiona), arquivo ignorado, artefato gerado — os três passam despercebidos por qualquer gate que olhe a árvore de trabalho.

Foi assim que duas pastas de arte vazias, com os `.meta` ainda versionados, derrubaram o CI de 13 a 19 set 2026 enquanto o `meta-check` local aprovava todo commit. Seis dias, oito runs vermelhos, nenhuma trava local capaz de ver.

`meta-check/check_clean_checkout.py` fecha a diferença: materializa o índice do git com `git checkout-index` numa pasta temporária e roda os gates **a partir dela**, então a versão commitada dos próprios scripts de gate é que decide. Custa ~5 s. O pre-commit o chama no lugar da checagem em disco; rodá-lo à mão antes de um push também vale, sobretudo depois de remover arquivos de uma pasta de `Assets/`.

## 9. Servidores MCP

`.mcp.json` + `enabledMcpjsonServers`: `aseprite` (pixel-mcp sobre o Aseprite local — `@SpriteArtist`), `unity` (CLI oficial; controla um Editor **aberto** com `com.unity.pipeline` — `@UnityDeveloper`) e `comfyui` (configurado no usuário; concept art da rota C). Cada agente declara só os MCPs que usa em `mcpServers:`.

## 10. Contexto de IA

| Arquivo | Conteúdo | Como é usado |
|---------|----------|--------------|
| [`Desenvolvimento/Docs/GDD/visao.md`](../GDD/visao.md) | Pitch, pilares e experiência-alvo | Lido pelos agentes e pela skill `fechar-decisao` |
| `.claude/rules/csharp.md` | Convenções C# e definição de pronto | Carregada ao tocar `*.cs` |
| `.claude/rules/arte.md` · [`direcao-de-arte.md`](../../../Design/GuiasDeArte/direcao-de-arte.md) | Direção de arte e áudio | Regra carregada nas pastas de arte (`ArteConceitual`, `ArteFonte`, `GuiasDeArte`, `Assets/Art`); guia sob demanda |
| `.claude/rules/todos.md` | Regras de TODO e status | Carregada em `**/TODO.md` e no `Roadmap/` |
| `Desenvolvimento/Docs/Architecture/architecture_decisions.md` | ADRs | Referenciado pelos agentes |
| `Desenvolvimento/Docs/Tech/tech_debt.md` | Dívida técnica | Referenciado pelos agentes |

## 11. Modo, skill ou regra — onde cada procedimento mora

Critério aplicado na consolidação de 2026-09-13 (Historiador 7→4 modos, GameCreative 10→7, GameArchitect 6→4, skills `gerir-todo` e `concept-art`, definição de pronto em regra). Seguir ao criar ou refatorar agente:

| Vira… | Quando | Exemplo |
|-------|--------|---------|
| **Modo do agente** | O procedimento é o núcleo daquele agente e depende das barreiras e ferramentas dele | Pesquisar tema (Historiador), Nova feature (GameArchitect) |
| **Um modo com parâmetro** | Vários gatilhos disparam o mesmo procedimento com saída diferente | "Pesquisar" e "Fontes sobre"; "Listar" e "Compilar estado" |
| **Skill** | O procedimento é usado por mais de um agente, carrega script ou gate próprio, ou é longo e raro (carga sob demanda) | `gerir-todo`, `handoff`, `concept-art`, `hemeroteca-blumenau` |
| **Regra por caminho** (`.claude/rules/`) | Vale sempre que alguém toca um tipo de arquivo, qualquer que seja o agente | Definição de pronto em `csharp.md`; regras de TODO em `todos.md` |
| **Script** (tool chamada pela skill) | Parte determinística: parsear, contar, cruzar, copiar — o modelo só recebe o resultado | `todo.py` (varredura), `todos_inline.py`, `check_state.py`, `validar.py` |
| **Teste** (`dotnet test`) | Invariante verificável do repositório — vira falha de build, não item de auditoria | Roteador completo, feature no backlog, serviço com teste, paleta com status |
| **Hook** | Tem de acontecer sozinho num evento (sessão, edição, commit) | Foto do projeto na sessão, bloquear arquivo congelado, gate do Unity no commit |
| **Skill em fork** (`context: fork`) | Procedimento que só devolve relatório e leria muito texto — isola o contexto | `validar-todos`, `structure-audit`, `hemeroteca-blumenau` |

Não roda em fork a skill que conversa com o usuário no meio (aprovação de concept art, DDR, handoff): o fork devolve um resultado e perde o diálogo.

Não vira skill: gatilho que só roteia para um agente — o agente já é o ponto de entrada (`@agent-{nome}`), e cada skill a mais põe sua descrição em toda sessão.
