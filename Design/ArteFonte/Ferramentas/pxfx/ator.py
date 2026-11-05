"""Personagem de teste: os efeitos de status envolvem a silhueta dele, golpes acertam nele.

Port de `src/core/actor.js` do PixelFX (MIT). É o boneco de 24×38 do original — serve
à PARIDADE. O manequim do Braziliation (96 px) sai do esqueleto (`pxfx.esqueleto`).
"""
from __future__ import annotations

import math

from .cor import hex
from .objeto import Obj

HERO = [
    "....kkkkk...",
    "..kkhhhhhk..",
    ".khhhhhhhhk.",
    ".khhhhhhhhhk",
    ".khhssssshhk",
    ".khsessesshk",
    ".khsessesshk",
    "..ksssssssk.",
    "...kkSSSkk..",
    "..kttttttk..",
    ".kttTttTttk.",
    ".ksttTTttsk.",
    ".kstttttttk.",
    "..kbbbbbbk..",
    "..kppkkppk..",
    "..kppk.kppk.",
    "..kppk.kppk.",
    "..koook.kook",
    "..kkkkk.kkkk",
]
HERO_PAL = {
    "k": "#17121f", "h": "#7a4128", "s": "#f3c49d", "S": "#c98b6c", "e": "#17121f",
    "t": "#5f6f94", "T": "#46536f", "b": "#8a5a32", "p": "#38334a", "o": "#6a4030",
    "H": "#a35d34", "w": "#ffffff", "m": "#a3564a", "g": "#e8c060", "L": "#7f90b6", "O": "#8f5a3f", "P": "#4b4560",
    "c": "#f53cd1", "C": "#ff8fe6", "D": "#a31f8a",
}
# O manequim: casca neutra que deixa as cores de qualquer efeito falarem.
DUMMY_PAL = {
    "k": "#0e0c14", "A": "#e4e6ec", "B": "#b6b9c3", "C": "#868995", "D": "#5c5e6a", "E": "#6e707c",
    "F": "#4b4d58", "G": "#34353f", "J": "#2a2b33", "m": "#f53cd1",
}
# O mesmo personagem no dobro (24 × 38), parado: a pose de descanso do rig, assada.
HERO2 = [
    "...........kkk..........",
    "..........kAABk.........",
    ".........kAAABJk........",
    ".........kABBJJk........",
    ".........kBBBJCDk.......",
    ".........kBCJDDDk.......",
    ".........kkJJJDk........",
    ".......kkkkABBJCkk......",
    "......kAABCJBCCCkDk.....",
    "......kABBCJCCCmDkDk....",
    "......kBBCDDJCDDDkDk....",
    "......kABCDJDDDDDkk.....",
    ".....kAABDkDDDDJkk......",
    ".....kABCDkDDJJGkk......",
    ".....kABCkJJJGGGkk......",
    "....kJJCDkFFFGGGk.......",
    "....kAJJDkJJJGGGk.......",
    "....kJCJJkABBJGGk.......",
    ".....kJCCkBBCDJJJk......",
    ".....kCCCJBBCDJJDk......",
    ".....kCCCDJCCDkJDDk.....",
    "......kCDDJBCDkDDDk.....",
    ".......kDJJJCDkDDDkk....",
    ".......kJBCJCDkDDDkk....",
    ".......kBDJBCDkCDDkk....",
    "........kJJBCDkCDDk.....",
    "........kBBBCDkCCDDk....",
    "........kBBBCDkCCDDk....",
    ".........kBBCDkJDDDk....",
    "........kBJJJJkCJJJk....",
    "........kBBCCDkCCDDk....",
    "........kBBCDDkCDDk.....",
    "........kBBCDkCCDDk.....",
    "........kBCCDkCCDDk.....",
    "........kBCDDkCDDDk.....",
    ".......kJBCJkkkDJkkkk...",
    ".......kAJJAAAAkCCCCCk..",
    "........kkkkkkkkkkkkk...",
]


def maskOf(rows, k=1):
    h, w = len(rows) * k, len(rows[0]) * k
    data = bytearray(w * h)
    for y, r in enumerate(rows):
        for x, ch in enumerate(r):
            if ch == ".":
                continue
            for j in range(k * k):
                data[(y * k + j // k) * w + x * k + (j % k)] = 1
    return Obj(w=w, h=h, data=data)


def pixelsOf(rows, pal):
    w = len(rows[0])
    data = [0] * (w * len(rows))
    for y, r in enumerate(rows):
        for x, ch in enumerate(r):
            data[y * w + x] = 0 if ch == "." else hex(pal[ch])
    return data


MASKS = {1: maskOf(HERO, 1), 2: maskOf(HERO2, 1)}
SPRITES = {1: HERO, 2: HERO2}
PIXELS = {1: pixelsOf(HERO, HERO_PAL), 2: pixelsOf(HERO2, DUMMY_PAL)}


def stockActor(k=1):
    """O ator padrão na escala k (1: 12×19, 2: 24×38), pés em (0, 0) no espaço local."""
    k = 2 if k == 2 else 1
    m = MASKS[k]
    x, y = -math.floor(m.w / 2), -m.h
    a = Obj(mask=m, pixels=PIXELS[k], x=x, y=y, w=m.w, h=m.h, k=k, head=[0, y],
            chest=[0, -26 if k == 2 else y + 11])
    if k == 2:
        a.eyes = [[13, 3], [15, 3]]
    return a


def drawActor(p, actor=None, a=1):
    """Desenha o ator com os pés na origem do pintor, com alpha a (em dither)."""
    actor = actor or stockActor()
    if a > 0:
        k2 = actor.k == 2
        p.sprite(SPRITES[2 if k2 else 1], DUMMY_PAL if k2 else HERO_PAL, actor.x, actor.y, {"a": a})


def actorAlphaOf(mod, t, o):
    """Quão visível o efeito quer o personagem no tempo t (efeitos podem exportar actorAlpha)."""
    f = getattr(mod, "actorAlpha", None)
    return f(t, o) if callable(f) else 1
