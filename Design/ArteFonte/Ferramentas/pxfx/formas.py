"""Listas de pontos que os efeitos usam o tempo todo: raio, estrela, polígono, rastro.

Port de `src/core/shapes.js` do PixelFX (MIT). O `bolt()` (deslocamento de ponto
médio) é o arco voltaico do dieselpunk: bobina Tesla, fio desencapado, faísca de máquina.
"""
from __future__ import annotations

import math

from .matematica import TAU


def bolt(r, x0, y0, x1, y1, jag=0.22, depth=5):
    """Caminho de raio de (x0, y0) a (x1, y1). jag: quanto o ponto médio desvia, em fração do segmento."""
    pts = [[x0, y0], [x1, y1]]
    for _ in range(depth):
        nxt = [pts[0]]
        for i in range(1, len(pts)):
            ax, ay = pts[i - 1]
            bx, by = pts[i]
            dx, dy = bx - ax, by - ay
            L = math.hypot(dx, dy)
            off = (r.next() * 2 - 1) * jag * L
            nxt.append([(ax + bx) / 2 + (-dy / (L or 1)) * off, (ay + by) / 2 + (dx / (L or 1)) * off])
            nxt.append(pts[i])
        pts = nxt
    return pts


def forks(r, path, count=3, len=20, jag=0.3, spread=0.9):  # noqa: A002 — espelha o original
    """Galhos saindo de um raio: count ramos de até len px."""
    out = []
    for _ in range(count):
        i = 1 + math.floor(r.next() * (_len(path) - 2))
        x, y = path[i]
        px, py = path[i - 1]
        a = math.atan2(y - py, x - px) + (-1 if r.next() < 0.5 else 1) * spread * (0.4 + 0.6 * r.next())
        ll = len * (0.4 + 0.6 * r.next())
        out.append(bolt(r, x, y, x + math.cos(a) * ll, y + math.sin(a) * ll, jag=jag, depth=3))
    return out


_len = len


def star(cx, cy, r0, r1, n=5, rot=-math.pi / 2):
    """Estrela de n pontas entre r1 (pontas) e r0 (cantos internos)."""
    pts = []
    for i in range(n * 2):
        a = rot + (i * math.pi) / n
        r = r0 if i % 2 else r1
        pts.append([cx + math.cos(a) * r, cy + math.sin(a) * r])
    return pts


def ngon(cx, cy, r, n=6, rot=0):
    return [[cx + math.cos(rot + (i * TAU) / n) * r, cy + math.sin(rot + (i * TAU) / n) * r] for i in range(n)]


def trail(pos, t, n, dt):
    """pos(t - i*dt) para i = 0..n-1: o rastro de algo em movimento, mais novo primeiro."""
    return [pos(max(0, t - i * dt)) for i in range(n)]
