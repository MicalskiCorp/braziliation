"""Fundos de preview: o que as ferramentas desenham atrás de um efeito. Sheets ficam transparentes.

Port de `src/core/scene.js` do PixelFX (MIT). Para leitura no jogo de verdade use o
`mock_scene.py` (960×540, paleta regional) — estes fundos são só para a crítica.
"""
from __future__ import annotations

import math

from .cor import hex, mix
from .matematica import rand

SKY, SKY_TOP, SKY_LOW = hex("#15131d"), hex("#0d0b14"), hex("#221d33")
FLOOR_EDGE, FLOOR, FLOOR_DARK, MORTAR = hex("#4a4263"), hex("#2b2639"), hex("#211d2d"), hex("#1a1724")
BAYER = [0, 8, 2, 10, 12, 4, 14, 6, 3, 11, 1, 9, 15, 7, 13, 5]
BACKDROPS = ["dark", "ground", "sky", "light", "black"]


def backdrop(kind, w, h, groundY=None):
    """Fundo como lista de w × h cores. kind: dark | ground (piso de pedra de groundY para baixo) | sky | light | black."""
    if groundY is None:
        groundY = h
    if kind == "light":
        return [hex("#ebe8f0")] * (w * h)
    if kind == "black":
        return [hex("#000000")] * (w * h)
    out = [0] * (w * h)
    estrela = hex("#cfc8ff")
    for y in range(h):
        for x in range(w):
            c = SKY
            if kind == "sky":
                t = y / max(1, h - 1)
                step = int(t * 5 + BAYER[((y & 3) << 2) | (x & 3)] / 16)
                c = mix(SKY_TOP, SKY_LOW, min(1, step / 4))
                r = rand(x, y, 77)
                if r > 0.994:
                    c = mix(c, estrela, 0.35 + (r - 0.994) * 90)
            if kind == "ground" and y >= groundY:
                gy = y - groundY
                if gy == 0:
                    c = FLOOR_EDGE
                else:
                    row = math.floor((gy - 1) / 5)
                    off = 6 if row % 2 else 0
                    mortar = (gy - 1) % 5 == 4 or (x + off) % 12 == 0
                    c = MORTAR if mortar else FLOOR if gy < 3 else FLOOR_DARK
            out[y * w + x] = c
    return out
