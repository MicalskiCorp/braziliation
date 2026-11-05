"""Números, easing, aleatório com seed e ruídos — tudo puro e determinístico.

Port de `src/core/math.js` do PixelFX (MIT, ver LICENSE-pixelfx.txt). O gerador
aleatório e o hash são idênticos bit a bit ao original: é isso que deixa a
paridade JS × Python comparar quadro a quadro (`py -m pxfx.paridade`).

Três diferenças de linguagem que o port precisa respeitar, e que moram aqui:
- `Math.round` do JS arredonda 0,5 para cima; `round()` do Python arredonda para o
  par. Use `jsround()`.
- `x | 0` e `x >>> 0` do JS truncam para inteiro de 32 bits. Use `i32()` / `u32()`.
- `Uint8ClampedArray` arredonda para o par (como o `round()` do Python): use `clamp8()`.
"""
from __future__ import annotations

import math

TAU = math.pi * 2
M32 = 0xFFFFFFFF
INF = math.inf


# ---- semântica numérica do JS -------------------------------------------------
def u32(n) -> int:
    """ToUint32 do JS (`n >>> 0`)."""
    if isinstance(n, float):
        if n != n or n in (INF, -INF):
            return 0
        n = int(n)  # trunca em direção a zero, como o JS
    return n & M32


def i32(n) -> int:
    """ToInt32 do JS (`n | 0`)."""
    v = u32(n)
    return v - 0x100000000 if v & 0x80000000 else v


def imul(a: int, b: int) -> int:
    """`Math.imul` como uint32."""
    return (u32(a) * u32(b)) & M32


def jsround(x: float) -> int:
    """`Math.round` do JS: meio arredonda para cima (+inf)."""
    return math.floor(x + 0.5)


def clamp8(v: float) -> int:
    """Conversão de Uint8ClampedArray: satura em 0..255 e arredonda para o par."""
    if v != v or v <= 0:
        return 0
    if v >= 255:
        return 255
    return int(round(v))


def call(v, *args):
    """Valor ou função dos argumentos (o `call` do pintor)."""
    return v(*args) if callable(v) else v


# ---- números -----------------------------------------------------------------
def clamp(x, a=0.0, b=1.0):
    return a if x < a else b if x > b else x


def lerp(a, b, t):
    return a + (b - a) * t


def invLerp(a, b, x):
    return 0 if b == a else (x - a) / (b - a)


def remap(x, a0, a1, b0, b1):
    return lerp(b0, b1, invLerp(a0, a1, x))


def fract(x):
    return x - math.floor(x)


def jsmod(x, m):
    """O `%` do JS (sinal do dividendo) — o do Python segue o sinal do divisor."""
    if isinstance(x, int) and isinstance(m, int):
        r = abs(x) % abs(m)
        return -r if x < 0 else r
    return math.fmod(x, m)


def wrap(x, m):
    """Resto sempre positivo: `((x % m) + m) % m` com a aritmética exata do JS."""
    return jsmod(jsmod(x, m) + m, m)


def seg(t, t0, t1):
    """Progresso 0..1 de t na janela [t0, t1]."""
    return clamp((t - t0) / (t1 - t0))


def smooth(e0, e1, x):
    t = seg(x, e0, e1)
    return t * t * (3 - 2 * t)


def bump(t, t0, t1):
    """0 → 1 → 0 na janela [t0, t1]."""
    return 0 if (t <= t0 or t >= t1) else math.sin(math.pi * seg(t, t0, t1))


def pingpong(x):
    return 1 - abs(wrap(x, 2) - 1)


def dist(x0, y0, x1, y1):
    return math.hypot(x1 - x0, y1 - y0)


def angleTo(x0, y0, x1, y1):
    return math.atan2(y1 - y0, x1 - x0)


def _out_bounce(t):
    n, d = 7.5625, 2.75
    if t < 1 / d:
        return n * t * t
    if t < 2 / d:
        t -= 1.5 / d
        return n * t * t + 0.75
    if t < 2.5 / d:
        t -= 2.25 / d
        return n * t * t + 0.9375
    t -= 2.625 / d
    return n * t * t + 0.984375


class _Ease:
    """Curvas de easing: entrada 0..1, saída 0..1 (back e elastic passam do ponto)."""

    linear = staticmethod(lambda t: t)
    inQuad = staticmethod(lambda t: t * t)
    outQuad = staticmethod(lambda t: 1 - (1 - t) * (1 - t))
    inOutQuad = staticmethod(lambda t: 2 * t * t if t < 0.5 else 1 - (-2 * t + 2) ** 2 / 2)
    inCubic = staticmethod(lambda t: t * t * t)
    outCubic = staticmethod(lambda t: 1 - (1 - t) ** 3)
    inOutCubic = staticmethod(lambda t: 4 * t * t * t if t < 0.5 else 1 - (-2 * t + 2) ** 3 / 2)
    inQuart = staticmethod(lambda t: t * t * t * t)
    outQuart = staticmethod(lambda t: 1 - (1 - t) ** 4)
    inExpo = staticmethod(lambda t: 0 if t <= 0 else 2 ** (10 * t - 10))
    outExpo = staticmethod(lambda t: 1 if t >= 1 else 1 - 2 ** (-10 * t))
    inSine = staticmethod(lambda t: 1 - math.cos((t * math.pi) / 2))
    outSine = staticmethod(lambda t: math.sin((t * math.pi) / 2))
    inOutSine = staticmethod(lambda t: -(math.cos(math.pi * t) - 1) / 2)
    inBack = staticmethod(lambda t, s=1.70158: 0 if t <= 0 else 1 if t >= 1 else (s + 1) * t * t * t - s * t * t)
    outBack = staticmethod(
        lambda t, s=1.70158: 0 if t <= 0 else 1 if t >= 1 else 1 + (s + 1) * (t - 1) ** 3 + s * (t - 1) ** 2)
    outElastic = staticmethod(
        lambda t: 0 if t <= 0 else 1 if t >= 1
        else 2 ** (-10 * t) * math.sin((t * 10 - 0.75) * ((2 * math.pi) / 3)) + 1)
    outBounce = staticmethod(_out_bounce)

    def __getitem__(self, nome):
        return getattr(self, nome)


ease = _Ease()


# ---- aleatório ---------------------------------------------------------------
def hash(*ns) -> int:  # noqa: A001 — o nome espelha o original de propósito
    """Hash inteiro de 32 bits de qualquer quantidade de inteiros."""
    h = 0x9E3779B9
    for n in ns:
        h = imul(h ^ u32(n), 0x85EBCA6B)
        h ^= h >> 13
        h = imul(h, 0xC2B2AE35)
        h ^= h >> 16
    return h


def rand(*ns) -> float:
    """Número em [0, 1) determinístico a partir de inteiros (seed, índice, qual valor...)."""
    return hash(*ns) / 4294967296


class Rng:
    """Gerador com seed (mulberry32), idêntico ao do PixelFX."""

    __slots__ = ("s",)

    def __init__(self, seed=1):
        self.s = u32(seed) or 1

    def next(self) -> float:
        self.s = (self.s + 0x6D2B79F5) & M32
        t = self.s
        t = imul(t ^ (t >> 15), t | 1)
        t ^= (t + imul(t ^ (t >> 7), t | 61)) & M32
        return ((t ^ (t >> 14)) & M32) / 4294967296

    def range(self, a, b):
        return a + (b - a) * self.next()

    def int(self, a, b):
        return math.floor(self.range(a, b + 1))

    def chance(self, p):
        return self.next() < p

    def sign(self):
        return -1 if self.next() < 0.5 else 1

    def pick(self, lista):
        return lista[math.floor(self.next() * len(lista))]

    def gauss(self):
        """Aproximadamente normal, média 0, desvio 1."""
        return (self.next() + self.next() + self.next() + self.next() - 2) * 1.732


def rng(*ns) -> Rng:
    """Um gerador por partícula: rng(seed, i) dá os mesmos números em todo quadro."""
    return Rng(hash(*ns))


# ---- ruído -------------------------------------------------------------------
def noise(x, seed=0):
    """Ruído de valor 1D suave em [-1, 1]."""
    i = math.floor(x)
    f = x - i
    u = f * f * (3 - 2 * f)
    return lerp(rand(i, seed), rand(i + 1, seed), u) * 2 - 1


def noise2(x, y, seed=0):
    """Ruído de valor 2D suave em [-1, 1]."""
    ix, iy = math.floor(x), math.floor(y)
    fx, fy = x - ix, y - iy
    ux, uy = fx * fx * (3 - 2 * fx), fy * fy * (3 - 2 * fy)
    a, b = rand(ix, iy, seed), rand(ix + 1, iy, seed)
    c, d = rand(ix, iy + 1, seed), rand(ix + 1, iy + 1, seed)
    return lerp(lerp(a, b, ux), lerp(c, d, ux), uy) * 2 - 1


def fbm(x, y, seed=0, octaves=3):
    s = a_n = 0.0
    a = 0.5
    for o in range(octaves):
        s += noise2(x, y, seed + o * 101) * a
        a_n += a
        x *= 2.03
        y *= 2.03
        a *= 0.5
    return s / a_n


def tileNoise(x, y, px=0, py=0, seed=0):
    """Ruído 2D cuja grade se repete a cada px células em x e py em y (0: sem repetição).

    É o que faz textura ladrilhar sem costura e loop rolar sem emenda:
    tileNoise(x, y + fase * py, 0, py).
    """
    ix, iy = math.floor(x), math.floor(y)
    fx, fy = x - ix, y - iy
    ux, uy = fx * fx * (3 - 2 * fx), fy * fy * (3 - 2 * fy)
    x0 = wrap(ix, px) if px else ix
    x1 = wrap(ix + 1, px) if px else ix + 1
    y0 = wrap(iy, py) if py else iy
    y1 = wrap(iy + 1, py) if py else iy + 1
    a, b = rand(x0, y0, seed), rand(x1, y0, seed)
    c, d = rand(x0, y1, seed), rand(x1, y1, seed)
    return lerp(lerp(a, b, ux), lerp(c, d, ux), uy) * 2 - 1


def tileFbm(x, y, px=0, py=0, seed=0, octaves=3):
    s = n = 0.0
    a, k = 0.5, 1
    for o in range(octaves):
        s += tileNoise(x * k, y * k, px * k, py * k, seed + o * 101) * a
        n += a
        a *= 0.5
        k *= 2
    return s / n


def loopNoise(phase, radius=1, seed=0):
    """Ruído que fecha o loop: o mesmo valor na fase 0 e na fase 1."""
    a = phase * TAU
    return noise2(math.cos(a) * radius + 50, math.sin(a) * radius + 50, seed)
