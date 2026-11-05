#!/usr/bin/env python3
"""Pixel pass da engrenagem da comporta — redesenha a roda nas 3 specs 3x.

TESTE (2026-11-04): roda sobre as CÓPIAS das specs que estão nesta pasta, não
sobre o context pack `exemplo-prop-comporta-blumenau/`. A comporta canônica
(context pack, Selected/ e Assets/) segue com a roda antiga. Ver ../index.md.

Por que existe: na re-autoria do ADR-011 a comporta passou pelo
`spec_redetail.py --scale 3` (Scale3x + textura). No 1x a roda era um disco de
raio 4 com 3 dentes; o Scale3x arredondou cada dente em lóbulo e a peça passou
a ler como um torrão de latão, não como engrenagem. No frame 2 ainda sobraram
dois dentes soltos, flutuando fora da roda.

O que este passe faz, nas 3 specs `*.3x.spec.json` desta pasta:
  1. apaga o latão antigo (6/7/8) dentro da caixa da roda — só latão: o braço
     de ferro da alavanca, o poste de madeira e a caixa de ferro ficam;
  2. desenha uma roda de verdade: 10 dentes quadrados, aro, alma rebaixada,
     3 raios e cubo de ferro com parafuso de cobre;
  3. gira a roda junto com a alavanca (-45°, 0°, +45°) — a alavanca É a
     manivela dela. Com 3 raios os três frames ficam distintos (com 4 raios o
     primeiro e o último seriam iguais; com 8 dentes, a rotação de 45° seria
     invisível nos dentes);
  4. a metade de baixo da roda some na fenda da caixa de ferro (linha 66+):
     lê como engrenagem montada no mancal, não como disco solto.

Luz de cima e da esquerda, como no resto do prop: aresta voltada para a luz em
8, corpo em 7, aresta da sombra e alma em 6.

Idempotente: roda sobre as specs atuais e pode ser rodado de novo — o passo 1
apaga também a roda que ele mesmo desenhou (é toda latão + cubo de ferro
dentro do raio do cubo).

Uso:
  py pixel_pass_engrenagem.py            # reescreve as 3 specs 3x
  py pixel_pass_engrenagem.py --dry-run  # só mostra quantos pixels mudariam
"""
import argparse
import json
import math
from pathlib import Path

AQUI = Path(__file__).resolve().parent
FRAMES = {  # spec 3x -> giro da roda em graus (horário, acompanha a alavanca)
    "prop_blumenau_floodgate_lever.3x.spec.json": -45.0,
    "prop_blumenau_floodgate_lever_f2.3x.spec.json": 0.0,
    "prop_blumenau_floodgate_lever_f3.3x.spec.json": 45.0,
}

CX, CY = 49.0, 55.0          # centro da roda (coordenada de pixel, canto)
R_PE = 12.0                  # raio do pé do dente (fim do aro)
R_TOPO = 16.0                # raio da ponta do dente
R_ALMA = 9.0                 # dentro disto é a alma rebaixada, entre os raios
R_CUBO = 3.2                 # cubo de ferro
N_DENTES = 10
N_RAIOS = 3
CAIXA = (26, 30, 65, 65)     # x0, y0, x1, y1 — onde a roda antiga vivia (o dente esquerdo ia até x=27)
FENDA_Y = 66                 # dali para baixo a roda está dentro da caixa de ferro
POSTE = (66, 72)             # colunas do poste de madeira que o dente antigo invadia
LATAO = set("678")


def ang_dist(a: float, b: float) -> float:
    d = (a - b) % 360.0
    return min(d, 360.0 - d)


def dentro_da_roda(x: float, y: float, giro: float) -> str | None:
    """Classifica o ponto (centro do pixel) em uma parte da roda, ou None."""
    dx, dy = x - CX, y - CY
    r = math.hypot(dx, dy)
    if r > R_TOPO:
        return None
    ang = math.degrees(math.atan2(dy, dx))
    if r <= R_CUBO:
        return "cubo"
    if r <= R_PE:
        if r > R_ALMA:
            return "aro"
        passo_raio = 360.0 / N_RAIOS
        if any(ang_dist(ang, giro + 90.0 + k * passo_raio) * math.pi / 180.0 * r <= 1.3
               for k in range(N_RAIOS)):
            return "raio"
        return "alma"
    # dente: largura em px constante (2,6 no pé, 2,0 na ponta) — dente quadrado,
    # não cunha; é isso que o Scale3x tinha apagado
    meia = 2.6 - 0.6 * (r - R_PE) / (R_TOPO - R_PE)
    passo = 360.0 / N_DENTES
    for k in range(N_DENTES):
        if ang_dist(ang, giro + k * passo) * math.pi / 180.0 * r <= meia:
            return "dente"
    return None


def cor(parte: str, x: int, y: int, giro: float) -> str:
    def aceso(px: float, py: float) -> bool:
        # a aresta é "acesa" se o vizinho fora da roda fica para cima/esquerda
        return dentro_da_roda(px - 1 + .5, py + .5, giro) is None or \
            dentro_da_roda(px + .5, py - 1 + .5, giro) is None

    def sombra(px: float, py: float) -> bool:
        return dentro_da_roda(px + 1 + .5, py + .5, giro) is None or \
            dentro_da_roda(px + .5, py + 1 + .5, giro) is None

    if parte == "cubo":
        r = math.hypot(x + .5 - CX, y + .5 - CY)
        if r <= 1.3:
            return "9"                              # parafuso de cobre
        return "5" if (x + .5 - CX) + (y + .5 - CY) < 0 else "3"
    if parte == "alma":
        return "6"
    if parte == "raio":
        return "8" if (x + .5 - CX) + (y + .5 - CY) < -2 else "7"
    # aro e dente
    if aceso(x, y):
        return "8"
    if sombra(x, y):
        return "6"
    return "7"


def passar(rows: list[str], giro: float) -> tuple[list[str], int]:
    g = [list(r) for r in rows]
    x0, y0, x1, y1 = CAIXA
    mudou = 0
    # 1. apaga o latão antigo (e o cubo de um passe anterior) dentro da caixa
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            ch = g[y][x]
            r = math.hypot(x + .5 - CX, y + .5 - CY)
            # latão sai todo; cobre sai todo (só existe na bucha velha e no parafuso
            # novo); ferro 3/5 só dentro do cubo — o 4 do braço da alavanca fica
            if ch in LATAO or ch == "9" or (ch in "35" and r <= R_CUBO):
                g[y][x] = "."
    # 1b. o dente direito antigo era desenhado POR CIMA do poste (x 66-70, linhas
    #     51-59). Apagar ali abriria um buraco na madeira: recompõe copiando a
    #     textura do próprio poste 9 linhas acima, que está limpa.
    for y in range(y0, y1 + 1):
        for x in range(POSTE[0], POSTE[1] + 1):
            if g[y][x] in LATAO:
                g[y][x] = g[y - 9][x] if g[y - 9][x] not in LATAO else "B"
    # 2. desenha a roda só sobre vazio — o ferro da alavanca fica por cima
    for y in range(y0, min(y1, FENDA_Y - 1) + 1):
        for x in range(x0, x1 + 1):
            parte = dentro_da_roda(x + .5, y + .5, giro)
            if parte is None or g[y][x] != ".":
                continue
            g[y][x] = cor(parte, x, y, giro)
    novas = ["".join(r) for r in g]
    mudou = sum(a != b for ra, rb in zip(rows, novas) for a, b in zip(ra, rb))
    return novas, mudou


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    for nome, giro in FRAMES.items():
        p = AQUI / nome
        spec = json.loads(p.read_text(encoding="utf-8"))
        spec["rows"], mudou = passar(spec["rows"], giro)
        print(f"{nome}: giro {giro:+.0f}°, {mudou} px alterados")
        if not args.dry_run:
            p.write_text(json.dumps(spec, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
