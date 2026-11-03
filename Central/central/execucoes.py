"""Execuções: itens selecionados → sessão do agente → chat → validação → commit (ADR-012).

Regras de paralelismo:
- o mesmo item em duas execuções ativas é bloqueado;
- fila com isolamento "worktree" roda num worktree próprio e pode correr em paralelo com qualquer
  outra; se outra execução ativa lê do mesmo TODO, a Central avisa (o git costuma juntar mudanças
  em seções diferentes; se não juntar, o conflito aparece na integração e o responsável decide);
- fila com isolamento "principal" roda na árvore do projeto, uma por vez, e só começa com a árvore
  limpa — é o que garante que "descartar" devolve exatamente o estado anterior;
- no máximo `MAX_PARALELO` processos de agente vivos; o excedente espera na fila.
"""
from __future__ import annotations

import datetime as dt
import json
import secrets
import shlex
import shutil
import subprocess
import threading
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path

from . import config, conversa, fontes, gitops
from .agente import SessaoAgente

ATIVOS = {"na-fila", "preparando", "rodando", "aguardando-voce", "aguardando-validacao", "interrompida", "conflito"}
SEGURAM_A_ARVORE = ATIVOS - {"na-fila"}
ROTULOS = {
    "na-fila": "na fila", "preparando": "preparando", "rodando": "rodando", "aguardando-voce": "aguardando você",
    "aguardando-validacao": "aguardando validação", "interrompida": "interrompida",
    "conflito": "conflito na integração", "commitada": "commitada", "descartada": "descartada", "erro": "erro",
}
PEDEM_ATENCAO = {"aguardando-voce", "aguardando-validacao", "interrompida", "conflito", "erro"}


class Bloqueio(Exception):
    """A execução não pode acontecer (ou a ação não cabe no estado atual)."""


def agora() -> str:
    return dt.datetime.now().isoformat(timespec="seconds")


@dataclass
class Execucao:
    id: str
    fila_id: str
    fila_nome: str
    camada: str
    arquivo_fonte: str
    itens: list
    agente: str
    modo: str
    prompt: str
    estado: str = "na-fila"
    criada: str = ""
    atualizada: str = ""
    inicio_ts: float = 0.0
    cwd: str = ""
    branch: str = ""
    base: str = ""
    session_id: str = ""
    resultado: dict | None = None
    pendentes: list = field(default_factory=list)
    permitidas: list = field(default_factory=list)
    checagens: dict = field(default_factory=dict)
    commit: str = ""
    integrada: bool = False
    mensagem: str = ""
    avisos: list = field(default_factory=list)
    ultimo_evento_ts: float = 0.0
    ultimo_texto: str = ""
    uso: dict = field(default_factory=dict)

    @property
    def rotulo(self) -> str:
        return ROTULOS.get(self.estado, self.estado)

    @property
    def ativa(self) -> bool:
        return self.estado in ATIVOS

    @property
    def ids_itens(self) -> set[str]:
        return {i["id"] for i in self.itens}


def _prefixo(ferramenta: str, resumo: str) -> str:
    if ferramenta in ("Bash", "PowerShell"):
        try:
            partes = shlex.split(resumo, posix=False)
        except ValueError:
            partes = resumo.split()
        return " ".join(partes[:2])
    return ""


class Gerenciador:
    def __init__(self, raiz: Path | None = None, estado: Path | None = None, fabrica=SessaoAgente,
                 max_paralelo: int | None = None, zelador: bool = True):
        self.raiz = Path(raiz or config.RAIZ)
        self.dir = Path(estado or config.ESTADO) / "execucoes"
        self.dir.mkdir(parents=True, exist_ok=True)
        self.fabrica = fabrica
        self.max = max_paralelo or config.MAX_PARALELO
        self.trava = threading.RLock()
        self.execucoes: dict[str, Execucao] = {}
        self.sessoes: dict[str, SessaoAgente] = {}
        self.versao = 0
        self._n: dict[str, int] = {}
        self._carregar()
        if zelador:
            threading.Thread(target=self.limpar_sobras, daemon=True).start()
            threading.Thread(target=self._zelador, daemon=True, name="zelador").start()

    # ── persistência ────────────────────────────────────────────────────────

    def _pasta(self, ex_id: str) -> Path:
        return self.dir / ex_id

    def _salvar(self, ex: Execucao) -> None:
        ex.atualizada = agora()
        pasta = self._pasta(ex.id)
        pasta.mkdir(parents=True, exist_ok=True)
        tmp = pasta / "execucao.json.tmp"
        tmp.write_text(json.dumps(asdict(ex), ensure_ascii=False, indent=1), encoding="utf-8")
        tmp.replace(pasta / "execucao.json")
        self.versao += 1

    def _carregar(self) -> None:
        for arq in sorted(self.dir.glob("*/execucao.json")):
            try:
                ex = Execucao(**json.loads(arq.read_text(encoding="utf-8")))
            except (ValueError, TypeError):
                continue
            # Processo nenhum sobrevive a um reinício da Central.
            if ex.estado in ("rodando", "preparando") or (ex.estado == "aguardando-voce" and ex.pendentes):
                ex.estado, ex.pendentes = "interrompida", []
                ex.mensagem = "A Central reiniciou com esta execução em andamento. Use «Retomar»."
            self.execucoes[ex.id] = ex

    def _registrar(self, ex: Execucao, entrada: dict) -> None:
        arq = self._pasta(ex.id) / "eventos.jsonl"
        arq.parent.mkdir(parents=True, exist_ok=True)
        if ex.id not in self._n:
            self._n[ex.id] = self._contar(ex.id)
        n = self._n[ex.id]
        self._n[ex.id] = n + 1
        entrada = {"i": n, "ts": agora(), **entrada}
        with arq.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entrada, ensure_ascii=False) + "\n")
        self.versao += 1

    def _contar(self, ex_id: str) -> int:
        arq = self._pasta(ex_id) / "eventos.jsonl"
        if not arq.exists():
            return 0
        with arq.open("rb") as f:
            return sum(1 for _ in f)

    def eventos(self, ex_id: str, desde: int = 0) -> list[dict]:
        arq = self._pasta(ex_id) / "eventos.jsonl"
        if not arq.exists():
            return []
        linhas = arq.read_text(encoding="utf-8").splitlines()
        return [json.loads(l) for l in linhas[desde:] if l.strip()]

    # ── consulta ────────────────────────────────────────────────────────────

    def obter(self, ex_id: str) -> Execucao:
        try:
            return self.execucoes[ex_id]
        except KeyError:
            raise Bloqueio(f"execução {ex_id} não existe") from None

    def listar(self) -> list[Execucao]:
        return sorted(self.execucoes.values(), key=lambda e: e.criada, reverse=True)

    def ativas(self) -> list[Execucao]:
        return [e for e in self.listar() if e.ativa]

    def pedem_atencao(self) -> list[Execucao]:
        return [e for e in self.listar() if e.estado in PEDEM_ATENCAO or e.pendentes]

    def vivas(self) -> int:
        return sum(1 for s in self.sessoes.values() if s.vivo)

    def itens_em_execucao(self) -> dict[str, Execucao]:
        return {i: e for e in self.ativas() for i in e.ids_itens}

    # ── criação ─────────────────────────────────────────────────────────────

    def avaliar(self, fila, itens: list[dict], modo: str | None = None) -> tuple[list[str], list[str]]:
        bloqueios, avisos = [], []
        if fila is not None and fila.acompanhamento:
            bloqueios.append("Esta fila é só de acompanhamento: quem processa é a camada seguinte.")
        elif fila is not None and not itens:
            bloqueios.append("Selecione ao menos um item da fila.")
        ids = {i["id"] for i in itens}
        modo = modo or (fila.isolamento if fila is not None else "worktree")
        with self.trava:
            for e in self.ativas():
                comuns = ids & e.ids_itens
                if comuns:
                    titulos = ", ".join(f"«{i['titulo'][:50]}»" for i in itens if i["id"] in comuns)
                    bloqueios.append(f"{titulos} já está na execução {e.id} ({e.rotulo}).")
                elif fila is not None and modo == "worktree" and e.arquivo_fonte == fila.arquivo and fila.arquivo.endswith("TODO.md"):
                    avisos.append(f"A execução {e.id} ({e.fila_nome}) também mexe em {fila.arquivo}. Seções diferentes "
                                  "costumam se juntar sozinhas; se as duas mexerem nas mesmas linhas, o conflito aparece "
                                  "na hora do commit e você decide.")
            if modo == "principal":
                ocupante = next((e for e in self.ativas() if e.modo == "principal" and e.estado in SEGURAM_A_ARVORE), None)
                if ocupante:
                    avisos.append(f"A árvore principal está com a execução {ocupante.id} ({ocupante.fila_nome}). "
                                  "Esta entra na fila e começa quando aquela for commitada ou descartada.")
                else:
                    sujos = gitops.alteracoes(self.raiz)
                    if sujos:
                        bloqueios.append(
                            f"Há {len(sujos)} alteração(ões) sem commit na árvore principal "
                            f"({', '.join(p for _, p in sujos[:4])}{'…' if len(sujos) > 4 else ''}). Execução desta fila "
                            "roda na árvore principal e precisa começar limpa, para o descarte ser seguro — commite ou "
                            "descarte antes.")
            if self.vivas() >= self.max:
                avisos.append(f"Já há {self.vivas()} agente(s) rodando (limite {self.max}): esta entra na fila.")
        return bloqueios, avisos

    def criar(self, fila, itens: list[dict], agente: str, prompt: str, confirmado: bool = False,
              modo: str | None = None) -> tuple[Execucao | None, list[str]]:
        bloqueios, avisos = self.avaliar(fila, itens, modo)
        if bloqueios:
            raise Bloqueio(" ".join(bloqueios))
        if avisos and not confirmado:
            return None, avisos
        fila_id = fila.id if fila is not None else "conversa"
        ex = Execucao(
            id=f"{dt.datetime.now():%Y%m%d-%H%M%S}-{fila_id}-{secrets.token_hex(2)}",
            fila_id=fila_id, fila_nome=fila.nome if fila is not None else "Conversa livre",
            camada=fila.camada if fila is not None else "", arquivo_fonte=fila.arquivo if fila is not None else "",
            itens=[{"id": i["id"], "titulo": i["titulo"]} for i in itens], agente=agente,
            modo=modo or (fila.isolamento if fila is not None else "worktree"), prompt=prompt,
            criada=agora(), avisos=avisos)
        with self.trava:
            self.execucoes[ex.id] = ex
            pasta = self._pasta(ex.id)
            pasta.mkdir(parents=True, exist_ok=True)
            (pasta / "contrato.md").write_text(conversa.CONTRATO.format(id=ex.id, fila=ex.fila_nome), encoding="utf-8")
            self._salvar(ex)
            self._registrar(ex, {"tipo": "pedido", "texto": prompt})
        self._escalonar()
        return ex, avisos

    def edicao_manual(self, fila, item: dict | None, descricao: str, aplicar) -> Execucao:
        """Edição feita pelo responsável no painel (status, prioridade, baixa, item novo).

        Não toca a árvore principal: vai para um worktree próprio da fila e entra direto em
        "aguardando validação" — o commit segue o mesmo caminho das execuções com agente.
        Edições seguidas na mesma fila se acumulam na mesma execução até ela ser commitada."""
        with self.trava:
            ex = next((e for e in self.ativas() if e.fila_id == fila.id and not e.agente
                       and e.estado == "aguardando-validacao"), None)
            if ex is None and item is not None and item["id"] in self.itens_em_execucao():
                outra = self.itens_em_execucao()[item["id"]]
                raise Bloqueio(f"«{item['titulo'][:50]}» está na execução {outra.id} ({outra.rotulo}).")
        if ex is None:
            ex = Execucao(id=f"{dt.datetime.now():%Y%m%d-%H%M%S}-{fila.id}-manual-{secrets.token_hex(2)}",
                          fila_id=fila.id, fila_nome=fila.nome, camada=fila.camada, arquivo_fonte=fila.arquivo,
                          itens=[], agente="", modo="worktree", prompt="Edições manuais pelo painel",
                          estado="preparando", criada=agora())
            with self.trava:
                self.execucoes[ex.id] = ex
                self._salvar(ex)
            destino = config.pasta_worktrees(self.raiz) / ex.id
            ex.branch = f"central/{ex.id}"
            try:
                ex.base = gitops.criar_worktree(self.raiz, destino, ex.branch)
            except Exception as erro:
                with self.trava:
                    ex.estado, ex.mensagem = "erro", str(erro)
                    self._salvar(ex)
                raise
            ex.cwd = str(destino)
            ex.resultado = {"itens": [], "commit": ""}
        aplicar(Path(ex.cwd))
        with self.trava:
            if item is not None and item["id"] not in ex.ids_itens:
                ex.itens.append({"id": item["id"], "titulo": item["titulo"]})
            ex.resultado["itens"].append({"titulo": descricao, "situacao": "feito", "resumo": "edição manual no painel"})
            corpo = "\n".join(f"- {fontes.todo_md.sem_acento(i['titulo'])}" for i in ex.resultado["itens"])
            ex.resultado["commit"] = (f"docs(todo): edicoes manuais na fila {fontes.todo_md.sem_acento(fila.nome).lower()}"
                                      f"\n\n{corpo}\n")
            ex.estado = "aguardando-validacao"
            self._registrar(ex, {"tipo": "voce", "texto": descricao})
            self._salvar(ex)
        return ex

    # ── escalonamento ───────────────────────────────────────────────────────

    def _pode_iniciar(self, ex: Execucao) -> bool:
        if self.vivas() >= self.max:
            return False
        if ex.modo == "principal":
            if any(e.modo == "principal" and e.estado in SEGURAM_A_ARVORE and e.id != ex.id for e in self.execucoes.values()):
                return False
            if gitops.alteracoes(self.raiz):
                if "árvore principal" not in ex.mensagem:
                    ex.mensagem = "Esperando a árvore principal ficar limpa (há alterações sem commit)."
                    self._salvar(ex)
                return False
        return True

    def _escalonar(self) -> None:
        with self.trava:
            for ex in sorted((e for e in self.execucoes.values() if e.estado == "na-fila"), key=lambda e: e.criada):
                if self._pode_iniciar(ex):
                    ex.estado, ex.mensagem = "preparando", ""
                    self._salvar(ex)
                    threading.Thread(target=self._preparar, args=(ex.id,), daemon=True).start()

    def _preparar(self, ex_id: str) -> None:
        ex = self.execucoes[ex_id]
        try:
            if ex.modo == "worktree":
                destino = config.pasta_worktrees(self.raiz) / ex.id
                ex.branch = f"central/{ex.id}"
                ex.base = gitops.criar_worktree(self.raiz, destino, ex.branch)
                ex.cwd = str(destino)
            else:
                ex.cwd = str(self.raiz)
                ex.base = gitops.head(self.raiz)
            with self.trava:
                ex.inicio_ts = time.time()
                ex.estado = "rodando"
                self._salvar(ex)
                self._abrir_sessao(ex, ex.prompt)
        except Exception as erro:
            if isinstance(erro, FileNotFoundError) and erro.filename:
                erro = f"programa não encontrado: {erro.filename}"
            with self.trava:
                ex.estado, ex.mensagem = "erro", f"Não foi possível iniciar: {erro}"
                self._salvar(ex)
                self._registrar(ex, {"tipo": "nota", "texto": ex.mensagem})

    def tentar_de_novo(self, ex_id: str) -> None:
        """Execução que falhou ao iniciar (antes de o agente trabalhar) volta para a fila."""
        with self.trava:
            ex = self.obter(ex_id)
            if ex.estado != "erro":
                raise Bloqueio(f"a execução está {ex.rotulo}: só se tenta de novo o que deu erro ao iniciar")
            if "-manual-" in ex.id:
                raise Bloqueio("edição manual não se repete — faça a edição de novo pelo painel")
            ocupados = self.itens_em_execucao()
            if any(i in ocupados for i in ex.ids_itens):
                raise Bloqueio("um dos itens já está em outra execução")
        if ex.modo == "worktree" and ex.cwd and Path(ex.cwd).exists():
            gitops.remover_worktree(self.raiz, Path(ex.cwd), ex.branch)
        with self.trava:
            ex.cwd = ex.branch = ex.base = ex.session_id = ""
            ex.estado, ex.mensagem = "na-fila", ""
            self._registrar(ex, {"tipo": "nota", "texto": "Nova tentativa pedida pelo responsável."})
            self._salvar(ex)
        self._escalonar()

    def _abrir_sessao(self, ex: Execucao, mensagem: str, retomar: bool = False) -> None:
        sessao = self.fabrica(cwd=Path(ex.cwd), agente=ex.agente, contrato=self._pasta(ex.id) / "contrato.md",
                              nome=f"Central · {ex.fila_nome} · {ex.id[-4:]}",
                              ao_evento=lambda ev, i=ex.id: self._evento(i, ev),
                              retomar=ex.session_id if retomar and ex.session_id else None)
        self.sessoes[ex.id] = sessao
        sessao.iniciar()
        sessao.enviar(mensagem)

    # ── eventos do agente ───────────────────────────────────────────────────

    def _evento(self, ex_id: str, ev: dict) -> None:
        with self.trava:
            ex = self.execucoes.get(ex_id)
            if ex is None:
                return
            with (self._pasta(ex_id) / "bruto.jsonl").open("a", encoding="utf-8") as f:
                f.write(json.dumps(ev, ensure_ascii=False) + "\n")
            ex.ultimo_evento_ts = time.time()
            tipo = ev.get("type")
            if tipo == "_fim":
                self._fim_do_processo(ex, ev)
                return
            if tipo == "system" and ev.get("subtype") == "init":
                ex.session_id = ev.get("session_id", ex.session_id)
            if tipo == "rate_limit_event":
                ex.uso = ev.get("rate_limit_info", {})
            if tipo == "control_request" and ev.get("request", {}).get("subtype") == "can_use_tool":
                if self._permitida(ex, ev):
                    return
            for entrada in conversa.normalizar(ev):
                if entrada["tipo"] == "agente":
                    ex.ultimo_texto += entrada["texto"] + "\n"
                    entrada["texto"] = conversa.sem_bloco(entrada["texto"])
                    if not entrada["texto"]:
                        continue
                if entrada["tipo"] == "permissao":
                    ex.pendentes.append(entrada)
                    ex.estado = "aguardando-voce"
                if entrada["tipo"] == "fim_turno":
                    self._fim_do_turno(ex)
                self._registrar(ex, entrada)
            self._salvar(ex)

    def _permitida(self, ex: Execucao, ev: dict) -> bool:
        req = ev["request"]
        ferramenta = req.get("tool_name", "")
        resumo = conversa.resumo_ferramenta(ferramenta, req.get("input", {}))
        for regra in ex.permitidas:
            if regra["ferramenta"] == ferramenta and (not regra["prefixo"] or resumo.startswith(regra["prefixo"])):
                sessao = self.sessoes.get(ex.id)
                if sessao and sessao.vivo:
                    sessao.responder_permissao(ev.get("request_id", ""), True, req.get("input", {}))
                    self._registrar(ex, {"tipo": "nota", "texto": f"Permitido pela regra desta execução: {ferramenta} {resumo}"})
                    return True
        return False

    def _fim_do_turno(self, ex: Execucao) -> None:
        resultado = conversa.extrair_resultado(ex.ultimo_texto)
        ex.ultimo_texto = ""
        if resultado is not None and self._so_pede_decisao(ex, resultado):
            # Sem arquivo alterado não há o que validar: a resposta vem pelo chat e a sessão segue
            # viva (2026-11-03: o ADR da política de IA ia para a validação com o diff vazio).
            resultado = None
            self._registrar(ex, {"tipo": "nota", "texto": "O agente pediu decisão sem alterar arquivo — responda pelo chat."})
        if resultado is not None:
            ex.resultado = resultado
            ex.estado = "aguardando-validacao"
            sessao = self.sessoes.get(ex.id)
            if sessao:
                threading.Thread(target=sessao.encerrar, daemon=True).start()
            threading.Thread(target=self.rodar_checagens, args=(ex.id,), daemon=True).start()
        elif not ex.pendentes:
            ex.estado = "aguardando-voce"

    @staticmethod
    def _so_pede_decisao(ex: Execucao, resultado: dict) -> bool:
        situacoes = {i.get("situacao", "") for i in resultado.get("itens", []) if isinstance(i, dict)}
        if not situacoes or not situacoes <= {"precisa-decisao"}:
            return False
        cwd = Path(ex.cwd) if ex.cwd else None
        return cwd is not None and cwd.exists() and not gitops.alteracoes(cwd)

    def _fim_do_processo(self, ex: Execucao, ev: dict) -> None:
        self.sessoes.pop(ex.id, None)
        if ex.estado == "rodando" or (ex.estado == "aguardando-voce" and ex.pendentes):
            ex.estado, ex.pendentes = "interrompida", []
            detalhe = " / ".join(ev.get("stderr", [])[-3:])
            ex.mensagem = f"O processo do agente terminou no meio do trabalho (código {ev.get('codigo')}). {detalhe}".strip()
            self._registrar(ex, {"tipo": "nota", "texto": ex.mensagem + " Use «Retomar» para continuar."})
        self._salvar(ex)
        threading.Thread(target=self._escalonar, daemon=True).start()

    # ── ações do responsável ────────────────────────────────────────────────

    def enviar(self, ex_id: str, texto: str) -> None:
        texto = texto.strip()
        if not texto:
            raise Bloqueio("mensagem vazia")
        with self.trava:
            ex = self.obter(ex_id)
            if ex.estado not in ("aguardando-voce", "rodando", "interrompida", "aguardando-validacao"):
                raise Bloqueio(f"a execução está {ex.rotulo}: não recebe mensagem")
            self._registrar(ex, {"tipo": "voce", "texto": texto})
            ex.estado, ex.resultado, ex.mensagem = "rodando", None, ""
            sessao = self.sessoes.get(ex.id)
            if sessao and sessao.vivo:
                sessao.enviar(texto)
            else:
                if self.vivas() >= self.max:
                    raise Bloqueio(f"já há {self.vivas()} agentes rodando (limite {self.max}) — tente quando um terminar")
                self._abrir_sessao(ex, texto, retomar=True)
            self._salvar(ex)

    def retomar(self, ex_id: str) -> None:
        self.enviar(ex_id, "A sessão foi interrompida (a Central reiniciou ou o processo caiu). Continue de onde "
                           "parou; se já tinha terminado, encerre com o bloco de resultado.")

    def ajuste(self, ex_id: str, texto: str) -> None:
        self.enviar(ex_id, f"Ajuste pedido pelo responsável na validação:\n\n{texto.strip()}")

    def permissao(self, ex_id: str, request_id: str, decisao: str, motivo: str = "") -> None:
        with self.trava:
            ex = self.obter(ex_id)
            pedido = next((p for p in ex.pendentes if p["request_id"] == request_id), None)
            if pedido is None:
                raise Bloqueio("esse pedido de permissão já foi respondido ou expirou")
            sessao = self.sessoes.get(ex.id)
            if not (sessao and sessao.vivo):
                ex.pendentes = []
                ex.estado = "interrompida"
                self._salvar(ex)
                raise Bloqueio("o processo do agente não está mais rodando — use «Retomar»")
            permitir = decisao in ("permitir", "sempre")
            sessao.responder_permissao(request_id, permitir, pedido.get("entrada"), motivo)
            if decisao == "sempre":
                ex.permitidas.append({"ferramenta": pedido["ferramenta"], "prefixo": _prefixo(pedido["ferramenta"], pedido["resumo"])})
            ex.pendentes = [p for p in ex.pendentes if p["request_id"] != request_id]
            texto = {"permitir": "Permitido", "sempre": "Permitido sempre nesta execução", "negar": "Negado"}[decisao]
            self._registrar(ex, {"tipo": "decisao", "request_id": request_id,
                                 "texto": f"{texto}: {pedido['ferramenta']} {pedido['resumo']}" + (f" — {motivo}" if motivo else "")})
            if not ex.pendentes:
                ex.estado = "rodando"
            self._salvar(ex)

    def finalizar(self, ex_id: str) -> None:
        """O responsável leva a execução para a validação sem esperar o bloco de resultado."""
        with self.trava:
            ex = self.obter(ex_id)
            if ex.estado not in ("rodando", "aguardando-voce", "interrompida"):
                raise Bloqueio(f"a execução está {ex.rotulo}")
            sessao = self.sessoes.get(ex.id)
            ex.estado, ex.pendentes = "aguardando-validacao", []
            self._registrar(ex, {"tipo": "nota", "texto": "O responsável levou a execução para a validação."})
            self._salvar(ex)
        if sessao:
            sessao.encerrar(espera=5)
        threading.Thread(target=self.rodar_checagens, args=(ex_id,), daemon=True).start()

    def diff(self, ex_id: str) -> list[dict]:
        ex = self.obter(ex_id)
        if not ex.cwd or not Path(ex.cwd).exists():
            return []
        return gitops.diff(Path(ex.cwd))

    def fora_do_git(self, ex_id: str) -> list[str]:
        """Arquivos ignorados pelo git que mudaram durante a execução (o descarte não os desfaz)."""
        ex = self.obter(ex_id)
        if ex.modo != "principal" or not ex.inicio_ts:
            return []
        achados = []
        for pasta in ("Design/Pesquisa/Entrevistas/_inbox", "Design/Pesquisa/Entrevistas/_pendente-curadoria",
                      "Design/Pesquisa/Entrevistas/_processado", "Design/Pesquisa/Entrevistas/_lotes",
                      "Desenvolvimento/Assets/Plugins/Braziliation"):
            base = self.raiz / pasta
            if base.exists():
                for arq in base.rglob("*"):
                    if arq.is_file() and arq.stat().st_mtime >= ex.inicio_ts:
                        achados.append(arq.relative_to(self.raiz).as_posix())
                        if len(achados) >= 200:
                            return achados
        return achados

    # ── checagens ───────────────────────────────────────────────────────────

    def _checagens_para(self, ex: Execucao) -> dict[str, list[str]]:
        py = config.python_do_projeto()
        caminhos = [p for _, p in gitops.alteracoes(Path(ex.cwd))] if ex.cwd and Path(ex.cwd).exists() else []
        lista = {
            "todo.py validar": [*py, ".claude/skills/gerir-todo/todo.py", "validar"],
            "dotnet test": ["dotnet", "test", "Desenvolvimento/Tests/Braziliation.Game.Tests/Braziliation.Game.Tests.csproj",
                            "--nologo", "-v", "quiet"],
        }
        if any(p.startswith("Desenvolvimento/Assets/") for p in caminhos):
            lista["meta-check"] = [*py, ".claude/skills/meta-check/check_meta_pairs.py"]
        if any((p.startswith("Desenvolvimento/Assets/Art/") and p.endswith(".png")) or
               p.startswith("Design/ArteConceitual/Paletas/") for p in caminhos):
            lista["paletas"] = [*py, "Design/ArteFonte/Ferramentas/check_art_palettes.py"]
        if any(p.startswith(".claude/skills/gerir-todo/") for p in caminhos):
            lista["testes do parser"] = [*py, "-m", "unittest", "discover", "-s", ".claude/skills/gerir-todo/tests"]
        return lista

    def rodar_checagens(self, ex_id: str, so: str | None = None) -> None:
        ex = self.obter(ex_id)
        if not ex.cwd or not Path(ex.cwd).exists():
            return
        lista = self._checagens_para(ex)
        if so == "unity":
            if ex.modo != "principal":
                raise Bloqueio("unity-validar roda só em execução na árvore principal (o worktree não tem a Library do Unity)")
            if fontes.unity_aberto():
                raise Bloqueio("feche o Editor do Unity antes — o batchmode não roda com o projeto aberto")
            lista = {"unity-validar": [*config.python_do_projeto(), ".claude/skills/unity-validar/scripts/validar.py", "--testes"]}
        elif so:
            lista = {k: v for k, v in lista.items() if k == so}
        with self.trava:
            for nome in lista:
                ex.checagens[nome] = {"estado": "rodando", "saida": "", "quando": agora()}
            self._salvar(ex)
        for nome, cmd in lista.items():
            try:
                r = subprocess.run(cmd, cwd=ex.cwd, capture_output=True, timeout=1800,
                                   env=config.ambiente({"CI": "true"}), creationflags=config.SEM_JANELA)
                saida = (r.stdout + r.stderr).decode("utf-8", "replace")
                estado = "ok" if r.returncode == 0 else "falhou"
            except (OSError, subprocess.SubprocessError) as erro:
                saida, estado = str(erro), "falhou"
            with self.trava:
                ex.checagens[nome] = {"estado": estado, "saida": saida[-6000:], "quando": agora()}
                self._salvar(ex)
        with self.trava:
            falhas = [n for n in lista if ex.checagens[n]["estado"] != "ok"]
            self._registrar(ex, {"tipo": "nota", "texto": "Checagens: " + (
                "todas passaram." if not falhas else "falharam " + ", ".join(falhas) + ".")})

    # ── desfecho ────────────────────────────────────────────────────────────

    def descartar(self, ex_id: str) -> None:
        with self.trava:
            ex = self.obter(ex_id)
            if not ex.ativa and ex.estado != "erro":
                raise Bloqueio(f"a execução já está {ex.rotulo}")
            sessao = self.sessoes.pop(ex.id, None)
        if sessao:
            sessao.encerrar(espera=5)
        if ex.modo == "worktree" and ex.cwd and Path(ex.cwd).exists():
            gitops.remover_worktree(self.raiz, Path(ex.cwd), ex.branch)
        elif ex.modo == "principal" and ex.estado in SEGURAM_A_ARVORE:
            gitops.restaurar(self.raiz)
        with self.trava:
            ex.estado, ex.pendentes = "descartada", []
            self._registrar(ex, {"tipo": "nota", "texto": "Execução descartada: os arquivos voltaram ao estado anterior."})
            self._salvar(ex)
        self._escalonar()

    def commitar(self, ex_id: str, mensagem: str, caminhos: list[str]) -> gitops.Saida:
        with self.trava:
            ex = self.obter(ex_id)
            if ex.estado != "aguardando-validacao":
                raise Bloqueio(f"só se commita depois da validação — a execução está {ex.rotulo}")
            if not mensagem.strip():
                raise Bloqueio("mensagem de commit vazia")
            ex.mensagem = "Commit em andamento (o pre-commit roda os testes)…"
            self._salvar(ex)
        cwd = Path(ex.cwd)
        r = gitops.commitar(cwd, caminhos, mensagem)
        with self.trava:
            if not r.ok:
                ex.mensagem = "O pre-commit recusou o commit. Veja a saída, peça ajuste ao agente ou corrija."
                self._registrar(ex, {"tipo": "nota", "texto": "Pre-commit recusou o commit:\n" + r.texto[-3000:]})
                self._salvar(ex)
                return r
            ex.commit = gitops.head(cwd)
            self._registrar(ex, {"tipo": "nota", "texto": f"Commit {ex.commit[:9]} criado."})
        if ex.modo == "worktree":
            return self.integrar(ex_id, ja_commitado=True)
        with self.trava:
            ex.estado, ex.integrada = "commitada", True
            sobra = gitops.alteracoes(self.raiz)
            ex.mensagem = (f"{len(sobra)} arquivo(s) não selecionado(s) continuam sem commit na árvore principal."
                           if sobra else "")
            self._salvar(ex)
        self._escalonar()
        return r

    def integrar(self, ex_id: str, ja_commitado: bool = False) -> gitops.Saida:
        ex = self.obter(ex_id)
        if ex.modo != "worktree" or not ex.commit:
            raise Bloqueio("não há commit de worktree para integrar")
        cwd = Path(ex.cwd)
        if cwd.exists():
            gitops.restaurar(cwd)   # o que não foi selecionado sai junto com o worktree
        r = gitops.integrar(self.raiz, cwd, ex.branch)
        with self.trava:
            if r.ok:
                ex.commit = gitops.head(self.raiz)
                ex.estado, ex.integrada, ex.mensagem = "commitada", True, ""
                self._registrar(ex, {"tipo": "nota", "texto": f"Integrado ao {gitops.branch(self.raiz)} ({ex.commit[:9]})."})
            elif r.texto.startswith("conflito"):
                ex.estado, ex.mensagem = "conflito", r.texto
                self._registrar(ex, {"tipo": "nota", "texto": "Conflito na integração: " + r.texto +
                                     f" Resolva no worktree ({ex.cwd}) com `git rebase {gitops.branch(self.raiz)}` e clique em «Integrar», ou descarte."})
            else:
                ex.estado, ex.mensagem = "conflito", ("O commit existe no branch " + ex.branch + ", mas não entrou no "
                                                     "branch principal: " + r.texto[-600:])
                self._registrar(ex, {"tipo": "nota", "texto": ex.mensagem})
            self._salvar(ex)
        if r.ok and cwd.exists():
            gitops.remover_worktree(self.raiz, cwd, ex.branch)
        return r

    # ── manutenção ──────────────────────────────────────────────────────────

    def limpar_sobras(self) -> list[str]:
        """Apaga pasta em .git/central/wt/ que não é worktree registrado nem de execução ativa.

        Visto em 2026-11-03: um build do dotnet gravou `obj/` no worktree no mesmo segundo do
        descarte, e a pasta sobrou. A varredura não depende de saber quem escreveu."""
        pasta = config.pasta_worktrees(self.raiz)
        if not pasta.exists():
            return []
        registrados = gitops.worktrees_registrados(self.raiz)
        em_uso = {str(Path(e.cwd).resolve()).lower() for e in self.execucoes.values() if e.cwd and e.ativa}
        apagadas = []
        for d in pasta.iterdir():
            chave = str(d.resolve()).lower()
            if d.is_dir() and chave not in registrados and chave not in em_uso:
                shutil.rmtree(d, ignore_errors=True)
                apagadas.append(d.name)
        return apagadas

    def _zelador(self) -> None:
        while True:
            time.sleep(30)
            try:
                limite = time.time() - config.INATIVIDADE_MIN * 60
                with self.trava:
                    ociosas = [(e, self.sessoes.get(e.id)) for e in self.execucoes.values()
                               if e.estado == "aguardando-voce" and not e.pendentes and e.ultimo_evento_ts < limite]
                for ex, sessao in ociosas:
                    if sessao and sessao.vivo:
                        sessao.encerrar(espera=5)
                self._escalonar()
                self.limpar_sobras()
            except Exception:
                pass

    def encerrar_tudo(self) -> None:
        for sessao in list(self.sessoes.values()):
            sessao.encerrar(espera=3)
