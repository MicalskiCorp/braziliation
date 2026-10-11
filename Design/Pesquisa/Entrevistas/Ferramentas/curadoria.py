"""Prepara e fecha o mapeamento de um lote de entrevista: áudio ↔ lugar ↔ fotos e vídeos.

Por que existe: na curadoria da visita ao Teatro Carlos Gomes (2026-10-11) a linha do tempo,
as folhas de miniaturas, a detecção de duplicatas e o de-para foram montados com scripts
improvisados, um passo de cada vez. Este script faz o mesmo de forma repetível. Fluxo completo
na skill `processar-entrevistas`.

    py curadoria.py linha  --lote 2026-10-11-teatro-carlos-gomes
    py curadoria.py gerar  --lote 2026-10-11-teatro-carlos-gomes

`linha` lê as capturas de `_pendente-curadoria/` (e de `_processado/`), e grava em
`_lotes/{lote}/` (fora do git):
  - `mapa.json`    — trechos de áudio na ordem da gravação e cada mídia com o trecho sugerido
                     pelo horário. A curadoria edita: nome e explicação de cada lugar, seções
                     extras (ex.: EXT para o exterior), o trecho final de cada mídia.
  - `folhas/`      — miniaturas numeradas de todas as imagens e quadros dos vídeos, para ler
                     tudo de uma vez em vez de abrir arquivo por arquivo.
  - `revisao.md`   — transcrições na ordem da visita, com palavras por minuto (cobertura) e
                     espaço para os prováveis erros de transcrição.
`gerar` lê o `mapa.json` editado, recusa se alguma mídia ficou sem lugar, grava `de-para.md`
e escreve `trecho` e `lugar` (e `observacao`, quando houver destaque) no `meta.json` de cada
captura. Rodar de novo depois de mover as pastas para `_processado/` refaz os links.
"""

import argparse
import datetime
import hashlib
import json
import re
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PASTAS = [ROOT / "_pendente-curadoria", ROOT / "_processado"]
LOTES = ROOT / "_lotes"
NOME_CAMERA = re.compile(r"(\d{8})_(\d{6})")
# Abaixo disso a transcrição provavelmente perdeu trecho — fala contínua fica em 130–170.
PPM_SUSPEITO = 110


def mvhd(arquivo: Path):
    """(criação UTC, duração em s) do cabeçalho de um .m4a/.mp4; None quando não houver."""
    dados = arquivo.read_bytes()
    i = dados.find(b"mvhd")
    if i < 0:
        return None
    if dados[i + 4] == 0:
        criado, _, escala, duracao = struct.unpack(">IIII", dados[i + 8:i + 24])
    else:
        criado, _ = struct.unpack(">QQ", dados[i + 8:i + 24])
        escala, duracao = struct.unpack(">IQ", dados[i + 24:i + 36])
    return datetime.datetime(1904, 1, 1) + datetime.timedelta(seconds=criado), duracao / escala


def hora_foto(arquivo: Path, nome_original: str):
    """Horário local da câmera: pelo nome original (20261011_102033.jpg) ou pelo EXIF."""
    m = NOME_CAMERA.search(nome_original or "")
    if m:
        return datetime.datetime.strptime(m.group(1) + m.group(2), "%Y%m%d%H%M%S")
    try:
        from PIL import Image
        exif = Image.open(arquivo).getexif()
        bruto = exif.get_ifd(0x8769).get(36867) or exif.get(306)
        if bruto:
            return datetime.datetime.strptime(bruto, "%Y:%m:%d %H:%M:%S")
    except Exception:  # noqa: BLE001 - foto sem EXIF (o WhatsApp apaga) é o caso comum
        pass
    return None


def capturas(lote: str, todas: bool):
    """Pastas de captura do lote. Sem marca de lote ainda, entram as não descartadas."""
    for base in PASTAS:
        if not base.exists():
            continue
        for pasta in sorted(p for p in base.iterdir() if (p / "meta.json").exists()):
            meta = json.loads((pasta / "meta.json").read_text(encoding="utf-8"))
            if meta.get("lote") not in (None, lote):
                continue
            if meta.get("resultado") == "descartado" and not todas:
                continue
            yield pasta, meta


def achar(nome: str) -> Path:
    for base in PASTAS:
        if (base / nome).exists():
            return base / nome
    raise FileNotFoundError(nome)


def linha(args) -> None:
    from PIL import Image, ImageDraw, ImageOps

    destino = LOTES / args.lote
    (destino / "folhas").mkdir(parents=True, exist_ok=True)
    fuso = datetime.timedelta(hours=args.fuso)
    audios, midias, hashes = [], [], {}

    for pasta, meta in capturas(args.lote, args.incluir_descartados):
        meta["lote"] = args.lote
        (pasta / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
        for arq in sorted(pasta.iterdir()):
            if arq.stem == "audio":
                info = mvhd(arq) if arq.suffix.lower() in {".m4a", ".mp4"} else None
                texto = (pasta / "transcricao.txt").read_text(encoding="utf-8") if (pasta / "transcricao.txt").exists() else ""
                audios.append({"pasta": pasta.name, "criado": info[0] + fuso if info else None,
                               "duracao": info[1] if info else None, "palavras": len(texto.split())})
            elif arq.stem in {"imagem", "documento"} and arq.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp", ".mp4"}:
                h = hashlib.md5(arq.read_bytes()).hexdigest()
                video = arq.suffix.lower() == ".mp4"
                if video:
                    info = mvhd(arq)
                    hora = info[0] + fuso if info else None
                else:
                    hora = hora_foto(arq, meta.get("nomeOriginal"))
                midias.append({"pasta": pasta.name, "arquivo": arq.name, "tipo": "video" if video else "foto",
                               "hora": hora, "duplicata_de": hashes.get(h), "trecho": "", "destaque": ""})
                hashes.setdefault(h, pasta.name)

    # O cabeçalho do gravador marca o início ou o fim da gravação, conforme o app. Lido como fim,
    # os trechos de uma visita não se sobrepõem; se sobrepuserem, ele marca o início.
    com_hora = [a for a in audios if a["criado"]]
    for referencia in ("fim", "inicio"):
        for a in com_hora:
            delta = datetime.timedelta(seconds=a["duracao"])
            a["inicio"], a["fim"] = (a["criado"] - delta, a["criado"]) if referencia == "fim" else (a["criado"], a["criado"] + delta)
        com_hora.sort(key=lambda a: a["inicio"])
        if all(x["fim"] <= y["inicio"] for x, y in zip(com_hora, com_hora[1:])):
            break
    trechos = []
    for n, a in enumerate(com_hora + [a for a in audios if not a["criado"]], 1):
        minutos = (a["duracao"] or 0) / 60
        ppm = round(a["palavras"] / minutos) if minutos else None
        trechos.append({"id": f"A{n}", "pasta": a["pasta"], "lugar": "", "explicacao": "", "nota": "",
                        "inicio": a.get("inicio").strftime("%H:%M:%S") if a.get("inicio") else "",
                        "fim": a.get("fim").strftime("%H:%M:%S") if a.get("fim") else "",
                        "duracao_min": round(minutos, 1), "palavras": a["palavras"], "ppm": ppm,
                        "alerta": "ppm baixo: conferir se a transcrição perdeu trecho" if ppm and ppm < PPM_SUSPEITO else ""})

    def sugerir(hora):
        if not hora:
            return "?"
        for t, a in zip(trechos, com_hora):
            if a["inicio"] <= hora <= a["fim"]:
                return t["id"]
        antes = [t["id"] for t, a in zip(trechos, com_hora) if a["fim"] < hora]
        if not antes:
            return "antes"
        if len(antes) == len(com_hora):
            return "depois"
        # Entre dois áudios o grupo está indo para o próximo lugar: na visita de 2026-10-11, as 30
        # fotos tiradas entre trechos pertenciam todas ao trecho seguinte.
        return f"A{len(antes) + 1}"

    midias.sort(key=lambda m: (m["hora"] is None, m["tipo"], m["hora"] or datetime.datetime.min, m["pasta"]))
    contadores = {"foto": 0, "semhora": 0, "video": 0}
    for m in midias:
        if m["tipo"] == "video":
            contadores["video"] += 1
            m["num"] = f"V{contadores['video']}"
        elif m["hora"]:
            contadores["foto"] += 1
            m["num"] = f"#{contadores['foto']:02d}"
        else:
            contadores["semhora"] += 1
            m["num"] = f"F{contadores['semhora']}"
        m["sugestao"] = "duplicata" if m["duplicata_de"] else sugerir(m["hora"])
        m["hora"] = m["hora"].strftime("%H:%M:%S") if m["hora"] else ""

    # Folhas de miniaturas (12 por folha) e quadros dos vídeos.
    def folha(itens, nome):
        w, h = 400, 300
        for p in range(0, len(itens), 12):
            img = Image.new("RGB", (4 * w, 3 * (h + 20)), "white")
            desenho = ImageDraw.Draw(img)
            for k, (rotulo, caminho) in enumerate(itens[p:p + 12]):
                im = ImageOps.exif_transpose(Image.open(caminho)).convert("RGB")
                im.thumbnail((w - 6, h - 6))
                x, y = (k % 4) * w, (k // 4) * (h + 20)
                img.paste(im, (x + 3, y + 3))
                desenho.text((x + 6, y + h + 2), rotulo, fill="black")
            img.save(destino / "folhas" / f"{nome}{p // 12 + 1:02d}.jpg", quality=80)

    folha([(f"{m['num']} {m['hora']} sug:{m['sugestao']}", achar(m["pasta"]) / m["arquivo"])
           for m in midias if m["tipo"] == "foto" and not m["duplicata_de"]], "fotos")
    quadros = []
    for m in (m for m in midias if m["tipo"] == "video" and not m["duplicata_de"]):
        for k, q in enumerate(extrair_quadros(achar(m["pasta"]) / m["arquivo"])):
            quadros.append((f"{m['num']} {m['hora']} quadro {k + 1}", q))
    if quadros:
        folha(quadros, "videos")

    mapa = {"lote": args.lote, "fuso": args.fuso, "trechos": trechos,
            "secoes_extras": [], "midias": midias}
    # O mapa.json é editado à mão na curadoria: rodar `linha` de novo não pode apagar esse trabalho.
    arquivo_mapa = destino / ("mapa-rascunho.json" if (destino / "mapa.json").exists() else "mapa.json")
    if arquivo_mapa.name != "mapa.json":
        print("  mapa.json já existe (curadoria em andamento) — rascunho novo gravado em mapa-rascunho.json")
    arquivo_mapa.write_text(json.dumps(mapa, ensure_ascii=False, indent=2), encoding="utf-8")
    escrever_revisao(destino, trechos)

    print(f"{len(trechos)} trechos de áudio, {len(midias)} mídias "
          f"({sum(1 for m in midias if m['duplicata_de'])} duplicatas) → {destino}")
    for t in trechos:
        print(f"  {t['id']} {t['inicio']}–{t['fim']} {t['duracao_min']} min {t['ppm']} ppm {t['alerta']}")
    print("Próximo passo: ler as folhas, preencher lugar/explicação/trecho em mapa.json e rodar `gerar`.")


def extrair_quadros(video: Path):
    """Três quadros (1/4, 1/2, 3/4) gravados ao lado do vídeo; vazio sem OpenCV."""
    try:
        import cv2
    except ImportError:
        print("  aviso: sem OpenCV (pip install opencv-python), vídeos ficam sem quadro", file=sys.stderr)
        return []
    captura = cv2.VideoCapture(str(video))
    total = int(captura.get(cv2.CAP_PROP_FRAME_COUNT))
    saida = []
    for k, quadro in enumerate((total // 4, total // 2, 3 * total // 4)):
        captura.set(cv2.CAP_PROP_POS_FRAMES, quadro)
        ok, img = captura.read()
        if ok:
            escala = 1280 / max(img.shape[:2])
            img = cv2.resize(img, (int(img.shape[1] * escala), int(img.shape[0] * escala)))
            caminho = video.parent / f"quadro-{k + 1}.jpg"
            cv2.imwrite(str(caminho), img)
            saida.append(caminho)
    return saida


def escrever_revisao(destino: Path, trechos) -> None:
    linhas = [f"# Revisão das transcrições — {destino.name}", "",
              "> Fora do git. Ordem = ordem da gravação. Preencher os prováveis erros de cada trecho",
              "> (✅ confirmado em fonte · ⚠️ palpite, conferir com o responsável) e, ao final, a tabela",
              "> \"Resultado da revisão\" com a decisão de cada ⚠️.", "",
              "| Trecho | Horário | Duração | Palavras/min |", "|---|---|---|---|"]
    linhas += [f"| {t['id']} | {t['inicio']}–{t['fim']} | {t['duracao_min']} min | {t['ppm']} {('⚠️ ' + t['alerta']) if t['alerta'] else ''} |" for t in trechos]
    linhas += ["", "## Resultado da revisão", "", "| Trecho | Na transcrição | Decisão | Base |", "|---|---|---|---|"]
    for t in trechos:
        texto = (achar(t["pasta"]) / "transcricao.txt").read_text(encoding="utf-8").strip()
        linhas += ["", "---", "", f"## {t['id']}", "", "### Prováveis erros de transcrição", "", "- ", "",
                   "### Transcrição (como saiu do Whisper)", "", texto]
    arquivo = destino / "revisao.md"
    if arquivo.exists():
        print(f"  {arquivo.name} já existe — não sobrescrito (revisão em andamento)")
        return
    arquivo.write_text("\n".join(linhas) + "\n", encoding="utf-8")


def gerar(args) -> None:
    destino = LOTES / args.lote
    mapa = json.loads((destino / "mapa.json").read_text(encoding="utf-8"))
    secoes = mapa["secoes_extras"] + mapa["trechos"]
    ids = {s["id"] for s in secoes}

    problemas = [f"seção {s['id']} sem nome de lugar" for s in secoes if not s.get("lugar")]
    problemas += [f"{m['num']} ({m['pasta']}) sem trecho válido: '{m['trecho']}'"
                  for m in mapa["midias"] if not m["duplicata_de"] and m["trecho"] not in ids]
    if problemas:
        print("Mapa incompleto — nenhuma mídia pode ficar sem lugar:\n  " + "\n  ".join(problemas))
        sys.exit(1)

    def link(m, arquivo=None):
        return Path("..", "..", achar(m["pasta"]).relative_to(ROOT), arquivo or m["arquivo"]).as_posix()

    def figura(caminho, legenda):
        return (f'<figure style="display:inline-block;margin:4px;width:230px;vertical-align:top">'
                f'<a href="{caminho}"><img src="{caminho}" width="230"></a>'
                f'<figcaption><small>{legenda}</small></figcaption></figure>')

    saida = [f"# De-para: áudio ↔ lugar ↔ imagens — {mapa['lote']}", "",
             "> Fora do git. Abra no preview do Markdown (Ctrl+Shift+V). Clique numa miniatura para abrir o original.",
             "> `#` = foto com horário da câmera · `F` = foto sem horário (agrupada pelo que mostra) · `V` = vídeo.", "",
             "| Seção | Lugar | Horário | Áudio | Mídias |", "|---|---|---|---|---|"]
    for s in secoes:
        qtd = sum(1 for m in mapa["midias"] if m["trecho"] == s["id"] and not m["duplicata_de"])
        horario = f"{s['inicio']}–{s['fim']}" if s.get("inicio") else s.get("horario", "")
        audio = f"{s['duracao_min']} min" if s.get("duracao_min") else "sem áudio"
        saida.append(f"| [{s['id']}](#{s['id'].lower()}) | {s['lugar']} | {horario} | {audio} | {qtd} |")

    for s in secoes:
        saida += ["", "---", "", f"## {s['id']}", f"### {s['lugar']}", ""]
        if s.get("pasta"):
            audio = next(p.name for p in achar(s["pasta"]).iterdir() if p.stem == "audio")
            saida.append(f"🎙️ **Áudio:** [{s['inicio']}–{s['fim']}, {s['duracao_min']} min]({link({'pasta': s['pasta'], 'arquivo': audio})})")
        else:
            saida.append("🎙️ **Áudio:** nenhum (sem narração)")
        saida += ["", f"**O lugar:** {s.get('explicacao', '')}", ""]
        if s.get("nota"):
            saida += [f"> {s['nota']}", ""]
        figuras = []
        for m in (m for m in mapa["midias"] if m["trecho"] == s["id"] and not m["duplicata_de"]):
            legenda = f"{m['num']} · {m['hora'] or 'sem horário'}" + (f" · {m['destaque']}" if m["destaque"] else "")
            if m["tipo"] == "video":
                quadro = achar(m["pasta"]) / "quadro-2.jpg"
                caminho = link(m, quadro.name) if quadro.exists() else link(m)
                figuras.append(figura(caminho, f"🎬 {legenda} — <a href=\"{link(m)}\">abrir vídeo</a>"))
            else:
                figuras.append(figura(link(m), legenda))
        saida += ["<div>"] + figuras + ["</div>"]
        if s.get("pasta"):
            texto = (achar(s["pasta"]) / "transcricao.txt").read_text(encoding="utf-8").strip()
            saida += ["", "<details><summary><b>Transcrição deste trecho</b> (correções em <code>revisao.md</code>)</summary>",
                      "", texto, "", "</details>"]

        lugar = {m["pasta"]: m.get("destaque", "") for m in mapa["midias"] if m["trecho"] == s["id"]}
        if s.get("pasta"):
            lugar[s["pasta"]] = ""
        for pasta, destaque in lugar.items():
            arq = achar(pasta) / "meta.json"
            meta = json.loads(arq.read_text(encoding="utf-8"))
            meta.update({"trecho": s["id"], "lugar": s["lugar"]})
            if destaque:
                meta["observacao"] = destaque
            arq.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")

    (destino / "de-para.md").write_text("\n".join(saida) + "\n", encoding="utf-8")
    print(f"de-para.md gerado com {len(secoes)} seções; meta.json atualizado em todas as capturas ligadas.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="comando", required=True)
    p_linha = sub.add_parser("linha", help="linha do tempo, folhas, rascunho do mapa e da revisão")
    p_linha.add_argument("--lote", required=True, help="AAAA-MM-DD-assunto")
    p_linha.add_argument("--fuso", type=int, default=-3, help="horas em relação a UTC (padrão: -3)")
    p_linha.add_argument("--incluir-descartados", action="store_true")
    p_gerar = sub.add_parser("gerar", help="de-para.md e trecho/lugar no meta.json, a partir do mapa editado")
    p_gerar.add_argument("--lote", required=True)
    args = parser.parse_args()
    {"linha": linha, "gerar": gerar}[args.comando](args)


if __name__ == "__main__":
    main()
