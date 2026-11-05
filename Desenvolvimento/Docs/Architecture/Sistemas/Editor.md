# Sistema: Editor

> **Responsabilidade:** Ferramentas do Unity Editor — import de arte, fatiamento de sheets, animação, importação de mapas WFC e montagem de cenas. Não entram no build do jogo.
> **Status:** 🔨 Em Desenvolvimento

---

## Fontes Técnicas

| Arquivo | Caminho | Função |
|---------|---------|--------|
| `SpriteImportPostprocessor.cs` | `Assets/Editor/Art/SpriteImportPostprocessor.cs` | Força Point, sem compressão e o PPU de `PixelScale` em toda textura de `Assets/Art/` |
| `PixelScale.cs` | `Assets/Editor/Art/PixelScale.cs` | Fonte única do PPU por asset durante a migração do ADR-011: 48 no grid atual, 32 no que ainda não foi re-autorado |
| `SheetAutoSlicer.cs` | `Assets/Editor/Art/SheetAutoSlicer.cs` | Fatia `*_sheet.png`: com o JSON lateral do pxfx, quadro e pivô do JSON (ADR-016); sem ele, grade quadrada com pivot no centro-inferior. Preserva IDs |
| `SheetMetadata.cs` | `Assets/Editor/Art/SheetMetadata.cs` | Lê o JSON lateral `{nome}_sheet.json` (formato `braziliation-sheet/1`: quadro, pivô, durações, loop) para o slicer e o gerador de clipe |
| `SheetAnimationTool.cs` | `Assets/Editor/Art/SheetAnimationTool.cs` | Gera AnimationClip + AnimatorController de um sheet fatiado (`Assets > Braziliation > Criar Animação do Spritesheet`), com a duração de cada quadro e o loop do JSON lateral quando existe (senão 8 fps); lote fixo da onda atual em `Tools > Braziliation > Setup > Gerar Animators da Onda Atual` |
| `WfcMapImporter.cs` | `Assets/Editor/Art/WfcMapImporter.cs` | Pinta um Tilemap a partir do `.unity.json` do `gen_map_wfc.py` (`Assets > Braziliation > Importar Mapa WFC...`); variante sem diálogo para o mapa de teste em `Tools > Braziliation > Setup > Importar Mapa WFC de Teste` |
| `DemoSceneBuilderEditor.cs` | `Assets/Editor/Gameplay/DemoSceneBuilderEditor.cs` | Cria/atualiza a cena fixa `DemoGameplay.unity` (`Braziliation > Demo > Create or Update Fixed Demo Scene`) |
| `MainMenuUISetupEditor.cs` | `Assets/Editor/Menu/MainMenuUISetupEditor.cs` | Monta a hierarquia de UI do menu principal (`Tools > Braziliation > Setup Main Menu UI`) |
| `MenuBackgroundSetupEditor.cs` | `Assets/Editor/Menu/MenuBackgroundSetupEditor.cs` | Configura o fundo animado do menu (`Tools > Braziliation > Setup Menu Background`) |
| `FloodgateLeverPrefabBuilder.cs` | `Assets/Editor/Interactables/FloodgateLeverPrefabBuilder.cs` | Cria/atualiza `Prop_FloodgateLever.prefab` a partir do Animator da onda atual (`Tools > Braziliation > Setup > Build Floodgate Lever Prefab`) |
| `FloodgateGatePrefabBuilder.cs` | `Assets/Editor/Interactables/FloodgateGatePrefabBuilder.cs` | Cria/atualiza `Prop_FloodgateGate.prefab`: comporta + alavanca aninhada já ligada ao `FloodgateController.Toggle` (`Tools > Braziliation > Setup > Build Floodgate Gate Prefab`) |
| `AutomatoPrefabBuilder.cs` | `Assets/Editor/Enemies/AutomatoPrefabBuilder.cs` | Cria/atualiza `Enemy_Automato.prefab` com o Animator de idle em loop (`Tools > Braziliation > Setup > Build Automato Enemy Prefab`) |
| `TilesetAutoSlicer.cs` | `Assets/Editor/Art/TilesetAutoSlicer.cs` | Fatia `*_tileset.png` sob `Assets/Art/ThirdParty/` em grid completo (`{PixelScale.Para}²`), nomes `{nome}_{col}_{row}` — escopo restrito a ThirdParty de propósito (ver Notas de Design) |
| `CastleBlockoutEditor.cs` | `Assets/Editor/Gameplay/CastleBlockoutEditor.cs` | Cria/atualiza o blockout `Assets/Scenes/Sandbox/CastleBlockout.unity` (Tilemap + TilemapCollider2D) a partir de 3 Tiles do tileset placeholder do castelo (`Braziliation > Demo > Create or Update Castle Blockout Scene`) |

## Features que Usam Este Sistema

| Feature | Arquivo | Relação |
|---------|---------|---------|
| *(nenhuma documentada ainda)* | — | — |

## Dependências de Outros Sistemas

| Sistema | Arquivo | Motivo |
|---------|---------|--------|
| [Gameplay](Gameplay.md) | `DemoSceneVisuals.cs` | O builder da cena fixa usa a mesma fonte de geometria do bootstrap de runtime |

## Parâmetros Configuráveis

| Parâmetro | Tipo | Valor Padrão | Descrição |
|-----------|------|-------------|-----------|
| PPU de import | float | 48 | `PixelScale.Atual` (ADR-011); assets na lista `PixelScale.Legado` continuam a 32 até serem re-autorados |

## Notas de Design

- `SheetAutoSlicer`, `SheetAnimationTool` e `WfcMapImporter` foram exercitados em batchmode (`-executeMethod`) em 2026-11-03: geraram os três Animators da onda atual, os prefabs `Prop_FloodgateLever`/`Enemy_Automato` e o Tilemap de teste em `Assets/Scenes/WfcImportTest.unity`. O achado: a guarda de "já fatiado" do `SheetAutoSlicer` só olhava a contagem de quadros, não o tamanho — dois sheets redesenhados em PPU maior (lever e sino) ficaram fatiados com o rect antigo até o fix.
- `MainMenuUISetupEditor` ainda calcula o tamanho da câmera para 320×180 @ 16 PPU (pré-ADR-004) — registrado em `Tech/tech_debt.md`.
- `TilesetAutoSlicer` ficou restrito a `Assets/Art/ThirdParty/` (não todo `Assets/Art/`) porque os tilesets próprios em `Assets/Art/Environments/Blumenau/Tilesets/` também terminam em `_tileset.png`, mas já têm fatiamento autorado à mão (outra convenção de nomes). Rodar o postprocessor neles reatribui GUID novo a cada sprite e quebra qualquer Tile/Tilemap que já referencie os antigos — aconteceu na prática em 2026-11-04 (revertido antes do commit; ver `Tech/tech_debt.md`).
- `CastleBlockoutEditor`: os três Tiles (parede, topo e fuste do piso) são carregados/criados **depois** do `EditorSceneManager.NewScene(..., Single)`, nunca antes — carregá-los antes faz a referência em memória virar "fake null" assim que a cena anterior é descarregada (sem erro nenhum; o Tilemap simplesmente fica vazio). Custou um ciclo de depuração via `unity run_script` nesta sessão.
