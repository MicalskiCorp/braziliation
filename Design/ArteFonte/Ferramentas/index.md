# Ferramentas — Pipeline Programático de Sprites

Scripts que sustentam o pipeline descrito em [`../../GuiasDeArte/pipeline-sprites-programaticos.md`](../../GuiasDeArte/pipeline-sprites-programaticos.md). Todos rodam **sem nenhum agente de IA** — são código puro, versionado e reproduzível.

**Dependências:** `pip install pillow numpy` (Python 3.10+). Node só para a paridade do `pxfx`.

> No Windows desta máquina, o comando é `py` (launcher), não `python` — ex.: `py render_spec.py spec.json` e `py -m pip install pillow`.

## Onde está cada coisa

| O quê | Onde |
|-------|------|
| **Motor `pxfx`** — efeitos (VFX), esqueleto e animação de personagem por código (ADR-016) | [`pxfx/index.md`](pxfx/index.md) · `py -m pxfx.render` · `py -m pxfx.esqueleto.animar` |
| Scripts do pipeline de sprite (Opções A–D): `render_spec.py`, `palette_check.py`, `mock_scene.py`, `upscale_preview.py`, `sheet_pack.py`, `spec_tween.py`, `gen_tileset.py`, `gen_map_wfc.py`, `comfy_batch.py`, `spec_redetail.py`, `pagina_personagem.py`, `montagem_base.py`, `raster_3over2.py`, `prepare_thirdparty_gothicvania.py`, `palette_swatch.py`, `check_art_palettes.py`, `pixelize.py` | [`catalogo.md`](catalogo.md) — uso e parâmetros de cada um |
| Cópia fixa do PixelFX original (gabarito de paridade; nunca editar) | `vendor/pixelfx/SOURCES.txt` |

## Aseprite via MCP

Para retoque fino e pixel pass, o `@SpriteArtist` usa o servidor MCP `aseprite` (pixel-mcp sobre o Aseprite local). Setup, localização dos arquivos e o motivo do perfil limpo: [`../IA/Models/aseprite-mcp.md`](../IA/Models/aseprite-mcp.md).

## Onde vive o quê

- **Specs de sprite (fonte)**: junto do context pack do asset em `../IA/ContextPacks/{asset}/` — a spec É a fonte editável do sprite programático.
- **Paletas machine-readable**: `../../ArteConceitual/Paletas/*.json` (derivadas do [`palette-guide.md`](../../GuiasDeArte/palette-guide.md)).
- **PNGs gerados**: `../IA/Outputs/` → curadoria em `../IA/Selected/` → final em `Desenvolvimento/Assets/Art/`.
- **Import no Unity**: automático — `Desenvolvimento/Assets/Editor/Art/SpriteImportPostprocessor.cs` força Point / sem compressão e o PPU de `PixelScale.cs` (48 no grid do ADR-011, 32 no legado) em tudo que entra em `Assets/Art/`.

## Formato da spec (Opção A)

O formato consolidado (um JSON por objeto, com `outputs` por frame/variação e `sheets` por
animação), a regra de `rows` e a convenção de nomes dos PNGs estão descritos em
[`pipeline-sprites-programaticos.md`](../../GuiasDeArte/pipeline-sprites-programaticos.md#formato-da-spec-consolidada)
— este índice só aponta. **Formato legado** (1 arquivo por frame, `rows` na raiz em vez de `outputs`): o `render_spec.py` ainda lê para não quebrar assets já entregues — não usar em specs novas.
