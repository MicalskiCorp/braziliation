#!/usr/bin/env python3
"""Re-autoria assistida de specs 1x para o grid 2x (ADR-004) ou 3x (ADR-011).

Faz o que um pixel artist faz ao "upres" um sprite:
  1. Expansão EPX/Scale2x (--scale 2) ou Scale3x (--scale 3) sobre a matriz de
     keys — suavizam os degraus de diagonais e curvas usando a vizinhança, em vez
     do bloco cego do nearest;
  2. Textura de material (seed determinística por nome do asset): veios em
     madeira (A/B/C), pites em ferro (3/4), grão em pedra/concreto — só dentro
     de regiões grandes da mesma cor, nunca em bordas.

Saída: spec versionada (`{nome}.2x.spec.json` ou `{nome}.3x.spec.json`) + PNG.
O resultado é um PONTO DE PARTIDA de re-autoria: retoques manuais na spec nova
seguem o ciclo normal de crítica visual do pipeline.

Por que 3x resolve a migração do ADR-011: o grid foi de 32 para 48 PPU, fator 1,5,
que não é escala inteira. Mas as specs **1x** continuam versionadas, e quase todas
nasceram no grid 16 — e 16x3 = 48 é exato. Então a migração não passa por 1,5:
ela refaz a expansão a partir do 1x, com Scale3x no lugar do Scale2x.

Uso:
  python spec_redetail.py spec1x.json [--scale 3] [-o out.png] [--no-noise]

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


def scale3x(grid: list[str]) -> list[str]:
    """Scale3x — o irmão x3 do EPX. Mesma ideia: o pixel do meio só é trocado
    quando a vizinhança indica uma diagonal, então curva vira curva em vez de
    degrau, e nada é inventado onde o original é transparente."""
    h, w = len(grid), len(grid[0])

    def g(x: int, y: int) -> str:
        return grid[y][x] if 0 <= x < w and 0 <= y < h else "."

    out = [["."] * (w * 3) for _ in range(h * 3)]
    for y in range(h):
        for x in range(w):
            e = g(x, y)
            a, b, c = g(x - 1, y - 1), g(x, y - 1), g(x + 1, y - 1)
            d, f = g(x - 1, y), g(x + 1, y)
            gg, hh, i = g(x - 1, y + 1), g(x, y + 1), g(x + 1, y + 1)
            if b != hh and d != f:
                e1 = d if d == b else e
                e2 = b if (d == b and e != c) or (b == f and e != a) else e
                e3 = f if f == b else e
                e4 = d if (d == b and e != gg) or (d == hh and e != a) else e
                e5 = e
                e6 = f if (b == f and e != i) or (hh == f and e != c) else e
                e7 = d if d == hh else e
                e8 = hh if (d == hh and e != i) or (hh == f and e != gg) else e
                e9 = f if f == hh else e
            else:
                e1 = e2 = e3 = e4 = e5 = e6 = e7 = e8 = e9 = e
            if e == ".":
                e1 = e2 = e3 = e4 = e5 = e6 = e7 = e8 = e9 = "."
            for j, v in enumerate((e1, e2, e3, e4, e5, e6, e7, e8, e9)):
                out[y * 3 + j // 3][x * 3 + j % 3] = v
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
    ap.add_argument("--no-noise", action="store_true", help="Só a expansão, sem textura")
    ap.add_argument("--scale", type=int, choices=(2, 3), default=2,
                    help="2 = EPX/Scale2x (grid do ADR-004) · 3 = Scale3x (grid 48 do ADR-011)")
    args = ap.parse_args()

    spec = json.loads(args.spec.read_text(encoding="utf-8"))
    rows = epx(spec["rows"]) if args.scale == 2 else scale3x(spec["rows"])
    if not args.no_noise:
        rows = add_noise(rows, spec["name"])

    n = args.scale
    adr = "ADR-004" if n == 2 else "ADR-011"
    algoritmo = "EPX/Scale2x" if n == 2 else "Scale3x"
    spec2x = dict(spec)
    spec2x["name"] = spec["name"]
    spec2x["size"] = [spec["size"][0] * n, spec["size"][1] * n]
    spec2x["rows"] = rows
    spec2x["notes"] = (spec.get("notes", "") +
                       f" [Re-autoria {adr}: {algoritmo} + textura via spec_redetail.py;"
                       f" retoques manuais aplicados sobre esta spec {n}x.]")

    spec2x_path = args.spec.with_name(args.spec.name.replace(".spec.json", f".{n}x.spec.json"))
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
