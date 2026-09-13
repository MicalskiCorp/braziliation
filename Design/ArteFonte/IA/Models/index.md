# Models — Modelos, workflows e benches de IA

> Notas sobre modelos, configurações e workflows da geração por difusão (rota C) e do retoque no Aseprite. Guia do processo: [`pipeline-ia-sprites.md`](../../../GuiasDeArte/pipeline-ia-sprites.md).

## Guias e registros

| Arquivo | Conteúdo |
|---------|----------|
| [`comfyui-setup.md`](comfyui-setup.md) | Setup local do ComfyUI (torch/CUDA, nós, modelos) e a pegadinha do `requirements.txt` |
| [`aseprite-mcp.md`](aseprite-mcp.md) | Aseprite via MCP (pixel-mcp) para retoque fino e pixel pass |
| [`bench-modelo-base-2026-09.md`](bench-modelo-base-2026-09.md) | SDXL × Z-Image Turbo — Z-Image para concept, SDXL + `pixel-art-xl` para referência pixelada |
| [`bench-modelo-claude-spec-2026-09.md`](bench-modelo-claude-spec-2026-09.md) | Qual modelo Claude o `@SpriteArtist` usa para escrever spec JSON |
| [`pesquisa-ferramentas-2026-07.md`](pesquisa-ferramentas-2026-07.md) | Ferramentas de sprite e animação por IA, com preços — decisão vigente: só free/local |

## Workflows do ComfyUI (usados pelo `comfy_batch.py`)

| Arquivo | Uso |
|---------|-----|
| `workflow-thumbnails.json` | Lote de thumbnails a partir de texto (SDXL) |
| `workflow-zimage-thumbnails.json` | Lote de thumbnails com Z-Image Turbo |
| `workflow-img2img.json` | Image-to-image a partir de concept ou silhueta (`--reference-image`) |
| `workflow-sprite-alpha.json` | Sprite com alpha nativo (LayerDiffuse) |
