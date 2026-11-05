"""Volumes de cada modelo de corpo e `desenhar(modelo, pose)`.

- bípede: os volumes do boneco do PixelFX (MIT), raios × escala;
- mecânico: o mesmo esqueleto vestido de caixas e chapas (autômatos) — material "metal", tinta nas juntas;
- quadrúpede e serpente: `quadrupede.py`, `serpente.py`.

Cada modelo expõe `solve(pose)` → {"B": referenciais por nome, ...}, `FRAME_IDS` e `volumes(S, r)`.
"""
from __future__ import annotations

from .bipede import FRAME_IDS, Bipede
from .raster import Raster
from .vetor import add, mv

PARTES = {n: i + 1 for i, n in enumerate([
    "pelvis", "waist", "chest", "neck", "head", "face", "upperN", "elbowN", "foreN", "handN", "upperF", "elbowF",
    "foreF", "handF", "thighN", "kneeN", "shinN", "footN", "thighF", "kneeF", "shinF", "footF", "extra1", "extra2",
    "extra3", "extra4", "extra5", "extra6", "extra7", "extra8", "extra9", "extra10", "extra11", "extra12", "extra13",
    "extra14", "extra15", "extra16", "extra17", "extra18", "extra19", "extra20", "extra21", "extra22", "extra23",
    "extra24", "extra25", "extra26", "extra27", "extra28", "extra29", "extra30", "extra31", "extra32"])}


def _usa(r, nome, ids):
    r.cur_frame = ids.index(nome) if nome in ids else -1


def volumes_bipede(S, r, mult=None, mat_casca="casca", mat_nucleo="nucleo"):
    """O corpo do boneco do PixelFX: elipsoides no tronco e cabeça, cápsulas nos membros, esferas nas juntas."""
    k = r.k
    m = mult or {}

    def R_(nome, v):
        return v * k * m.get(nome, 1.0)

    B = S["B"]
    P = PARTES
    _usa(r, "pelvis", FRAME_IDS)
    r.elipsoide(add(B["pelvis"]["t"], mv(B["pelvis"]["R"], [0, -0.2 * k, 0])), B["pelvis"]["R"],
                [R_("pelvis", 2.9), R_("pelvis", 2.6), R_("pelvis", 4.2)], P["pelvis"], mat_casca)
    _usa(r, "waist", FRAME_IDS)
    r.capsula(B["pelvis"]["t"], B["chest"]["t"], R_("waist", 3), R_("waist", 3.3), P["waist"], mat_nucleo)
    _usa(r, "chest", FRAME_IDS)
    r.elipsoide(add(B["chest"]["t"], mv(B["chest"]["R"], [0.2 * k, 0.9 * k, 0])), B["chest"]["R"],
                [R_("chest", 3.4), R_("chest", 4.2), R_("chest", 5.5)], P["chest"], mat_casca)
    _usa(r, "neck", FRAME_IDS)
    r.capsula(B["neck"]["t"], add(B["neck"]["t"], mv(B["head"]["R"], [0, 1.6 * k, 0])), R_("neck", 1.25),
              R_("neck", 1.15), P["neck"], mat_nucleo)
    _usa(r, "head", FRAME_IDS)
    r.elipsoide(B["head"]["t"], B["head"]["R"], [R_("head", 3), R_("head", 3.3), R_("head", 2.8)], P["head"], mat_casca)
    r.elipsoide(add(B["head"]["t"], mv(B["head"]["R"], [0.85 * k, -0.45 * k, 0])), B["head"]["R"],
                [R_("head", 2.4), R_("head", 2.7), R_("head", 2.35)], P["face"], mat_casca)

    def braco(longe, A, sh, sfx):
        r.cur_dim = 1 if longe else 0
        _usa(r, "upper" + sfx, FRAME_IDS)
        r.esfera(sh, R_("upper", 2.5), P["upper" + sfx], mat_casca)
        r.capsula(sh, A["joint"], R_("upper", 2.1), R_("upper", 1.6), P["upper" + sfx], mat_casca)
        r.esfera(A["joint"], R_("elbow", 1.45), P["elbow" + sfx], mat_nucleo)
        _usa(r, "fore" + sfx, FRAME_IDS)
        r.capsula(A["joint"], A["end"], R_("fore", 1.6), R_("fore", 1.2), P["fore" + sfx], mat_casca, 0.15 * k)
        r.esfera(A["end"], R_("hand", 1.9), P["hand" + sfx], mat_casca)
        r.cur_dim = 0

    braco(False, S["armN"], S["sN"], "N")
    braco(True, S["armF"], S["sF"], "F")

    def perna(longe, L, hip, sfx):
        r.cur_dim = 1 if longe else 0
        _usa(r, "thigh" + sfx, FRAME_IDS)
        r.capsula(hip, L["joint"], R_("thigh", 3.2), R_("thigh", 2.2), P["thigh" + sfx], mat_casca)
        r.esfera(L["joint"], R_("knee", 1.9), P["knee" + sfx], mat_nucleo)
        _usa(r, "shin" + sfx, FRAME_IDS)
        r.capsula(L["joint"], L["end"], R_("shin", 2.15), R_("shin", 1.4), P["shin" + sfx], mat_casca, 0.4 * k)
        _usa(r, "foot" + sfx, FRAME_IDS)
        F = B["foot" + sfx]
        r.capsula(add(F["t"], mv(F["R"], [-1.5 * k, -0.6 * k, 0])), add(F["t"], mv(F["R"], [4.6 * k, -1.1 * k, 0])),
                  R_("foot", 1.7), R_("foot", 1.25), P["foot" + sfx], mat_casca)
        r.cur_dim = 0

    perna(False, S["legN"], S["hipN"], "N")
    if getattr(S.get("modelo"), "pernas", 2) >= 2:
        perna(True, S["legF"], S["hipF"], "F")


def volumes_mecanico(S, r, mult=None):
    """Autômato: o esqueleto bípede vestido de chapas e blocos de metal. Engrenagens e detalhe ficam na pele."""
    k = r.k
    m = mult or {}
    B = S["B"]
    P = PARTES

    def R_(nome, v):
        return v * k * m.get(nome, 1.0)

    _usa(r, "pelvis", FRAME_IDS)
    r.caixa(add(B["pelvis"]["t"], mv(B["pelvis"]["R"], [0, -0.4 * k, 0])), B["pelvis"]["R"],
            [R_("pelvis", 2.8), R_("pelvis", 2.0), R_("pelvis", 3.8)], P["pelvis"], "metal")
    _usa(r, "waist", FRAME_IDS)
    r.capsula(B["pelvis"]["t"], B["chest"]["t"], R_("waist", 2.0), R_("waist", 2.0), P["waist"], "nucleo")
    _usa(r, "chest", FRAME_IDS)
    r.caixa(add(B["chest"]["t"], mv(B["chest"]["R"], [0.2 * k, 1.2 * k, 0])), B["chest"]["R"],
            [R_("chest", 3.4), R_("chest", 4.0), R_("chest", 5.0)], P["chest"], "metal")
    _usa(r, "head", FRAME_IDS)
    r.caixa(B["head"]["t"], B["head"]["R"], [R_("head", 2.8), R_("head", 2.8), R_("head", 2.6)], P["head"], "metal")
    S2 = dict(S)
    volumes_bipede_membros(S2, r, R_)


def volumes_bipede_membros(S, r, R_):
    """Só os membros do bípede (braços e pernas), para modelos que trocam o tronco."""
    B, P = S["B"], PARTES
    for longe, A, sh, sfx in ((False, S["armN"], S["sN"], "N"), (True, S["armF"], S["sF"], "F")):
        r.cur_dim = 1 if longe else 0
        _usa(r, "upper" + sfx, FRAME_IDS)
        r.capsula(sh, A["joint"], R_("upper", 1.8), R_("upper", 1.5), P["upper" + sfx], "metal")
        r.esfera(A["joint"], R_("elbow", 1.6), P["elbow" + sfx], "nucleo")
        _usa(r, "fore" + sfx, FRAME_IDS)
        r.capsula(A["joint"], A["end"], R_("fore", 1.5), R_("fore", 1.5), P["fore" + sfx], "metal")
        r.esfera(A["end"], R_("hand", 1.7), P["hand" + sfx], "metal")
    for longe, L, hip, sfx in ((False, S["legN"], S["hipN"], "N"), (True, S["legF"], S["hipF"], "F")):
        r.cur_dim = 1 if longe else 0
        _usa(r, "thigh" + sfx, FRAME_IDS)
        r.capsula(hip, L["joint"], R_("thigh", 2.4), R_("thigh", 2.0), P["thigh" + sfx], "metal")
        r.esfera(L["joint"], R_("knee", 1.9), P["knee" + sfx], "nucleo")
        _usa(r, "shin" + sfx, FRAME_IDS)
        r.capsula(L["joint"], L["end"], R_("shin", 2.0), R_("shin", 1.6), P["shin" + sfx], "metal")
        _usa(r, "foot" + sfx, FRAME_IDS)
        F = B["foot" + sfx]
        r.caixa(add(F["t"], mv(F["R"], [1.4 * r.k, -0.9 * r.k, 0])), F["R"], [R_("foot", 3.0), R_("foot", 1.2), R_("foot", 1.6)],
                P["foot" + sfx], "metal")
    r.cur_dim = 0


class Mecanico(Bipede):
    tipo = "mecanico"

    def volumes(self, S, r, mult=None):
        volumes_mecanico(S, r, mult)


def _volumes(modelo, S, r, mult):
    if hasattr(modelo, "volumes"):
        return modelo.volumes(S, r, mult)
    return volumes_bipede(S, r, mult)


def desenhar(modelo, pose, rampas, contorno="seletivo", com_src=True, mult=None):
    """A pose em pixels: {xs, ys, color, src, tom, mat, parte, ink} em espaço local (pés em 0, y para baixo)."""
    S = modelo.solve(pose)
    S["modelo"] = modelo
    r = Raster(modelo.k)
    ids = getattr(modelo, "FRAME_IDS", FRAME_IDS)
    _volumes(modelo, S, r, mult)
    descanso = None
    if com_src:
        cache = getattr(modelo, "_descanso", None)
        if cache is None:
            cache = modelo.solve({})["B"]
            modelo._descanso = cache
        descanso = cache
    return r.acabar(S["B"], descanso, ids, rampas, contorno)
