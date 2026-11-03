"""Git das execuções: worktree, diff, descarte, commit pelo pre-commit e integração no main.

Nunca `--no-verify`, nunca push (ADR-012).
"""
from __future__ import annotations

import shutil
import subprocess
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path

from . import config

LIMITE_PATCH = 200_000


class ErroGit(Exception):
    pass


@dataclass
class Saida:
    codigo: int
    texto: str

    @property
    def ok(self) -> bool:
        return self.codigo == 0


def git(cwd: Path, *args: str, timeout: int = 600) -> Saida:
    r = subprocess.run(["git", *args], cwd=cwd, capture_output=True, timeout=timeout,
                       env=config.ambiente(), creationflags=config.SEM_JANELA)
    texto = (r.stdout + r.stderr).decode("utf-8", "replace")
    return Saida(r.returncode, texto.strip())


def exigir(saida: Saida, acao: str) -> str:
    if not saida.ok:
        raise ErroGit(f"{acao} falhou: {saida.texto[-1500:]}")
    return saida.texto


def head(cwd: Path) -> str:
    return exigir(git(cwd, "rev-parse", "HEAD"), "rev-parse")


def branch(cwd: Path) -> str:
    return exigir(git(cwd, "rev-parse", "--abbrev-ref", "HEAD"), "rev-parse")


def alteracoes(cwd: Path) -> list[tuple[str, str]]:
    """(código XY do porcelain, caminho) de tudo que difere do HEAD, inclusive arquivo novo.
    Renomeação vira duas linhas: o caminho novo como "A " e o antigo como " D"."""
    r = subprocess.run(["git", "status", "--porcelain=v1", "-z", "--untracked-files=all"], cwd=cwd,
                       capture_output=True, env=config.ambiente(), creationflags=config.SEM_JANELA)
    if r.returncode != 0:
        raise ErroGit(r.stderr.decode("utf-8", "replace"))
    partes = r.stdout.decode("utf-8", "replace").split("\0")
    saida, i = [], 0
    while i < len(partes):
        p = partes[i]
        i += 1
        if not p:
            continue
        codigo, caminho = p[:2], p[3:]
        if codigo[0] in "RC" and i < len(partes):
            saida.append(("A ", caminho))
            if codigo[0] == "R":
                saida.append((" D", partes[i]))
            i += 1
            continue
        saida.append((codigo, caminho))
    return saida


def arvore_limpa(cwd: Path) -> bool:
    return not alteracoes(cwd)


def criar_worktree(raiz: Path, destino: Path, nome_branch: str) -> str:
    destino.parent.mkdir(parents=True, exist_ok=True)
    exigir(git(raiz, "worktree", "add", "-q", "-b", nome_branch, str(destino), "HEAD"), "git worktree add")
    return head(destino)


def remover_worktree(raiz: Path, destino: Path, nome_branch: str) -> None:
    for tentativa in range(3):
        r = git(raiz, "worktree", "remove", "--force", str(destino))
        if r.ok or not destino.exists():
            break
        if tentativa == 1:
            # Último recurso: os servidores de build do dotnet seguram arquivo do worktree.
            subprocess.run(["dotnet", "build-server", "shutdown"], capture_output=True,
                           creationflags=config.SEM_JANELA)
        time.sleep(2)
    if destino.exists():
        shutil.rmtree(destino, ignore_errors=True)
    git(raiz, "worktree", "prune")
    git(raiz, "branch", "-D", nome_branch)


def worktrees_registrados(raiz: Path) -> set[str]:
    texto = git(raiz, "worktree", "list", "--porcelain").texto
    return {str(Path(l[9:]).resolve()).lower() for l in texto.splitlines() if l.startswith("worktree ")}


def _binario(caminho: Path) -> bool:
    try:
        with caminho.open("rb") as f:
            return b"\0" in f.read(8000)
    except OSError:
        return False


def diff(cwd: Path) -> list[dict]:
    """Um bloco por arquivo alterado em relação ao HEAD, com o patch quando é texto."""
    arquivos = []
    for codigo, caminho in alteracoes(cwd):
        estado = "novo" if codigo == "??" or "A" in codigo else ("removido" if "D" in codigo else "alterado")
        absoluto = cwd / caminho
        item = {"caminho": caminho, "estado": estado, "patch": "", "binario": False}
        if estado == "novo":
            if absoluto.is_file() and _binario(absoluto):
                item["binario"] = True
            elif absoluto.is_file():
                texto = absoluto.read_text(encoding="utf-8", errors="replace")
                item["patch"] = "".join(f"+{l}\n" for l in texto.splitlines())[:LIMITE_PATCH]
        else:
            r = git(cwd, "diff", "HEAD", "--", caminho)
            if "Binary files" in r.texto[:400] or (absoluto.is_file() and _binario(absoluto)):
                item["binario"] = True
            else:
                item["patch"] = r.texto[:LIMITE_PATCH]
        arquivos.append(item)
    return arquivos


def restaurar(cwd: Path, caminhos: list[str] | None = None) -> None:
    """Desfaz alterações em relação ao HEAD: rastreados voltam, novos (não ignorados) somem."""
    alvo = [(c, p) for c, p in alteracoes(cwd) if caminhos is None or p in caminhos]
    novos = [p for c, p in alvo if c == "??" or c[0] == "A"]
    existentes = [p for c, p in alvo if not (c == "??" or c[0] == "A")]
    preparados = [p for c, p in alvo if c != "??"]
    if preparados:
        exigir(git(cwd, "reset", "-q", "HEAD", "--", *preparados), "git reset")
    if existentes:
        exigir(git(cwd, "checkout", "-q", "HEAD", "--", *existentes), "git checkout")
    for p in novos:
        arquivo = cwd / p
        if arquivo.is_file():
            arquivo.unlink()


def commitar(cwd: Path, caminhos: list[str], mensagem: str) -> Saida:
    """Stage só do que foi aprovado e commit pelo pre-commit do projeto."""
    if not caminhos:
        raise ErroGit("nenhum arquivo selecionado")
    exigir(git(cwd, "reset", "-q"), "git reset")
    exigir(git(cwd, "add", "-A", "--", *caminhos), "git add")
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".txt", delete=False) as f:
        f.write(mensagem.strip() + "\n")
        arquivo_msg = f.name
    try:
        r = git(cwd, "commit", "-F", arquivo_msg, timeout=1800)
    finally:
        Path(arquivo_msg).unlink(missing_ok=True)
    if not r.ok:
        git(cwd, "reset", "-q")
    return r


def integrar(raiz: Path, worktree: Path, nome_branch: str) -> Saida:
    """Leva o commit do worktree para o branch da árvore principal: rebase e fast-forward."""
    alvo = branch(raiz)
    if head(raiz) != git(worktree, "merge-base", "HEAD", alvo).texto:
        r = git(worktree, "rebase", alvo)
        if not r.ok:
            conflitos = git(worktree, "diff", "--name-only", "--diff-filter=U").texto
            git(worktree, "rebase", "--abort")
            return Saida(1, f"conflito ao reaplicar sobre {alvo}: {conflitos or r.texto[-800:]}")
    return git(raiz, "merge", "--ff-only", nome_branch)
