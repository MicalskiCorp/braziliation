#!/usr/bin/env python3
"""Gerador procedural de tilesets — desenha em 16x16 e entrega 48x48 (Opção B do pipeline programático, ADR-011).

Gera famílias de tiles parametrizadas pela paleta JSON da região, com seed
determinística (mesma seed + paleta = mesmo tileset, sempre). Saída: PNG em
grade (linhas = tipos de tile, colunas = variações) + manifest JSON com
seed/paleta/tipos, satisfazendo o registro exigido pelo pipeline.

Famílias disponíveis:
  enxaimel          — parede Fachwerk: reboco claro + vigas de madeira + marca de umidade
  metal             — chapas de ferro clockpunk: bisel, rebites, ferrugem, emendas
  agua              — superfície d'água, lama e parede com marca de nível de enchente
  pedra_portuguesa  — túnel séc. XVIII: cantaria, abóbada, piso pé-de-moleque, variante com musgo
  cemiterio         — chão de cemitério: terra batida, mato ralo, cascalho, cova revolvida
  marmore           — mausoléu: placa polida, bloco veado, cimalha, variante lascada
  periferia         — bairro pós-enchente: tábua encharcada, zinco, reboco com lama, entulho

Uso:
  python gen_tileset.py enxaimel --palette ../../ArteConceitual/Paletas/blumenau.json --seed 42 -o out.png

Dependência: pip install pillow
"""
import argparse
import json
import random
from pathlib import Path

from PIL import Image

from spec_redetail import add_noise, epx, scale3x

TILE = 16


def hex_to_rgba(h: str) -> tuple:
    h = h.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), 255)


def load_palette(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    return {c["key"]: hex_to_rgba(c["hex"]) for c in data["colors"]}


def blank(fill: str) -> list:
    return [[fill] * TILE for _ in range(TILE)]


def speckle(grid: list, rng: random.Random, color: str, density: float, y0: int = 0, y1: int = TILE) -> None:
    for y in range(y0, y1):
        for x in range(TILE):
            if rng.random() < density:
                grid[y][x] = color


def blob(grid: list, rng: random.Random, color: str, cx: int, cy: int, size: int) -> None:
    for _ in range(size):
        x = min(TILE - 1, max(0, cx + rng.randint(-2, 2)))
        y = min(TILE - 1, max(0, cy + rng.randint(-1, 1)))
        grid[y][x] = color


# ---------------------------------------------------------------- enxaimel

def enxaimel_panel(rng: random.Random) -> list:
    g = blank("D")
    speckle(g, rng, "C", 0.08)
    if rng.random() < 0.5:
        blob(g, rng, "E", rng.randint(3, 12), rng.randint(12, 15), rng.randint(3, 7))
    return g


def enxaimel_beam_v(rng: random.Random) -> list:
    g = enxaimel_panel(rng)
    for y in range(TILE):
        g[y][0] = "A"
        g[y][1] = "B"
        g[y][2] = "A" if rng.random() < 0.2 else "B"
        g[y][3] = "1"
    return g


def enxaimel_beam_h(rng: random.Random) -> list:
    g = enxaimel_panel(rng)
    for x in range(TILE):
        g[0][x] = "A"
        g[1][x] = "B"
        g[2][x] = "B" if rng.random() < 0.8 else "C"
        g[3][x] = "1"
    return g


def enxaimel_diag(rng: random.Random) -> list:
    g = enxaimel_panel(rng)
    for i in range(TILE):
        g[i][i] = "B"
        if i + 1 < TILE:
            g[i][i + 1] = "B"
            g[i + 1][i] = "A"
    return g


# ------------------------------------------------------------------- metal

def metal_plate(rng: random.Random) -> list:
    g = blank("3")
    for i in range(TILE):
        g[0][i] = "4"
        g[i][0] = "4"
        g[TILE - 1][i] = "1"
        g[i][TILE - 1] = "1"
    for cx, cy in ((2, 2), (13, 2), (2, 13), (13, 13)):
        g[cy][cx] = "5"
        g[cy + 1 if cy < 13 else cy][cx] = "2" if cy < 13 else g[cy][cx]
    speckle(g, rng, "2", 0.05, 1, TILE - 1)
    return g


def metal_rusty(rng: random.Random) -> list:
    g = metal_plate(rng)
    for _ in range(rng.randint(2, 4)):
        blob(g, rng, "9", rng.randint(2, 13), rng.randint(2, 13), rng.randint(4, 9))
    speckle(g, rng, "6", 0.04, 2, TILE - 2)
    return g


def metal_seams(rng: random.Random) -> list:
    g = blank("3")
    ys = sorted(rng.sample(range(2, TILE - 2), 2))
    for x in range(TILE):
        g[0][x] = "4"
        g[TILE - 1][x] = "1"
        for y in ys:
            g[y][x] = "2"
            g[y - 1][x] = "4" if rng.random() < 0.7 else "3"
    speckle(g, rng, "2", 0.05, 1, TILE - 1)
    return g


# -------------------------------------------------------------------- agua

def agua_superficie(rng: random.Random) -> list:
    g = blank("E")
    for band in range(3):
        y = 2 + band * 5 + rng.randint(0, 2)
        x0 = rng.randint(0, 6)
        for x in range(x0, min(TILE, x0 + rng.randint(5, 10))):
            g[y][x] = "2"
            if rng.random() < 0.3 and y > 0:
                g[y - 1][x] = "F"
    speckle(g, rng, "2", 0.04)
    return g


def agua_lama(rng: random.Random) -> list:
    g = blank("B")
    speckle(g, rng, "A", 0.15)
    speckle(g, rng, "F", 0.06)
    for _ in range(rng.randint(1, 3)):
        blob(g, rng, "E", rng.randint(2, 13), rng.randint(2, 13), rng.randint(3, 6))
    return g


def agua_marca_nivel(rng: random.Random) -> list:
    g = blank("D")
    speckle(g, rng, "C", 0.08)
    nivel = rng.randint(5, 8)
    for x in range(TILE):
        g[nivel][x] = "F" if rng.random() < 0.4 else "E"
        for y in range(nivel + 1, TILE):
            g[y][x] = "E" if rng.random() < 0.25 or y == nivel + 1 else ("B" if y > 11 else "C")
    return g


# ------------------------------------------------- pedra portuguesa (túnel)
# O Unterwasser-Gang e as passagens do século XVIII: cantaria assentada em
# argamassa de cal, anterior a tudo que é clockpunk em cima. A leitura tem de
# ser FRIA e PESADA — pedra em 2/3/4/5, argamassa em C/D, e nada de latão.


def pedra_silhar(rng: random.Random) -> list:
    """Cantaria em 2 fiadas de 8px com junta vertical em posição irregular — o
    bloco tem de ler como PEDRA talhada, não como tijolo (a iteração 1, com
    bloco 8x4, leu como tijolo). Argamassa de cal em ocre, com o bege só de
    vez em quando: junta clara demais vira o elemento dominante da parede.
    Luz de cima e da esquerda: topo do bloco de baixo aceso, pé do bloco de
    cima na sombra, face direita de cada bloco escurecida."""
    g = blank("4")
    speckle(g, rng, "3", 0.07)
    speckle(g, rng, "5", 0.03)
    for fiada in range(2):
        y0 = fiada * 8
        for x in range(TILE):
            g[(y0 - 1) % TILE][x] = "2"          # sombra sob o bloco de cima
            g[y0][x] = "C" if rng.random() < 0.75 else "D"
            if rng.random() < 0.55:
                g[y0 + 1][x] = "5"               # aresta acesa do bloco de baixo
            if g[y0 + 6][x] == "4" and rng.random() < 0.35:
                g[y0 + 6][x] = "3"               # barriga do bloco: volume
        # 2 juntas longe da borda: o bloco que atravessa a emenda entre tiles
        # fica com largura variável (4 a 14px) e a parede não vira grade
        a = rng.randint(2, 6)
        b = a + rng.randint(6, 8)
        for bx in (a, b):
            for y in range(y0 + 1, y0 + 8):
                g[y][bx] = "C" if rng.random() < 0.75 else "D"
                g[y][bx - 1] = "2"
                if rng.random() < 0.5:
                    g[y][bx + 1] = "5"
    return g


def pedra_abobada(rng: random.Random) -> list:
    """Abóbada do túnel: aduelas de cantaria com a junta inclinando 1px a cada
    2 linhas, o leque do arco. É teto — pega menos luz, então a rampa desce
    um degrau (3 de base, 4 de luz). Sem preto: na iteração 1 a sombra em
    `1` fez o teto ler como ripado de madeira."""
    g = blank("3")
    speckle(g, rng, "4", 0.08)
    speckle(g, rng, "2", 0.05)
    for fiada in range(2):
        y0 = fiada * 8
        for x in range(TILE):
            g[(y0 - 1) % TILE][x] = "2"
            g[y0][x] = "C" if rng.random() < 0.5 else "2"
            if rng.random() < 0.45:
                g[y0 + 1][x] = "4"
        for base in (rng.randint(1, 5), rng.randint(9, 12)):
            for i, y in enumerate(range(y0 + 1, y0 + 8)):
                x = (base + i // 2) % TILE
                g[y][x] = "C" if rng.random() < 0.5 else "2"
                g[y][(x - 1) % TILE] = "2"
    return g


def pedra_piso(rng: random.Random) -> list:
    """Pé-de-moleque: o calçamento colonial português do Brasil (Paraty, Ouro
    Preto) — pedra arredondada de tamanho irregular, assentada justa. É o piso
    certo para um túnel do século XVIII; o mosaico de cubos da calçada
    portuguesa só chega ao Brasil no XIX.

    Histórico do tipo (4 iterações):
      1-2. mosaico de cubos 3px: o Scale3x arredondou cada cubo contra a junta
           e o piso leu como bolinha e depois como chapa de rebite;
      3.   pé-de-moleque de 3-5px: pedra de 2px de miolo virou losango, a pedra
           bege leu como moeda, e a pedra que cruzava a borda saía com um tom
           diferente em cada variação — costura visível entre tiles;
      4.   (esta) 3 fiadas FIXAS de 5/5/6px com desencontro fixo, e a pedra que
           cruza a borda do tile com largura e tom FIXOS. Assim qualquer
           variação encosta em qualquer outra sem emenda; o que varia é só o
           miolo de cada fiada. Pedra de 4px de miolo para cima: cabe luz no
           topo, corpo e sombra no pé, e o Scale3x arredonda em seixo."""
    g = blank("2")
    claro = {"4": "5", "3": "4", "5": "5", "C": "D"}
    escuro = {"4": "3", "3": "3", "5": "4", "C": "B"}

    def pedra(x0: int, y0: int, w: int, alt: int, tom: str) -> None:
        for y in range(y0, y0 + alt - 1):
            for dx in range(w - 1):
                g[y][(x0 + dx) % TILE] = tom
        for dx in range(1, w - 2):
            g[y0][(x0 + dx) % TILE] = claro[tom]               # topo aceso
            g[y0 + alt - 2][(x0 + dx + 1) % TILE] = escuro[tom]  # pé na sombra

    for y0, alt, desloc in ((0, 5, 0), (5, 5, 6), (10, 6, 3)):
        pedra(desloc - 5, y0, 5, alt, "4")       # a pedra da borda: igual em toda variação
        w1 = rng.randint(4, 7)                   # o miolo: 11px em duas pedras
        for x0, w in ((desloc, w1), (desloc + w1, 11 - w1)):
            r = rng.random()
            tom = "4" if r < 0.47 else ("3" if r < 0.73 else ("5" if r < 0.95 else "C"))  # ocre raro: túnel é frio
            pedra(x0, y0, w, alt, tom)
    return g


def pedra_musgo(rng: random.Random) -> list:
    """Variante úmida da cantaria: infiltração escorrendo pela face e musgo
    tomando a junta, que é onde a água fica parada."""
    g = pedra_silhar(rng)
    for _ in range(rng.randint(1, 3)):           # escorrido vertical
        x = rng.randrange(TILE)
        for y in range(TILE):
            if rng.random() < 0.75:
                g[y][x] = "2"
            if rng.random() < 0.25:
                g[y][(x + 1) % TILE] = "E"
    for y in range(TILE):                        # musgo encharca a argamassa
        for x in range(TILE):
            if g[y][x] in ("D", "C") and rng.random() < 0.45:
                g[y][x] = "E"
    return g


# ------------------------------------------------------- cemitério / terra
# Chão do Cemitério dos Gatos e do cemitério municipal: terra batida, mato
# ralo (não gramado), a trilha de cascalho das fotos de referência, e a cova
# fechada há pouco.


def cemiterio_terra(rng: random.Random) -> list:
    """Terra batida do caminho entre as covas — pisada, sem vegetação."""
    g = blank("B")
    speckle(g, rng, "A", 0.18)
    speckle(g, rng, "C", 0.10)
    speckle(g, rng, "1", 0.04)
    for _ in range(rng.randint(2, 4)):
        blob(g, rng, "A", rng.randint(2, 13), rng.randint(2, 13), rng.randint(4, 8))
    return g


def cemiterio_mato(rng: random.Random) -> list:
    """Mato ralo tomando a terra: tufos em leque (lâmina central alta e duas
    laterais abrindo), com ponta seca em F e sombra de contato no pé. Sem
    pontilhado verde solto — na iteração 1 ele fez o tile ler como camuflagem.
    Ralo de propósito: o cemitério está abandonado, mas não é gramado."""
    g = cemiterio_terra(rng)
    for _ in range(rng.randint(4, 7)):
        x = rng.randrange(TILE)
        y = rng.randrange(4, TILE - 1)
        for i in range(rng.randint(3, 4)):
            g[y - i][x] = "F" if i >= 2 else "E"
        g[y - 1][(x - 1) % TILE] = "E"
        g[y - 2][(x - 2) % TILE] = "F"
        g[y - 1][(x + 1) % TILE] = "E"
        g[y - 2][(x + 2) % TILE] = "E"
        g[y + 1][x] = "A"                        # sombra de contato
    return g


def cemiterio_cascalho(rng: random.Random) -> list:
    """Trilha de cascalho — a das fotos do Cemitério dos Gatos: pedra miúda
    clara sobre terra escura, com sombra de contato por baixo de cada caco."""
    g = blank("A")
    speckle(g, rng, "B", 0.25)
    for _ in range(26):
        x = rng.randrange(TILE)
        y = rng.randrange(TILE)
        tom = "5" if rng.random() < 0.35 else ("D" if rng.random() < 0.5 else "C")
        g[y][x] = tom
        if rng.random() < 0.5:
            g[y][(x + 1) % TILE] = tom
        if rng.random() < 0.3:
            g[(y + 1) % TILE][x] = "1"
    return g


def cemiterio_cova(rng: random.Random) -> list:
    """Terra revolvida: a cova fechada há pouco — torrão solto e marca de pá.
    A marca é curta e torta (4-7px, desce 1px de vez em quando); na iteração 1
    os sulcos atravessavam o tile inteiro e o chão leu como código de barras."""
    g = blank("A")
    speckle(g, rng, "B", 0.22)
    speckle(g, rng, "1", 0.06)
    for _ in range(rng.randint(3, 6)):           # torrões com sombra embaixo
        cx, cy = rng.randrange(TILE), rng.randrange(TILE)
        blob(g, rng, "C", cx, cy, rng.randint(3, 6))
        g[(cy + 1) % TILE][cx] = "1"
    for _ in range(rng.randint(2, 4)):           # marca de pá
        y = rng.randrange(2, TILE - 2)
        x0 = rng.randrange(TILE)
        for i in range(rng.randint(4, 7)):
            if rng.random() < 0.2:
                y += 1
            x = (x0 + i) % TILE
            g[y][x] = "1"
            if rng.random() < 0.6:
                g[y - 1][x] = "C"                # beira levantada pela pá
    return g


# ------------------------------------------------------------------ mármore
# Mausoléu e a parte cara da cidade. A paleta de Blumenau não tem branco —
# o mais claro é o bege D e o cinza frio 5. O mármore daqui é cinza, não
# branco de catálogo, e isso é bom: casa com o resto sem brigar por atenção.


def marmore_placa(rng: random.Random) -> list:
    """Placa polida: fundo frio, veio discreto, fiada de 8px e prumo na
    esquerda. É a superfície mais lisa do jogo — pouco ruído de propósito
    (na iteração 1 o pontilhado bege a 14% leu como granilite)."""
    g = blank("5")
    speckle(g, rng, "D", 0.05)
    x = rng.randrange(TILE)                      # um veio só, para ler polido
    for y in range(TILE):
        g[y][x % TILE] = "4"
        if rng.random() < 0.4:
            g[y][(x + 1) % TILE] = "D"
        x += rng.choice((-1, 0, 0, 1))
    for fiada in range(2):                       # junta horizontal da placa
        y0 = fiada * 8
        for xx in range(TILE):
            g[(y0 - 1) % TILE][xx] = "4"
            g[y0][xx] = "D"
    for yy in range(TILE):                       # prumo entre placas
        g[yy][0] = "4"
        g[yy][1] = "D" if rng.random() < 0.7 else "5"
    return g


def marmore_veio(rng: random.Random) -> list:
    """Bloco veado — o caro, o que o mausoléu usa na frente. Dois a três veios
    longos e finos; na iteração 1 eram até 5 e o bloco leu como gelo trincado."""
    g = blank("5")
    speckle(g, rng, "D", 0.07)
    for _ in range(rng.randint(2, 3)):
        x = rng.randrange(TILE)
        for y in range(TILE):
            g[y][x % TILE] = "4" if rng.random() < 0.8 else "3"
            if rng.random() < 0.3:
                g[y][(x + 1) % TILE] = "D"
            if rng.random() < 0.5:
                x += rng.choice((-1, 1))
    return g


def marmore_rodape(rng: random.Random) -> list:
    """Cimalha: o perfil que fecha a parede no teto e no chão. Tile de
    remate — alterna com placa/veio para a parede não ser um bloco único."""
    g = blank("5")
    speckle(g, rng, "D", 0.10)
    perfil = {0: "D", 1: "5", 2: "4", 3: "D", 4: "5",
              12: "4", 13: "D", 14: "5", 15: "3"}
    for y, cor in perfil.items():
        for x in range(TILE):
            g[y][x] = cor
    return g


def marmore_lascado(rng: random.Random) -> list:
    """O mármore depois do Colapso: lasca, trinca e bolor na junta. É este
    que deve aparecer mais — o mausoléu está em ruína, não em manutenção.
    A trinca anda numa direção própria por tile (esquerda ou direita, com
    queda), núcleo preto interrompido por grafite: na iteração 1 todas eram
    verticais e pretas, e a repetição saltava aos olhos ao ladrilhar."""
    g = marmore_placa(rng)
    for _ in range(rng.randint(2, 4)):           # lascas
        cx, cy = rng.randrange(TILE), rng.randrange(TILE)
        blob(g, rng, "4", cx, cy, rng.randint(3, 6))
        blob(g, rng, "3", cx, cy, rng.randint(1, 3))
    x, y = rng.randrange(TILE), rng.randrange(TILE // 2)
    dx = rng.choice((-1, 1))
    for i in range(rng.randint(6, 11)):          # trinca
        g[y % TILE][x % TILE] = "3" if i % 3 == 2 else "1"
        if rng.random() < 0.5:
            x += dx
        else:
            y += 1
    for yy in range(TILE):                       # bolor onde a água fica
        for xx in range(TILE):
            if g[yy][xx] == "4" and rng.random() < 0.18:
                g[yy][xx] = "E"
    return g


# --------------------------------------------------- periferia pós-enchente
# O bairro que a água pegou e ninguém reconstruiu. O eixo de leitura é a
# ALTURA DA LAMA: tudo abaixo da linha d'água é escuro e esverdeado, tudo
# acima continua com a cor original. Difere da família `agua` por ser o
# depois — lama seca e material improvisado, não água parada.


def periferia_tabua(rng: random.Random) -> list:
    """Tapume de tábua encharcada: 4 tábuas de 4px, fresta preta entre elas,
    e o pé ainda escuro de água. Tábua em B/C com A só no veio — na iteração 1
    a base em A deixou a parede turva demais para ler contra o fundo.
    Tile de BASE: a faixa molhada fica nas 4 linhas de baixo e não ladrilha
    na vertical (ver NOTAS)."""
    g = blank("B")
    for tab in range(4):
        x0 = tab * 4
        r = rng.random()
        tom = "B" if r < 0.5 else ("C" if r < 0.8 else "A")
        for y in range(TILE):
            for x in range(x0, x0 + 3):
                g[y][x] = tom if rng.random() > 0.10 else "A"
            g[y][x0] = "D" if (tom == "C" and rng.random() < 0.3) else ("C" if rng.random() < 0.4 else tom)
            g[y][x0 + 3] = "1"                              # fresta
        for _ in range(rng.randint(1, 3)):                  # veio da madeira
            y = rng.randrange(TILE)
            for x in range(x0 + 1, x0 + 3):
                g[y][x] = "A"
    for y in range(12, TILE):                               # pé encharcado
        for x in range(TILE):
            if g[y][x] != "1" and rng.random() < 0.55:
                g[y][x] = "2" if rng.random() < 0.6 else "E"
    return g


def periferia_zinco(rng: random.Random) -> list:
    """Telha de zinco amarrada por cima do que sobrou: onda vertical de
    período 4 e ferrugem onde a água empoçou."""
    g = blank("4")
    onda = {0: "5", 1: "4", 2: "3", 3: "2"}
    for x in range(TILE):
        for y in range(TILE):
            g[y][x] = onda[x % 4]
    for _ in range(rng.randint(2, 5)):
        blob(g, rng, "9", rng.randrange(TILE), rng.randrange(TILE), rng.randint(4, 9))
    speckle(g, rng, "6", 0.05)
    for x in range(TILE):                                   # emenda horizontal
        g[0][x] = "1"
        g[1][x] = "5" if rng.random() < 0.5 else "4"
    return g


def periferia_reboco(rng: random.Random) -> list:
    """Reboco com a lama já seca por cima: mancha, trinca e um pedaço caído
    mostrando o tijolo. Sem linha de água limpa — isso é o `agua/marca_nivel`;
    aqui a enchente já passou e secou torto."""
    g = blank("D")
    speckle(g, rng, "C", 0.12)
    for _ in range(rng.randint(2, 4)):
        blob(g, rng, "B", rng.randrange(TILE), rng.randrange(TILE), rng.randint(5, 11))
    speckle(g, rng, "F", 0.05)
    x = rng.randrange(TILE)                                 # trinca
    for y in range(TILE):
        g[y][x % TILE] = "1" if rng.random() < 0.8 else "C"
        x += rng.choice((-1, 0, 0, 1))
    if rng.random() < 0.5:                                  # reboco caído
        cx, cy = rng.randrange(3, 12), rng.randrange(3, 12)
        for y in range(cy, min(TILE, cy + rng.randint(3, 6))):
            for x2 in range(cx, min(TILE, cx + rng.randint(3, 7))):
                g[y][x2] = "9" if rng.random() < 0.7 else "A"
    return g


def periferia_entulho(rng: random.Random) -> list:
    """Chão de entulho: o que a água empurrou e deixou. Cada caco leva sombra
    de contato embaixo, senão o chão lê como ruído e não como volume solto."""
    g = blank("A")
    speckle(g, rng, "B", 0.20)
    speckle(g, rng, "E", 0.08)
    for _ in range(rng.randint(4, 7)):
        cx, cy = rng.randrange(TILE), rng.randrange(2, TILE)
        tom = rng.choice(("3", "4", "C", "9", "D"))
        larg, alt = rng.randint(2, 5), rng.randint(1, 2)
        for y in range(cy, min(TILE, cy + alt)):
            for x in range(cx, min(TILE, cx + larg)):
                g[y][x] = tom
        if cy + alt < TILE:
            for x in range(cx, min(TILE, cx + larg)):
                g[cy + alt][x] = "1"
    return g


FAMILIES = {
    "enxaimel": [("panel", enxaimel_panel), ("beam_v", enxaimel_beam_v), ("beam_h", enxaimel_beam_h), ("diag", enxaimel_diag)],
    "metal": [("plate", metal_plate), ("rusty", metal_rusty), ("seams", metal_seams)],
    "agua": [("superficie", agua_superficie), ("lama", agua_lama), ("marca_nivel", agua_marca_nivel)],
    "pedra_portuguesa": [("silhar", pedra_silhar), ("abobada", pedra_abobada), ("piso", pedra_piso), ("musgo", pedra_musgo)],
    "cemiterio": [("terra", cemiterio_terra), ("mato", cemiterio_mato), ("cascalho", cemiterio_cascalho), ("cova", cemiterio_cova)],
    "marmore": [("placa", marmore_placa), ("veio", marmore_veio), ("rodape", marmore_rodape), ("lascado", marmore_lascado)],
    "periferia": [("tabua", periferia_tabua), ("zinco", periferia_zinco), ("reboco", periferia_reboco), ("entulho", periferia_entulho)],
}


# Tiles que NÃO ladrilham livremente — vão para o manifest e para o Rule Tile.
NOTAS = {
    "agua": {"marca_nivel": "base: uma linha d'água por tile, não empilhar na vertical"},
    "marmore": {"rodape": "remate: perfil de cimalha, alternar com placa/veio"},
    "periferia": {"tabua": "base: faixa molhada nas 4 linhas de baixo, só na fiada do chão"},
}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("familia", choices=sorted(FAMILIES))
    ap.add_argument("--palette", type=Path, required=True)
    ap.add_argument("--seed", type=int, required=True, help="Seed determinística (registrada no manifest)")
    ap.add_argument("--variations", type=int, default=4, help="Variações por tipo de tile (default 4)")
    ap.add_argument("--scale", type=int, default=3, help="Expansão do sheet final: 3 = tile 48px do ADR-011 (default, Scale3x + textura), 2 = tile 32px do ADR-004, legado (EPX + textura), 1 = nativo 16")
    ap.add_argument("-o", "--out", type=Path, required=True)
    args = ap.parse_args()

    palette = load_palette(args.palette)
    rng = random.Random(args.seed)
    types = FAMILIES[args.familia]

    out_tile = TILE * args.scale
    sheet = Image.new("RGBA", (out_tile * args.variations, out_tile * len(types)), (0, 0, 0, 0))
    for row, (_, fn) in enumerate(types):
        for col in range(args.variations):
            grid = ["".join(r) for r in fn(rng)]
            if args.scale == 2:
                # Detail pass ADR-004: EPX (curvas) + textura fina no grid 32.
                # Tiles são opacos e seamless: onde o EPX vaza '.' na borda
                # (vizinho fora do tile), cai no nearest do pixel original.
                smooth = epx(grid)
                nearest = ["".join(ch * 2 for ch in r) for r in grid for _ in (0, 1)]
                merged = ["".join(s if s != "." else n for s, n in zip(sr, nr)) for sr, nr in zip(smooth, nearest)]
                grid = add_noise(merged, f"{args.familia}-{args.seed}-{row}-{col}")
            elif args.scale == 3:
                # Detail pass ADR-011: Scale3x (curvas) + textura fina no grid 48.
                # 16 x 3 = 48 é exato, então o tile do grid novo sai sem interpolação.
                smooth = scale3x(grid)
                nearest = ["".join(ch * 3 for ch in r) for r in grid for _ in range(3)]
                merged = ["".join(s if s != "." else n for s, n in zip(sr, nr)) for sr, nr in zip(smooth, nearest)]
                grid = add_noise(merged, f"{args.familia}-{args.seed}-{row}-{col}")
            elif args.scale > 3:
                grid = [ "".join(ch * args.scale for ch in r) for r in grid for _ in range(args.scale) ]
            for y in range(len(grid)):
                for x in range(len(grid[0])):
                    sheet.putpixel((col * out_tile + x, row * out_tile + y), palette[grid[y][x]])
    sheet.save(args.out)

    manifest = {
        "generator": "gen_tileset.py",
        "familia": args.familia,
        "seed": args.seed,
        "variations": args.variations,
        "palette": str(args.palette),
        "tile_size": TILE * args.scale,
        "draw_size": TILE,
        "scale": args.scale,
        "rows": [name for name, _ in types],
        "layout": "linhas = tipos, colunas = variações",
    }
    if args.familia in NOTAS:
        manifest["notas"] = NOTAS[args.familia]
    manifest_path = args.out.with_suffix(".manifest.json")
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"OK: {args.out} ({len(types)} tipos x {args.variations} variações, seed {args.seed}) + {manifest_path.name}")


if __name__ == "__main__":
    main()
