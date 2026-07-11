#!/usr/bin/env python3
"""Compõe um sprite numa cena mock 320x180 para o teste de leitura em 1x.

Implementa o passo "Validar em cena" do pipeline: o sprite precisa ler
claramente na resolução de referência do jogo (320x180, 16 PPU), sobre
faixas de valor que simulam céu/fundo/meio/chão da paleta da região.

Gera dois arquivos: {nome}_mock.png (320x180 real) e {nome}_mock_3x.png
(ampliado para inspeção visual).

Uso:
  python mock_scene.py sprite.png ../../ArteConceitual/Paletas/blumenau.json [-y CHAO]

Dependência: pip install pillow
"""
import argparse
import json
from pathlib import Path

from PIL import Image

REF_W, REF_H = 320, 180


def hex_to_rgba(h: str) -> tuple:
    h = h.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), 255)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("png", type=Path)
    ap.add_argument("palette", type=Path)
    ap.add_argument("-y", "--ground", type=int, default=140, help="Linha do chão em px (default 140)")
    args = ap.parse_args()

    data = json.loads(args.palette.read_text(encoding="utf-8"))
    colors = {c["key"]: hex_to_rgba(c["hex"]) for c in data["colors"]}

    # Faixas de valor típicas: céu (sombra petróleo), fundo (grafite),
    # meio (madeira escura) e chão (verde acinzentado de lama).
    scene = Image.new("RGBA", (REF_W, REF_H), colors.get("2", (35, 44, 51, 255)))
    for y in range(60, args.ground):
        for x in range(REF_W):
            scene.putpixel((x, y), colors.get("3", (58, 63, 68, 255)))
    for y in range(args.ground, REF_H):
        for x in range(REF_W):
            scene.putpixel((x, y), colors.get("E", (90, 107, 82, 255)))

    sprite = Image.open(args.png).convert("RGBA")
    pos = ((REF_W - sprite.width) // 2, args.ground - sprite.height)
    scene.alpha_composite(sprite, pos)

    out_1x = args.png.with_name(args.png.stem + "_mock.png")
    out_3x = args.png.with_name(args.png.stem + "_mock_3x.png")
    scene.save(out_1x)
    scene.resize((REF_W * 3, REF_H * 3), Image.NEAREST).save(out_3x)
    print(f"OK: {out_1x} (320x180 real) e {out_3x} (3x para inspeção)")


if __name__ == "__main__":
    main()
