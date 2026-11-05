"""Pele: o personagem desenhado UMA vez, levado para qualquer pose.

A técnica é a do PixelFX (`act.js`, MIT) para gelo e veneno no corpo em movimento — cada pixel
de uma pose sabe de qual pixel da pose de descanso veio (o `src` do raster) — aplicada ao
personagem inteiro, como o lookup de UV do aarthificial/Astortion.

Fluxo:
1. `py -m pxfx.esqueleto.animar <rig.json> --referencia` renderiza a pose de descanso no
   manequim e o mapa de partes. É o GABARITO: a pele é pintada por cima dele (pixel pass no
   Aseprite, ou concept aprovado reduzido à paleta), mesmo tamanho, mesma origem.
2. Cada quadro de animação busca a cor na pele pelo `src`.
3. A luz é refeita SEM sair da paleta: se a cor da pele pertence a uma rampa de `rampas`
   (aceso → escuro), ela anda tantos degraus quanto o tom da pose difere do tom do descanso
   naquele pixel. Cor fora de rampa (olho, emblema, detalhe) não muda: é detalhe fixo.
4. Buraco (o pixel de origem estava escondido no descanso, ou a pele está vazia ali) usa o
   pixel de pele mais próximo dentro de 7 × escala — o mesmo raio do original.
"""
from __future__ import annotations

import math

import numpy as np
from PIL import Image

from ..cor import hex


def carregar_pele(caminho):
    img = np.asarray(Image.open(caminho).convert("RGBA"), dtype=np.uint8)
    return img


def _cor_rgba(px):
    r, g, b, a = (int(v) for v in px)
    return 0 if a < 128 else (0xFF000000 | (b << 16) | (g << 8) | r)


class Pele:
    def __init__(self, imagem, origem, rampas, descanso, k=1.0, tinta="#1b1616"):
        """imagem: RGBA (h, w, 4); origem: (x, y) dos pés na imagem; rampas: {nome: [4+ hex, aceso→escuro]};
        descanso: a saída de desenhar() da pose de descanso (para o tom de cada pixel de origem)."""
        self.img = imagem
        self.ox, self.oy = origem
        self.k = k
        self.rampas = [[hex(c) for c in cs] for cs in rampas.values()]
        self.indice = {}
        for ri, ramp in enumerate(self.rampas):
            for ti, c in enumerate(ramp):
                self.indice.setdefault(c, (ri, ti))
        self.tinta = hex(tinta)
        self.tom_descanso = {(x, y): t for x, y, t, parte in zip(descanso["xs"], descanso["ys"], descanso["tom"],
                                                                   descanso["parte"]) if parte}
        # a peça que o gabarito mostra em cada pixel: a busca só aceita origem da MESMA peça
        self.parte_descanso = {(x, y): parte for x, y, parte in zip(descanso["xs"], descanso["ys"], descanso["parte"])
                               if parte}
        h, w = imagem.shape[:2]
        self._cheio = {}
        for y in range(h):
            for x in range(w):
                c = _cor_rgba(imagem[y, x])
                if c:
                    self._cheio[(x - self.ox, y - self.oy)] = c
        self._perto = {}

    def _mais_perto(self, sx, sy, parte=0):
        chave = (sx, sy, parte)
        if chave in self._perto:
            return self._perto[chave]
        raio = math.ceil(7 * self.k)
        melhor, bd = None, 1e9
        for dy in range(-raio, raio + 1):
            for dx in range(-raio, raio + 1):
                d = dx * dx + dy * dy
                q = (sx + dx, sy + dy)
                if d < bd and q in self._cheio and (not parte or self.parte_descanso.get(q) == parte):
                    bd, melhor = d, q
        self._perto[chave] = melhor
        return melhor

    def cor(self, src, tom_pose, parte=0):
        """A cor da pele para um pixel cuja origem é src, com o tom que a pose dá a ele. Com `parte`, a origem
        precisa ser da mesma peça no gabarito — senão o topo da coxa puxaria o cinto que cobre a coxa no descanso."""
        if src is None:
            return None
        ok = src in self._cheio and (not parte or self.parte_descanso.get(src) == parte)
        alvo = src if ok else self._mais_perto(src[0], src[1], parte)
        if alvo is None:
            return None
        c = self._cheio[alvo]
        if c & 0xFFFFFF == 0x140C0E:  # a tinta do manequim que ficou no gabarito vira a tinta do personagem
            return self.tinta
        onde = self.indice.get(c)
        if onde is None:
            return c  # detalhe fixo: não re-ilumina
        ri, ti = onde
        t_desc = self.tom_descanso.get(alvo)
        if t_desc is None:
            return c
        ramp = self.rampas[ri]
        return ramp[max(0, min(len(ramp) - 1, ti + (tom_pose - t_desc)))]

    def aplicar(self, saida):
        """Troca as cores do manequim pelas da pele, pixel a pixel, sem sair da paleta: tinta vira a tinta do
        personagem, costura e contorno do lado da luz viram o degrau mais escuro da rampa daquela pele."""
        cores = list(saida["color"])
        for i, (src, tom, parte) in enumerate(zip(saida["src"], saida["tom"], saida["parte"])):
            if saida["ink"][i]:
                cores[i] = self.tinta
                continue
            escuro = (not parte) or saida["costura"][i]
            c = self.cor(src, 3 if escuro else tom, parte or saida["viz"][i])
            if c and escuro:
                onde = self.indice.get(c)
                if onde:
                    c = self.rampas[onde[0]][-1]
            if c:
                cores[i] = c
        novo = dict(saida)
        novo["color"] = cores
        return novo
