# Ferramentas — Pipeline Programático de Sprites

Scripts que sustentam o pipeline descrito em [`../../GuiasDeArte/pipeline-sprites-programaticos.md`](../../GuiasDeArte/pipeline-sprites-programaticos.md). Todos rodam **sem nenhum agente de IA** — são código puro, versionado e reproduzível.

**Dependência única:** `pip install pillow` (Python 3.10+).

> No Windows desta máquina, o comando é `py` (launcher), não `python` — ex.: `py render_spec.py spec.json` e `py -m pip install pillow`.

## Scripts

| Script | Função | Uso típico |
|--------|--------|-----------|
| [`render_spec.py`](render_spec.py) | Transforma spec JSON (matriz de chars + paleta) em PNG — spec consolidada (multi-output + sheets) ou legada (1 arquivo por frame) | `py render_spec.py spec.json` |
| [`palette_check.py`](palette_check.py) | Valida PNG contra paleta oficial (cores permitidas + limite `max_colors_per_sprite` da paleta — 32) | `py palette_check.py sprite.png paleta.json` |
| [`mock_scene.py`](mock_scene.py) | Compõe sprite em cena mock 960×540 para teste de leitura 1x | `py mock_scene.py sprite.png paleta.json` |
| [`upscale_preview.py`](upscale_preview.py) | Amplia PNG (nearest-neighbor, grade opcional) para crítica visual | `py upscale_preview.py sprite.png -s 8 --grid` |
| [`sheet_pack.py`](sheet_pack.py) | Empacota frames em spritesheet horizontal (canvas estável obrigatório) | `py sheet_pack.py -o sheet.png f1.png f2.png f3.png` |
| [`spec_tween.py`](spec_tween.py) | Deriva os frames de uma animação de specs-chave + receita (`.anim.json`): chaves ciclam, camadas deslocam faixas de linhas por frame; emite a spec consolidada | `py spec_tween.py x.anim.json` |
| [`gen_tileset.py`](gen_tileset.py) | Gera tilesets procedurais (famílias: enxaimel, metal, agua) com seed determinística + manifest; `--scale 3` produz o tile 48×48 do ADR-011 | `py gen_tileset.py enxaimel --palette paleta.json --seed 42 -o out.png` |
| [`gen_map_wfc.py`](gen_map_wfc.py) | **Monta** os tiles em mapa por WFC: preview + `.map.json` + manifest. Adjacência à mão ou derivada de exemplo (`--learn`); `--pin` fixa marcos | `py gen_map_wfc.py rulesets/blumenau-fachada.json --seed 42 -w 20 -H 12 -o ../IA/Outputs/mapa.png` |
| [`comfy_batch.py`](comfy_batch.py) | Submete lote ao ComfyUI e registra prompt/seed (`.lote.json`); `--reference-image` usa concept aprovado como base | `py comfy_batch.py --asset x --seed N --positive "..." --negative "..." [--reference-image concept.png --denoise 0.55]` |
| [`spec_redetail.py`](spec_redetail.py) | Re-autoria assistida do 1×: EPX (`--scale 2`) ou Scale3x (`--scale 3`, grid 48 do ADR-011) + textura com seed; emite spec versionada + PNG | `py spec_redetail.py spec1x.json --scale 3` |
| [`pagina_personagem.py`](pagina_personagem.py) | Gera a página do personagem (artefato) da spec + `{asset}.pagina.json` | `py pagina_personagem.py x.spec.json --saida p/` |
| [`montagem_base.py`](montagem_base.py) | Motor da montagem por peças: primitivas, rampas, ligas e acabamento. O catálogo fica com o asset | `from montagem_base import *` |
| [`raster_3over2.py`](raster_3over2.py) | ×1,5 para PNG **sem spec** (raster antigo, saída de difusão): Scale3x + redução 2:1 por cor dominante, sem inventar cor | `py raster_3over2.py in.png -o out.png` |
| [`prepare_thirdparty_gothicvania.py`](prepare_thirdparty_gothicvania.py) | Baixa e instala os placeholders CC0 do Gothicvania em `Assets/Art/ThirdParty/`, com sheets fatiáveis e `.meta` de GUID fixo | `py prepare_thirdparty_gothicvania.py [--dry-run]` |
| [`palette_swatch.py`](palette_swatch.py) | Converte a paleta em imagem de amostras — ponte para os nós do ComfyUI que recebem paleta como IMAGEM | `py palette_swatch.py ../../ArteConceitual/Paletas/blumenau.json -o D:/Tools/ComfyUI/input/blumenau_swatch.png` |
| [`check_art_palettes.py`](check_art_palettes.py) | Gate em lote: todo PNG próprio de `Assets/Art/` contra `regras-assets.json`; PNG sem regra reprova. Roda no pre-commit | `py check_art_palettes.py` |
| [`pixelize.py`](pixelize.py) | Reduz saída crua de difusão à paleta da região no canvas alvo; ponto de partida do pixel pass manual, não substituto | `py pixelize.py concept_raw.png paleta.json --size 64x64` |

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
