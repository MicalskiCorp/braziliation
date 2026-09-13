#!/usr/bin/env python3
"""Gate de paleta para toda a arte própria em Desenvolvimento/Assets/Art/.

A regra "palette_check precisa APROVAR antes do export" existia só como texto. Este
script a aplica em lote: cada PNG recebe a paleta indicada em
Design/ArteConceitual/Paletas/regras-assets.json e passa pelo palette_check.py.
PNG sem regra também reprova — asset novo precisa ganhar paleta de propósito.

Uso:
  py Design/ArteFonte/Ferramentas/check_art_palettes.py

Sai com 0 se tudo aprovar, 1 caso contrário. Roda no pre-commit e no CI.
"""
import fnmatch
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
ART = ROOT / "Desenvolvimento" / "Assets" / "Art"
RULES = ROOT / "Design" / "ArteConceitual" / "Paletas" / "regras-assets.json"
CHECK = Path(__file__).with_name("palette_check.py")


def main() -> int:
    config = json.loads(RULES.read_text(encoding="utf-8"))
    ignorar = config.get("ignorar", [])
    regras = config["regras"]

    aprovados, reprovados, sem_regra = 0, [], []
    for png in sorted(ART.rglob("*.png")):
        rel = png.relative_to(ART).as_posix()
        if any(fnmatch.fnmatch(rel, g) for g in ignorar):
            continue

        regra = next((r for r in regras if fnmatch.fnmatch(rel, r["glob"])), None)
        if regra is None:
            sem_regra.append(rel)
            continue

        paleta = RULES.parent / regra["paleta"]
        result = subprocess.run(
            [sys.executable, str(CHECK), str(png), str(paleta)],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
        )
        if result.returncode == 0:
            aprovados += 1
        else:
            reprovados.append((rel, result.stdout.strip().splitlines()[-4:]))

    print(f"Paletas: {aprovados} aprovado(s), {len(reprovados)} reprovado(s), {len(sem_regra)} sem regra")
    for rel, detalhe in reprovados:
        print(f"  REPROVADO {rel}")
        for linha in detalhe:
            print(f"      {linha}")
    for rel in sem_regra:
        print(f"  SEM REGRA {rel} — adicione um glob em {RULES.relative_to(ROOT).as_posix()}")

    return 1 if reprovados or sem_regra else 0


if __name__ == "__main__":
    sys.exit(main())
