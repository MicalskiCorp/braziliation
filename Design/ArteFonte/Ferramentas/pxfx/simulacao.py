"""Partículas, detritos e luzes simulados: faísca que quica, estilhaço que tomba,
vapor e fumaça que incham e afinam, luz que acende e morre.

Port de `src/core/sim.js` do PixelFX, que por sua vez adapta os VFX open-source do
Sprite Fusion (https://www.spritefusion.com/pixel-art-vfx), MIT License,
Copyright (c) 2026 Hugo Duprez. Unidades: pixels de arte e segundos; desenha pelo
pintor, então espelha, gira e escala como qualquer efeito.
"""
from __future__ import annotations

import math

from .cor import WHITE, hex, mix, scale
from .matematica import TAU, Rng, clamp, jsround
from .objeto import Obj

GRAVITY = 950  # px/s²
CROSS = [[1, 0], [-1, 0], [0, 1], [0, -1]]
DIAG = [[1, 1], [1, -1], [-1, 1], [-1, -1]]
HOT = [hex(c) for c in ("#fff3a6", "#ffe26b", "#ff8a2a", "#f2561d")]
# Fogo do branco ao brasa, e fumaça de fresca a rala: as rampas que FIRE e SMOKE descem.
FIRE_RAMP = [hex(c) for c in ("#ffffff", "#fff3a6", "#ffe26b", "#ffc23d", "#ff8a2a", "#f2561d", "#c9281f",
                              "#8a1f17", "#4a1712")]
SMOKE_RAMP = [hex(c) for c in ("#7b6f72", "#5d5660", "#433d48", "#2b2630", "#1a171e")]


def rampAt(r, t):
    return r[min(len(r) - 1, max(0, math.floor(t * len(r))))]


class _P:
    SPARK, MOTE, STREAK, FLAKE, VAPOUR, DUST, STAR, EMBER, SMOKE, FIRE, BRAND, GRIT = range(12)


class _PF:
    SMOKES, BIG, BACK = 1, 2, 4


P = _P
PF = _PF
SOFT = {P.VAPOUR, P.DUST, P.SMOKE}


class _Part:
    __slots__ = ("k", "x", "y", "vx", "vy", "life", "max", "col", "size", "seed", "delay", "flag")


class Particles:
    """Sistema de partículas. opts: {seed, rng, ground: (x) -> y do chão, sparks: cores da cabeça à cauda,
    haze: cor com que o vapor brilha, onLand: (x, y) quando um BRAND bate no chão}.
    draw(p, layer): "back" desenha os tipos suaves (vapor, poeira, fumaça), "front" o resto, None os dois."""

    def __init__(self, opts=None, **kw):
        opts = dict(opts or {}, **kw)
        self.R = opts.get("rng") or Rng(opts.get("seed", 1) if opts.get("seed") is not None else 1)
        self.list = []
        self.t = 0.0
        self.ground = opts.get("ground") or (lambda x: math.inf)
        self.sparks = [hex(c) for c in (opts.get("sparks") or HOT)]
        self.haze = None if opts.get("haze") is None else hex(opts["haze"])
        self.onLand = opts.get("onLand")

    def spawn(self, k, x, y, vx, vy, life, col=WHITE, size=1, delay=0, flag=0):
        """delay: segundos antes de aparecer; flag: bits PF. col 0 deixa FIRE e SMOKE usarem as próprias rampas."""
        q = _Part()
        q.k, q.x, q.y, q.vx, q.vy, q.life, q.max = k, x, y, vx, vy, life, life
        q.col = hex(col) if col else 0
        q.size, q.seed, q.delay, q.flag = size, self.R.next() * 100, delay, flag
        self.list.append(q)

    @property
    def count(self):
        return len(self.list)

    def update(self, dt):
        self.t += dt
        R, t = self.R, self.t
        lst = self.list
        for i in range(len(lst) - 1, -1, -1):
            p = lst[i]
            if p.delay > 0:
                p.delay -= dt
                continue
            p.life -= dt
            if p.life <= 0:
                if p.k == P.FIRE and p.flag & PF.SMOKES:
                    big = p.flag & PF.BIG
                    self.spawn(P.SMOKE, p.x, p.y, p.vx * 0.6, p.vy * 0.6 - 6,
                               R.range(1.3, 2.3) if big else R.range(0.8, 1.4), 0,
                               p.size * (0.85 if big else 0.7), 0, PF.BIG if big else 0)
                del lst[i]
                continue
            k = p.k
            if k == P.FIRE:
                p.vy -= 95 * dt
                p.vx += math.sin(t * 17 + p.seed) * 30 * dt
                p.vx -= p.vx * 5 * dt
                p.vy -= p.vy * 3.2 * dt
            elif k == P.GRIT:
                p.vy += GRAVITY * dt
                p.vx -= p.vx * 0.8 * dt
                g = self.ground(p.x)
                ny = p.y + p.vy * dt
                p.x += p.vx * dt
                if p.vy > 0 and p.y <= g and ny >= g:
                    p.y = g - 0.25
                    if p.vy > 130 and R.chance(0.4):
                        p.vy = -p.vy * 0.25
                        p.vx = p.vx * 0.5 + R.range(-10, 10)
                    else:
                        p.vx = p.vy = 0
                        p.life = min(p.life, 0.5)
                else:
                    p.y = ny
                continue
            elif k == P.BRAND:
                # pedaço em brasa: faz arco, solta chama e acende um foguinho onde cai
                p.vy += GRAVITY * 0.8 * dt
                p.vx -= p.vx * 0.9 * dt
                if R.chance(0.9 * min(1, dt * 60)):
                    self.spawn(P.FIRE, p.x, p.y, p.vx * 0.1 + R.range(-7, 7), p.vy * 0.1 - 10, R.range(0.16, 0.32), 0,
                               R.range(0.9, 1.7) * (0.5 + (p.life / p.max) * 0.6), 0,
                               PF.SMOKES if R.chance(0.4) else 0)
                g = self.ground(p.x)
                ny = p.y + p.vy * dt
                p.x += p.vx * dt
                if p.vy > 0 and p.y <= g and ny >= g:
                    if self.onLand:
                        self.onLand(p.x, g)
                    del lst[i]  # o que o onLand/spawn acrescentou foi para o fim: i ainda é p
                else:
                    p.y = ny
                continue
            elif k == P.SPARK:
                p.vy += GRAVITY * 0.45 * dt
                p.vx -= p.vx * 2.2 * dt
                p.vy -= p.vy * 2.2 * dt
                g = self.ground(p.x)
                ny = p.y + p.vy * dt
                p.x += p.vx * dt
                if p.vy > 0 and p.y <= g and ny >= g:
                    p.vy = -p.vy * 0.45
                    p.vx *= 0.7
                    p.y = g - 0.25
                else:
                    p.y = ny
                continue
            elif k == P.STREAK:
                p.vx += p.vx * 3 * dt
                p.vy += p.vy * 3 * dt
            elif k == P.FLAKE:
                p.vx -= p.vx * 2.2 * dt
                p.vy -= p.vy * 2.2 * dt - 35 * dt
                p.x += math.sin(self.t * 2.5 + p.seed) * 7 * dt
            elif k == P.EMBER:
                p.vy += (-30 + math.sin(t * 3 + p.seed) * 20) * dt
                p.vx += math.cos(t * 2.3 + p.seed) * 45 * dt
                p.vx -= p.vx * 1.6 * dt
                p.vy -= p.vy * 1.6 * dt
            elif k == P.SMOKE:
                big = p.flag & PF.BIG
                p.vy -= (23 if big else 16) * dt
                p.vx += math.sin(t * 1.3 + p.seed) * 8 * dt
                p.vx -= p.vx * 1.6 * dt
                p.vy -= p.vy * 1.2 * dt
            elif k == P.MOTE:
                p.vx -= p.vx * 0.6 * dt
                p.vy -= p.vy * 0.6 * dt
            else:
                drag = 4 if k in SOFT else 1.6
                p.vx -= p.vx * drag * dt
                p.vy -= p.vy * drag * dt + 5 * dt
            p.x += p.vx * dt
            p.y += p.vy * dt

    def draw(self, p, layer=None, *_):
        for q in self.list:
            if q.delay > 0:
                continue
            if layer and ("back" if (q.k in SOFT or q.flag & PF.BACK) else "front") != layer:
                continue
            k = q.life / q.max
            x, y = q.x, q.y
            sp = math.hypot(q.vx, q.vy) or 1
            ux, uy = q.vx / sp, q.vy / sp
            kind = q.k
            if kind == P.SPARK:
                S = self.sparks
                head = S[0] if k > 0.6 else S[1] if k > 0.3 else S[2]
                ln = min(9, 1 + sp * 0.022)
                p.line(x - ux * ln, y - uy * ln, x - ux * ln * 0.4, y - uy * ln * 0.4, head if k > 0.5 else S[-1])
                p.line(x - ux * ln * 0.45, y - uy * ln * 0.45, x, y, head)
                p.glow(x, y, 3, head, 0.45 * k)
            elif kind == P.MOTE:
                ln = min(16, 0.5 + sp * 0.026) * q.size
                a = k / 0.35 if k < 0.35 else 1
                p.line(x - ux * ln, y - uy * ln, x - ux * ln * 0.35, y - uy * ln * 0.35, scale(q.col, 0.55), a)
                p.line(x - ux * ln * 0.4, y - uy * ln * 0.4, x, y, q.col, a)
                p.glow(x, y, 2.5 + q.size, q.col, 0.4 * k)
            elif kind == P.STREAK:
                L = clamp(sp / 30, 1, 7)
                d = L
                while d >= 0:
                    c = WHITE if d < 1 else q.col if d < L * 0.5 else scale(q.col, 0.6)
                    p.dot(x - ux * d, y - uy * d, c, 1 if d < L * 0.5 else 1.2 - d / L)
                    d -= 0.5
                p.glow(x, y, 4, q.col, 0.4)
            elif kind == P.FLAKE:
                a = min(1, k * 3)
                p.dot(x, y, q.col, a)
                if q.size > 1.3:
                    for dx, dy in CROSS:
                        p.dot(x + dx, y + dy, scale(q.col, 0.8), a * 0.8)
            elif kind == P.VAPOUR:
                r = q.size * (0.6 + (1 - k) * 0.9)
                p.disc(x, y, r, q.col, k ** 1.3 * 0.45)
                if self.haze:
                    p.glow(x, y, r * 1.8, self.haze, 0.16 * k)
            elif kind == P.DUST:
                p.disc(x, y, q.size * (0.6 + (1 - k) * 0.9), q.col, k ** 1.3 * 0.7)
            elif kind == P.SMOKE:
                # três discos suaves: corpo, núcleo mais denso embaixo, topo iluminado enquanto é nova
                age = 1 - k
                big = q.flag & PF.BIG
                r = q.size * (0.65 + min(1, age * 2.5) * 0.45 + age * (0.5 if big else 0.4))
                a = min(1, age * 12) * min(1, k * 2.4) * (0.7 if big else 0.58)
                c = mix(q.col, rampAt(SMOKE_RAMP, age), age) if q.col else rampAt(SMOKE_RAMP, age * 1.05)
                p.disc(x, y, r, c, a * 0.45)
                p.disc(x + r * 0.05, y + r * 0.06, r * 0.74, c, a * 0.62)
                if age < 0.5:
                    p.disc(x - r * 0.22, y - r * 0.3, r * 0.5, mix(c, WHITE, 0.12), a * 0.4 * (1 - age * 2))
            elif kind == P.FIRE:
                # bola de chama que esfria descendo a rampa enquanto sobe: borda escura, miolo aceso, língua no topo
                age = 1 - k
                heat = min(0.999, age ** 0.62 + math.fmod(q.seed, 1) * 0.1)
                F = FIRE_RAMP
                n = len(F)
                idx = min(n - 2, math.floor(heat * (n - 1)))
                r = q.size * (0.55 + 0.45 * min(1, age * 7)) * (1 - age * 0.55)
                c = F[idx]
                if idx >= n - 2:
                    p.disc(x, y, r, c, min(1, k * 3) * 0.85)
                else:
                    p.circle(x, y, r, F[min(n - 1, idx + 2)])
                    p.circle(x - r * 0.16, y - r * 0.22, r * 0.78, c)
                    if r > 1.6:
                        p.circle(x, y - r * 0.9, r * 0.42, c)
                    if idx <= 3 and r > 1.8:
                        p.circle(x - r * 0.28, y - r * 0.34, r * 0.36, F[max(0, idx - 1)])
                    if idx < 6:
                        p.glow(x, y, r * 2.4 + 2, c, 0.18 * k)
            elif kind == P.BRAND:
                p.circle(x, y, 1.6, HOT[3])
                p.px(x, y, HOT[0] if math.sin(self.t * 40 + q.seed) > 0 else HOT[1])
                p.px(x + 1, y, HOT[1])
                p.glow(x, y, 7, HOT[2], 0.45)
            elif kind == P.GRIT:
                if k > 0.25 or k * 4 > 0.5:
                    p.px(x, y, q.col)
                    if q.size >= 2:
                        p.px(x + 1, y, q.col)
                        p.px(x, y + 1, scale(q.col, 0.8))
                        p.px(x + 1, y + 1, scale(q.col, 0.7))
            elif kind == P.EMBER:
                c = self.sparks[0] if k > 0.6 else self.sparks[1] if k > 0.3 else self.sparks[2]
                if k < 0.25 and math.sin(self.t * 40 + q.seed) < 0:
                    continue
                p.px(x, y, c)
                if q.size > 1.5:
                    p.px(x, y + 1, self.sparks[-1])
                p.glow(x, y, 3 + q.size, c, 0.35 * k)
            else:
                # STAR: cruz que pisca, braços pelo tamanho
                tw = 0.6 + 0.4 * math.sin(self.t * (8 + math.fmod(q.seed, 5)) + q.seed)
                if q.size < 1:
                    if tw * k > 0.25:
                        p.px(x, y, WHITE if tw > 0.8 else q.col)
                    p.glow(x, y, 3, q.col, 0.4 * k * tw)
                    continue
                sparkle(p, x, y, q.size * tw * min(1, k * 3), q.col, scale(q.col, 0.75), 0.5 * k * tw)


class _Blaze:
    __slots__ = ("x", "y", "life", "max", "acc", "power")


class Blazes:
    """Foguinhos onde algo caiu: add(x, y, life, power) alimenta puffs de FIRE num sistema de partículas."""

    def __init__(self, ps):
        self.ps = ps
        self.list = []

    def add(self, x, y, life, power):
        b = _Blaze()
        b.x, b.y, b.life, b.max, b.acc, b.power = x, y, life, life, self.ps.R.next(), power
        self.list.append(b)

    @property
    def count(self):
        return len(self.list)

    def update(self, dt):
        ps = self.ps
        R = ps.R
        for i in range(len(self.list) - 1, -1, -1):
            b = self.list[i]
            b.life -= dt
            if b.life <= 0:
                del self.list[i]
                continue
            k = b.life / b.max
            intensity = b.power * (1 if k > 0.7 else 0.35 + (k / 0.7) * 0.65)
            b.acc += dt * (6 + 16 * intensity)
            while b.acc > 1:
                s = R.range(1.2, 2.8) * intensity
                ps.spawn(P.FIRE, b.x + R.range(-1.5, 1.5), b.y - s * 0.6, R.range(-6, 6), R.range(-30, -12),
                         R.range(0.28, 0.6), 0, s, 0, PF.BACK | (PF.SMOKES if R.chance(0.3) else 0))
                if R.chance(0.06):
                    ps.spawn(P.EMBER, b.x, b.y - 1.5, R.range(-15, 15), R.range(-45, -15), R.range(0.6, 1.4), HOT[2],
                             1, 0, PF.BACK)
                b.acc -= 1

    def drawBack(self, p):
        for b in self.list:
            k = b.life / b.max
            p.px(b.x, b.y, (HOT[1] if math.sin(b.life * 31 + b.x) > 0 else HOT[2]) if k > 0.4 else HOT[3])
            p.glow(b.x, b.y, 6 + 5 * k * b.power, HOT[2], 0.3 * k * b.power)


class _B:
    SHARD, CHUNK, DRIP = range(3)


B = _B


class Bits:
    """Detritos rígidos que tombam, quicam e assentam. add({kind, x, y, vx, vy, a, va, s, c, ramp, g, drag,
    bounce, life})."""

    def __init__(self, opts=None, **kw):
        opts = dict(opts or {}, **kw)
        self.list = []
        self.ground = opts.get("ground") or (lambda x: math.inf)

    def add(self, b=None, **kw):
        b = dict(b or {}, **kw)
        life = b.get("life", 1) if b.get("life") is not None else 1
        d = Obj(kind=B.SHARD, vx=0, vy=0, a=0, va=0, s=1, c=WHITE, g=1, drag=0, bounce=0, rest=False)
        d.update(b)
        d.life = life
        d.max = life
        self.list.append(d)

    @property
    def count(self):
        return len(self.list)

    def update(self, dt):
        for i in range(len(self.list) - 1, -1, -1):
            b = self.list[i]
            b.life -= dt
            if b.life <= 0:
                del self.list[i]
                continue
            if b.rest:
                continue
            b.vy += GRAVITY * b.g * dt
            b.vx -= b.vx * b.drag * dt
            b.vy -= b.vy * b.drag * dt
            b.x += b.vx * dt
            b.y += b.vy * dt
            b.a += b.va * dt
            floor = self.ground(b.x)
            sp = b.vy
            if b.g <= 0 or b.y < floor or sp <= 0:
                continue
            b.y = floor - 0.01
            if b.kind == B.DRIP:
                b.life = 0
            elif b.bounce > 0 and sp > 70:
                b.vy = -sp * b.bounce
                b.vx *= 0.7
                b.va *= 0.6
            else:
                b.rest = True
                b.vx = b.vy = 0

    def draw(self, p, *_):
        for b in self.list:
            a = min(1, b.life / 0.4)
            ca, sa = math.cos(b.a), math.sin(b.a)
            if b.kind == B.SHARD:
                d = -b.s / 2
                while d <= b.s / 2:
                    p.dot(b.x + ca * d, b.y + sa * d, WHITE if d > b.s / 2 - 0.6 else hex(b.c), a)
                    d += 0.5
            elif b.kind == B.DRIP:
                p.dot(b.x, b.y, hex(b.c), a)
                p.dot(b.x, b.y - 1, hex(b.c), a * 0.5)
            else:
                # pedaço sombreado: aceso em cima à esquerda, escuro embaixo à direita, borda escura
                R = [hex(c) for c in (b.ramp or ["#1c2030", "#3a4a66", "#6e86a8", "#a8c0dc", "#e8f2ff"])]
                n = len(R)
                x, y, r = jsround(b.x), jsround(b.y), math.ceil(b.s) + 1
                for py in range(-r, r + 1):
                    for px in range(-r, r + 1):
                        u = (px + 0.5) * ca + (py + 0.5) * sa
                        v = -(px + 0.5) * sa + (py + 0.5) * ca
                        dd = abs(u) / b.s + abs(v) / (b.s * 0.62)
                        if dd > 1.3:
                            continue
                        c = R[0] if dd > 1 else ((R[n - 1] if u < 0 else R[n - 2]) if v < 0
                                                 else (R[n - 3] if u < 0 else R[max(1, n - 4)]))
                        p.dot(x + px, y + py, c, a)


class _Light:
    __slots__ = ("x", "y", "r", "color", "k", "life", "max")


class Lights:
    """Luzes que acendem e morrem: add(x, y, r, color, k, life)."""

    def __init__(self):
        self.list = []

    def add(self, x, y, r, color, k, life):
        l = _Light()
        l.x, l.y, l.r, l.color, l.k, l.life, l.max = x, y, r, hex(color), k, life, life
        self.list.append(l)

    def update(self, dt):
        for i in range(len(self.list) - 1, -1, -1):
            self.list[i].life -= dt
            if self.list[i].life <= 0:
                del self.list[i]

    def draw(self, p, *_):
        for l in self.list:
            k = l.life / l.max
            p.glow(l.x, l.y, l.r * (0.55 + 0.45 * k), l.color, l.k * k * k)


def sparkle(p, x, y, arm, c, tip=None, k=0.6):
    """Brilho em estrela: braços de comprimento arm na cor c com pontas em tip, miolo branco, luz."""
    if tip is None:
        tip = c
    n = jsround(arm)
    if n < 1:
        return
    X, Y = math.floor(x), math.floor(y)
    for d in range(1, n + 1):
        cc = tip if d > n * 0.6 else c
        for dx, dy in CROSS:
            p.px(X + dx * d, Y + dy * d, cc)
    if n >= 3:
        for dx, dy in DIAG:
            p.px(X + dx, Y + dy, c)
    if n >= 6:
        for dx, dy in DIAG:
            p.px(X + dx * 2, Y + dy * 2, tip)
    p.px(X, Y, WHITE)
    p.glow(x, y, 4 + n * 2, c, k)


def flare(p, x, y, L, k, ramp):
    """Clarão de 8 raios: longos nos eixos, menores entre eles, sumindo ao longo do comprimento."""
    if L < 1:
        return
    R = [hex(c) for c in ramp]
    n = len(R)
    for i in range(8):
        an = (i * math.pi) / 4
        ln = L if i % 4 == 0 else L * 0.6 if i % 2 == 0 else L * 0.3
        ca, sa = math.cos(an), math.sin(an)
        d = 0.0
        while d <= ln:
            u = d / ln
            p.dot(x + ca * d, y + sa * d, WHITE if u < 0.35 else R[n - 2] if u < 0.7 else R[n - 3],
                  1 if u < 0.6 else k * 1.5 * (1 - u) + 0.2)
            d += 0.5


def band(p, cx, cy, r, sy, th, k, ramp, keep=None, hot=False):
    """Anel num plano inclinado (sy 0,16 deita no chão), espessura th para dentro, alpha k, colorido pela
    profundidade com ramp. keep(ângulo) escolhe que parte desenhar: (g) -> sin(g) < 0 é a metade de trás."""
    if r <= 0 or k <= 0:
        return
    keep = keep or (lambda g: True)
    R = [hex(c) for c in ramp]
    n = len(R)
    m = math.ceil(r * TAU * 1.2)
    for j in range(m):
        ang = (j / m) * TAU
        ca, sa = math.cos(ang), math.sin(ang)
        if not keep(ang):
            continue
        o = th
        while o >= 0:
            u = o / th
            c = (WHITE if hot else R[n - 1]) if u < 0.15 else R[n - 2] if u < 0.4 else R[n - 3] if u < 0.7 else R[n - 4]
            p.dot(cx + ca * (r - o), cy + sa * (r - o) * sy, c, k * (1.2 if u < 0.4 else 1.15 - u))
            o -= 0.5


def crystal(p, x, base, h, w, lean, ramp, opts=None):
    """Espinho de cristal facetado em pé em (x, base), altura h, base w, inclinado lean px na ponta,
    sombreado na rampa (6+ degraus). opts: {a, white, glint}."""
    opts = opts or {}
    if h < 1.5:
        return
    R = [hex(c) for c in ramp]
    n = len(R)

    def C(i):
        return R[max(0, n - 1 - i)]

    a = opts.get("a", 1)
    top = base - h
    ridge0 = x - w * 0.14
    glint = opts.get("glint", -1)

    def inside(px, py):
        u = (base - (py + 0.5)) / h
        return 0 <= u <= 1 and abs(px + 0.5 - (x + lean * u)) <= (w / 2) * (1 - u) + 0.35

    for py in range(math.floor(top) - 1, math.ceil(base)):
        for px in range(math.floor(x - w / 2 - abs(lean) - 2), math.ceil(x + w / 2 + abs(lean) + 2) + 1):
            if not inside(px, py):
                if inside(px - 1, py) or inside(px + 1, py) or inside(px, py + 1) or (inside(px, py - 1) and py < base - 1):
                    p.dot(px, py, R[0], a)
                continue
            if opts.get("white"):
                p.dot(px, py, WHITE, a)
                continue
            u = (base - (py + 0.5)) / h
            rx = ridge0 + (x + lean - ridge0) * u
            c = x + lean * u
            hw = (w / 2) * (1 - u) + 0.35
            fx = px + 0.5
            if u > 0.9:
                col = WHITE
            elif abs(fx - rx) < 0.55:
                col = C(1)
            elif fx < rx:
                col = C(1) if fx - (c - hw) < 1 else (C(2) if (fx - (c - hw)) / max(1, rx - (c - hw)) > 0.55 else C(3))
            else:
                col = C(min(n - 2, 6)) if c + hw - fx < 1.2 else (C(5) if (fx - rx) / max(1, c + hw - rx) > 0.5 else C(4))
            if glint >= 0 and fx <= rx + 0.6:
                g = abs(u - glint)
                if g < 0.05:
                    col = WHITE
                elif g < 0.1:
                    col = C(1)
            p.dot(px, py, col, a)
