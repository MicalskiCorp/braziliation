#!/usr/bin/env python3
"""Autômato Abandonado — catálogo de peças da máquina davinciana de Blumenau.

A criatura é um autômato de relojoaria no espírito dos desenhos de Leonardo:
armação aberta de madeira e metal, com o maquinismo à vista pelo vão do gradil
e engrenagem em toda junta.

Aqui mora só o DESENHO. O motor que desenha e acaba — primitivas, rampas,
sombra de contato, luz de borda, outline — está em
`Design/ArteFonte/Ferramentas/montagem_base.py`, compartilhado com os outros
personagens montados por peça.

Duas dimensões de variação, independentes:

- ARMAMENTO — o que muda a leitura de ameaça: lança, escudo-engrenagem, ou
  nada, no caso do que se remontou de sucata;
- LIGA — a cor do metal, que o jogo pode usar como grau de dificuldade: bronze
  é o comum, prata é o mais duro, ferro é o degradado. Só a rampa do metal muda;
  madeira, cobre e a brasa da lente ficam iguais, então a silhueta não muda com
  o grau e o jogador lê a dificuldade pela cor sem reaprender a forma.

O idle de 6 frames é o maquinismo girando: cada roda avança um período de
simetria por ciclo, rodas que engrenam giram em sentidos opostos, e a brasa da
lente respira. Sem bob — é máquina rígida.

Uso:
  py montagem.py enm_automato.spec.json
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "ArteFonte" / "Ferramentas"))
from montagem_base import *  # noqa: F403,E402  (primitivas e estado da tela)
from montagem_base import NFRAMES  # noqa: F401,E402


# ------------------------------------------------------------------- as peças
def armacao():
    """Gradil: duas longarinas de madeira e costelas de metal. Entre elas fica
    o vazio por onde se vê o maquinismo — a assinatura davinciana."""
    peca()
    # longarinas com cintura: abrem no ombro, apertam na cintura, abrem no quadril
    for y in range(30, 67):
        t = abs(y - 50) / 20.0
        recuo = round(3 * (1 - t))
        rect(42 + recuo, y, 45 + recuo, y, "madeira")
        rect(60 - recuo, y, 63 - recuo, y, "madeira")
    peca()
    for y in (31, 48, 64):                      # três costelas, não quatro
        rect(43, y, 62, y + 2, "metal_d")
        rebites(45, 60, y + 1, 5)
    peca()
    rect(38, 27, 68, 30, "madeira")             # travessa dos ombros
    rect(37, 28, 39, 33, "metal_d")             # cabeceira de trás
    rect(67, 28, 69, 33, "metal_d")             # cabeceira da frente
    rect(43, 66, 62, 70, "metal_d")             # bacia


def platina():
    """Platina: a chapa escura no fundo da caixa, atrás do trem de engrenagens.
    Sem ela o vazado das rodas mostra o cenário e o peito parece furado — com
    ela, o furo mostra o interior da máquina, que é o que se quer ver."""
    peca()
    rect(45, 33, 60, 63, "metal_d")
    for y in range(34, 63, 4):                  # nervuras da chapa
        rebites(46, 59, y, 6, "metal_d")


def trem_central():
    """O maquinismo no vão do gradil: roda grande engrenada numa média e numa
    pequena, ligadas por correia."""
    engrenagem(52, 40, 9, "cobre", dentes=16, giro=1)    # roda mestra
    engrenagem(56, 57, 5, "metal", fase=.4, giro=-1)     # secundária, engrena na mestra
    peca()
    line(52, 49, 56, 57, 1, "metal_d")          # correia entre as duas


def regulador():
    """Regulador de esferas: duas bolas em hastes que abrem com a rotação.
    Diz 'relojoaria' sem precisar de mais uma engrenagem."""
    peca()
    line(52, 19, 52, 26, 1, "metal_d")
    line(52, 20, 46, 24, 1, "metal_d")
    line(52, 20, 58, 24, 1, "metal_d")
    ellipse(45, 25, 2, 2, "metal")
    ellipse(59, 25, 2, 2, "metal")


def cabeca():
    """Crânio-gaiola: aros de metal vazados, lente montada no focinho."""
    peca()
    ellipse(52, 15, 8, 7, "metal_d")
    vazar(46, 10, 49, 13)
    vazar(46, 18, 49, 20)
    peca()
    ring(52, 15, 7, "metal", inner=.62)
    line(45, 15, 60, 15, 1, "metal")
    line(52, 8, 52, 22, 1, "metal_d")
    peca()
    rect(58, 11, 66, 20, "metal_d")
    rect(59, 12, 66, 19, "metal")
    rebites(59, 65, 21, 3)


def pescoco():
    peca()
    rect(50, 23, 56, 28, "metal_d")
    engrenagem(53, 25, 3, "cobre", fase=.1, giro=-1)


def ombro():
    engrenagem(65, 33, 4, "metal", fase=.15, giro=1)
    engrenagem(41, 33, 3, "metal", fase=.55, giro=-1)


def braco():
    """Braço articulado: haste de madeira entre juntas de engrenagem."""
    peca()
    line(66, 35, 72, 47, 4, "madeira")
    engrenagem(73, 49, 3, "metal", fase=.3, giro=-1)
    peca()
    line(72, 51, 69, 66, 4, "madeira")
    engrenagem(69, 68, 3, "metal", fase=.7, giro=1)
    peca()
    rect(66, 70, 72, 74, "metal_d")
    put(65, 72, "metal_d")
    put(73, 73, "metal_d")


def quadril():
    engrenagem(46, 69, 3, "metal", fase=.25, giro=-1)
    engrenagem(59, 69, 3, "metal", fase=.65, giro=1)


def perna_tras():
    peca()
    line(46, 71, 38, 80, 3, "madeira_d")
    engrenagem(38, 81, 3, "metal_d", fase=.4, giro=1)
    peca()
    line(38, 83, 42, 90, 3, "madeira_d")
    rect(33, 90, 46, 93, "metal_d")


def perna_frente():
    peca()
    line(58, 72, 54, 81, 4, "madeira")
    engrenagem(55, 82, 3, "metal", fase=.9, giro=-1)
    peca()
    line(56, 85, 60, 91, 4, "madeira")
    rect(52, 91, 70, 95, "metal_d")
    rebites(54, 68, 93, 4)


def lanca():
    """Variante lanceira: pique longo preso ao punho."""
    peca()
    line(75, 16, 63, 86, 3, "madeira")
    peca()
    line(76, 9, 74, 20, 3, "metal")
    put(75, 7, "metal")
    line(73, 21, 78, 21, 1, "cobre")
    line(66, 62, 71, 62, 1, "cobre")


def escudo():
    """Variante escudeira: engrenagem gigante presa ao antebraço."""
    engrenagem(75, 56, 15, "metal_d", dentes=18, fase=.1, giro=1)
    peca()
    ring(75, 56, 10, "metal", inner=.55)
    ring(75, 56, 5, "metal_d", inner=.30)
    peca()
    ellipse(75, 56, 2, 2, "cobre")


def sucata_remendos():
    """Variante sucata: tábua amarrada na costela e roda torta de reposição."""
    peca()
    rect(37, 46, 42, 60, "madeira_d")
    line(36, 49, 43, 49, 1, "metal_d")
    line(36, 57, 43, 57, 1, "metal_d")
    engrenagem(36, 67, 5, "metal_d", fase=.35, giro=-1)
    peca()
    line(39, 62, 37, 67, 1, "metal_d")


def lente():
    """Único ponto quente do sprite, cercado de preto para queimar a 1x."""
    for y in range(13, 19):
        for x in range(60, 67):
            if material(x, y) is not None:
                pintar(x, y, "1")
    # a brasa respira com o ciclo: dois frames mais acesa, os outros em brasa baixa
    aceso = FRAME[0] % NFRAMES in (1, 2)
    for x in range(62, 66):
        pintar(x, 15, "G")
        pintar(x, 16, "G")
    pintar(65, 15, "D" if aceso else "9")
    pintar(64, 16, "9" if aceso else "1")
    if aceso:
        pintar(64, 14, "9")


ORDEM = [
    ("perna_tras", perna_tras), ("armacao", armacao), ("platina", platina), ("trem_central", trem_central),
    ("sucata_remendos", sucata_remendos), ("escudo", escudo), ("quadril", quadril),
    ("pescoco", pescoco), ("regulador", regulador), ("cabeca", cabeca), ("ombro", ombro),
    ("braco", braco), ("lanca", lanca), ("perna_frente", perna_frente),
]

CORPO = {"perna_tras", "armacao", "platina", "trem_central", "quadril", "pescoco",
         "regulador", "cabeca", "ombro", "braco", "perna_frente"}

ESTATICOS = {
    "lanca":       (CORPO | {"lanca"}, "bronze"),
    "escudo":      (CORPO | {"escudo"}, "bronze"),
    "sucata":      ((CORPO | {"sucata_remendos"}) - {"regulador"}, "ferro"),
    "lanca_prata": (CORPO | {"lanca"}, "prata"),
}

# O idle anima o lanceiro bronze: as rodas giram, a brasa respira. O corpo não
# se desloca — é uma máquina rígida, e o que dá vida é o maquinismo, não um bob.
ANIMA = (CORPO | {"lanca"}, "bronze")




if __name__ == "__main__":
    ids_idle = ["idle"] + [f"f{i}" for i in range(2, NFRAMES + 1)]
    outputs = [{"id": ids_idle[i], "rows": montar(ORDEM, ANIMA[0], ANIMA[1], i, acabamento=lente)}
               for i in range(NFRAMES)]
    outputs += [{"id": nome, "rows": montar(ORDEM, partes, liga, acabamento=lente)}
                for nome, (partes, liga) in ESTATICOS.items()]
    destino = sys.argv[1] if len(sys.argv) > 1 else "enm_automato.spec.json"
    emitir_spec(destino, "enm_automato", outputs, sheets={"idle": ids_idle})
