"""As N filas: registro em `Central/filas.json`, itens lidos pelo parser único dos TODOs."""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path

from . import config, fontes
from .fontes import todo_md

# Nome no TODO → arquivo em .claude/agents/.
AGENTES = {
    "historiador": "historiador", "gamecreative": "game-creative", "gamearchitect": "game-architect",
    "spriteartist": "sprite-artist", "unitydeveloper": "unity-developer", "gameplayengineer": "gameplay-engineer",
    "systemsdeveloper": "systems-developer", "techlead": "tech-lead", "qaengineer": "qa-engineer",
    "testengineer": "test-engineer", "agentarchitect": "agent-architect",
}
ORDEM_CAMADAS = ["Pesquisa", "Criativo", "Arte", "Desenvolvimento"]


def agente_do_responsavel(texto: str) -> str:
    """Primeiro @Agente citado; só 'Usuário' vira conversa com o @TechLead para ajudar a decidir."""
    for nome in re.findall(r"@([A-Za-z]+)", texto or ""):
        if nome.lower() in AGENTES:
            return AGENTES[nome.lower()]
    return "tech-lead"


@dataclass
class Fila:
    id: str
    camada: str
    nome: str
    fonte: dict
    agente: str = ""
    isolamento: str = "worktree"
    instrucao: str = ""
    nota: str = ""
    acompanhamento: bool = False
    itens: list[dict] = field(default_factory=list)
    hash: str = ""

    @property
    def arquivo(self) -> str:
        if "todo" in self.fonte:
            return todo_md.CAMADAS[self.fonte["todo"]]
        return {"divida": "Desenvolvimento/Docs/Tech/tech_debt.md",
                "entrevistas": fontes.ENTREVISTAS + "/"}.get(self.fonte.get("tipo", ""), "")

    @property
    def abertos(self) -> list[dict]:
        return [i for i in self.itens if i["aberto"]]

    def contagem(self) -> dict:
        ab = self.abertos
        return {
            "abertos": len(ab),
            "alta": sum(1 for i in ab if i["prioridade"] == "Alta"),
            "bloqueados": sum(1 for i in ab if i["status"] == "⏸"),
            "usuario": sum(1 for i in ab if "usu" in fontes.todo_md.sem_acento(i["responsavel"]).lower()),
        }

    def agente_do_item(self, item: dict) -> str:
        if self.agente == "@responsavel":
            return agente_do_responsavel(item.get("responsavel", ""))
        return self.agente

    def secao_pertence(self, secao: str) -> bool:
        if "secao" in self.fonte:
            return secao == self.fonte["secao"]
        if "secao_prefixo" in self.fonte:
            return secao.startswith(self.fonte["secao_prefixo"])
        return False


def registro(raiz: Path | None = None) -> list[dict]:
    caminho = (raiz or config.RAIZ) / "Central" / "filas.json"
    if not caminho.exists():
        caminho = config.CENTRAL / "filas.json"
    return json.loads(caminho.read_text(encoding="utf-8"))["filas"]


def carregar(raiz: Path | None = None) -> list[Fila]:
    raiz = raiz or config.RAIZ
    docs = {c: todo_md.ler(raiz / rel) for c, rel in todo_md.CAMADAS.items()}
    filas = []
    for r in registro(raiz):
        f = Fila(id=r["id"], camada=r["camada"], nome=r["nome"], fonte=r["fonte"], agente=r.get("agente", ""),
                 isolamento=r.get("isolamento", "worktree"), instrucao=r.get("instrucao", ""),
                 nota=r.get("nota", ""), acompanhamento=r.get("acompanhamento", False))
        if "todo" in f.fonte:
            doc = docs[f.fonte["todo"]]
            f.hash = doc.hash
            f.itens = [_dict(i) for i in doc.itens() if f.secao_pertence(i.secao) and not i.placeholder]
        elif f.fonte.get("tipo") == "divida":
            f.itens = fontes.divida(raiz)
        elif f.fonte.get("tipo") == "entrevistas":
            f.itens = fontes.entrevistas(raiz)
        filas.append(f)
    return filas


def _dict(item) -> dict:
    d = item.como_dict()
    d["titulo_md"] = item.bruto[0] if item.bruto else item.titulo
    d["descricao"] = item.campos.get("descricao", "")
    d["categoria"] = item.campos.get("categoria", "")
    d["data"] = item.campos.get("data", "")
    return d


def por_id(filas: list[Fila], fila_id: str) -> Fila:
    for f in filas:
        if f.id == fila_id:
            return f
    raise KeyError(fila_id)


def secoes_sem_fila(filas: list[Fila], raiz: Path | None = None) -> list[str]:
    """Seções com tabela nos TODOs que nenhuma fila cobre — o painel avisa, o teste falha."""
    raiz = raiz or config.RAIZ
    faltando = []
    for camada, rel in todo_md.CAMADAS.items():
        doc = todo_md.ler(raiz / rel)
        for t in doc.tabelas:
            if not t.campos or t.secao == todo_md.SECAO_CONCLUIDO:
                continue
            if not any("todo" in f.fonte and f.fonte["todo"] == camada and f.secao_pertence(t.secao) for f in filas):
                faltando.append(f"{rel} § {t.secao}")
    return faltando


def _handoff(item: dict) -> str:
    m = re.search(r"Handoffs/([^)\]\s`/]+\.md)", item.get("referencia", "") + " " + item.get("titulo", ""))
    return m.group(1) if m else ""


def dessincronias(filas: list[Fila], raiz: Path | None = None) -> list[str]:
    """Handoff aberto numa ponta e fechado (ou ausente) na outra, entre Pesquisa e Criativo."""
    raiz = raiz or config.RAIZ
    try:
        saida = por_id(filas, "pes-handoffs")
        entrada = por_id(filas, "cri-entrada")
    except KeyError:
        return []
    concluido_criativo = todo_md.ler(raiz / todo_md.CAMADAS["criativo"]).texto.split(f"## {todo_md.SECAO_CONCLUIDO}", 1)[-1]
    enviados = {_handoff(i): i for i in saida.abertos if _handoff(i)}
    recebidos = {_handoff(i): i for i in entrada.abertos if _handoff(i)}
    avisos = []
    for nome, item in enviados.items():
        if nome not in recebidos:
            if nome in concluido_criativo:
                avisos.append(f"«{item['titulo']}»: o Criativo já processou, mas a Pesquisa não deu baixa.")
            else:
                avisos.append(f"«{item['titulo']}»: aberto na Pesquisa e ausente da entrada do Criativo.")
    for nome, item in recebidos.items():
        if nome not in enviados:
            avisos.append(f"«{item['titulo']}»: na entrada do Criativo, mas a Pesquisa não o lista como pendente.")
    return avisos


def agrupadas(filas: list[Fila]) -> list[tuple[str, list[Fila]]]:
    return [(c, [f for f in filas if f.camada == c]) for c in ORDEM_CAMADAS]
