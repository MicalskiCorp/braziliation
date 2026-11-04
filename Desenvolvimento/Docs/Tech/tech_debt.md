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

- **Item:** Dois artefatos antigos do autômato continuam publicados e duplicam a página do personagem
- **Where:** claude.ai/artifact/SG8dXeBixrnPTm6GrGWiLP ("Autômato Abandonado", página de revisão de 26 set) e claude.ai/artifact/N9vDgyhyb5QNJBLjHqMxXu ("Idle do Autômato")
- **Why:** Nasceram antes do passo de página por personagem. Hoje o conteúdo deles vive na página canônica (9TF8ejHqNuMmzcJe43EurS), e a lista da galeria mostra dois itens com o mesmo nome "Autômato Abandonado" — exatamente a desorganização que o hub veio resolver.
- **Fix:** Apagar os dois, com confirmação do usuário (apagar artefato é irreversível e quebra o link para quem o tiver). Só o usuário decide.



- **Item:** `Ferramentas/index.md` vive raspando o teto de 1500 tokens do roteador
- **Where:** `Design/ArteFonte/Ferramentas/index.md`
- **Why:** São 19 ferramentas numa tabela só, com descrição de uma ou duas linhas cada. Em 2026-10-07 estourou ao ganhar duas linhas e foi preciso enxugar seis descrições para caber. A próxima ferramenta estoura de novo.
- **Fix:** Separar como já se fez em `Design/Pesquisa/Fontes/`: o `index.md` vira roteador com nome e meia linha por ferramenta, e um `catalogo.md` ao lado guarda uso, parâmetros e o porquê de cada uma.



- **Item:** Só os placeholders CC0 seguem no grid antigo depois do ADR-011
- **Where:** `Assets/Art/ThirdParty/Gothicvania/**` · lista viva em `Assets/Editor/Art/Escala/PixelScale.cs`
- **Why:** Toda a arte própria está no grid de 48 desde 2026-10-05, quando o autômato foi redesenhado. Restam os 9 placeholders do Gothicvania, importados a 32 PPU — mantêm o tamanho em mundo e só parecem menos densos ao lado do resto.
- **Fix:** Saem junto com `Art/ThirdParty/` e o `CREDITS.md` quando a arte própria os substituir, conforme o item já rastreado no TODO. Aí `PixelScale` vira uma constante só.

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

### Média

- **Item:** `architecture_decisions.md` passou do teto de tokens — registrado como exceção em `TokenBudgetTests.DocumentExceptions`
- **Where:** `Desenvolvimento/Docs/Architecture/architecture_decisions.md` (~5595 de 5000 tokens do `TokenBudgetTests`)
- **Why:** O ADR-012 (Central, 2026-11-03) já precisou ser enxugado para caber; o ADR-013 (declaração de IA na Steam, 2026-11-03) estourou de fato. Um arquivo único com todos os ADRs só cresce.
- **Fix:** Um arquivo por ADR em `Architecture/ADR/` com um `index.md` roteador (e a skill `novo-adr` apontando para lá), ou mover os ADRs substituídos (001, 003, 004) para um arquivo de histórico. Até lá, a exceção no teste segue valendo.

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
- **Fix:** no `comfy_batch.py`, detectar o `class_type` do nó de encode (`TextEncodeZImageOmni`
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
- **Fix:** Redesenhar `exemplos/blumenau-fachada-exemplo.json` com massas de prédio mais largas
  e variadas, e passar a usar o ruleset derivado como padrão. É edição de uma grade de texto de
  12 linhas, não reescrita de regras — decisão de direção de arte, não de código.

- **Item:** `PlayerInventory` é uma lista sem capacidade, categorias nem persistência
- **Where:** `Assets/Scripts/Core/PlayerInventory.cs` (TODO inline)
- **Why:** stub para destravar crafting.
- **Fix:** definir regras no GDD antes de implementar; inventário não entra no save hoje.

- **Item:** Efeito híbrido nomeado `"PrótesisViva"` (espanhol) entre nomes PT-BR
- **Where:** `src/Braziliation.Game.Core/Build/HybridSynergyResolver.cs`
- **Why:** erro de digitação que virou identificador.
- **Fix:** renomear para `"ProteseViva"` **junto com** um degrau `ISaveMigration`, se o
  identificador chegar a ser persistido — hoje ainda não é. Fazer antes que seja.

- **Item:** `MainMenuUISetupEditor` calcula a câmera do menu para 320×180 @ 16 PPU
- **Where:** `Assets/Editor/Menu/MainMenuUISetupEditor.cs` (comentário e cálculo de `orthographicSize`)
- **Why:** anterior ao ADR-004 (640×360 @ 32 PPU). Encontrado ao indexar os scripts em 2026-09-13.
- **Fix:** recalcular com 640×360 / 32 PPU (mesmo `orthographicSize` 5,625 se o fundo for re-autorado em 32 PPU) e conferir o menu no Editor.

- **Item:** Dois documentos acima do teto de 5 mil tokens
- **Where:** `Design/Criativo/Estados/SantaCatarina/cidades/Blumenau/index.md` (~5,8k) · `Design/GuiasDeArte/pipeline-ia-sprites.md` (~5,8k)
- **Why:** crescem por acréscimo; são lidos inteiros pelo `@GameCreative` e pelo `@SpriteArtist`. Estão como exceção explícita no `TokenBudgetTests`.
- **Fix:** dividir a ficha de Blumenau por seção (características, monstros, lugares, missões) com o `index.md` virando roteador — muda o template `ModelCidade`, então é decisão do usuário; dividir o guia de IA por rota. Ao dividir, remover a exceção (o teste acusa exceção sobrando).

- **Item:** `BuildProgressionView` lê `ExpansionLevel` pelo `ReceptacleController`, não pelo `BuildState`
- **Where:** `Assets/Scripts/UI/BuildProgressionView.cs` (TODO inline nas linhas 11 e 71)
- **Why:** `BuildState` não expõe o nível de expansão por receptáculo, então a view de UI
  vai buscar o dado no controller de crafting. É UI atravessando uma camada: a view passa a
  depender de `ReceptacleController` estar vinculado na cena, e já degrada com
  `Debug.LogWarning` quando não está.
- **Fix:** expor `BuildState.GetReceptacle(ReceptacleType)` no core (com teste, I2) e trocar
  as três leituras; a view volta a depender só do estado que o `PlayerBuildController` emite.

- **Item:** `BuildProgressionView` aplica os três arrays de estágio no mesmo `SpriteRenderer`
- **Where:** `Assets/Scripts/UI/BuildProgressionView.cs` (TODO inline na linha 80)
- **Why:** exoesqueleto, capa e espinha têm arrays de sprite separados, mas são aplicados em
  sequência no único renderer do personagem — na prática o último `AplicarSprite` vence e os
  dois primeiros não aparecem. Funciona como placeholder enquanto o personagem é um sprite só.
- **Fix:** quando a arte entregar o personagem em partes, um `SerializeField` de renderer por
  parte (`_rendererCapa`, `_rendererEspinha`) e um `AplicarSprite` por renderer. Depende da
  pendência "Progressão visual da build" no `TODO.md`.

- **Item:** Comporta hídrica de Blumenau só conhece aberta/fechada local, sem o sistema global de 4 estados nem arte de porta
- **Where:** `Assets/Scripts/Gameplay/FloodgateController.cs` · `Docs/GDD/Features/Blumenau-SistemaHidrico.md`
- **Why:** A fila Unity de 2026-11-03 pedia só "integrar a alavanca ao sistema hídrico"; o
  `HydricStateManager` (4 estados Rotina/Alerta/Cheia/Saturação, `@SystemsDeveloper`, Core
  puro) ainda não existe, então a comporta ganhou toggle local (`Open`/`Close`/`Toggle`) com
  um hook `SetLocked` para esse sistema travar em Cheia/Saturação quando existir. Também não
  há sprite de comporta/porta em `Assets/Art/Environments/Blumenau/Props/` — só a alavanca —
  então `FloodgateController` funciona hoje só com o colisor (sem troca de sprite visível).
- **Fix:** Modelar `HydricState.cs`/`HydricStateManager.cs` (TODOs já descritos em
  `Blumenau-SistemaHidrico.md`) e chamar `FloodgateController.SetLocked` nas transições de
  estado; pedir o asset de comporta pela skill `novo-asset` e plugar em `_gateRenderer`.

- **Item:** `HealthComponent` dispara `OnHealthChanged` no `Awake`
- **Where:** `Assets/Scripts/Gameplay/HealthComponent.cs`
- **Why:** ouvinte registrado por código em outro `Awake` pode não estar inscrito ainda.
- **Fix:** mover a emissão inicial para `Start`, ou expor `EmitCurrent()` para a HUD puxar.

- **Item:** Editar um `.unity` em disco (fora do Editor) enquanto o Editor tem essa cena
  aberta trava o servidor de comandos (`unity command ...`) sem erro visível
- **Where:** processo geral de qualquer agente que edite `Assets/Scenes/*.unity` direto pelo
  `Edit`/`Write` com o Editor aberto (não só este item)
- **Why:** Ao editar `MainMenu.unity`/`DemoGameplay.unity` em disco e, bem depois, rodar
  `AssetDatabase.Refresh()` via `unity command run_script` (para gerar
  `CraftingPanel.prefab`), o Editor abriu o diálogo nativo "The open scene(s) have been
  modified externally" — um modal Win32 que não aparece no JSON de nenhum comando: todo
  `unity command <algo>` subsequente só devolve "Main thread operation timed out after
  30000ms" (confirmado no `Editor.log`), indefinidamente, porque o diálogo roda seu próprio
  loop de mensagens e nunca libera a thread principal para o despachante de comandos. `unity
  status` continua dizendo "ready" (não sonda o processo de verdade) — só
  `Get-Process -Id <pid> | Select Responding,MainWindowTitle` mostra `Responding: True` com
  o título sem alteração, e enumerar as janelas do processo (Win32 `EnumWindows`) revela o
  diálogo e os botões `&Reload`/`&Ignore`.
- **Fix:** Nenhuma ação de código pendente — é comportamento normal do Editor. Registrado
  para a próxima vez: se `unity command` travar em 30 s repetidamente com o Editor "ready",
  suspeitar de um diálogo nativo antes de supor crash; recuperar clicando `Reload` (ou pedir
  ao usuário) em vez de esperar ou derrubar o processo. Evitar o gatilho: preferir editar
  cenas pelos comandos do Editor (`set_component_properties`, `attach_script` etc.) a
  editar o `.unity` em disco quando o Editor já tem aquela cena aberta.

- **Item:** `DemoGameplay.unity` não tem `EventSystem` — nenhum painel UGUI instanciado nela
  ganha navegação por teclado/controle
- **Where:** `Assets/Scenes/DemoGameplay.unity`
- **Why:** Encontrado ao criar `Assets/Prefabs/UI/CraftingPanel.prefab` (2026-11-04): a cena
  só tem o Canvas da HUD (`HUD_Demo`, sem `GraphicRaycaster` interativo de fato) — sem
  `EventSystem`, `EventSystem.current` é `null` e qualquer `ShowPanel()` que chame
  `SetSelectedGameObject` (convenção de Steam Input deste agente) lança `NullReferenceException`
  assim que um painel interativo for instanciado e aberto nessa cena.
- **Fix:** Adicionar `EventSystem` + `InputSystemUIInputModule` à cena (mesmo par que já existe
  em `MainMenu.unity`) quando o crafting (ou qualquer outro painel UGUI) for de fato wireado em
  `DemoGameplay`.

- **Item:** `HUD_Demo` (`CanvasHealthHud`) usa `CanvasScaler` com referência 800×600, de antes do ADR-011
- **Where:** `Assets/Scenes/DemoGameplay.unity` → GameObject `HUD_Demo` → `CanvasScaler`
- **Why:** Encontrado na mesma inspeção acima. `Assets/Prefabs/UI/CraftingPanel.prefab` já nasce
  com `CanvasScaler` em Scale With Screen Size, referência 960×540 (ADR-011); o HUD ficou para
  trás.
- **Fix:** Alinhar o `CanvasScaler` do HUD para 960×540 / Match Width Or Height 0.5 e conferir a
  HUD em jogo depois.

### Baixa

- **Item:** `TilesetAutoSlicer` fatia o tileset placeholder do castelo em todas as 780 células (grid 52×15), não só as não-vazias
- **Where:** `Assets/Editor/Art/TilesetAutoSlicer.cs` · `Assets/Art/ThirdParty/Gothicvania/Environments/env_placeholder_castelo_tileset.png`
- **Why:** Ler a transparência por célula durante o import (`OnPreprocessTexture`) exigiria decodificar o PNG à mão nesse ponto do pipeline (a textura ainda não existe como objeto legível) — optei pela fatia completa, igual ao "Grid By Cell Size" padrão do Unity, para não arriscar um import quebrado sem retorno visual síncrono. A maioria das ~500 células vazias nunca vira sprite usado; só 3 viraram Tile asset para o blockout.
- **Fix:** Se algum dia vier um segundo tileset de terceiros maior, considerar filtrar por alfa no pós-import (`OnPostprocessTexture`, textura já legível) para não gerar sprites inúteis.

- **Item:** `env_placeholder_castelo_tileset.png` reslicado por engano durante o desenvolvimento do `TilesetAutoSlicer` chegou a colidir com os tilesets próprios de Blumenau (mesmo sufixo `_tileset.png`) — revertido antes do commit, mas o Editor aberto na sessão manteve os três por um instante com GUIDs trocados
- **Where:** `Assets/Art/Environments/Blumenau/Tilesets/env_blumenau_{agua,enxaimel,metal}_tileset.png`
- **Why:** O postprocessor nasceu com escopo `Assets/Art/` inteiro; corrigido para `Assets/Art/ThirdParty/` apenas (ver `Sistemas/Editor.md` → Notas de Design). Os três `.meta` foram revertidos via `git checkout --` e resincronizados com `AssetDatabase.Refresh(ForceUpdate)` antes do commit; nenhuma mudança chegou a ser commitada.
- **Fix:** Nenhuma ação pendente — registrado para o caso de algum Tile/Tilemap de Blumenau aparecer com sprite faltando; sinal de que o Editor ficou com estado em memória dessincronizado do disco por algum motivo não coberto aqui. Reimportar os três manualmente (clique direito → Reimport) resolveria.

---

*QA Engineer and Tech Lead can add items when reviewing code or after refactors. Remove or mark “Done” when addressed.*
