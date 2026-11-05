"""Tocha de parede num suporte de ferro: chama lambendo um enrolado de pano com piche,
lambidas e puffs soltos das pontas, fumaça, brasas e luz tremulando na parede.

Port de `src/fx/fire/torch.js` do PixelFX (MIT). A receita de língua, lambida, puff,
fumaça e brasa adapta o fogo open-source do Sprite Fusion
(https://www.spritefusion.com/pixel-art-vfx/fire), MIT License, Copyright (c) 2026 Hugo Duprez.
"""
from __future__ import annotations

import math

from ... import clamp, fit, jsround, mix, rand
from ._lib import burn, hotFirst, noiseFor

meta = {
    "name": "Torch",
    "desc": "A wall torch on an iron bracket: a licking flame leaping off a pitch-soaked wrap, licks and puffs "
            "torn off its tips, smoke, embers, a flickering light on the wall.",
    "tags": ["fire", "torch", "prop", "light", "wall", "dungeon", "loop"],
    "size": [72, 120],
    "origin": [36, 94],
    "duration": 2,
    "loop": True,
    "fps": 30,
    "bg": "dark",
    "options": {
        "palette": ["#4a1712", "#8a1f17", "#c9281f", "#f2561d", "#ff8a2a", "#ffc23d", "#ffe26b", "#fff3a6", "#ffffff"],
        "wood": ["#0e080a", "#24130f", "#3b2216", "#5a3520", "#8a5a34", "#b9884f"],
        "iron": ["#0d0b12", "#1e1b26", "#363242", "#5b5566", "#8a8396"],
        "seed": 4,
    },
}

D = meta["duration"]
NL = noiseFor(D)
BASE = -16
# a chama: [x, y a partir do topo do enrolado, fração de altura, meia largura, fileira de trás?]
TONGUES = [
    [-1.9, -1, 0.74, 2.0, 1],
    [2.1, -1, 0.7, 2.0, 1],
    [-3.4, 0.5, 0.42, 1.6, 0],
    [3.6, 0.5, 0.46, 1.6, 0],
    [0, 0, 1, 2.9, 0],
]


def plate(p, I, H, fl):
    """O suporte: placa de ferro chanfrada na parede com dois rebites."""
    def fn(x, y, _o):
        if x < -5 or x > 5 or y < -5 or y > 11:
            return I[0]
        rv = abs(x) < 0.6 and (abs(y + 3.5) < 0.6 or abs(y - 9.5) < 0.6)
        if rv:
            return mix(I[4], H[3], 0.35 * fl)
        if y < -4 or x < -4:
            return mix(I[3], H[4], 0.3 * fl)
        if y > 10 or x > 4:
            return I[1]
        return I[2] if y < 2 else I[1]

    p.shade(-5.5, -5.5, 5.5, 11.5, fn)


def handle(p, W):
    def fn(x, y, _o):
        half = 1.3 + clamp((14 - y) / 26) * 0.9
        if abs(x) > half + 0.5 or y > 14.5:
            return None
        if abs(x) > half - 0.5 or y > 13.5:
            return W[0]
        g = rand(math.floor(y / 3), jsround(x), 9)
        return (W[2] if g < 0.3 else W[4]) if x < -0.3 else (W[1] if g < 0.4 else W[2])

    p.shade(-3, -12, 3, 15, fn)


def ring(p, I, H, fl):
    p.rect(-3, -2, 7, 4, I[0])
    p.rect(-2, -1, 5, 1, mix(I[4], H[3], 0.3 * fl))
    p.rect(-2, 0, 5, 1, I[2])


def wrap_(p, W, I, H, t):
    """A cabeça: trapos amarrados com corda e encharcados de piche, queimados onde arde."""
    def fn(x, y, out):
        v = (y - (BASE - 1.5)) / 7.5
        half = 4.6 - v * 1.9
        if abs(x) > half + 0.5 or y < BASE - 1.5 or y > -9.5:
            return None
        if abs(x) > half - 0.5 or y > -10.5:
            return W[0]
        cord = math.floor(y - x * 0.6 + 40) % 3 == 0
        h = rand(math.floor(x), math.floor(y), 31)
        if v < 0.45:
            if h < 0.42:
                g = 0.5 + 0.5 * math.sin((t / D) * math.pi * 4 + h * 40)
                out.k = 0.3 * g
                return H[2] if g > 0.66 else H[4] if g > 0.33 else H[5]
            return W[0] if h < 0.75 else W[1]
        if cord:
            return I[2]
        return W[3] if x < -1 else W[2] if x < 1.5 else W[1]

    p.shade(-6, BASE - 2, 6, -9, fn)


def draw(p, t, o):
    F = fit(o.palette, 9)
    H = hotFirst(F)
    W = fit(o.wood, 6)
    I = fit(o.iron, 5)
    S = o.seed
    fl0 = 0.74 + 0.16 * NL(t, 7.3, S + 1) + 0.1 * NL(t, 19, S + 2)
    plate(p, I, H, fl0)
    handle(p, W)
    ring(p, I, H, fl0)
    burn(p, t, TONGUES, {
        "H": H, "D": D, "NL": NL, "S": S, "x": 0, "y": BASE, "height": 20, "lean": 0.12, "spread": 4,
        "puffs": 10, "licks": 5, "smoke": 7, "smokeSize": 2.3, "smokeLife": [1.3, 2.1], "embers": 7, "glowR": 48,
        "glow": 1.25, "wind": 2,
        "mid": lambda fl: wrap_(p, W, I, H, t),
    })
