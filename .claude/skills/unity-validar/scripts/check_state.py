"""
Gate do pre-commit: script Unity no commit exige `unity-validar` OK depois da última edição.

Por que existe: "mudou algo em Assets/? rode unity-validar antes de commitar" era regra
só escrita (CLAUDE.md, skill). O CI Unity depende de secrets que ainda não existem, então
nada impedia commitar um script que não compila. Este gate lê o resultado que a skill já
grava em .claude/state/unity-validar.json — não abre o Unity, custa milissegundos.

Entrada: caminhos dos .cs em stage, um por linha, no stdin. Saída 1 bloqueia o commit.
"""
import json
import os
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]  # scripts → unity-validar → skills → .claude → raiz
STATE = ROOT / ".claude" / "state" / "unity-validar.json"
COMANDO = "py .claude/skills/unity-validar/scripts/validar.py"


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    arquivos = [l.strip() for l in sys.stdin if l.strip()]
    if not arquivos:
        return 0

    if not STATE.exists():
        print(f"[unity] Nenhuma validação registrada nesta máquina. Rode: {COMANDO}")
        return 1
    estado = json.loads(STATE.read_text(encoding="utf-8"))
    if not estado.get("ok"):
        print(f"[unity] A última validação FALHOU ({estado.get('quando')}). Corrija e rode: {COMANDO}")
        return 1

    validado = datetime.fromisoformat(estado["quando"]).timestamp()
    editados = [(os.path.getmtime(ROOT / a), a) for a in arquivos if (ROOT / a).exists()]
    if not editados:
        return 0
    ultima, arquivo = max(editados)
    if ultima > validado:
        print(f"[unity] {arquivo} foi editado depois da última validação ({estado['quando']}). Rode: {COMANDO}")
        return 1

    print(f"[unity] OK — {len(editados)} script(s) validados em {estado['quando']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
