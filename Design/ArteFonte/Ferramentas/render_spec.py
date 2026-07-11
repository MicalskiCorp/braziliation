#!/usr/bin/env python3
"""Renderiza uma spec JSON de sprite (matriz de caracteres + paleta) em PNG.

A spec é a "fonte" versionável do sprite (Opção A do pipeline programático).
Formato da spec:

{
  "name": "prop_blumenau_floodgate_lever",
  "size": [32, 32],
  "palette": "../../ArteConceitual/Paletas/blumenau.json",
  "rows": [
    "................",
    "......77........",
    ...  // 1 char por pixel; '.' = transparente; chars = key da paleta
  ]
}

Uso:
  python render_spec.py spec.json [-o saida.png]

Dependência: pip install pillow
"""
import argparse
import json
import sys
from pathlib import Path

from PIL import Image


def hex_to_rgba(h: str) -> tuple:
    h = h.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), 255)


def load_palette(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    return {c["key"]: hex_to_rgba(c["hex"]) for c in data["colors"]}


def render(spec_path: Path, out_path: Path | None) -> Path:
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    width, height = spec["size"]
    palette_path = (spec_path.parent / spec["palette"]).resolve()
    palette = load_palette(palette_path)

    rows = spec["rows"]
    if len(rows) != height:
        sys.exit(f"ERRO: spec declara altura {height} mas tem {len(rows)} linhas em 'rows'.")

    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    px = img.load()
    for y, row in enumerate(rows):
        if len(row) != width:
            sys.exit(f"ERRO: linha {y} tem {len(row)} chars; esperado {width}.")
        for x, ch in enumerate(row):
            if ch == ".":
                continue
            if ch not in palette:
                sys.exit(f"ERRO: char '{ch}' em ({x},{y}) não existe na paleta {palette_path.name}.")
            px[x, y] = palette[ch]

    out = out_path or spec_path.with_suffix(".png")
    img.save(out)
    used = {ch for row in rows for ch in row if ch != "."}
    print(f"OK: {out} ({width}x{height}, {len(used)} cores da paleta {palette_path.stem})")
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("spec", type=Path, help="Caminho da spec JSON")
    ap.add_argument("-o", "--out", type=Path, default=None, help="PNG de saída (default: mesmo nome da spec)")
    args = ap.parse_args()
    render(args.spec, args.out)
