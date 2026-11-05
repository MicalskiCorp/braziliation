"""Golpes: vários efeitos tocados como um. Um projétil é só um efeito cujo x é função do tempo.

Port de `src/core/chain.js` do PixelFX (MIT). De fora, um golpe é um efeito comum:
toca, recolore e exporta.
"""
from __future__ import annotations

import math

from .objeto import Obj
from .quadro import createFx

_POS = ("fx", "t", "until", "x", "y", "flip")


def chain(cues):
    """create(o) para uma lista de deixas: {fx (módulo), t (início), until (corta aqui), x, y (número ou
    função do tempo do golpe), flip, ...opções daquele efeito}."""

    def create(o):
        lst = []
        for i, cue in enumerate(cues):
            opts = {k: v for k, v in cue.items() if k not in _POS}
            opts["seed"] = (o.get("seed") if o.get("seed") is not None else 1) + i
            lst.append(Obj(fx=cue["fx"], t=cue.get("t") or 0,
                           until=math.inf if cue.get("until") is None else cue["until"],
                           x=cue.get("x") or 0, y=cue.get("y") or 0, flip=bool(cue.get("flip")),
                           opts=opts, inst=None, over=False))
        estado = {"t": 0.0}

        def at(v):
            return v(estado["t"]) if callable(v) else v

        def each(p, layer):
            frame, tx, ty, sign, cs, sn, k, fade, lk = p.frame, p.tx, p.ty, p.fx, p.cs, p.sn, p.k, p.fade, p.lightK
            for c in lst:
                if not c.inst or c.over:
                    continue
                c.inst.options.x = tx + sign * at(c.x) * k
                c.inst.options.y = ty + at(c.y) * k
                c.inst.options.flip = (sign < 0) != c.flip
                c.inst.options.escala = k
                c.inst.draw(frame, layer)
            # cada um posiciona o pintor para si: devolve para quem desenhar depois
            p.tx, p.ty, p.fx, p.cs, p.sn, p.k, p.fade, p.lightK = tx, ty, sign, cs, sn, k, fade, lk

        def update(dt):
            estado["t"] += dt
            t = estado["t"]
            for c in lst:
                if c.over or t < c.t:
                    continue
                if not c.inst:
                    c.inst = createFx(c.fx, c.opts)
                else:
                    c.inst.update(dt)
                meta = getattr(c.fx, "meta", None) or {}
                if t >= c.until or (c.inst.done() and not meta.get("loop")):
                    c.over = True

        return Obj(update=update, drawBack=lambda p: each(p, "back"), draw=lambda p: each(p, "front"))

    return create


def shiftKeys(keys, dt, dx=0, **over):
    """Reaproveita as chaves de um ato num golpe maior: dt mais tarde, dx adiante, com `over` sobre cada pose."""
    out = []
    for k in keys:
        t, pose = k[0], k[1]
        how = k[2] if len(k) > 2 else None
        np_ = Obj(pose)
        np_.update(over)
        np_.x = (pose.get("x") or 0) + dx
        out.append([t + dt, np_, how] if how is not None else [t + dt, np_])
    return out


def shiftHits(hits, dt):
    out = []
    for h in hits:
        n = Obj(h)
        n.t = h["t"] + dt
        out.append(n)
    return out
