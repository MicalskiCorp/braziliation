#!/usr/bin/env python3
"""Soldado Mercenário Clérico — catálogo de peças, 96x96 lateral.

Brief (Blumenau/index.md, secção Monstros): "humano com armadura clockpunk
completa, servo do alto clero. Usa armas pneumáticas e escudos de engrenagem
giratória."

Direção: NÃO é cavaleiro medieval. É um colono alemão do Vale do Itajaí em
**armadura improvisada de sucata doméstica**, no fim do século XIX — o que um
blumenauense teria à mão quando o alto clero o armou. Referência de leitura:
os cavaleiros de Ghosts'n Goblins e Castlevania, onde a silhueta carrega o
personagem; referência de época e lugar: a Prússia vitoriana e a cozinha de
enxaimel.

O que o separa do Autômato Abandonado, que é o irmão de linha de montagem:

| | Autômato | Soldado |
|---|---|---|
| dominante | latão, claro | **sobretudo escuro**, pano |
| silhueta | gradil aberto, redondo | **Pickelhaube e saia de sobretudo** |
| material | máquina fundida | **sucata de casa amarrada com couro** |
| acento | brasa vermelha | **esmalte claro** e um pouco de cobre de cervejaria |

A sucata é literal e doméstica, e é ela que ancora o personagem em Blumenau:

- porta de fogão a lenha no peito, com dobradiça e trinco à vista;
- tampa de panela como ombreira, com a asa ainda no lugar;
- pedaço de cano de chaminé como braçadeira;
- panela pequena como joelheira;
- caneca de ágata esmaltada pendurada no cinto.

Variação em dois eixos, como no autômato:
- ARMAMENTO: fuzil pneumático, ou escudo de tampa de tacho com engrenagem
  soldada — o "escudo de engrenagem giratória" do brief, feito de sucata;
- LIGA: ferro é a tropa (sucata crua), bronze é quem conseguiu chapa de
  cervejaria. Só a rampa do metal muda.

Uso:
  py montagem.py enm_soldado_clerico.spec.json
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "ArteFonte" / "Ferramentas"))
from montagem_base import *  # noqa: F403,E402  (primitivas e estado da tela)
from montagem_base import registrar_material  # noqa: E402

# Sobretudo: azul-petróleo escuro, o uniforme vitoriano. É o que domina a área
# e o que mais separa este sprite do latão do autômato.
registrar_material("sobretudo", ["1", "1", "2", "3"])
# Esmalte de ágata: o branco-azulado da louça de cozinha alemã. Único claro.
registrar_material("esmalte", ["2", "4", "5", "D"])
registrar_material("couro", ["1", "A", "B", "D"])
# Fuligem: ferro que viveu dentro de um fogão.
registrar_material("fuligem", ["1", "1", "2", "3"])
registrar_material("clero", ["1", "G", "9", "C"])


# ------------------------------------------------------------------- as peças
def perna_tras():
    peca()
    line(50, 68, 43, 80, 5, "sobretudo")
    rect(39, 80, 48, 93, "couro")                 # bota de cano alto
    rect(37, 90, 50, 94, "fuligem")


def sobretudo():
    """Sobretudo militar: gola alta, peito duplo e saia que abre abaixo do
    cinto. A saia é a silhueta — é ela que diz 'uniforme', não 'armadura'."""
    peca()
    rect(47, 28, 63, 60, "sobretudo")
    peca()
    BARRA = [78, 84, 80, 86, 82, 88, 85, 87, 84, 86, 82, 85, 80, 83, 78, 81, 76, 79]
    for i, fim in enumerate(BARRA):               # saia com barra irregular
        x = 40 + i
        rect(x, 58, x, fim, "sobretudo")
    peca()
    rect(48, 24, 62, 29, "sobretudo")             # gola alta
    rect(48, 24, 62, 25, "couro")
    peca()
    for y in range(32, 56, 5):                    # duas fileiras de botões
        put(52, y, "cobre")
        put(60, y, "cobre")
    line(56, 30, 56, 58, 1, "fuligem")            # vinco do peito duplo


def cinto():
    peca()
    rect(42, 56, 66, 61, "couro")
    rect(53, 56, 58, 61, "fuligem")               # fivela
    peca()
    ellipse(44, 66, 3, 4, "esmalte")              # caneca de ágata pendurada
    rect(43, 62, 45, 64, "fuligem")
    put(47, 65, "esmalte")                        # asa


def peitoral_sucata():
    """Porta de fogão a lenha amarrada no peito: dobradiça de um lado, trinco
    do outro, e a fuligem que nunca sai."""
    peca()
    rect(48, 33, 64, 50, "fuligem")
    peca()
    rect(49, 34, 63, 49, "metal")
    rect(51, 37, 61, 46, "fuligem")               # a boca da porta, encardida
    rect(53, 39, 59, 44, "esmalte")               # chapa de esmalte rebitada por dentro
    rebites(51, 61, 36, 3, "metal_d")
    peca()
    rect(47, 35, 49, 38, "metal_d")               # dobradiça
    rect(47, 45, 49, 48, "metal_d")
    rect(63, 40, 66, 43, "cobre")                 # trinco
    peca()
    line(46, 32, 66, 36, 2, "couro")              # correias em cruz
    line(46, 51, 66, 47, 2, "couro")


def ombreira_tampa():
    """Tampa de panela como ombreira — a asa continua no lugar dela."""
    peca()
    ellipse(66, 34, 8, 5, "esmalte")
    ring(66, 34, 6, "metal_d", inner=.70)         # friso da tampa
    put(63, 33, "clero")                          # lasca onde o esmalte saltou
    peca()
    rect(64, 27, 68, 29, "metal_d")               # asa
    put(63, 28, "metal_d")
    put(69, 28, "metal_d")
    peca()
    ellipse(43, 34, 6, 4, "fuligem")              # ombro de trás, chapa simples


def braco():
    peca()
    line(66, 38, 71, 50, 5, "sobretudo")
    peca()
    rect(68, 50, 75, 58, "metal_d")               # cano de chaminé como braçadeira
    ring(71, 54, 4, "metal", inner=.72)
    peca()
    line(69, 58, 66, 66, 4, "sobretudo")
    rect(62, 65, 70, 70, "couro")                 # luva


def cabeca():
    """Pickelhaube: o capacete prussiano. É o que data o personagem no século
    XIX e o que mais afasta a silhueta de um elmo medieval."""
    peca()
    ellipse(53, 17, 9, 7, "metal")
    rect(45, 17, 62, 21, "metal")
    peca()
    rect(52, 6, 54, 12, "metal_d")                # a espigão
    ellipse(53, 5, 2, 2, "metal_d")
    rect(50, 11, 56, 13, "metal_d")               # base do espigão
    peca()
    rect(58, 19, 67, 23, "metal_d")               # pala da frente
    rect(42, 19, 48, 24, "metal_d")               # proteção de nuca
    peca()
    ellipse(54, 14, 5, 2, "cobre")                # placa frontal, latão de brasão
    peca()
    rect(56, 23, 64, 28, "fuligem")               # o rosto não se vê: só sombra
    line(57, 26, 63, 26, 1, "couro")              # jugular


def faixa_clero():
    """Braçadeira do clero. Pequena de propósito: o tabardo grande competia com
    a silhueta e sumia atrás da sucata."""
    peca()
    rect(67, 40, 72, 46, "clero")
    put(66, 41, "clero")
    put(73, 45, "clero")


def joelheira():
    peca()
    ellipse(56, 76, 5, 4, "esmalte")              # panela pequena como joelheira
    ring(56, 76, 3, "metal", inner=.60)


def perna_frente():
    peca()
    line(58, 66, 54, 78, 6, "sobretudo")
    peca()
    rect(52, 80, 62, 93, "couro")                 # bota de cano alto
    rect(50, 90, 68, 94, "fuligem")
    rebites(53, 61, 84, 4, "metal_d")             # fivelas da bota


def fuzil():
    """Fuzil pneumático: coronha de madeira, câmara de ar de cobre de
    cervejaria, baioneta curta. A mangueira desce do tanque das costas."""
    peca()
    line(62, 60, 88, 50, 3, "metal_d")            # cano
    peca()
    ellipse(72, 59, 6, 3, "cobre")                # câmara de ar
    rebites(68, 76, 59, 4, "metal_d")
    peca()
    rect(58, 62, 66, 66, "madeira")               # coronha
    line(86, 48, 92, 45, 2, "metal")              # baioneta
    put(93, 44, "metal")


def tanque():
    """Tanque de ar nas costas, de barril de cervejaria: aros e tudo."""
    peca()
    ellipse(39, 44, 7, 12, "metal_d")
    for y in (36, 44, 52):
        rect(32, y, 46, y + 1, "cobre")           # aros do barril
    peca()
    line(45, 38, 52, 34, 2, "fuligem")            # mangueira
    line(52, 34, 60, 42, 2, "fuligem")
    engrenagem(39, 31, 3, "metal", fase=.2)       # válvula


def escudo():
    """Tampa de tacho de cervejaria com uma engrenagem soldada no meio: o
    'escudo de engrenagem giratória' do brief, construído de sucata."""
    peca()
    ellipse(74, 54, 14, 15, "metal_d")
    peca()
    ellipse(74, 54, 12, 13, "metal")
    ring(74, 54, 9, "metal_d", inner=.80)         # friso do tacho
    peca()
    engrenagem(74, 54, 6, "cobre", dentes=12, fase=.3)
    peca()
    rect(72, 39, 76, 41, "metal_d")               # asa do tacho, ainda presa


def maca():
    """Martelo de ferreiro — a arma de quem não tinha arma."""
    peca()
    line(62, 66, 66, 82, 3, "madeira")
    peca()
    rect(62, 84, 71, 90, "fuligem")
    rect(63, 85, 70, 89, "metal_d")


def olhar():
    """A fresta sob a pala: dois pixels frios no vazio do rosto."""
    for x in range(57, 65):
        for y in (24, 25):
            if material(x, y) is not None:
                pintar(x, y, "1")
    pintar(62, 24, "5")
    pintar(63, 24, "D")
    pintar(62, 25, "4")


ORDEM = [
    ("tanque", tanque), ("perna_tras", perna_tras), ("escudo", escudo),
    ("sobretudo", sobretudo), ("peitoral_sucata", peitoral_sucata), ("cinto", cinto),
    ("cabeca", cabeca), ("ombreira_tampa", ombreira_tampa), ("faixa_clero", faixa_clero),
    ("braco", braco), ("maca", maca), ("fuzil", fuzil),
    ("joelheira", joelheira), ("perna_frente", perna_frente),
]

CORPO = {"perna_tras", "sobretudo", "peitoral_sucata", "cinto", "cabeca",
         "ombreira_tampa", "faixa_clero", "braco", "joelheira", "perna_frente"}

VARIANTES = {
    "idle":   (CORPO | {"tanque", "fuzil"}, "ferro"),
    "escudo": (CORPO | {"escudo", "maca"}, "ferro"),
    "guarda": (CORPO | {"tanque", "fuzil"}, "bronze"),
}


if __name__ == "__main__":
    outputs = [{"id": nome, "rows": montar(ORDEM, partes, liga, acabamento=olhar)}
               for nome, (partes, liga) in VARIANTES.items()]
    destino = sys.argv[1] if len(sys.argv) > 1 else "enm_soldado_clerico.spec.json"
    emitir_spec(destino, "enm_soldado_clerico", outputs)
