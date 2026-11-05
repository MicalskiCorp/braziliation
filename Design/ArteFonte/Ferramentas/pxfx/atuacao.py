"""Atuação: o que o corpo faz em volta de um efeito — poses no tempo, impactos, tempo de jogo.

Port da parte de dados de `src/core/act.js` do PixelFX (MIT), que adapta como o Hollow Crown
toca suas habilidades (https://github.com/rehan-remade/hollow-crown), MIT License,
Copyright (c) 2026 rehan-remade: poses em degraus de 12 fps, congelamento no impacto, tremor.

Uma trilha é [[t, pose, chegada], ...]: `chegada` diz como a pose chega — suave (padrão),
"out" (rápido e assenta), "in" (devagar e acelera), "line" (constante), "snap" (segura a pose
anterior e pula na chave). Membros andam em degraus inteiros de 12 fps contados de cada chave,
para lerem como desenho segurado; o deslocamento dos pés no chão (x, y) continua suave.
"""
from __future__ import annotations

import math

from .esqueleto.bipede import STAND


def _lerp(a, b, u):
    return a + (b - a) * u


def _num(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def lerpPose(a, b, u):
    """Entre duas poses: números se movem; o resto muda na chave posterior."""
    out = dict(STAND)
    out.update(a or {})
    Bp = dict(STAND)
    Bp.update(b or {})
    for k, v in Bp.items():
        if _num(v) and _num(out.get(k)):
            out[k] = _lerp(out[k], v, u)
        elif out.get(k) is None and _num(v):
            out[k] = v
    # o que a pose posterior não menciona volta ao padrão
    for k in ("hx", "hy", "lean", "crouch"):
        if (b or {}).get(k) is None and Bp.get(k) is None and _num(out.get(k)):
            out[k] = _lerp(out[k], 0, u)
    if Bp.get("wl") is None and _num(out.get("wl")):
        out["wl"] = _lerp(out["wl"], 1, u)
    return out


EASES = {"out": lambda u: 1 - (1 - u) * (1 - u), "in": lambda u: u * u, "line": lambda u: u}


def _suave(u):
    return u * u * (3 - 2 * u)


def poseAt(track, t, passo=12):
    """A pose no tempo t numa trilha de chaves. passo: fps dos degraus dos membros (12 no original)."""
    if t <= track[0][0]:
        return track[0][1]
    for i in range(len(track) - 1):
        t0, a = track[i][0], track[i][1]
        t1, b = track[i + 1][0], track[i + 1][1]
        how = track[i + 1][2] if len(track[i + 1]) > 2 else None
        if t >= t1:
            continue
        if how == "snap":
            return a
        e = EASES.get(how, _suave)
        stepped = t0 + math.floor((t - t0) * passo + 1e-6) / passo
        out = lerpPose(a, b, e((stepped - t0) / (t1 - t0)))
        u = e((t - t0) / (t1 - t0))
        out["x"] = _lerp(a.get("x") or 0, b.get("x") or 0, u)
        out["y"] = _lerp(a.get("y") or 0, b.get("y") or 0, u)
        return out
    return track[-1][1]


def isHeld(track, t):
    """O corpo está entre chaves quase iguais, ou depois da última? (aí ele respira)."""
    if t >= track[-1][0] or t < track[0][0]:
        return True
    for i in range(len(track) - 1):
        if t >= track[i + 1][0]:
            continue
        a = dict(STAND)
        a.update(track[i][1])
        b = dict(STAND)
        b.update(track[i + 1][1])
        return track[i + 1][0] - track[i][0] > 0.4 and all(
            abs((a.get(k) or 0) - (b.get(k) or 0)) < 1.5 for k in ("fx", "fy", "bx", "by", "crouch", "lean", "x", "y"))
    return True


def actSpan(mod):
    a = getattr(mod, "act", None) or {}
    meta = getattr(mod, "meta", None) or {}
    D = meta.get("duration", 1)
    k = a.get("poses")
    de = min(0, k[0][0] if k else 0)
    ate = math.inf if meta.get("loop") else max(D, k[-1][0] if k else 0)
    return {"from": de, "to": ate}


def actTiming(mod):
    """O tempo do ato como dado, para o jogo: preparação, recuperação, impactos com congelamento."""
    a = getattr(mod, "act", None)
    if not a:
        return None
    span = actSpan(mod)
    meta = getattr(mod, "meta", None) or {}
    D = meta.get("duration", 1)
    alvos = a.get("targets") or ([a["target"]] if a.get("target") else [])
    return {
        "windup": -span["from"],
        "recovery": 0 if meta.get("loop") else max(0, span["to"] - D),
        "onBody": bool(a.get("onBody")),
        "targets": [g.get("x", 66) for g in alvos],
        "hits": [{"t": h["t"], "freeze": h.get("stop", 0), "shake": h.get("shake", 0), "amp": h.get("amp", 0),
                  "push": 0 if h.get("target") is False else h.get("push", 1.2), "skin": h.get("skin"), "at": h.get("at")}
                 for h in a.get("hits", [])],
        "poses": [{"t": p[0], "how": p[2] if len(p) > 2 else "smooth", "pose": p[1]} for p in a.get("poses", [])],
    }
