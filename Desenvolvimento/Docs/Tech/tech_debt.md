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
- **Where:** `Assets/Scripts/UI/SaveSlotsView.cs` (usa `SaveGameService.Load`) e `SaveSlotEntryView.cs`
- **Why:** ADR-007 criou `LoadDetailed` com status distinguíveis, mas a UI ainda chama o
  `Load` de conveniência. O jogador que abrir um save de build mais nova vê "vazio" e, em
  Novo Jogo, pode gravar por cima dele.
- **Fix:** contrato em [`Sistemas/UI.md`](../Architecture/Sistemas/UI.md) › Estado do slot; implementa o `@UnityDeveloper` (`Docs/TODO.md` › UI e arte).

- **Item:** Não há UI de rebind de controles nem integração Steam Input
- **Where:** `Assets/Scripts/Core/GameInput.cs`, `Assets/InputSystem_Actions.inputactions`
- **Why:** ADR-006 destravou a possibilidade ao centralizar o input no action map, mas
  parou aí. Steam Deck Verified exige suporte a controle e glifos corretos.
- **Fix:** → [ADR-017](../Architecture/ADR/ADR-017.md) (Steam Input em emulação de gamepad, rebind no jogo, glifos próprios) e
  três pendências em `Docs/TODO.md` › UI e arte: campos no `GameSettings` (`@SystemsDeveloper`), `GameInput` +
  `RebindView` (`@UnityDeveloper`) e sprites de glifo (`@SpriteArtist`).

### Média

- **Item:** `montagem_base.py` pinta contorno uniforme e sombreia por faixa horizontal
- **Where:** `Design/ArteFonte/Ferramentas/montagem_base.py` (`outline()`, `shade()`) — usado pelo Autômato e pelo Soldado Clérico
- **Why:** A style-bible pede "outline não uniforme" (escuro na sombra, sutil na luz), e o `outline()` pinta `"1"` em toda a borda; o `shade()` decide a banda só pela posição do pixel na linha, então topo e base de uma peça não diferem por luz. Achado na análise do PixelFX (ADR-016).
- **Fix:** Personagem novo nasce no `pxfx` (contorno seletivo, 4 tons por normal · luz); os dois personagens abertos serão refeitos do zero lá. O `montagem_base` fica para props e legado — só corrigir se um prop precisar.

- **Item:** Reescala de efeito do `pxfx` amostra ruído por célula LOCAL — trama em blocos
- **Where:** `pxfx/efeitos/*` com `rand(floor(x), floor(y))` em `shade` (ex.: o enrolado do `fire/torch` na escala 2,5)
- **Why:** Na escala 1 cada célula local é um pixel; na 2,5 vira um bloco de 2,5 px, a mesma mistura de densidade que o ADR-011 veta. A paridade não pega porque roda na escala 1.
- **Fix:** → `Docs/TODO.md` › UI e arte, pxfx onda 1 (`@SpriteArtist`, 🔨), que já pede `--escala 2.5` corrigida. Ao reescalar cada efeito (ondas do TODO), amostrar o ruído por pixel de TELA quando `p.k != 1` — mesmo padrão do `flameTongue` no `fire/_lib.py`.

- **Item:** O veredito do bench de modelo base nunca entrou na rota operacional — `comfy_batch.py` só dirige SDXL
- **Where:** `Design/ArteFonte/Ferramentas/comfy_batch.py` (linhas 65-71 e 106) · `Design/ArteFonte/IA/Models/workflow-zimage-thumbnails.json`
- **Why:** O bench de 2026-09-03 decidiu **Z-Image Turbo para a Etapa 2 (concept)** e SDXL +
  `pixel-art-xl` só para a rota de referência pixelada. A decisão está escrita em
  `bench-modelo-base-2026-09.md` e em `comfyui-setup.md`, mas o executor não a implementa: o
  `comfy_batch.py` escolhe entre dois workflows SDXL fixos, escreve em `wf["6"]["inputs"]["text"]`
  e registra `"model": "sd_xl_base_1.0.safetensors"` **fixo** no log. Como o
  `TextEncodeZImageOmni` lê o campo `prompt`, passar `--workflow workflow-zimage-thumbnails.json`
  **não quebra**: ele grava um `text` que ninguém lê, gera com o prompt embutido no JSON e
  mente no `lotes.md`. Falha silenciosa — a pior categoria. Resultado prático: a skill
  `concept-art` roda SDXL em toda Etapa 2, e os 11,7 GB do Z-Image não têm rota de uso.
- **Fix:** → `Docs/TODO.md` › UI e arte (`@SpriteArtist`). No `comfy_batch.py`, detectar o `class_type` do nó de encode (`TextEncodeZImageOmni`
  → campo `prompt`; `CLIPTextEncode` → `text`), ajustar steps/cfg do destilado (8 / 1.0) e ler o
  nome do modelo do próprio workflow em vez da constante. Enquanto não for pago, o aviso no
  passo 5 da skill `concept-art` segura o engano, e o A/B pendente roda com o campo `prompt`
  patcheado à mão. **Some quando o A/B fechar por abandono do Z-Image** — aí o certo é o
  script recusar o workflow em vez de aprender a dirigi-lo.

- **Item:** Ruleset WFC de Blumenau é primeira versão — lâmina d'água serrilhada
- **Where:** `Design/ArteFonte/Ferramentas/rulesets/blumenau-fachada.json`
- **Why:** A adjacência escrita à mão deixa `agua`/`lama` variarem de altura livremente, então
  a superfície da água sobe e desce em degraus em vez de ser plana. O ruleset **derivado**
  (`--learn` a partir de `exemplos/blumenau-fachada-exemplo.json`) já sai com água plana, mas
  produz prédios estreitos demais — porque o exemplo desenhado é estreito.
- **Fix:** → `Docs/TODO.md` › UI e arte (`@SpriteArtist`, desenho aprovado pelo responsável). Redesenhar `exemplos/blumenau-fachada-exemplo.json` com massas de prédio mais largas
  e variadas, e passar a usar o ruleset derivado como padrão. É edição de uma grade de texto de
  12 linhas, não reescrita de regras — decisão de direção de arte, não de código.

- **Item:** `PlayerInventory` é uma lista sem capacidade, categorias nem persistência
- **Where:** `Assets/Scripts/Core/PlayerInventory.cs` (TODO inline)
- **Why:** stub para destravar crafting.
- **Fix:** → `Docs/TODO.md` › Gameplay, inventário completo (`@SystemsDeveloper` + `@GameplayEngineer`, ⏸ números de Crafting). Definir regras no GDD antes de implementar; inventário não entra no save hoje.

- **Item:** Efeito híbrido nomeado `"PrótesisViva"` (espanhol) entre nomes PT-BR
- **Where:** `src/Braziliation.Game.Core/Build/HybridSynergyResolver.cs`
- **Why:** erro de digitação que virou identificador.
- **Fix:** → `Docs/TODO.md` › Gameplay (`@GameplayEngineer`). Renomear para `"ProteseViva"` **junto com** um degrau `ISaveMigration`, se o
  identificador chegar a ser persistido — hoje ainda não é. Fazer antes que seja.

- **Item:** `MainMenuUISetupEditor` calcula a câmera do menu para 320×180 @ 16 PPU
- **Where:** `Assets/Editor/Menu/MainMenuUISetupEditor.cs` (comentário e log do `orthographicSize`, l. 338-355; `referenceResolution` do canvas, l. 133)
- **Why:** anterior ao ADR-004. Revisto em 2026-11-09: o **valor** 5,625 está certo — 540 / (2 × 48) = 5,625, o
  mesmo enquadramento de 20 × 11,25 unidades desde o ADR-001. Desatualizados estão o comentário e o log, e o
  canvas de referência 320×180 com as constantes de layout nessa escala, enquanto o `CraftingPanel` já nasce em 960×540.
- **Fix:** → `Docs/TODO.md` › UI e arte, padrão único de `CanvasScaler` (`@UnityDeveloper`): constantes ×3, referência
  960×540, comentário e log corrigidos; conferir o menu no Editor.

- **Item:** Dois documentos acima do teto de 5 mil tokens
- **Where:** `Design/GuiasDeArte/pipeline-ia-sprites.md` (~5,8k). A ficha de Blumenau já foi dividida em 2026-11-09: a ficha de cidade virou pasta, com um arquivo por seção e um por lugar (`ModelCidade`, decisão do responsável), e as 10 cidades de SC migraram
- **Why:** cresce por acréscimo e é lido inteiro pelo `@SpriteArtist`. Está como exceção explícita no `TokenBudgetTests`.
- **Fix:** → `Docs/TODO.md` › UI e arte (`@SpriteArtist`): dividir o guia de IA por rota e, ao terminar, remover a exceção dele do `TokenBudgetTests` (o teste acusa exceção sobrando).

- **Item:** `BuildProgressionView` lê `ExpansionLevel` pelo `ReceptacleController`, não pelo `BuildState`
- **Where:** `Assets/Scripts/UI/BuildProgressionView.cs` (TODO inline nas linhas 11 e 71)
- **Why:** `BuildState` não expõe o nível de expansão por receptáculo, então a view de UI
  vai buscar o dado no controller de crafting. É UI atravessando uma camada: a view passa a
  depender de `ReceptacleController` estar vinculado na cena, e já degrada com
  `Debug.LogWarning` quando não está.
- **Fix:** → `Docs/TODO.md` › Gameplay (`@GameplayEngineer` + `@UnityDeveloper`). Expor `BuildState.GetReceptacle(ReceptacleType)` no core (com teste, I2) e trocar
  as três leituras; a view volta a depender só do estado que o `PlayerBuildController` emite.

- **Item:** `BuildProgressionView` aplica os três arrays de estágio no mesmo `SpriteRenderer`
- **Where:** `Assets/Scripts/UI/BuildProgressionView.cs` (TODO inline na linha 80)
- **Why:** exoesqueleto, capa e espinha têm arrays de sprite separados, mas são aplicados em
  sequência no único renderer do personagem — na prática o último `AplicarSprite` vence e os
  dois primeiros não aparecem. Funciona como placeholder enquanto o personagem é um sprite só.
- **Fix:** quando a arte entregar o personagem em partes, um `SerializeField` de renderer por
  parte (`_rendererCapa`, `_rendererEspinha`) e um `AplicarSprite` por renderer. Depende da
  decisão dos estágios visuais em «Parâmetros numéricos de Build» (`Docs/TODO.md` › Decisões de design) e
  da arte em partes; aí implementa o `@UnityDeveloper`.

- **Item:** Comporta hídrica de Blumenau só conhece aberta/fechada local, sem o sistema global de 4 estados nem arte de porta
- **Where:** `Assets/Scripts/Gameplay/FloodgateController.cs` · `Docs/GDD/Features/Blumenau-SistemaHidrico.md`
- **Why:** A fila Unity de 2026-11-03 pedia só "integrar a alavanca ao sistema hídrico"; o
  `HydricStateManager` (4 estados Rotina/Alerta/Cheia/Saturação, `@SystemsDeveloper`, Core
  puro) ainda não existe, então a comporta ganhou toggle local (`Open`/`Close`/`Toggle`) com
  um hook `SetLocked` para esse sistema travar em Cheia/Saturação quando existir. Também não
  há sprite de comporta/porta em `Assets/Art/Environments/Blumenau/Props/` — só a alavanca —
  então `FloodgateController` funciona hoje só com o colisor (sem troca de sprite visível).
- **Fix:** → `Docs/TODO.md` › Gameplay, sistema hídrico global (`@SystemsDeveloper` + `@GameplayEngineer`). Modelar `HydricState.cs`/`HydricStateManager.cs` (TODOs já descritos em
  `Blumenau-SistemaHidrico.md`) e chamar `FloodgateController.SetLocked` nas transições de
  estado; pedir o asset de comporta pela skill `novo-asset` e plugar em `_gateRenderer`.

- **Item:** `HealthComponent` dispara `OnHealthChanged` no `Awake`
- **Where:** `Assets/Scripts/Gameplay/HealthComponent.cs`
- **Why:** ouvinte registrado por código em outro `Awake` pode não estar inscrito ainda.
- **Fix:** → `Docs/TODO.md` › Gameplay (`@GameplayEngineer`); decidido pelo @TechLead: emissão inicial no `Start`; quem se inscreve depois lê `CurrentHealth`/`MaxHealth` — `EmitCurrent()` só se surgir caso real.

- **Item:** `DemoGameplay.unity` não tem `EventSystem` — nenhum painel UGUI instanciado nela
  ganha navegação por teclado/controle
- **Where:** `Assets/Scenes/DemoGameplay.unity`
- **Why:** Encontrado ao criar `Assets/Prefabs/UI/CraftingPanel.prefab` (2026-11-04): a cena
  só tem o Canvas da HUD (`HUD_Demo`, sem `GraphicRaycaster` interativo de fato) — sem
  `EventSystem`, `EventSystem.current` é `null` e qualquer `ShowPanel()` que chame
  `SetSelectedGameObject` (convenção de Steam Input deste agente) lança `NullReferenceException`
  assim que um painel interativo for instanciado e aberto nessa cena.
- **Fix:** → `Docs/TODO.md` › UI e arte, na pendência do `CanvasScaler` (`@UnityDeveloper`): pôr o par `EventSystem` +
  `InputSystemUIInputModule` já (o mesmo da `MainMenu.unity`), sem esperar o crafting ser wireado — custa nada e
  tira a `NullReferenceException` do caminho.

- **Item:** `HUD_Demo` (`CanvasHealthHud`) usa `CanvasScaler` com referência 800×600, de antes do ADR-011
- **Where:** `Assets/Scenes/DemoGameplay.unity` → GameObject `HUD_Demo` → `CanvasScaler`
- **Why:** Encontrado na mesma inspeção acima. `Assets/Prefabs/UI/CraftingPanel.prefab` já nasce
  com `CanvasScaler` em Scale With Screen Size, referência 960×540 (ADR-011); o HUD ficou para
  trás.
- **Fix:** → `Docs/TODO.md` › UI e arte, padrão único de `CanvasScaler` (`@UnityDeveloper`). A causa é código, não só
  cena: `DemoSceneBuilderEditor` e `DemoSceneBootstrap` fazem `AddComponent<CanvasScaler>()` sem configurar, e
  800×600 é o padrão do Unity — corrigir só a cena volta no próximo rebuild. Conferir a HUD em jogo depois.

- **Item:** `gen_tileset.py` só gera tile de **miolo** — nenhuma das 7 famílias tem borda (topo de chão, quina, beiral)
- **Where:** `Design/ArteFonte/Ferramentas/gen_tileset.py` · tilesets em `Assets/Art/Environments/Blumenau/Tilesets/` e o teste em `Design/ArteFonte/IA/Testes/tilesets-onda2/`
- **Why:** Todo tipo de tile é uma textura opaca que ladrilha nas 4 direções. Para montar nível
  em vista lateral, o Rule Tile do Unity precisa do tile de **topo** (a superfície onde se pisa,
  com recorte transparente em cima) e de quina; sem eles o chão termina numa linha reta cortada.
  Apareceu no mock do teste da Onda 2 (2026-11-04, `Design/ArteFonte/IA/Testes/tilesets-onda2/env_blumenau_onda2_tilesets_mock.png`): o
  cemitério e a periferia param seco na borda de cima. Afeta as 3 famílias antigas também — o
  blockout atual só tem topo porque usa o tileset Gothicvania (`CastleBlockout.unity`).
- **Fix:** → `Docs/TODO.md` › UI e arte (`@SpriteArtist`). Um modificador de borda genérico em vez de tipo novo por família — dado um tipo de
  chão, gerar `topo` (3-5 linhas de superfície com silhueta irregular e alfa acima), `quina_esq`
  e `quina_dir`, derivados do próprio miolo para casar de cor. Entra como linha extra no sheet e
  no manifest; o `gen_map_wfc.py` ganha a adjacência "topo só encosta em ar por cima".

### Baixa

- **Item:** Rampas de material anteriores à paleta de 32 continuam repetindo degrau ou emprestando cor de outro material
- **Where:** `Design/ArteFonte/Ferramentas/montagem_base.py` (`LIGAS` bronze `6·7·8·8` e prata `3·4·5·5`, `BASE_RAMPS` cobre `1·9·C·C`) · `ContextPacks/enm-soldado-clerico/montagem.py` (`esmalte` `2·4·5·D`, `clero` `1·G·9·C`, `loden` `1·2·E·E`, `meia` `2·C·D·D`) · mapas fixos de textura do `spec_redetail.py` e do `gen_tileset.py` (`claro`/`escuro`), que só conhecem as keys `1`-`G`
- **Why:** A paleta de Blumenau ganhou 16 cores de rampa em 2026-11-05 (keys `H`-`Y`, rampas por nome no bloco `"rampas"` do `blumenau.json`). Por decisão do usuário, as rampas antigas **não** foram trocadas: o Autômato e o Soldado Clérico estão aprovados, e regerar com rampa nova mudaria os PNGs entregues.
- **Fix:** Trocar pela rampa nomeada do `palette-guide.md` (invertida, porque o `montagem_base` pede escuro → claro) **só quando o asset for re-autorado** — e os dois personagens já vão ser refeitos no `pxfx` (item do `montagem_base` acima). Os mapas `claro`/`escuro` ganham as keys novas quando um tile ou spec de prop usar cor de rampa. Atenção também ao `pixelize.py`: ele quantiza para as 32 cores, então um concept sem gente pode cair em tom de pele — conferir no gate e, se acontecer, dar a ele um filtro por rampa.

- **Item:** `TilesetAutoSlicer` fatia o tileset placeholder do castelo em todas as 780 células (grid 52×15), não só as não-vazias
- **Where:** `Assets/Editor/Art/TilesetAutoSlicer.cs` · `Assets/Art/ThirdParty/Gothicvania/Environments/env_placeholder_castelo_tileset.png`
- **Why:** Ler a transparência por célula durante o import (`OnPreprocessTexture`) exigiria decodificar o PNG à mão nesse ponto do pipeline (a textura ainda não existe como objeto legível) — optei pela fatia completa, igual ao "Grid By Cell Size" padrão do Unity, para não arriscar um import quebrado sem retorno visual síncrono. A maioria das ~500 células vazias nunca vira sprite usado; só 3 viraram Tile asset para o blockout.
- **Fix:** Se algum dia vier um segundo tileset de terceiros maior, considerar filtrar por alfa no pós-import (`OnPostprocessTexture`, textura já legível) para não gerar sprites inúteis.

---

*QA Engineer and Tech Lead can add items when reviewing code or after refactors. Remove or mark “Done” when addressed.*
