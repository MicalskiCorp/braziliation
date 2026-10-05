#!/usr/bin/env python3
"""Autômato Abandonado — máquina davinciana de Blumenau, 96x96 lateral.

A criatura é um AUTÔMATO DE RELOJOARIA no espírito dos desenhos de Leonardo:
armação aberta de madeira e metal, com o maquinismo à vista. O corpo não é uma
carcaça fechada — é um gradil vazado por onde se enxerga o trem de engrenagens
por dentro. Engrenagem pequena aparece em toda junta: pescoço, ombro, cotovelo,
punho, quadril, joelho.

Duas dimensões de variação, independentes:

- ARMAMENTO — o que muda a leitura de ameaça: lança, escudo-engrenagem, ou
  nada, no caso do que se remontou de sucata;
- LIGA — a cor do metal, que o jogo pode usar como grau de dificuldade: bronze
  é o comum, prata é o mais duro, ferro é o degradado. Só a rampa do metal muda;
  madeira, cobre e a brasa da lente ficam iguais, então a silhueta não muda com
  o grau e o jogador lê a dificuldade pela cor sem reaprender a forma.

Fica no context pack, e não em Ferramentas/, porque é específico deste asset:
Ferramentas/ guarda o que serve a qualquer sprite.

Lições codificadas aqui (custaram iterações, não apague sem motivo):
- engrenagem só lê como roda se for DISCO SÓLIDO FURADO — aro de 1px some;
- dente tem que ser bloco 2x2; pixel isolado vira ponta de estrela;
- o preto é exclusividade do outline e da sombra de contato: o corpo vive em
  valores médios e é a LUZ DE BORDA de 1px que o recorta do fundo;
- cada engrenagem precisa de folga escura em volta — a 64x64 cabiam duas, por
  isso este arquivo nasceu em 96x96 (ADR-011);
- o vazado entre as costelas é o que faz ler "máquina aberta" em vez de
  "boneco de lata": sem buraco, detalhe interno vira textura.

Uso:
  py montagem.py enm_automato.spec.json
"""
import json
import math
import sys
from pathlib import Path

W = H = 96
EMPTY = "."

# Animação: o idle é o maquinismo girando. NFRAMES e FRAME são lidos pela
# engrenagem() para avançar a fase de cada roda.
NFRAMES = 6
FRAME = [0]

# Ligas: rampa do metal principal. [sombra profunda, sombra, meio-tom, luz]
LIGAS = {
    "bronze": ["6", "7", "8", "8"],
    "prata":  ["3", "4", "5", "5"],
    "ferro":  ["2", "3", "4", "5"],
}
LIGA = ["bronze"]

BASE_RAMPS = {
    # "vazio" é o furo da engrenagem: não é transparência, é o interior escuro
    # da máquina visto pela janela. Apagar o pixel abriria buraco na silhueta e
    # levaria junto o que estivesse atrás.
    "vazio":     ["1", "1", "2", "2"],
    "madeira":   ["A", "B", "C", "D"],
    "madeira_d": ["1", "A", "B", "C"],
    "cobre":     ["1", "9", "C", "C"],
}


def ramp(m: str) -> list:
    if m == "metal":
        return LIGAS[LIGA[0]]
    if m == "metal_d":
        c = LIGAS[LIGA[0]]
        return ["1", c[0], c[1], c[2]]
    return BASE_RAMPS[m]


grid, mat, z = None, None, None
Z = [0]


def limpar():
    global grid, mat, z
    grid = [[EMPTY] * W for _ in range(H)]
    mat = [[None] * W for _ in range(H)]
    z = [[-1] * W for _ in range(H)]
    Z[0] = 0


def peca():
    Z[0] += 1


def put(x, y, m):
    if 0 <= x < W and 0 <= y < H:
        grid[y][x] = "?"
        mat[y][x] = m
        z[y][x] = Z[0]


def furar(x, y):
    if 0 <= x < W and 0 <= y < H:
        grid[y][x] = EMPTY
        mat[y][x] = None
        z[y][x] = -1


def rect(x0, y0, x1, y1, m):
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            put(x, y, m)


def vazar(x0, y0, x1, y1):
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            furar(x, y)


def ellipse(cx, cy, rx, ry, m):
    for y in range(cy - ry, cy + ry + 1):
        for x in range(cx - rx, cx + rx + 1):
            if ((x - cx + .5) / (rx + .5)) ** 2 + ((y - cy + .5) / (ry + .5)) ** 2 <= 1.1:
                put(x, y, m)


def ring(cx, cy, r, m, inner=.45):
    for y in range(cy - r, cy + r + 1):
        for x in range(cx - r, cx + r + 1):
            d = ((x - cx + .5) / (r + .5)) ** 2 + ((y - cy + .5) / (r + .5)) ** 2
            if inner <= d <= 1.05:
                put(x, y, m)


def line(x0, y0, x1, y1, t, m):
    steps = max(abs(x1 - x0), abs(y1 - y0), 1)
    for i in range(steps + 1):
        x = round(x0 + (x1 - x0) * i / steps)
        y = round(y0 + (y1 - y0) * i / steps)
        rect(x, y, x + t - 1, y + t - 1, m)


def engrenagem(cx, cy, r, m="metal", dentes=None, fase=0.0, eixo="cobre", giro=1):
    """Disco sólido + dentes em bloco + janelas vazadas.

    `giro` (+1/-1) é o sentido de rotação: rodas que engrenam uma na outra giram
    em sentidos opostos, e é esse contraste que faz o maquinismo ler como
    mecanismo em vez de enfeite girando junto. O passo por frame é um período
    de simetria da peça dividido pelo ciclo, então o último frame emenda no
    primeiro sem salto."""
    if dentes is None:
        dentes = max(6, min(18, r * 2))
    janelas = (4 if r < 7 else 5) if r >= 4 else 0
    periodo = 2 * math.pi / (janelas if janelas else dentes)
    fase += giro * FRAME[0] * periodo / NFRAMES
    peca()
    ellipse(cx, cy, r, r, m)
    for i in range(dentes):
        a = fase + i * 2 * math.pi / dentes
        tx, ty = cx + (r + 1.0) * math.cos(a), cy + (r + 1.0) * math.sin(a)
        for ox in (0, 1):
            for oy in (0, 1):
                put(round(tx) + ox - 1, round(ty) + oy - 1, m)
    if r >= 4:
        raio_j = max(1, r // 3)
        meu_z = Z[0]
        for i in range(janelas):
            a = fase + math.pi / janelas + i * 2 * math.pi / janelas
            vx, vy = round(cx + (r * .55) * math.cos(a)), round(cy + (r * .55) * math.sin(a))
            for dx in range(-raio_j, raio_j + 1):
                for dy in range(-raio_j, raio_j + 1):
                    # a janela vaza SÓ a própria roda: o que está atrás (a platina,
                    # outra engrenagem) continua lá e é o que se enxerga pelo furo
                    if abs(dx) + abs(dy) <= raio_j and 0 <= vx + dx < W and 0 <= vy + dy < H:
                        if z[vy + dy][vx + dx] == meu_z:
                            put(vx + dx, vy + dy, "vazio")
    peca()
    if r >= 5:
        ellipse(cx, cy, r // 5, r // 5, eixo)


def rebites(x0, x1, y, passo, m="cobre"):
    for x in range(x0, x1 + 1, passo):
        put(x, y, m)


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
            if mat[y][x] is not None:
                grid[y][x] = "1"
    # a brasa respira com o ciclo: dois frames mais acesa, os outros em brasa baixa
    aceso = FRAME[0] % NFRAMES in (1, 2)
    for x in range(62, 66):
        grid[15][x] = "G"
        grid[16][x] = "G"
    grid[15][65] = "D" if aceso else "9"
    grid[16][64] = "9" if aceso else "1"
    if aceso:
        grid[14][64] = "9"


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


# ---------------------------------------------------------------- acabamento
def runs_por_material():
    out = {}
    for y in range(H):
        x = 0
        while x < W:
            m = mat[y][x]
            if m is None:
                x += 1
                continue
            x0 = x
            while x < W and mat[y][x] == m:
                x += 1
            out.setdefault((y, m), []).append((x0, x - 1))
    return out


def shade():
    for (y, m), runs in runs_por_material().items():
        r = ramp(m)
        for x0, x1 in runs:
            n = x1 - x0 + 1
            for x in range(x0, x1 + 1):
                t = (x - x0) / max(n - 1, 1)
                if n <= 3:
                    band = 2 if t < .5 else 1
                elif n <= 5:
                    band = 2 if t < .34 else (1 if t < .7 else 0)
                elif t < .18:
                    band = 3
                elif t < .38:
                    band = 2
                elif t < .74:
                    band = 1
                else:
                    band = 0
                if .34 <= t < .44 and (x + y) % 2 == 0:
                    band = min(band + 1, 3)
                if .70 <= t < .80 and (x + y) % 2 == 1:
                    band = max(band - 1, 0)
                grid[y][x] = r[band]


def contato():
    for y in range(H):
        for x in range(W):
            if mat[y][x] is None:
                continue
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, ny = x + dx, y + dy
                if 0 <= nx < W and 0 <= ny < H and z[ny][nx] > z[y][x]:
                    grid[y][x] = ramp(mat[y][x])[0]
                    break


def luz_de_borda():
    for y in range(H):
        xs = [x for x in range(W) if mat[y][x] is not None]
        if not xs:
            continue
        x = max(xs)
        m = mat[y][x]
        grid[y][x] = ramp(m)[3]
        if y % 3 == 0 and x - 1 >= 0 and mat[y][x - 1] == m:
            grid[y][x - 1] = ramp(m)[2]


def outline():
    base = [row[:] for row in grid]
    for y in range(H):
        for x in range(W):
            if base[y][x] != EMPTY:
                continue
            if any(0 <= x + dx < W and 0 <= y + dy < H and base[y + dy][x + dx] != EMPTY
                   for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                grid[y][x] = "1"


def montar(partes: set, liga: str, frame: int = 0) -> list:
    LIGA[0] = liga
    FRAME[0] = frame
    limpar()
    for nome, fn in ORDEM:
        if nome in partes:
            fn()
    shade()
    contato()
    luz_de_borda()
    lente()
    outline()
    return ["".join(r) for r in grid]


if __name__ == "__main__":
    ids_idle = ["idle"] + [f"f{i}" for i in range(2, NFRAMES + 1)]
    outputs = [{"id": ids_idle[i], "rows": montar(ANIMA[0], ANIMA[1], i)} for i in range(NFRAMES)]
    outputs += [{"id": nome, "rows": montar(partes, liga)} for nome, (partes, liga) in ESTATICOS.items()]
    out = Path(sys.argv[1] if len(sys.argv) > 1 else "enm_automato.spec.json")
    anterior = json.loads(out.read_text(encoding="utf-8")) if out.exists() else {}
    spec = {
        "name": "enm_automato",
        "size": [W, H],
        "palette": "../../../../ArteConceitual/Paletas/blumenau.json",
        "notes": anterior.get("notes", ""),
        "outputs": outputs,
        "sheets": {"idle": ids_idle},
    }
    out.write_text(json.dumps(spec, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    usadas = sorted({c for o in outputs for r in o["rows"] for c in r if c != EMPTY})
    print(f"OK: {out} — {NFRAMES} frames de idle + {len(ESTATICOS)} estáticos em {W}x{H}, "
          f"{len(usadas)} cores: {' '.join(usadas)}")
