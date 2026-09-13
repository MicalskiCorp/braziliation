# Implementação

> Camada 4 · Desenvolvimento · Fonte canônica: agentes em [`.claude/agents/`](../../../.claude/agents/) · regra [`csharp.md`](../../../.claude/rules/csharp.md) · skills [`novo-inimigo`](../../../.claude/skills/novo-inimigo/SKILL.md), [`unity-validar`](../../../.claude/skills/unity-validar/SKILL.md) · [`DevelopmentRules.md`](../Tech/DevelopmentRules.md). Este manual resume; em divergência, vale a fonte.

Agentes **@GameplayEngineer · @UnityDeveloper · @SystemsDeveloper · @TestEngineer · @QAEngineer** · Código **Assets/Scripts/ · src/Braziliation.Game.Core/** · Testes **Tests/Braziliation.Game.Tests/**

Lógica testável vive em C# puro (`src/`), sem Unity; o Unity só adapta. Scripts vão para a pasta do domínio (ADR-005: Core, Gameplay, Build, Crafting, Enemies, UI), todo input passa por `GameInput` (ADR-006) e UI nunca contém regra de jogo. A **definição de pronto** de qualquer código — teste primeiro no core, `unity-validar`, `.meta`, ficha de sistema, dívida e TODO registrados — é regra por caminho em `.claude/rules/csharp.md` (e no espelho do Copilot), aplicada a qualquer agente que toque `.cs`.

## I1 — Direção técnica e roteamento

**Quem:** @TechLead
**Aciona:** "onde colocar", "qual agente usar", "interface", "limite de módulo"

1. Classificar: feature, refatoração, decisão de arquitetura ou bugfix.
2. Apontar os docs que se aplicam (instructions, Architecture, Tech, Roadmap).
3. Definir limites: pasta, namespace, responsabilidade; propor interfaces (`IDamageable`, `IInteractable`) ou contrato de ScriptableObject.
4. Escolha estrutural → D7.
5. Expor trade-offs (performance, complexidade, dívida).
6. Entregar algo executável pelo agente certo.

- **Princípios:** Um script, um trabalho · dependência Core → domínios → UI · eventos em vez de acoplamento · dados em ScriptableObject

## I2 — Sistema C# puro com TDD

**Quem:** @TestEngineer → @SystemsDeveloper
**Aciona:** Save, settings, storage, serialização e a lógica pura de Build, Crafting e Enemies

1. Receber a API pública desejada.
2. @TestEngineer escreve os testes xUnit (caminho feliz, bordas, falhas; `Metodo_Contexto_Resultado`; fakes em `TestDoubles.cs`).
3. Confirmar que falham com a implementação ausente.
4. @SystemsDeveloper implementa: zero `UnityEngine`, dependências por construtor, nada estático, caminho injetado, JSON determinístico com `SaveJsonOptions.Default`.
5. Save: subir a versão exige degrau em `SaveMigrations.All`; load pelo `LoadDetailed` com `SaveLoadStatus` (ADR-007).
6. Rodar os testes até todos passarem; o build copia a DLL para `Assets/Plugins/` sozinho.
7. Linha na ficha do sistema (D3/D5).

- **Gate:** Classe sem teste não está concluída · `netstandard2.1`, C# 10

## I3 — Mecânica de gameplay

**Quem:** @GameplayEngineer
**Aciona:** "implementar mecânica", "sistema de combate", "player movement"

1. Ler GDD e `Mechanics/`; comportamento indefinido vira proposta de atualização de doc.
2. Propor os componentes: MonoBehaviours, ScriptableObjects, prefabs.
3. Colocar na pasta do domínio; extrair lógica testável para o core (I2).
4. Input novo: binding no action map + propriedade em `GameInput`.
5. Estados explícitos (idle, move, attack, hurt) e números sugeridos para tuning.
6. Rodar `unity-validar` (I7) e registrar o script na ficha.

- **Escopo:** Uma feature ou um inimigo por resposta

## I4 — Novo inimigo como dado

**Quem:** @GameplayEngineer · skill `novo-inimigo`

1. Exigir origem criativa (cidade, lenda ou DDR); sem ela, sugerir C9.
2. Ler `EnemyBehaviorProfile.cs` e "Como criar um inimigo novo" em `InimigosIA.md`.
3. Escolher o `EnemyAggressionStyle`; se nenhum servir, parar — estilo novo é mudança de motor (I1 + I2).
4. Definir números partindo do inimigo mais parecido, marcados como provisórios.
5. Teste primeiro em `EnemyBrainTests.cs` fixando o comportamento que define o inimigo.
6. Criar `Assets/ScriptableObjects/Enemies/{Nome}.asset` com os mesmos números (ou pendência para o Editor).
7. Linha no catálogo de `InimigosIA.md`; arte via A1/A3; prefab e animação via I5.

- **Gate:** Nenhum código por inimigo · mesmos números no teste, no asset e no catálogo

## I5 — Setup do engine e wiring Unity

**Quem:** @UnityDeveloper · MCP `unity`
**Aciona:** URP, câmera, physics layers, action map, UI, ServiceLocator, Steam Input

1. Classificar: setup de engine, wiring de runtime ou os dois.
2. Respeitar as restrições: Unity 6000.2, URP 2D, 640×360, 32 PPU, alvo PC/Steam.
3. Views passivas (`Show`/`Hide`), serviços obtidos do `GameServiceLocator` no `Awake`, zero regra de negócio.
4. Todo painel chama `EventSystem.SetSelectedGameObject` (teclado, controle, Steam Deck).
5. `[SerializeField]` sempre, com `[Header]`/`[Tooltip]`; layers via `GameLayers`.
6. Validar com `unity-validar` e `meta-check`; decisão relevante vai para ADR, atalho para `tech_debt.md`.

- **Editor aberto:** Usar o MCP `unity` em vez do batchmode

## I6 — Revisão de qualidade

**Quem:** @QAEngineer
**Aciona:** "revisar código", "edge case", "acceptance criteria", "está correto segundo o GDD"

1. Esclarecer o comportamento esperado, inferindo critérios do GDD e das mecânicas.
2. Listar casos: caminho feliz, bordas, falhas.
3. Revisar null refs, limites, validação de input, riscos de plataforma e de regressão.
4. Sugerir testes concretos (xUnit no core, EditMode no Unity) — quem escreve é o @TestEngineer.
5. Problema recorrente vai para `tech_debt.md`.

- **Não faz:** Não escreve teste nem corrige código (só leitura)

## I7 — Validação do lado Unity

**Quem:** skills `unity-validar` · `meta-check`

1. Com o Editor fechado: `py .claude/skills/unity-validar/scripts/validar.py` (~1–2 min).
2. `--testes` roda também os EditMode — exige a licença ativada na máquina.
3. Erro vem como `arquivo(linha,coluna): error CSxxxx`; corrigir e repetir.
4. `py .claude/skills/meta-check/check_meta_pairs.py` e incluir os `.meta` novos no commit.
5. Conferir o `git status`: import pode reescrever `.meta` e `ProjectSettings/`.

- **Gate:** Compilação reprovada bloqueia commit de script Unity
- **Registro:** `.claude/state/unity-validar.json`, lido no início de cada sessão

## I8 — Commit e versionamento

**Quem:** Todos · `Tech/DevelopmentRules.md`

1. Até a v1: commit direto no `main`, sem PR.
2. Pre-commit (`.githooks/pre-commit`): `dotnet test` sempre; meta-check quando `Assets/` muda; gate de paletas quando arte ou paleta muda; gate do Unity quando há script de `Assets/` em stage (exige `unity-validar` OK posterior à edição).
3. Mensagem `tipo(escopo): descrição` — `feat`, `fix`, `docs`, `refactor`, `chore`, `test`.
4. Versão: `scripts/update_version.ps1` atualiza `VERSION` e `bundleVersion` juntos; tags semver.
5. Depois da v1: `develop`, `feature/*`, merge via PR com CI verde.

- **Ativar por clone:** `git config core.hooksPath .githooks`

## I9 — Integração contínua

**Quem:** GitHub Actions

1. `ci.yml` a cada push: restore, build e testes .NET; meta-check; gate de paletas.
2. `unity-ci.yml` (GameCI): compilação e EditMode — em espera até os secrets de licença existirem.
3. Pega o que escapou do pre-commit (`--no-verify`, clone sem o hook).

- **Pendente:** Secrets do GameCI (ver `Tech/unity-ci.md`)

---

[← Manual de processos](index.md)
