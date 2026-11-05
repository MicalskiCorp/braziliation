"""Vetores 3D e matrizes 3×3 (listas de 9, por linha) — as mesmas contas do `rig.js` do PixelFX (MIT)."""
from __future__ import annotations

import math

DEG = math.pi / 180


def add(a, b):
    return [a[0] + b[0], a[1] + b[1], a[2] + b[2]]


def sub(a, b):
    return [a[0] - b[0], a[1] - b[1], a[2] - b[2]]


def mul(a, s):
    return [a[0] * s, a[1] * s, a[2] * s]


def dot(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def cross(a, b):
    return [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]]


def length(a):
    return math.hypot(a[0], a[1], a[2])


def unit(a):
    return mul(a, 1 / (length(a) or 1e-6))


def rotY(t):
    c, s = math.cos(t), math.sin(t)
    return [c, 0, s, 0, 1, 0, -s, 0, c]


def rotZ(t):
    c, s = math.cos(t), math.sin(t)
    return [c, -s, 0, s, c, 0, 0, 0, 1]


def rotX(t):
    c, s = math.cos(t), math.sin(t)
    return [1, 0, 0, 0, c, -s, 0, s, c]


def mm(A, B):
    o = [0.0] * 9
    for r in range(3):
        for c in range(3):
            o[r * 3 + c] = A[r * 3] * B[c] + A[r * 3 + 1] * B[3 + c] + A[r * 3 + 2] * B[6 + c]
    return o


def mv(M, v):
    return [M[0] * v[0] + M[1] * v[1] + M[2] * v[2], M[3] * v[0] + M[4] * v[1] + M[5] * v[2],
            M[6] * v[0] + M[7] * v[1] + M[8] * v[2]]


def tv(M, v):
    """Transposta de M vezes v (volta do mundo para o espaço do osso)."""
    return [M[0] * v[0] + M[3] * v[1] + M[6] * v[2], M[1] * v[0] + M[4] * v[1] + M[7] * v[2],
            M[2] * v[0] + M[5] * v[1] + M[8] * v[2]]


def clamp01(v):
    return max(0.0, min(1.0, v))


def ik(a, target, L1, L2, pole, margem=0.02):
    """Cinemática inversa de dois ossos: de onde está o ombro (a) e onde a mão deve ir, acha o cotovelo.
    margem: folga do alcance máximo, em px — escala junto com o corpo (0,02 no boneco de 38 px)."""
    to = sub(target, a)
    d = length(to)
    reach = L1 + L2 - margem
    if d > reach:
        to = mul(to, reach / d)
        d = reach
    u = unit(to)
    along = (L1 * L1 - L2 * L2 + d * d) / (2 * d)
    h = math.sqrt(max(0, L1 * L1 - along * along))
    v = sub(pole, mul(u, dot(pole, u)))
    v = unit(cross(u, [0, 0, 1])) if length(v) < 1e-4 else unit(v)
    return {"joint": add(a, add(mul(u, along), mul(v, h))), "end": add(a, to), "u": u, "v": v}


def frame(t, R):
    return {"t": t, "R": R}


def boneFrame(a, b, pole):
    """Um referencial ao longo de um osso: o x local corre pelo osso."""
    x = unit(sub(b, a))
    y = sub(pole, mul(x, dot(pole, x)))
    y = unit(cross(x, [0, 0, 1])) if length(y) < 1e-4 else unit(y)
    z = cross(x, y)
    return frame(a, [x[0], y[0], z[0], x[1], y[1], z[1], x[2], y[2], z[2]])
