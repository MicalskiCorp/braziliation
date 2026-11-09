# Catálogo das ferramentas de arte

> Uso, parâmetros e o porquê de cada script de `Design/ArteFonte/Ferramentas/`. O roteador é o [`index.md`](index.md); o motor `pxfx` tem a própria página em [`pxfx/index.md`](pxfx/index.md).

## Scripts do pipeline (Opções A–D)

| Script | Função | Uso típico |
|--------|--------|-----------|
| [`render_spec.py`](render_spec.py) | Transforma spec JSON (matriz de chars + paleta) em PNG — spec consolidada (multi-output + sheets) ou legada (1 arquivo por frame) | `py render_spec.py spec.json` |
| [`palette_check.py`](palette_check.py) | Valida PNG contra paleta oficial (cores permitidas + limite `max_colors_per_sprite` da paleta — 32) | `py palette_check.py sprite.png paleta.json` |
| [`mock_scene.py`](mock_scene.py) | Compõe sprite em cena mock 960×540 para teste de leitura 1x | `py mock_scene.py sprite.png paleta.json` |
| [`upscale_preview.py`](upscale_preview.py) | Amplia PNG (nearest-neighbor, grade opcional) para crítica visual | `py upscale_preview.py sprite.png -s 8 --grid` |
| [`sheet_pack.py`](sheet_pack.py) | Empacota frames em spritesheet horizontal (canvas estável obrigatório) | `py sheet_pack.py -o sheet.png f1.png f2.png f3.png` |
| [`spec_tween.py`](spec_tween.py) | Deriva os frames de uma animação de specs-chave + receita (`.anim.json`): chaves ciclam, camadas deslocam faixas de linhas por frame; emite a spec consolidada | `py spec_tween.py x.anim.json` |
| [`gen_tileset.py`](gen_tileset.py) | Gera tilesets procedurais com seed determinística + manifest — 7 famílias: enxaimel, metal, agua, pedra_portuguesa, cemiterio, marmore, periferia. Tile 48×48 do ADR-011 por default (`--scale 3`); o manifest marca em `notas` os tiles de base/remate que não ladrilham livres. `--bordas TIPO` acrescenta topo, quinas e laterais derivados do miolo do tipo (ar transparente), sem mudar o resto do sheet | `py gen_tileset.py cemiterio --palette paleta.json --seed 42 -o out.png` |
| [`gen_map_wfc.py`](gen_map_wfc.py) | **Monta** os tiles em mapa por WFC: preview + `.map.json` + manifest. Adjacência à mão ou derivada de exemplo (`--learn`); `--pin` fixa marcos; tile com `"exige_ar_acima": true` (topo e quinas) só aceita ar por cima | `py gen_map_wfc.py rulesets/blumenau-fachada.json --seed 42 -w 20 -H 12 -o ../IA/Outputs/mapa.png` |
| [`comfy_batch.py`](comfy_batch.py) | Submete lote ao ComfyUI e registra prompt, seed, modelo e sampler (`.lote.json`). Dirige qualquer workflow pelo grafo (SDXL, Z-Image, sprite-alpha); `--reference-image` usa concept aprovado como base; `--dry-run` confere sem gerar | `py comfy_batch.py --asset x --seed N --positive "..." --negative "..." [--reference-image concept.png --denoise 0.55]` |
| [`spec_redetail.py`](spec_redetail.py) | Re-autoria assistida do 1×: EPX (`--scale 2`) ou Scale3x (`--scale 3`, grid 48 do ADR-011) + textura com seed; emite spec versionada + PNG | `py spec_redetail.py spec1x.json --scale 3` |
| [`pagina_personagem.py`](pagina_personagem.py) | Gera a página do personagem (artefato) da spec + `{asset}.pagina.json` | `py pagina_personagem.py x.spec.json --saida p/` |
| [`galeria_personagens.py`](galeria_personagens.py) | Regenera todas as páginas de personagem e monta o hub da galeria (`IA/Paginas/_hub/`): a galeria do claude.ai não tem pastas, e o hub é a lista única com capa, status e link | `py galeria_personagens.py [--so-hub]` |
| [`montagem_base.py`](montagem_base.py) | Motor da montagem por peças: primitivas, rampas, ligas e acabamento. O catálogo fica com o asset | `from montagem_base import *` |
| [`raster_3over2.py`](raster_3over2.py) | ×1,5 para PNG **sem spec** (raster antigo, saída de difusão): Scale3x + redução 2:1 por cor dominante, sem inventar cor | `py raster_3over2.py in.png -o out.png` |
| [`prepare_thirdparty_gothicvania.py`](prepare_thirdparty_gothicvania.py) | Baixa e instala os placeholders CC0 do Gothicvania em `Assets/Art/ThirdParty/`, com sheets fatiáveis e `.meta` de GUID fixo | `py prepare_thirdparty_gothicvania.py [--dry-run]` |
| [`palette_swatch.py`](palette_swatch.py) | Converte a paleta em imagem de amostras — ponte para os nós do ComfyUI que recebem paleta como IMAGEM | `py palette_swatch.py ../../ArteConceitual/Paletas/blumenau.json -o D:/Tools/ComfyUI/input/blumenau_swatch.png` |
| [`check_art_palettes.py`](check_art_palettes.py) | Gate em lote: todo PNG próprio de `Assets/Art/` contra `regras-assets.json`; PNG sem regra reprova. Roda no pre-commit | `py check_art_palettes.py` |
| [`pixelize.py`](pixelize.py) | Reduz saída crua de difusão à paleta da região no canvas alvo; ponto de partida do pixel pass manual, não substituto | `py pixelize.py concept_raw.png paleta.json --size 64x64` |
