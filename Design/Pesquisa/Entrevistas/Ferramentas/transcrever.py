"""Prepara as capturas de _inbox/ para curadoria e move cada item para _pendente-curadoria/.

Local, sem API. Audio vira texto com faster-whisper (Whisper rodando na propria maquina);
documento com camada de texto (PDF, DOCX, TXT/CSV) e extraido para `texto-documento.txt`.
Imagem e PDF escaneado nao tem extracao automatica — vao inteiros para a curadoria, que
le o arquivo direto no Claude Code. Rodar sob demanda (ADR-009): nao e um daemon, processa
o que estiver pendente e termina.

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

TEXTO_DOCUMENTO = "texto-documento.txt"
# Aviso gravado no lugar do texto quando o arquivo nao tem camada extraivel — a curadoria
# le que precisa abrir o arquivo em vez de achar que o documento veio vazio.
SEM_TEXTO = "[sem camada de texto extraivel — abrir o arquivo direto na curadoria]"


def extrair_pdf(caminho: Path) -> str:
    import pdfplumber

    with pdfplumber.open(str(caminho)) as pdf:
        paginas = [(pagina.extract_text() or "").strip() for pagina in pdf.pages]
    return "\n\n".join(p for p in paginas if p).strip()


def extrair_docx(caminho: Path) -> str:
    import docx

    return "\n".join(p.text for p in docx.Document(str(caminho)).paragraphs).strip()


def extrair_texto_do_documento(pasta: Path) -> None:
    """Grava texto-documento.txt quando o documento capturado tiver texto extraivel."""
    documentos = [p for p in pasta.iterdir() if p.stem == "documento"]
    if not documentos:
        return

    documento = documentos[0]
    sufixo = documento.suffix.lower()
    try:
        if sufixo == ".pdf":
            texto = extrair_pdf(documento)
        elif sufixo == ".docx":
            texto = extrair_docx(documento)
        elif sufixo in {".txt", ".csv", ".md"}:
            texto = documento.read_text(encoding="utf-8", errors="replace").strip()
        else:
            # .doc, .xlsx e o resto: sem extrator aqui, a curadoria decide o que fazer.
            texto = ""
    except Exception as exc:  # noqa: BLE001 - documento ilegivel nao pode travar o lote
        print(f"  aviso: falha ao extrair texto de {documento.name}: {exc}", file=sys.stderr)
        texto = ""

    (pasta / TEXTO_DOCUMENTO).write_text(texto or SEM_TEXTO, encoding="utf-8")
    if texto:
        print(f"  texto extraido de {documento.name} ({len(texto)} caracteres)")
    else:
        # PDF so de imagem (digitalizacao) cai aqui — e o caso comum de foto de documento.
        print(f"  {documento.name}: sem texto extraivel, vai inteiro para a curadoria")


def destino_livre(nome: str) -> Path:
    """Evita que shutil.move enfie a pasta dentro de outra de mesmo nome ja existente."""
    destino = PENDENTE / nome
    sufixo = 2
    while destino.exists():
        destino = PENDENTE / f"{nome}__{sufixo}"
        sufixo += 1
    return destino


def preparar_pasta(carregar_modelo, pasta: Path) -> None:
    # O listener grava o meta.json por ultimo. Sem ele, a captura ainda esta sendo baixada
    # (audio longo e PDF demoram) — mover agora levaria arquivo pela metade para a curadoria.
    if not (pasta / "meta.json").exists():
        print(f"Ignorado (captura incompleta, sem meta.json): {pasta.name}")
        return

    # audio.ogg e o caso normal; audio encaminhado de outro app mantem o formato de origem.
    audios = sorted(p for p in pasta.iterdir() if p.stem == "audio")
    if audios:
        segments, _info = carregar_modelo().transcribe(str(audios[0]), language="pt")
        texto = " ".join(segment.text.strip() for segment in segments).strip()
        (pasta / "transcricao.txt").write_text(texto, encoding="utf-8")

    extrair_texto_do_documento(pasta)

    destino = destino_livre(pasta.name)
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

    # Carregar o Whisper custa minutos e RAM — um lote so de imagem/documento nao paga isso.
    modelo = None

    def carregar_modelo() -> "WhisperModel":
        nonlocal modelo
        if modelo is None:
            compute_type = "int8" if args.device == "cpu" else "float16"
            modelo = WhisperModel(args.modelo, device=args.device, compute_type=compute_type)
        return modelo

    for pasta in pendentes:
        try:
            preparar_pasta(carregar_modelo, pasta)
        except Exception as exc:  # noqa: BLE001 - relata e segue para a proxima pasta
            print(f"Falhou em {pasta.name}: {exc}", file=sys.stderr)


if __name__ == "__main__":
    main()
