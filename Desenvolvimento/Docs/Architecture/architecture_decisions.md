# Architecture Decision Records (ADRs) – Braziliation

This file records **significant architecture and structure decisions** so future work and AI agents stay consistent.

Format per entry:
- **Title:** Short name
- **Date:** YYYY-MM-DD
- **Status:** Proposed | Accepted | Deprecated
- **Context:** What problem or option we faced
- **Decision:** What we chose
- **Consequences:** Trade-offs, follow-ups

---

## ADR-001: Unity 6 + URP 2D + 320×180 @ 16 PPU

- **Date:** (nunca registrada)
- **Status:** **Superseded por ADR-004** (2026-07-12). Unity 6 + URP 2D continuam valendo;
  a resolução e o PPU passaram a 640×360 @ 32 PPU.
- **Context:** Need stable resolution and pixel-perfect rendering for SNES-style pixel art.
- **Decision:** Use Unity 6, URP 2D, reference resolution 320×180, 16 pixels per unit. CameraScaler and GameInitializer enforce this.
- **Consequences:** All art and tiles must be authored for 16 PPU; scaling handled by pipeline. Documented in `.github/instructions/art-direction.instructions.md`.

---

## ADR-002: Input System (com.unity.inputsystem)

- **Date:** (fill when accepted)
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

*(Add new ADRs below. Keep entries short and link to Docs/Architecture or code when relevant.)*
