"""Renderiza efeitos para olhar e para exportar: quadros, folha de contato, sheet + JSON, GIF.

Port de `tools/lib/fxlib.mjs` do PixelFX (MIT), com o JSON lateral do Braziliation
(ADR-016): todo sheet sai com `{sheet}.json` levando pivô, duração por quadro, loop e
eventos — é o que o `SheetAutoSlicer` e o `SheetAnimationTool` leem no Unity.
"""
from __future__ import annotations

import fnmatch
import importlib
import json
import math
from pathlib import Path

import numpy as np
from PIL import Image

from .ator import actorAlphaOf, drawActor, stockActor
from .cenario import backdrop
from .fonte import rasterText
from .matematica import jsround
from .objeto import Obj, obj
from .quadro import clearFrame, composite, createFrame, createFx, painterFor

RAIZ = Path(__file__).resolve().parent
EFEITOS = RAIZ / "efeitos"


# ---- achar e carregar efeitos -------------------------------------------------
def modulo_de(id_: str) -> str:
    cat, nome = id_.split("/", 1)
    return f"pxfx.efeitos.{cat}.{nome.replace('-', '_')}"


def allIds():
    """Todo id de efeito portado ('fire/torch'), ordenado. Arquivos com _ são auxiliares."""
    out = []
    if not EFEITOS.exists():
        return out
    for cat in sorted(p for p in EFEITOS.iterdir() if p.is_dir() and not p.name.startswith(("_", "."))):
        for f in sorted(cat.glob("*.py")):
            if not f.name.startswith("_"):
                out.append(f"{cat.name}/{f.stem.replace('_', '-')}")
    return out


def resolveIds(padroes):
    todos = allIds()
    out = []
    for p in padroes:
        hits = [i for i in todos if i == p or i.startswith(p + "/") or fnmatch.fnmatch(i, p)]
        if not hits:
            print(f"nenhum efeito portado casa com {p}")
        for h in hits:
            if h not in out:
                out.append(h)
    return out


def loadEffect(id_: str):
    mod = importlib.import_module(modulo_de(id_))
    if getattr(mod, "meta", None) is None:
        raise ValueError(f"{id_}: sem meta")
    if not hasattr(mod, "draw") and not hasattr(mod, "create"):
        raise ValueError(f"{id_}: não exporta draw nem create")
    meta = Obj(fps=30, bg="dark", loop=False, duration=1, tags=[], options={})
    meta.update(obj(mod.meta))
    mod.meta = meta
    return Obj(id=id_, mod=mod, meta=meta)


def isScreen(meta):
    """Efeito de tela cheia (transição, clima, quadro de impacto): 16:9 e ao menos 320 de largura."""
    return meta.size[0] >= 320 and abs(meta.size[0] / meta.size[1] - 16 / 9) < 0.05


def edgeFade(f, E=8):
    """Brilho cortado pela borda vira caixa no jogo: apaga a luz nos últimos E pixels. A cor fica."""
    w, h, L = f.w, f.h, f.light
    for y in range(h):
        ey = min(y, h - 1 - y)
        x = 0
        while x < w:
            e = min(ey, x, w - 1 - x)
            if e >= E:
                x = w - 1 - E + 1
                continue
            i = y * w + x
            l = L[i]
            if l & 0xFFFFFF:
                u = (e + 0.5) / E
                k = u * u * (3 - 2 * u)
                L[i] = ((l & 0xFF000000) | jsround((l & 255) * k) | (jsround(((l >> 8) & 255) * k) << 8)
                        | (jsround(((l >> 16) & 255) * k) << 16))
            x += 1


def renderFrames(fx, fps=None, seed=None, bg=None, margin=0, options=None, actor=None, escala=None):
    """Os quadros de um efeito: {w, h, fps, n, frames: [{t, color (RGBA sobre o fundo), transparente (RGBA
    transparente), raw, light}]}."""
    meta = fx.meta
    W, H = meta.size
    OX, OY = meta.origin
    k = escala or meta.get("escala") or 1
    m = margin
    w, h = math.ceil(W * k) + m * 2, math.ceil(H * k) + m * 2
    fps = fps or meta.fps
    n = max(1, jsround(meta.duration * fps) + (0 if meta.loop else 1))
    shown, bare = createFrame(w, h, -m, -m), createFrame(w, h, -m, -m)
    kind = bg or meta.bg
    fundo = None if kind == "none" else backdrop(kind, w, h, OY * k + m)
    o = {"x": OX * k, "y": OY * k}
    if k != 1:
        o["escala"] = k
    if seed is not None:
        o["seed"] = seed
    o.update(options or {})
    inst = createFx(fx.mod, o)
    ator = (inst.options.get("actor") or stockActor()) if (meta.get("actor") and actor is not False) else None
    fade = m == 0 and not isScreen(meta)
    frames = []
    for i in range(n):
        if i > 0:
            inst.update(1 / fps)
        clearFrame(shown)
        clearFrame(bare)
        inst.draw(bare)
        inst.draw(shown, "back")
        if ator:
            tt = inst.t % meta.duration if meta.loop else min(inst.t, meta.duration)
            drawActor(painterFor(shown).place(OX * k, OY * k, bool((options or {}).get("flip")), 0, k), ator,
                      actorAlphaOf(fx.mod, tt, inst.options))
        inst.draw(shown, "front")
        if fade:
            edgeFade(bare)
            edgeFade(shown)
        frames.append(Obj(t=i / fps, color=composite(shown, fundo), transparente=composite(bare, None),
                          raw=list(bare.color), light=list(bare.light)))
    return Obj(w=w, h=h, fps=fps, n=n, frames=frames, margin=m, escala=k)


# ---- imagens -----------------------------------------------------------------
def pickFrames(n, mx=16):
    if n <= mx:
        return list(range(n))
    return [jsround((i * (n - 1)) / (mx - 1)) for i in range(mx)]


def _texto(img: np.ndarray, s, x, y, k=2, cor=(232, 228, 240)):
    def plot(gx, gy):
        y0, x0 = y + gy * k, x + gx * k
        if 0 <= y0 < img.shape[0] - k and 0 <= x0 < img.shape[1] - k:
            img[y0:y0 + k, x0:x0 + k, :3] = cor
            img[y0:y0 + k, x0:x0 + k, 3] = 255
    rasterText(str(s).upper(), "mini", plot)


def contactSheet(fx, r, mx=16, width=1600, title=None, zoom=None) -> Image.Image:
    """Folha de contato: quadros em grade, rotulados com índice e tempo — o agente julga tudo numa imagem."""
    w, h, frames, fps = r.w, r.h, r.frames, r.fps
    idx = pickFrames(len(frames), mx)
    k = zoom or max(1, min(6, math.floor((width - 16) / min(len(idx), 6) / (w + 6))))
    cw, ch, pad, label = w * k, h * k, 8, 16
    cols = max(1, min(len(idx), math.floor((max(width, cw + pad * 2) - pad) / (cw + pad))))
    rows = math.ceil(len(idx) / cols)
    head = 30
    img = np.zeros((head + rows * (ch + label + pad) + pad, pad + cols * (cw + pad), 4), dtype=np.uint8)
    img[..., :3] = (12, 11, 16)
    img[..., 3] = 255
    m = fx.meta
    _texto(img, title or f"{fx.id}  {m.size[0]}x{m.size[1]}  {m.duration}S  {len(frames)}F @{fps}  "
                          f"{'LOOP' if m.loop else 'ONE-SHOT'}", pad, 8, 3)
    for j, fi in enumerate(idx):
        x = pad + (j % cols) * (cw + pad)
        y = head + (j // cols) * (ch + label + pad)
        _texto(img, f"{fi}  {frames[fi].t:.2f}", x, y, 2, (140, 134, 160))
        big = np.repeat(np.repeat(frames[fi].color, k, axis=0), k, axis=1)
        img[y + label:y + label + ch, x:x + cw] = big
    return Image.fromarray(img, "RGBA")


def spriteSheet(fx, r, nome, eventos=None):
    """Sheet em tira horizontal (o formato do SheetAutoSlicer) + JSON lateral do ADR-016."""
    w, h, frames, fps = r.w, r.h, r.frames, r.fps
    n = len(frames)
    img = np.zeros((h, w * n, 4), dtype=np.uint8)
    for i, f in enumerate(frames):
        img[:, i * w:(i + 1) * w] = f.transparente
    m = fx.meta
    k = r.get("escala") or 1
    dados = {
        "formato": "braziliation-sheet/1",
        "origem": f"pxfx:{fx.id}",
        "imagem": f"{nome}.png",
        "quadro": [w, h],
        "quadros": n,
        "pivo": [m.origin[0] * k + r.margin, m.origin[1] * k + r.margin],
        "loop": bool(m.loop),
        "fps": fps,
        "duracoes_ms": [jsround(1000 / fps)] * n,
        "eventos": eventos or [],
    }
    if getattr(fx.mod, "act", None):
        dados["atuacao"] = _act_timing(fx.mod)
    return Image.fromarray(img, "RGBA"), dados


def _act_timing(mod):
    try:
        from .atuacao import actTiming
        return actTiming(mod)
    except ImportError:
        return None


def gif(r, caminho, k=4, fundo=True):
    """Prévia animada em GIF (Pillow, sem ffmpeg)."""
    quadros = []
    for f in r.frames:
        a = f.color if fundo else f.transparente
        a = np.repeat(np.repeat(a, k, axis=0), k, axis=1)
        quadros.append(Image.fromarray(a, "RGBA").convert("RGB" if fundo else "RGBA"))
    quadros[0].save(caminho, save_all=True, append_images=quadros[1:], duration=jsround(1000 / r.fps), loop=0,
                    disposal=2)


def salvar_png(img: Image.Image, caminho):
    Path(caminho).parent.mkdir(parents=True, exist_ok=True)
    img.save(caminho)


def salvar_json(dados, caminho):
    Path(caminho).parent.mkdir(parents=True, exist_ok=True)
    Path(caminho).write_text(json.dumps(dados, ensure_ascii=False, indent=2), encoding="utf-8")
