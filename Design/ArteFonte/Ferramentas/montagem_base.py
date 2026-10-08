#!/usr/bin/env python3
"""Motor de montagem de sprite por peças — a linha de montagem do Braziliation.

Nasceu no autômato davinciano e foi extraído aqui quando o segundo personagem
precisou do mesmo tratamento. O que mora aqui é o que não depende de QUAL
criatura está sendo desenhada:

- a tela de chars com material e profundidade por pixel;
- as primitivas de desenho (rect, ellipse, ring, line, engrenagem, rebites);
- as rampas de valor por material e as ligas de metal;
- os passes de acabamento: bandas de sombra, sombra de contato entre peças,
  luz de borda e outline.

O que NÃO mora aqui é o catálogo de peças: cada asset tem o seu, no próprio
context pack, porque peça é desenho, não ferramenta. O asset declara a ordem de
montagem e as variantes; este módulo monta e acaba.

Como usar, a partir do context pack de um asset:

    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "ArteFonte" / "Ferramentas"))
    from montagem_base import *

    def cabeca():
        peca()
        ellipse(52, 15, 8, 7, "metal_d")

    ORDEM = [("cabeca", cabeca)]
    rows = montar(ORDEM, {"cabeca"}, "bronze")

Lições codificadas aqui (custaram iteração, não apague sem motivo):
- engrenagem só lê como roda se for DISCO SÓLIDO FURADO — aro de 1px some;
- dente tem que ser bloco 2x2; pixel isolado vira ponta de estrela;
- a janela da engrenagem é PINTADA como interior escuro, não apagada: apagar
  levava junto o que estivesse atrás e abria buraco na silhueta;
- o preto é exclusividade do outline e da sombra de contato — o corpo vive em
  valores médios, e é a luz de borda de 1px que o recorta do fundo;
- cada engrenagem precisa de folga escura em volta: a 64x64 cabiam duas num
  torso, e foi isso que levou o projeto ao grid de 96 (ADR-011).
"""
import json
import math
from pathlib import Path

# Canvas padrão do grid de 48 PPU (ADR-011): 96 px = 2 unidades de mundo.
# Um asset pode redimensionar antes de montar, com redimensionar(w, h).
W, H = 96, 96
EMPTY = "."

# Animação: NFRAMES e FRAME são lidos pela engrenagem() para avançar a fase de
# cada roda. Um asset que anime de outro jeito só ignora isso.
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


def registrar_material(nome: str, rampa: list) -> None:
    """Material próprio de um asset: tecido de uma ordem, couro, pedra. A rampa
    é [sombra profunda, sombra, meio-tom, luz] em keys da paleta. Fica aqui e
    não no catálogo do asset porque o acabamento precisa alcançá-la."""
    BASE_RAMPS[nome] = rampa


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


def material(x, y):
    """Material do pixel, ou None se vazio. Acessor porque `limpar()` recria as
    matrizes a cada montagem: quem importa o nome direto congela o valor antigo."""
    return mat[y][x] if 0 <= x < W and 0 <= y < H else None


def pintar(x, y, ch):
    """Força um char no pixel, por cima do que o acabamento decidiu. É o que um
    passe de brilho ou brasa usa, depois das bandas de sombra."""
    if 0 <= x < W and 0 <= y < H:
        grid[y][x] = ch


def rebites(x0, x1, y, passo, m="cobre"):
    for x in range(x0, x1 + 1, passo):
        put(x, y, m)




def redimensionar(largura: int, altura: int) -> None:
    """Muda o canvas antes de montar. Asset menor que 96 usa isto."""
    global W, H
    W, H = largura, altura


def emitir_spec(destino, nome: str, outputs: list, sheets: dict | None = None,
                palette: str = "../../../../ArteConceitual/Paletas/blumenau.json") -> None:
    """Grava a spec consolidada, preservando as `notes` que já estiverem lá."""
    destino = Path(destino)
    anterior = json.loads(destino.read_text(encoding="utf-8")) if destino.exists() else {}
    spec = {
        "name": nome,
        "size": [W, H],
        "palette": palette,
        "notes": anterior.get("notes", ""),
        "outputs": outputs,
    }
    if sheets:
        spec["sheets"] = sheets
    destino.write_text(json.dumps(spec, ensure_ascii=False, indent=2) + chr(10), encoding="utf-8")
    usadas = sorted({c for o in outputs for r in o["rows"] for c in r if c != EMPTY})
    print(f"OK: {destino} — {len(outputs)} outputs em {W}x{H}, {len(usadas)} cores: {' '.join(usadas)}")


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


def montar(ordem: list, partes: set, liga: str = "bronze", frame: int = 0,
           acabamento=None) -> list:
    """Monta um output: desenha as peças de `partes` na ordem de `ordem` e passa
    o acabamento. `ordem` é uma lista de (nome, função) — o z-order é ela."""
    LIGA[0] = liga
    FRAME[0] = frame
    limpar()
    for nome, fn in ordem:
        if nome in partes:
            fn()
    shade()
    contato()
    luz_de_borda()
    if acabamento:
        acabamento()
    outline()
    return ["".join(r) for r in grid]


