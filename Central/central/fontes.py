"""Leitura do que não é tabela de TODO: dívida técnica, entrevistas, listener, saúde e Markdown.

A Central só importa o parser do projeto (dependência de fora para dentro, ADR-012);
nada aqui escreve em arquivo do projeto.
"""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from html import escape
from pathlib import Path
from urllib.parse import quote, unquote

from markdown_it import MarkdownIt

from . import config

sys.path.insert(0, str(config.RAIZ / ".claude" / "skills" / "gerir-todo"))
import todo_md  # noqa: E402

IMAGENS = (".png", ".jpg", ".jpeg", ".gif", ".webp")


def _id(*partes: str) -> str:
    return hashlib.sha1("|".join(partes).encode("utf-8")).hexdigest()[:10]


# ── dívida técnica ───────────────────────────────────────────────────────────

def divida(raiz: Path) -> list[dict]:
    """Itens de `tech_debt.md`: blocos `- **Item:**` sob `### Alta|Média|Baixa`."""
    caminho = raiz / "Desenvolvimento/Docs/Tech/tech_debt.md"
    if not caminho.exists():
        return []
    itens, prioridade, atual = [], "", None
    for n, linha in enumerate(caminho.read_text(encoding="utf-8").splitlines(), start=1):
        m = re.match(r"^###\s+(Alta|Média|Baixa)\b", linha)
        if m:
            prioridade = m.group(1)
            continue
        if linha.startswith("## "):
            prioridade = ""
        m = re.match(r"^- \*\*(Item|Where|Why|Fix[^:]*):\*\*\s*(.*)$", linha)
        if m and prioridade:
            chave, valor = m.group(1), m.group(2).strip()
            if chave == "Item":
                atual = {"titulo": valor, "prioridade": prioridade, "linha": n, "onde": "", "por_que": "", "correcao": ""}
                itens.append(atual)
            elif atual is not None:
                atual[{"Where": "onde", "Why": "por_que"}.get(chave, "correcao")] = valor
    for i in itens:
        i.update({
            "id": _id("divida", i["titulo"]), "status": "❌", "texto_status": "❌ a pagar", "aberto": True,
            "responsavel": "", "secao": i["prioridade"], "arquivo": "Desenvolvimento/Docs/Tech/tech_debt.md",
            "referencia": i["onde"], "descricao": i["por_que"],
        })
    return itens


# ── entrevistas ──────────────────────────────────────────────────────────────

ENTREVISTAS = "Design/Pesquisa/Entrevistas"


def _meta(pasta: Path) -> dict:
    try:
        return json.loads((pasta / "meta.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def entrevistas(raiz: Path) -> list[dict]:
    """Uma linha por assunto+data em `_pendente-curadoria/`, mais o `_inbox/` ainda não transcrito."""
    base = raiz / ENTREVISTAS
    grupos: dict[tuple[str, str], list[dict]] = {}
    pendentes = base / "_pendente-curadoria"
    for pasta in sorted(p for p in pendentes.glob("*") if p.is_dir()) if pendentes.exists() else []:
        meta = _meta(pasta)
        assunto = meta.get("assunto") or "sem assunto"
        data = pasta.name[:10] if re.match(r"\d{4}-\d{2}-\d{2}", pasta.name) else "?"
        grupos.setdefault((assunto, data), []).append(meta)
    itens = []
    for (assunto, data), metas in sorted(grupos.items()):
        tipos: dict[str, int] = {}
        for m in metas:
            tipos[m.get("tipo", "?")] = tipos.get(m.get("tipo", "?"), 0) + 1
        resumo = ", ".join(f"{n} {t}" for t, n in sorted(tipos.items()))
        itens.append({
            "id": _id("entrevista", assunto, data), "titulo": f"{assunto} — {data}",
            "status": "❌", "texto_status": f"❌ {len(metas)} captura(s): {resumo}", "aberto": True,
            "prioridade": "Média", "responsavel": "", "secao": "_pendente-curadoria",
            "arquivo": f"{ENTREVISTAS}/_pendente-curadoria/", "referencia": "", "assunto": assunto, "data": data,
        })
    inbox = [p for p in (base / "_inbox").glob("*") if p.is_dir()] if (base / "_inbox").exists() else []
    if inbox:
        itens.insert(0, {
            "id": _id("entrevista", "_inbox"), "titulo": f"Transcrever o _inbox ({len(inbox)} captura(s))",
            "status": "❌", "texto_status": "❌ aguardando transcrever.py", "aberto": True, "prioridade": "Média",
            "responsavel": "", "secao": "_inbox", "arquivo": f"{ENTREVISTAS}/_inbox/", "referencia": "",
        })
    return itens


def lotes_de_entrevista(raiz: Path) -> list[dict]:
    lotes = []
    pasta = raiz / ENTREVISTAS / "_lotes"
    for lote in sorted((p for p in pasta.glob("*") if p.is_dir()), reverse=True) if pasta.exists() else []:
        etapa = "de-para gerado" if (lote / "de-para.md").exists() else ("mapa em edição" if (lote / "mapa.json").exists() else "linha do tempo")
        lotes.append({"nome": lote.name, "etapa": etapa})
    return lotes


def listener() -> dict:
    """Situação da tarefa agendada do listener do WhatsApp (ADR-009) e o fim do log."""
    estado = {"tarefa": "desconhecida", "log": []}
    if sys.platform == "win32":
        try:
            r = subprocess.run(["schtasks", "/query", "/tn", "Braziliation - Listener de entrevistas", "/fo", "csv", "/nh"],
                               capture_output=True, timeout=10, creationflags=config.SEM_JANELA)
            texto = r.stdout.decode("cp850", "replace").strip()
            if r.returncode == 0 and texto:
                estado["tarefa"] = texto.split('","')[-1].strip('"')
            else:
                estado["tarefa"] = "não registrada"
        except (OSError, subprocess.SubprocessError):
            pass
    log = config.RAIZ / ENTREVISTAS / "Ferramentas/whatsapp-listener/listener.log"
    if log.exists():
        with log.open("rb") as f:
            f.seek(max(0, log.stat().st_size - 4000))
            estado["log"] = f.read().decode("utf-8", "replace").splitlines()[-12:]
    return estado


# ── saúde ────────────────────────────────────────────────────────────────────

def git(raiz: Path, *args: str) -> str:
    try:
        r = subprocess.run(["git", *args], cwd=raiz, capture_output=True, timeout=15,
                           env=config.ambiente(), creationflags=config.SEM_JANELA)
        return r.stdout.decode("utf-8", "replace").strip()
    except (OSError, subprocess.SubprocessError):
        return ""


def saude(raiz: Path) -> dict:
    contagem = git(raiz, "rev-list", "--left-right", "--count", "@{u}...HEAD").split()
    unity = {}
    estado_unity = raiz / ".claude/state/unity-validar.json"
    if estado_unity.exists():
        try:
            unity = json.loads(estado_unity.read_text(encoding="utf-8"))
        except ValueError:
            pass
    alterados = [l for l in git(raiz, "status", "--porcelain").splitlines() if l.strip()]
    return {
        "branch": git(raiz, "rev-parse", "--abbrev-ref", "HEAD"),
        "ultimo_commit": git(raiz, "log", "-1", "--format=%h %s (%cr)"),
        "atras": contagem[0] if len(contagem) == 2 else "?",
        "frente": contagem[1] if len(contagem) == 2 else "?",
        "alterados": alterados,
        "hooks": git(raiz, "config", "--get", "core.hooksPath"),
        "unity": unity,
        "unity_aberto": unity_aberto(),
    }


def unity_aberto() -> bool:
    if sys.platform != "win32":
        return False
    try:
        r = subprocess.run(["tasklist", "/fi", "imagename eq Unity.exe", "/fo", "csv", "/nh"],
                           capture_output=True, timeout=10, creationflags=config.SEM_JANELA)
        return b"Unity.exe" in r.stdout
    except (OSError, subprocess.SubprocessError):
        return False


# ── Markdown ─────────────────────────────────────────────────────────────────

# html=False: texto vindo de pesquisa web ou do agente nunca vira HTML executável na Central.
_MD = MarkdownIt("commonmark", {"html": False, "linkify": False}).enable("table").enable("strikethrough")


def _resolver(destino: str, base_rel: str) -> str | None:
    """Link relativo de um .md do projeto → caminho relativo à raiz (ou None se sair dela)."""
    alvo = destino.split("#", 1)[0]
    if not alvo:
        return None
    partes = Path(base_rel).parent.joinpath(alvo).as_posix().split("/")
    pilha: list[str] = []
    for p in partes:
        if p in ("", "."):
            continue
        if p == "..":
            if not pilha:
                return None
            pilha.pop()
        else:
            pilha.append(p)
    return "/".join(pilha)


def renderizar_md(texto: str, base_rel: str = "", execucao: str = "") -> str:
    html = _MD.render(texto)
    sufixo = f"&e={quote(execucao)}" if execucao else ""

    def link(m: re.Match) -> str:
        attr, destino = m.group(1), m.group(2)
        if re.match(r"^[a-z]+:", destino):
            return f'{attr}="{destino}" target="_blank" rel="noopener noreferrer"' if attr == "href" else m.group(0)
        if destino.startswith("#") or destino.startswith("/"):
            return m.group(0)
        rel = _resolver(unquote(destino), base_rel)
        if rel is None:
            return m.group(0)
        rota = "arquivo" if rel.lower().endswith(IMAGENS) else "doc"
        return f'{attr}="/{rota}?c={quote(rel)}{sufixo}"'

    return re.sub(r'(href|src)="([^"]*)"', link, html)


def texto_simples(celula: str) -> str:
    return escape(todo_md.limpo(celula))
