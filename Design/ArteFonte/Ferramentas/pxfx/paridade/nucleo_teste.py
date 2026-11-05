"""Cenário de paridade do NÚCLEO — gêmeo de nucleo_teste.mjs. Mexeu num, mexa no outro igual.

Exercita toda a API: os 12 tipos de partícula, detritos, luzes, fogueiras, todas as formas
do pintor, texto, máscara e raios. `py -m pxfx.paridade --nucleo` compara com o original.
"""
from __future__ import annotations

import math

from .. import (PAL, PF, WHITE, B, Bits, Blazes, Lights, P, Particles, Rng, at, band, bolt, burst, crystal, cycle,
                ease, fit, flare, fly, forks, hex, jsround, loopNoise, mix, ngon, sparkle, star, stockActor, stream,
                tileFbm)

meta = {
    "name": "Núcleo", "size": [200, 150], "origin": [100, 120], "duration": 2, "loop": False, "fps": 20, "bg": "dark",
    "options": {"palette": PAL["ice"], "seed": 3},
}


class _Cena:
    def __init__(self, o):
        R = Rng(o.seed)
        self.t = 0.0
        floor = lambda x: 0  # noqa: E731
        self.ps = Particles(rng=R, ground=floor, haze="#9bdcff",
                            onLand=lambda x, y: self.real.add(x, y, 1.2, 1))
        self.real = Blazes(self.ps)
        self.bits = Bits(ground=floor)
        self.lights = Lights()
        C = self.C = fit(o.palette, 8)
        self.lights.add(0, -20, 40, C[5], 0.8, 1.2)
        kinds = [P.SPARK, P.MOTE, P.STREAK, P.FLAKE, P.VAPOUR, P.DUST, P.STAR, P.EMBER, P.SMOKE, P.FIRE, P.BRAND, P.GRIT]
        for i in range(48):
            k = kinds[i % len(kinds)]
            a = R.range(0, math.pi * 2)
            sp = R.range(40, 200)
            flag = (PF.SMOKES | (PF.BIG if i % 2 else 0)) if k == P.FIRE else (PF.BACK if i % 5 == 0 else 0)
            x, y = R.range(-20, 20), -R.range(5, 40)
            life = R.range(0.3, 1.5)
            col = 0 if k in (P.FIRE, P.SMOKE) else C[R.int(2, 7)]
            self.ps.spawn(k, x, y, math.cos(a) * sp, math.sin(a) * sp - 60, life, col, R.range(0.5, 3),
                          0.2 if i % 7 == 0 else 0, flag)
        for i in range(9):
            self.bits.add(kind=i % 3, x=R.range(-15, 15), y=-R.range(10, 30), vx=R.range(-90, 90), vy=-R.range(80, 220),
                          a=R.range(0, 6), va=R.range(-20, 20), s=R.range(1.5, 4), c=C[R.int(3, 7)], bounce=0.4,
                          life=R.range(0.8, 1.8))

    def update(self, dt):
        self.t += dt
        self.ps.update(dt)
        self.bits.update(dt)
        self.lights.update(dt)
        self.real.update(dt)

    def drawBack(self, p):
        self.ps.draw(p, "back")
        self.real.drawBack(p)
        band(p, 0, 0, 30 + self.t * 10, 0.16, 3, 0.9, PAL["ice"], lambda g: math.sin(g) < 0)

    def draw(self, p):
        t, C = self.t, self.C
        u = min(1, t / 2)

        def sh(x, y, out):
            out.c = at(C, (x + 95) / 35)
            out.a = 0.3 + 0.7 * ((y + 110) / 30)
            out.k = 0.1

        p.shade(-95, -110, -60, -80, sh)
        p.beam(-90, -70, -50, -40, 5, lambda uu, v: C[7] if v < 0.5 else C[4], lambda uu, v: 1 - uu * 0.5)
        p.circle(-40, -95, 8 * (1 - u) + 1, lambda d, ang: at(C, 1 - d))
        p.ellipse(40, -95, 14, 6, C[3], 0.7)
        p.ring(70, -95, 12, 3, lambda v, ang: at(C, v))
        p.arc(0, -60, 30, lambda uu: 6 * math.sin(uu * math.pi), -2.5, -0.6 + u * 0.5,
              lambda uu, v: mix(C[2], WHITE, v), 1)
        p.poly(star(-70, -20, 4, 9, 5, t), C[6])
        p.tri(60, -20, 80, -40, 90, -10, C[5], 0.6)
        p.polyline(ngon(85, -70, 9, 6, t), C[7])
        p.polyline(bolt(Rng(7), -90, -5, -40, -50), WHITE)
        for f in forks(Rng(9), bolt(Rng(8), 40, -5, 90, -50), count=2, len=14):
            p.polyline(f, C[6])
        p.glowLine(-90, -5, -40, -50, 5, C[5], 0.4)
        p.glowRing(0, -20, 20 + t * 15, 5, C[6], 0.5)
        p.text("NUCLEO 01", -96, -116, C[7], {"font": "big", "outline": C[0], "shadow": C[1]})
        p.text(f"T{jsround(t * 100)}", 96, -116, WHITE, {"align": "right"})
        actor = stockActor(2)
        p.outline(actor.mask, 40 + actor.x, actor.y, C[6], 0.8)
        p.mask(actor.mask, 40 + actor.x, actor.y, lambda mx, my: at(C, my / actor.h), 0.5)
        crystal(p, -20, 0, 18 * u + 2, 6, 2, PAL["ice"], {"glint": u})
        crystal(p, -8, 0, 12, 5, -1, PAL["ice"], {"white": t < 0.2})
        sparkle(p, 20, -30, 6 * (1 - u), C[6], C[4], 0.6)
        flare(p, -30, -40, 10 * (1 - u), 0.5, PAL["ice"])

        def cyc(age, life, r, i):
            x, y = fly(r.range(-60, 60), -10, r.range(-20, 20), -r.range(30, 60), age, 40, 1)
            p.dot(x, y, C[6], 1 - age / life)

        cycle(t, 1, 6, 5, 0.8, cyc)
        stream(t, 0, 1.5, 8, 6, 0.6, lambda age, life, r, i: p.px(-60 + age * 40, -60 - r.range(0, 20), C[5]))
        burst(5, 11, lambda r, i: p.light(r.range(-50, 50), -r.range(60, 100), C[7], 0.5))
        for i in range(8):
            p.dot(-60 + i * 3, -120 + tileFbm(i, t * 4, 8, 8, 2) * 4 + loopNoise(u, 1, 3) * 3,
                  C[7 if ease.outBack(u) > 0.5 else 3], ease.inOutSine(i / 8))
        p.sprite(["..##..", ".#oo#.", "#oooo#", ".#oo#."], {"#": "#222034", "o": hex("#ffe26b")}, 60, -100,
                 {"scale": 2, "flip": True})
        self.bits.draw(p)
        self.ps.draw(p, "front")
        self.lights.draw(p)


def create(o):
    return _Cena(o)
