"""
SessionStart: injeta no contexto a foto atual do projeto.

Por que existe: agentes começavam sessões com números velhos escritos em Markdown
(o CLAUDE.md chegou a dizer "154 testes" quando eram 187). Esta foto é calculada na
hora a partir do git, dos TODOs e do último resultado da skill unity-validar — nada
aqui é escrito à mão, então não envelhece.

Tem de ser rápido (roda em toda sessão): só git e leitura de arquivos, sem build.
"""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
# Conta pelo parser único dos TODOs (ADR-012): antes este hook tinha um leitor próprio que
# discordava do `todo.py` — 31 contra 29 pendências Alta no Criativo em 2026-11-03.
sys.path.insert(0, str(ROOT / ".claude" / "skills" / "gerir-todo"))
import todo_md  # noqa: E402

TODOS = list(todo_md.CAMADAS.values())
UNITY_STATE = ROOT / ".claude" / "state" / "unity-validar.json"


def git(*args: str) -> str:
    try:
        result = subprocess.run(
            ["git", *args], cwd=ROOT, capture_output=True, text=True,
            encoding="utf-8", errors="replace", timeout=10,
        )
        return result.stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return ""


def pendencias_alta(relativo: str) -> int:
    try:
        doc = todo_md.ler(ROOT / relativo)
    except (OSError, UnicodeDecodeError):
        return 0
    return sum(1 for i in doc.itens(so_abertos=True) if i.prioridade == "Alta")


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    linhas = ["## Foto do projeto (calculada no início desta sessão)"]
    linhas.append(f"- Branch `{git('rev-parse', '--abbrev-ref', 'HEAD')}` · último commit: {git('log', '-1', '--format=%h %s (%cr)')}")

    contagem = git("rev-list", "--left-right", "--count", "@{u}...HEAD")
    if contagem:
        atras, frente = contagem.split()
        linhas.append(f"- Remoto: {frente} commit(s) à frente, {atras} atrás")

    alterados = [l for l in git("status", "--porcelain").splitlines() if l.strip()]
    linhas.append("- Working tree limpo" if not alterados else f"- {len(alterados)} arquivo(s) alterado(s) sem commit")

    for todo in TODOS:
        linhas.append(f"- `{todo}`: {pendencias_alta(todo)} pendência(s) Alta em aberto")

    if UNITY_STATE.exists():
        try:
            estado = json.loads(UNITY_STATE.read_text(encoding="utf-8"))
            testes = estado.get("testes") or {}
            detalhe = f", EditMode {testes.get('passaram', 0)}/{testes.get('total', 0)}" if testes else ""
            linhas.append(
                f"- Última `unity-validar` ({estado.get('quando', '?')}): "
                f"{'OK' if estado.get('ok') else 'FALHOU'}{detalhe}"
            )
        except (ValueError, OSError):
            pass
    else:
        linhas.append("- `unity-validar` nunca rodou nesta máquina — o lado Unity não tem validação registrada")

    if git("config", "--get", "core.hooksPath") != ".githooks":
        linhas.append("- ⚠ Pre-commit desativado neste clone: rode `git config core.hooksPath .githooks`")

    print("\n".join(linhas))


if __name__ == "__main__":
    main()
