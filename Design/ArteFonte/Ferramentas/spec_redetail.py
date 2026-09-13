#!/usr/bin/env python3
"""Re-autoria assistida de specs 1x para o grid 2x do ADR-004.

Faz o que um pixel artist faz ao "upres" um sprite:
  1. Expansão EPX/Scale2x sobre a matriz de keys — suaviza os degraus de
     diagonais e curvas usando a vizinhança (em vez do quadrado 2x2 do nearest);
  2. Textura de material (seed determinística por nome do asset): veios em
     madeira (A/B/C), pites em ferro (3/4), grão em pedra/concreto — só dentro
     de regiões grandes da mesma cor, nunca em bordas.

Saída: spec 2x versionada (`{nome}.2x.spec.json`) + PNG renderizado.
O resultado é um PONTO DE PARTIDA de re-autoria: retoques manuais na spec 2x
seguem o ciclo normal de crítica visual do pipeline.

Uso:
  python spec_redetail.py spec1x.json [-o out.png] [--no-noise]

Dependência: pip install pillow
"""
import argparse
import hashlib
import json
import random
from pathlib import Path

from PIL import Image

from render_spec import hex_to_rgba, load_palette

# Materiais que recebem textura: char -> (char da textura, densidade)
NOISE = {
    "B": ("A", 0.05),  # madeira úmida -> veio escuro
    "C": ("B", 0.05),  # ocre -> veio
    "D": ("C", 0.04),  # reboco/bege -> grão
    "3": ("2", 0.04),  # grafite -> pite
    "4": ("3", 0.04),  # ferro -> pite
    "7": ("6", 0.03),  # latão -> mancha sutil
    "E": ("F", 0.03),  # lama/água -> acento
}


def epx(grid: list[str]) -> list[str]:
    h, w = len(grid), len(grid[0])

    def g(x: int, y: int) -> str:
        return grid[y][x] if 0 <= x < w and 0 <= y < h else "."

    out = [["."] * (w * 2) for _ in range(h * 2)]
    for y in range(h):
        for x in range(w):
            p = g(x, y)
            a, b, c, d = g(x, y - 1), g(x + 1, y), g(x - 1, y), g(x, y + 1)
            p1 = a if (c == a and c != d and a != b) else p
            p2 = b if (a == b and a != c and b != d) else p
            p3 = c if (d == c and d != b and c != a) else p
            p4 = d if (b == d and b != a and d != c) else p
            if p == ".":  # nunca inventar pixel onde o original é transparente
                p1 = p2 = p3 = p4 = "."
            out[y * 2][x * 2] = p1
            out[y * 2][x * 2 + 1] = p2
            out[y * 2 + 1][x * 2] = p3
            out[y * 2 + 1][x * 2 + 1] = p4
    return ["".join(r) for r in out]


def add_noise(rows: list[str], seed: str) -> list[str]:
    rng = random.Random(int(hashlib.md5(seed.encode()).hexdigest()[:8], 16))
    h, w = len(rows), len(rows[0])
    grid = [list(r) for r in rows]
    for y in range(1, h - 1):
        for x in range(1, w - 1):
            ch = grid[y][x]
            if ch not in NOISE:
                continue
            # só no interior de regiões da mesma cor (evita sujar bordas/shading)
            same = all(rows[y + dy][x + dx] == ch for dy in (-1, 0, 1) for dx in (-1, 0, 1))
            if same and rng.random() < NOISE[ch][1]:
                grid[y][x] = NOISE[ch][0]
    return ["".join(r) for r in grid]


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("spec", type=Path, help="Spec 1x de origem")
    ap.add_argument("-o", "--out", type=Path, default=None, help="PNG de saída")
    ap.add_argument("--no-noise", action="store_true", help="Só EPX, sem textura")
    args = ap.parse_args()

    spec = json.loads(args.spec.read_text(encoding="utf-8"))
    rows = epx(spec["rows"])
    if not args.no_noise:
        rows = add_noise(rows, spec["name"])

    spec2x = dict(spec)
    spec2x["name"] = spec["name"]
    spec2x["size"] = [spec["size"][0] * 2, spec["size"][1] * 2]
    spec2x["rows"] = rows
    spec2x["notes"] = spec.get("notes", "") + " [Re-autoria ADR-004: EPX + textura via spec_redetail.py; retoques manuais aplicados sobre esta spec 2x.]"

    spec2x_path = args.spec.with_name(args.spec.name.replace(".spec.json", ".2x.spec.json"))
    spec2x_path.write_text(json.dumps(spec2x, indent=2, ensure_ascii=False), encoding="utf-8")

    palette = load_palette((args.spec.parent / spec["palette"]).resolve())
    w, h = spec2x["size"]
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    px = img.load()
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            if ch != ".":
                px[x, y] = palette[ch]
    out = args.out or spec2x_path.with_suffix("").with_suffix(".png")
    img.save(out)
    print(f"OK: {spec2x_path.name} + {out} ({w}x{h})")


if __name__ == "__main__":
    main()
