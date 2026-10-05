#!/usr/bin/env python3
"""Deriva os frames de uma animação a partir de specs-chave + uma receita de movimento.

Fecha a lacuna entre "3 frames desenhados à mão" e as contagens que o
animation-guide.md pede (idle 4–6, run 8–12): as poses-chave continuam sendo
autoradas pixel a pixel, e os frames intermediários saem de **transformação
geométrica determinística** sobre a matriz de chars — não de geração de imagem.

A receita (`{asset}_{acao}.anim.json`) declara duas coisas independentes:

- `keys`: as specs-chave já aprovadas, cicladas ao longo dos frames. É o
  detalhe autorado (brilho de lente, dente de engrenagem) que não se
  interpola — se repete no ritmo que o autor escolheu.
- `layers`: o movimento calculado por frame (respiração, bob, recuo), aplicado
  sobre a matriz. Uma curva por camada, um valor por frame.

Receita:

{
  "name": "enm_automato",
  "action": "idle",
  "palette": "../../../../ArteConceitual/Paletas/blumenau.json",
  "keys": ["enm_automato_idle_f1.2x.spec.json", "..._f2.2x.spec.json", "..._f3.2x.spec.json"],
  "frames": 6,
  "output_ids": ["idle", "f2", "f3", "f4", "f5", "f6"],
  "layers": [
    {"op": "shift", "rows": [0, 43], "dy": [0, -1, -2, -2, -1, 0], "fill": "repeat_edge"}
  ]
}

Saída: a spec CONSOLIDADA do objeto (um output por frame + a entrada em
`sheets`), pronta para o `render_spec.py`. A spec gerada é versionada como
qualquer outra e carrega em `source` a receita e as chaves que a produziram —
é o registro de reprodutibilidade, equivalente ao manifest dos geradores `gen_`.

Uso:
  python spec_tween.py receita.anim.json            # grava {name}.spec.json ao lado
  python spec_tween.py receita.anim.json -o out.json

Operações de `layers`:
  shift — desloca a faixa de linhas [topo, base] por `dy` pixels (negativo = sobe).
          `fill`: "repeat_edge" (estica a linha da borda, default) ou "clear"
          (deixa transparente). Linhas fora da faixa não são tocadas — é assim
          que as pernas ficam ancoradas enquanto o torso respira.
"""
import argparse
import json
import sys
from pathlib import Path

EMPTY = "."


def load_key_rows(path: Path) -> list[str]:
    """Lê as linhas de uma spec-chave — aceita o formato legado (rows na raiz)
    e o consolidado (usa o primeiro output, ou o id após '#' no caminho)."""
    ref, _, output_id = str(path).partition("#")
    spec = json.loads(Path(ref).read_text(encoding="utf-8"))
    if "rows" in spec:
        return list(spec["rows"])
    outputs = spec.get("outputs") or []
    if not outputs:
        sys.exit(f"ERRO: {ref} não tem 'rows' nem 'outputs'.")
    if output_id:
        for output in outputs:
            if output["id"] == output_id:
                return list(output["rows"])
        ids = [o["id"] for o in outputs]
        sys.exit(f"ERRO: output '{output_id}' não existe em {ref}. Ids: {ids}")
    return list(outputs[0]["rows"])


def apply_shift(rows: list[str], top: int, bottom: int, dy: int, fill: str) -> list[str]:
    if dy == 0:
        return rows
    height = len(rows)
    if not (0 <= top <= bottom < height):
        sys.exit(f"ERRO: faixa [{top}, {bottom}] fora do canvas de {height} linhas.")
    region = rows[top : bottom + 1]
    blank = EMPTY * len(rows[0])
    k = abs(dy)
    if k >= len(region):
        sys.exit(f"ERRO: dy={dy} maior que a faixa [{top}, {bottom}].")
    if dy < 0:  # sobe
        edge = region[-1] if fill == "repeat_edge" else blank
        region = region[k:] + [edge] * k
    else:  # desce
        edge = region[0] if fill == "repeat_edge" else blank
        region = [edge] * k + region[:-k]
    return rows[:top] + region + rows[bottom + 1 :]


def apply_layer(rows: list[str], layer: dict, frame: int) -> list[str]:
    op = layer.get("op")
    if op == "shift":
        top, bottom = layer["rows"]
        return apply_shift(rows, top, bottom, layer["dy"][frame], layer.get("fill", "repeat_edge"))
    sys.exit(f"ERRO: operação '{op}' desconhecida. Disponíveis: shift.")


def build(recipe_path: Path, out_path: Path | None) -> Path:
    recipe = json.loads(recipe_path.read_text(encoding="utf-8"))
    frames = recipe["frames"]
    keys = recipe["keys"]
    output_ids = recipe.get("output_ids") or ["idle"] + [f"f{i}" for i in range(2, frames + 1)]
    if len(output_ids) != frames:
        sys.exit(f"ERRO: {len(output_ids)} output_ids para {frames} frames.")

    key_rows = [load_key_rows(recipe_path.parent / k) for k in keys]
    height = len(key_rows[0])
    width = len(key_rows[0][0])
    for k, rows in zip(keys, key_rows):
        if len(rows) != height or any(len(r) != width for r in rows):
            sys.exit(f"ERRO: {k} não tem o mesmo canvas das demais chaves ({width}x{height}).")

    for layer in recipe.get("layers", []):
        curve = layer.get("dy", [])
        if len(curve) != frames:
            sys.exit(f"ERRO: camada '{layer.get('op')}' tem {len(curve)} valores para {frames} frames.")

    outputs = []
    for i in range(frames):
        rows = list(key_rows[i % len(key_rows)])
        for layer in recipe.get("layers", []):
            rows = apply_layer(rows, layer, i)
        outputs.append({"id": output_ids[i], "rows": rows})

    action = recipe.get("action", "idle")
    spec = {
        "name": recipe["name"],
        "size": [width, height],
        "palette": recipe["palette"],
        "notes": recipe.get("notes", ""),
        "source": {
            "tool": "spec_tween.py",
            "recipe": recipe_path.name,
            "keys": keys,
            "layers": recipe.get("layers", []),
        },
        "outputs": outputs,
        "sheets": {action: output_ids},
    }
    out = out_path or recipe_path.parent / f"{recipe['name']}.spec.json"
    out.write_text(json.dumps(spec, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"OK: {out} ({frames} frames de {width}x{height}, sheet '{action}' = {output_ids})")
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("recipe", type=Path, help="Receita de animação (.anim.json)")
    ap.add_argument("-o", "--out", type=Path, default=None, help="Spec consolidada de saída")
    args = ap.parse_args()
    build(args.recipe, args.out)
