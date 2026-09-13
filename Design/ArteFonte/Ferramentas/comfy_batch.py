#!/usr/bin/env python3
"""Submete um lote de thumbnails ao ComfyUI local (Opção C do pipeline).

Preenche o workflow-template com prompt/seed, envia via API (POST /prompt),
aguarda a conclusão e copia os PNGs gerados para Design/ArteFonte/IA/Outputs/{asset}/.
Registra prompt+seed num arquivo .lote.json junto dos outputs (exigência do pipeline).

Modo padrão (text-to-image, workflow-thumbnails.json): lote de 6 variações por seed.

Modo com referência (--reference-image): usa workflow-img2img.json — carrega o
concept art aprovado no Passo 2 (`Design/ArteConceitual/{categoria}/{asset}/concept.png`)
ou uma silhueta própria como imagem inicial (LoadImage + VAEEncode + denoise parcial,
só com nós stock do ComfyUI). Gera 1 imagem por submissão; repita com seeds diferentes
para variações. NÃO testado ponta a ponta neste ambiente (servidor ComfyUI não estava
rodando ao escrever isto) — faça um dry run antes de confiar no resultado.

Uso:
  python comfy_batch.py --asset soldado-clerico --seed 20260712 \
      --positive "pixel art concept ..." --negative "photorealistic, ..." \
      [--workflow ../IA/Models/workflow-thumbnails.json] [--server 127.0.0.1:8188]

  python comfy_batch.py --asset soldado-clerico --seed 20260712 \
      --positive "..." --negative "..." \
      --reference-image ../../ArteConceitual/Personagens/soldado-clerico/concept.png --denoise 0.55

Pré-requisito: servidor ComfyUI rodando (py main.py em D:\\Tools\\ComfyUI).
Dependência: stdlib apenas (urllib).
"""
import argparse
import json
import shutil
import time
import urllib.request
from pathlib import Path

HERE = Path(__file__).parent


def api(server: str, path: str, payload: dict | None = None):
    url = f"http://{server}{path}"
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"} if data else {})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--asset", required=True, help="Nome do lote (vira subpasta em IA/Outputs/)")
    ap.add_argument("--positive", required=True)
    ap.add_argument("--negative", required=True)
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--workflow", type=Path, default=None,
                     help="Default: workflow-thumbnails.json, ou workflow-img2img.json se --reference-image for usado")
    ap.add_argument("--server", default="127.0.0.1:8188")
    ap.add_argument("--comfy-output", type=Path, default=Path("D:/Tools/ComfyUI/output"))
    ap.add_argument("--reference-image", type=Path, default=None,
                     help="Concept art aprovado (Passo 2) ou silhueta própria — ativa o modo image-to-image")
    ap.add_argument("--denoise", type=float, default=0.55,
                     help="Denoise do KSampler no modo --reference-image (menor = mais fiel à referência)")
    ap.add_argument("--comfy-input", type=Path, default=Path("D:/Tools/ComfyUI/input"),
                     help="Pasta input/ do servidor ComfyUI, onde LoadImage lê os arquivos")
    args = ap.parse_args()

    workflow_path = args.workflow or HERE / (
        "../IA/Models/workflow-img2img.json" if args.reference_image else "../IA/Models/workflow-thumbnails.json"
    )
    wf = json.loads(workflow_path.read_text(encoding="utf-8"))
    wf.pop("_comment", None)
    wf["6"]["inputs"]["text"] = args.positive
    wf["7"]["inputs"]["text"] = args.negative
    wf["3"]["inputs"]["seed"] = args.seed
    wf["9"]["inputs"]["filename_prefix"] = f"braziliation_{args.asset}"

    if args.reference_image:
        args.comfy_input.mkdir(parents=True, exist_ok=True)
        dest_ref = args.comfy_input / args.reference_image.name
        shutil.copy2(args.reference_image, dest_ref)
        wf["10"]["inputs"]["image"] = args.reference_image.name
        wf["3"]["inputs"]["denoise"] = args.denoise

    resp = api(args.server, "/prompt", {"prompt": wf})
    pid = resp["prompt_id"]
    print(f"Lote submetido (prompt_id={pid}, seed={args.seed}). Aguardando...")

    while True:
        hist = api(args.server, f"/history/{pid}")
        if pid in hist and hist[pid].get("outputs"):
            break
        time.sleep(5)

    images = []
    for node in hist[pid]["outputs"].values():
        for img in node.get("images", []):
            images.append(img["filename"])

    dest = HERE / f"../IA/Outputs/{args.asset}"
    dest.mkdir(parents=True, exist_ok=True)
    for name in images:
        src = args.comfy_output / name
        if src.exists():
            shutil.copy2(src, dest / name)
    lote = {
        "asset": args.asset, "seed": args.seed, "prompt_id": pid,
        "positive": args.positive, "negative": args.negative,
        "workflow": workflow_path.name, "model": "sd_xl_base_1.0.safetensors",
        "images": images,
    }
    if args.reference_image:
        lote["reference_image"] = str(args.reference_image)
        lote["denoise"] = args.denoise
    (dest / f"{args.asset}.lote.json").write_text(
        json.dumps(lote, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"OK: {len(images)} imagens em {dest} + registro {args.asset}.lote.json")


if __name__ == "__main__":
    main()
