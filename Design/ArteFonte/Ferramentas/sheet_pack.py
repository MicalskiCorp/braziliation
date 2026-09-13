#!/usr/bin/env python3
"""Empacota frames PNG em um spritesheet horizontal.

Todos os frames devem ter o mesmo tamanho (canvas estável entre frames,
conforme animation-guide.md). A ordem dos argumentos define a ordem no sheet.

Uso:
  python sheet_pack.py -o sheet.png frame1.png frame2.png frame3.png

Dependência: pip install pillow
"""
import argparse
import sys
from pathlib import Path

from PIL import Image


def pack_horizontal(imgs: list[Image.Image]) -> Image.Image:
    """Empacota imagens (mesmo tamanho) lado a lado. Usado pela CLI e por render_spec.py
    ao empacotar as 'sheets' declaradas numa spec consolidada."""
    w, h = imgs[0].size
    for img in imgs:
        if img.size != (w, h):
            raise ValueError(f"frame tem {img.size}, esperado {(w, h)} — canvas deve ser estável entre frames.")
    sheet = Image.new("RGBA", (w * len(imgs), h), (0, 0, 0, 0))
    for i, img in enumerate(imgs):
        sheet.alpha_composite(img, (i * w, 0))
    return sheet


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("frames", type=Path, nargs="+", help="PNGs dos frames, na ordem da animação")
    ap.add_argument("-o", "--out", type=Path, required=True, help="PNG do spritesheet de saída")
    args = ap.parse_args()

    imgs = [Image.open(f).convert("RGBA") for f in args.frames]
    try:
        sheet = pack_horizontal(imgs)
    except ValueError as e:
        sys.exit(f"ERRO: {e}")
    sheet.save(args.out)
    print(f"OK: {args.out} ({len(imgs)} frames de {imgs[0].width}x{imgs[0].height} -> {sheet.width}x{sheet.height})")


if __name__ == "__main__":
    main()
