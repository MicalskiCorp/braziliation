"""Checa efeitos pelos erros que o olho deixa passar (port enxuto de `tools/check.mjs` do PixelFX, MIT).

    py -m pxfx.check                 todos os efeitos portados
    py -m pxfx.check fire/torch --escala 2.5

- meta: name, size, origin, duration presentes;
- sobra: nada desenhado fora do canvas (renderiza com margem de 24 px e procura pixel fora);
- fim: one-shot termina VAZIO no último quadro;
- emenda: num loop, o último quadro para o primeiro não muda mais que um passo normal;
- determinismo: o mesmo t duas vezes dá o mesmo quadro;
- tempo: menos de 2 ms por quadro no original — aqui o teto é 250 ms × escala² (Python), só para pegar explosão de custo.
"""
from __future__ import annotations

import argparse
import sys
import time

import numpy as np

from .renderizar import loadEffect, renderFrames, resolveIds, allIds

M = 24


def _diff(a, b):
    return float(np.mean(np.any(a != b, axis=-1)))


def checar(id_, escala=None):
    fx = loadEffect(id_)
    meta = fx.meta
    prob = []
    for campo in ("name", "size", "origin", "duration"):
        if meta.get(campo) is None:
            prob.append(f"meta sem {campo}")
    t0 = time.perf_counter()
    r = renderFrames(fx, margin=M, escala=escala, bg="none")
    ms = (time.perf_counter() - t0) * 1000 / max(1, r.n)
    fora = 0
    for f in r.frames:
        # só o buffer de COR: luz que passa da borda é suavizada pelo edgeFade, como no original
        a = (np.asarray(f.raw, dtype=np.uint64) != 0).reshape(r.h, r.w)
        dentro = np.zeros_like(a)
        dentro[M:-M, M:-M] = True
        fora = max(fora, int(np.sum(a & ~dentro)))
    if fora:
        prob.append(f"sobra: {fora} px fora do canvas")
    ult = r.frames[-1].transparente
    if not meta.loop and np.any(ult[..., 3] > 0):
        prob.append(f"fim: one-shot não termina vazio ({int(np.sum(ult[..., 3] > 0))} px no último quadro)")
    if meta.loop and r.n > 2:
        passos = [_diff(r.frames[i].transparente, r.frames[i + 1].transparente) for i in range(r.n - 1)]
        em = _diff(r.frames[-1].transparente, r.frames[0].transparente)
        if em > max(passos) * 1.5 + 0.002:
            prob.append(f"emenda: volta do loop muda {em:.3f} (passo normal até {max(passos):.3f})")
    r2 = renderFrames(fx, margin=M, escala=escala, bg="none")
    if any(not np.array_equal(a.transparente, b.transparente) for a, b in zip(r.frames, r2.frames)):
        prob.append("determinismo: dois renders diferem (aleatório sem seed?)")
    teto = 250 * (escala or 1) ** 2
    if ms > teto:
        prob.append(f"tempo: {ms:.0f} ms por quadro (teto {teto:.0f} na escala {escala or 1})")
    return prob, ms


def main(argv=None):
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("ids", nargs="*")
    ap.add_argument("--escala", type=float)
    a = ap.parse_args(argv)
    ids = resolveIds(a.ids) if a.ids else allIds()
    falhas = 0
    for id_ in ids:
        prob, ms = checar(id_, a.escala)
        falhas += bool(prob)
        print(f"{'OK   ' if not prob else 'FALHA'} {id_:34} {ms:6.0f} ms/quadro  " + "; ".join(prob))
    return 1 if falhas else 0


if __name__ == "__main__":
    sys.exit(main())
