#!/usr/bin/env python3
"""Converte a paleta JSON da regiao numa imagem de amostras (swatch).

Existe porque varios nos do ComfyUI (DNFReferencePaletteFinalize, DNFSpatialChromaLock)
recebem a paleta como IMAGEM de referencia, nao como JSON. Este script e a ponte entre
a fonte de verdade do projeto (`ArteConceitual/Paletas/*.json`) e o que esses nos leem.

Cada cor vira um bloco quadrado. O tamanho do bloco nao importa para o algoritmo, que so
amostra as cores presentes -- importa apenas que TODAS as cores da paleta aparecam e que
nenhuma cor de fora entre.

Uso:
  py palette_swatch.py ../../ArteConceitual/Paletas/blumenau.json -o blumenau_swatch.png
  py palette_swatch.py ../../ArteConceitual/Paletas/blumenau.json --cell 16 --columns 8 -o s.png

Dependencia: pip install pillow
"""
import argparse
import json
from pathlib import Path

from PIL import Image


def hex_to_rgb(h: str) -> tuple:
    h = h.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("palette", type=Path)
    ap.add_argument("--cell", type=int, default=16, help="Lado do bloco de cada cor em px (default 16)")
    ap.add_argument("--columns", type=int, default=8, help="Blocos por linha (default 8)")
    ap.add_argument("-o", "--out", type=Path, required=True)
    args = ap.parse_args()

    data = json.loads(args.palette.read_text(encoding="utf-8"))
    colors = [hex_to_rgb(c["hex"]) for c in data["colors"]]

    cols = min(args.columns, len(colors))
    rows = -(-len(colors) // cols)  # divisao para cima
    img = Image.new("RGB", (cols * args.cell, rows * args.cell))

    for i, rgb in enumerate(colors):
        x, y = (i % cols) * args.cell, (i // cols) * args.cell
        img.paste(Image.new("RGB", (args.cell, args.cell), rgb), (x, y))

    args.out.parent.mkdir(parents=True, exist_ok=True)
    img.save(args.out)
    print(f"OK: {args.out} — {len(colors)} cores de '{data.get('region', args.palette.stem)}' "
          f"em {cols}x{rows} blocos de {args.cell}px")


if __name__ == "__main__":
    main()
