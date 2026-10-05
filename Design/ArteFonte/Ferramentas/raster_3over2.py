#!/usr/bin/env python3
"""Reescala PNG de pixel art de 32 para o grid 48 (×1,5) preservando a paleta.

Para o que **não tem spec 1x** e por isso não pode ser re-expandido pelo
`spec_redetail.py` — raster antigo, saída de difusão já pixelizada, arte vinda
de fora. Os assets com spec devem usar `spec_redetail.py --scale 3`, que é
sempre melhor: parte do desenho original em vez de um resultado já expandido.

Como faz ×1,5 sem inventar cor: **Scale3x e depois redução 2:1 por cor
dominante**. Nenhuma média, nenhum pixel novo — cada pixel de saída é uma das
cores que já estavam no bloco, então a paleta sai intacta e o `palette_check`
continua valendo. Empates no bloco 2x2 vão para a cor do canto superior
esquerdo, o que mantém o resultado determinístico.

A saída é um ponto de partida: 1,5 sempre perde algum detalhe de borda, e o
ciclo de crítica visual continua valendo.

Uso:
  py raster_3over2.py entrada.png -o saida.png

Dependência: pip install pillow
"""
import argparse
from collections import Counter
from pathlib import Path

from PIL import Image


def scale3x_rgba(img: Image.Image) -> Image.Image:
    """Scale3x sobre pixels RGBA — mesma regra do spec_redetail, em cor."""
    w, h = img.size
    src = img.load()
    out = Image.new("RGBA", (w * 3, h * 3), (0, 0, 0, 0))
    dst = out.load()

    def g(x: int, y: int):
        return src[min(max(x, 0), w - 1), min(max(y, 0), h - 1)]

    for y in range(h):
        for x in range(w):
            e = g(x, y)
            a, b, c = g(x - 1, y - 1), g(x, y - 1), g(x + 1, y - 1)
            d, f = g(x - 1, y), g(x + 1, y)
            gg, hh, i = g(x - 1, y + 1), g(x, y + 1), g(x + 1, y + 1)
            if b != hh and d != f:
                vals = (
                    d if d == b else e,
                    b if (d == b and e != c) or (b == f and e != a) else e,
                    f if f == b else e,
                    d if (d == b and e != gg) or (d == hh and e != a) else e,
                    e,
                    f if (b == f and e != i) or (hh == f and e != c) else e,
                    d if d == hh else e,
                    hh if (d == hh and e != i) or (hh == f and e != gg) else e,
                    f if f == hh else e,
                )
            else:
                vals = (e,) * 9
            for j, v in enumerate(vals):
                dst[x * 3 + j % 3, y * 3 + j // 3] = v
    return out


def reduzir2(img: Image.Image) -> Image.Image:
    """Redução 2:1 por cor dominante no bloco 2x2 — sem média, sem cor nova."""
    w, h = img.width // 2, img.height // 2
    src = img.load()
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    dst = out.load()
    for y in range(h):
        for x in range(w):
            bloco = [src[x * 2, y * 2], src[x * 2 + 1, y * 2],
                     src[x * 2, y * 2 + 1], src[x * 2 + 1, y * 2 + 1]]
            contagem = Counter(bloco)
            topo = max(contagem.values())
            # empate resolve pelo canto superior esquerdo: determinístico
            dst[x, y] = next(c for c in bloco if contagem[c] == topo)
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("png", type=Path)
    ap.add_argument("-o", "--out", type=Path, required=True)
    args = ap.parse_args()

    origem = Image.open(args.png).convert("RGBA")
    if origem.width % 2 or origem.height % 2:
        raise SystemExit(f"ERRO: {args.png.name} tem lado ímpar ({origem.size}); "
                         "a redução 2:1 depois do Scale3x exige lados pares.")
    destino = reduzir2(scale3x_rgba(origem))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    destino.save(args.out)

    cores_antes = {p for p in origem.get_flattened_data() if p[3] > 0}
    cores_depois = {p for p in destino.get_flattened_data() if p[3] > 0}
    novas = cores_depois - cores_antes
    print(f"OK: {args.out} ({origem.width}x{origem.height} -> {destino.width}x{destino.height}, "
          f"{len(cores_depois)} cores)")
    if novas:
        raise SystemExit(f"ERRO: {len(novas)} cor(es) que não existiam na origem — "
                         "a redução deveria ser por dominância, não por média.")


if __name__ == "__main__":
    main()
