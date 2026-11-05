"""Partículas sem simulação: a posição de cada uma é função fechada da idade.

Port de `src/core/particles.js` do PixelFX (MIT). Por ser fórmula, o efeito pode ser
desenhado em qualquer t, voltado, posto em loop e exportado quadro a quadro — é o
que o `cycle()` usa para vapor, fagulha e gota que rodam em loop sem emenda.
"""
from __future__ import annotations

import math

from .matematica import clamp, jsmod, rng


def fly(x, y, vx, vy, t, g=0, drag=0):
    """Onde está, após t s, uma partícula lançada de (x, y) a (vx, vy) px/s, gravidade g, arrasto drag."""
    if drag <= 0:
        return [x + vx * t, y + vy * t + 0.5 * g * t * t]
    f = (1 - math.exp(-drag * t)) / drag
    vt = g / drag
    return [x + vx * f, y + vt * t + (vy - vt) * f]


def flyV(vx, vy, t, g=0, drag=0):
    """A velocidade em t, para rastros que apontam no sentido do movimento."""
    if drag <= 0:
        return [vx, vy + g * t]
    e = math.exp(-drag * t)
    vt = g / drag
    return [vx * e, vt + (vy - vt) * e]


def burst(n, seed, fn):
    """n partículas one-shot: fn(r, i) com um gerador repetível por partícula."""
    for i in range(n):
        fn(rng(seed, i), i)


def cycle(t, period, count, seed, life, fn):
    """Partículas que se repetem a cada `period` s: loops sem emenda. Para cada cópia viva,
    fn(age, life, r, i); r é um gerador novo da partícula i, o mesmo a cada período."""
    for i in range(count):
        g = rng(seed, i, 911)
        born = g.next() * period
        L = life(g) if callable(life) else life
        age = jsmod(jsmod(t - born, period) + period, period)
        while age < L:
            fn(age, L, rng(seed, i), i)
            age += period


def stream(t, t0, t1, rate, seed, life, fn):
    """Partículas nascidas a taxa constante entre t0 e t1 (um emissor que para)."""
    n = math.floor((min(t, t1) - t0) * rate)
    for i in range(n + 1):
        born = t0 + i / rate
        g = rng(seed, i, 911)
        L = life(g) if callable(life) else life
        age = t - born
        if 0 <= age < L:
            fn(age, L, rng(seed, i), i)


class ParticlesSimples:
    """Lista simples de partículas simuladas (o `Particles` de particles.js; o índice exporta o de sim)."""

    def __init__(self):
        self.list = []

    def add(self, p):
        p["age"] = 0
        p.setdefault("g", 0)
        p.setdefault("drag", 0)
        self.list.append(p)
        return p

    def update(self, dt):
        for i in range(len(self.list) - 1, -1, -1):
            p = self.list[i]
            p["age"] += dt
            if p["age"] >= p["life"]:
                del self.list[i]
                continue
            p["vx"] -= p["vx"] * p["drag"] * dt
            p["vy"] += p["g"] * dt - p["vy"] * p["drag"] * dt
            p["x"] += p["vx"] * dt
            p["y"] += p["vy"] * dt
            if p.get("ground") is not None and p["y"] > p["ground"]:
                p["y"] = p["ground"]
                p["vy"] = -abs(p["vy"]) * (p.get("bounce") if p.get("bounce") is not None else 0.3)
                p["vx"] *= 0.7

    @staticmethod
    def k(p):
        return clamp(1 - p["age"] / p["life"])
