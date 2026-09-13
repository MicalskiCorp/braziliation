#!/usr/bin/env python3
"""Gerador procedural de tilesets 16x16 (Opção B do pipeline programático).

Gera famílias de tiles parametrizadas pela paleta JSON da região, com seed
determinística (mesma seed + paleta = mesmo tileset, sempre). Saída: PNG em
grade (linhas = tipos de tile, colunas = variações) + manifest JSON com
seed/paleta/tipos, satisfazendo o registro exigido pelo pipeline.

Famílias disponíveis:
  enxaimel — parede Fachwerk: reboco claro + vigas de madeira + marca de umidade
  metal    — chapas de ferro clockpunk: bisel, rebites, ferrugem, emendas
  agua     — superfície d'água, lama e parede com marca de nível de enchente

Uso:
  python gen_tileset.py enxaimel --palette ../../ArteConceitual/Paletas/blumenau.json --seed 42 -o out.png

Dependência: pip install pillow
"""
import argparse
import json
import random
from pathlib import Path

from PIL import Image

from spec_redetail import add_noise, epx

TILE = 16


def hex_to_rgba(h: str) -> tuple:
    h = h.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), 255)


def load_palette(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    return {c["key"]: hex_to_rgba(c["hex"]) for c in data["colors"]}


def blank(fill: str) -> list:
    return [[fill] * TILE for _ in range(TILE)]


def speckle(grid: list, rng: random.Random, color: str, density: float, y0: int = 0, y1: int = TILE) -> None:
    for y in range(y0, y1):
        for x in range(TILE):
            if rng.random() < density:
                grid[y][x] = color


def blob(grid: list, rng: random.Random, color: str, cx: int, cy: int, size: int) -> None:
    for _ in range(size):
        x = min(TILE - 1, max(0, cx + rng.randint(-2, 2)))
        y = min(TILE - 1, max(0, cy + rng.randint(-1, 1)))
        grid[y][x] = color


# ---------------------------------------------------------------- enxaimel

def enxaimel_panel(rng: random.Random) -> list:
    g = blank("D")
    speckle(g, rng, "C", 0.08)
    if rng.random() < 0.5:
        blob(g, rng, "E", rng.randint(3, 12), rng.randint(12, 15), rng.randint(3, 7))
    return g


def enxaimel_beam_v(rng: random.Random) -> list:
    g = enxaimel_panel(rng)
    for y in range(TILE):
        g[y][0] = "A"
        g[y][1] = "B"
        g[y][2] = "A" if rng.random() < 0.2 else "B"
        g[y][3] = "1"
    return g


def enxaimel_beam_h(rng: random.Random) -> list:
    g = enxaimel_panel(rng)
    for x in range(TILE):
        g[0][x] = "A"
        g[1][x] = "B"
        g[2][x] = "B" if rng.random() < 0.8 else "C"
        g[3][x] = "1"
    return g


def enxaimel_diag(rng: random.Random) -> list:
    g = enxaimel_panel(rng)
    for i in range(TILE):
        g[i][i] = "B"
        if i + 1 < TILE:
            g[i][i + 1] = "B"
            g[i + 1][i] = "A"
    return g


# ------------------------------------------------------------------- metal

def metal_plate(rng: random.Random) -> list:
    g = blank("3")
    for i in range(TILE):
        g[0][i] = "4"
        g[i][0] = "4"
        g[TILE - 1][i] = "1"
        g[i][TILE - 1] = "1"
    for cx, cy in ((2, 2), (13, 2), (2, 13), (13, 13)):
        g[cy][cx] = "5"
        g[cy + 1 if cy < 13 else cy][cx] = "2" if cy < 13 else g[cy][cx]
    speckle(g, rng, "2", 0.05, 1, TILE - 1)
    return g


def metal_rusty(rng: random.Random) -> list:
    g = metal_plate(rng)
    for _ in range(rng.randint(2, 4)):
        blob(g, rng, "9", rng.randint(2, 13), rng.randint(2, 13), rng.randint(4, 9))
    speckle(g, rng, "6", 0.04, 2, TILE - 2)
    return g


def metal_seams(rng: random.Random) -> list:
    g = blank("3")
    ys = sorted(rng.sample(range(2, TILE - 2), 2))
    for x in range(TILE):
        g[0][x] = "4"
        g[TILE - 1][x] = "1"
        for y in ys:
            g[y][x] = "2"
            g[y - 1][x] = "4" if rng.random() < 0.7 else "3"
    speckle(g, rng, "2", 0.05, 1, TILE - 1)
    return g


# -------------------------------------------------------------------- agua

def agua_superficie(rng: random.Random) -> list:
    g = blank("E")
    for band in range(3):
        y = 2 + band * 5 + rng.randint(0, 2)
        x0 = rng.randint(0, 6)
        for x in range(x0, min(TILE, x0 + rng.randint(5, 10))):
            g[y][x] = "2"
            if rng.random() < 0.3 and y > 0:
                g[y - 1][x] = "F"
    speckle(g, rng, "2", 0.04)
    return g


def agua_lama(rng: random.Random) -> list:
    g = blank("B")
    speckle(g, rng, "A", 0.15)
    speckle(g, rng, "F", 0.06)
    for _ in range(rng.randint(1, 3)):
        blob(g, rng, "E", rng.randint(2, 13), rng.randint(2, 13), rng.randint(3, 6))
    return g


def agua_marca_nivel(rng: random.Random) -> list:
    g = blank("D")
    speckle(g, rng, "C", 0.08)
    nivel = rng.randint(5, 8)
    for x in range(TILE):
        g[nivel][x] = "F" if rng.random() < 0.4 else "E"
        for y in range(nivel + 1, TILE):
            g[y][x] = "E" if rng.random() < 0.25 or y == nivel + 1 else ("B" if y > 11 else "C")
    return g


FAMILIES = {
    "enxaimel": [("panel", enxaimel_panel), ("beam_v", enxaimel_beam_v), ("beam_h", enxaimel_beam_h), ("diag", enxaimel_diag)],
    "metal": [("plate", metal_plate), ("rusty", metal_rusty), ("seams", metal_seams)],
    "agua": [("superficie", agua_superficie), ("lama", agua_lama), ("marca_nivel", agua_marca_nivel)],
}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("familia", choices=sorted(FAMILIES))
    ap.add_argument("--palette", type=Path, required=True)
    ap.add_argument("--seed", type=int, required=True, help="Seed determinística (registrada no manifest)")
    ap.add_argument("--variations", type=int, default=4, help="Variações por tipo de tile (default 4)")
    ap.add_argument("--scale", type=int, default=2, help="Upscale nearest do sheet final (default 2: desenho 16px -> tile 32px do ADR-004; usar 1 para saída nativa 16)")
    ap.add_argument("-o", "--out", type=Path, required=True)
    args = ap.parse_args()

    palette = load_palette(args.palette)
    rng = random.Random(args.seed)
    types = FAMILIES[args.familia]

    out_tile = TILE * args.scale
    sheet = Image.new("RGBA", (out_tile * args.variations, out_tile * len(types)), (0, 0, 0, 0))
    for row, (_, fn) in enumerate(types):
        for col in range(args.variations):
            grid = ["".join(r) for r in fn(rng)]
            if args.scale == 2:
                # Detail pass ADR-004: EPX (curvas) + textura fina no grid 32.
                # Tiles são opacos e seamless: onde o EPX vaza '.' na borda
                # (vizinho fora do tile), cai no nearest do pixel original.
                smooth = epx(grid)
                nearest = ["".join(ch * 2 for ch in r) for r in grid for _ in (0, 1)]
                merged = ["".join(s if s != "." else n for s, n in zip(sr, nr)) for sr, nr in zip(smooth, nearest)]
                grid = add_noise(merged, f"{args.familia}-{args.seed}-{row}-{col}")
            elif args.scale > 2:
                grid = [ "".join(ch * args.scale for ch in r) for r in grid for _ in range(args.scale) ]
            for y in range(len(grid)):
                for x in range(len(grid[0])):
                    sheet.putpixel((col * out_tile + x, row * out_tile + y), palette[grid[y][x]])
    sheet.save(args.out)

    manifest = {
        "generator": "gen_tileset.py",
        "familia": args.familia,
        "seed": args.seed,
        "variations": args.variations,
        "palette": str(args.palette),
        "tile_size": TILE * args.scale,
        "draw_size": TILE,
        "scale": args.scale,
        "rows": [name for name, _ in types],
        "layout": "linhas = tipos, colunas = variações",
    }
    manifest_path = args.out.with_suffix(".manifest.json")
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"OK: {args.out} ({len(types)} tipos x {args.variations} variações, seed {args.seed}) + {manifest_path.name}")


if __name__ == "__main__":
    main()
