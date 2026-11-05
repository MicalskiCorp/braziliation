"""Renderiza efeitos para olhar e exportar.

    py -m pxfx.render fire/torch                     folha de contato em <out>/fire/torch/contact.png
    py -m pxfx.render fire --gif                     a categoria inteira, com GIF de cada um
    py -m pxfx.render fire/torch --escala 2.5        na escala do grid de 96 px (ADR-011)
    py -m pxfx.render fire/torch --sheet --nome vfx_tocha_parede   sheet + JSON lateral (ADR-016)
    py -m pxfx.render fire/torch --opts '{"palette": ["#1b1616", "#5a2a1a", "#b8641f", "#f2c14e"]}'

Opções: --gif --sheet --all (todo quadro na folha) --max N --zoom N --bg dark|ground|sky|light|black|none
--seed N --fps N --escala K --regiao blumenau --rampa 1,2,6,8 (recolore pela paleta regional) --out DIR
Roda da pasta Design/ArteFonte/Ferramentas/. Saída padrão: Design/ArteFonte/IA/Outputs/pxfx/.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .cor import rampa_regional
from .renderizar import contactSheet, gif, loadEffect, renderFrames, resolveIds, salvar_json, salvar_png, spriteSheet

SAIDA = Path(__file__).resolve().parents[2] / "IA" / "Outputs" / "pxfx"


def main(argv=None):
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("ids", nargs="+")
    ap.add_argument("--gif", action="store_true")
    ap.add_argument("--sheet", action="store_true")
    ap.add_argument("--nome", help="nome base do sheet (padrão vfx_<categoria>_<efeito>)")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--max", type=int, default=16)
    ap.add_argument("--zoom", type=int)
    ap.add_argument("--bg")
    ap.add_argument("--seed", type=int)
    ap.add_argument("--fps", type=int)
    ap.add_argument("--escala", type=float)
    ap.add_argument("--opts", help="opções do efeito em JSON")
    ap.add_argument("--regiao", help="paleta regional para --rampa")
    ap.add_argument("--rampa", help="keys da paleta regional, escuro → claro, ex.: 1,2,6,8")
    ap.add_argument("--no-actor", action="store_true")
    ap.add_argument("--out", default=str(SAIDA))
    a = ap.parse_args(argv)

    opts = json.loads(a.opts) if a.opts else {}
    if a.rampa:
        opts["palette"] = rampa_regional(a.regiao or "blumenau", a.rampa.split(","))
    falhas = 0
    for id_ in resolveIds(a.ids):
        try:
            fx = loadEffect(id_)
            r = renderFrames(fx, fps=a.fps, seed=a.seed, bg=a.bg, options=opts, escala=a.escala,
                             actor=False if a.no_actor else None)
            pasta = Path(a.out) / id_
            mx = r.n if a.all else a.max
            salvar_png(contactSheet(fx, r, mx=mx, zoom=a.zoom), pasta / "contact.png")
            linha = f"{id_:34} {r.n:3} quadros  {r.w}x{r.h}  ->  {pasta / 'contact.png'}"
            if a.gif:
                gif(r, pasta / f"{id_.split('/')[1]}.gif")
            if a.sheet:
                nome = a.nome or f"vfx_{id_.replace('/', '_').replace('-', '_')}"
                img, dados = spriteSheet(fx, r, f"{nome}_sheet")
                salvar_png(img, pasta / f"{nome}_sheet.png")
                salvar_json(dados, pasta / f"{nome}_sheet.json")
                linha += f"  + {nome}_sheet.png/.json"
            print(linha)
        except Exception as e:  # noqa: BLE001
            falhas += 1
            print(f"ERRO  {id_}: {type(e).__name__}: {e}")
    return 1 if falhas else 0


if __name__ == "__main__":
    sys.exit(main())
