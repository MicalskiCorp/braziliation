"""Cores como inteiros de 32 bits (R no byte baixo, como ImageData) e rampas.

Port de `src/core/color.js` do PixelFX (MIT). Toda cor aqui é um uint32
0xAABBGGRR não negativo — o JS guarda int32 com sinal, mas os bits são os mesmos.

Acréscimo do Braziliation: `rampa_regional()` monta rampas a partir da paleta
JSON da região, para que um efeito recolorido nunca saia da paleta aprovada.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

from .matematica import clamp, M32


def rgb(r, g, b) -> int:
    return (0xFF000000 | ((int(b) & 255) << 16) | ((int(g) & 255) << 8) | (int(r) & 255)) & M32


def red(c):
    return c & 255


def green(c):
    return (c >> 8) & 255


def blue(c):
    return (c >> 16) & 255


def alpha(c):
    return (c >> 24) & 255


def hex(h) -> int:  # noqa: A001 — espelha o original
    """'#rgb' ou '#rrggbb' (ou um número de cor, devolvido como está) para cor."""
    if isinstance(h, int):
        return h & M32
    s = h.replace("#", "")
    if len(s) == 3:
        s = s[0] * 2 + s[1] * 2 + s[2] * 2
    v = int(s[:6], 16)
    return rgb((v >> 16) & 255, (v >> 8) & 255, v & 255)


def toHex(c) -> str:
    return "#" + "".join(f"{v:02x}" for v in (red(c), green(c), blue(c)))


def mix(a, b, t):
    t = clamp(t)
    return rgb(red(a) + (red(b) - red(a)) * t, green(a) + (green(b) - green(a)) * t,
               blue(a) + (blue(b) - blue(a)) * t)


def scale(c, k):
    """Multiplica o brilho por k."""
    return rgb(min(255, red(c) * k), min(255, green(c) * k), min(255, blue(c) * k))


def luma(c):
    return (0.299 * red(c) + 0.587 * green(c) + 0.114 * blue(c)) / 255


def ramp(lista):
    return [hex(c) for c in lista]


def fit(r, n):
    """Reamostra uma rampa para exatamente n degraus, mantendo as pontas."""
    r = [hex(c) for c in r]
    if len(r) == n:
        return r
    return [r[_jsround((i * (len(r) - 1)) / max(1, n - 1))] for i in range(n)]


def _jsround(x):
    return math.floor(x + 0.5)


def at(r, t):
    """O degrau da rampa para t em 0..1, sem misturar: pixel art escolhe uma cor."""
    i = math.floor(t * len(r))
    return r[min(len(r) - 1, max(0, i))]


def blend(r, t):
    """Cor misturada ao longo da rampa (para luz, onde suave é o certo)."""
    x = clamp(t) * (len(r) - 1)
    i = min(len(r) - 2, math.floor(x))
    return mix(r[i], r[i + 1], x - i)


# Rampas com deslocamento de matiz, do escuro ao claro: sombra puxa para o frio,
# luz para o quente ou branco. Qualquer uma recolore um efeito pela opção `palette`.
PAL = {
    "fire": ["#1f0b10", "#4a1118", "#8c1d1c", "#cc3a1a", "#f2701f", "#ffae35", "#ffe27a", "#fff8d6"],
    "ember": ["#1a0a0e", "#3d1012", "#701a14", "#a8301a", "#e0561e", "#ff8a2a", "#ffc46a"],
    "lava": ["#14060a", "#380a10", "#6e1210", "#ac2410", "#e8501a", "#ff8c2a", "#ffd25a"],
    "smoke": ["#0e0c12", "#1d1a22", "#2e2a35", "#433e4b", "#5c5664", "#7b7484", "#a39cab"],
    "dust": ["#1c1610", "#33281c", "#4f3f2c", "#6e5a40", "#927a58", "#b89f78", "#dcc8a2"],
    "ice": ["#0c1430", "#162c5c", "#1f4f94", "#2f7fcc", "#58b4ec", "#9bdcff", "#d8f4ff", "#ffffff"],
    "water": ["#081830", "#0e2e5a", "#14508c", "#1c76bc", "#36a2e0", "#78ccf4", "#c4ecff", "#ffffff"],
    "electric": ["#0a0f2e", "#172a78", "#2550d0", "#3f8cff", "#7cc8ff", "#c8f0ff", "#ffffff"],
    "volt": ["#24160a", "#5e3a0c", "#a8680f", "#e8a218", "#ffd23c", "#fff08a", "#ffffff"],
    "poison": ["#0d1a0c", "#173a14", "#265e18", "#3f8a1e", "#6cb82a", "#a8e04a", "#e0ff8a"],
    "holy": ["#2a1c08", "#5a3e10", "#9a6c18", "#d8a428", "#ffd84a", "#fff09a", "#fffbe6", "#ffffff"],
    "heal": ["#08201a", "#0f3f2c", "#17663e", "#24924e", "#3ec466", "#7ee88a", "#c8ffc4", "#ffffff"],
    "arcane": ["#140a26", "#2b1252", "#481c88", "#6b2cc0", "#9a48ec", "#c684ff", "#ecc8ff", "#ffffff"],
    "shadow": ["#050308", "#0f0a18", "#1c1230", "#2c1a4a", "#432468", "#5e3290", "#8048b8", "#a970e0"],
    "blood": ["#14040a", "#3a0a14", "#6a101c", "#a01824", "#d42a30", "#ff5a50", "#ff9a8a"],
    "earth": ["#140e0a", "#2a1e14", "#47321e", "#69492a", "#8e6638", "#b88a52", "#dcb47c"],
    "stone": ["#0e0e12", "#1c1c24", "#2c2c38", "#42424f", "#5c5c6b", "#7d7d8c", "#a4a4b2", "#d0d0da"],
    "gold": ["#1e1206", "#4a2c08", "#86520c", "#c48412", "#f0b424", "#ffe066", "#fff6c4", "#ffffff"],
    "leaf": ["#0c1a0e", "#163418", "#225224", "#357530", "#4f9a3a", "#7cc048", "#b4e070", "#e4ffb0"],
    "wood": ["#160c06", "#2e1a0c", "#4a2c14", "#6a421e", "#8e5c2c", "#b47c40", "#d8a464"],
    "metal": ["#0c0e14", "#1c2230", "#2e3648", "#4a5468", "#6e7a90", "#9aa6ba", "#d0d8e6", "#ffffff"],
    "bone": ["#1a1814", "#3a352c", "#5e5648", "#8a806c", "#b8ad96", "#e4dcc8", "#fffaf0"],
    "neon": ["#1a0516", "#3d0a33", "#701560", "#b0228f", "#f53cd1", "#ff86e6", "#ffd2f6", "#ffffff"],
    "cyber": ["#041418", "#08303a", "#0c5260", "#108088", "#18b4b0", "#4ce8d8", "#b4fff0", "#ffffff"],
    "matrix": ["#020a04", "#05200c", "#0a3c16", "#106624", "#1a9a34", "#3cd650", "#a4ffa8", "#e8ffe8"],
    "candy": ["#ff4a5a", "#ff9a2a", "#ffe03c", "#5ad84a", "#3cc8ff", "#7a6cff", "#f53cd1"],
    "night": ["#07060d", "#0c0a18", "#131026", "#1b1734", "#241f44", "#2f2956"],
}
RAMP = {k: ramp(v) for k, v in PAL.items()}

WHITE = hex("#ffffff")
BLACK = hex("#000000")
INK = hex("#0b0a10")
PATCH = hex("#f53cd1")


# ---- Braziliation: paleta regional -------------------------------------------
_PALETAS = Path(__file__).resolve().parents[3] / "ArteConceitual" / "Paletas"


def paleta_regional(regiao: str) -> dict:
    """Carrega `ArteConceitual/Paletas/{regiao}.json` como {key: hex}."""
    dados = json.loads((_PALETAS / f"{regiao}.json").read_text(encoding="utf-8"))
    return {c["key"]: c["hex"] for c in dados["colors"]}


def rampa_regional(regiao: str, keys) -> list:
    """Uma rampa (escuro → claro) feita de keys da paleta regional, ex.: ('1', '2', '6', '8').

    Passe o resultado como `palette` de qualquer efeito: o efeito escolhe degraus com
    `at()`/`fit()` e nunca inventa cor fora da paleta. Luz aditiva continua à parte.
    """
    pal = paleta_regional(regiao)
    return [pal[k] for k in keys]
