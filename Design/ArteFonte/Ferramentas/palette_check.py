#!/usr/bin/env python3
"""Valida um PNG contra uma paleta oficial do projeto.

Verifica: (1) toda cor opaca do PNG pertence à paleta; (2) o total de cores
não excede o limite do art direction (máx. 16 por sprite).

Uso:
  python palette_check.py sprite.png ../../ArteConceitual/Paletas/blumenau.json

Sai com código 0 se aprovado, 1 se reprovado (usável em CI/skill).
Dependência: pip install pillow
"""
import argparse
import json
import sys
from pathlib import Path

from PIL import Image


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("png", type=Path)
    ap.add_argument("palette", type=Path)
    args = ap.parse_args()

    data = json.loads(args.palette.read_text(encoding="utf-8"))
    allowed = {c["hex"].lstrip("#").lower() for c in data["colors"]}
    max_colors = int(data.get("max_colors_per_sprite", 16))

    img = Image.open(args.png).convert("RGBA")
    found: set[str] = set()
    strays: set[str] = set()
    for r, g, b, a in (img.getpixel((x, y)) for y in range(img.height) for x in range(img.width)):
        if a == 0:
            continue
        if a != 255:
            strays.add(f"alpha parcial ({a})")
            continue
        h = f"{r:02x}{g:02x}{b:02x}"
        found.add(h)
        if h not in allowed:
            strays.add(f"#{h}")

    ok = not strays and len(found) <= max_colors
    print(f"Sprite: {args.png.name} | Paleta: {data.get('region', args.palette.stem)}")
    print(f"Cores opacas usadas: {len(found)}/{max_colors}")
    if strays:
        print("REPROVADO — cores fora da paleta / alpha parcial:")
        for s in sorted(strays):
            print(f"  - {s}")
    elif len(found) > max_colors:
        print(f"REPROVADO — excede o limite de {max_colors} cores.")
    else:
        print("APROVADO — todas as cores pertencem à paleta.")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
