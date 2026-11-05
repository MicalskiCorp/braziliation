"""Modelo QUADRÚPEDE: tronco, quatro pernas com cinemática inversa, pescoço, cabeça e cauda — Lobisomem, cão.

Mesma convenção do bípede: medidas e poses nas unidades do boneco de 38 px, o `escala` multiplica.
Pernas de dois ossos com o "cotovelo" para trás (lê como a perna de cão em pixel art).

Pose: crouch (abaixa o tronco), lean (inclina: + abaixa a frente), cabeca (rad, + olha para cima),
cauda (rad, + levanta), pdn/pdl/ptn/ptl ([dx, dy] dos pés: dianteiro perto/longe, traseiro perto/longe,
relativos ao lugar de repouso; dy negativo sobe), x, y, yaw.
Medidas: tronco, altura_ombro, altura_quadril, braco [2], perna [2], pescoco, cabeca [3], focinho [3],
cauda_segmentos, cauda_segmento, largura.
"""
from __future__ import annotations

import math

from .corpo import PARTES, _usa
from .vetor import add, boneFrame, frame, ik, mm, mul, mv, rotY, rotZ, sub, unit

MEDIDAS = {"tronco": 20.0, "altura_ombro": 15.0, "altura_quadril": 15.5, "braco": [7.2, 7.2], "perna": [7.8, 8.0],
           "pescoco": 6.0, "cabeca": [3.6, 3.0, 2.8], "focinho": [2.8, 1.6, 1.6], "cauda_segmentos": 5,
           "cauda_segmento": 3.4, "largura": 3.2, "raio_tronco": [4.6, 4.2, 4.0], "raio_quadril": [4.0, 4.4, 3.8]}
PERNAS = (("pdn", "upperN", "foreN", "handN", 1, True), ("pdl", "upperF", "foreF", "handF", -1, True),
          ("ptn", "thighN", "shinN", "footN", 1, False), ("ptl", "thighF", "shinF", "footF", -1, False))


class Quadrupede:
    tipo = "quadrupede"

    def __init__(self, medidas=None, escala=1.0):
        self.k = escala
        m = dict(MEDIDAS)
        m.update(medidas or {})
        self.m = m
        nc = int(m["cauda_segmentos"])
        self.FRAME_IDS = ["chest", "pelvis", "waist", "neck", "head"] + [p[1] for p in PERNAS] + [p[2] for p in PERNAS] \
            + [f"cauda{i}" for i in range(nc)]

    def solve(self, pose):
        m, k = self.m, self.k
        q = pose or {}
        T = m["tronco"] * k
        pitch = math.atan2(q.get("lean", 0.0), 13.0)
        crouch = q.get("crouch", 0.0) * k
        quadril = [-T / 2, m["altura_quadril"] * k - crouch, 0]
        ombro = add(quadril, [T * math.cos(pitch), -T * math.sin(pitch) + (m["altura_ombro"] - m["altura_quadril"]) * k, 0])
        R_tronco = rotZ(math.atan2(ombro[1] - quadril[1], ombro[0] - quadril[0]))
        B = {"pelvis": frame(quadril, R_tronco), "chest": frame(ombro, R_tronco),
             "waist": frame(add(quadril, mul(sub(ombro, quadril), 0.5)), R_tronco)}
        w = m["largura"] * k
        pernas = {}
        for nome, sup, inf, pe, s, dianteira in PERNAS:
            base = add(ombro if dianteira else quadril, [0, -1.5 * k, s * w])
            L1, L2 = (m["braco"] if dianteira else m["perna"])
            pd = q.get(nome) or [0, 0]
            alvo = [base[0] + pd[0] * k + (1.0 * k if dianteira else -0.5 * k), 1.2 * k - pd[1] * k, s * w]
            sol = ik(base, alvo, L1 * k, L2 * k, [-1, 0, 0.2 * s], 0.02 * k)
            pernas[nome] = (base, sol)
            B[sup] = boneFrame(base, sol["joint"], sol["v"])
            B[inf] = boneFrame(sol["joint"], sol["end"], sol["v"])
        ang_pesc = math.radians(40) + q.get("cabeca", 0.0) * 0.6
        pesc0 = add(ombro, [1.5 * k, 2.0 * k, 0])
        pesc1 = add(pesc0, [math.cos(ang_pesc) * m["pescoco"] * k, math.sin(ang_pesc) * m["pescoco"] * k, 0])
        ang_cab = q.get("cabeca", 0.0) * 0.5 - 0.15
        B["neck"] = boneFrame(pesc0, pesc1, [0, 1, 0])
        B["head"] = frame(pesc1, mm(rotY(0), rotZ(ang_cab)))
        cauda = [add(quadril, [-1.5 * k, 1.5 * k, 0])]
        ang_c = math.radians(160) - q.get("cauda", 0.0)
        for i in range(int(m["cauda_segmentos"])):
            a = ang_c + i * 0.18 * (1 if q.get("cauda", 0.0) >= 0 else -1)
            cauda.append(add(cauda[-1], [math.cos(a) * m["cauda_segmento"] * k, math.sin(a) * m["cauda_segmento"] * k, 0]))
            B[f"cauda{i}"] = boneFrame(cauda[-2], cauda[-1], [0, 1, 0])
        S = {"B": B, "q": q, "pernas": pernas, "quadril": quadril, "ombro": ombro, "pesc": (pesc0, pesc1), "cauda": cauda}
        yaw = q.get("yaw", 0.0)
        if yaw:
            R = rotY(-yaw)
            for f in B.values():
                f["t"] = mv(R, f["t"])
                f["R"] = mm(R, f["R"])
            S["pernas"] = {n: (mv(R, b), {**s_, "joint": mv(R, s_["joint"]), "end": mv(R, s_["end"])})
                           for n, (b, s_) in S["pernas"].items()}
            for n in ("quadril", "ombro"):
                S[n] = mv(R, S[n])
            S["pesc"] = tuple(mv(R, p) for p in S["pesc"])
            S["cauda"] = [mv(R, p) for p in S["cauda"]]
        return S

    def volumes(self, S, r, mult=None):
        m, k, B, P = self.m, self.k, S["B"], PARTES
        ids = self.FRAME_IDS
        for nome, sup, inf, pe, s, dianteira in PERNAS:
            if s > 0:
                continue
            self._perna(S, r, nome, sup, inf, pe, dianteira, 1)
        _usa(r, "pelvis", ids)
        r.elipsoide(S["quadril"], B["pelvis"]["R"], [v * k for v in m["raio_quadril"]], P["pelvis"], "casca")
        _usa(r, "waist", ids)
        r.capsula(S["quadril"], S["ombro"], m["raio_quadril"][1] * k * 0.8, m["raio_tronco"][1] * k * 0.85, P["waist"], "casca")
        _usa(r, "chest", ids)
        r.elipsoide(S["ombro"], B["chest"]["R"], [v * k for v in m["raio_tronco"]], P["chest"], "casca")
        for i in range(len(S["cauda"]) - 1):
            _usa(r, f"cauda{i}", ids)
            u = i / max(1, len(S["cauda"]) - 1)
            r.capsula(S["cauda"][i], S["cauda"][i + 1], (1.4 - u) * k, (1.3 - u) * k * 0.9, P[f"extra{i + 1}"], "casca")
        _usa(r, "neck", ids)
        r.capsula(S["pesc"][0], S["pesc"][1], 2.6 * k, 2.0 * k, P["neck"], "nucleo")
        _usa(r, "head", ids)
        h = B["head"]
        r.elipsoide(h["t"], h["R"], [v * k for v in m["cabeca"]], P["head"], "casca")
        r.elipsoide(add(h["t"], mv(h["R"], [m["cabeca"][0] * k * 0.95, -0.6 * k, 0])), h["R"],
                    [v * k for v in m["focinho"]], P["face"], "casca")
        for nome, sup, inf, pe, s, dianteira in PERNAS:
            if s < 0:
                continue
            self._perna(S, r, nome, sup, inf, pe, dianteira, 0)

    def _perna(self, S, r, nome, sup, inf, pe, dianteira, longe):
        k, P, ids = self.k, PARTES, self.FRAME_IDS
        base, sol = S["pernas"][nome]
        r.cur_dim = longe
        _usa(r, sup, ids)
        r.capsula(base, sol["joint"], (2.4 if dianteira else 2.8) * k, 1.5 * k, P[sup], "casca")
        _usa(r, inf, ids)
        r.capsula(sol["joint"], sol["end"], 1.4 * k, 1.1 * k, P[inf], "casca")
        r.esfera(add(sol["end"], [0.8 * k, -0.2 * k, 0]), 1.5 * k, P[pe], "nucleo")
        r.cur_dim = 0
