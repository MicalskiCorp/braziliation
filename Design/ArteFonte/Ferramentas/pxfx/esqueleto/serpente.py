"""Modelo SERPENTE: uma corrente de segmentos movida por onda — Minhocão, Boitatá, cauda da Iara.

Sem cinemática inversa: a pose descreve a onda e o corpo segue. Medidas e poses nas unidades
do boneco de 38 px (o `escala` multiplica), como o bípede.

Pose: fase (rad, anda a onda), amp (ondulação vertical, px), onda (comprimento de onda, px),
lado (ondulação em profundidade, px), erguer (quanto a frente se levanta, px), boca (0..1),
x, y. Repouso (pose vazia): corpo reto no chão — é o gabarito da pele.
Medidas: segmentos, comprimento, raio, raio_cauda, raio_pescoco, cabeca [comprimento, altura, largura].
"""
from __future__ import annotations

import math

from .corpo import PARTES, _usa
from .vetor import add, boneFrame, frame, mm, mul, rotY, rotZ, sub, unit

MEDIDAS = {"segmentos": 14, "comprimento": 64.0, "raio": 3.6, "raio_cauda": 0.7, "raio_pescoco": 2.6,
           "cabeca": [5.4, 3.2, 3.4]}


class Serpente:
    tipo = "serpente"

    def __init__(self, medidas=None, escala=1.0):
        self.k = escala
        m = dict(MEDIDAS)
        m.update(medidas or {})
        self.m = m
        self.n = int(m["segmentos"])
        self.FRAME_IDS = [f"seg{i}" for i in range(self.n)] + ["head"]

    def _raio(self, u):
        """Raio ao longo do corpo, u = 0 na cauda, 1 no pescoço: afina na cauda, engrossa no meio."""
        m, k = self.m, self.k
        corpo = m["raio_cauda"] + (m["raio"] - m["raio_cauda"]) * math.sin(min(1.0, u * 1.25) * math.pi / 2)
        if u > 0.85:
            corpo += (m["raio_pescoco"] - corpo) * (u - 0.85) / 0.15
        return corpo * k

    def solve(self, pose):
        m, k, n = self.m, self.k, self.n
        q = pose or {}
        L = m["comprimento"] * k
        seg = L / n
        fase = q.get("fase", 0.0)
        amp = q.get("amp", 0.0) * k
        onda = max(1.0, q.get("onda", 32.0) * k)
        lado = q.get("lado", 0.0) * k
        erguer = q.get("erguer", 0.0) * k
        pts = []
        for i in range(n + 1):
            u = i / n
            x = -L * 0.55 + i * seg
            env = math.sin(u * math.pi) ** 0.6
            frente = max(0.0, (u - 0.6) / 0.4)
            y = self._raio(u) + amp * math.sin(2 * math.pi * x / onda - fase) * env + erguer * frente * frente
            z = lado * math.sin(math.pi * x / onda - fase) * env
            pts.append([x, y, z])
        # a corrente mantém o comprimento de cada segmento: reprojeta em sequência a partir da cauda
        for i in range(1, n + 1):
            d = sub(pts[i], pts[i - 1])
            pts[i] = add(pts[i - 1], mul(unit(d), seg))
        B = {}
        for i in range(n):
            B[f"seg{i}"] = boneFrame(pts[i], pts[i + 1], [0, 1, 0])
        ux = unit(sub(pts[n], pts[n - 1]))
        ang = math.atan2(ux[1], ux[0]) + q.get("cabeca", 0.0)
        B["head"] = frame(add(pts[n], mul([math.cos(ang), math.sin(ang), 0], m["cabeca"][0] * 0.55 * k)),
                          mm(rotY(0), rotZ(ang)))
        return {"B": B, "pts": pts, "q": q}

    def volumes(self, S, r, mult=None):
        k, n = self.k, self.n
        pts, B = S["pts"], S["B"]
        for i in range(n):
            _usa(r, f"seg{i}", self.FRAME_IDS)
            r.capsula(pts[i], pts[i + 1], self._raio(i / n), self._raio((i + 1) / n), PARTES[f"extra{i % 32 + 1}"], "casca")
        _usa(r, "head", self.FRAME_IDS)
        c = self.m["cabeca"]
        h = B["head"]
        r.elipsoide(h["t"], h["R"], [c[0] * k * 0.55, c[1] * k * 0.55, c[2] * k * 0.55], PARTES["head"], "casca")
        boca = (S["q"].get("boca") or 0.0)
        mand = add(h["t"], [0, -c[1] * k * 0.25 - boca * c[1] * k * 0.5, 0])
        r.elipsoide(add(mand, [c[0] * k * 0.12, 0, 0]), h["R"], [c[0] * k * 0.45, c[1] * k * 0.28, c[2] * k * 0.45],
                    PARTES["face"], "nucleo")
