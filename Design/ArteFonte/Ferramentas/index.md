# Ferramentas — Pipeline Programático de Sprites

Scripts que sustentam o pipeline descrito em [`../../GuiasDeArte/pipeline-sprites-programaticos.md`](../../GuiasDeArte/pipeline-sprites-programaticos.md). Todos rodam **sem nenhum agente de IA** — são código puro, versionado e reproduzível.

**Dependência única:** `pip install pillow` (Python 3.10+).

> No Windows desta máquina, o comando é `py` (launcher), não `python` — ex.: `py render_spec.py spec.json` e `py -m pip install pillow`.

## Scripts

| Script | Função | Uso típico |
|--------|--------|-----------|
| [`render_spec.py`](render_spec.py) | Transforma spec JSON (matriz de chars + paleta) em PNG — spec consolidada (multi-output + sheets) ou legada (1 arquivo por frame) | `py render_spec.py spec.json` |
| [`palette_check.py`](palette_check.py) | Valida PNG contra paleta oficial (cores permitidas + limite `max_colors_per_sprite` da paleta — 32 no ADR-004) | `py palette_check.py sprite.png paleta.json` |
| [`mock_scene.py`](mock_scene.py) | Compõe sprite em cena mock 640×360 para teste de leitura 1x | `py mock_scene.py sprite.png paleta.json` |
| [`upscale_preview.py`](upscale_preview.py) | Amplia PNG (nearest-neighbor, grade opcional) para crítica visual | `py upscale_preview.py sprite.png -s 8 --grid` |
| [`sheet_pack.py`](sheet_pack.py) | Empacota frames em spritesheet horizontal (canvas estável obrigatório) | `py sheet_pack.py -o sheet.png f1.png f2.png f3.png` |
| [`gen_tileset.py`](gen_tileset.py) | Gera tilesets procedurais (famílias: enxaimel, metal, agua) com seed determinística + manifest; `--scale 2` produz o tile 32×32 do ADR-004 | `py gen_tileset.py enxaimel --palette paleta.json --seed 42 -o out.png` |
| [`gen_map_wfc.py`](gen_map_wfc.py) | **Monta** os tiles em mapa por Wave Function Collapse: preview PNG + `.map.json` para o Unity + manifest. Adjacência escrita à mão no ruleset ou derivada de um exemplo desenhado (`--learn`); `--pin` fixa marcos autorais | `py gen_map_wfc.py rulesets/blumenau-fachada.json --seed 42 -w 20 -H 12 -o ../IA/Outputs/mapa.png` |
| [`comfy_batch.py`](comfy_batch.py) | Submete lote de thumbnails ao ComfyUI local via API e registra prompt/seed (`.lote.json`); com `--reference-image` usa concept art aprovado (Passo 2) como base image-to-image | `py comfy_batch.py --asset x --seed N --positive "..." --negative "..." [--reference-image concept.png --denoise 0.55]` |
| [`spec_redetail.py`](spec_redetail.py) | Re-autoria assistida 1×→2× (ADR-004): EPX suaviza curvas + textura de material com seed; emite spec 2× versionada + PNG | `py spec_redetail.py spec1x.json -o out.png` |
| [`prepare_thirdparty_gothicvania.py`](prepare_thirdparty_gothicvania.py) | Baixa, prepara e instala os placeholders CC0 do Gothicvania (ansimuz) em `Assets/Art/ThirdParty/` — upscale ×2, recorte por bbox de união por animação, sheets em células quadradas e `.meta` com GUID fixo | `py prepare_thirdparty_gothicvania.py [--dry-run]` |
| [`palette_swatch.py`](palette_swatch.py) | Converte a paleta JSON da região em imagem de amostras — ponte para os nós do ComfyUI que recebem paleta como IMAGEM (`DNFReferencePaletteFinalize`, `DNFSpatialChromaLock`) | `py palette_swatch.py ../../ArteConceitual/Paletas/blumenau.json -o D:/Tools/ComfyUI/input/blumenau_swatch.png` |
| [`check_art_palettes.py`](check_art_palettes.py) | Gate em lote: todo PNG próprio de `Assets/Art/` contra a paleta indicada em `ArteConceitual/Paletas/regras-assets.json`; PNG sem regra reprova. Roda no pre-commit e no CI | `py check_art_palettes.py` |
| [`pixelize.py`](pixelize.py) | Reduz saída crua de difusão (Rota C) à paleta oficial da região no canvas alvo — downscale por cor dominante por bloco + `Image.quantize` na paleta exata; ponto de partida pro pixel pass manual, não substitui | `py pixelize.py concept_raw.png paleta.json --size 64x64` |

## Aseprite via MCP

Para retoque fino e pixel pass, o `@SpriteArtist` usa o servidor MCP `aseprite` (pixel-mcp sobre o Aseprite local). Setup, localização dos arquivos e o motivo do perfil limpo: [`../IA/Models/aseprite-mcp.md`](../IA/Models/aseprite-mcp.md).

## Onde vive o quê

- **Specs de sprite (fonte)**: junto do context pack do asset em `../IA/ContextPacks/{asset}/` — a spec É a fonte editável do sprite programático.
- **Paletas machine-readable**: `../../ArteConceitual/Paletas/*.json` (derivadas do [`palette-guide.md`](../../GuiasDeArte/palette-guide.md)).
- **PNGs gerados**: `../IA/Outputs/` → curadoria em `../IA/Selected/` → final em `Desenvolvimento/Assets/Art/`.
- **Import no Unity**: automático — `Desenvolvimento/Assets/Editor/Art/SpriteImportPostprocessor.cs` força 32 PPU / Point / sem compressão em tudo que entra em `Assets/Art/`.

## Formato da spec (Opção A)

**Padrão atual — spec consolidada** (um JSON por objeto, todos os frames/variações dentro; ver detalhes em [`pipeline-sprites-programaticos.md`](../../GuiasDeArte/pipeline-sprites-programaticos.md#formato-da-spec-consolidada)):

```json
{
  "name": "prop_blumenau_floodgate_lever",
  "size": [32, 32],
  "palette": "../../ArteConceitual/Paletas/blumenau.json",
  "outputs": [
    {"id": "idle", "rows": ["...7A...", "..77AA..", "..."]},
    {"id": "f2",   "rows": ["...", "..."]}
  ],
  "sheets": {
    "activate": ["idle", "f2"]
  }
}
```

Cada caractere de `rows` é um pixel: `.` = transparente; os demais são a `key` da cor na paleta JSON. `rows` deve ter exatamente `size[1]` linhas de `size[0]` caracteres. `id: "idle"`/`"default"` renderiza para `{name}.png`; outros ids renderizam para `{name}_{id}.png`; cada entrada de `sheets` empacota a sequência em `{name}_{chave}_sheet.png`.

**Formato legado** (1 arquivo por frame, `rows` na raiz em vez de `outputs`): o `render_spec.py` ainda lê para não quebrar assets já entregues — não usar em specs novas.
