"""Rotas da Central (ADR-012). Toda ação é POST via fetch com o token da página (seguranca.py)."""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import re
import subprocess
import threading
from pathlib import Path
from urllib.parse import quote

from fastapi import FastAPI, Form, Request
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from markupsafe import Markup
from starlette.concurrency import run_in_threadpool

from . import config, filas as mod_filas, fontes, gitops
from .execucoes import ATIVOS, ROTULOS, Bloqueio, Gerenciador
from .fontes import todo_md
from .seguranca import Protecao

PASTA = Path(__file__).resolve().parent
IMAGEM_NO_TEXTO = re.compile(r"[\w./\\\-À-ÿ]+\.(?:png|jpe?g|webp|gif)", re.IGNORECASE)

GATES = {
    "todo.py validar": [".claude/skills/gerir-todo/todo.py", "validar"],
    "dotnet test": None,
    "meta-check": [".claude/skills/meta-check/check_meta_pairs.py"],
    "paletas": ["Design/ArteFonte/Ferramentas/check_art_palettes.py"],
    "unity-validar": [".claude/skills/unity-validar/scripts/validar.py", "--testes"],
}
PRESETS = {
    "validar-todos": ("agent-architect", "Rode a skill validar-todos e me traga o relatório: o que está marcado como concluído e não está implementado, testado ou documentado, e os gaps da milestone."),
    "structure-audit": ("agent-architect", "Rode a skill structure-audit e me traga o relatório de gaps entre disco e documentação, com o plano de correção. Não corrija nada sem eu aprovar."),
    "tokens": ("game-architect", "Faça a análise de tokens da documentação (o seu modo de otimizar tokens): o que está perto dos tetos do TokenBudgetTests e como dividir."),
    "revisao-qa": ("qa-engineer", "Revise as últimas mudanças de código do projeto (git log recente) atrás de edge cases, null safety e risco de regressão, e proponha critérios de aceite."),
    "sessao": ("agent-architect", "Abra uma sessão de desenvolvimento: leia os TODOs e o roadmap, classifique as próximas tarefas e diga quais filas da Central atacar primeiro e com qual agente."),
}


def ok(**dados) -> JSONResponse:
    return JSONResponse({"ok": True, **dados})


def falha(erro: str, status: int = 400, **dados) -> JSONResponse:
    return JSONResponse({"ok": False, "erro": erro, **dados}, status_code=status)


def criar_app(raiz: Path | None = None, estado: Path | None = None, fabrica=None,
              hosts_extra: tuple[str, ...] = (), token: str | None = None, observar: bool = True) -> FastAPI:
    raiz = Path(raiz or config.RAIZ)
    kwargs = {"raiz": raiz, "estado": estado, "zelador": observar}
    if fabrica is not None:
        kwargs["fabrica"] = fabrica
    ger = Gerenciador(**kwargs)
    app = FastAPI(title="Central do Braziliation", docs_url=None, redoc_url=None, openapi_url=None)
    app.state.ger = ger
    app.state.raiz = raiz
    app.state.versao_arquivos = 0
    app.state.gates = {}
    templates = Jinja2Templates(directory=str(PASTA / "templates"))
    protecao_token = {"valor": token}

    def md(texto: str, base: str = "", execucao: str = "") -> Markup:
        return Markup(fontes.renderizar_md(texto or "", base, execucao))

    def celula(texto: str, base: str) -> Markup:
        return md(texto, base).replace("<p>", "").replace("</p>", "")

    templates.env.globals.update(md=md, celula=celula, ROTULOS=ROTULOS, quote=quote)
    templates.env.filters["limpo"] = todo_md.limpo

    def pagina(request: Request, nome: str, **ctx) -> HTMLResponse:
        ctx.setdefault("n_atencao", len(ger.pedem_atencao()))
        ctx.setdefault("n_ativas", len(ger.ativas()))
        return templates.TemplateResponse(request, nome, {"token": protecao_token["valor"], **ctx})

    def carregar():
        return mod_filas.carregar(raiz)

    def base_de(execucao: str) -> Path:
        if execucao:
            ex = ger.obter(execucao)
            if ex.cwd and Path(ex.cwd).exists():
                return Path(ex.cwd)
        return raiz

    def seguro(base: Path, rel: str) -> Path:
        alvo = (base / rel).resolve()
        if not alvo.is_relative_to(base.resolve()):
            raise Bloqueio("caminho fora do projeto")
        return alvo

    def imagens_citadas(texto: str, ex) -> list[str]:
        achadas = []
        for m in IMAGEM_NO_TEXTO.findall(texto or ""):
            rel = m.replace("\\", "/").lstrip("./")
            for base in ([Path(ex.cwd)] if ex.cwd else []) + [raiz]:
                try:
                    if seguro(base, rel).is_file() and rel not in achadas:
                        achadas.append(rel)
                        break
                except Bloqueio:
                    pass
            if len(achadas) >= 12:
                break
        return achadas

    def html_entrada(entrada: dict, ex) -> str:
        imgs = imagens_citadas(entrada.get("texto", ""), ex) if entrada["tipo"] == "agente" else []
        pendentes = {p["request_id"] for p in ex.pendentes}
        return templates.get_template("_entrada.html").render(
            e=entrada, ex=ex, imagens=imgs, pendente=entrada.get("request_id") in pendentes, md=md, quote=quote)

    # ── painel e filas ──────────────────────────────────────────────────────

    @app.get("/", response_class=HTMLResponse)
    async def painel(request: Request):
        fs = await run_in_threadpool(carregar)
        em_exec = ger.itens_em_execucao()
        por_fila = {}
        for e in ger.ativas():
            por_fila.setdefault(e.fila_id, []).append(e)
        usuario = [(f, i) for f in fs for i in f.abertos if "usu" in todo_md.sem_acento(i["responsavel"]).lower()]
        return pagina(request, "painel.html", grupos=mod_filas.agrupadas(fs), atencao=ger.pedem_atencao(),
                      por_fila=por_fila, em_exec=em_exec, usuario=usuario,
                      sem_fila=mod_filas.secoes_sem_fila(fs, raiz), dessinc=mod_filas.dessincronias(fs, raiz))

    @app.get("/fila/{fila_id}", response_class=HTMLResponse)
    async def fila(request: Request, fila_id: str, todos: int = 0):
        fs = await run_in_threadpool(carregar)
        try:
            f = mod_filas.por_id(fs, fila_id)
        except KeyError:
            return pagina(request, "erro.html", erro=f"Fila {fila_id} não existe.")
        itens = f.itens if todos else f.abertos
        em_exec = ger.itens_em_execucao()
        manual = next((e for e in ger.ativas() if e.fila_id == f.id and not e.agente), None)
        responsaveis = sorted({i["responsavel"] for i in itens if i["responsavel"]})
        return pagina(request, "fila.html", f=f, itens=itens, todos=todos, em_exec=em_exec,
                      execucoes=[e for e in ger.ativas() if e.fila_id == f.id], manual=manual,
                      responsaveis=responsaveis, status=todo_md.STATUS, prioridades=todo_md.PRIORIDADES,
                      secoes=sorted({i["secao"] for i in f.itens}),
                      dessinc=mod_filas.dessincronias(fs, raiz) if f.id in ("pes-handoffs", "cri-entrada") else [],
                      lotes=fontes.lotes_de_entrevista(raiz) if f.fonte.get("tipo") == "entrevistas" else [],
                      listener=fontes.listener() if f.fonte.get("tipo") == "entrevistas" else None)

    def montar_pedido(f, itens: list[dict], extra: str) -> str:
        onde = f.arquivo + (f" § {f.fonte['secao']}" if "secao" in f.fonte else "")
        linhas = [f"Fila «{f.nome}» (camada {f.camada}) — fonte: {onde}.", "",
                  "Itens selecionados pelo responsável na Central:"]
        for n, i in enumerate(itens, 1):
            partes = [f"{n}. {i['titulo']}"]
            if i.get("secao") and "secao" not in f.fonte:
                partes.append(f"seção: {i['secao']}")
            if i.get("texto_status"):
                partes.append(f"status: {todo_md.limpo(i['texto_status'])}")
            if i.get("prioridade"):
                partes.append(f"prioridade: {i['prioridade']}")
            if i.get("responsavel"):
                partes.append(f"responsável: {i['responsavel']}")
            if i.get("referencia"):
                partes.append(f"referência: {i['referencia']}")
            if i.get("descricao"):
                partes.append(f"detalhe: {todo_md.limpo(i['descricao'])}")
            if i.get("correcao"):
                partes.append(f"correção sugerida: {i['correcao']}")
            linhas.append(" — ".join(partes))
        if f.instrucao:
            linhas += ["", f.instrucao]
        if extra.strip():
            linhas += ["", "Orientação do responsável: " + extra.strip()]
        linhas += ["", "Trabalhe nesses itens seguindo o seu Passo 0 e o seu Passo Final. Pergunte quando precisar de decisão."]
        return "\n".join(linhas)

    @app.post("/fila/{fila_id}/executar")
    async def executar(request: Request, fila_id: str):
        form = await request.form()
        ids = form.getlist("itens")
        confirmado = form.get("confirmado") == "1"
        extra = str(form.get("orientacao", ""))
        fs = await run_in_threadpool(carregar)
        try:
            f = mod_filas.por_id(fs, fila_id)
        except KeyError:
            return falha("fila inexistente", 404)
        escolhidos = [i for i in f.itens if i["id"] in ids]
        if len(escolhidos) != len(set(ids)):
            return falha("A fila mudou desde que a página foi aberta — recarregue e selecione de novo.")
        grupos: dict[str, list[dict]] = {}
        for i in escolhidos:
            grupos.setdefault(f.agente_do_item(i), []).append(i)
        if not grupos:
            grupos[f.agente] = []
        try:
            avisos = []
            for agente, itens in grupos.items():
                bloq, av = ger.avaliar(f, itens)
                if bloq:
                    return falha(" ".join(bloq))
                avisos += av
            if len(grupos) > 1:
                avisos.insert(0, "Os itens têm responsáveis diferentes: serão " + str(len(grupos)) + " execuções ("
                              + ", ".join(f"@{a} com {len(it)} item(ns)" for a, it in grupos.items()) + ").")
            if avisos and not confirmado:
                return falha("confirmar", 409, avisos=avisos)
            criadas = []
            for agente, itens in grupos.items():
                ex, _ = await run_in_threadpool(ger.criar, f, itens, agente, montar_pedido(f, itens, extra), True)
                criadas.append(ex)
        except Bloqueio as erro:
            return falha(str(erro))
        return ok(ir=f"/execucao/{criadas[0].id}" if len(criadas) == 1 else "/execucoes")

    def _edicao(fila_id: str, item_id: str | None, descricao_fn, transformar):
        fs = carregar()
        f = mod_filas.por_id(fs, fila_id)
        if "todo" not in f.fonte:
            raise Bloqueio("esta fila não é um TODO de camada: a edição é pelo agente")
        item = next((i for i in f.itens if i["id"] == item_id), None) if item_id else None
        if item_id and item is None:
            raise Bloqueio("o item mudou ou saiu da fila — recarregue")
        rel = todo_md.CAMADAS[f.fonte["todo"]]

        def aplicar(cwd: Path):
            doc = todo_md.ler(cwd / rel)
            todo_md.gravar(cwd / rel, transformar(doc, f, item), doc.hash)

        return ger.edicao_manual(f, item, descricao_fn(item), aplicar)

    @app.post("/fila/{fila_id}/item/{item_id}/{acao}")
    async def editar_item(fila_id: str, item_id: str, acao: str, valor: str = Form(""), data: str = Form("")):
        hoje = data or dt.date.today().isoformat()
        try:
            if acao == "status":
                ex = await run_in_threadpool(_edicao, fila_id, item_id, lambda i: f"Status de «{i['titulo'][:70]}» → {valor}",
                                             lambda d, f, i: todo_md.mudar_status(d, i["id"], valor))
            elif acao == "prioridade":
                ex = await run_in_threadpool(_edicao, fila_id, item_id, lambda i: f"Prioridade de «{i['titulo'][:70]}» → {valor}",
                                             lambda d, f, i: todo_md.mudar_prioridade(d, i["id"], valor))
            elif acao == "concluir":
                ex = await run_in_threadpool(_edicao, fila_id, item_id, lambda i: f"Baixa de «{i['titulo'][:70]}» ({hoje})",
                                             lambda d, f, i: todo_md.concluir(d, i["id"], hoje))
            else:
                return falha("ação desconhecida", 404)
        except (Bloqueio, KeyError, ValueError, todo_md.Conflito, gitops.ErroGit) as erro:
            return falha(str(erro))
        return ok(ir=f"/execucao/{ex.id}/validacao", mensagem="Edição feita num worktree — valide e commite.")

    @app.post("/fila/{fila_id}/adicionar")
    async def adicionar(fila_id: str, titulo: str = Form(...), secao: str = Form(""), referencia: str = Form(""),
                        prioridade: str = Form("Média"), responsavel: str = Form(""), status: str = Form("❌ Não iniciado")):
        def transformar(doc, f, _item):
            alvo = secao or f.fonte.get("secao") or ""
            if not alvo:
                raise Bloqueio("escolha a seção")
            return todo_md.adicionar(doc, alvo, {"titulo": titulo, "referencia": referencia, "prioridade": prioridade,
                                                 "responsavel": responsavel, "status": status})
        try:
            ex = await run_in_threadpool(_edicao, fila_id, None, lambda _i: f"Item novo: «{titulo[:70]}»", transformar)
        except (Bloqueio, KeyError, ValueError, todo_md.Conflito, gitops.ErroGit) as erro:
            return falha(str(erro))
        return ok(ir=f"/execucao/{ex.id}/validacao")

    @app.post("/fila/{fila_id}/varredura")
    async def varredura(fila_id: str):
        fs = carregar()
        f = mod_filas.por_id(fs, fila_id)
        camada = f.fonte.get("todo")
        if camada not in ("criativo", "pesquisa"):
            return falha("varredura só existe para Criativo e Pesquisa")
        cmd = [*config.python_do_projeto(), ".claude/skills/gerir-todo/todo.py", "varredura", camada]
        r = await run_in_threadpool(subprocess.run, cmd, cwd=raiz, capture_output=True, timeout=120,
                                    env=config.ambiente(), creationflags=config.SEM_JANELA)
        return ok(texto=(r.stdout + r.stderr).decode("utf-8", "replace"))

    # ── execuções ───────────────────────────────────────────────────────────

    @app.get("/execucoes", response_class=HTMLResponse)
    async def execucoes(request: Request):
        return pagina(request, "execucoes.html", lista=ger.listar(), vivas=ger.vivas(), maximo=ger.max)

    def obter_ou_none(ex_id: str):
        try:
            return ger.obter(ex_id)
        except Bloqueio:
            return None

    @app.get("/execucao/{ex_id}", response_class=HTMLResponse)
    async def execucao(request: Request, ex_id: str):
        ex = obter_ou_none(ex_id)
        if ex is None:
            return pagina(request, "erro.html", erro="Execução não encontrada.")
        evs = ger.eventos(ex_id)
        return pagina(request, "execucao.html", ex=ex, entradas=[Markup(html_entrada(e, ex)) for e in evs],
                      proximo=len(evs), viva=bool(ger.sessoes.get(ex_id) and ger.sessoes[ex_id].vivo))

    def assinatura(ex) -> str:
        return json.dumps([ex.estado, [p["request_id"] for p in ex.pendentes], ex.mensagem,
                           {k: v["estado"] for k, v in ex.checagens.items()}, ex.commit], ensure_ascii=False)

    # Atualização ao vivo por consulta curta (o navegador pergunta a cada 1,5 s), não por conexão aberta:
    # o navegador aceita só 6 conexões por endereço, e cada aba com EventSource segurava uma — com várias
    # abas da Central nada mais carregava. Voltar pelo histórico também matava o EventSource (2026-11-03).

    def resumo_vivo() -> dict:
        estados = [(e.id, e.estado, len(e.pendentes), e.commit, e.mensagem) for e in ger.listar()]
        bruto = json.dumps([estados, app.state.versao_arquivos], ensure_ascii=False).encode("utf-8")
        return {"v": hashlib.sha1(bruto).hexdigest()[:16], "atencao": len(ger.pedem_atencao()),
                "ativas": len(ger.ativas())}

    @app.get("/vivo")
    async def vivo():
        return resumo_vivo()

    @app.get("/execucao/{ex_id}/novidades")
    async def novidades(ex_id: str, desde: int = 0):
        ex = obter_ou_none(ex_id)
        if ex is None:
            return JSONResponse({"erro": "não existe"}, status_code=404)
        entradas = [{"i": e["i"], "html": html_entrada(e, ex)} for e in ger.eventos(ex_id, desde)]
        estado = {"estado": ex.estado, "rotulo": ex.rotulo, "mensagem": ex.mensagem, "ocupada": ex.ocupada,
                  "pendentes": [p["request_id"] for p in ex.pendentes], "commit": ex.commit,
                  "checagens": {k: v["estado"] for k, v in ex.checagens.items()}}
        return {"entradas": entradas, "estado": estado, "assinatura": assinatura(ex), **resumo_vivo()}

    async def acao_execucao(fn, *args, ir: str | None = None):
        try:
            await run_in_threadpool(fn, *args)
        except (Bloqueio, gitops.ErroGit, RuntimeError) as erro:
            return falha(str(erro))
        return ok(ir=ir) if ir else ok()

    @app.post("/execucao/{ex_id}/mensagem")
    async def mensagem(ex_id: str, texto: str = Form("")):
        return await acao_execucao(ger.enviar, ex_id, texto)

    @app.post("/execucao/{ex_id}/permissao")
    async def permissao(ex_id: str, request_id: str = Form(...), decisao: str = Form(...), motivo: str = Form("")):
        if decisao not in ("permitir", "sempre", "negar"):
            return falha("decisão inválida")
        return await acao_execucao(ger.permissao, ex_id, request_id, decisao, motivo)

    @app.post("/execucao/{ex_id}/interromper")
    async def interromper(ex_id: str):
        sessao = ger.sessoes.get(ex_id)
        if not (sessao and sessao.vivo):
            return falha("o agente não está rodando")
        return await acao_execucao(sessao.interromper)

    @app.post("/execucao/{ex_id}/finalizar")
    async def finalizar(ex_id: str):
        return await acao_execucao(ger.finalizar, ex_id, ir=f"/execucao/{ex_id}/validacao")

    @app.post("/execucao/{ex_id}/tentar-de-novo")
    async def tentar_de_novo(ex_id: str):
        return await acao_execucao(ger.tentar_de_novo, ex_id, ir=f"/execucao/{ex_id}")

    @app.post("/execucao/{ex_id}/retomar")
    async def retomar(ex_id: str):
        return await acao_execucao(ger.retomar, ex_id)

    @app.get("/execucao/{ex_id}/validacao", response_class=HTMLResponse)
    async def validacao(request: Request, ex_id: str):
        ex = obter_ou_none(ex_id)
        if ex is None:
            return pagina(request, "erro.html", erro="Execução não encontrada.")
        arquivos = await run_in_threadpool(ger.diff, ex_id) if ex.ativa or ex.estado == "erro" else []
        mensagem_commit = (ex.resultado or {}).get("commit") or (
            f"chore({ex.camada.lower() or 'central'}): {todo_md.sem_acento(ex.fila_nome).lower()}\n\n"
            + "\n".join(f"- {todo_md.sem_acento(i['titulo'])}" for i in ex.itens))
        em_rebase = bool(ex.modo == "worktree" and ex.cwd and Path(ex.cwd).exists() and ex.ativa
                         and await run_in_threadpool(gitops.em_rebase, Path(ex.cwd)))
        return pagina(request, "validacao.html", ex=ex, arquivos=arquivos, mensagem_commit=mensagem_commit,
                      proximo=len(ger.eventos(ex_id)), em_rebase=em_rebase,
                      fora=ger.fora_do_git(ex_id), unity_aberto=fontes.unity_aberto() if ex.modo == "principal" else False)

    @app.post("/execucao/{ex_id}/checagens")
    async def checagens(ex_id: str, so: str = Form("")):
        try:
            ger.obter(ex_id)
            if so == "unity":
                if fontes.unity_aberto():
                    return falha("Feche o Editor do Unity antes — o batchmode não roda com o projeto aberto.")
                if ger.obter(ex_id).modo != "principal":
                    return falha("unity-validar roda só em execução na árvore principal.")
            lista = await run_in_threadpool(ger.preparar_checagens, ex_id, so or None)
        except Bloqueio as erro:
            return falha(str(erro))
        if lista:
            threading.Thread(target=ger._executar_checagens, args=(ger.obter(ex_id), lista), daemon=True).start()
        return ok()

    @app.post("/execucao/{ex_id}/ajuste")
    async def ajuste(ex_id: str, texto: str = Form("")):
        return await acao_execucao(ger.ajuste, ex_id, texto, ir=f"/execucao/{ex_id}")

    @app.post("/execucao/{ex_id}/descartar")
    async def descartar(ex_id: str):
        return await acao_execucao(ger.descartar, ex_id, ir="/")

    @app.post("/execucao/{ex_id}/commit")
    async def commit(request: Request, ex_id: str):
        form = await request.form()
        if form.get("revisei") != "1":
            return falha("Marque «Revisei o diff» antes de commitar.")
        arquivos = form.getlist("arquivos")
        try:
            r = await run_in_threadpool(ger.commitar, ex_id, str(form.get("mensagem", "")), arquivos)
        except (Bloqueio, gitops.ErroGit) as erro:
            return falha(str(erro))
        if not r.ok:
            return falha("O pre-commit recusou o commit.", saida=r.texto[-4000:])
        return ok(ir=f"/execucao/{ex_id}/validacao")

    @app.post("/execucao/{ex_id}/resolver")
    async def resolver(ex_id: str, orientacao: str = Form("")):
        return await acao_execucao(ger.resolver_conflito, ex_id, orientacao, ir=f"/execucao/{ex_id}")

    @app.post("/execucao/{ex_id}/integrar")
    async def integrar(ex_id: str):
        try:
            r = await run_in_threadpool(ger.integrar, ex_id)
        except (Bloqueio, gitops.ErroGit) as erro:
            return falha(str(erro))
        return ok(ir=f"/execucao/{ex_id}/validacao") if r.ok else falha(r.texto[-1500:])

    # ── conversa livre e ações globais ──────────────────────────────────────

    @app.get("/conversa", response_class=HTMLResponse)
    async def conversa_livre(request: Request):
        agentes = sorted(p.stem for p in (raiz / ".claude/agents").glob("*.md"))
        return pagina(request, "conversa.html", agentes=agentes, presets=PRESETS)

    @app.post("/conversa")
    async def criar_conversa(agente: str = Form(""), modo: str = Form("worktree"), mensagem: str = Form(""),
                             preset: str = Form(""), confirmado: str = Form("")):
        if preset in PRESETS:
            agente, mensagem = PRESETS[preset][0], PRESETS[preset][1] + ("\n\n" + mensagem if mensagem.strip() else "")
        agentes = {p.stem for p in (raiz / ".claude/agents").glob("*.md")}
        if agente and agente not in agentes:
            return falha("agente desconhecido")
        if not mensagem.strip():
            return falha("escreva a mensagem para o agente")
        if modo not in ("worktree", "principal"):
            return falha("isolamento inválido")
        try:
            bloq, av = ger.avaliar(None, [], modo)
            if bloq:
                return falha(" ".join(bloq))
            if av and confirmado != "1":
                return falha("confirmar", 409, avisos=av)
            ex, _ = await run_in_threadpool(ger.criar, None, [], agente, mensagem.strip(), True, modo)
        except Bloqueio as erro:
            return falha(str(erro))
        return ok(ir=f"/execucao/{ex.id}")

    @app.get("/saude", response_class=HTMLResponse)
    async def saude(request: Request):
        info = await run_in_threadpool(fontes.saude, raiz)
        ultimo_uso = next((e.uso for e in ger.listar() if e.uso), {})
        return pagina(request, "saude.html", s=info, gates=app.state.gates, nomes_gates=list(GATES),
                      ferramentas=config.ferramentas(),
                      listener=fontes.listener(), uso=ultimo_uso)

    @app.post("/saude/gate")
    async def gate(nome: str = Form(...)):
        if nome not in GATES:
            return falha("checagem desconhecida")
        if nome == "unity-validar" and fontes.unity_aberto():
            return falha("Feche o Editor do Unity antes.")
        if app.state.gates.get(nome, {}).get("estado") == "rodando":
            return falha("já está rodando")
        cmd = (["dotnet", "test", "Desenvolvimento/Tests/Braziliation.Game.Tests/Braziliation.Game.Tests.csproj", "--nologo", "-v", "quiet"]
               if GATES[nome] is None else [*config.python_do_projeto(), *GATES[nome]])
        app.state.gates[nome] = {"estado": "rodando", "saida": "", "quando": dt.datetime.now().isoformat(timespec="seconds")}
        app.state.versao_arquivos += 1     # as outras abas da Saúde mostram «rodando» na hora

        def rodar():
            try:
                r = subprocess.run(cmd, cwd=raiz, capture_output=True, timeout=1800, env=config.ambiente({"CI": "true"}),
                                   creationflags=config.SEM_JANELA)
                app.state.gates[nome].update(estado="ok" if r.returncode == 0 else "falhou",
                                             saida=(r.stdout + r.stderr).decode("utf-8", "replace")[-6000:])
            except (OSError, subprocess.SubprocessError) as erro:
                app.state.gates[nome].update(estado="falhou", saida=str(erro))
            app.state.versao_arquivos += 1

        threading.Thread(target=rodar, daemon=True).start()
        return ok()

    # ── documentos e arquivos ───────────────────────────────────────────────

    @app.get("/doc", response_class=HTMLResponse)
    async def doc(request: Request, c: str, e: str = ""):
        try:
            base = base_de(e)
            alvo = seguro(base, c)
        except Bloqueio as erro:
            return pagina(request, "erro.html", erro=str(erro))
        if alvo.is_dir():
            filhos = sorted(p.relative_to(base).as_posix() + ("/" if p.is_dir() else "") for p in alvo.iterdir()
                            if not p.name.startswith("."))
            return pagina(request, "doc.html", caminho=c, html=None, filhos=filhos, execucao=e)
        if not alvo.is_file():
            return pagina(request, "erro.html", erro=f"{c} não existe.")
        texto = alvo.read_text(encoding="utf-8", errors="replace")
        html = md(texto, c, e) if alvo.suffix.lower() == ".md" else None
        return pagina(request, "doc.html", caminho=c, html=html, texto=None if html else texto[:200_000],
                      filhos=None, execucao=e)

    @app.get("/arquivo")
    async def arquivo(c: str, e: str = ""):
        try:
            alvo = seguro(base_de(e), c)
        except Bloqueio:
            return PlainTextResponse("fora do projeto", status_code=403)
        if not alvo.is_file() or alvo.suffix.lower() not in fontes.IMAGENS:
            return PlainTextResponse("só imagens", status_code=404)
        return FileResponse(alvo)

    if observar:
        threading.Thread(target=_observar, args=(app, raiz), daemon=True, name="observador").start()

    app.mount("/static", StaticFiles(directory=str(PASTA / "static")), name="static")
    protegido = Protecao(app, config.PORTA, hosts_extra, token)
    protecao_token["valor"] = protegido.token
    protegido.state = app.state     # os testes alcançam o gerenciador por aqui
    return protegido


def _observar(app: FastAPI, raiz: Path) -> None:
    """TODO editado no VS Code ou por um agente → o painel atualiza sozinho."""
    try:
        from watchfiles import watch
    except ImportError:
        return
    pastas = [p for p in (raiz / "Design", raiz / "Desenvolvimento" / "Docs", raiz / ".claude", raiz / "Central")
              if p.exists()]

    def interessa(_mudanca, caminho: str) -> bool:
        partes = Path(caminho).parts
        return caminho.endswith((".md", ".json")) and ".estado" not in partes and ".venv" not in partes

    try:
        for _ in watch(*pastas, watch_filter=interessa, debounce=800, raise_interrupt=False):
            app.state.versao_arquivos += 1
    except Exception:
        pass
