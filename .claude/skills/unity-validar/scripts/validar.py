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

Sai com 0 se compilou (e, com --testes, se todos passaram), 1 caso contrário.
Grava o resumo em .claude/state/unity-validar.json e o log em .claude/state/unity-validar.log.
"""
import argparse
import datetime as dt
import json
import os
import re
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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--testes", action="store_true",
                        help="também roda os testes EditMode (exige licença ativada na máquina)")
    args = parser.parse_args()

    exe = unity_exe()
    if not exe.exists():
        print(f"ERRO: Unity não encontrado em {exe}. Instale a versão do ProjectVersion.txt pelo Hub ou defina UNITY_EXE.")
        return 1
    if editor_aberto():
        print("ERRO: o Unity Editor está aberto com este projeto. Feche o Editor e rode de novo "
              "(ou use a CLI oficial `unity status` para agir no Editor aberto).")
        return 1

    STATE_DIR.mkdir(parents=True, exist_ok=True)
    log_path = STATE_DIR / "unity-validar.log"
    xml_path = STATE_DIR / "unity-validar-editmode.xml"
    xml_path.unlink(missing_ok=True)

    # Sem -nographics de propósito: com ele o Editor pede o entitlement
    # 'com.unity.editor.headless' (licença de build server). -batchmode já roda sem janela.
    cmd = [str(exe), "-batchmode", "-projectPath", str(PROJECT), "-logFile", str(log_path)]
    modo = "testes" if args.testes else "compilar"
    if args.testes:
        cmd += ["-runTests", "-testPlatform", "EditMode", "-testResults", str(xml_path)]
    else:
        cmd.append("-quit")

    print(f"Unity {exe.parent.parent.name} · modo {modo} · pode levar alguns minutos...", flush=True)
    inicio = time.time()
    try:
        codigo = subprocess.run(cmd, timeout=TIMEOUT_S).returncode
    except subprocess.TimeoutExpired:
        codigo = -1
    duracao = round(time.time() - inicio)

    log = log_path.read_text(encoding="utf-8", errors="replace") if log_path.exists() else ""
    erros = erros_de_compilacao(log)
    compilou = not erros and "Scripts have compiler errors" not in log and codigo != -1
    licenca_recusada = LICENCA_RECUSADA in log and codigo == 198
    testes = ler_resultados(xml_path) if args.testes else None

    if args.testes:
        ok = compilou and testes is not None and testes["falharam"] == 0
    else:
        ok = compilou and codigo == 0

    resumo = {
        "quando": dt.datetime.now().isoformat(timespec="seconds"),
        "modo": modo,
        "ok": ok,
        "compilou": compilou,
        "codigo_saida": codigo,
        "licenca_recusada": licenca_recusada,
        "duracao_s": duracao,
        "erros_compilacao": erros,
        "testes": testes,
    }
    (STATE_DIR / "unity-validar.json").write_text(json.dumps(resumo, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"{'OK' if ok else 'FALHOU'} em {duracao}s (código {codigo})")
    if codigo == -1:
        print(f"  Tempo esgotado ({TIMEOUT_S // 60} min).")
    if erros:
        print(f"  {len(erros)} erro(s) de compilação:")
        for erro in erros[:30]:
            print(f"    {erro}")
    elif compilou:
        print("  Compilação sem erros.")
    if testes is not None:
        print(f"  EditMode: {testes['passaram']}/{testes['total']} passaram")
        for falha in testes["falhas"]:
            print(f"    FALHOU {falha['teste']}: {falha['mensagem']}")
    elif args.testes and licenca_recusada:
        print("  Testes não rodaram: não há licença Unity ativada nesta máquina para o Editor aberto por linha de comando.")
        print("  Ativar uma vez: Unity Hub → Preferences → Licenses → Add → 'Get a free personal license'")
        print("  (ou `unity license activate` na CLI oficial). A compilação acima continua valendo.")
    elif args.testes:
        print("  Sem arquivo de resultados de teste — ver .claude/state/unity-validar.log")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
