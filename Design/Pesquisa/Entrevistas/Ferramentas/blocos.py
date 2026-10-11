"""Divide as transcrições de um lote em blocos numerados para o inventário de assuntos.

Por que existe: em 2026-10-11 a curadoria da visita ao Teatro Carlos Gomes resumiu ~62 min de
áudio direto em texto de pesquisa e deixou 12 assuntos de fora sem ninguém perceber — a unidade
de decisão era o áudio inteiro, e um resumo seleciona. Com blocos de ~150 palavras, cada pedaço
da fala ganha um id (A1.01, A1.02…) que o inventário precisa cobrir, e o teste
`InterviewInventoryTests` barra o commit se algum bloco ficar sem destino.

    py blocos.py --lote 2026-10-11-teatro-carlos-gomes
    py blocos.py --lote 2026-10-11-teatro-carlos-gomes --pasta ../_processado

Grava `blocos.txt` dentro de cada pasta de áudio (fora do git, como a transcrição) e imprime a
tabela "Trechos" pronta para colar no inventário. Os trechos são ordenados pelo horário de
gravação (cabeçalho do .m4a; sem ele, a ordem das pastas).
"""

import argparse
import datetime
import json
import re
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PALAVRAS_POR_BLOCO = 150


def horario_gravacao(audio: Path) -> str:
    """Horário gravado no cabeçalho mvhd do .m4a/.mp4 (UTC); vazio quando não houver."""
    if audio.suffix.lower() not in {".m4a", ".mp4"}:
        return ""
    dados = audio.read_bytes()
    i = dados.find(b"mvhd")
    if i < 0:
        return ""
    if dados[i + 4] == 0:
        segundos = struct.unpack(">I", dados[i + 8:i + 12])[0]
    else:
        segundos = struct.unpack(">Q", dados[i + 8:i + 16])[0]
    return (datetime.datetime(1904, 1, 1) + datetime.timedelta(seconds=segundos)).isoformat()


def dividir(texto: str, alvo: int = PALAVRAS_POR_BLOCO) -> list:
    """Blocos de ~alvo palavras, cortados em fim de frase para não partir uma ideia ao meio."""
    frases = []
    for frase in (f for f in re.split(r"(?<=[.!?])\s+", texto.strip()) if f):
        # O Whisper pontua pouco: uma "frase" pode ter 400 palavras e esconder vários assuntos
        # num bloco só. Frase acima do alvo é fatiada em pedaços de no máximo `alvo` palavras.
        palavras = frase.split()
        frases += [" ".join(palavras[i:i + alvo]) for i in range(0, len(palavras), alvo)]
    blocos, atual = [], []
    for frase in frases:
        # Fecha o bloco antes de estourar: somar um pedaço cheio a um bloco quase pronto
        # gerava blocos de ~280 palavras.
        if atual and sum(len(f.split()) for f in atual) + len(frase.split()) > alvo * 1.4:
            blocos.append(" ".join(atual))
            atual = []
        atual.append(frase)
        if sum(len(f.split()) for f in atual) >= alvo:
            blocos.append(" ".join(atual))
            atual = []
    if atual:
        # Sobra curta junta no bloco anterior: um bloco de 10 palavras só gera ruído no inventário.
        if blocos and sum(len(f.split()) for f in atual) < alvo // 3:
            blocos[-1] += " " + " ".join(atual)
        else:
            blocos.append(" ".join(atual))
    return blocos


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--lote", required=True,
                        help="só as capturas deste lote (meta.json 'lote', gravado por curadoria.py linha) — "
                             "dois assuntos pendentes nunca entram na mesma numeração")
    parser.add_argument("--pasta", default=str(ROOT / "_pendente-curadoria"))
    parser.add_argument("--prefixo", default="A", help="letra dos ids dos trechos (padrão: A)")
    parser.add_argument("--incluir-descartados", action="store_true",
                        help="inclui capturas com resultado=descartado no meta.json")
    args = parser.parse_args()

    trechos = []
    for pasta in sorted(Path(args.pasta).iterdir()):
        transcricao = pasta / "transcricao.txt"
        if not transcricao.exists():
            continue
        meta = json.loads((pasta / "meta.json").read_text(encoding="utf-8"))
        if meta.get("lote") != args.lote:
            continue
        if meta.get("resultado") == "descartado" and not args.incluir_descartados:
            continue
        audios = sorted(p for p in pasta.iterdir() if p.stem == "audio")
        horario = horario_gravacao(audios[0]) if audios else ""
        trechos.append((horario or pasta.name, pasta, transcricao.read_text(encoding="utf-8")))

    if not trechos:
        print("Nenhuma transcrição encontrada em", args.pasta)
        return

    print("| Trecho | Pasta | Blocos |")
    print("|---|---|---|")
    for n, (_, pasta, texto) in enumerate(sorted(trechos, key=lambda t: t[0]), 1):
        trecho = f"{args.prefixo}{n}"
        blocos = dividir(texto)
        linhas = [f"[{trecho}.{i:02d}] {b}" for i, b in enumerate(blocos, 1)]
        (pasta / "blocos.txt").write_text("\n\n".join(linhas) + "\n", encoding="utf-8")
        print(f"| {trecho} | `{pasta.name}` | {len(blocos)} |")


if __name__ == "__main__":
    main()
