# Sistema: Editor

> **Responsabilidade:** Ferramentas do Unity Editor — import de arte, fatiamento de sheets, animação, importação de mapas WFC e montagem de cenas. Não entram no build do jogo.
> **Status:** 🔨 Em Desenvolvimento

---

## Fontes Técnicas

| Arquivo | Caminho | Função |
|---------|---------|--------|
| `SpriteImportPostprocessor.cs` | `Assets/Editor/Art/SpriteImportPostprocessor.cs` | Força 32 PPU, Point e sem compressão em toda textura de `Assets/Art/` (ADR-004) |
| `SheetAutoSlicer.cs` | `Assets/Editor/Art/SheetAutoSlicer.cs` | Fatia `*_sheet.png` em grade quadrada com pivot no centro-inferior, preservando IDs |
| `SheetAnimationTool.cs` | `Assets/Editor/Art/SheetAnimationTool.cs` | Gera AnimationClip + AnimatorController de um sheet fatiado (`Assets > Braziliation > Criar Animação do Spritesheet`) |
| `WfcMapImporter.cs` | `Assets/Editor/Art/WfcMapImporter.cs` | Pinta um Tilemap a partir do `.unity.json` do `gen_map_wfc.py` (`Assets > Braziliation > Importar Mapa WFC...`) |
| `DemoSceneBuilderEditor.cs` | `Assets/Editor/Gameplay/DemoSceneBuilderEditor.cs` | Cria/atualiza a cena fixa `DemoGameplay.unity` (`Braziliation > Demo > Create or Update Fixed Demo Scene`) |
| `MainMenuUISetupEditor.cs` | `Assets/Editor/Menu/MainMenuUISetupEditor.cs` | Monta a hierarquia de UI do menu principal (`Tools > Braziliation > Setup Main Menu UI`) |
| `MenuBackgroundSetupEditor.cs` | `Assets/Editor/Menu/MenuBackgroundSetupEditor.cs` | Configura o fundo animado do menu (`Tools > Braziliation > Setup Menu Background`) |

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
| PPU de import | int | 32 | Definido no `SpriteImportPostprocessor` (ADR-004) |

## Notas de Design

- Várias ferramentas compilam mas ainda não foram exercitadas num Editor aberto — ver `Tech/tech_debt.md`.
- `MainMenuUISetupEditor` ainda calcula o tamanho da câmera para 320×180 @ 16 PPU (pré-ADR-004) — registrado em `Tech/tech_debt.md`.
