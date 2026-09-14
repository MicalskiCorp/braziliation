"""Transcreve os audios capturados em _inbox/ e move cada item para _pendente-curadoria/.

Local, sem API — usa faster-whisper (Whisper rodando na propria maquina). Uma pasta de
texto puro (sem audio.ogg) so e movida, sem custo de transcricao. Rodar sob demanda
(ADR-009): nao e um daemon, processa o que estiver pendente e termina.

    pip install -r requirements.txt
    py transcrever.py [--modelo medium] [--device cpu]
"""

import argparse
import shutil
import sys
from pathlib import Path

try:
    from faster_whisper import WhisperModel
except ImportError:
    print("Falta instalar as dependencias: pip install -r requirements.txt", file=sys.stderr)
    raise

ROOT = Path(__file__).resolve().parents[1]
INBOX = ROOT / "_inbox"
PENDENTE = ROOT / "_pendente-curadoria"


def transcrever_pasta(model: "WhisperModel", pasta: Path) -> None:
    audio = pasta / "audio.ogg"
    if audio.exists():
        segments, _info = model.transcribe(str(audio), language="pt")
        texto = " ".join(segment.text.strip() for segment in segments).strip()
        (pasta / "transcricao.txt").write_text(texto, encoding="utf-8")

    destino = PENDENTE / pasta.name
    shutil.move(str(pasta), str(destino))
    print(f"Processado: {pasta.name} -> _pendente-curadoria/")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--modelo", default="medium", help="tiny/base/small/medium/large-v3 (padrao: medium)")
    parser.add_argument("--device", default="cpu", help="cpu ou cuda (padrao: cpu)")
    args = parser.parse_args()

    PENDENTE.mkdir(exist_ok=True)
    pendentes = [p for p in INBOX.iterdir() if p.is_dir()] if INBOX.exists() else []
    if not pendentes:
        print("Nada novo em _inbox/.")
        return

    compute_type = "int8" if args.device == "cpu" else "float16"
    model = WhisperModel(args.modelo, device=args.device, compute_type=compute_type)

    for pasta in pendentes:
        try:
            transcrever_pasta(model, pasta)
        except Exception as exc:  # noqa: BLE001 - relata e segue para a proxima pasta
            print(f"Falhou em {pasta.name}: {exc}", file=sys.stderr)


if __name__ == "__main__":
    main()
