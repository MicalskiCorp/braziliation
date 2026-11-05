"""Quadros e instâncias vivas de efeito.

Port de `src/core/fx.js` do PixelFX (MIT). Um quadro tem `color` (pixels opacos) e
`light` (brilho aditivo); `composite()` junta os dois em RGBA.

Convenção de efeito em Python (ver PORT.md): um módulo com `meta` e `draw(p, t, o)`
(efeito puro) ou `create(o)` (simulado) devolvendo um objeto com `update(dt)`,
`draw(p)` e, opcionalmente, `drawBack(p)`. As funções podem aceitar menos
argumentos que o JS passa — o adaptador abaixo chama cada uma com o que ela aceita.
"""
from __future__ import annotations

import inspect
import math
import re

import numpy as np

from .ator import stockActor
from .cor import fit, toHex
from .matematica import clamp
from .objeto import Obj, obj
from .pintor import Painter

INF = math.inf
FADE = 0.3


class Frame:
    """w × h pixels com o canto em (ox, oy) no mundo. Mesmo formato dos quadros do Sprite Fusion."""

    __slots__ = ("w", "h", "ox", "oy", "color", "light", "_painter")

    def __init__(self, w, h, ox=0, oy=0):
        self.w, self.h, self.ox, self.oy = w, h, ox, oy
        self.color = [0] * (w * h)
        self.light = [0] * (w * h)
        self._painter = None


def createFrame(w, h, ox=0, oy=0):
    return Frame(w, h, ox, oy)


def clearFrame(f):
    n = f.w * f.h
    f.color[:] = [0] * n
    f.light[:] = [0] * n
    return f


def painterFor(frame):
    """O pintor de um quadro (um por quadro, reaproveitado)."""
    if frame._painter is None:
        frame._painter = Painter(frame)
    return frame._painter.reset()


_HEXRE = re.compile(r"^#[0-9a-f]{3,8}$", re.I)


def _is_ramp(v):
    return isinstance(v, (list, tuple)) and len(v) > 0 and all(
        isinstance(c, int) or (isinstance(c, str) and _HEXRE.match(c)) for c in v)


def resolveOptions(meta, o=None):
    """Opções do efeito: os padrões dele com os do chamador por cima. Rampa de tamanho
    diferente do padrão é reamostrada para o tamanho do padrão."""
    o = o or {}
    defaults = (meta or {}).get("options") or {}
    opts = Obj(defaults)
    opts.update(o)
    for k, d in defaults.items():
        if _is_ramp(d) and _is_ramp(o.get(k)) and len(o[k]) != len(d):
            opts[k] = [toHex(c) for c in fit(o[k], len(d))]
    if meta and meta.get("actor") and not opts.get("actor"):
        opts.actor = stockActor(2 if meta.get("actor") == 2 else 1)
    return opts


def _aridade(fn):
    """Chamador que passa a fn só os argumentos posicionais que ela aceita."""
    if fn is None:
        return None
    try:
        params = list(inspect.signature(fn).parameters.values())
    except (TypeError, ValueError):
        return fn
    if any(p.kind == p.VAR_POSITIONAL for p in params):
        return fn
    n = sum(1 for p in params if p.kind in (p.POSITIONAL_ONLY, p.POSITIONAL_OR_KEYWORD))
    return lambda *a: fn(*a[:n])


def _get(mod, nome):
    if isinstance(mod, dict):
        return mod.get(nome)
    return getattr(mod, nome, None)


class FxInstance:
    """Instância viva de um módulo de efeito: update(dt), draw(frame, layer), stop(), done()."""

    def __init__(self, mod, o=None):
        self.mod = mod
        self.meta = obj(_get(mod, "meta") or {})
        self.options = resolveOptions(self.meta, o)
        create = _get(mod, "create")
        self.impl = create(self.options) if create else mod
        self._upd = _aridade(_get(self.impl, "update"))
        self._draw = _aridade(_get(self.impl, "draw"))
        self._back = _aridade(_get(self.impl, "drawBack"))
        self.D = self.meta.get("duration", 1)
        self.t = 0.0
        self.stopAt = INF

    def update(self, dt):
        self.t += dt
        if not self._upd:
            return
        # simulações andam a 120 Hz ou mais fino, qualquer que seja o fps de quem chama
        n = max(1, math.ceil(dt * 120 - 1e-9))
        for _ in range(n):
            self._upd(dt / n, self.options)

    def draw(self, frame, layer=None):
        o = self.options
        p = painterFor(frame)
        p.place(o.get("x") or 0, o.get("y") or 0, bool(o.get("flip")), o.get("angle") or 0,
                o.get("escala") or self.meta.get("escala") or 1)
        p.fade = 1 if self.stopAt == INF else clamp(1 - (self.t - self.stopAt) / FADE)
        lk = o.get("light")
        p.lightK = 1 if lk is None else lk
        tt = self.t % self.D if self.meta.get("loop") else min(self.t, self.D)
        if layer != "front" and self._back:
            p.layer = "back"
            self._back(p, tt, o)
        if layer != "back" and self._draw:
            p.layer = "front"
            self._draw(p, tt, o)

    def stop(self):
        """Deixa terminar: loops somem em fade, one-shots são cortados."""
        if self.stopAt == INF:
            self.stopAt = self.t

    def done(self):
        return self.t - self.stopAt >= FADE or (not self.meta.get("loop") and self.t >= self.D)


def createFx(mod, o=None):
    return FxInstance(mod, o)


def composite(f, bg=None, lightK=1.0):
    """Cor sobre um fundo, mais a luz, em RGBA (ndarray h × w × 4, uint8).

    bg: None (transparente), uma cor, ou uma lista do tamanho do quadro. Sobre transparência a
    luz vira cor com alpha (o canal mais forte), que lê como aditiva sobre fundo escuro."""
    C = np.asarray(f.color, dtype=np.uint64).astype(np.uint32)
    L = np.asarray(f.light, dtype=np.uint64).astype(np.uint32) & 0xFFFFFF
    ca = (C >> 24).astype(np.float64)
    r = (C & 255).astype(np.float64)
    g = ((C >> 8) & 255).astype(np.float64)
    b = ((C >> 16) & 255).astype(np.float64)
    opaco = ca == 255
    a = np.where(opaco, 255.0, ca)
    if bg is not None:
        K = np.full(C.shape, bg & 0xFFFFFFFF, dtype=np.uint64) if isinstance(bg, int) else np.asarray(bg, dtype=np.uint64)
        K = K.astype(np.uint32)
        fr = ca / 255
        tr = ~opaco
        r = np.where(tr, r * fr + (K & 255) * (1 - fr), r)
        g = np.where(tr, g * fr + ((K >> 8) & 255) * (1 - fr), g)
        b = np.where(tr, b * fr + ((K >> 16) & 255) * (1 - fr), b)
        a = np.where(tr, 255.0, a)
    tem = L != 0
    if tem.any():
        lr = (L & 255).astype(np.float64) * lightK
        lg = ((L >> 8) & 255).astype(np.float64) * lightK
        lb = ((L >> 16) & 255).astype(np.float64) * lightK
        sob = tem & (a < 255)
        pa = a / 255
        pr, pg, pb = r * pa + lr, g * pa + lg, b * pa + lb
        na = np.minimum(1, np.maximum(pa, np.maximum(np.maximum(lr, lg), lb) / 255))
        ok = sob & (na > 0)
        nz = np.where(na > 0, na, 1)
        r2 = np.where(ok, np.minimum(255, pr / nz), r)
        g2 = np.where(ok, np.minimum(255, pg / nz), g)
        b2 = np.where(ok, np.minimum(255, pb / nz), b)
        a2 = np.where(ok, na * 255, a)
        cheio = tem & (a >= 255)
        r = np.where(cheio, np.minimum(255, r + lr), r2)
        g = np.where(cheio, np.minimum(255, g + lg), g2)
        b = np.where(cheio, np.minimum(255, b + lb), b2)
        a = a2
    out = np.stack([r, g, b, a], axis=-1)
    out = np.rint(np.clip(np.nan_to_num(out, nan=0.0), 0, 255)).astype(np.uint8)
    return out.reshape(f.h, f.w, 4)
