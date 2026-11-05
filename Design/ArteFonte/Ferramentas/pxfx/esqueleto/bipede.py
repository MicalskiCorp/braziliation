"""Modelo BÍPEDE: o resolvedor de pose do `rig.js` do PixelFX (MIT), com medidas escaláveis.

Uma pose diz só onde ficam mãos e pés e como o corpo se carrega (agacha, inclina, gira);
o resolvedor acha cada junta. As medidas `M` são as do boneco de 38 px do PixelFX; o
`escala` multiplica tudo — com escala 2,5 é o manequim de ~96 px do grid do ADR-011.
As POSES continuam nas unidades do boneco de 38 px (o resolvedor multiplica): por isso as
atuações do PixelFX (sword-slash, hammer-smash...) servem direto como biblioteca.

Variantes do elenco por parâmetro (rig.json, chave "medidas"/"variante"):
- Curupira: `pes_invertidos: true` (o pé aponta para trás);
- Saci: `pernas: 1` (só a perna da frente é desenhada e resolvida);
- proporções (Mapinguari, Cuca): sobrescreva qualquer medida de M.

Vocabulário da pose (igual ao original): x, y (pés), crouch, lean, hx, hy (cabeça), fx, fy, fz
(mão da frente), bx, by, bz (mão de trás), ffx, ffy (pé da frente), fbx, fby (pé de trás), turn,
yaw, twist, armsFront, toeF, toeB.
"""
from __future__ import annotations

import math

from .vetor import (DEG, add, boneFrame, clamp01, cross, dot, frame, ik, length, mm, mul, mv, rotY, rotZ, sub,
                    unit)

M_PIXELFX = {
    "pelvis": 19.7, "spine1": 2.8, "spine2": 4.6, "shoulderUp": 2.5, "shoulderOut": 5.9, "neckUp": 4.0, "headUp": 3.1,
    "hipDown": 1.1, "hipOut": 2.8, "thigh": 8.6, "shin": 8.3, "upper": 7.6, "fore": 7.4, "turn": 36 * DEG,
}
# De pé, à vontade, em termos de tela: mãos e pés onde devem ficar, y negativo é para cima.
STAND = {"lean": 0, "crouch": 0, "yaw": 0, "fx": -3, "fy": -15, "bx": 5, "by": -15, "ffx": -2, "ffy": -4, "fbx": 3, "fby": -4}
# A postura de onde os atos partem (poses.js).
READY = {"crouch": 3, "fx": 11, "fy": -21, "bx": 9, "by": -21, "ffx": 7, "fbx": -7}

FRAME_IDS = ["pelvis", "waist", "chest", "head", "neck", "upperN", "foreN", "upperF", "foreF", "thighN", "shinN",
             "thighF", "shinF", "footN", "footF"]
_ANGULARES = {"turn", "yaw", "twist", "sa", "sb"}
_DISTANCIAS = {"x", "y", "crouch", "lean", "fx", "fy", "fz", "bx", "by", "bz", "ffx", "ffy", "fbx", "fby", "fzz", "bzz"}


class Bipede:
    """Resolve poses de um bípede. medidas: sobrescreve M; escala: multiplica medidas e poses."""

    tipo = "bipede"

    def __init__(self, medidas=None, escala=1.0, pes_invertidos=False, pernas=2):
        self.k = escala
        base = dict(M_PIXELFX)
        base.update(medidas or {})
        self.M = {n: (v if n == "turn" else v * escala) for n, v in base.items()}
        self.pes_invertidos = pes_invertidos
        self.pernas = pernas

    def _escala_pose(self, pose):
        q = dict(STAND)
        q.update(pose or {})
        if self.k == 1:
            return q
        return {n: (v * self.k if (n in _DISTANCIAS and isinstance(v, (int, float))) else v) for n, v in q.items()}

    def solve(self, pose):
        M, k = self.M, self.k
        q = self._escala_pose(pose)
        st_fx, st_bx = STAND["fx"] * k, STAND["bx"] * k
        lean = q["lean"]
        two = False  # armas ficam com o motor de VFX; o corpo resolve mãos livres
        nearZ = q.get("fz") if q.get("fz") is not None else 4.5 * k
        # o giro do peito segue as mãos: mão que avança traz o ombro; mão recolhida abre o corpo
        fwd = (q["fx"] - st_fx) / (24 * k)
        farFwd = (q["bx"] - st_bx) / (22 * k)
        turn = M["turn"] + (-44 * DEG * min(1, fwd) if fwd >= 0 else 28 * DEG * min(1, -fwd * 1.8))
        turn += (34 * DEG * min(1, farFwd) if farFwd > 0 else 0) + (q.get("twist") or 0) * 4 * DEG
        if q.get("turn") is not None:
            turn = q["turn"]
        hipTurn = M["turn"] + (turn - M["turn"]) * 0.45
        tilt = math.atan2(lean, 13 * k)
        Rp = mm(rotZ(-tilt * 0.25), rotY(-hipTurn))
        Rc = mm(rotZ(-tilt), rotY(-turn))
        # pés primeiro: a pelve afunda se é isso que as duas pernas precisam para alcançá-los
        ankleN = [q["ffx"], -q["ffy"] - 1.8 * k, q.get("fzz") if q.get("fzz") is not None else 2.4 * k]
        ankleF = [q["fbx"], -q["fby"] - 1.8 * k, q.get("bzz") if q.get("bzz") is not None else -2.4 * k]
        pelvis = [lean * 0.2, M["pelvis"] - q["crouch"], 0]

        def hipAt(s):
            return add(pelvis, mv(Rp, [0, -M["hipDown"], s * M["hipOut"]]))

        maxLeg = (M["thigh"] + M["shin"]) * 0.995
        for s, a in ((1, ankleN), (-1, ankleF)):
            h = hipAt(s)
            dx, dz = h[0] - a[0], h[2] - a[2]
            flat = dx * dx + dz * dz
            if flat < maxLeg * maxLeg:
                top = a[1] + math.sqrt(maxLeg * maxLeg - flat)
                if h[1] > top:
                    pelvis = [pelvis[0], pelvis[1] - (h[1] - top), pelvis[2]]
        waist = add(pelvis, [math.sin(tilt * 0.45) * M["spine1"], math.cos(tilt * 0.45) * M["spine1"], 0])
        chest = add(waist, [math.sin(tilt) * M["spine2"], math.cos(tilt) * M["spine2"], 0])
        neck = add(chest, mv(Rc, [0, M["neckUp"], 0]))
        headTurn = M["turn"] * 0.9 + (turn - M["turn"]) * 0.35
        nod = tilt * 0.35 + (q.get("hy") or 0) * 7 * DEG
        roll = (q.get("hx") or 0) * 7 * DEG
        Rh = mm(rotZ(-nod - roll), rotY(-headTurn))
        head = add(neck, mv(Rh, [0.15 * k, M["headUp"], 0]))

        def pick(s, target):
            base = add(chest, mv(Rc, [0, M["shoulderUp"], s * M["shoulderOut"]]))
            to = sub(target, base)
            d = length(to)
            return add(base, mul(unit(to), min(1.8 * k, max(0, d - 11 * k) * 0.35)))

        nearT = [q["fx"], -q["fy"], nearZ]
        farT = [q["bx"], -q["by"], q.get("bz") if q.get("bz") is not None else (5.5 * k if q.get("armsFront") else -4.5 * k)]
        sN, sF = pick(1, nearT), pick(-1, farT)

        def pole(s, T, shoulder):
            # cotovelos pendem para baixo e para trás; acima da cabeça vão para fora e para a frente
            up = clamp01((T[1] - shoulder[1] + 2 * k) / (10 * k))
            return [-0.55 + up * 1.1, -1 + up * 0.9, s * (0.45 + up * 0.5)]

        armN = ik(sN, nearT, M["upper"], M["fore"], pole(1, nearT, sN), 0.02 * k)
        armF = ik(sF, farT, M["upper"], M["fore"], pole(-1, farT, sF), 0.02 * k)

        def kneePole(s):
            return mv(Rp, [-1 if self.pes_invertidos else 1, 0, s * 0.35])

        hipN, hipF = hipAt(1), hipAt(-1)
        legN = ik(hipN, ankleN, M["thigh"], M["shin"], kneePole(1), 0.02 * k)
        legF = ik(hipF, ankleF, M["thigh"], M["shin"], kneePole(-1), 0.02 * k)

        def footDir(s):
            t = hipTurn * 0.6 + s * 8 * DEG + (math.pi if self.pes_invertidos else 0)
            return [math.cos(t), 0, math.sin(t)]

        B = {
            "pelvis": frame(pelvis, Rp),
            "waist": frame(waist, mm(rotZ(-tilt * 0.6), rotY(-(turn + hipTurn) / 2))),
            "chest": frame(chest, Rc), "head": frame(head, Rh), "neck": frame(neck, Rh),
            "upperN": boneFrame(sN, armN["joint"], armN["v"]), "foreN": boneFrame(armN["joint"], armN["end"], armN["v"]),
            "upperF": boneFrame(sF, armF["joint"], armF["v"]), "foreF": boneFrame(armF["joint"], armF["end"], armF["v"]),
            "thighN": boneFrame(hipN, legN["joint"], legN["v"]), "shinN": boneFrame(legN["joint"], legN["end"], legN["v"]),
            "thighF": boneFrame(hipF, legF["joint"], legF["v"]), "shinF": boneFrame(legF["joint"], legF["end"], legF["v"]),
        }
        fdN, fdF = footDir(1), footDir(-1)
        B["footN"] = frame(legN["end"], mm(rotY(-math.atan2(fdN[2], fdN[0])), rotZ(-55 * DEG if q.get("toeF") else 0)))
        B["footF"] = frame(legF["end"], mm(rotY(-math.atan2(fdF[2], fdF[0])), rotZ(-55 * DEG if q.get("toeB") else 0)))
        S = {"B": B, "q": q, "armN": armN, "armF": armF, "legN": legN, "legF": legF, "sN": sN, "sF": sF,
             "hipN": hipN, "hipF": hipF, "turn": turn}
        whole = (q.get("yaw") or 0) + (math.pi if q.get("face") == -1 else 0)
        if whole:
            _turnAll(S, whole)
        return S

    def juntas(self, pose):
        """As juntas da pose em espaço local de tela (x direita, y para baixo, pés em 0, z para quem olha)."""
        S = self.solve(pose)
        B = S["B"]

        def at(f, v):
            return add(f["t"], mv(f["R"], v))

        k = self.k
        J = {
            "pelvis": B["pelvis"]["t"], "waist": B["waist"]["t"], "chest": B["chest"]["t"], "neck": B["neck"]["t"],
            "head": B["head"]["t"], "crown": at(B["head"], [0, 3.3 * k, 0]),
            "shoulderN": S["sN"], "elbowN": S["armN"]["joint"], "handN": S["armN"]["end"],
            "shoulderF": S["sF"], "elbowF": S["armF"]["joint"], "handF": S["armF"]["end"],
            "hipN": S["hipN"], "kneeN": S["legN"]["joint"], "ankleN": S["legN"]["end"], "toeN": at(B["footN"], [4.6 * k, -1.1 * k, 0]),
            "hipF": S["hipF"], "kneeF": S["legF"]["joint"], "ankleF": S["legF"]["end"], "toeF": at(B["footF"], [4.6 * k, -1.1 * k, 0]),
        }
        return {n: [v[0], -v[1], v[2]] for n, v in J.items()}


def _turnAll(S, a):
    """A figura inteira girada em torno da vertical que passa pelos pés."""
    R = rotY(-a)

    def P(v):
        return mv(R, v)

    for f in S["B"].values():
        f["t"] = P(f["t"])
        f["R"] = mm(R, f["R"])
    for A in (S["armN"], S["armF"], S["legN"], S["legF"]):
        A["joint"] = P(A["joint"])
        A["end"] = P(A["end"])
    for n in ("sN", "sF", "hipN", "hipF"):
        S[n] = P(S[n])
