#!/usr/bin/env python3
"""Renderiza uma spec JSON de sprite (matriz de caracteres + paleta) em PNG.

A spec é a "fonte" versionável do sprite (Opção A do pipeline programático).
Desde a migração do Passo 4 (fluxo concept art -> spec -> sprite), o formato
padrão é a spec CONSOLIDADA: um JSON por objeto, com todos os frames/variações
dentro. O formato legado (1 arquivo por frame) continua sendo lido para não
quebrar specs já entregues, mas specs novas devem nascer no formato consolidado.

Formato consolidado (padrão atual):

{
  "name": "prop_blumenau_floodgate_lever",
  "size": [32, 32],
  "palette": "../../ArteConceitual/Paletas/blumenau.json",
  "outputs": [
    {"id": "idle", "rows": ["................", "......77........", "..."]},
    {"id": "f2",   "rows": ["...", "..."]},
    {"id": "f3",   "rows": ["...", "..."]}
  ],
  "sheets": {
    "activate": ["idle", "f2", "f3"]
  }
}

Cada output vira um PNG: id "idle"/"default" -> {name}.png; qualquer outro id
-> {name}_{id}.png. Cada entrada em "sheets" empacota a sequência de outputs
(nessa ordem) em {name}_{sheet}_sheet.png — equivalente a rodar sheet_pack.py
manualmente, mas a partir da mesma fonte.

Formato legado (specs pré-migração, 1 arquivo por frame — ex.: {asset}_f2.spec.json):

{
  "name": "...",
  "size": [32, 32],
  "palette": "...",
  "rows": ["...", ...]
}

Uso:
  python render_spec.py spec.json                    # consolidada: renderiza outputs + sheets
  python render_spec.py spec.json --only f2 -o f2.png # consolidada: só um output
  python render_spec.py spec_legado.json -o saida.png # legada: comportamento inalterado

Dependência: pip install pillow
"""
import argparse
import json
import sys
from pathlib import Path

from PIL import Image

from sheet_pack import pack_horizontal


def hex_to_rgba(h: str) -> tuple:
    h = h.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), 255)


def load_palette(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    return {c["key"]: hex_to_rgba(c["hex"]) for c in data["colors"]}


def render_rows(rows: list[str], width: int, height: int, palette: dict, palette_name: str) -> Image.Image:
    if len(rows) != height:
        sys.exit(f"ERRO: spec declara altura {height} mas tem {len(rows)} linhas em 'rows'.")
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    px = img.load()
    for y, row in enumerate(rows):
        if len(row) != width:
            sys.exit(f"ERRO: linha {y} tem {len(row)} chars; esperado {width}.")
        for x, ch in enumerate(row):
            if ch == ".":
                continue
            if ch not in palette:
                sys.exit(f"ERRO: char '{ch}' em ({x},{y}) não existe na paleta {palette_name}.")
            px[x, y] = palette[ch]
    return img


def output_filename(spec_name: str, output_id: str) -> str:
    return f"{spec_name}.png" if output_id in ("idle", "default") else f"{spec_name}_{output_id}.png"


def render(spec_path: Path, out_path: Path | None, scale: int = 1, only: str | None = None) -> list[Path]:
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    width, height = spec["size"]
    palette_path = (spec_path.parent / spec["palette"]).resolve()
    palette = load_palette(palette_path)
    base_dir = out_path.parent if out_path else spec_path.parent

    if "rows" in spec:
        # Spec legada — 1 arquivo por frame, comportamento inalterado.
        img = render_rows(spec["rows"], width, height, palette, palette_path.name)
        if scale > 1:
            img = img.resize((width * scale, height * scale), Image.NEAREST)
        out = out_path or spec_path.with_suffix(".png")
        img.save(out)
        used = {ch for row in spec["rows"] for ch in row if ch != "."}
        print(f"OK: {out} ({img.width}x{img.height}, {len(used)} cores da paleta {palette_path.stem})")
        return [out]

    outputs = spec.get("outputs")
    if not outputs:
        sys.exit("ERRO: spec não tem 'rows' (legada) nem 'outputs' (consolidada).")

    name = spec.get("name", spec_path.stem)
    wanted = [o for o in outputs if only is None or o["id"] == only]
    if only and not wanted:
        ids = [o["id"] for o in outputs]
        sys.exit(f"ERRO: output '{only}' não existe nesta spec. Ids disponíveis: {ids}")

    rendered: dict[str, Image.Image] = {}
    written: list[Path] = []
    for output in wanted:
        img = render_rows(output["rows"], width, height, palette, palette_path.name)
        rendered[output["id"]] = img
        saved = img.resize((width * scale, height * scale), Image.NEAREST) if scale > 1 else img
        out = out_path if (only and out_path) else base_dir / output_filename(name, output["id"])
        saved.save(out)
        used = {ch for row in output["rows"] for ch in row if ch != "."}
        print(f"OK: {out} ({saved.width}x{saved.height}, {len(used)} cores da paleta {palette_path.stem}) [output '{output['id']}']")
        written.append(out)

    if only:
        return written

    for sheet_name, frame_ids in spec.get("sheets", {}).items():
        missing = [fid for fid in frame_ids if fid not in rendered]
        if missing:
            print(f"AVISO: sheet '{sheet_name}' referencia outputs inexistentes {missing} — pulando.")
            continue
        imgs = [rendered[fid] for fid in frame_ids]
        if scale > 1:
            imgs = [im.resize((im.width * scale, im.height * scale), Image.NEAREST) for im in imgs]
        try:
            sheet = pack_horizontal(imgs)
        except ValueError as e:
            sys.exit(f"ERRO: sheet '{sheet_name}': {e}")
        sheet_out = base_dir / f"{name}_{sheet_name}_sheet.png"
        sheet.save(sheet_out)
        print(f"OK: {sheet_out} ({len(imgs)} frames -> {sheet.width}x{sheet.height}) [sheet '{sheet_name}']")
        written.append(sheet_out)

    return written


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("spec", type=Path, help="Caminho da spec JSON")
    ap.add_argument("-o", "--out", type=Path, default=None,
                     help="PNG de saída (spec legada, ou spec consolidada + --only). Ignorado ao renderizar todos os outputs de uma spec consolidada.")
    ap.add_argument("--scale", type=int, default=1,
                     help="Upscale nearest após o render (ex.: 2 para specs 1x legadas no grid 32 PPU do ADR-004)")
    ap.add_argument("--only", type=str, default=None,
                     help="Spec consolidada: renderiza só o output com este id (ex.: f2), útil durante o ciclo de crítica")
    args = ap.parse_args()
    render(args.spec, args.out, args.scale, args.only)
