import json
import os
import subprocess
import sys

HOOKS_DIR = os.path.dirname(os.path.abspath(__file__))
CSPROJ = os.path.join(
    HOOKS_DIR, "..", "..", "Desenvolvimento", "src",
    "Braziliation.Game.Core", "Braziliation.Game.Core.csproj",
)


def main() -> None:
    data = json.load(sys.stdin)
    path = data.get("tool_input", {}).get("file_path", "") or data.get("tool_response", {}).get("filePath", "")
    path = path.replace("\\", "/")
    if "src/Braziliation.Game.Core" not in path or not path.endswith(".cs"):
        return

    result = subprocess.run(
        ["dotnet", "build", CSPROJ, "--nologo", "-v", "quiet"],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        tail = (result.stdout[-3000:] + "\n" + result.stderr[-2000:]).strip()
        print(json.dumps({
            "hookSpecificOutput": {
                "hookEventName": "PostToolUse",
                "additionalContext": "dotnet build falhou apos editar Braziliation.Game.Core:\n" + tail,
            }
        }))


if __name__ == "__main__":
    main()
