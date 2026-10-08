#!/usr/bin/env python3
"""Soldado Mercenário Clérico — catálogo de peças, 96x96 lateral.

Brief (Blumenau/index.md, secção Monstros): "humano com armadura clockpunk
completa, servo do alto clero. Usa armas pneumáticas e escudos de engrenagem
giratória."

É o segundo asset montado pela linha de montagem, e serve de teste dela: o
autômato é uma máquina de gradil aberto, este é um HOMEM DENTRO DE ARMADURA.
O que muda no desenho:

- a superfície é fechada, não vazada: peitoral sólido, e o olhar não atravessa;
- a proporção é humana — cabeça pequena, ombreiras largas, perna comprida;
- engrenagem é acessório de junta e de arma, não o corpo. Três ou quatro, não
  uma dezena: ele usa a máquina, o autômato é a máquina;
- entra tecido, que o autômato não tinha: o tabardo do clero, em carmim
  desbotado, é o que separa este inimigo de qualquer soldado genérico.

O que NÃO mudou e é o ponto do teste: nenhuma primitiva, nenhum passe de
acabamento, nenhuma rampa de metal. Só o catálogo.

Variação em dois eixos, como no autômato:
- ARMAMENTO: fuzil pneumático (com tanque nas costas e mangueira) ou escudo de
  engrenagem giratória com maça curta;
- LIGA: bronze é a tropa, prata é a guarda do alto clero.

Uso:
  py montagem.py enm_soldado_clerico.spec.json
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "ArteFonte" / "Ferramentas"))
from montagem_base import *  # noqa: F403,E402  (primitivas e estado da tela)
from montagem_base import registrar_material  # noqa: E402

# Carmim desbotado do clero: a única cor quente fora do metal. Vai do vermelho
# de alerta ao ocre, então lê como tecido velho e não como sangue fresco.
registrar_material("clero", ["1", "G", "9", "C"])
registrar_material("couro", ["1", "A", "B", "C"])


# ------------------------------------------------------------------- as peças
def tanque():
    """Tanque pneumático nas costas, com a mangueira que alimenta o fuzil."""
    peca()
    ellipse(37, 44, 7, 13, "metal_d")
    rect(34, 32, 42, 36, "metal_d")              # cinta de topo
    rebites(35, 41, 34, 3)
    peca()
    line(43, 38, 50, 34, 2, "metal_d")           # mangueira subindo ao ombro
    line(50, 34, 58, 40, 2, "metal_d")
    engrenagem(37, 31, 3, "metal", fase=.2)      # válvula


def perna_tras():
    peca()
    line(50, 62, 43, 76, 4, "metal_d")
    line(43, 76, 46, 87, 4, "metal_d")
    rect(40, 86, 54, 92, "metal_d")              # bota traseira


def tabardo():
    """Tabardo do clero: a peça que diz de quem ele é servo. Barra irregular,
    gasta embaixo — o carmim escurece na bainha."""
    peca()
    BARRA = [68, 74, 70, 78, 72, 80, 76, 81, 78, 80, 75, 79, 73, 77, 71, 74]
    for i, fim in enumerate(BARRA):
        x = 46 + i
        rect(x, 57, x, fim, "clero")
    peca()
    for i, fim in enumerate(BARRA):               # bainha encardida
        x = 46 + i
        for y in range(max(57, fim - 4), fim + 1):
            if material(x, y) == "clero":
                pintar(x, y, "1" if y > fim - 2 or (x + y) % 3 == 0 else "G")


def couraca():
    """Peitoral fechado, com placas sobrepostas e fivelas."""
    peca()
    rect(46, 28, 64, 60, "metal")
    ellipse(55, 42, 10, 16, "metal")
    peca()
    for y in (33, 41, 49):                        # placas que se sobrepõem
        rect(46, y, 64, y + 1, "metal_d")
        rebites(48, 62, y, 5)
    peca()
    rect(45, 56, 65, 60, "couro")                 # cinturão
    rect(52, 56, 56, 60, "metal")                 # fivela
    peca()
    engrenagem(60, 37, 4, "cobre", fase=.5)       # manômetro de pressão no peito


def gola():
    peca()
    rect(49, 24, 61, 29, "metal_d")
    rebites(50, 60, 26, 4)


def elmo():
    """Elmo fechado de fresta horizontal, com crista — o aceno ao clero."""
    peca()
    ellipse(54, 18, 8, 7, "metal")
    rect(54, 15, 64, 22, "metal")                 # viseira projetada
    peca()
    rect(45, 7, 56, 11, "metal_d")                # crista
    line(47, 5, 54, 5, 2, "metal_d")
    peca()
    rect(56, 16, 65, 19, "metal_d")               # fresta
    for x in range(57, 65, 3):
        rect(x, 16, x, 19, "metal")               # barras da fresta
    rebites(56, 64, 21, 3)


def ombreira():
    """Ombreiras grandes e ornamentais — o volume vitoriano do conjunto."""
    peca()
    ellipse(66, 32, 8, 6, "metal")
    rebites(61, 71, 31, 4)
    peca()
    ellipse(44, 32, 6, 5, "metal_d")
    engrenagem(68, 36, 3, "metal_d", fase=.3)     # junta do ombro


def braco():
    peca()
    line(66, 37, 71, 48, 4, "metal")
    engrenagem(72, 50, 3, "metal_d", fase=.6)     # cotovelo
    peca()
    line(70, 52, 66, 60, 4, "metal")
    rect(62, 59, 70, 63, "couro")                 # manopla


def fuzil():
    """Fuzil pneumático: cano longo, câmara de ar sob ele, coronha de madeira."""
    peca()
    line(60, 56, 88, 46, 3, "metal_d")            # cano
    peca()
    ellipse(70, 56, 6, 3, "metal")                # câmara de ar
    rebites(66, 74, 56, 4)
    peca()
    rect(55, 58, 64, 62, "madeira")               # coronha
    line(63, 54, 67, 54, 1, "cobre")              # registro
    line(86, 44, 90, 43, 2, "metal")              # boca


def escudo():
    """Escudo de engrenagem giratória, preso ao antebraço."""
    engrenagem(74, 52, 14, "metal_d", dentes=18, fase=.1)
    peca()
    ring(74, 52, 9, "metal", inner=.55)
    peca()
    ellipse(74, 52, 4, 4, "cobre")
    peca()
    ring(74, 52, 2, "metal_d", inner=.1)


def maca():
    """Maça curta na mão livre, para a variante de escudo."""
    peca()
    line(60, 62, 64, 78, 3, "madeira")
    peca()
    ellipse(65, 81, 4, 4, "metal_d")
    rebites(62, 68, 81, 3)


def perna_frente():
    peca()
    line(57, 60, 53, 76, 5, "metal")
    engrenagem(55, 77, 3, "metal_d", fase=.8)     # joelheira
    peca()
    line(55, 80, 59, 89, 5, "metal")
    rect(52, 88, 72, 94, "metal_d")               # bota dianteira
    rebites(55, 69, 90, 4)


def visor():
    """A luz fria da fresta: o homem lá dentro não se vê, só o reflexo."""
    for x in range(58, 65):
        if material(x, 17) is not None:
            pintar(x, 17, "1")
        if material(x, 18) is not None:
            pintar(x, 18, "1")
    pintar(62, 17, "5")
    pintar(63, 17, "D")
    pintar(63, 18, "5")


ORDEM = [
    ("tanque", tanque), ("perna_tras", perna_tras),
    ("couraca", couraca), ("tabardo", tabardo), ("gola", gola),
    ("elmo", elmo), ("ombreira", ombreira),
    ("escudo", escudo), ("braco", braco), ("maca", maca), ("fuzil", fuzil),
    ("perna_frente", perna_frente),
]

CORPO = {"perna_tras", "tabardo", "couraca", "gola", "elmo", "ombreira",
         "braco", "perna_frente"}

VARIANTES = {
    "idle":        (CORPO | {"tanque", "fuzil"}, "bronze"),
    "escudo":      (CORPO | {"escudo", "maca"}, "bronze"),
    "guarda":      (CORPO | {"tanque", "fuzil"}, "prata"),
}


if __name__ == "__main__":
    outputs = [{"id": nome, "rows": montar(ORDEM, partes, liga, acabamento=visor)}
               for nome, (partes, liga) in VARIANTES.items()]
    destino = sys.argv[1] if len(sys.argv) > 1 else "enm_soldado_clerico.spec.json"
    emitir_spec(destino, "enm_soldado_clerico", outputs)
