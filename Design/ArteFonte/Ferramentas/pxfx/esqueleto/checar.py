"""Checagens de animação — o que o olho deixa passar (inspirado no `tools/check.mjs` do PixelFX, MIT).

Julga MOVIMENTO em passos consecutivos de 12 fps, não amostras soltas:
- chão: os pés ficam na linha do pivô quando a pose não pula (style-bible: "chão e sombra estáveis");
- salto: dois passos seguidos com silhueta muito diferente sem uma chave "snap" pedindo = estalo;
- emenda: num loop, o último passo para o primeiro não pode mudar mais que um passo normal;
- cores: até 32 por sprite (ADR-011) e, com `regiao` no rig, todas da paleta regional;
- órfãos: pixel de cor única cercado de pixels de outra cor (a regra "sem pixel órfão").
"""
from __future__ import annotations

import numpy as np

from ..cor import hex, paleta_regional


def _iou(a, b):
    ma, mb = a[..., 3] > 0, b[..., 3] > 0
    u = np.logical_or(ma, mb).sum()
    return 1.0 if u == 0 else float(np.logical_and(ma, mb).sum() / u)


def _orfaos(img):
    a = img[..., 3] > 0
    c = img[..., :3].astype(np.int32)
    cod = (c[..., 0] << 16) | (c[..., 1] << 8) | c[..., 2]
    cod = np.where(a, cod, -1)
    centro = cod[1:-1, 1:-1]
    viz = [cod[:-2, 1:-1], cod[2:, 1:-1], cod[1:-1, :-2], cod[1:-1, 2:]]
    todos_opacos = np.all([v >= 0 for v in viz], axis=0)
    diferente = np.all([v != centro for v in viz], axis=0)
    return int(np.sum((centro >= 0) & todos_opacos & diferente)), int(a.sum())


def checar(quadros, pivo, anim, rig):
    from .animar import amostras, pose_no_tempo
    rel = []
    ts = amostras(anim)
    poses = [pose_no_tempo(anim, t) for t in ts]
    chao = pivo[1]
    piores = []
    for img, p in zip(quadros, poses):
        if (p.get("y") or 0) < -0.5:
            continue
        linhas = np.where((img[..., 3] > 0).any(axis=1))[0]
        if len(linhas):
            piores.append(abs(int(linhas.max()) - chao))
    d = max(piores) if piores else 0
    rel.append(f"{'OK   ' if d <= 2 else 'AVISO'} chão: pés a no máximo {d} px da linha do pivô nos passos sem pulo")
    snaps = {round(ch[0] * 12) for ch in anim["chaves"] if len(ch) > 2 and ch[2] == "snap"}
    ious = [_iou(quadros[i], quadros[i + 1]) for i in range(len(quadros) - 1)]
    saltos = [i for i, v in enumerate(ious) if v < 0.45 and round(ts[i + 1] * 12) not in snaps]
    if ious:
        rel.append(f"{'OK   ' if not saltos else 'AVISO'} salto: menor semelhança entre passos {min(ious):.2f}"
                   + (f" — estalo nos passos {saltos} (sem 'snap' pedindo)" if saltos else ""))
    if anim.get("loop") and len(quadros) > 2:
        em = _iou(quadros[-1], quadros[0])
        ok = em >= min(ious) * 0.9
        rel.append(f"{'OK   ' if ok else 'FALHA'} emenda do loop: {em:.2f} (passo normal mais diferente {min(ious):.2f})")
    cores = set()
    for img in quadros:
        a = img[..., 3] > 0
        for r, g, b in img[a][:, :3]:
            cores.add((int(r), int(g), int(b)))
    rel.append(f"{'OK   ' if len(cores) <= 32 else 'FALHA'} cores: {len(cores)} (máx. 32 por sprite)")
    if rig.get("regiao"):
        pal = {hex(c) & 0xFFFFFF for c in paleta_regional(rig["regiao"]).values()}
        fora = [c for c in cores if ((c[2] << 16) | (c[1] << 8) | c[0]) not in pal]
        rel.append(f"{'OK   ' if not fora else 'FALHA'} paleta {rig['regiao']}: {len(fora)} cor(es) fora")
    orf, tot = 0, 0
    for img in quadros:
        o, t = _orfaos(img)
        orf, tot = orf + o, tot + t
    taxa = orf / max(1, tot)
    rel.append(f"{'OK   ' if taxa <= 0.005 else 'AVISO'} órfãos: {orf} pixel(s) isolado(s) ({taxa * 100:.2f}% do corpo)")
    return rel
