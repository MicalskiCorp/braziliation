# ComfyUI — Setup Local (Opção C do pipeline)

> Registro exigido pelo `pipeline-ia-sprites.md` (pasta `Models/` = notas sobre modelos e configurações).

## Instalação (2026-07-11)

| Item | Valor |
|------|-------|
| Local | `D:\Tools\ComfyUI` (fora do repo — só os workflows e notas são versionados) |
| GPU | NVIDIA RTX 2060 SUPER, 8GB VRAM — SDXL roda em fp16 |
| Python | 3.13 via launcher `py` |
| Torch | 2.8.0+cu129 (`py -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu129 --force-reinstall`) |

> ⚠️ **Pegadinha:** o `requirements.txt` do ComfyUI sobrescreve torch/torchaudio com builds **CPU** do PyPI. Sempre reinstalar os três (torch, torchvision, torchaudio) da index cu129 **depois** do `pip install -r requirements.txt` — sintomas: `Torch not compiled with CUDA enabled` ou `WinError 127` no torchaudio. Validação executada em 2026-07-12: lote de 6 thumbnails (seed 20260712) via `Ferramentas/comfy_batch.py` → `IA/Outputs/soldado-clerico-thumbs/`. |
| Modelo base | `sd_xl_base_1.0.safetensors` (SDXL 1.0, ~6.9GB) em `models/checkpoints/` |
| LoRA | `pixel-art-xl.safetensors` (170.5MB) em `models/loras/` — [nerijs/pixel-art-xl](https://huggingface.co/nerijs/pixel-art-xl), licença `creativeml-openrail-m`, sem trigger word, força recomendada 1.2. Baixado em 2026-07-26 depois que os lotes 1-3 do teste-âncora (Edith Gaertner, ver `ContextPacks/chr-blumenau-edith-gaertner/lotes.md`) confirmaram que `sd_xl_base_1.0` puro não produz densidade/estilo de pixel art via prompt sozinho, mesmo com referência real em img2img. Wired nos dois workflows (`workflow-thumbnails.json`, `workflow-img2img.json`) via nó `LoraLoader` entre o checkpoint e o CLIP/KSampler. **Proveniência do dataset de treino do LoRA não confirmada** pela página do modelo — ver `pipeline-ia-sprites.md#regra-legal-e-criativa` antes de usar a saída como asset final sem pixel pass manual pesado (já é regra do pipeline, mas vale reforçar aqui). |

## Custom nodes instalados (2026-09-03)

Esta instalação **não tem ComfyUI-Manager** — os packs entram por `git clone` direto em
`D:\Tools\ComfyUI\custom_nodes\` e exigem restart do servidor para carregar.

| Pack | Repo | O que traz | Deps |
|------|------|-----------|------|
| `ComfyUI-layerdiffuse` | [huchenlei/ComfyUI-layerdiffuse](https://github.com/huchenlei/ComfyUI-layerdiffuse) | 8 nós de transparência latente — `LayeredDiffusionApply`, `LayeredDiffusionDecodeRGBA` e variantes. Gera sprite **já recortado**, com alpha real | `diffusers>=0.29.0`, `opencv-python` |
| `ComfyUI-DNF-ColorLock` | [yifu23333/ComfyUI-DNF-ColorLock](https://github.com/yifu23333/ComfyUI-DNF-ColorLock) | `DNFReferencePaletteFinalize` (downscale + quantização travada numa paleta de referência), `DNFPixelPerfectFinalize` (limpeza de outline + máscara do sujeito), `DNFSpatialChromaLock` | nenhuma |

Nomes de retorno que importam ao montar grafo:
`DNFReferencePaletteFinalize` → `(final_image, nearest_preview, reference_palette)` — índice **0** é o sprite.
`DNFPixelPerfectFinalize` → `(final_original_background, green_edge_check, subject_mask)`.

> **Nota de pesquisa (2026-09-03):** circula a recomendação de inserir um nó de *Palette
> Quantize dentro do loop do KSampler* pelo slot Custom Noise. **Não foi possível confirmar** —
> nenhum dos nós instalados faz quantização durante a amostragem; os do DNF são pós-processo.
> A fonte da recomendação era de baixa qualidade. O ganho real e verificado destes nós é outro:
> alpha nativo (LayerDiffuse) e quantização **travada numa paleta de referência** em vez de
> torcida para cair na paleta depois (o que `pixelize.py` faz).

## Workflows do projeto

| Arquivo | Para quê |
|---------|----------|
| `workflow-thumbnails.json` | Lote de concepts opacos 1024×1024 (Etapa 2 — concept de cena) |
| `workflow-img2img.json` | Igual, partindo de concept/referência aprovada |
| `workflow-sprite-alpha.json` | **Sprite de produção**: LayerDiffuse (alpha nativo) → downscale para o canvas alvo → paleta travada no swatch da região. Salva duas saídas: o sprite pixelizado e o RGBA cru |
| `workflow-zimage-thumbnails.json` | **Candidato B do bench de modelo base**: Z-Image Turbo. Contraparte de `workflow-thumbnails.json` (SDXL = candidato A) para A/B com prompt e seed idênticos |

> **Resultado do bench (2026-09-03):** ver [`bench-modelo-base-2026-09.md`](bench-modelo-base-2026-09.md).
> Resumo: Z-Image **não substitui** o SDXL — some. Z-Image para concept (Etapa 2), SDXL +
> `pixel-art-xl` para referência pixelada. E o gargalo desta máquina é **RAM do sistema**
> (0,6 GB livres com os dois modelos residentes), não VRAM: rode um modelo de cada vez.

### Z-Image Turbo — arquivos e diferenças

Z-Image não vem como checkpoint único; são **três** arquivos separados:

| Arquivo | Pasta | Origem |
|---------|-------|--------|
| `z_image_turbo_fp8_e4m3fn.safetensors` | `models/diffusion_models/` | [tsqn/Z-Image-Turbo_fp8_comfyui](https://huggingface.co/tsqn/Z-Image-Turbo_fp8_comfyui) — o repo oficial só publica bf16/int8/nvfp4, e o bf16 pede 16 GB |
| `qwen_3_4b_fp8_mixed.safetensors` | `models/text_encoders/` | [Comfy-Org/z_image_turbo](https://huggingface.co/Comfy-Org/z_image_turbo) |
| `z_image_ae.safetensors` | `models/vae/` | idem (`split_files/vae/ae.safetensors`) |

Três diferenças que quebram se você copiar o workflow do SDXL:

- Text encoder é **Qwen** — `CLIPLoader` com `type: "qwen_image"`, e o encode é
  `TextEncodeZImageOmni` (campo **`prompt`**, não `text`).
- Latente é `EmptySD3LatentImage`, não `EmptyLatentImage`.
- É modelo **destilado**: `steps: 8`, `cfg: 1.0`. Os 25 steps / cfg 6.5 do SDXL queimam a imagem.

> `comfy_batch.py` não patcheia este workflow direto — ele escreve em `inputs.text` dos nós
> 6/7, que aqui se chama `prompt`.

`workflow-sprite-alpha.json` mantém os ids `3/6/7/9` do workflow de thumbnails, então
`comfy_batch.py --workflow ../IA/Models/workflow-sprite-alpha.json` funciona sem alteração.
Requer o swatch em `D:\Tools\ComfyUI\input\` — gerar com
`py Ferramentas/palette_swatch.py ../../ArteConceitual/Paletas/blumenau.json -o D:/Tools/ComfyUI/input/blumenau_swatch.png`.

Na primeira execução o LayerDiffuse baixa o modelo de transparência (~700 MB) para
`models/layer_model/`.

### Cadeia verificada de sprite com alpha (2026-09-03)

Testada ponta a ponta. Resultado em `IA/Outputs/sprite-alpha-teste/` (seed 20260903):

```
LayerDiffuse (Conv Injection) → RGBA 1024×1024 (88% dos px transparentes)
    → py pixelize.py {rgba}.png blumenau.json --size 32x32
    → 32×32 RGBA, 8/32 cores, palette_check APROVADO
    → pixel pass manual (continua obrigatório)
```

Três armadilhas encontradas e resolvidas, todas com sintoma silencioso:

1. **`Attention Injection` mata o LoRA.** A variante de atenção do LayerDiffuse colide com
   `pixel-art-xl`, que também patcheia atenção: o log cospe ~560 `patch type not recognized
   lora ...attn...` e o LoRA simplesmente não vale. **Use `Conv Injection`** — com ele o
   contador vai a zero.
2. **`ComfyUI-layerdiffuse` está desatualizado para o ComfyUI 0.27.** Ele chama
   `JoinImageWithAlpha().join_image_with_alpha()`, e o 0.27 migrou esse nó para o schema V3
   (`classmethod execute()` → `io.NodeOutput`). Quebra com `AttributeError` no último passo,
   **depois** de gastar os 25 steps. Há um **patch local** em
   `custom_nodes/ComfyUI-layerdiffuse/layered_diffusion.py` (marcado `PATCH LOCAL`) — um
   `git pull` nesse pack o desfaz.
3. **`DNFReferencePaletteFinalize` não serve como passo final de sprite transparente.** Ele
   quantiza o fundo junto com o sprite, então o verde vira uma cor da paleta e deixa de ser
   chaveável. Serve para inspecionar leitura em paleta travada, não para produzir o asset.
   Quem faz o passo de paleta preservando alpha é o `pixelize.py`.

## Como rodar

```powershell
cd D:\Tools\ComfyUI
py main.py            # UI em http://127.0.0.1:8188
# headless p/ API: py main.py --dont-print-server
```

## Workflow padrão do projeto

`Design/ArteFonte/IA/Models/workflow-thumbnails.json` — text-to-image de thumbnails (lote de 6, 512×512, seed fixa) usando o prompt em camadas do projeto. Carregar via "Load" na UI ou submeter via API (`POST /prompt`).

Parâmetros padrão do lote de thumbnails:

| Parâmetro | Valor | Motivo |
|-----------|-------|--------|
| Resolução | 1024×1024 (SDXL nativo) | Conceito; o pixel pass reduz depois |
| Steps | 25 | Suficiente p/ thumbnail |
| CFG | 6.5 | Médio — pipeline pede "evitar exagero de detalhe" |
| Sampler | euler / normal | Estável |
| Batch | 6 | Lote pequeno p/ comparação lado a lado (pipeline: 6–12) |
| Seed | fixa por lote, registrada no context pack | Reprodutibilidade |

## Regras (do pipeline-ia-sprites.md)

- Saída bruta → `Design/ArteFonte/IA/Outputs/{asset}/`; seleção → `Selected/`; descartes úteis → `Rejected/`.
- Prompt, seed, modelo e referências registrados no context pack do asset.
- **Nunca** aprovar sprite direto da IA — pixel pass manual/programático obrigatório.
- Sem nomes de artistas vivos no prompt; sem datasets de jogos comerciais.
