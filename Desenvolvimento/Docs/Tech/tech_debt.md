# Tech Debt – Braziliation

Known technical debt, shortcuts, and follow-up work. Use this so agents and the developer don’t forget and so refactors are prioritized.

Format:
- **Item:** Short description
- **Where:** Path or system
- **Why:** Reason it exists or why it’s debt
- **Fix (optional):** Suggested direction

---

## Current items

> Consolidado em 2026-09-02 a partir da auditoria de estrutura. Antes desta data este
> arquivo dizia "None yet" enquanto ~30 itens de dívida viviam no `Docs/TODO.md` e 29
> `TODO` inline no código — o processo existia e não era usado. `TODO.md` é pendência de
> **trabalho planejado**; este arquivo é **atalho que foi tomado** e precisa ser pago.

### Alta

- **Item:** UI de slots trata `Corrupt` e `FromNewerBuild` como "slot vazio"
- **Where:** `Assets/Scripts/UI/SaveSlotsView.cs` (usa `SaveGameService.Load`)
- **Why:** ADR-007 criou `LoadDetailed` com status distinguíveis, mas a UI ainda chama o
  `Load` de conveniência. O jogador que abrir um save de build mais nova vê "vazio".
- **Fix:** trocar por `LoadDetailed` e renderizar estado por `SaveLoadStatus`.

- **Item:** Não há UI de rebind de controles nem integração Steam Input
- **Where:** `Assets/Scripts/Core/GameInput.cs`, `Assets/InputSystem_Actions.inputactions`
- **Why:** ADR-006 destravou a possibilidade ao centralizar o input no action map, mas
  parou aí. Steam Deck Verified exige suporte a controle e glifos corretos.
- **Fix:** tela de rebind sobre `InputActionRebindingExtensions`; avaliar Steam Input API.

- **Item:** Testes EditMode escritos mas nunca executados
- **Where:** `Assets/Tests/EditMode/ProjectSetupTests.cs`, skill `unity-validar --testes`
- **Why:** O assembly compila (batchmode 2026-09-13), mas rodar testes exige licença Unity
  ativada na máquina: a licença Personal só via Hub dá 198 `No valid Unity Editor license
  found` para o Editor aberto por linha de comando — com `-batchmode`, sem ele e pela CLI
  oficial (`unity license status`: "nenhuma ativa"). Até lá, as mesmas verificações rodam
  pelo lado de fora em `UnityAssetConsistencyTests` (xUnit, no CI).
- **Fix:** Unity Hub → Preferences → Licenses → Add → licença Personal; depois
  `py .claude/skills/unity-validar/scripts/validar.py --testes`.

### Média

- **Item:** Ruleset WFC de Blumenau é primeira versão — lâmina d'água serrilhada
- **Where:** `Design/ArteFonte/Ferramentas/rulesets/blumenau-fachada.json`
- **Why:** A adjacência escrita à mão deixa `agua`/`lama` variarem de altura livremente, então
  a superfície da água sobe e desce em degraus em vez de ser plana. O ruleset **derivado**
  (`--learn` a partir de `exemplos/blumenau-fachada-exemplo.json`) já sai com água plana, mas
  produz prédios estreitos demais — porque o exemplo desenhado é estreito.
- **Fix:** Redesenhar `exemplos/blumenau-fachada-exemplo.json` com massas de prédio mais largas
  e variadas, e passar a usar o ruleset derivado como padrão. É edição de uma grade de texto de
  12 linhas, não reescrita de regras — decisão de direção de arte, não de código.

- **Item:** `WfcMapImporter` compila, mas nunca foi executado
- **Where:** `Assets/Editor/Art/WfcMapImporter.cs`
- **Why:** Compilou no primeiro batchmode (2026-09-13, skill `unity-validar`). A premissa
  anterior — "a licença Personal não permite `-batchmode`" — estava errada: a Personal só não
  pode ser *ativada* pela linha de comando; ativada pelo Hub, batchmode funciona. Executar o
  importador ainda exige o menu do Editor.
- **Fix:** Abrir o Editor, rodar `Assets > Braziliation > Importar Mapa WFC...` apontando para
  `Design/ArteFonte/IA/Outputs/wfc-teste/blumenau_s42.unity.json` e conferir o Tilemap.

- **Item:** `PlayerInventory` é uma lista sem capacidade, categorias nem persistência
- **Where:** `Assets/Scripts/Core/PlayerInventory.cs` (TODO inline)
- **Why:** stub para destravar crafting.
- **Fix:** definir regras no GDD antes de implementar; inventário não entra no save hoje.

- **Item:** Ferramentas de editor de sprite compilam, mas nunca foram exercitadas
- **Where:** `Assets/Editor/Art/SheetAutoSlicer.cs`, `SheetAnimationTool.cs`
- **Why:** compilaram no batchmode de 2026-09-13; o slicing e a geração de `.anim` ainda não
  foram conferidos num sheet real.
- **Fix:** abrir o Unity, reimportar um `*_sheet.png` e confirmar slicing + `.anim`.

- **Item:** Efeito híbrido nomeado `"PrótesisViva"` (espanhol) entre nomes PT-BR
- **Where:** `src/Braziliation.Game.Core/Build/HybridSynergyResolver.cs`
- **Why:** erro de digitação que virou identificador.
- **Fix:** renomear para `"ProteseViva"` **junto com** um degrau `ISaveMigration`, se o
  identificador chegar a ser persistido — hoje ainda não é. Fazer antes que seja.

- **Item:** `HealthComponent` dispara `OnHealthChanged` no `Awake`
- **Where:** `Assets/Scripts/Gameplay/HealthComponent.cs`
- **Why:** ouvinte registrado por código em outro `Awake` pode não estar inscrito ainda.
- **Fix:** mover a emissão inicial para `Start`, ou expor `EmitCurrent()` para a HUD puxar.

### Baixa

- **Item:** 11 agentes duplicados em 2 formatos (22 arquivos que diferem em ~1 linha)
- **Where:** `.claude/agents/` × `.github/agents/`
- **Why:** Copilot e Claude Code usam formatos diferentes; a sincronia depende de
  disciplina via skill `novo-agente`.
- **Fix:** gerar o formato Copilot a partir do Claude + teste de CI que falha na divergência.

---

*QA Engineer and Tech Lead can add items when reviewing code or after refactors. Remove or mark “Done” when addressed.*
