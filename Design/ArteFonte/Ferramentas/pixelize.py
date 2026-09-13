#!/usr/bin/env python3
"""Reduz uma imagem de difusão (ComfyUI/SDXL, RGB "pintado") a pixel art
paletizada na paleta oficial do projeto — a ponte que faltava entre a Rota C
(difusão) e o pixel pass manual no Aseprite.

Não substitui o pixel pass manual (a style-bible proíbe aprovar sprite direto
da IA) — entrega um ponto de partida já na paleta certa e no canvas certo,
pra quem for limpar no Aseprite gastar tempo corrigindo, não desenhando do
zero. Ver Design/GuiasDeArte/pipeline-ia-sprites.md, Etapa 2b, e
Design/GuiasDeArte/style-bible.md#densidade-alvo-referência-castlevania-sotn-blasphemous.

Como funciona (sem numpy, só Pillow):
  1. Blur leve pra reduzir ruído de amostragem antes de reduzir a escala.
  2. Downscale por blocos: cada pixel de saída vem da cor DOMINANTE (não da
     média nem de um pixel aleatório) da região correspondente na origem —
     preserva bordas melhor que resize comum, evita "lavar" o desenho.
  3. Transparência: blocos majoritariamente transparentes na origem viram
     transparentes na saída.
  4. Quantização pra paleta exata do projeto via Image.quantize(palette=...),
     com dithering Floyd-Steinberg opcional (ligado por padrão) pra já
     visualizar as bandas de transição — a style-bible pede dithering
     controlado por material, então trate o resultado como rascunho de
     onde as transições podem ir, não como decisão final.

Uso:
  python pixelize.py concept_raw.png ../../ArteConceitual/Paletas/blumenau.json --size 64x64
  python pixelize.py concept_raw.png paleta.json --size 48x64 --no-dither -o saida.png

Dependência: pip install pillow (mesma do resto do pipeline).
"""
import argparse
import json
import sys
from collections import Counter
from pathlib import Path

from PIL import Image, ImageFilter

BUCKET = 16  # tamanho do balde de cor pra achar a cor dominante por bloco


def parse_size(text: str) -> tuple[int, int]:
    try:
        w, h = text.lower().split("x")
        return int(w), int(h)
    except ValueError:
        raise argparse.ArgumentTypeError(f"formato inválido '{text}', use LARGURAxALTURA (ex.: 64x64)")


def load_palette(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    colors = data["colors"]
    for c in colors:
        hexv = c["hex"].lstrip("#")
        c["_rgb"] = tuple(int(hexv[i : i + 2], 16) for i in (0, 2, 4))
    return data


def dominant_color(pixels: list[tuple[int, int, int]]) -> tuple[int, int, int]:
    """Cor representativa do bloco: agrupa em baldes grosseiros pra achar a
    moda de verdade (pixels de foto/difusão quase nunca repetem exatos), e
    devolve a média dos pixels que caíram no balde vencedor."""
    buckets: Counter = Counter()
    bucket_members: dict[tuple[int, int, int], list[tuple[int, int, int]]] = {}
    for p in pixels:
        key = tuple(c // BUCKET for c in p)
        buckets[key] += 1
        bucket_members.setdefault(key, []).append(p)
    winner = buckets.most_common(1)[0][0]
    members = bucket_members[winner]
    n = len(members)
    return tuple(sum(c[i] for c in members) // n for i in range(3))


def block_downsample(img: Image.Image, target_w: int, target_h: int, alpha_threshold: int = 32) -> Image.Image:
    """Downscale por cor dominante por bloco, preservando transparência."""
    src_w, src_h = img.size
    px = img.load()
    out = Image.new("RGBA", (target_w, target_h))
    out_px = out.load()

    for ty in range(target_h):
        y0 = ty * src_h // target_h
        y1 = max(y0 + 1, (ty + 1) * src_h // target_h)
        for tx in range(target_w):
            x0 = tx * src_w // target_w
            x1 = max(x0 + 1, (tx + 1) * src_w // target_w)

            opaque_pixels = []
            alpha_sum = 0
            count = 0
            for y in range(y0, y1):
                for x in range(x0, x1):
                    r, g, b, a = px[x, y]
                    alpha_sum += a
                    count += 1
                    if a >= alpha_threshold:
                        opaque_pixels.append((r, g, b))

            avg_alpha = alpha_sum // max(count, 1)
            if not opaque_pixels or avg_alpha < alpha_threshold:
                out_px[tx, ty] = (0, 0, 0, 0)
                continue

            r, g, b = dominant_color(opaque_pixels)
            out_px[tx, ty] = (r, g, b, 255)

    return out


def quantize_to_palette(img: Image.Image, colors: list[dict], dither: bool) -> Image.Image:
    """Mapeia as cores opacas de img pra paleta exata do projeto (por hex),
    preservando o canal alpha (o quantize do Pillow não lida com RGBA)."""
    alpha = img.getchannel("A")
    rgb = img.convert("RGB")

    # Preenche os 256 slots do modo P só com cores reais da paleta (repetidas
    # em ciclo) — encher com preto puro faria pixels quase-pretos migrarem
    # pra um preto "fantasma" fora da paleta em vez da cor 1 real do projeto.
    pal_img = Image.new("P", (1, 1))
    flat: list[int] = []
    for i in range(256):
        flat.extend(colors[i % len(colors)]["_rgb"])
    pal_img.putpalette(flat)

    mode = Image.Dither.FLOYDSTEINBERG if dither else Image.Dither.NONE
    quantized = rgb.quantize(palette=pal_img, dither=mode).convert("RGB")

    result = Image.new("RGBA", img.size)
    result.paste(quantized, (0, 0))
    result.putalpha(alpha)
    return result


def report_usage(img: Image.Image, colors: list[dict]) -> None:
    by_hex = {c["_rgb"]: c for c in colors}
    used: Counter = Counter()
    px = img.load()
    w, h = img.size
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if a == 0:
                continue
            used[(r, g, b)] += 1
    print(f"Cores da paleta usadas: {len(used)}/{len(colors)}")
    for rgb, n in used.most_common():
        c = by_hex.get(rgb)
        label = f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"
        if c:
            label += f" (key {c['key']} — {c['role']})"
        print(f"  {n:5d}px  {label}")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("input", type=Path, help="PNG de origem (saída crua de difusão)")
    ap.add_argument("palette", type=Path, help="paleta JSON da região (ex.: blumenau.json)")
    ap.add_argument("--size", required=True, type=parse_size, help="canvas de saída, LARGURAxALTURA (ex.: 64x64)")
    ap.add_argument("-o", "--output", type=Path, default=None, help="padrão: {input}_pixelized.png")
    ap.add_argument("--pre-blur", type=float, default=1.5, help="raio do blur antes do downsample (default 1.5, 0 desliga)")
    dither_group = ap.add_mutually_exclusive_group()
    dither_group.add_argument("--dither", dest="dither", action="store_true", default=True, help="dithering Floyd-Steinberg (default)")
    dither_group.add_argument("--no-dither", dest="dither", action="store_false", help="desliga o dithering")
    args = ap.parse_args()

    target_w, target_h = args.size
    if target_w * target_h < 32 * 32:
        print(f"Aviso: canvas {target_w}x{target_h} é pequeno pra um asset orgânico — "
              f"style-bible.md recomenda mínimo 48x64 pra personagens/criaturas.")

    src = Image.open(args.input).convert("RGBA")
    if args.pre_blur > 0:
        src = src.filter(ImageFilter.GaussianBlur(radius=args.pre_blur))

    downsampled = block_downsample(src, target_w, target_h)
    palette_data = load_palette(args.palette)
    result = quantize_to_palette(downsampled, palette_data["colors"], args.dither)

    out_path = args.output or args.input.with_name(f"{args.input.stem}_pixelized.png")
    result.save(out_path)

    print(f"Origem: {args.input.name} ({src.size[0]}x{src.size[1]}) -> {out_path.name} ({target_w}x{target_h})")
    print(f"Paleta: {palette_data.get('region', args.palette.stem)} ({palette_data.get('status', '?')})")
    print(f"Dithering: {'ligado' if args.dither else 'desligado'}")
    report_usage(result, palette_data["colors"])
    print("\nISTO NÃO É UM SPRITE APROVADO — é ponto de partida pro pixel pass manual "
          "(bandas de sombra, outline, highlight direcional continuam trabalho humano).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
