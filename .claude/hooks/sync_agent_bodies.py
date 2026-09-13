"""
PostToolUse: editou um agente em .claude/agents/? Propaga o corpo para o par Copilot.

Por que existe: o corpo dos 11 agentes é o mesmo nos dois formatos, e a sincronia
dependia de lembrar de rodar `sync_bodies.py`. Esquecer só aparecia no AgentParityTests,
no commit. Agora a cópia acontece no mesmo instante da edição — zero passo manual.
"""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SYNC = ROOT / ".claude" / "skills" / "novo-agente" / "sync_bodies.py"


def main() -> None:
    data = json.load(sys.stdin)
    path = (data.get("tool_input", {}).get("file_path", "")
            or data.get("tool_response", {}).get("filePath", "")).replace("\\", "/")
    if "/.claude/agents/" not in path or not path.endswith(".md"):
        return

    result = subprocess.run(
        [sys.executable, str(SYNC)], cwd=ROOT, capture_output=True,
        text=True, encoding="utf-8", errors="replace", env={"PYTHONIOENCODING": "utf-8", **__import__("os").environ},
    )
    saida = (result.stdout + result.stderr).strip()
    if result.returncode != 0 or not saida.startswith("0 "):
        print(json.dumps({
            "hookSpecificOutput": {
                "hookEventName": "PostToolUse",
                "additionalContext": f"sync_bodies.py (corpo Claude → Copilot): {saida}",
            }
        }))


if __name__ == "__main__":
    main()
