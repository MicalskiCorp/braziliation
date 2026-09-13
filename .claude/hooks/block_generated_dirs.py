import json
import os
import sys
from pathlib import PurePath

# Pastas geradas pelo Unity/.NET dentro do projeto. Comparação por segmento de
# caminho, sem diferenciar maiúsculas (Windows).
GENERATED_DIRS = {"library", "temp", "obj", "bin"}


def is_generated(path: str, project_dir: str) -> bool:
    """
    Só bloqueia pastas geradas **do projeto**. A versão anterior casava a regex
    em qualquer lugar do caminho absoluto, e com isso bloqueava também o temp do
    sistema (C:\\Users\\...\\AppData\\Local\\Temp\\...), onde vivem scratchpads.
    """
    try:
        rel = os.path.relpath(os.path.abspath(path), os.path.abspath(project_dir))
    except ValueError:
        # Outro drive no Windows: com certeza fora do projeto.
        return False

    parts = PurePath(rel).parts
    if not parts or parts[0] == os.pardir:
        return False

    return any(part.lower() in GENERATED_DIRS for part in parts[:-1])


def main() -> None:
    data = json.load(sys.stdin)
    path = data.get("tool_input", {}).get("file_path", "")
    project_dir = os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()

    if path and is_generated(path, project_dir):
        print(json.dumps({
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": f"Diretorio gerado (Unity/.NET), nao editar: {path}",
            }
        }))


if __name__ == "__main__":
    main()
