#!/usr/bin/env python3
"""Amplia um PNG por nearest-neighbor para o ciclo visual de crítica.

Usado no loop gerar -> visualizar -> criticar -> refinar: o agente (ou humano)
inspeciona o sprite ampliado, opcionalmente com grade de pixels, e compara
com as regras da style-bible antes de aprovar.

Uso:
  python upscale_preview.py sprite.png [-s 8] [--grid]

Dependência: pip install pillow
"""
import argparse
from pathlib import Path

from PIL import Image

GRID_COLOR = (255, 0, 255, 90)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("png", type=Path)
    ap.add_argument("-s", "--scale", type=int, default=8, help="Fator de ampliação (default 8)")
    ap.add_argument("--grid", action="store_true", help="Sobrepõe grade de 1px por pixel original")
    args = ap.parse_args()

    img = Image.open(args.png).convert("RGBA")
    big = img.resize((img.width * args.scale, img.height * args.scale), Image.NEAREST)

    if args.grid:
        overlay = Image.new("RGBA", big.size, (0, 0, 0, 0))
        for x in range(0, big.width, args.scale):
            for y in range(big.height):
                overlay.putpixel((x, y), GRID_COLOR)
        for y in range(0, big.height, args.scale):
            for x in range(big.width):
                overlay.putpixel((x, y), GRID_COLOR)
        big = Image.alpha_composite(big, overlay)

    out = args.png.with_name(f"{args.png.stem}_preview{args.scale}x.png")
    big.save(out)
    print(f"OK: {out}")


if __name__ == "__main__":
    main()
