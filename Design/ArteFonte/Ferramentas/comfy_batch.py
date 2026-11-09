#!/usr/bin/env python3
"""Submete um lote de thumbnails ao ComfyUI local (Opção C do pipeline).

Preenche o workflow-template com prompt/seed, envia via API (POST /prompt),
aguarda a conclusão e copia os PNGs gerados para Design/ArteFonte/IA/Outputs/{asset}/.
Registra prompt+seed num arquivo .lote.json junto dos outputs (exigência do pipeline).

O script dirige o workflow que recebe, lendo o próprio grafo: acha o KSampler, segue as
ligações `positive`/`negative` até os nós de encode e escreve no campo que cada tipo de
encode lê (`CLIPTextEncode` → `text`, `TextEncodeZImageOmni` → `prompt`). Encode de tipo
desconhecido, nó faltando ou placeholder `{...}` sem preencher param o script com erro —
nunca uma falha silenciosa. Modelo, LoRAs, steps e cfg vão para o log como estão no
workflow (o Z-Image Turbo, destilado, já vem com 8 steps e cfg 1.0).

Workflows (em ../IA/Models/):
  workflow-thumbnails.json        SDXL + pixel-art-xl, texto → imagem (padrão)
  workflow-img2img.json           SDXL + pixel-art-xl, a partir de --reference-image (padrão com ela)
  workflow-zimage-thumbnails.json Z-Image Turbo, texto → imagem (rota decidida no bench para a Etapa 2)

Modo com referência (--reference-image): carrega o concept art aprovado no Passo 2
(`Design/ArteConceitual/{categoria}/{asset}/concept.png`) ou uma silhueta própria como imagem
inicial (LoadImage + VAEEncode + denoise parcial). Gera 1 imagem por submissão; repita com
seeds diferentes para variações.

Uso:
  py comfy_batch.py --asset soldado-clerico --seed 20260712 \\
      --positive "pixel art concept ..." --negative "photorealistic, ..." \\
      [--workflow ../IA/Models/workflow-zimage-thumbnails.json] [--server 127.0.0.1:8188]

  py comfy_batch.py --asset soldado-clerico --seed 20260712 \\
      --positive "..." --negative "..." \\
      --reference-image ../../ArteConceitual/Personagens/soldado-clerico/concept.png --denoise 0.55

  --dry-run monta e confere o workflow e mostra o que seria enviado, sem servidor.

Pré-requisito: servidor ComfyUI rodando (py main.py em D:\\Tools\\ComfyUI).
Dependência: stdlib apenas (urllib).
"""
import argparse
import json
import re
import shutil
import sys
import time
import urllib.request
from pathlib import Path

HERE = Path(__file__).parent
MODELS = HERE / "../IA/Models"

# Campo de texto que cada tipo de nó de encode lê. Tipo novo entra aqui, nunca por id de nó.
ENCODE_TEXT_FIELD = {
    "CLIPTextEncode": "text",
    "TextEncodeZImageOmni": "prompt",
}
# Nó que carrega o modelo base → campo com o nome do arquivo.
MODEL_LOADERS = {
    "CheckpointLoaderSimple": "ckpt_name",
    "UNETLoader": "unet_name",
}
PLACEHOLDER = re.compile(r"^\{[A-Z_]+\}$")


class WorkflowError(Exception):
    """Workflow que este script não sabe dirigir — melhor parar do que gerar com o prompt errado."""


def api(server: str, path: str, payload: dict | None = None):
    url = f"http://{server}{path}"
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"} if data else {})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())


def load_workflow(path: Path) -> dict:
    """Lê o workflow e tira as chaves de anotação (`_comment`, `_...`), que o ComfyUI rejeitaria como nó."""
    wf = json.loads(path.read_text(encoding="utf-8"))
    return {k: v for k, v in wf.items() if not k.startswith("_")}


def nodes_of(wf: dict, class_type: str) -> list[str]:
    return [nid for nid, node in wf.items() if node.get("class_type") == class_type]


def single(wf: dict, class_type: str) -> str:
    ids = nodes_of(wf, class_type)
    if len(ids) != 1:
        raise WorkflowError(f"esperado 1 nó {class_type}, achei {len(ids)}")
    return ids[0]


def encode_target(wf: dict, sampler_id: str, which: str) -> tuple[str, str]:
    """(id do nó, campo) do encode ligado à entrada `which` (positive/negative) do KSampler."""
    link = wf[sampler_id]["inputs"].get(which)
    if not (isinstance(link, list) and link and str(link[0]) in wf):
        raise WorkflowError(f"KSampler sem ligação válida em '{which}'")
    nid = str(link[0])
    ctype = wf[nid].get("class_type")
    field = ENCODE_TEXT_FIELD.get(ctype)
    if field is None:
        raise WorkflowError(
            f"encode '{ctype}' (nó {nid}) desconhecido — acrescente o campo dele em ENCODE_TEXT_FIELD "
            f"(conhecidos: {', '.join(ENCODE_TEXT_FIELD)})")
    return nid, field


def describe_model(wf: dict) -> dict:
    """Modelo base, LoRAs e parâmetros do sampler, lidos do próprio workflow (não de constante)."""
    base = [wf[nid]["inputs"][field] for ctype, field in MODEL_LOADERS.items() for nid in nodes_of(wf, ctype)]
    if len(base) != 1:
        raise WorkflowError(f"esperado 1 carregador de modelo ({', '.join(MODEL_LOADERS)}), achei {len(base)}")
    loras = [
        {"name": wf[nid]["inputs"]["lora_name"], "strength": wf[nid]["inputs"].get("strength_model")}
        for nid in nodes_of(wf, "LoraLoader")
    ]
    ks = wf[single(wf, "KSampler")]["inputs"]
    return {
        "model": base[0],
        "loras": loras,
        "sampler": {k: ks.get(k) for k in ("steps", "cfg", "sampler_name", "scheduler")},
    }


def prepare(wf: dict, *, asset: str, positive: str, negative: str, seed: int,
            reference_name: str | None = None, denoise: float | None = None) -> dict:
    """Preenche o workflow pelo grafo. Devolve o próprio dict, pronto para POST /prompt."""
    sampler = single(wf, "KSampler")
    for which, text in (("positive", positive), ("negative", negative)):
        nid, field = encode_target(wf, sampler, which)
        wf[nid]["inputs"][field] = text
    wf[sampler]["inputs"]["seed"] = seed

    saves = nodes_of(wf, "SaveImage")
    if not saves:
        raise WorkflowError("nenhum nó SaveImage")
    for nid in saves:
        # Com mais de uma saída (ex.: sprite-alpha salva a paleta travada e o RGBA), cada uma guarda o
        # próprio sufixo para não se misturarem.
        old = str(wf[nid]["inputs"].get("filename_prefix", ""))
        suffix = old.removeprefix("braziliation_") if len(saves) > 1 else ""
        wf[nid]["inputs"]["filename_prefix"] = f"braziliation_{asset}" + (f"_{suffix}" if suffix else "")

    # A imagem de referência entra só no LoadImage marcado com {IMAGE}; LoadImage fixo (ex.: o swatch
    # da paleta no sprite-alpha) fica como está.
    ref_loaders = [nid for nid in nodes_of(wf, "LoadImage") if wf[nid]["inputs"].get("image") == "{IMAGE}"]
    if reference_name is not None:
        if len(ref_loaders) != 1:
            raise WorkflowError("--reference-image pede um workflow com 1 LoadImage marcado {IMAGE} "
                                "(ex.: workflow-img2img.json)")
        wf[ref_loaders[0]]["inputs"]["image"] = reference_name
        wf[sampler]["inputs"]["denoise"] = denoise

    pending = [f"nó {nid}.{k}" for nid, node in wf.items() for k, v in node.get("inputs", {}).items()
               if isinstance(v, str) and PLACEHOLDER.match(v)]
    if pending:
        hint = " — este workflow parte de uma imagem: passe --reference-image" if ref_loaders else ""
        raise WorkflowError("placeholder sem preencher: " + ", ".join(pending) + hint)
    return wf


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
    ap.add_argument("--dry-run", action="store_true",
                     help="Monta e confere o workflow e mostra modelo, sampler e campos preenchidos, sem enviar")
    args = ap.parse_args()

    workflow_path = args.workflow or MODELS / (
        "workflow-img2img.json" if args.reference_image else "workflow-thumbnails.json")
    wf = load_workflow(workflow_path)
    try:
        info = describe_model(wf)
        prepare(wf, asset=args.asset, positive=args.positive, negative=args.negative, seed=args.seed,
                reference_name=args.reference_image.name if args.reference_image else None,
                denoise=args.denoise if args.reference_image else None)
    except WorkflowError as e:
        sys.exit(f"ERRO ({workflow_path.name}): {e}")

    if args.dry_run:
        print(json.dumps({"workflow": workflow_path.name, **info, "prompt": wf}, indent=2, ensure_ascii=False))
        return

    if args.reference_image:
        args.comfy_input.mkdir(parents=True, exist_ok=True)
        shutil.copy2(args.reference_image, args.comfy_input / args.reference_image.name)

    resp = api(args.server, "/prompt", {"prompt": wf})
    pid = resp["prompt_id"]
    print(f"Lote submetido (prompt_id={pid}, seed={args.seed}, modelo={info['model']}). Aguardando...")

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
        "workflow": workflow_path.name, **info,
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
