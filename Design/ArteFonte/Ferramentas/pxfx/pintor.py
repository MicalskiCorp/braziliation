"""O pintor: desenha nos dois buffers de um quadro.

Port de `src/core/painter.js` do PixelFX (MIT). Dois buffers:

- `color`: pixels OPACOS. Fade é dither ordenado (Bayer 4×4), nunca mistura — por
  isso este buffer passa no `palette_check.py` quando as cores vêm da paleta.
- `light`: brilho aditivo, composto por cima. É a única fonte de alpha parcial
  num sheet exportado (junto com `blend`/`disc`, que são translúcidos de verdade).

Os efeitos desenham em coordenadas locais em torno da própria origem; o pintor
posiciona, espelha e gira — e, acréscimo do Braziliation, ESCALA (`escala`, ADR-016):
com escala 1 tudo é idêntico ao original (paridade); com 2,5 a geometria cresce para
o grid de 96 px e as linhas continuam com 1 px, que é a densidade que o ADR-011 pede.
Primitivas de ponto (`px`, `dot`, `sprite`) não ganham área com a escala — efeito que
desenha "pontilhado" em passo fixo precisa usar `p.passo` (ver PORT.md).
"""
from __future__ import annotations

import math

from .cor import hex
from .fonte import FONTS, rasterText, textWidth
from .matematica import clamp, call, jsround, M32

# Limiares do Bayer 4×4: um pixel de alpha a é desenhado quando a passa do limiar da célula.
BAYER = [(v + 0.5) / 16 for v in (0, 8, 2, 10, 12, 4, 14, 6, 3, 11, 1, 9, 15, 7, 13, 5)]
INF = math.inf


class _Out:
    __slots__ = ("c", "a", "l", "k")


class Painter:
    def __init__(self, frame):
        self.frame = frame
        self._sprites = {}
        self.reset()

    def reset(self):
        """Relê o quadro e zera posição, fade e força da luz."""
        f = self.frame
        self.w, self.h = f.w, f.h
        self.ox, self.oy = int(f.ox), int(f.oy)
        self.C, self.L = f.color, f.light
        self.tx = self.ty = 0.0
        self.fx = 1
        self.cs, self.sn = 1.0, 0.0
        self.k = 1.0
        self.fade = 1.0
        self.lightK = 1.0
        self.layer = "front"
        return self

    @property
    def passo(self):
        """Passo de amostragem em unidades locais que dá ~1 px na tela (0,5 na escala 1)."""
        return 0.5 / self.k

    def place(self, x, y, flip=False, angle=0.0, escala=1.0):
        """Origem do efeito em (x, y) do quadro, espelhada se flip, girada por angle, escalada."""
        self.tx, self.ty = x, y
        self.fx = -1 if flip else 1
        self.cs, self.sn = math.cos(angle), math.sin(angle)
        self.k = escala
        return self

    # ---- transformações: espaço local (efeito) <-> tela (quadro)
    def toX(self, x, y):
        return self.tx + (x * self.fx * self.cs - y * self.sn) * self.k

    def toY(self, x, y):
        return self.ty + (x * self.fx * self.sn + y * self.cs) * self.k

    def fromX(self, sx, sy):
        dx, dy = sx - self.tx, sy - self.ty
        return ((dx * self.cs + dy * self.sn) * self.fx) / self.k

    def fromY(self, sx, sy):
        dx, dy = sx - self.tx, sy - self.ty
        return (-dx * self.sn + dy * self.cs) / self.k

    def cellX(self, x, y):
        if self.k != 1:
            return math.floor(self.toX(x, y))
        return math.floor(self.toX(math.floor(x) + 0.5, math.floor(y) + 0.5))

    def cellY(self, x, y):
        if self.k != 1:
            return math.floor(self.toY(x, y))
        return math.floor(self.toY(math.floor(x) + 0.5, math.floor(y) + 0.5))

    # ---- escritas cruas, espaço de tela, pixel inteiro. Cor 0 = "nada": nunca apaga.
    def put(self, sx, sy, c, a=1.0):
        if not c:
            return
        a *= self.fade
        if a < 1 and a <= BAYER[((sy & 3) << 2) | (sx & 3)]:
            return
        x, y = sx - self.ox, sy - self.oy
        if x < 0 or y < 0 or x >= self.w or y >= self.h:
            return
        self.C[y * self.w + x] = c & M32

    def add(self, sx, sy, c, k=1.0):
        k *= self.fade * self.lightK
        if k <= 0.004:
            return
        x, y = sx - self.ox, sy - self.oy
        if x < 0 or y < 0 or x >= self.w or y >= self.h:
            return
        i = y * self.w + x
        d = self.L[i]
        r = int(min(255, (d & 255) + (c & 255) * k))
        g = int(min(255, ((d >> 8) & 255) + ((c >> 8) & 255) * k))
        b = int(min(255, ((d >> 16) & 255) + ((c >> 16) & 255) * k))
        self.L[i] = 0xFF000000 | (b << 16) | (g << 8) | r

    def blendPx(self, sx, sy, c, a):
        """Mistura c sobre o que existe com alpha a (fumaça, vapor, névoa): translúcido de verdade."""
        a *= self.fade
        if not c or a <= 0.004:
            return
        x, y = sx - self.ox, sy - self.oy
        if x < 0 or y < 0 or x >= self.w or y >= self.h:
            return
        i = y * self.w + x
        d = self.C[i]
        da = (d >> 24) / 255
        oa = a + da * (1 - a)
        k = a / oa

        def ch(s):
            return int(((c >> s) & 255) * k + ((d >> s) & 255) * (1 - k)) & 255

        self.C[i] = ((int(oa * 255) & 255) << 24) | (ch(16) << 16) | (ch(8) << 8) | ch(0)

    def blend(self, x, y, c, a):
        self.blendPx(self.cellX(x, y), self.cellY(x, y), c, a)

    def disc(self, cx, cy, r, c, a):
        """Disco translúcido: fumaça, vapor, poeira. c e a podem ser funções de (d: 0 centro..1 borda, ângulo)."""
        if r < 0.5:
            return self.blend(cx, cy, call(c, 0, 0), call(a, 0, 0))
        r2 = r * r

        def fn(x, y, sx, sy):
            dx, dy = x - cx, y - cy
            d2 = dx * dx + dy * dy
            if d2 > r2:
                return
            d = math.sqrt(d2) / r
            ang = math.atan2(dy, dx)
            self.blendPx(sx, sy, call(c, d, ang), call(a, d, ang))

        self.each(cx - r, cy - r, cx + r, cy + r, fn)

    def get(self, x, y):
        """Lê a cor sob um ponto local (0 se vazio)."""
        sx = self.cellX(x, y) - self.ox
        sy = self.cellY(x, y) - self.oy
        return 0 if (sx < 0 or sy < 0 or sx >= self.w or sy >= self.h) else self.C[sy * self.w + sx]

    # ---- pixels
    def px(self, x, y, c):
        self.put(self.cellX(x, y), self.cellY(x, y), c, 1)

    def dot(self, x, y, c, a=1.0):
        if a > 0:
            self.put(self.cellX(x, y), self.cellY(x, y), c, a)

    def light(self, x, y, c, k=1.0):
        self.add(self.cellX(x, y), self.cellY(x, y), c, k)

    def each(self, x0, y0, x1, y1, fn):
        """Visita cada pixel de tela cujo centro cai na caixa local, com o centro em espaço local:
        fn(lx, ly, sx, sy). Base de toda forma cheia — por isso espelho, giro e escala são exatos."""
        ax = ay = INF
        bx = by = -INF
        for kk in range(4):
            x = x1 if kk & 1 else x0
            y = y1 if kk & 2 else y0
            sx, sy = self.toX(x, y), self.toY(x, y)
            if sx < ax:
                ax = sx
            if sx > bx:
                bx = sx
            if sy < ay:
                ay = sy
            if sy > by:
                by = sy
        sx0 = max(math.floor(ax), self.ox)
        sx1 = min(math.ceil(bx), self.ox + self.w - 1)
        sy0 = max(math.floor(ay), self.oy)
        sy1 = min(math.ceil(by), self.oy + self.h - 1)
        tx, ty, cs, sn, f, k = self.tx, self.ty, self.cs, self.sn, self.fx, self.k
        for sy in range(sy0, sy1 + 1):
            dy = sy + 0.5 - ty
            for sx in range(sx0, sx1 + 1):
                dx = sx + 0.5 - tx
                fn(((dx * cs + dy * sn) * f) / k, (-dx * sn + dy * cs) / k, sx, sy)

    def shade(self, x0, y0, x1, y1, fn):
        """Shader por pixel numa caixa local. fn(x, y, out) devolve uma cor, ou ajusta out.c (cor),
        out.a (alpha), out.l (cor da luz, padrão out.c) e out.k (quantidade de luz)."""
        o = _Out()

        def visit(lx, ly, sx, sy):
            o.c = 0
            o.a = 1
            o.l = 0
            o.k = 0
            r = fn(lx, ly, o)
            c = r if r else o.c
            if c:
                self.put(sx, sy, c, o.a)
            if o.k > 0:
                self.add(sx, sy, o.l or c, o.k)

        self.each(x0, y0, x1, y1, visit)

    # ---- formas. Cor (c) e alpha (a) podem ser números ou funções das coordenadas da forma.
    def line(self, x0, y0, x1, y1, c, a=1.0):
        """Linha de 1 px. c e a podem ser funções de u (0 no início, 1 no fim)."""
        sx, sy = self.cellX(x0, y0), self.cellY(x0, y0)
        ex, ey = self.cellX(x1, y1), self.cellY(x1, y1)
        dx, dy = abs(ex - sx), -abs(ey - sy)
        stepx = 1 if sx < ex else -1
        stepy = 1 if sy < ey else -1
        n = max(dx, -dy) or 1
        fc, fa = callable(c), callable(a)
        err, i = dx + dy, 0
        while True:
            u = i / n
            i += 1
            self.put(sx, sy, c(u) if fc else c, a(u) if fa else a)
            if sx == ex and sy == ey:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                sx += stepx
            if e2 <= dx:
                err += dx
                sy += stepy

    def polyline(self, pts, c, a=1.0):
        for i in range(1, len(pts)):
            self.line(pts[i - 1][0], pts[i - 1][1], pts[i][0], pts[i][1], c, a)

    def beam(self, x0, y0, x1, y1, width, c, a=1.0):
        """Segmento grosso de ponta redonda. c e a: funções de (u ao longo, v através: 0 centro, 1 borda)."""
        r = width / 2
        dx, dy = x1 - x0, y1 - y0
        L2 = dx * dx + dy * dy or 1e-9
        r2 = r * r

        def fn(x, y, o):
            u = clamp(((x - x0) * dx + (y - y0) * dy) / L2)
            px, py = x0 + dx * u - x, y0 + dy * u - y
            d2 = px * px + py * py
            if d2 > r2:
                return
            v = math.sqrt(d2) / r
            o.c = call(c, u, v)
            o.a = call(a, u, v)

        self.shade(min(x0, x1) - r, min(y0, y1) - r, max(x0, x1) + r, max(y0, y1) + r, fn)

    def circle(self, cx, cy, r, c, a=1.0):
        """Disco cheio. c e a: funções de (d: 0 centro a 1 borda, ângulo)."""
        if r < 0.6:
            return self.dot(cx, cy, call(c, 0, 0), call(a, 0, 0))
        r2 = r * r

        def fn(x, y, o):
            dx, dy = x - cx, y - cy
            d2 = dx * dx + dy * dy
            if d2 > r2:
                return
            d = math.sqrt(d2) / r
            ang = math.atan2(dy, dx)
            o.c = call(c, d, ang)
            o.a = call(a, d, ang)

        self.shade(cx - r, cy - r, cx + r, cy + r, fn)

    def ellipse(self, cx, cy, rx, ry, c, a=1.0):
        if rx <= 0 or ry <= 0:
            return

        def fn(x, y, o):
            dx, dy = (x - cx) / rx, (y - cy) / ry
            d2 = dx * dx + dy * dy
            if d2 > 1:
                return
            d = math.sqrt(d2)
            ang = math.atan2(dy, dx)
            o.c = call(c, d, ang)
            o.a = call(a, d, ang)

        self.shade(cx - rx, cy - ry, cx + rx, cy + ry, fn)

    def ring(self, cx, cy, r, w, c, a=1.0):
        """Anel do raio r - w a r. c e a: funções de (v: 0 dentro a 1 fora, ângulo)."""
        r0 = max(0, r - w)
        r2, r02 = r * r, r0 * r0

        def fn(x, y, o):
            dx, dy = x - cx, y - cy
            d2 = dx * dx + dy * dy
            if d2 > r2 or d2 < r02:
                return
            v = (math.sqrt(d2) - r0) / ((r - r0) or 1) if w > 0 else 1
            ang = math.atan2(dy, dx)
            o.c = call(c, v, ang)
            o.a = call(a, v, ang)

        self.shade(cx - r, cy - r, cx + r, cy + r, fn)

    def arc(self, cx, cy, r, w, a0, a1, c, a=1.0):
        """Faixa de anel de a0 a a1 (rad), raio r - w a r: a forma do corte e do smear.
        c e a: funções de (u: 0 em a0 a 1 em a1, v: 0 dentro a 1 fora). w pode ser função de u."""
        span = a1 - a0
        wf = callable(w)
        tau = math.pi * 2

        def fn(x, y, o):
            dx, dy = x - cx, y - cy
            d = math.sqrt(dx * dx + dy * dy)
            if d > r:
                return
            ang = math.atan2(dy, dx) - a0
            ang -= math.floor(ang / tau) * tau
            if ang > span:
                return
            u = ang / span
            ww = w(u) if wf else w
            if ww <= 0 or d < r - ww:
                return
            v = (d - (r - ww)) / ww
            o.c = call(c, u, v)
            o.a = call(a, u, v)

        self.shade(cx - r, cy - r, cx + r, cy + r, fn)

    def rect(self, x, y, w, h, c, a=1.0):
        if self.sn == 0 and self.k == 1:
            X0, Y0, X1, Y1 = jsround(x), jsround(y), jsround(x + w), jsround(y + h)
            for yy in range(Y0, Y1):
                for xx in range(X0, X1):
                    self.put(self.cellX(xx, yy), self.cellY(xx, yy), c, a)
            return

        def fn(lx, ly, o):
            if lx < x or ly < y or lx >= x + w or ly >= y + h:
                return
            o.c = c
            o.a = a

        self.shade(x, y, x + w, y + h, fn)

    def poly(self, pts, c, a=1.0):
        """Polígono cheio de pontos [[x, y], ...] (regra par-ímpar)."""
        x0 = min(p[0] for p in pts)
        x1 = max(p[0] for p in pts)
        y0 = min(p[1] for p in pts)
        y1 = max(p[1] for p in pts)
        n = len(pts)

        def fn(x, y, o):
            inside = False
            j = n - 1
            for i in range(n):
                xi, yi = pts[i][0], pts[i][1]
                xj, yj = pts[j][0], pts[j][1]
                if (yi > y) != (yj > y) and x < ((xj - xi) * (y - yi)) / (yj - yi) + xi:
                    inside = not inside
                j = i
            if not inside:
                return
            o.c = call(c, x, y)
            o.a = call(a, x, y)

        self.shade(x0, y0, x1, y1, fn)

    def tri(self, x0, y0, x1, y1, x2, y2, c, a=1.0):
        self.poly([[x0, y0], [x1, y1], [x2, y2]], c, a)

    # ---- luz
    def glow(self, x, y, r, c, k=0.5):
        """Brilho radial no buffer de luz: k no centro, caindo a 0 no raio r."""
        r *= self.k
        if r < 1 or k <= 0.004:
            return
        cx, cy = self.toX(x, y), self.toY(x, y)
        x0, x1 = math.floor(cx - r), math.ceil(cx + r)
        y0, y1 = math.floor(cy - r), math.ceil(cy + r)
        for sy in range(y0, y1 + 1):
            dy = (sy + 0.5 - cy) / r
            for sx in range(x0, x1 + 1):
                dx = (sx + 0.5 - cx) / r
                d = dx * dx + dy * dy
                if d >= 1:
                    continue
                f = 1 - math.sqrt(d)
                self.add(sx, sy, c, f * f * k)

    def glowLine(self, x0, y0, x1, y1, r, c, k=0.5):
        """Brilho em volta de um segmento (um feixe suave de luz)."""
        r *= self.k
        if r < 1 or k <= 0.004:
            return
        ax, ay = self.toX(x0, y0), self.toY(x0, y0)
        bx, by = self.toX(x1, y1), self.toY(x1, y1)
        dx, dy = bx - ax, by - ay
        L2 = dx * dx + dy * dy or 1e-9
        X0, X1 = math.floor(min(ax, bx) - r), math.ceil(max(ax, bx) + r)
        Y0, Y1 = math.floor(min(ay, by) - r), math.ceil(max(ay, by) + r)
        for sy in range(Y0, Y1 + 1):
            for sx in range(X0, X1 + 1):
                px, py = sx + 0.5, sy + 0.5
                u = clamp(((px - ax) * dx + (py - ay) * dy) / L2)
                ex, ey = ax + dx * u - px, ay + dy * u - py
                d = math.sqrt(ex * ex + ey * ey) / r
                if d >= 1:
                    continue
                f = 1 - d
                self.add(sx, sy, c, f * f * k)

    def glowRing(self, x, y, R, r, c, k=0.5):
        """Brilho abraçando um círculo de raio R (a luz de uma onda de choque), caindo em r."""
        R *= self.k
        r *= self.k
        if r < 1 or k <= 0.004:
            return
        cx, cy = self.toX(x, y), self.toY(x, y)
        E = R + r
        for sy in range(math.floor(cy - E), math.ceil(cy + E) + 1):
            for sx in range(math.floor(cx - E), math.ceil(cx + E) + 1):
                d = abs(math.hypot(sx + 0.5 - cx, sy + 0.5 - cy) - R) / r
                if d >= 1:
                    continue
                f = 1 - d
                self.add(sx, sy, c, f * f * k)

    # ---- sprites, texto, máscaras
    def sprite(self, rows, pal, x, y, opts=None):
        """Sprite de strings: linhas como ["..##..", ".#oo#."]; pal mapeia caractere → cor; "." e " " vazios.
        opts: {scale, a, flip, flipY, tint}."""
        opts = opts or {}
        k = opts.get("scale", 1)
        a = opts.get("a", 1)
        W = len(rows[0]) if rows else 0
        cache = {}
        tint = opts.get("tint")
        nr = len(rows)
        for r, linha in enumerate(rows):
            for q, ch in enumerate(linha):
                if ch in (".", " "):
                    continue
                c = tint
                if c is None:
                    if ch not in cache:
                        cache[ch] = hex(pal[ch]) if ch in pal else 0
                    c = cache[ch]
                if not c:
                    continue
                col = W - 1 - q if opts.get("flip") else q
                row = nr - 1 - r if opts.get("flipY") else r
                if k == 1:
                    self.dot(x + col, y + row, c, a)
                else:
                    self.rect(x + col * k, y + row * k, k, k, c, a)

    def text(self, s, x, y, c, opts=None):
        """Texto em pixel. opts: {font: 'mini'|'big', scale, align, outline, shadow, a}."""
        opts = opts or {}
        font = opts.get("font", "mini")
        k = opts.get("scale", 1)
        a = opts.get("a", 1)
        w = textWidth(s, font) * k
        align = opts.get("align")
        left = jsround(x - w / 2 if align == "center" else x - w if align == "right" else x)
        top = jsround(y)
        ol, sh = opts.get("outline"), opts.get("shadow")
        if ol is not None:
            rasterText(s, font, lambda gx, gy: self.rect(left + gx * k - 1, top + gy * k - 1, k + 2, k + 2, ol, a))
        if sh is not None:
            rasterText(s, font, lambda gx, gy: self.rect(left + gx * k + 1, top + gy * k + 1, k, k, sh, a))
        rasterText(s, font, lambda gx, gy: self.rect(left + gx * k, top + gy * k, k, k, call(c, gx, gy), a))

    def measure(self, s, opts=None):
        opts = opts or {}
        k = opts.get("scale", 1)
        font = opts.get("font", "mini")
        return [textWidth(s, font) * k, FONTS[font]["h"] * k]

    def mask(self, m, x, y, c, a=1.0):
        """Preenche uma máscara ({w, h, data}) com o canto em (x, y). c pode ser função de (mx, my)."""
        mw, mh, data = m["w"], m["h"], m["data"]
        for my in range(mh):
            for mx in range(mw):
                if data[my * mw + mx]:
                    self.dot(x + mx, y + my, call(c, mx, my), call(a, mx, my))

    def outline(self, m, x, y, c, a=1.0):
        """O contorno de 1 px logo fora de uma máscara."""
        mw, mh, data = m["w"], m["h"], m["data"]

        def at(mx, my):
            return 0 <= mx < mw and 0 <= my < mh and data[my * mw + mx]

        for my in range(-1, mh + 1):
            for mx in range(-1, mw + 1):
                if not at(mx, my) and (at(mx - 1, my) or at(mx + 1, my) or at(mx, my - 1) or at(mx, my + 1)):
                    self.dot(x + mx, y + my, call(c, mx, my), call(a, mx, my))
