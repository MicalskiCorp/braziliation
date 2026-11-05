"""Gera a animação de um personagem a partir de dados: rig.json + anim.json → sheet + JSON + folhas de crítica.

    py -m pxfx.esqueleto.animar <rig.json> --referencia                gabarito da pele (descanso + mapa de partes)
    py -m pxfx.esqueleto.animar <rig.json> <acao.anim.json>             a animação
    py -m pxfx.esqueleto.animar <rig.json> --biblioteca melee/sword-slash --acao ataque
                                                                        uma atuação da biblioteca (atos_pixelfx.json)
Opções: --out DIR  --gif  --zoom N

rig.json (no context pack do personagem):
    {"nome": "chr_x", "modelo": "bipede|mecanico|quadrupede|serpente", "escala": 2.5,
     "medidas": {...}, "variante": {"pes_invertidos": true, "pernas": 1}, "mult_volumes": {"head": 1.2},
     "rampas": {"pele": ["#..", "#..", "#..", "#.."], ...},     aceso → escuro, keys da paleta regional
     "contorno": "seletivo", "pele": "chr_x.pele.png", "pele_origem": [x, y]}
anim.json:
    {"acao": "ataque", "loop": false, "passo": 12, "respira": false,
     "chaves": [[t, {pose}, "snap|out|in|line"], ...],           pose em px do boneco de 38 px
     "eventos": [{"t": 0.06, "tipo": "impacto", "congela": 0.14, "tremor": 0.18, "amp": 2}]}

Saída: {nome}_{acao}_sheet.png + .json (ADR-016: quadro, pivô, duração por quadro, loop, eventos),
_contact.png (quadros únicos, rotulados), _tira.png (passos consecutivos de 12 fps — é onde se julga
o MOVIMENTO), .gif, e o relatório de checagens (anim_check). Retoques manuais: {acao}.retoques/fNN.png
sobrepostos ao quadro NN; se o quadro base mudar, o JSON lista o retoque em "retoques_a_revisar".
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from pathlib import Path

import numpy as np
from PIL import Image

from ..atuacao import isHeld, poseAt
from ..cor import hex
from ..matematica import jsround
from .bipede import STAND, Bipede
from .corpo import PARTES, Mecanico, desenhar
from .pele import Pele, carregar_pele
from .raster import RAMPAS_MANEQUIM

AQUI = Path(__file__).resolve().parent
BIBLIOTECA = AQUI / "biblioteca" / "atos_pixelfx.json"
SAIDA = Path(__file__).resolve().parents[3] / "IA" / "Outputs" / "pxfx" / "esqueleto"


def modelo_de(rig):
    tipo = rig.get("modelo", "bipede")
    k = rig.get("escala", 2.5)
    var = rig.get("variante", {})
    if tipo == "bipede":
        return Bipede(rig.get("medidas"), k, var.get("pes_invertidos", False), var.get("pernas", 2))
    if tipo == "mecanico":
        return Mecanico(rig.get("medidas"), k, var.get("pes_invertidos", False), var.get("pernas", 2))
    if tipo == "quadrupede":
        from .quadrupede import Quadrupede
        return Quadrupede(rig.get("medidas"), k)
    if tipo == "serpente":
        from .serpente import Serpente
        return Serpente(rig.get("medidas"), k)
    raise ValueError(f"modelo desconhecido: {tipo}")


def carregar_rig(caminho):
    caminho = Path(caminho)
    rig = json.loads(caminho.read_text(encoding="utf-8"))
    rig["_pasta"] = caminho.parent
    return rig


def _rampas_volume(rig):
    r = dict(RAMPAS_MANEQUIM)
    r.update(rig.get("rampas_volume", {}))
    return r


def _pele(rig, modelo):
    if not rig.get("pele"):
        return None
    caminho = rig["_pasta"] / rig["pele"]
    if not caminho.exists():
        print(f"aviso: pele {caminho.name} não existe ainda — usando o manequim")
        return None
    desc = desenhar(modelo, {}, _rampas_volume(rig), rig.get("contorno", "seletivo"), mult=rig.get("mult_volumes"))
    return Pele(carregar_pele(caminho), rig.get("pele_origem", [0, 0]), rig.get("rampas", {}), desc, modelo.k,
                rig.get("tinta", "#1b1616"))


def render_pose(rig, modelo, pose, pele=None):
    s = desenhar(modelo, pose, _rampas_volume(rig), rig.get("contorno", "seletivo"), com_src=pele is not None,
                 mult=rig.get("mult_volumes"))
    if pele is None and rig.get("tinta"):
        t = hex(rig["tinta"])
        s["color"] = [t if ink else c for c, ink in zip(s["color"], s["ink"])]
    if pele:
        s = pele.aplicar(s)
    k = modelo.k
    dx, dy = jsround((pose.get("x") or 0) * k), jsround((pose.get("y") or 0) * k)
    return [(x + dx, y + dy, c, p) for x, y, c, p in zip(s["xs"], s["ys"], s["color"], s["parte"])]


def amostras(anim):
    ch = anim["chaves"]
    passo = anim.get("passo", 12)
    if anim.get("loop"):
        D = anim.get("duracao") or ch[-1][0]
        n = max(1, jsround(D * passo))
        return [ch[0][0] + i / passo for i in range(n)]
    t0, t1 = ch[0][0], ch[-1][0]
    n = max(1, jsround((t1 - t0) * passo)) + 1
    return [t0 + i / passo for i in range(n)]


def pose_no_tempo(anim, t):
    q = dict(poseAt(anim["chaves"], t, anim.get("passo", 12)))
    if anim.get("respira") and not anim.get("loop") and isHeld(anim["chaves"], t):
        up = math.floor(t * 3) & 1
        base = dict(STAND)
        base.update(q)
        base["crouch"] = (base.get("crouch") or 0) + up
        base["fy"] = (base.get("fy") or STAND["fy"]) + up
        base["by"] = (base.get("by") or STAND["by"]) + up
        q = base
    return q


def _rgba(c):
    return (c & 255, (c >> 8) & 255, (c >> 16) & 255, 255)


def montar_quadros(listas, margem=2):
    xs = [x for lst in listas for x, _, _, _ in lst] or [0]
    ys = [y for lst in listas for _, y, _, _ in lst] or [0]
    x0, x1, y0, y1 = min(xs) - margem, max(xs) + margem, min(ys) - margem, max(ys) + margem
    w, h = x1 - x0 + 1, y1 - y0 + 1
    quadros = []
    for lst in listas:
        img = np.zeros((h, w, 4), dtype=np.uint8)
        for x, y, c, _ in lst:
            img[y - y0, x - x0] = _rgba(c)
        quadros.append(img)
    return quadros, (-x0, -y0)


def _hash(img):
    return hashlib.sha1(img.tobytes()).hexdigest()[:16]


def aplicar_retoques(quadros_unicos, pasta_ret):
    """Sobrepõe {acao}.retoques/fNN.png e confere se o quadro base mudou desde o retoque."""
    revisar = []
    if not pasta_ret.exists():
        return quadros_unicos, revisar
    reg_path = pasta_ret / "retoques.json"
    reg = json.loads(reg_path.read_text(encoding="utf-8")) if reg_path.exists() else {}
    novos = []
    for i, img in enumerate(quadros_unicos):
        f = pasta_ret / f"f{i:02d}.png"
        if not f.exists():
            novos.append(img)
            continue
        base = _hash(img)
        if reg.get(f.stem) and reg[f.stem] != base:
            revisar.append(f.name)
        reg.setdefault(f.stem, base)
        ov = np.asarray(Image.open(f).convert("RGBA"), dtype=np.uint8)
        out = img.copy()
        if ov.shape == img.shape:
            m = ov[..., 3] > 0
            out[m] = ov[m]
        else:
            revisar.append(f"{f.name} (tamanho {ov.shape[1]}x{ov.shape[0]} ≠ {img.shape[1]}x{img.shape[0]})")
        novos.append(out)
    reg_path.write_text(json.dumps(reg, indent=1), encoding="utf-8")
    return novos, revisar


def _ampliar(img, z):
    return np.repeat(np.repeat(img, z, axis=0), z, axis=1)


def _fundo(img, cor=(21, 19, 29)):
    out = np.zeros_like(img)
    out[..., :3] = cor
    out[..., 3] = 255
    a = img[..., 3:4] > 0
    return np.where(a, img, out)


def folha(quadros, rotulos, z=3, colunas=8, pad=6):
    h, w = quadros[0].shape[:2]
    n = len(quadros)
    cols = min(colunas, n)
    rows = math.ceil(n / cols)
    from ..fonte import rasterText
    W, H = pad + cols * (w * z + pad), pad + rows * (h * z + 14 + pad)
    out = np.zeros((H, W, 4), dtype=np.uint8)
    out[..., :3] = (12, 11, 16)
    out[..., 3] = 255
    for i, (img, rot) in enumerate(zip(quadros, rotulos)):
        x = pad + (i % cols) * (w * z + pad)
        y = pad + (i // cols) * (h * z + 14 + pad)

        def plot(gx, gy, x=x, y=y):
            out[y + gy * 2:y + gy * 2 + 2, x + gx * 2:x + gx * 2 + 2, :3] = (150, 144, 170)

        rasterText(str(rot).upper(), "mini", plot)
        out[y + 14:y + 14 + h * z, x:x + w * z] = _ampliar(_fundo(img), z)
    return Image.fromarray(out, "RGBA")


def gerar(rig, anim, out, gif=True, zoom=3):
    modelo = modelo_de(rig)
    pele = _pele(rig, modelo)
    ts = amostras(anim)
    poses = [pose_no_tempo(anim, t) for t in ts]
    listas = [render_pose(rig, modelo, p, pele) for p in poses]
    quadros, pivo = montar_quadros(listas)
    # passos iguais em seguida viram UM quadro segurado: é a duração por quadro do ADR-016
    passo_ms = 1000 / anim.get("passo", 12)
    unicos, dur, inicio = [], [], []
    for i, img in enumerate(quadros):
        if unicos and np.array_equal(unicos[-1], img):
            dur[-1] += passo_ms
        else:
            unicos.append(img)
            dur.append(passo_ms)
            inicio.append(ts[i])
    nome = f"{rig.get('nome', 'chr_manequim')}_{anim.get('acao', 'acao')}"
    unicos, revisar = aplicar_retoques(unicos, rig["_pasta"] / f"{anim.get('acao', 'acao')}.retoques")
    eventos = []
    for ev in anim.get("eventos", []):
        qi = max([i for i, t in enumerate(inicio) if t <= ev["t"] + 1e-9] or [0])
        e = dict(ev)
        e["quadro"] = qi
        eventos.append(e)
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    h, w = unicos[0].shape[:2]
    sheet = np.concatenate(unicos, axis=1)
    Image.fromarray(sheet, "RGBA").save(out / f"{nome}_sheet.png")
    dados = {
        "formato": "braziliation-sheet/1", "origem": f"pxfx.esqueleto:{rig.get('modelo', 'bipede')}",
        "imagem": f"{nome}_sheet.png", "quadro": [w, h], "quadros": len(unicos), "pivo": list(pivo),
        "loop": bool(anim.get("loop")), "fps": anim.get("passo", 12),
        "duracoes_ms": [jsround(d) for d in dur], "eventos": eventos,
    }
    if revisar:
        dados["retoques_a_revisar"] = revisar
    (out / f"{nome}_sheet.json").write_text(json.dumps(dados, ensure_ascii=False, indent=2), encoding="utf-8")
    folha(unicos, [f"{i} {d:.0f}MS" for i, d in enumerate(dur)], z=zoom).save(out / f"{nome}_contact.png")
    folha(quadros, [f"{t:+.2f}" for t in ts], z=max(1, zoom - 1), colunas=12).save(out / f"{nome}_tira.png")
    if gif:
        frames = [Image.fromarray(_ampliar(_fundo(q), zoom), "RGBA").convert("RGB") for q in unicos]
        frames[0].save(out / f"{nome}.gif", save_all=True, append_images=frames[1:],
                       duration=[jsround(d) for d in dur], loop=0)
    from .checar import checar
    relatorio = checar(quadros, pivo, anim, rig)
    return nome, dados, relatorio


def referencia(rig, out, zoom=4):
    """O gabarito da pele: a pose de descanso no manequim + o mapa de partes (uma cor por peça)."""
    modelo = modelo_de(rig)
    s = desenhar(modelo, {}, _rampas_volume(rig), rig.get("contorno", "seletivo"), com_src=False,
                 mult=rig.get("mult_volumes"))
    lst = list(zip(s["xs"], s["ys"], s["color"], s["parte"]))
    (img,), pivo = montar_quadros([lst])
    partes = np.zeros_like(img)
    nomes = {v: k for k, v in PARTES.items()}
    cores = {}
    for x, y, c, p in lst:
        if not p:
            continue
        h_ = int(hashlib.md5(nomes.get(p, str(p)).encode()).hexdigest()[:6], 16)
        cores[nomes.get(p, str(p))] = f"#{h_:06x}"
        partes[y + pivo[1], x + pivo[0]] = ((h_ >> 16) & 255, (h_ >> 8) & 255, h_ & 255, 255)
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    nome = rig.get("nome", "chr_manequim")
    Image.fromarray(img, "RGBA").save(out / f"{nome}.referencia.png")
    Image.fromarray(partes, "RGBA").save(out / f"{nome}.partes.png")
    Image.fromarray(_ampliar(_fundo(img), zoom), "RGBA").save(out / f"{nome}.referencia_x{zoom}.png")
    info = {"pele_origem": list(pivo), "tamanho": [img.shape[1], img.shape[0]], "partes": cores,
            "como_usar": "pinte a pele POR CIMA de .referencia.png (mesmo tamanho, mesma origem), salve como "
                         "{nome}.pele.png e aponte 'pele' e 'pele_origem' no rig.json"}
    (out / f"{nome}.referencia.json").write_text(json.dumps(info, ensure_ascii=False, indent=2), encoding="utf-8")
    return info


def anim_da_biblioteca(id_, acao=None):
    atos = json.loads(BIBLIOTECA.read_text(encoding="utf-8"))["atos"]
    a = atos[id_]
    return {"acao": acao or id_.split("/")[1].replace("-", "_"), "loop": a["loop"], "passo": 12,
            "chaves": a["chaves"], "duracao": a["duracao"] if a["loop"] else None,
            "eventos": [{"t": h["t"], "tipo": "impacto", "congela": h["congela"], "tremor": h["tremor"], "amp": h["amp"]}
                        for h in a["impactos"]]}


def main(argv=None):
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("rig")
    ap.add_argument("anim", nargs="?")
    ap.add_argument("--referencia", action="store_true")
    ap.add_argument("--biblioteca")
    ap.add_argument("--acao")
    ap.add_argument("--out")
    ap.add_argument("--zoom", type=int, default=3)
    ap.add_argument("--sem-gif", action="store_true")
    a = ap.parse_args(argv)
    rig = carregar_rig(a.rig)
    out = Path(a.out) if a.out else SAIDA / rig.get("nome", "chr_manequim")
    if a.referencia:
        info = referencia(rig, out)
        print(f"gabarito em {out}  (origem dos pés {info['pele_origem']}, {info['tamanho'][0]}x{info['tamanho'][1]})")
        return 0
    if a.biblioteca:
        anim = anim_da_biblioteca(a.biblioteca, a.acao)
    else:
        anim = json.loads(Path(a.anim).read_text(encoding="utf-8"))
    nome, dados, rel = gerar(rig, anim, out, gif=not a.sem_gif, zoom=a.zoom)
    print(f"{nome}: {dados['quadros']} quadros únicos {dados['quadro'][0]}x{dados['quadro'][1]}  "
          f"durações {dados['duracoes_ms']}  eventos {[(e['tipo'], e['quadro']) for e in dados['eventos']]}")
    for linha in rel:
        print("  " + linha)
    print(f"  -> {out}")
    return 1 if any(l.startswith("FALHA") for l in rel) else 0


if __name__ == "__main__":
    sys.exit(main())
