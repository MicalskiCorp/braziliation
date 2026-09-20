#!/usr/bin/env python3
"""Roda os gates de repositório contra o que o git realmente tem, não contra o disco.

Por que existe
--------------
Em 13 set 2026 duas pastas de arte ficaram vazias (`Assets/Art/Characters/` e
`Assets/Art/Props/`). O git não versiona pasta vazia, mas os `.meta` delas continuaram
versionados — então em qualquer checkout limpo a pasta não existe e o `.meta` fica órfão.
O CI reprovou em todos os pushes seguintes; o `meta-check` local passou o tempo todo,
porque na máquina do desenvolvedor as pastas existem no disco. Seis dias de CI vermelho
sem que nenhuma trava local tivesse como perceber.

A diferença entre o disco de quem trabalha e um checkout limpo é o ponto cego: pasta
vazia, arquivo ignorado, artefato gerado que só existe localmente. Este script fecha a
diferença materializando o **índice** do git — exatamente o que o commit vai conter — e
rodando os gates contra essa cópia.

Os gates rodam a partir da **cópia**, não da árvore de trabalho: assim a versão commitada
dos próprios scripts de gate é que decide, e um gate quebrado no commit também aparece.

Uso:
  py .claude/skills/meta-check/check_clean_checkout.py
  py .claude/skills/meta-check/check_clean_checkout.py --gates meta
  py .claude/skills/meta-check/check_clean_checkout.py --keep    # não apaga a cópia

Sai com 0 se todos os gates pedidos passarem, 1 se algum reprovar.
Sem dependências além da stdlib (os gates chamados podem ter as suas).
"""
import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

# Cada gate: nome → (caminho do script dentro da cópia, argumentos)
GATES = {
    "meta": (Path(".claude") / "skills" / "meta-check" / "check_meta_pairs.py", []),
    "paletas": (Path("Design") / "ArteFonte" / "Ferramentas" / "check_art_palettes.py", []),
}


def git_root() -> Path:
    saida = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        capture_output=True, text=True, check=True,
    )
    return Path(saida.stdout.strip())


def materializar(raiz: Path, destino: Path) -> None:
    """
    `git checkout-index -a` escreve a representação de árvore de trabalho de tudo que está
    no índice — com os filtros aplicados, então arquivo de LFS sai como binário de verdade
    (desde que o objeto esteja em .git/lfs/objects). O prefixo precisa terminar em barra.
    """
    prefixo = destino.as_posix().rstrip("/") + "/"
    subprocess.run(
        ["git", "checkout-index", "-a", "--prefix=" + prefixo],
        cwd=raiz, check=True, capture_output=True, text=True,
    )


def rodar_gate(nome: str, copia: Path) -> bool:
    script, extras = GATES[nome]
    caminho = copia / script
    if not caminho.is_file():
        print(f"[{nome}] REPROVADO — {script.as_posix()} não está no índice do git.")
        return False

    # cwd = raiz da cópia: os gates resolvem caminhos relativos a partir dela, e o
    # check_art_palettes deriva a raiz do próprio local do arquivo (parents[3]).
    resultado = subprocess.run(
        [sys.executable, str(caminho), *extras],
        cwd=copia, capture_output=True, text=True,
    )
    saida = (resultado.stdout + resultado.stderr).strip()
    ok = resultado.returncode == 0
    print(f"[{nome}] {'APROVADO' if ok else 'REPROVADO'}")
    if not ok and saida:
        for linha in saida.splitlines():
            print("    " + linha)
    return ok


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--gates", default=",".join(GATES),
                    help="gates a rodar, separados por vírgula (padrão: todos)")
    ap.add_argument("--keep", action="store_true",
                    help="não apagar a cópia — imprime o caminho para inspeção")
    args = ap.parse_args()

    pedidos = [g.strip() for g in args.gates.split(",") if g.strip()]
    desconhecidos = [g for g in pedidos if g not in GATES]
    if desconhecidos:
        print(f"ERRO: gate desconhecido: {', '.join(desconhecidos)}. "
              f"Disponíveis: {', '.join(GATES)}")
        return 1

    raiz = git_root()
    destino = Path(tempfile.mkdtemp(prefix="braziliation-checkout-"))
    copia = destino / "arvore"
    copia.mkdir()

    try:
        print(f"Materializando o índice do git ({', '.join(pedidos)})...")
        try:
            materializar(raiz, copia)
        except subprocess.CalledProcessError as erro:
            # Causa mais provável: objeto de LFS ausente em .git/lfs/objects (clone raso
            # ou `git lfs pull` nunca rodado) — o filtro de smudge falha e o checkout-index
            # aborta. Não é motivo para reprovar o commit: é ambiente incompleto.
            print("AVISO: não foi possível materializar o índice — gates não rodaram.")
            detalhe = (erro.stderr or erro.stdout or "").strip()
            for linha in detalhe.splitlines()[:10]:
                print("    " + linha)
            print("    Se houver arquivo de LFS ausente, rode `git lfs pull` e repita.")
            return 0

        resultados = [rodar_gate(nome, copia) for nome in pedidos]

        if all(resultados):
            print("\nAPROVADO — o que está no índice passa nos gates de um checkout limpo.")
            return 0
        print("\nREPROVADO — o disco local passa, mas o commit não passaria no CI. "
              "Causa comum: pasta que ficou vazia e cujo .meta continua versionado "
              "(git não versiona pasta vazia — acrescente um .gitkeep).")
        return 1
    finally:
        if args.keep:
            print(f"\nCópia mantida em: {copia}")
        else:
            shutil.rmtree(destino, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
