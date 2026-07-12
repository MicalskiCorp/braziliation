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


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("frames", type=Path, nargs="+", help="PNGs dos frames, na ordem da animação")
    ap.add_argument("-o", "--out", type=Path, required=True, help="PNG do spritesheet de saída")
    args = ap.parse_args()

    imgs = [Image.open(f).convert("RGBA") for f in args.frames]
    w, h = imgs[0].size
    for f, img in zip(args.frames, imgs):
        if img.size != (w, h):
            sys.exit(f"ERRO: {f.name} tem {img.size}, esperado {(w, h)} — canvas deve ser estável entre frames.")

    sheet = Image.new("RGBA", (w * len(imgs), h), (0, 0, 0, 0))
    for i, img in enumerate(imgs):
        sheet.alpha_composite(img, (i * w, 0))
    sheet.save(args.out)
    print(f"OK: {args.out} ({len(imgs)} frames de {w}x{h} -> {sheet.width}x{sheet.height})")


if __name__ == "__main__":
    main()
