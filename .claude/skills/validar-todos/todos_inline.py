"""
Lista os `// TODO` e `// TODO-DESIGN` do código e diz quais já parecem rastreados.

Passo E da skill validar-todos. Antes o agente fazia Grep e conferia um a um contra o
TODO.md e o tech_debt.md — trabalho mecânico pago em tokens. Classificação heurística:

  arquivo  — o nome do arquivo aparece no TODO.md ou no tech_debt.md
  domínio  — a ficha de sistema que lista o arquivo (ex.: Sistemas/Build.md) ou a
             mecânica de mesmo nome (Mechanics/Build.md) é citada no TODO.md
  NÃO      — nenhum dos dois: o agente decide se registra

Uso: py .claude/skills/validar-todos/todos_inline.py
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
DEV = ROOT / "Desenvolvimento"
FONTES = [DEV / "Assets" / "Scripts", DEV / "Assets" / "Editor", DEV / "src" / "Braziliation.Game.Core"]
TODO = DEV / "Docs" / "TODO.md"
DEBT = DEV / "Docs" / "Tech" / "tech_debt.md"
FICHAS = DEV / "Docs" / "Architecture" / "Sistemas"
MARCA = re.compile(r"//\s*(TODO(?:-DESIGN)?)\b[:\s-]*(.*)")


def dominio_por_arquivo() -> dict:
    """Nome do .cs → nome da ficha de sistema que o lista em "Fontes Técnicas"."""
    mapa = {}
    for ficha in FICHAS.glob("*.md"):
        if ficha.name == "index.md":
            continue
        for nome in re.findall(r"`([A-Za-z0-9_]+\.cs)`", ficha.read_text(encoding="utf-8")):
            mapa.setdefault(nome, ficha.stem)
    return mapa


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    todo = TODO.read_text(encoding="utf-8")
    registro = todo + "\n" + (DEBT.read_text(encoding="utf-8") if DEBT.exists() else "")
    dominios = dominio_por_arquivo()

    achados = []
    for base in FONTES:
        for arquivo in sorted(base.rglob("*.cs")):
            if {"bin", "obj"} & set(arquivo.parts):
                continue
            for n, linha in enumerate(arquivo.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
                m = MARCA.search(linha)
                if not m:
                    continue
                dominio = dominios.get(arquivo.name)
                if arquivo.stem in registro:
                    classe = "arquivo"
                elif dominio and f"{dominio}.md" in todo:
                    classe = f"domínio ({dominio})"
                else:
                    classe = "NÃO"
                achados.append((classe, arquivo.relative_to(DEV).as_posix(), n, m.group(1), m.group(2).strip()))

    nao = [a for a in achados if a[0] == "NÃO"]
    print(f"{len(achados)} marcador(es) inline · {len(achados) - len(nao)} rastreados (arquivo ou domínio) · {len(nao)} sem rastreio")
    for classe, caminho, n, tipo, texto in sorted(achados, key=lambda a: (a[0] != "NÃO", a[1], a[2])):
        print(f"  {classe:<22} {caminho}:{n} [{tipo}] {texto[:90]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
