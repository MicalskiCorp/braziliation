"""Paridade do esqueleto: juntas, interpolação de poses e silhueta contra o rig.js original.

    py -m pxfx.paridade.esqueleto

Três checagens:
1. juntas na escala 1 iguais às do `skeleton()` original (tolerância 1e-6 px);
2. juntas na escala 2,5 iguais a 2,5 × as do original (a escala é linear);
3. `poseAt` igual ao original em trilhas com todas as chegadas (snap, out, in, line, suave);
4. silhueta do manequim na escala 1 contra a do `posed()` original (sobreposição ≥ 0,85 —
   o acabamento é do Braziliation, então a borda não precisa ser idêntica).
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

from ..atuacao import poseAt
from ..esqueleto.bipede import READY, Bipede

AQUI = Path(__file__).resolve().parent

# poses de verdade dos atos do PixelFX (sword-slash, hammer-smash, frost-nova...) mais extremos
GUARD = {**READY, "fx": 12, "fy": -19, "sa": -0.75}
POSES = [
    {}, READY, GUARD,
    {**GUARD, "crouch": 4, "lean": -4, "fx": -9, "fy": -33, "sa": -2.7, "bx": 9, "by": -22, "armsFront": True},
    {**GUARD, "crouch": 4, "lean": 5, "fx": 24, "fy": -19, "sa": 0.6, "ffx": 13, "fbx": -10},
    {"crouch": 8, "lean": 6, "fx": 16, "fy": -6, "bx": 12, "by": -8, "ffx": 9, "fbx": -9, "toeB": True},
    {"fx": -6, "fy": -40, "bx": 8, "by": -40, "turn": 1, "hy": -1},
    {"x": 10, "y": -14, "fx": 30, "fy": -26, "bx": -12, "by": -20, "ffx": 12, "ffy": -10, "fbx": -10, "fby": -2},
    {"yaw": 1.2, "fx": 14, "fy": -24, "lean": 3},
    {"yaw": 3.14159, "crouch": 2, "hx": 1},
    {"fx": 40, "fy": -20, "bx": -30, "by": -20},
    {"twist": 2, "fx": 6, "fy": -28, "bx": 2, "by": -30, "toeF": True, "fz": 6, "bz": -6},
]
TRILHAS = [
    [[-0.5, GUARD], [-0.2, POSES[3]], [0.06, POSES[4], "snap"], [0.3, POSES[5], "out"], [0.7, GUARD, "in"],
     [1.0, READY, "line"], [1.4, {}]],
    [[0, {"crouch": 0}], [0.25, {"crouch": 6, "x": 8}], [0.6, {"crouch": 0, "x": 20, "y": -4}, "out"]],
]


def _js():
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        json.dump({"poses": POSES, "trilhas": TRILHAS}, f)
        caminho = f.name
    r = subprocess.run(["node", str(AQUI / "esqueleto.mjs"), caminho], capture_output=True, text=True)
    Path(caminho).unlink(missing_ok=True)
    if r.returncode:
        raise RuntimeError(r.stderr)
    return json.loads(r.stdout)


def _dif_juntas(a, b, k=1.0):
    return max(abs(a[n][i] - b[n][i] * k) for n in b for i in range(3))


def _dif_pose(a, b):
    pior = 0.0
    for n in set(a) | set(b):
        va, vb = a.get(n), b.get(n)
        if isinstance(va, (int, float)) and isinstance(vb, (int, float)) and not isinstance(va, bool):
            pior = max(pior, abs(va - vb))
        elif va != vb and not (va in (None, False) and vb in (None, False)):
            return float("inf")
    return pior


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    js = _js()
    b1, b25 = Bipede(escala=1), Bipede(escala=2.5)
    falhas = 0
    pior1 = max(_dif_juntas(b1.juntas(p), j["juntas"]) for p, j in zip(POSES, js["poses"]))
    pior25 = max(_dif_juntas(b25.juntas(p), j["juntas"], 2.5) for p, j in zip(POSES, js["poses"]))
    for nome, v, tol in (("juntas escala 1", pior1, 1e-6), ("juntas escala 2,5 (= 2,5 × JS)", pior25, 1e-6)):
        ok = v <= tol
        falhas += not ok
        print(f"{'OK   ' if ok else 'FALHA'} {nome:34} pior diferença {v:.2e} px em {len(POSES)} poses")
    pior_t, n = 0.0, 0
    for tr, amostras in zip(TRILHAS, js["trilhas"]):
        t = tr[0][0] - 0.1
        for ref in amostras:
            pior_t = max(pior_t, _dif_pose(poseAt(tr, t), ref))
            t += 1 / 60
            n += 1
    ok = pior_t <= 1e-6
    falhas += not ok
    print(f"{'OK   ' if ok else 'FALHA'} {'poseAt (trilhas)':34} pior diferença {pior_t:.2e} em {n} amostras")
    try:
        from ..esqueleto.raster import silhueta
        ious = []
        for p, j in zip(POSES, js["poses"]):
            a = set(silhueta(b1, p))
            b = {tuple(x) for x in j["pixels"]}
            ious.append(len(a & b) / max(1, len(a | b)))
        ok = min(ious) >= 0.85
        falhas += not ok
        print(f"{'OK   ' if ok else 'FALHA'} {'silhueta (sobreposição)':34} mínima {min(ious):.3f}  média {sum(ious) / len(ious):.3f}")
    except ImportError:
        print("—     silhueta: raster ainda não existe")
    return 1 if falhas else 0


if __name__ == "__main__":
    sys.exit(main())
