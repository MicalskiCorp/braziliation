#!/usr/bin/env python3
"""Audita pares asset/.meta sob Desenvolvimento/Assets/.

O Unity exige um arquivo `.meta` para cada asset (arquivo ou pasta) versionado
— é ele que guarda o GUID usado por todas as referências (prefabs, cenas,
scenes, ScriptableObjects). Um asset sem `.meta` gera um GUID novo na próxima
vez que o Editor abrir o projeto; um `.meta` órfão (sem asset correspondente)
é lixo que pode reviver referências quebradas. Nenhum dos dois casos gera erro
de compilação — o import "conserta sozinho" e o problema só aparece depois,
como referência perdida numa cena ou prefab.

Uso:
  python check_meta_pairs.py [--assets-dir Desenvolvimento/Assets]

Sai com código 0 se não houver gaps, 1 se houver (usável em CI/skill).
Sem dependências além da stdlib.
"""
import argparse
import sys
from pathlib import Path

IGNORED_NAMES = {".DS_Store", "Thumbs.db"}


def is_hidden_from_unity(path: Path, assets_dir: Path) -> bool:
    """
    Regra de import do Unity: arquivo ou pasta que começa com '.', termina com '~',
    se chama 'cvs' ou tem extensão .tmp não é importado e nunca ganha .meta —
    nem nada dentro de uma pasta assim. Sem este filtro, todo .gitkeep saía como
    "asset sem .meta" e o gate reprovava um projeto correto.
    """
    for part in path.relative_to(assets_dir).parts:
        if part.startswith(".") or part.endswith("~") or part.lower() == "cvs":
            return True
    return path.suffix.lower() == ".tmp"


def iter_assets(assets_dir: Path):
    for path in assets_dir.rglob("*"):
        if path.name in IGNORED_NAMES:
            continue
        if path.suffix == ".meta":
            continue
        if is_hidden_from_unity(path, assets_dir):
            continue
        yield path


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--assets-dir", type=Path, default=Path("Desenvolvimento/Assets"))
    args = ap.parse_args()

    assets_dir = args.assets_dir
    if not assets_dir.is_dir():
        print(f"ERRO: pasta não encontrada: {assets_dir}")
        return 1

    missing_meta: list[Path] = []
    for asset in iter_assets(assets_dir):
        meta = asset.with_name(asset.name + ".meta")
        if not meta.exists():
            missing_meta.append(asset)

    orphan_meta: list[Path] = []
    for meta in assets_dir.rglob("*.meta"):
        asset = meta.with_name(meta.name[: -len(".meta")])
        if not asset.exists():
            orphan_meta.append(meta)

    total_checked = sum(1 for _ in iter_assets(assets_dir))
    print(f"Assets verificados: {total_checked}")

    if missing_meta:
        print(f"\nAssets SEM .meta ({len(missing_meta)}):")
        for p in sorted(missing_meta):
            print(f"  - {p}")
    if orphan_meta:
        print(f"\n.meta ÓRFÃOS, sem asset correspondente ({len(orphan_meta)}):")
        for p in sorted(orphan_meta):
            print(f"  - {p}")

    ok = not missing_meta and not orphan_meta
    print("\nAPROVADO — todos os assets têm .meta e todos os .meta têm asset." if ok
          else "\nREPROVADO — corrigir os gaps acima antes de commitar.")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
