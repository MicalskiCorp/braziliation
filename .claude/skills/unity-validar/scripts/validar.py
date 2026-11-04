#!/usr/bin/env python3
"""Compila o projeto Unity em batchmode e, com --testes, roda os testes EditMode.

Uso:
  py .claude/skills/unity-validar/scripts/validar.py           # compila (padrão)
  py .claude/skills/unity-validar/scripts/validar.py --testes  # compila + EditMode

Licença: a compilação acontece durante o carregamento do projeto e funciona com a licença
Personal gerenciada pelo Unity Hub. Rodar testes exige uma licença **ativada na máquina**
(Hub → Preferences → Licenses → Add → licença Personal); sem ela o Editor sai com 198
"No valid Unity Editor license found" — com ou sem -batchmode, com ou sem a CLI oficial.

Variável opcional UNITY_EXE aponta outro executável; sem ela, usa o editor do Hub na
versão de ProjectSettings/ProjectVersion.txt.

Editor aberto com o projeto: o batchmode não pode abrir o mesmo projeto, então a validação
roda no próprio Editor pela CLI oficial `unity` (recompile → recompile_status, e run_tests
com --testes). Por quê: até 2026-11-04 o script só recusava, o agente validava à mão pela
CLI, nada era gravado e o pre-commit barrava o commit da Central (duas vezes no mesmo dia).

Sai com 0 se compilou (e, com --testes, se todos passaram), 1 caso contrário.
Grava o resumo em .claude/state/unity-validar.json e, no batchmode, o log em
.claude/state/unity-validar.log.
"""
import argparse
import datetime as dt
import json
import os
import re
import shutil
import subprocess
import sys
import time
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
PROJECT = ROOT / "Desenvolvimento"
STATE_DIR = ROOT / ".claude" / "state"
TIMEOUT_S = 30 * 60
LICENCA_RECUSADA = "No valid Unity Editor license found"


def unity_exe() -> Path:
    override = os.environ.get("UNITY_EXE")
    if override:
        return Path(override)
    version_file = (PROJECT / "ProjectSettings" / "ProjectVersion.txt").read_text(encoding="utf-8")
    version = re.search(r"m_EditorVersion:\s*(\S+)", version_file).group(1)
    return Path(rf"C:\Program Files\Unity\Hub\Editor\{version}\Editor\Unity.exe")


def editor_aberto() -> bool:
    """O Editor mantém Temp/UnityLockfile aberto com trava exclusiva enquanto o projeto está aberto."""
    lock = PROJECT / "Temp" / "UnityLockfile"
    if not lock.exists():
        return False
    try:
        with open(lock, "r+b"):
            return False
    except PermissionError:
        return True


def erros_de_compilacao(log: str) -> list[str]:
    vistos, erros = set(), []
    for match in re.finditer(r"^(.*?\(\d+,\d+\)): error (CS\d+): (.*)$", log, re.MULTILINE):
        linha = f"{match.group(1).strip()}: error {match.group(2)}: {match.group(3).strip()}"
        if linha not in vistos:
            vistos.add(linha)
            erros.append(linha)
    return erros


def ler_resultados(xml_path: Path) -> dict | None:
    if not xml_path.exists():
        return None
    root = ET.parse(xml_path).getroot()
    falhas = []
    for case in root.iter("test-case"):
        if case.get("result") == "Failed":
            mensagem = case.findtext("failure/message", default="").strip().splitlines()
            falhas.append({"teste": case.get("fullname"), "mensagem": mensagem[0] if mensagem else ""})
    return {
        "total": int(root.get("total", 0)),
        "passaram": int(root.get("passed", 0)),
        "falharam": int(root.get("failed", 0)),
        "falhas": falhas,
    }


def unity_cli(comando: list[str], timeout_s: int = 60) -> dict | None:
    """Roda `unity command <comando>` no Editor aberto e devolve o `result` como dict.

    None quando a CLI não responde — inclusive durante o domain reload que segue uma
    compilação, quando o Editor some por alguns segundos.
    """
    exe = shutil.which("unity")
    if not exe:
        return None
    cmd = [exe, "--json", "--no-banner", "--no-pager", "--non-interactive", "command",
           "--project-path", str(PROJECT), "--timeout", str(timeout_s), *comando]
    try:
        r = subprocess.run(cmd, capture_output=True, timeout=timeout_s + 30)
        saida = json.loads(r.stdout.decode("utf-8", "replace"))
    except (OSError, subprocess.TimeoutExpired, ValueError):
        return None
    dados = saida.get("data") if isinstance(saida, dict) and saida.get("success") else None
    resultado = dados.get("result") if isinstance(dados, dict) else None
    if isinstance(resultado, str):  # recompile_status devolve o JSON serializado numa string
        try:
            resultado = json.loads(resultado)
        except ValueError:
            return None
    return resultado if isinstance(resultado, dict) else None


def validar_no_editor(testes_pedidos: bool) -> dict | None:
    """Compila (e testa) no Editor aberto. None se o Editor não respondeu: nada é gravado."""
    if not shutil.which("unity"):
        print("ERRO: o Unity Editor está aberto com este projeto e a CLI oficial `unity` não está no PATH. "
              "Feche o Editor e rode de novo.")
        return None
    print("Editor aberto · validando no próprio Editor pela CLI `unity`...", flush=True)
    inicio = time.time()

    # O recompile faz um refresh do AssetDatabase antes (RefreshV2 no Editor.log), então
    # pega .cs novos ou editados fora do Editor. "up_to_date" = nada mudou desde a última
    # compilação; as flags de falha dizem se essa compilação passou.
    if unity_cli(["recompile"]) is None:
        print("ERRO: o Editor não respondeu ao `unity command recompile` (ver `unity status`). Nada foi gravado.")
        return None
    # Só os estados finais encerram a espera: durante "compiling" as flags failed e
    # compilationFailed ainda são as da compilação ANTERIOR (medido: falha antiga lida como
    # se fosse a nova). Uma compilação que falha termina em "completed" com failed=true.
    status = {}
    limite = time.time() + 10 * 60
    while time.time() < limite:
        status = unity_cli(["recompile_status"]) or {}
        if status.get("status") in ("completed", "up_to_date"):
            break
        time.sleep(3)
    else:
        print("ERRO: a compilação no Editor não terminou em 10 min. Nada foi gravado.")
        return None

    # Depois do "completed" vem o domain reload: o Editor some por alguns segundos e
    # compilationFailed só se atualiza no fim dele (medido: completed com failed=false e
    # compilationFailed=true por ~6 s depois de corrigir um erro). Espera o Editor assentar
    # — console respondendo, sem compilar, e as duas flags concordando. Se não concordarem
    # em 90 s, vale a leitura final, que pende para FALHOU.
    console = {}
    limite = time.time() + 90
    while time.time() < limite:
        console = (unity_cli(["console_status"]) or {}).get("groundTruth") or {}
        status = unity_cli(["recompile_status"]) or status
        if (console and not console.get("compiling")
                and status.get("status") in ("completed", "up_to_date")
                and bool(status.get("failed")) == bool(status.get("compilationFailed"))):
            break
        time.sleep(3)

    erros = [e if isinstance(e, str) else json.dumps(e, ensure_ascii=False) for e in status.get("errors") or []]
    compilou = not (erros or status.get("failed") or status.get("compilationFailed")
                    or console.get("compilationFailed"))

    testes = None
    if testes_pedidos and compilou:
        resultado = unity_cli(["run_tests", "--mode", "EditMode"], timeout_s=TIMEOUT_S)
        sumario = (resultado or {}).get("Summary")
        if sumario:
            testes = {
                "total": int(sumario.get("Total", 0)),
                "passaram": int(sumario.get("Passed", 0)),
                "falharam": int(sumario.get("Failed", 0)),
                "falhas": [{"teste": r.get("FullName"), "mensagem": (r.get("Message") or "").strip().split("\n")[0]}
                           for r in resultado.get("Results") or [] if r.get("Status") == "Failed"],
            }

    ok = compilou and (not testes_pedidos or (testes is not None and testes["falharam"] == 0))
    return {
        "via": "editor-aberto",
        "ok": ok,
        "compilou": compilou,
        "codigo_saida": 0 if ok else 1,
        "licenca_recusada": False,
        "duracao_s": round(time.time() - inicio),
        "erros_compilacao": erros,
        "testes": testes,
    }


def validar_em_batchmode(exe: Path, testes_pedidos: bool) -> dict:
    log_path = STATE_DIR / "unity-validar.log"
    xml_path = STATE_DIR / "unity-validar-editmode.xml"
    xml_path.unlink(missing_ok=True)

    # Sem -nographics de propósito: com ele o Editor pede o entitlement
    # 'com.unity.editor.headless' (licença de build server). -batchmode já roda sem janela.
    cmd = [str(exe), "-batchmode", "-projectPath", str(PROJECT), "-logFile", str(log_path)]
    if testes_pedidos:
        cmd += ["-runTests", "-testPlatform", "EditMode", "-testResults", str(xml_path)]
    else:
        cmd.append("-quit")

    print(f"Unity {exe.parent.parent.name} · batchmode · pode levar alguns minutos...", flush=True)
    inicio = time.time()
    try:
        codigo = subprocess.run(cmd, timeout=TIMEOUT_S).returncode
    except subprocess.TimeoutExpired:
        codigo = -1

    log = log_path.read_text(encoding="utf-8", errors="replace") if log_path.exists() else ""
    erros = erros_de_compilacao(log)
    compilou = not erros and "Scripts have compiler errors" not in log and codigo != -1
    testes = ler_resultados(xml_path) if testes_pedidos else None

    if testes_pedidos:
        ok = compilou and testes is not None and testes["falharam"] == 0
    else:
        ok = compilou and codigo == 0

    return {
        "via": "batchmode",
        "ok": ok,
        "compilou": compilou,
        "codigo_saida": codigo,
        "licenca_recusada": LICENCA_RECUSADA in log and codigo == 198,
        "duracao_s": round(time.time() - inicio),
        "erros_compilacao": erros,
        "testes": testes,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--testes", action="store_true",
                        help="também roda os testes EditMode (exige licença ativada na máquina)")
    args = parser.parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    # Carimbo do INÍCIO, não do fim: o pre-commit aceita todo .cs com mtime anterior a ele,
    # e um arquivo salvo durante a validação pode não ter entrado na compilação.
    quando = dt.datetime.now().isoformat(timespec="seconds")

    if editor_aberto():
        resultado = validar_no_editor(args.testes)
        if resultado is None:
            return 1
    else:
        exe = unity_exe()
        if not exe.exists():
            print(f"ERRO: Unity não encontrado em {exe}. Instale a versão do ProjectVersion.txt pelo Hub ou defina UNITY_EXE.")
            return 1
        STATE_DIR.mkdir(parents=True, exist_ok=True)
        resultado = validar_em_batchmode(exe, args.testes)

    resumo = {"quando": quando, "modo": "testes" if args.testes else "compilar", **resultado}
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    (STATE_DIR / "unity-validar.json").write_text(json.dumps(resumo, indent=2, ensure_ascii=False), encoding="utf-8")

    ok, codigo, erros, testes = resumo["ok"], resumo["codigo_saida"], resumo["erros_compilacao"], resumo["testes"]
    print(f"{'OK' if ok else 'FALHOU'} em {resumo['duracao_s']}s ({resumo['via']}, código {codigo})")
    if codigo == -1:
        print(f"  Tempo esgotado ({TIMEOUT_S // 60} min).")
    if erros:
        print(f"  {len(erros)} erro(s) de compilação:")
        for erro in erros[:30]:
            print(f"    {erro}")
    elif resumo["compilou"]:
        print("  Compilação sem erros.")
    else:
        print("  Falha sem erro CS listado — "
              + ("ver .claude/state/unity-validar.log" if resumo["via"] == "batchmode" else "ver o Console do Editor"))
    if testes is not None:
        print(f"  EditMode: {testes['passaram']}/{testes['total']} passaram")
        for falha in testes["falhas"]:
            print(f"    FALHOU {falha['teste']}: {falha['mensagem']}")
    elif args.testes and resumo["licenca_recusada"]:
        print("  Testes não rodaram: não há licença Unity ativada nesta máquina para o Editor aberto por linha de comando.")
        print("  Ativar uma vez: Unity Hub → Preferences → Licenses → Add → 'Get a free personal license'")
        print("  (ou `unity license activate` na CLI oficial). A compilação acima continua valendo.")
    elif args.testes and resumo["compilou"]:
        print("  Sem resultado de teste — "
              + ("ver .claude/state/unity-validar.log" if resumo["via"] == "batchmode" else "ver o Test Runner do Editor"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
