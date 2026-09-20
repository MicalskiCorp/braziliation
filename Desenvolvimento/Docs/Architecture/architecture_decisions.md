# Architecture Decision Records (ADRs) – Braziliation

Registro das **decisões significativas de arquitetura e estrutura**, para que trabalho futuro e agentes de IA sigam consistentes. Nova entrada: skill `novo-adr`.

Formato de cada entrada (os rótulos ficam em inglês — o `DocsConsistencyTests` e a skill leem `**Status:**`):
- **Date:** AAAA-MM-DD
- **Status:** Proposed | Accepted | Superseded por ADR-NNN
- **Context:** o problema ou a opção que se apresentou
- **Decision:** o que foi escolhido
- **Consequences:** trade-offs e desdobramentos

---

## ADR-001: Unity 6 + URP 2D + 320×180 @ 16 PPU

- **Date:** não registrada — anterior a 2026-04 (início do projeto)
- **Status:** **Superseded por ADR-004** (2026-07-12). Unity 6 + URP 2D continuam valendo;
  a resolução e o PPU passaram a 640×360 @ 32 PPU.
- **Context:** Need stable resolution and pixel-perfect rendering for SNES-style pixel art.
- **Decision:** Use Unity 6, URP 2D, reference resolution 320×180, 16 pixels per unit. CameraScaler and GameInitializer enforce this.
- **Consequences:** All art and tiles must be authored for 16 PPU; scaling handled by pipeline. Documented in `.github/instructions/art-direction.instructions.md`.

---

## ADR-002: Input System (com.unity.inputsystem)

- **Date:** não registrada — anterior a 2026-09-02 (o ADR-006 parte dela)
- **Status:** Accepted
- **Context:** Modern input with actions and rebinding; replace legacy Input Manager.
- **Decision:** Use com.unity.inputsystem; single Input Actions asset (e.g. InputSystem_Actions.inputactions) for player and UI.
- **Consequences:** All player and UI input goes through action maps; no direct Input.GetKey in gameplay code.

---

## ADR-003: Recommended Assets/Scripts layout

- **Date:** (nunca aceito)
- **Status:** **Superseded por ADR-005** (2026-09-02). Ficou `Proposed` enquanto o código
  crescia num layout diferente; o limbo entre ADR e realidade era pior que qualquer das
  duas opções.
- **Context:** Scalable structure for Core, Player, Enemies, Combat, Inventory, World, UI, Utils.
- **Decision:** Document and adopt folder layout under Assets/Scripts/ as in Docs/Architecture/Assets/AssetsStructure.md. Namespaces match folders.
- **Consequences:** New scripts go in the correct subfolder; existing Core, Tools, UI can be merged into this layout over time.

---

## ADR-004: Upgrade de resolução para 640×360 (Blasphemous-like)

- **Date:** 2026-07-12
- **Status:** Accepted
- **Context:** A direção de arte original (320×180, 16 PPU, tile 16, SNES-era) limitava a densidade de pixels. Decisão do usuário: elevar a fidelidade ao patamar de Blasphemous (640×360 nativo, ~2× densidade, mesma proporção de personagem em tela ~17%).
- **Decision:** Resolução de referência **640×360** (escala inteira ×3 → 1080p), **32 PPU**, tile base **32×32**, player ~64px de altura, limite de cores por sprite elevado a **~32**. Assets legados convertidos por upscale ×2 nearest (preservam leitura e tamanho em tela; densidade nova entra por re-autoria asset a asset). Contagens de animação elevadas (run 8-12, attack 6-10).
- **Consequences:** `CameraScaler` e `SpriteImportPostprocessor` reparametrizados (32 PPU / 640×360); ferramentas do pipeline com `--scale`; guias de arte atualizados; **o alvo "SNES (EverDrive)" citado em regras antigas fica formalmente descartado** — plataforma alvo é PC; rota C (difusão + pixel pass) passa a ser a principal para personagens/inimigos, rota A fica para props/ícones/tiles; assets legados marcados para re-autoria em densidade nova (rastreados no TODO.md).

---

## ADR-005: Layout de `Assets/Scripts/` por domínio (substitui ADR-003)

- **Date:** 2026-09-02
- **Status:** Accepted
- **Context:** O ADR-003 propunha `Core/Player/Enemies/Combat/Inventory/World/UI/Utils` e
  nunca foi aceito. O código cresceu em outro eixo — por **domínio de sistema**, não por
  tipo de entidade. Resultado: cinco pastas vazias com `.gitkeep` no repositório e uma
  tabela de namespaces em `coding-standards.instructions.md` que não descrevia nada real.
- **Decision:** Adotar o layout **que existe**:

  | Pasta | Namespace | Papel |
  |-------|-----------|-------|
  | `Core/` | `Braziliation.Core` | Infra transversal: service locator, layers, input, interfaces |
  | `Gameplay/` | `Braziliation.Gameplay` | MonoBehaviours de jogo: player, inimigo, vida, câmera |
  | `Build/` | `Braziliation.Build` | Adaptadores Unity da build do personagem |
  | `Crafting/` | `Braziliation.Crafting` | Adaptadores Unity de crafting |
  | `Enemies/` | `Braziliation.Enemies` | ScriptableObjects de perfil de inimigo |
  | `UI/` | `Braziliation.UI` | Views e controllers de UI |

  Pastas do ADR-003 sem conteúdo (`Player/`, `Combat/`, `World/`, `Utils/`) são removidas.
  `Braziliation.Build` e `Braziliation.Crafting` existem também em
  `src/Braziliation.Game.Core/` — é intencional: mesmo domínio, camadas diferentes
  (adaptador Unity × lógica pura). Nomes de tipo não podem colidir entre as duas.
- **Consequences:** Script novo vai para a pasta do **domínio**, não do tipo de entidade.
  A tabela de namespaces em `.github/instructions/coding-standards.instructions.md` e em
  `.claude/rules/csharp.md` passa a refletir esta tabela.

---

## ADR-006: Todo input passa por `GameInput` sobre o action map

- **Date:** 2026-09-02
- **Status:** Accepted
- **Context:** O ADR-002 adotou o Input System, e o asset
  `Assets/InputSystem_Actions.inputactions` chegou a ser registrado como project-wide
  actions — mas nenhum script o consumia. `PlayerController` e `PlayerCombat` liam
  `Keyboard.current`, `Mouse.current` e `Gamepad.current` direto. Para o alvo Steam isso
  bloqueia rebind pelo jogador, Steam Input, glifos de controle e Steam Deck, e cada
  mecânica nova nascia acoplada ao dispositivo.
- **Decision:** `Braziliation.Core.GameInput` é a **única** porta de leitura de input.
  Expõe as ações do map `Player` do asset project-wide, com cache resolvido uma vez e
  limpo em `SubsystemRegistration`. Ação nova = binding no asset primeiro, propriedade em
  `GameInput` depois. Polling de dispositivo em script de gameplay é proibido.
- **Consequences:** Trocar tecla é editar dado, não código. Bindings de paridade com o
  input antigo (W/↑ para pular, F para atacar) foram adicionados ao asset. Falta ainda a
  UI de rebind e a integração Steam Input propriamente dita — ambas agora são possíveis.

---

## ADR-007: Save versionado com migração explícita

- **Date:** 2026-09-02
- **Status:** Accepted
- **Context:** `SaveGameService.Load` devolvia `null` para slot inexistente, JSON
  corrompido **e** versão de schema diferente — indistinguíveis. Num jogo distribuído por
  Steam, que recebe patch, isso significa o slot do jogador aparecer vazio depois de uma
  atualização, sem aviso e sem recuperação.
- **Decision:** `LoadDetailed` devolve `SaveLoadResult` com `SaveLoadStatus`
  (`Ok`, `Empty`, `Corrupt`, `Migrated`, `FromNewerBuild`, `NoMigrationPath`).
  Migrações são degraus `ISaveMigration` sobre o JSON bruto (`JsonObject`), registrados em
  `SaveMigrations.All` e aplicados em cadeia. Save de build **mais nova** nunca é migrado
  nem sobrescrito. `Load` continua existindo como conveniência e devolve o slot ou null.
- **Consequences:** Subir `SaveSlot.CurrentSchemaVersion` sem registrar o degrau **quebra o
  build** (teste `Every_Version_Below_Current_Must_Have_A_Migration_Registered`). A UI de
  slots ainda trata tudo que não é utilizável como "vazio" — deve passar a distinguir
  `FromNewerBuild` e `Corrupt` para o jogador.

---

## ADR-008: Claude Code é o único harness de agentes

- **Date:** 2026-09-13
- **Status:** Accepted
- **Context:** O projeto nasceu no VS Code Copilot e ganhou o Claude Code depois; os 11 agentes
  existiam nos dois formatos. O Copilot deixou de ser usado, mas o espelho continuava custando
  um teste de paridade, um script e um hook de sincronização, instruções duplicadas e ~20
  documentos explicando "os dois formatos". Conteúdo que o Claude usava (visão do jogo,
  direção de arte) morava na pasta de configuração do Copilot. Havia ainda regras do Cursor
  esquecidas em `Desenvolvimento/.cursor/`.
- **Decision:** Claude Code é o único harness. Saem `.github/agents/`, `.github/prompts/`,
  `.github/instructions/` e `Desenvolvimento/.cursor/`. A visão do jogo vai para
  `Desenvolvimento/Docs/GDD/visao.md`; a direção de arte e áudio, para
  `Design/GuiasDeArte/direcao-de-arte.md`. A `.github/` fica só com o que a plataforma
  GitHub usa: `workflows/`, `ISSUE_TEMPLATE/`, `PULL_REQUEST_TEMPLATE.md`.
- **Consequences:** O Copilot deixa de funcionar com o projeto (os arquivos seguem no
  histórico do git). `AgentParityTests`, `sync_bodies.py` e o hook `sync_agent_bodies.py`
  saem; o `AgentDefinitionTests` cobra nome = arquivo, `model:`, registro no `AGENTS.md` e
  que a `.github/` não volte a ter agentes. ADRs anteriores que citam `.github/instructions/`
  ficam como registro histórico.

---

## ADR-009: Captura de entrevistas de pesquisa via WhatsApp (Baileys + Whisper local)

- **Date:** 2026-09-14
- **Status:** Accepted
- **Context:** A pesquisa do `@Historiador` dependia só de fontes web e do que o usuário
  digitava na conversa. Parte do material relevante — relatos de historiadores locais,
  memória oral de quem viveu ou ouviu as lendas — só existe em conversa falada, gravada de
  forma esporádica conforme a oportunidade de entrevistar alguém aparece. Restrição do
  usuário: usar só a licença já paga (Claude Code), nada de chamada à API da Anthropic fora
  dela, e nenhuma API paga de terceiro além da integração direta com o WhatsApp — e nem a
  API nem o Claude Code processam áudio como entrada.
- **Decision:** Uma conversa dedicada do WhatsApp é o canal de captura. Um listener local
  (Node.js + Baileys, protocolo multi-device não-oficial, rodando na máquina pessoal do
  usuário — `Design/Pesquisa/Entrevistas/Ferramentas/whatsapp-listener/`) grava cada
  mensagem nova (áudio ou texto) em `Design/Pesquisa/Entrevistas/_inbox/`. Um transcritor
  local (Python + faster-whisper, sem API, `Ferramentas/transcrever.py`) converte os áudios
  para texto e move o lote para `_pendente-curadoria/`. A curadoria roda dentro do Claude
  Code (skill `processar-entrevistas`, agente `@Historiador`), aplicando o critério de
  memória oral já registrado em `memories/repo/historian-guardrails.md`. O WhatsApp
  Business Cloud API oficial foi descartado por exigir número dedicado, verificação de
  negócio da Meta e webhook público — infraestrutura desproporcional a uma pessoa
  entrevistando esporadicamente.
- **Consequences:** Baileys é não-oficial — usar a conta pessoal para automação viola os
  Termos de Serviço do WhatsApp; o risco é considerado baixo em uso pessoal, volume baixo e
  número próprio, mas não é zero, sem garantia de recuperação se a conta for banida. A
  sessão pareada (`auth/`) e todo o conteúdo bruto de `_inbox/`, `_pendente-curadoria/` e
  `_processado/` ficam fora do git (dado pessoal/de terceiros) — só o material já curado e
  aprovado entra em `Design/Pesquisa/`. Entrevistar terceiros exige confirmar consentimento
  antes de aprovar qualquer relato. O listener precisa estar rodando (PC de casa) para
  capturar em tempo real; mensagens enviadas enquanto ele está offline chegam na
  reconexão, pela fila do próprio WhatsApp — sem precisar de acesso remoto à máquina.
- **Atualização (2026-09-20) — imagem e documento:** a captura passou a cobrir também foto e
  documento (PDF, DOCX, TXT/CSV) enviados na conversa, com a legenda quando houver. O
  `transcrever.py` extrai o texto de documento com camada de texto (pdfplumber / python-docx,
  local, sem API); imagem e PDF escaneado seguem inteiros para a curadoria, que lê o arquivo
  direto no Claude Code — **não há OCR no pipeline**, e adicionar um exigiria dependência nova
  (Tesseract). O arquivo bruto continua fora do git; imagem ou documento **aprovado** na
  curadoria é copiado para `Design/Pesquisa/Fontes/Arquivos/`, que é versionado — com limite de
  ~5 MB por arquivo, já que o repo não tem regra LFS para `.jpg`/`.pdf`. Na mesma passagem, o
  listener passou a guardar em `estado.json` (fora do git) até onde já leu: a promessa de que
  "mensagem enviada com o listener offline chega na reconexão" valia só para reconexão de
  socket — reinício de processo descartava a fila em silêncio. A decisão original segue
  valendo; só o escopo do que é capturado mudou.

---

## ADR-010: CI do Unity desligado — a validação do lado Unity é local e obrigatória

- **Date:** 2026-09-20
- **Status:** Accepted
- **Context:** O workflow `unity-ci.yml` existia desde o início "em espera pelos secrets de
  licença", e a pendência ficou aberta por meses. Ao tentar fechá-la em 20 set 2026,
  descobrimos que **não há caminho**: a Unity encerrou a ativação manual de licenças
  Personal. O fluxo `.alf → .ulf` — única porta do tier gratuito no GameCI — responde
  agora *"You are not eligible to activate your license offline. Offline activation is
  available only for Enterprise and Industry seats"*. O Unity 6 passou a licenciar
  Personal por **entitlement de conta** (`UnityEntitlementLicense.xml`), formato que o
  `game-ci/unity-test-runner@v4` não consome. O issue #408 do GameCI documenta o impasse
  e segue aberto. As alternativas foram avaliadas e recusadas: runner self-hosted exige
  a máquina pessoal ligada e expõe superfície de ataque via PR de fork; a estratégia
  experimental do CLI novo do GameCI (`--include-personal`) exige a senha da conta Unity
  como secret e **consome o seat Personal até devolvê-lo** — o que pode derrubar a
  licença do Editor local no meio do trabalho.
- **Decision:** O CI do Unity fica **desligado por decisão**, não por pendência. O job é
  gateado por `vars.UNITY_CI_ENABLED` e aparece como `skipped` — nunca como verde. A
  validação do lado Unity é **local e obrigatória**: a skill `unity-validar` compila em
  batchmode e roda os testes EditMode, e o `pre-commit` recusa qualquer script de
  `Assets/` em stage sem uma validação OK posterior à última edição. O workflow e a
  documentação de habilitação ficam no repositório: se a Unity voltar a oferecer ativação
  de Personal em CI, ligar é criar os secrets e a variável.
- **Consequences:** A cobertura do lado Unity depende de o pre-commit estar ativo no clone
  (`git config core.hooksPath .githooks`) — quem commitar com `--no-verify` escapa, e o CI
  não pega. Em troca, nenhuma senha da conta Unity vira secret e o seat Personal continua
  inteiro para o Editor local. Os testes EditMode passaram a rodar de fato em 20 set 2026
  (9/9), depois que a licença foi ativada na máquina por `unity auth login` +
  `unity license activate --personal --accept-eula` — o CLI ativa Personal, ao contrário
  do que este projeto registrava. Revisitar se o GameCI publicar suporte estável a
  entitlement, ou se o projeto passar a ter licença Plus/Pro (aí `UNITY_SERIAL` resolve).

---

*(Novos ADRs entram acima desta linha. Entradas curtas, com link para `Docs/Architecture/` ou para o código quando ajudar.)*
