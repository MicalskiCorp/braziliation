"""Prepara e fecha o mapeamento de um lote de entrevista: áudio ↔ lugar ↔ fotos e vídeos.

Por que existe: na curadoria da visita ao Teatro Carlos Gomes (2026-10-11) a linha do tempo,
as folhas de miniaturas, a detecção de duplicatas e o de-para foram montados com scripts
improvisados, um passo de cada vez. Este script faz o mesmo de forma repetível. Fluxo completo
na skill `processar-entrevistas`.

    py curadoria.py triagem                                  # o que chegou sem #assunto
    py curadoria.py atribuir --grupo 2 --assunto benzedeira
    py curadoria.py linha    --assunto teatro-carlos-gomes [--data 2026-10-11]
    py curadoria.py gerar    --lote 2026-10-11-teatro-carlos-gomes

**Assunto e sessão.** Assunto é permanente e acumula (a benzedeira, o Teatro Carlos Gomes, Edith
Gaertner); sessão é uma coleta de um assunto numa data. O lote de trabalho é sempre uma sessão de
um assunto só: `{AAAA-MM-DD}-{assunto}`. O assunto vem do `#assunto` mandado no WhatsApp (o
listener grava no `meta.json`); o que chegar sem ele passa pela `triagem`, que agrupa por horário,
e pelo `atribuir`, com o assunto que o usuário confirmar. `linha` recusa captura sem assunto e
`gerar` recusa mapa com captura de outro assunto — material de assuntos diferentes no mesmo dia
nunca entra no mesmo lote.

`linha` lê as capturas do assunto em `_pendente-curadoria/` (e `_processado/`) e grava em
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


def todas_capturas(bases=PASTAS):
    for base in bases:
        if not base.exists():
            continue
        for pasta in sorted(p for p in base.iterdir() if (p / "meta.json").exists()):
            yield pasta, json.loads((pasta / "meta.json").read_text(encoding="utf-8"))


def gravar_meta(pasta: Path, meta: dict) -> None:
    (pasta / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")


def slug(texto: str) -> str:
    """Mesmo slug do listener (`slugAssunto`): sem acento, minúsculo, hífen."""
    import unicodedata
    sem_acento = unicodedata.normalize("NFD", texto).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", sem_acento.lower()).strip("-")[:60]


def hora_local(pasta: Path, fuso: int) -> datetime.datetime:
    """Horário de envio da mensagem: o prefixo UTC do nome da pasta, no fuso local."""
    utc = datetime.datetime.strptime(pasta.name[:19], "%Y-%m-%dT%H-%M-%S")
    return utc + datetime.timedelta(hours=fuso)


def capturas(lote: str, assunto: str, data: str, fuso: int, todas: bool):
    """Capturas da sessão: do assunto e da data de sessão gravada pela triagem (ou já deste lote)."""
    for pasta, meta in todas_capturas():
        if meta.get("lote") != lote and (meta.get("lote") or meta.get("assunto") != assunto
                                         or meta.get("sessao") != data):
            continue
        if meta.get("resultado") == "descartado" and not todas:
            continue
        yield pasta, meta


def hora_captura(pasta: Path, meta: dict, fuso: int):
    """Quando o material foi gravado ou fotografado — não quando foi enviado. None sem como saber
    (foto mandada como "Foto", que o WhatsApp entrega sem horário; texto)."""
    for arq in sorted(pasta.iterdir()):
        if arq.stem not in ("audio", "imagem", "documento"):
            continue
        sufixo = arq.suffix.lower()
        if sufixo in (".m4a", ".mp4"):
            info = mvhd(arq)
            if info and info[0].year > 1904:
                return info[0] + datetime.timedelta(hours=fuso)
        elif sufixo in (".jpg", ".jpeg", ".png", ".webp"):
            hora = hora_foto(arq, meta.get("nomeOriginal"))
            if hora:
                return hora
    return None


def data_da_sessao(itens, fuso: int):
    """(data, base, datas distintas) de um grupo: pela gravação/foto quando houver, senão pelo envio.
    O áudio mandado hoje e gravado ontem é da sessão de ontem."""
    gravadas = [h for h in (hora_captura(p, m, fuso) for p, m in itens) if h]
    if gravadas:
        datas = sorted({h.strftime("%Y-%m-%d") for h in gravadas})
        return datas[0], "gravação", datas
    envio = min(hora_local(p, fuso) for p, _ in itens).strftime("%Y-%m-%d")
    return envio, "envio", [envio]


ASSUNTOS = ROOT / "Assuntos"
SEM_TEXTO = "[sem camada de texto extraivel"


def normalizar(texto: str) -> str:
    import unicodedata
    return unicodedata.normalize("NFD", texto).encode("ascii", "ignore").decode().lower()


def palavras_chave() -> dict:
    """{slug: [chaves]} da linha '> Palavras-chave: a; b; c' de cada página em Assuntos/."""
    chaves = {}
    for pagina in sorted(ASSUNTOS.glob("*.md")) if ASSUNTOS.exists() else []:
        if pagina.name == "index.md":
            continue
        texto = pagina.read_text(encoding="utf-8")
        linha_chaves = re.search(r"Palavras-chave:\s*(.+)", texto)
        if linha_chaves:
            chaves[pagina.stem] = [normalizar(k.strip()) for k in linha_chaves.group(1).split(";") if k.strip()]
    return chaves


def texto_da_captura(pasta: Path, meta: dict) -> str:
    """Tudo o que a captura diz em texto: mensagem, transcrição, legenda, texto do documento."""
    partes = [meta.get("nomeOriginal") or ""]
    for nome in ("mensagem.txt", "transcricao.txt", "legenda.txt", "texto-documento.txt"):
        arq = pasta / nome
        if arq.exists():
            conteudo = arq.read_text(encoding="utf-8")
            if not conteudo.startswith(SEM_TEXTO):
                partes.append(conteudo)
    return " ".join(partes)


def pontuar(texto: str, chaves: dict) -> dict:
    """{slug: {chave: ocorrências}} — só chaves que aparecem."""
    alvo = normalizar(texto)
    pontos = {}
    for assunto, lista in chaves.items():
        achadas = {k: len(re.findall(r"\b" + re.escape(k) + r"\b", alvo)) for k in lista}
        achadas = {k: n for k, n in achadas.items() if n}
        if achadas:
            pontos[assunto] = achadas
    return pontos


def mais_provavel(pontos: dict):
    if not pontos:
        return None
    return max(pontos, key=lambda a: sum(pontos[a].values()))


def triagem(args) -> None:
    """Agrupa por horário o que está pendente sem assunto e sugere o assunto de cada grupo pelo
    conteúdo — transcrição, textos e legendas comparados às palavras-chave de cada página em
    Assuntos/. A sugestão é para o usuário confirmar, nunca é gravada sozinha."""
    # Passa pela triagem tudo o que ainda não tem sessão — inclusive o marcado com #assunto, que
    # entra com o assunto certo, mas precisa da data da sessão como qualquer outro.
    sem = [(p, m) for p, m in todas_capturas([PASTAS[0]]) if not m.get("sessao")]
    if not sem:
        print("Nada pendente sem sessão.")
        return
    chaves = palavras_chave()
    grupos, anterior = [], None
    for pasta, meta in sorted(sem, key=lambda pm: pm[0].name):
        hora = hora_local(pasta, args.fuso)
        # Mais de N minutos sem mensagem separa duas coletas — no mesmo dia pode haver uma visita
        # de manhã e uma conversa à tarde, de assuntos diferentes.
        if anterior is None or (hora - anterior).total_seconds() > args.intervalo * 60:
            grupos.append([])
        grupos[-1].append((pasta, meta, hora))
        anterior = hora
    registro = {}
    for i, g in enumerate(grupos, 1):
        tipos, total, por_item = {}, {}, {}
        for pasta, m, _ in g:
            tipos[m.get("tipo")] = tipos.get(m.get("tipo"), 0) + 1
            if m.get("assunto"):  # marcado com #assunto: vale mais que qualquer palavra-chave
                por_item[pasta.name] = m["assunto"]
                total.setdefault(m["assunto"], {})
                total[m["assunto"]]["#assunto"] = total[m["assunto"]].get("#assunto", 0) + 100
                continue
            pontos = pontuar(texto_da_captura(pasta, m), chaves)
            for assunto, achadas in pontos.items():
                for k, n in achadas.items():
                    total.setdefault(assunto, {})
                    total[assunto][k] = total[assunto].get(k, 0) + n
            if pontos:
                por_item[pasta.name] = mais_provavel(pontos)
        sugestao = mais_provavel(total)
        # Dois itens do mesmo horário apontando para assuntos diferentes: o horário juntou o que o
        # conteúdo separa. Não sugerir um assunto só — separar por --pastas.
        mistura = len(set(por_item.values())) > 1
        data, base, datas = data_da_sessao([(p, m) for p, m, _ in g], args.fuso)
        registro[str(i)] = {"pastas": [p.name for p, _, _ in g], "sugestao": None if mistura else sugestao,
                            "por_item": por_item, "mistura": mistura, "sessao": data}

        print(f"\nGrupo {i}: enviado {g[0][2]:%d/%m %H:%M} – {g[-1][2]:%H:%M} · "
              + ", ".join(f"{n} {t}" for t, n in tipos.items()))
        print(f"   sessão: {data[8:10]}/{data[5:7]} (pela {base})")
        if len(datas) > 1:
            print(f"   ⚠️ material gravado em datas diferentes ({', '.join(datas)}) — se forem sessões distintas, "
                  "atribuir por partes com --pastas --data")
        if mistura:
            print("   ⚠️ conteúdo aponta para mais de um assunto — separar com `atribuir --pastas`:")
            for nome, assunto in por_item.items():
                print(f"      {nome} → {assunto}")
        elif sugestao:
            sinais = ", ".join(f"{k}×{n}" for k, n in sorted(total[sugestao].items(), key=lambda kv: -kv[1])[:6])
            print(f"   sugestão: {sugestao}  ({sinais})")
        else:
            print("   sem correspondência com assunto conhecido — ler o conteúdo e propor (assunto novo?)")
        for pasta, m, hora in g:
            if m.get("tipo") in ("texto", "audio"):
                arq = pasta / ("mensagem.txt" if m.get("tipo") == "texto" else "transcricao.txt")
                if arq.exists():
                    trecho = arq.read_text(encoding="utf-8").strip().replace("\n", " ")
                    print(f"   {hora:%H:%M} {m.get('tipo')}: {trecho[:140]}")
        sem_sinal = sum(1 for p, m, _ in g if m.get("tipo") in ("imagem", "documento") and p.name not in por_item)
        if sem_sinal:
            print(f"   {sem_sinal} foto(s)/documento(s) sem texto — seguem o grupo pelo horário; conferir nas folhas")
    LOTES.mkdir(exist_ok=True)
    (LOTES / "_triagem.json").write_text(json.dumps(registro, ensure_ascii=False, indent=2), encoding="utf-8")
    print("\nApresentar as sugestões ao usuário numa pergunta só. Confirmadas: `atribuir --grupo N` "
          "(usa a sugestão) ou `atribuir --grupo N --assunto X` (corrige); grupo misto: `atribuir --pastas`.")


def atribuir(args) -> None:
    if args.grupo:
        grupo = json.loads((LOTES / "_triagem.json").read_text(encoding="utf-8"))[str(args.grupo)]
        if grupo["mistura"]:
            print(f"Grupo {args.grupo} mistura assuntos pelo conteúdo — atribuir por partes com --pastas.")
            sys.exit(1)
        nomes = grupo["pastas"]
        sessao = args.data or grupo["sessao"]
        escolhido = args.assunto or grupo["sugestao"]
        if not escolhido:
            print(f"Grupo {args.grupo} não tem sugestão — informar --assunto.")
            sys.exit(1)
    else:
        nomes = [n.strip() for n in args.pastas.split(",") if n.strip()]
        itens = [(achar(n), json.loads((achar(n) / "meta.json").read_text(encoding="utf-8"))) for n in nomes]
        sessao = args.data or data_da_sessao(itens, args.fuso)[0]
        escolhido = args.assunto
        if not escolhido:
            print("Com --pastas, informar --assunto.")
            sys.exit(1)
    alvo = slug(escolhido)
    for nome in nomes:
        pasta = achar(nome)
        meta = json.loads((pasta / "meta.json").read_text(encoding="utf-8"))
        if meta.get("assunto") not in (None, alvo) and not args.forcar:
            print(f"  {nome} já é do assunto '{meta['assunto']}' — não troquei (use --forcar se for engano)")
            continue
        meta["assunto"] = alvo
        meta["sessao"] = sessao
        gravar_meta(pasta, meta)
    print(f"{len(nomes)} captura(s) → assunto '{alvo}', sessão {sessao}.")


def achar(nome: str) -> Path:
    for base in PASTAS:
        if (base / nome).exists():
            return base / nome
    raise FileNotFoundError(nome)


def linha(args) -> None:
    from PIL import Image, ImageDraw, ImageOps

    assunto = slug(args.assunto)
    pendentes = [(p, m) for p, m in todas_capturas([PASTAS[0]]) if m.get("assunto") == assunto and not m.get("lote")]
    sem_sessao = [p.name for p, m in pendentes if not m.get("sessao")]
    if sem_sessao:
        print(f"{len(sem_sessao)} captura(s) de '{assunto}' sem data de sessão — rode `triagem` e `atribuir` antes.")
        sys.exit(1)
    datas = sorted({m["sessao"] for _, m in pendentes})
    data = args.data or (datas[0] if datas else None)
    if not data:  # sem pendente e sem --data: nada a montar (com --data, refaz um lote já arquivado)
        print(f"Nada pendente do assunto '{assunto}'.")
        sys.exit(1)
    if len(datas) > 1 and not args.data:
        print(f"O assunto '{assunto}' tem material de {len(datas)} datas ({', '.join(datas)}): cada data é uma "
              "sessão. Rode uma vez por data com --data.")
        sys.exit(1)
    sem_triagem = sum(1 for _, m in todas_capturas([PASTAS[0]]) if not m.get("sessao"))
    if sem_triagem:
        print(f"  aviso: {sem_triagem} captura(s) pendente(s) ainda sem triagem — rode `triagem` para não deixar "
              "material desta sessão de fora.")
    lote = f"{data}-{assunto}"
    args.lote = lote

    destino = LOTES / lote
    (destino / "folhas").mkdir(parents=True, exist_ok=True)
    fuso = datetime.timedelta(hours=args.fuso)
    audios, midias, hashes = [], [], {}

    for pasta, meta in capturas(lote, assunto, data, args.fuso, args.incluir_descartados):
        meta["lote"] = lote
        gravar_meta(pasta, meta)
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

    mapa = {"lote": args.lote, "assunto": assunto, "data": data, "fuso": args.fuso, "trechos": trechos,
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
              "> \"Resultado da revisão\" com a decisão de cada ⚠️.",
              "> Fiel à fala: corrigir só erro do Whisper; concordância, pronúncia e desvios da pessoa",
              "> ficam como ela falou (texto canônico só como referência, em seção à parte).", "",
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
    # Um lote é um assunto só: captura marcada com outro assunto aqui é mistura, não curadoria.
    for nome in [t["pasta"] for t in mapa["trechos"]] + [m["pasta"] for m in mapa["midias"]]:
        outro = json.loads((achar(nome) / "meta.json").read_text(encoding="utf-8")).get("assunto")
        if outro != mapa.get("assunto"):
            problemas.append(f"{nome} é do assunto '{outro}', não '{mapa.get('assunto')}'")
    problemas += [f"{m['num']} ({m['pasta']}) sem trecho válido: '{m['trecho']}'"
                  for m in mapa["midias"] if not m["duplicata_de"] and m["trecho"] not in ids]
    # Lote sem horário de captura (fotos como "Foto", notas de voz) se organiza por lugar: a seção
    # lista as anotações em áudio e as placas/textos daquele lugar. Áudio ou texto do lote que não
    # caiu em nenhuma seção ficaria de fora do de-para sem ninguém notar.
    ligados = {t["pasta"] for t in mapa["trechos"]}
    for s in secoes:
        ligados.update(s.get("audios", []) + s.get("textos", []))
    for pasta, meta in todas_capturas():
        if meta.get("lote") == mapa["lote"] and meta.get("tipo") in ("audio", "texto") \
                and meta.get("resultado") != "descartado" and pasta.name not in ligados:
            problemas.append(f"{meta['tipo']} {pasta.name} não está em nenhuma seção (campo audios/textos)")
    if problemas:
        print("Mapa recusado — toda mídia precisa de lugar, e o lote inteiro de um assunto só:\n  " + "\n  ".join(problemas))
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
        if s.get("duracao_min"):
            audio = f"{s['duracao_min']} min"
        elif s.get("audios") or s.get("textos"):
            audio = f"{len(s.get('audios', []))} anotação(ões), {len(s.get('textos', []))} placa(s)"
        else:
            audio = "sem áudio"
        saida.append(f"| [{s['id']}](#{s['id'].lower()}) | {s['lugar']} | {horario} | {audio} | {qtd} |")

    for s in secoes:
        saida += ["", "---", "", f"## {s['id']}", f"### {s['lugar']}", ""]
        if s.get("pasta"):
            audio = next(p.name for p in achar(s["pasta"]).iterdir() if p.stem == "audio")
            saida.append(f"🎙️ **Áudio:** [{s['inicio']}–{s['fim']}, {s['duracao_min']} min]({link({'pasta': s['pasta'], 'arquivo': audio})})")
        elif not s.get("audios"):
            saida.append("🎙️ **Áudio:** nenhum (sem narração)")
        saida += ["", f"**O lugar:** {s.get('explicacao', '')}", ""]
        if s.get("nota"):
            saida += [f"> {s['nota']}", ""]
        for pasta in s.get("textos", []):
            texto = (achar(pasta) / "mensagem.txt").read_text(encoding="utf-8").strip().replace("\n", " ")
            saida += [f"🪧 **Placa / texto:** {texto}", ""]
        for pasta in s.get("audios", []):
            audio = next(p.name for p in achar(pasta).iterdir() if p.stem == "audio")
            texto = (achar(pasta) / "transcricao.txt").read_text(encoding="utf-8").strip()
            saida += [f"🎙️ **Anotação em áudio** ([ouvir]({link({'pasta': pasta, 'arquivo': audio})})): {texto}", ""]
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
        for pasta in s.get("audios", []) + s.get("textos", []):
            lugar[pasta] = ""
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
    p_tri = sub.add_parser("triagem", help="agrupa por horário o que chegou sem #assunto e sugere o assunto pelo conteúdo")
    p_tri.add_argument("--fuso", type=int, default=-3)
    p_tri.add_argument("--intervalo", type=int, default=90, help="minutos sem mensagem que separam coletas (padrão: 90)")
    p_atr = sub.add_parser("atribuir", help="grava o assunto confirmado pelo usuário num grupo da triagem")
    alvo = p_atr.add_mutually_exclusive_group(required=True)
    alvo.add_argument("--grupo", type=int)
    alvo.add_argument("--pastas", help="nomes de pasta separados por vírgula")
    p_atr.add_argument("--assunto", help="assunto confirmado; sem ele, --grupo usa a sugestão da triagem")
    p_atr.add_argument("--data", help="AAAA-MM-DD da sessão; sem ela, a da triagem (pela gravação)")
    p_atr.add_argument("--fuso", type=int, default=-3)
    p_atr.add_argument("--forcar", action="store_true", help="troca assunto já gravado (correção de engano)")
    p_linha = sub.add_parser("linha", help="linha do tempo, folhas, rascunho do mapa e da revisão de uma sessão")
    p_linha.add_argument("--assunto", required=True)
    p_linha.add_argument("--data", help="AAAA-MM-DD da sessão (obrigatória se o assunto tiver mais de uma data pendente)")
    p_linha.add_argument("--fuso", type=int, default=-3, help="horas em relação a UTC (padrão: -3)")
    p_linha.add_argument("--incluir-descartados", action="store_true")
    p_gerar = sub.add_parser("gerar", help="de-para.md e trecho/lugar no meta.json, a partir do mapa editado")
    p_gerar.add_argument("--lote", required=True)
    args = parser.parse_args()
    {"triagem": triagem, "atribuir": atribuir, "linha": linha, "gerar": gerar}[args.comando](args)


if __name__ == "__main__":
    main()
