#!/usr/bin/env python3
"""Gerador da spec de ATAQUE do Autômato Abandonado (64x64).

Linguagem visual da ancora (enm_automato_idle_f1.2x.spec.json):
- massas de latao (cabeca, torso, ombreira) sombreadas por DISTANCIA DE BORDA:
  aro claro (8/D) no lado topo-esquerda, miolo 7, aro 6 no lado baixo-direita,
  rim 2/1 de contato na sombra + escurecimento vertical na base.
- membros de ferro como HASTES LISTRADAS (idle: "4433" bracos, "3311" pernas).
- recesso 2 no peito com engrenagem de cobre (9) e cubo 5.
"""
import json
import math
from pathlib import Path

W = H = 64
g = [["."] * W for _ in range(H)]
L2 = (-0.50, -0.62)  # luz vinda do topo-esquerda (2D)


def put(x, y, c):
    if 0 <= x < W and 0 <= y < H:
        g[y][x] = c


def get(x, y):
    return g[y][x] if (0 <= x < W and 0 <= y < H) else "."


# ------------------------------------------------------------------ rampas
BRASS = [(0.13, "2"), (0.40, "6"), (0.86, "7"), (9.9, "8")]
IRON = [(0.16, "1"), (0.46, "3"), (0.84, "4"), (9.9, "5")]
DITHER_PAIRS = set()  # ancora usa bandas chapadas; dithering de linha inteira lia como ruido em 1x


def pick(v, ramp, x, y):
    for i, (thr, c) in enumerate(ramp):
        if v < thr:
            if i + 1 < len(ramp) and (thr - v) < 0.028 and (x + y) % 2 == 0                     and (c, ramp[i + 1][1]) in DITHER_PAIRS:
                return ramp[i + 1][1]
            return c
    return ramp[-1][1]


# ------------------------------------------------------------------ massas
def shade_mass(cells, ramp, cap=6, vshade=0.20, contrast=0.40):
    cs = set(cells)
    ys = [c[1] for c in cells]
    y0, y1 = min(ys), max(ys)
    span = max(1, y1 - y0)
    for (x, y) in cells:
        dl = du = dr = dd = 0
        while dl < cap and (x - dl - 1, y) in cs:
            dl += 1
        while du < cap and (x, y - du - 1) in cs:
            du += 1
        while dr < cap and (x + dr + 1, y) in cs:
            dr += 1
        while dd < cap and (x, y + dd + 1) in cs:
            dd += 1
        du_e = min(cap, du * 2 + 1)
        dd_e = min(cap, dd * 2 + 1)
        tl, br = min(dl, du_e), min(dr, dd_e)
        t = max(-1.0, min(1.0, (br - tl) / cap))
        v = 0.5 + contrast * t - vshade * ((y - y0) / span) ** 1.5
        put(x, y, pick(v, ramp, x, y))


def ellipse_cells(cx, cy, rx, ry, shear=0.0):
    out = []
    for y in range(int(cy - ry) - 1, int(cy + ry) + 2):
        for x in range(int(cx - rx - abs(shear) * ry) - 2, int(cx + rx + abs(shear) * ry) + 3):
            nx = (x - (cx + (cy - y) * shear)) / rx
            ny = (y - cy) / ry
            if nx * nx + ny * ny <= 1.0 and 0 <= x < W and 0 <= y < H:
                out.append((x, y))
    return out


def rrect_cells(x0, y0, x1, y1, rad=2):
    out = []
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            cx = min(max(x, x0 + rad), x1 - rad)
            cy = min(max(y, y0 + rad), y1 - rad)
            if math.hypot(x - cx, y - cy) <= rad + 0.35:
                out.append((x, y))
    return out


# ------------------------------------------------------------------ hastes
def rod(x1, y1, x2, y2, stripes):
    """Haste listrada: stripes[0] = lado da luz, stripes[-1] = lado da sombra."""
    dx, dy = x2 - x1, y2 - y1
    ln = math.hypot(dx, dy)
    ux, uy = dx / ln, dy / ln
    px, py = -uy, ux
    if px * L2[0] + py * L2[1] > 0:  # garante que -p aponta para a luz
        px, py = -px, -py
    n = len(stripes)
    r = n / 2.0
    for y in range(int(min(y1, y2) - r) - 1, int(max(y1, y2) + r) + 2):
        for x in range(int(min(x1, x2) - r) - 1, int(max(x1, x2) + r) + 2):
            t = ((x - x1) * ux + (y - y1) * uy) / ln
            if t < 0.0 or t > 1.0:
                continue
            s = (x - x1) * px + (y - y1) * py
            if abs(s) > r - 0.02:
                continue
            put(x, y, stripes[min(n - 1, int((s + r) / (2 * r) * n))])


def joint(cx, cy, r, stripes):
    """Junta circular (rotula) com as mesmas listras diagonais."""
    for y in range(int(cy - r), int(cy + r) + 1):
        for x in range(int(cx - r), int(cx + r) + 1):
            if math.hypot(x - cx, y - cy) > r:
                continue
            u = ((x - cx) * L2[0] + (y - cy) * L2[1]) / r  # >0 = lado da luz
            idx = int((1 - max(-1.0, min(1.0, u))) / 2 * len(stripes))
            put(x, y, stripes[min(len(stripes) - 1, idx)])


ARM = ["4", "4", "3", "3"]
ARM_BACK = ["3", "3", "3", "1"]
LEG = ["3", "3", "3", "1", "1"]
SHIN = ["3", "3", "1", "1"]
STRIKE = ["5", "4", "4", "3", "1"]

# ============================================================ CAMADA DE TRAS
# braco esquerdo recuado (contrapeso do golpe)
# fica FORA do contorno do torso para ler na silhueta (contrapeso do golpe)
rod(19, 27, 9, 34, ARM_BACK)
joint(9, 34, 2.4, ARM_BACK)
rod(9, 34, 6, 43, ARM_BACK)
joint(6, 43.5, 2.4, ARM_BACK)

# pernas em afundo
rod(25, 43, 19, 52, LEG)
joint(19, 52, 3.0, LEG)
rod(19, 52, 15, 58, SHIN)
rod(34, 43, 43, 51, LEG)
joint(43, 51, 3.0, LEG)
rod(43, 51, 45, 58, SHIN)

# pe dianteiro (chapa apoiada)
for (y, x0, x1, c) in [(58, 42, 48, "3"), (59, 41, 50, "3"), (60, 40, 52, "3"),
                       (61, 40, 52, "1"), (62, 40, 52, "1"), (63, 41, 52, "1")]:
    for x in range(x0, x1 + 1):
        put(x, y, c)
put(46, 60, "1")
put(42, 58, "4"); put(43, 58, "4"); put(41, 59, "4")

# pe traseiro (cunha: bico no chao, calcanhar erguido = impulso)
for (y, x0, x1, c) in [(56, 13, 17, "3"), (57, 12, 18, "3"), (58, 11, 19, "3"),
                       (59, 11, 20, "1"), (60, 12, 21, "1"), (61, 13, 21, "1"),
                       (62, 15, 21, "1"), (63, 17, 21, "1")]:
    for x in range(x0, x1 + 1):
        put(x, y, c)
put(13, 56, "4"); put(14, 56, "4"); put(12, 57, "4"); put(11, 58, "4")

# pescoco articulado inclinado a frente
rod(33.5, 22, 36, 16, ["4", "4", "3", "3", "3", "1"])

# ============================================================ TORSO
shade_mass(ellipse_cells(29, 33, 15, 12, shear=0.30), BRASS, cap=6, vshade=0.14, contrast=0.44)

# recesso do peito
REC = ellipse_cells(28, 34, 8.0, 6.5, shear=0.30)
rec = set(REC)
for (x, y) in REC:
    put(x, y, "2")
for (x, y) in REC:  # borda dura do recesso (sombra em cima/esquerda)
    if (x - 1, y) not in rec or (x, y - 1) not in rec:
        put(x, y, "1")
    elif (x + 1, y) not in rec and (x, y + 1) not in rec:
        put(x, y, "6")

# engrenagem de cobre (dentes rotacionados em relacao ao idle)
GCX, GCY = 28.0, 34.0
for y in range(27, 42):
    for x in range(19, 38):
        cxs = GCX + (GCY - y) * 0.30
        dx, dy = x - cxs, y - GCY
        r = math.hypot(dx, dy)
        rmax = 5.9 if (math.cos(math.atan2(dy, dx) * 8 + 0.45) > 0.30) else 4.2
        u = (dx * L2[0] + dy * L2[1]) / max(r, 0.01)
        if 2.4 <= r <= rmax:
            put(x, y, "8" if u > 0.55 else "9")
        elif r < 2.4:
            put(x, y, "5" if r <= 1.5 else ("8" if u > 0.3 else "9"))

# specular do torso (2-3 px, unico ponto de luz)
put(23, 25, "D"); put(24, 25, "D"); put(23, 26, "D")

# rebites no aro do torso
for (rx_, ry_, c) in [(21, 30, "8"), (38, 26, "8"), (40, 38, "6"), (23, 42, "6")]:
    if get(rx_, ry_) != ".":
        put(rx_, ry_, c)

# ============================================================ CABECA
HEAD = rrect_cells(29, 8, 44, 17, rad=2)
shade_mass(HEAD, BRASS, cap=4, vshade=0.12, contrast=0.42)
head = set(HEAD)
put(30, 9, "D"); put(31, 9, "D"); put(30, 10, "D")
for x in range(30, 44):  # cinta baixa do cilindro (queixo)
    if (x, 16) in head and get(x, 16) in ("7", "8", "D"):
        put(x, 16, "6")

# visor escuro + lente de vidro acesa, voltada para frente
for y in range(10, 15):
    for x in range(36, 43):
        if (x, y) in head:
            put(x, y, "2")
for x in range(36, 43):
    if (x, 10) in head:
        put(x, 10, "1")
for y in range(11, 14):
    for x in range(37, 42):
        put(x, y, "E")
put(36, 11, "5"); put(36, 12, "5"); put(36, 13, "1")
put(37, 11, "D"); put(38, 11, "D"); put(37, 12, "5")
put(41, 13, "2"); put(42, 12, "1"); put(42, 13, "1")

# ============================================================ BRACO DE ATAQUE
shade_mass(ellipse_cells(41.5, 28, 6.8, 6.8), BRASS, cap=5, vshade=0.14)
PAULD = set(ellipse_cells(41.5, 28, 6.8, 6.8))
for (x, y) in sorted(PAULD):
    if (x - 1, y) not in PAULD and get(x - 1, y) in ("7", "8", "D"):
        put(x - 1, y, "6")
put(38, 24, "D"); put(45, 32, "2")
rod(45, 28, 55, 28, STRIKE)
for y in range(25, 32):  # luva de pistao em latao
    for x in range(48, 52):
        if get(x, y) != ".":
            put(x, y, {48: "8", 49: "7", 50: "7", 51: "6"}[x] if y > 25 else "8")
FIST = rrect_cells(54, 22, 62, 34, rad=3)
shade_mass(FIST, IRON, cap=3, vshade=0.10, contrast=0.36)
fist = set(FIST)
for y in range(25, 33):  # divisao dos dedos (vinco vertical unico)
    if (57, y) in fist:
        put(57, y, "1")
for y in range(22, 35):  # sombra de contato punho/haste
    if (54, y) in fist:
        put(54, y, "1")
put(55, 24, "5"); put(56, 23, "5")

# ============================================================ ACABAMENTO
# rim de contato mais escuro na borda inferior/direita do corpo
for y in range(40, 46):
    xs = [x for x in range(W) if g[y][x] in ("6", "7", "2")]
    if xs:
        put(max(xs), y, "1")

rows = ["".join(r) for r in g]
assert len(rows) == 64 and all(len(r) == 64 for r in rows)

spec = {
    "name": "enm_automato_attack_f1",
    "size": [64, 64],
    "palette": "../../../../../ArteConceitual/Paletas/blumenau.json",
    "notes": (
        "Frame de ATAQUE (golpe): autômato Da Vinci em investida — torso inclinado à frente, "
        "braço direito estendido em soco com punho de ferro cerrado, braço esquerdo recuado como "
        "contrapeso, pernas em afundo com calcanhar traseiro erguido. Lente acesa (núcleo D) e "
        "engrenagem do peito com dentes rotacionados em relação ao idle. Mesma linguagem do "
        "enm_automato_idle_f1.2x: latão em bandas 2/6/7/8(+D) por distância de borda com luz no "
        "topo-esquerda; ferro em hastes listradas 4433 / 3311; recesso 2 com engrenagem 9 e cubo 5."
    ),
    "rows": rows,
}

Path(__file__).with_name("enm_automato_attack_f1.spec.json").write_text(
    json.dumps(spec, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

for i, r in enumerate(rows):
    print("%02d|%s|" % (i, r))
print("cores:", sorted(set("".join(rows)) - {"."}))
