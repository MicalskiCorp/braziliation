import json
import os
import sys
from pathlib import PurePath

# Pastas geradas pelo Unity/.NET dentro do projeto. Comparação por segmento de
# caminho, sem diferenciar maiúsculas (Windows).
GENERATED_DIRS = {"library", "temp", "obj", "bin"}

# Arquivos que o projeto declara congelados: regra escrita que agora é trava.
# TODO-arquivo.md é o histórico até 2026-09-13; a DLL do core é saída do build
# (edite a fonte em src/Braziliation.Game.Core/).
FROZEN = {
    "desenvolvimento/docs/todo-arquivo.md": "histórico congelado — pendência nova vai no TODO.md",
}
FROZEN_SUFFIX = {
    ("desenvolvimento/assets/plugins/braziliation/", ".dll"): "saída do build do Braziliation.Game.Core — edite a fonte em src/",
}


def relative(path: str, project_dir: str):
    try:
        rel = os.path.relpath(os.path.abspath(path), os.path.abspath(project_dir))
    except ValueError:
        # Outro drive no Windows: com certeza fora do projeto.
        return None
    parts = PurePath(rel).parts
    if not parts or parts[0] == os.pardir:
        return None
    return parts


def blocked_reason(path: str, project_dir: str):
    """
    Só bloqueia pastas geradas **do projeto**. Uma versão antiga casava a regex em
    qualquer lugar do caminho absoluto, e com isso bloqueava também o temp do sistema
    (C:\\Users\\...\\AppData\\Local\\Temp\\...), onde vivem scratchpads.
    """
    parts = relative(path, project_dir)
    if parts is None:
        return None
    if any(part.lower() in GENERATED_DIRS for part in parts[:-1]):
        return "Diretorio gerado (Unity/.NET), nao editar"
    rel = "/".join(parts).lower()
    if rel in FROZEN:
        return f"Arquivo congelado: {FROZEN[rel]}"
    for (prefix, suffix), reason in FROZEN_SUFFIX.items():
        if rel.startswith(prefix) and rel.endswith(suffix):
            return f"Arquivo congelado: {reason}"
    return None


def main() -> None:
    data = json.load(sys.stdin)
    path = data.get("tool_input", {}).get("file_path", "")
    project_dir = os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()

    reason = blocked_reason(path, project_dir) if path else None
    if reason:
        print(json.dumps({
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": f"{reason}: {path}",
            }
        }))


if __name__ == "__main__":
    main()
