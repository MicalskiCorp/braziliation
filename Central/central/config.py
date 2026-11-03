"""Caminhos e limites da Central. Tudo pode ser trocado por variável de ambiente (os testes usam)."""
import os
import shutil
import subprocess
from pathlib import Path

CENTRAL = Path(__file__).resolve().parents[1]
RAIZ = CENTRAL.parent
ESTADO = Path(os.environ.get("CENTRAL_ESTADO", CENTRAL / ".estado"))

HOST = "127.0.0.1"
PORTA = int(os.environ.get("CENTRAL_PORTA", "8765"))

# Processos de agente vivos ao mesmo tempo. Cada claude.exe ocupa algumas centenas de MB.
MAX_PARALELO = int(os.environ.get("CENTRAL_MAX_PARALELO", "3"))
# Execução esperando resposta há mais que isso tem o processo fechado; a resposta o retoma.
INATIVIDADE_MIN = int(os.environ.get("CENTRAL_INATIVIDADE_MIN", "20"))

# Os servidores de build do dotnet prendem arquivos do worktree e impedem a remoção
# (medido em 2026-11-03). Toda checagem e todo commit da Central rodam sem eles.
ENV_SEM_SERVIDOR_DE_BUILD = {
    "MSBUILDDISABLENODEREUSE": "1",
    "DOTNET_CLI_USE_MSBUILD_SERVER": "0",
    "UseSharedCompilation": "false",
    "PYTHONIOENCODING": "utf-8",
    "GIT_TERMINAL_PROMPT": "0",
}


def _garantir_ferramentas() -> None:
    """Põe git e claude no PATH deste processo (e, portanto, dos agentes e hooks que ele abre).

    Nesta máquina o Git for Windows não está no PATH do sistema — o VS Code e o Git Bash o acham
    sozinhos, a tarefa agendada não. Sem isto a primeira execução pela tarefa falhava com
    "[WinError 2] O sistema não pode encontrar o arquivo especificado" (2026-11-03)."""
    extras = []
    if not shutil.which("git"):
        for base in (Path(os.environ.get("ProgramFiles", r"C:\Program Files")) / "Git",
                     Path(os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)")) / "Git",
                     Path.home() / "AppData" / "Local" / "Programs" / "Git"):
            if (base / "cmd" / "git.exe").exists():
                extras.append(str(base / "cmd"))          # git.exe e git-lfs.exe
                bash = base / "bin" / "bash.exe"
                if bash.exists():
                    os.environ.setdefault("CLAUDE_CODE_GIT_BASH_PATH", str(bash))
                break
    local_bin = Path.home() / ".local" / "bin"
    if not shutil.which("claude") and local_bin.exists():
        extras.append(str(local_bin))
    if extras:
        os.environ["PATH"] = os.pathsep.join(extras + [os.environ.get("PATH", "")])


_garantir_ferramentas()


def ferramentas() -> dict:
    """Qual executável a Central está usando — aparece na página Saúde."""
    return {nome: shutil.which(nome) or "" for nome in ("git", "git-lfs", "claude", "py", "dotnet")} | {
        "claude (usado)": claude_exe()}


# Variáveis com que o git aponta um repositório para os filhos dele. Rodando dentro de um hook (o
# pre-commit roda os testes da Central), `GIT_INDEX_FILE=.git/index` vazava para o `git worktree
# add` dos repositórios de teste e quebrava 14 testes (2026-11-03). Toda chamada da Central já diz
# o diretório; herdar essas variáveis só pode apontar para o repositório errado.
GIT_DO_CHAMADOR = ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_COMMON_DIR", "GIT_PREFIX",
                   "GIT_OBJECT_DIRECTORY", "GIT_ALTERNATE_OBJECT_DIRECTORIES")


def ambiente(extra: dict | None = None) -> dict:
    env = {k: v for k, v in os.environ.items() if k.upper() not in GIT_DO_CHAMADOR}
    env.update(ENV_SEM_SERVIDOR_DE_BUILD)
    if extra:
        env.update(extra)
    return env


def claude_exe() -> str:
    candidato = os.environ.get("CENTRAL_CLAUDE") or shutil.which("claude")
    if candidato:
        return candidato
    return str(Path.home() / ".local" / "bin" / ("claude.exe" if os.name == "nt" else "claude"))


def python_do_projeto() -> list[str]:
    """O interpretador que as skills usam (`py` no Windows, com Pillow)."""
    if shutil.which("py"):
        return ["py"]
    return [shutil.which("python3") or shutil.which("python") or "python"]


def pasta_worktrees(raiz: Path) -> Path:
    """Worktrees das execuções isoladas: dentro do .git comum, invisíveis para Unity, VS Code e testes."""
    r = subprocess.run(["git", "rev-parse", "--path-format=absolute", "--git-common-dir"],
                       cwd=raiz, capture_output=True, text=True, encoding="utf-8", env=ambiente())
    comum = Path(r.stdout.strip()) if r.returncode == 0 and r.stdout.strip() else raiz / ".git"
    return comum / "central" / "wt"


SEM_JANELA = 0x08000000 if os.name == "nt" else 0   # CREATE_NO_WINDOW
