"""Compara um efeito portado com o original, quadro a quadro.

    py -m pxfx.paridade fire/torch                 # um efeito
    py -m pxfx.paridade fire                       # a categoria inteira (só os portados)
    py -m pxfx.paridade fire/torch --seed 7 --diff # outra seed, e grava a imagem da diferença
    py -m pxfx.paridade nucleo                     # o cenário que exercita a API inteira do núcleo

Critério (PORT.md): a cor é comparada por pixel; a luz, por canal. Diferença de 1 ulp
em seno/cosseno entre o V8 e o CPython pode virar um pixel de fronteira — por isso a
tolerância: até 0,5% dos pixels de cor e 3 níveis por canal de luz. Acima disso é bug de port.
Roda da pasta Design/ArteFonte/Ferramentas/.
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image

from ..renderizar import loadEffect, renderFrames, resolveIds

AQUI = Path(__file__).resolve().parent
TOL_COR = 0.005
TOL_LUZ = 3


def js(id_, pasta, fps=None, seed=None, opts=None):
    cmd = ["node", str(AQUI / "dump.mjs"), id_, str(pasta), str(fps or "-"), "-" if seed is None else str(seed)]
    if opts:
        cmd.append(json.dumps(opts))
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode:
        raise RuntimeError(res.stderr.strip() or res.stdout.strip())
    meta = json.loads((Path(pasta) / "meta.json").read_text())
    raw = np.fromfile(Path(pasta) / "frames.bin", dtype=np.uint32)
    return meta, raw.reshape(meta["n"], 2, meta["h"] * meta["w"])


def _fx_do_nucleo():
    from ..objeto import Obj, obj
    from . import nucleo_teste as mod
    meta = Obj(fps=30, bg="dark", loop=False, duration=1, tags=[], options={})
    meta.update(obj(mod.meta))
    mod.meta = meta
    return Obj(id="nucleo", mod=mod, meta=meta)


def compara(id_, seed=None, diff=False, saida=None, opts=None):
    alvo_js = str(AQUI / "nucleo_teste.mjs") if id_ == "nucleo" else id_
    with tempfile.TemporaryDirectory() as tmp:
        mj, bj = js(alvo_js, tmp, seed=seed, opts=opts)
    fx = _fx_do_nucleo() if id_ == "nucleo" else loadEffect(id_)
    r = renderFrames(fx, seed=seed, options=opts)
    if (r.w, r.h, r.n) != (mj["w"], mj["h"], mj["n"]):
        return False, f"tamanho difere: py {r.w}x{r.h}x{r.n}  js {mj['w']}x{mj['h']}x{mj['n']}"
    pior_cor, pior_luz, pior_q = 0.0, 0, -1
    for i, f in enumerate(r.frames):
        cp = np.asarray(f.raw, dtype=np.uint64).astype(np.uint32)
        lp = np.asarray(f.light, dtype=np.uint64).astype(np.uint32)
        cj, lj = bj[i, 0], bj[i, 1]
        frac = float(np.mean(cp != cj))
        canais = lambda a: np.stack([(a >> s) & 255 for s in (0, 8, 16)]).astype(np.int32)  # noqa: E731
        dl = int(np.max(np.abs(canais(lp) - canais(lj)))) if lp.size else 0
        if frac > pior_cor or dl > pior_luz:
            pior_q = i
        pior_cor, pior_luz = max(pior_cor, frac), max(pior_luz, dl)
        if diff and saida and i == pior_q:
            m = (cp != cj).reshape(r.h, r.w)
            img = np.zeros((r.h, r.w, 3), dtype=np.uint8)
            img[m] = (255, 40, 80)
            Image.fromarray(img).resize((r.w * 4, r.h * 4), Image.NEAREST).save(Path(saida) / f"{id_.replace('/', '-')}.diff.png")
    ok = pior_cor <= TOL_COR and pior_luz <= TOL_LUZ
    return ok, f"{r.n} quadros  cor: {pior_cor * 100:.3f}% px  luz: {pior_luz} níveis  (pior quadro {pior_q})"


def main(argv=None):
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("ids", nargs="+")
    ap.add_argument("--seed", type=int)
    ap.add_argument("--diff", action="store_true", help="grava a imagem da diferença do pior quadro")
    ap.add_argument("--out", default=str(Path(tempfile.gettempdir()) / "pxfx-paridade"))
    a = ap.parse_args(argv)
    if not shutil.which("node"):
        print("node não encontrado: a paridade precisa do Node (só para rodar o original).")
        return 2
    Path(a.out).mkdir(parents=True, exist_ok=True)
    falhas = 0
    outros = [i for i in a.ids if i != "nucleo"]
    ids = (["nucleo"] if "nucleo" in a.ids else []) + (resolveIds(outros) if outros else [])
    for id_ in ids:
        try:
            ok, msg = compara(id_, a.seed, a.diff, a.out)
        except Exception as e:  # noqa: BLE001 — relatório, não trava o lote
            ok, msg = False, f"ERRO {type(e).__name__}: {e}"
        falhas += not ok
        print(f"{'OK   ' if ok else 'FALHA'} {id_:34} {msg}")
    return 1 if falhas else 0


if __name__ == "__main__":
    sys.exit(main())
