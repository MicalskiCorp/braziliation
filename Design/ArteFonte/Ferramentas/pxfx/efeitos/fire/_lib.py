"""Auxiliares dos efeitos de fogo: línguas de chama, lambidas, puffs que esfriam em fumaça,
brasas e faíscas, com o movimento em forma fechada para loops sem emenda.

Port de `src/fx/fire/_lib.js` do PixelFX (MIT). As receitas de língua, lambida, puff,
fumaça, brasa e faísca adaptam o fogo open-source do Sprite Fusion
(https://www.spritefusion.com/pixel-art-vfx/fire), MIT License, Copyright (c) 2026 Hugo Duprez.
"""
from __future__ import annotations

import math

from ... import P, PF, SMOKE_RAMP, WHITE, clamp, hex, jsround, mix, noise, rand, rng, wrap
from ...matematica import jsmod


def pnoise(x, period, seed=0):
    """Ruído suave em [-1, 1] que se repete a cada `period` células."""
    i = math.floor(x)
    f = x - i
    u = f * f * (3 - 2 * f)
    a, b = rand(wrap(i, period), seed), rand(wrap(i + 1, period), seed)
    return (a + (b - a) * u) * 2 - 1


def noiseFor(D):
    """Ruído para um loop de D s: N(tt, rate, seed, off) oscila ~rate vezes por segundo e é igual em tt e tt+D."""
    if not D:
        return lambda tt, rate, seed=0, off=0: noise(tt * rate + off, seed)

    def N(tt, rate, seed=0, off=0):
        Pp = max(1, jsround(rate * D))
        return pnoise((tt / D) * Pp + off, Pp, seed)

    return N


def looped(t, D, count, seed, make, draw):
    """Partículas sem emenda num loop de D s: cada uma nasce na sua fase e renasce a cada D."""
    for i in range(count):
        r = rng(seed, i)
        born = r.next() * D
        q = make(r, i)
        age = wrap(t - born, D)
        while age < q["life"]:
            draw(q, age, i)
            age += D


def flicker(N, s=0):
    return 0.74 + 0.16 * N(7.3, 1 + s) + 0.1 * N(19, 2 + s)


def hotFirst(F):
    """Rampa de fogo quente primeiro (H[0] branco .. H[8] brasa) a partir de uma paleta escuro → claro."""
    return list(reversed(F))


LAYERS = [[1, 1, 6], [0.76, 0.86, 4], [0.54, 0.68, 2], [0.3, 0.42, 0]]
BIG_LAYERS = [[1, 1, 6], [0.8, 0.9, 5], [0.62, 0.78, 4], [0.44, 0.6, 3], [0.26, 0.4, 1], [0.12, 0.22, 0]]
BACK_LAYERS = [[1, 1, 7], [0.76, 0.86, 5], [0.54, 0.68, 3], [0.3, 0.42, 2]]


def flameTongue(p, x, y, h, w, sx, N, n, H, layers=LAYERS, jit=0.5, wob=1.1):
    """Língua de chama em (x, y), h de altura, w meia largura na base, ponta varrida sx px."""
    if h < 1:
        return
    st = 1 / p.k  # escala (ADR-016): uma linha por pixel de TELA, não por unidade local
    for lw, lh, ri in layers:
        L = h * lh
        c = H[ri]
        r = 0
        while r <= L:
            u = r / max(1, L)
            half = w * lw * (1 - u) ** 0.85 * min(1, (r + 1.5) / 3.5) + N(9, n, r * 0.45) * jit
            if half >= 0.3:
                cx = x + sx * u * u * lh + N(4, n + 7, r * 0.2) * u * wob
                if p.k == 1:
                    Y = jsround(y - r)
                    for px in range(jsround(cx - half), jsround(cx + half) + 1):
                        p.px(px, Y, c)
                else:
                    q = cx - half
                    while q <= cx + half:
                        p.px(q, y - r, c)
                        q += st
            r += 1 if p.k == 1 else st


def flameBlade(p, x, y, ux, uy, ln, w, bend, N, n, H, layers=LAYERS, jit=0.5, wob=1.1):
    """A mesma língua deitada em qualquer direção (ux, uy): jatos, sopro, cauda de cometa."""
    if ln < 1:
        return
    nx, ny = -uy, ux
    st = 0.5 / p.k  # p.passo: ~meio pixel de tela em qualquer escala
    for lw, lh, ri in layers:
        L = ln * lh
        c = H[ri]
        r = 0.0
        while r <= L:
            u = r / max(1, L)
            half = w * lw * (1 - u) ** 0.85 * min(1, (r + 1.5) / 3.5) + N(9, n, r * 0.45) * jit
            if half >= 0.3:
                off = bend * u * u * lh + N(4, n + 7, r * 0.2) * u * wob
                cx, cy = x + ux * r + nx * off, y + uy * r + ny * off
                q = -half
                while q <= half:
                    p.px(cx + nx * q, cy + ny * q, c)
                    q += st
            r += st


def solid(p, x, y, r, c):
    """Disco cheio desenhado direto na tela (rápido; disco é igual espelhado ou girado)."""
    if r < 0.6:
        return p.px(x, y, c)
    r *= p.k
    cx, cy = p.toX(x, y), p.toY(x, y)
    r2 = r * r
    for sy in range(math.floor(cy - r), math.ceil(cy + r) + 1):
        dy = sy + 0.5 - cy
        s2 = r2 - dy * dy
        if s2 < 0:
            continue
        s = math.sqrt(s2)
        for sx in range(math.ceil(cx - s - 0.5), math.floor(cx + s - 0.5) + 1):
            p.put(sx, sy, c, 1)


def soft(p, x, y, r, c, a):
    """Disco translúcido na tela: fumaça e névoa."""
    if a <= 0.004:
        return
    if r < 0.5:
        return p.blend(x, y, c, a)
    r *= p.k
    cx, cy = p.toX(x, y), p.toY(x, y)
    r2 = r * r
    for sy in range(math.floor(cy - r), math.ceil(cy + r) + 1):
        dy = sy + 0.5 - cy
        s2 = r2 - dy * dy
        if s2 < 0:
            continue
        s = math.sqrt(s2)
        for sx in range(math.ceil(cx - s - 0.5), math.floor(cx + s - 0.5) + 1):
            p.blendPx(sx, sy, c, a)


def firePuff(p, x, y, k, size, frac, H, glowK=0.18, tx=0, ty=-1):
    """Bola de chama com vida k esfriando na rampa H: borda escura, miolo aceso, linguinha no topo, luz."""
    age = 1 - k
    n = len(H)
    heat = min(0.999, age ** 0.62 + frac * 0.1)
    idx = min(n - 2, math.floor(heat * (n - 1)))
    r = size * (0.55 + 0.45 * min(1, age * 7)) * (1 - age * 0.55)
    c = H[idx]
    if idx >= n - 2:
        return soft(p, x, y, r, c, min(1, k * 3) * 0.85)
    solid(p, x, y, r, H[min(n - 1, idx + 2)])
    if r > 1.6 and ty > -0.99:
        solid(p, x + tx * r * 1.5, y + ty * r * 1.5, r * 0.3, H[min(n - 1, idx + 1)])
    solid(p, x - r * 0.16, y - r * 0.22, r * 0.78, c)
    if r > 1.6:
        solid(p, x + tx * r * 0.9, y + ty * r * 0.9, r * 0.42, c)
    if idx <= 3 and r > 1.8:
        solid(p, x - r * 0.28, y - r * 0.34, r * 0.36, H[max(0, idx - 1)])
    if idx < 6:
        p.glow(x, y, r * 2.4 + 2, c, glowK * k)


def lick(p, x, y, k, s, H):
    """Lambida: bolha de chama arrancada da ponta, borda vermelha e miolo amarelo, encolhendo ao subir."""
    r = s * (0.4 + 0.6 * k)
    solid(p, x, y, r + 0.6, H[5] if k > 0.5 else H[6])
    if k > 0.35:
        solid(p, x, y - 0.3, r * 0.6, H[2] if k > 0.7 else H[4])


def _rampAt(r, t):
    return r[min(len(r) - 1, max(0, math.floor(t * len(r))))]


def smokePuff(p, x, y, k, size, col=0, big=False, aMul=1):
    """Puff de fumaça com vida k: três discos suaves, inchando e afinando."""
    age = 1 - k
    r = size * (0.65 + min(1, age * 2.5) * 0.45 + age * (0.5 if big else 0.4))
    a = min(1, age * 12) * min(1, k * 2.4) * (0.7 if big else 0.58) * aMul
    c = mix(col, _rampAt(SMOKE_RAMP, age), age) if col else _rampAt(SMOKE_RAMP, age * 1.05)
    soft(p, x, y, r, c, a * 0.45)
    soft(p, x + r * 0.05, y + r * 0.06, r * 0.74, c, a * 0.62)
    if age < 0.5:
        soft(p, x - r * 0.22, y - r * 0.3, r * 0.5, mix(c, WHITE, 0.12), a * 0.4 * (1 - age * 2))


def ember(p, x, y, k, size, cols, ph):
    """Brasa com vida k esfriando por cols [quente, morna, fria, borda], piscando perto do fim."""
    if k < 0.25 and math.sin(ph) < 0:
        return
    c = cols[0] if k > 0.6 else cols[1] if k > 0.3 else cols[2]
    if size >= 2:
        rim = cols[2] if k > 0.45 else cols[3]
        p.px(x - 1, y, rim)
        p.px(x + 1, y, rim)
        p.px(x, y - 1, rim)
        p.px(x, y + 1, rim)
        p.px(x, y, c)
        p.glow(x, y, 8, c, 0.4 * k)
        return
    p.px(x, y, c)
    if size > 1.4:
        p.px(x, y + 1, cols[3])
    p.glow(x, y, 3 + size, c, 0.35 * k)


def spark(p, x, y, vx, vy, k, cols):
    """Faísca: risco esticado na velocidade, cabeça quente, cauda mais fria e um ponto de luz."""
    sp = math.hypot(vx, vy) or 1
    ux, uy = vx / sp, vy / sp
    ln = min(9, 1 + sp * 0.022)
    head = cols[0] if k > 0.6 else cols[1] if k > 0.3 else cols[2]
    p.line(x - ux * ln, y - uy * ln, x - ux * ln * 0.4, y - uy * ln * 0.4, head if k > 0.5 else cols[-1])
    p.line(x - ux * ln * 0.45, y - uy * ln * 0.45, x, y, head)
    p.glow(x, y, 3, head, 0.45 * k)


def _along(x, v, a, k, t):
    if k <= 0:
        return [x + v * t + 0.5 * a * t * t, v + a * t]
    e = math.exp(-k * t)
    vt = a / k
    return [x + vt * t + ((v - vt) * (1 - e)) / k, vt + (v - vt) * e]


def drift(x, y, vx, vy, t, ax, ay, kx, ky):
    """Onde um corpo está t s após sair de (x, y) a (vx, vy), aceleração (ax, ay), arrasto (kx, ky)."""
    X = _along(x, vx, ax, kx, t)
    Y = _along(y, vy, ay, ky, t)
    return [X[0], Y[0], X[1], Y[1]]


def sparkAt(x, y, vx, vy, t, floor=0, g=427, k=2.2):
    """Voo de faísca: cai, freia e quica no chão em y = floor, perdendo velocidade."""
    s = [x, y, vx, vy]
    left = t
    for _ in range(3):
        e = drift(s[0], s[1], s[2], s[3], left, 0, g, k, k)
        if e[1] < floor or s[1] >= floor:
            return e
        lo, hi = 0.0, left
        for _i in range(16):
            m = (lo + hi) / 2
            if drift(s[0], s[1], s[2], s[3], m, 0, g, k, k)[1] < floor:
                lo = m
            else:
                hi = m
        c = drift(s[0], s[1], s[2], s[3], hi, 0, g, k, k)
        s = [c[0], floor - 0.25, c[2] * 0.7, -abs(c[3]) * 0.45]
        left -= hi
    e = drift(s[0], s[1], s[2], s[3], left, 0, g, k, k)
    return e if e[1] < floor else [e[0], floor - 0.25, e[2], 0]


def floorLight(p, x, y, rx, ry, c, k):
    """Poça de luz no chão: elipse de brilho, k no meio caindo a 0 na borda."""
    if k <= 0.004 or rx < 1 or ry < 0.5:
        return

    def fn(px, py, out):
        dx, dy = (px - x) / rx, (py - y) / ry
        d = dx * dx + dy * dy
        if d >= 1:
            return
        f = 1 - math.sqrt(d)
        out.l = c
        out.k = f * f * k

    p.shade(x - rx, y - ry, x + rx, y + ry, fn)


def simDraw(p, ps, H, layer=None):
    """Um Particles do núcleo desenhado com os puffs de fogo recoloridos na rampa H."""
    todos = ps.list
    resto, fogo = [], []
    for q in todos:
        (fogo if q.k == P.FIRE else resto).append(q)

    def puffs(back):
        for q in fogo:
            if q.delay <= 0 and bool(q.flag & PF.BACK) == back:
                firePuff(p, q.x, q.y, q.life / q.max, q.size, math.fmod(q.seed, 1), H)

    ps.list = resto
    if layer != "front":
        ps.draw(p, "back")
        puffs(True)
    if layer != "back":
        puffs(False)
        ps.draw(p, "front")
    ps.list = todos


SMOKE1 = hex("#5b5566")


def burn(p, t, T, o):
    """Um fogo para loops, desenhado só de t. T: [[dx, dy, fração de altura, meia largura, de trás?], ...].
    o: {H, D, NL, S, height, lean, puffs, licks, smoke, embers, spread, glow, glowR, mid(), x, y, ...}.
    Devolve {tip(i, tt), fl}."""
    H, D, NL, S = o["H"], o["D"], o["NL"], o["S"]
    HC = o["height"]
    X = o.get("x", 0) or 0
    Y = o.get("y", 0) or 0
    Wd = o["spread"] if o.get("spread") is not None else 6
    G = o["glow"] if o.get("glow") is not None else 1
    wind = o["wind"] if o.get("wind") is not None else 3

    def N(rate, seed=0, off=0):
        return NL(t, rate, seed, off)

    def fla(tt):
        return 0.74 + 0.16 * NL(tt, 7.3, S + 1) + 0.1 * NL(tt, 19, S + 2)

    fl = fla(t)
    SMOKE = mix(SMOKE1, H[6], 0.25)
    EMB = [H[1], H[2], H[4], H[6]]
    GLOW = mix(mix(H[3], H[4], 0.5), WHITE, 0.25)
    R = rng(S, 77)

    def count(rate):
        return jsround(rate * D)

    TT = []
    for i, tg in enumerate(T):
        dx, dy, h, w, back = tg
        TT.append({"dx": dx + R.range(-0.3, 0.3), "y": dy, "h": 2 + HC * h * R.range(0.92, 1.08),
                   "w": w * R.range(0.92, 1.08), "back": back, "env": h, "n": (S * 7 + i) * 13})
    lean_k = o["lean"] if o.get("lean") is not None else 0.1

    def lean(tt):
        return NL(tt, 0.67, S + 90) * lean_k

    def height(i, tt):
        h, n = TT[i]["h"], TT[i]["n"]
        leap = max(0, NL(tt, 2.6, n + 70) - 0.55) * 1.4
        return (h + 0.25 * h * NL(tt, 3.3, n) + h * leap) * (0.9 + 0.1 * fla(tt))

    def sweep(i, tt, h):
        return NL(tt, 2.2, TT[i]["n"] + 40) * (1 + h * 0.08) + lean(tt) * h * 0.9 - clamp(TT[i]["dx"] * 0.3, -2.5, 2.5)

    def tip(i, tt):
        h = height(i, tt)
        return [X + TT[i]["dx"] + sweep(i, tt, h) * 0.85, Y + TT[i]["y"] - h * 0.88 + 3, h]

    def tongueAt(i):
        tg = TT[i]
        h = height(i, t)
        layers = BACK_LAYERS if tg["back"] else BIG_LAYERS if tg["w"] > 2.2 else LAYERS
        flameTongue(p, X + tg["dx"], Y + tg["y"], h, tg["w"], sweep(i, t, h), N, tg["n"], H, layers, 0.5, 1.1 + h * 0.04)

    smokeLife = o.get("smokeLife") or [1.6, 2.6]
    smokeSize = o["smokeSize"] if o.get("smokeSize") is not None else 3

    # a pluma: cada puff guarda o balanço que a pluma tinha quando saiu, e o requebro sobe por ela
    def mk_smoke(r, i):
        return {"x": r.range(-Wd, Wd) * 0.7, "y": -HC * 0.8 - r.range(0, 6), "vx": r.range(-2, 2),
                "vy": -r.range(10, 17), "life": r.range(*smokeLife), "s": r.range(0.7, 1.1) * smokeSize}

    def dr_smoke(q, age, i):
        x, y = drift(q["x"], q["y"], q["vx"], q["vy"], age, wind, -20, 1.6, 1)[:2]
        smokePuff(p, X + x + NL(t - age, 0.8, S + 60) * (1.5 + 2.5 * age), Y + y, 1 - age / q["life"], q["s"], SMOKE)

    looped(t, D, count(o["smoke"] if o.get("smoke") is not None else 12), S + 300, mk_smoke, dr_smoke)

    # puffs de chama soltos das pontas
    puffs = []

    def mk_puff(r, j):
        i = j % len(TT)
        fire = r.range(0.14, 0.3)
        smokes = r.chance(0.45)
        return {"i": i, "fire": fire, "smokes": smokes, "sl": r.range(0.8, 1.4), "ox": r.range(-1, 1),
                "oy": r.range(0, 4), "vx": r.range(-4, 4), "vy": -r.range(15, 30),
                "s": r.range(0.8, 1.6) * (0.8 + 0.6 * TT[i]["env"]), "f": r.next(), "life": fire + (1.4 if smokes else 0)}

    def dr_puff(q, age, _i):
        tx, ty = tip(q["i"], t - age)[:2]
        x, y, vx, vy = drift(tx + q["ox"], ty + q["oy"], q["vx"], q["vy"], min(age, q["fire"]), 0, -95, 5, 3.2)
        if age < q["fire"]:
            puffs.append([x, y, 1 - age / q["fire"], q["s"], q["f"]])
            return
        if age - q["fire"] > q["sl"]:
            return
        sx, sy = drift(x, y, vx * 0.6, vy * 0.6 - 6, age - q["fire"], wind, -16, 1.6, 1.2)[:2]
        smokePuff(p, sx, sy, 1 - (age - q["fire"]) / q["sl"], q["s"] * 0.7, 0)

    looped(t, D, len(TT) * count(o["puffs"] if o.get("puffs") is not None else 8), S + 200, mk_puff, dr_puff)
    for i in range(len(TT)):
        if TT[i]["back"]:
            tongueAt(i)
    for i in range(len(TT)):
        if not TT[i]["back"]:
            tongueAt(i)
    if o.get("mid"):
        o["mid"](fl)

    # lambidas arrancadas das pontas, subindo e encolhendo
    def mk_lick(r, j):
        return {"i": j % len(TT), "vx": r.range(-3, 3), "vy": -r.range(12, 22),
                "s": r.range(0.9, 1.6) * (0.8 + 0.5 * TT[j % len(TT)]["env"]), "life": 0.26}

    def dr_lick(q, age, _i):
        tx, ty = tip(q["i"], t - age)[:2]
        lick(p, tx + q["vx"] * age, ty - 2 + q["vy"] * age, 1 - age / q["life"], q["s"], H)

    looped(t, D, len(TT) * count(o["licks"] if o.get("licks") is not None else 4), S + 220, mk_lick, dr_lick)
    for x, y, k, s, f in puffs:
        firePuff(p, x, y, k, s, f, H)

    # brasas levadas pelo calor, vagando e esfriando
    def mk_ember(r, i):
        return {"x": r.range(-Wd, Wd), "y": -r.range(HC * 0.3, HC * 0.8), "vx": r.range(-15, 15),
                "vy": -r.range(25, 60), "life": r.range(1.1, 2.4), "s": 2 if r.chance(0.15) else r.range(1, 1.6),
                "a": r.range(0, 6.3), "b": r.range(0, 6.3)}

    def dr_ember(q, age, _i):
        x, y = drift(q["x"], q["y"], q["vx"], q["vy"], age, 0, -30, 1.6, 1.6)[:2]
        ember(p, X + x + 7 * (math.sin(age * 2.3 + q["a"]) - math.sin(q["a"])),
              Y + y + 2 * (math.sin(age * 3 + q["b"]) - math.sin(q["b"])), 1 - age / q["life"], q["s"], EMB,
              age * 40 + q["a"])

    looped(t, D, count(o["embers"] if o.get("embers") is not None else 8), S + 500, mk_ember, dr_ember)

    # luz: um banho largo e quente, luz nas chamas, um coração quente na base
    if G > 0:
        R1 = o["glowR"] if o.get("glowR") is not None else 46
        lx = X + lean(t) * 12
        p.glow(lx, Y - HC * 0.35, R1 * 1.5, GLOW, 0.22 * fl * G)
        p.glow(lx, Y - HC * 0.75, R1, GLOW, 0.34 * fl * G)
        p.glow(X, Y - HC * 0.2, R1 * 0.32, H[2], 0.2 * fl * G)
        p.glow(X, Y - 2, 8, H[0], 0.14 * fl * G)
    return {"tip": tip, "fl": fl}


__all__ = ["pnoise", "noiseFor", "looped", "flicker", "hotFirst", "LAYERS", "BIG_LAYERS", "BACK_LAYERS",
           "flameTongue", "flameBlade", "solid", "soft", "firePuff", "lick", "smokePuff", "ember", "spark",
           "drift", "sparkAt", "floorLight", "simDraw", "burn", "jsmod"]
