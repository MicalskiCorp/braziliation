"""
Parser único dos três TODOs de camada (ADR-012).

Por que existe: até 2026-11-03 havia dois leitores de TODO que discordavam — o hook de
sessão contava 31 pendências Alta no Criativo e o `todo.py listar` contava 29, porque uma
citação no meio da tabela de Lendas fazia o `todo.py` tratar duas linhas de dados como
cabeçalho. Agora o hook, a skill `gerir-todo`, o pre-commit e a Central leem e escrevem
pela mesma biblioteca, e o `validar` recusa tabela malformada antes do commit.

Vocabulário de status e esquema de tabela: `.claude/rules/todos.md`.
"""
from __future__ import annotations

import hashlib
import re
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]

CAMADAS = {
    "pesquisa": "Design/Pesquisa/TODO.md",
    "criativo": "Design/Criativo/TODO.md",
    "dev": "Desenvolvimento/Docs/TODO.md",
}

# Ordem importa: o primeiro símbolo encontrado na célula de status decide.
STATUS = {
    "❌": "não iniciado",
    "📋": "rascunho",
    "🔨": "em andamento",
    "⏸": "bloqueado ou aguardando",
    "🟡": "confirmação fraca ou divergência",
    "🎙": "relato oral não confirmado",
    "✅": "concluído",
}
ABERTOS = ("❌", "📋", "🔨", "⏸", "🟡", "🎙")
PRIORIDADES = ("Alta", "Média", "Baixa")
SECAO_CONCLUIDO = "Concluído"

# Cabeçalho (minúsculo, sem acento) -> campo canônico. A primeira coluna é sempre o título.
CAMPOS = {
    "item": "titulo", "estado": "titulo", "tema": "descricao", "decisao": "titulo",
    "asset": "titulo", "feature/sistema": "titulo",
    "arquivo": "referencia", "referencia": "referencia", "referencia tecnica": "referencia",
    "referencia criativa": "referencia", "referencia criativa (lore/ideia)": "referencia",
    "arquivo handoff": "referencia",
    "descricao": "descricao", "observacao": "descricao",
    "categoria destino em arteconceitual": "categoria",
    "responsavel": "responsavel", "prioridade": "prioridade", "status": "status", "data": "data",
}
SEPARADOR = re.compile(r"^\|\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)*\|?\s*$")
DATA_ISO = re.compile(r"\d{4}-\d{2}-\d{2}")


class Conflito(Exception):
    """O arquivo mudou desde a leitura — quem ia gravar precisa reler."""


def sem_acento(texto: str) -> str:
    t = unicodedata.normalize("NFKD", texto)
    return "".join(c for c in t if not unicodedata.combining(c))


def chave_cabecalho(texto: str) -> str:
    return sem_acento(limpo(texto)).lower().strip()


def limpo(celula: str) -> str:
    """Tira link, crase e ênfase de uma célula de tabela."""
    return re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", celula).replace("`", "").replace("*", "").strip()


def celulas(linha: str) -> list[str]:
    return [c.strip() for c in linha.strip().strip("|").split("|")]


def status_de(texto: str) -> str:
    for s in STATUS:
        if s in texto:
            return s
    return ""


def hash_texto(texto: str) -> str:
    return hashlib.sha1(texto.encode("utf-8")).hexdigest()


@dataclass
class Item:
    id: str
    arquivo: str
    secao: str
    titulo: str
    bruto: list[str]
    campos: dict[str, str]
    linha: int
    status: str
    placeholder: bool = False

    @property
    def aberto(self) -> bool:
        return not self.placeholder and self.secao != SECAO_CONCLUIDO and self.status in ABERTOS

    @property
    def prioridade(self) -> str:
        return limpo(self.campos.get("prioridade", ""))

    @property
    def responsavel(self) -> str:
        return limpo(self.campos.get("responsavel", ""))

    @property
    def referencia(self) -> str:
        return self.campos.get("referencia", "")

    @property
    def texto_status(self) -> str:
        return self.campos.get("status", "")

    def como_dict(self) -> dict:
        return {
            "id": self.id, "arquivo": self.arquivo, "secao": self.secao, "titulo": self.titulo,
            "status": self.status, "texto_status": self.texto_status, "prioridade": self.prioridade,
            "responsavel": self.responsavel, "referencia": self.referencia, "aberto": self.aberto,
            "linha": self.linha + 1,
        }


@dataclass
class Tabela:
    secao: str
    inicio: int            # índice da linha de cabeçalho
    fim: int               # índice da última linha da tabela
    cabecalho: list[str]
    campos: list[str]
    itens: list[Item] = field(default_factory=list)
    problemas: list[str] = field(default_factory=list)


@dataclass
class Documento:
    caminho: Path
    texto: str
    linhas: list[str]
    tabelas: list[Tabela]
    secoes: list[tuple[int, int, str]]   # (índice da linha, nível, título)

    @property
    def hash(self) -> str:
        return hash_texto(self.texto)

    @property
    def relativo(self) -> str:
        return relativo_canonico(self.caminho)

    def itens(self, so_abertos: bool = False) -> list[Item]:
        todos = [i for t in self.tabelas for i in t.itens]
        return [i for i in todos if i.aberto] if so_abertos else todos

    def item(self, item_id: str) -> Item:
        for i in self.itens():
            if i.id == item_id:
                return i
        raise KeyError(f"item {item_id} não existe em {self.relativo}")

    def nomes_de_secao(self) -> list[str]:
        return [t for _, _, t in self.secoes]


def _id(arquivo: str, secao: str, titulo: str, vistos: dict) -> str:
    base = hashlib.sha1(f"{arquivo}|{secao}|{titulo}".encode("utf-8")).hexdigest()[:10]
    vistos[base] = vistos.get(base, 0) + 1
    return base if vistos[base] == 1 else f"{base}-{vistos[base]}"


def relativo_canonico(caminho: Path) -> str:
    """Caminho do TODO relativo à raiz do projeto — o mesmo numa cópia (worktree da Central),
    para o id de um item não depender de onde o arquivo foi lido."""
    posix = caminho.as_posix()
    for rel in CAMADAS.values():
        if posix.endswith("/" + rel) or posix == rel:
            return rel
    try:
        return caminho.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return posix


def analisar(texto: str, caminho: Path) -> Documento:
    linhas = texto.splitlines()
    arquivo = relativo_canonico(caminho)
    secoes, tabelas, vistos = [], [], {}
    secao = ""
    i = 0
    while i < len(linhas):
        linha = linhas[i]
        m = re.match(r"^(#{1,6})\s+(.*)$", linha)
        if m:
            secao = m.group(2).strip()
            secoes.append((i, len(m.group(1)), secao))
            i += 1
            continue
        if not linha.startswith("|"):
            i += 1
            continue
        inicio = i
        while i < len(linhas) and linhas[i].startswith("|"):
            i += 1
        bloco = linhas[inicio:i]
        cab = celulas(bloco[0])
        tabela = Tabela(secao, inicio, i - 1, cab, [])
        if len(bloco) < 2 or not SEPARADOR.match(bloco[1]):
            tabela.problemas.append(
                f"linha {inicio + 1}: tabela sem linha separadora logo abaixo do cabeçalho "
                "(citação ou linha em branco no meio de uma tabela quebra a tabela em duas)")
            tabelas.append(tabela)
            continue
        tabela.campos = ["titulo"] + [CAMPOS.get(chave_cabecalho(c), "?" + c) for c in cab[1:]]
        for n, bruta in enumerate(bloco[2:], start=inicio + 2):
            cel = celulas(bruta)
            titulo = limpo(cel[0]) if cel else ""
            campos = {}
            for k, c in zip(tabela.campos, cel):
                campos[k] = c
            st = status_de(campos.get("status", "")) or status_de(" ".join(cel[1:]))
            item = Item(_id(arquivo, secao, titulo, vistos), arquivo, secao, titulo, cel, campos, n, st,
                        placeholder=cel[0].startswith("*("))
            if len(cel) != len(cab):
                tabela.problemas.append(f"linha {n + 1}: {len(cel)} células, cabeçalho tem {len(cab)}")
            tabela.itens.append(item)
        tabelas.append(tabela)
    return Documento(caminho, texto, linhas, tabelas, secoes)


def ler(caminho: Path | str) -> Documento:
    caminho = Path(caminho)
    if not caminho.is_absolute():
        caminho = ROOT / caminho
    texto = caminho.read_text(encoding="utf-8") if caminho.exists() else ""
    return analisar(texto, caminho)


def ler_camada(camada: str, raiz: Path | None = None) -> Documento:
    base = raiz or ROOT
    return ler(base / CAMADAS[camada])


def camada_de(doc: Documento) -> str:
    for nome, rel in CAMADAS.items():
        if doc.relativo.endswith(rel):
            return nome
    return ""


# ── validação ────────────────────────────────────────────────────────────────

def validar(doc: Documento) -> list[str]:
    """Problemas de formato. Lista vazia = arquivo íntegro."""
    erros = []
    camada = camada_de(doc)
    for t in doc.tabelas:
        erros.extend(t.problemas)
        if not t.campos:
            continue
        for c in t.campos:
            if c.startswith("?"):
                erros.append(f"linha {t.inicio + 1}: cabeçalho desconhecido «{c[1:]}» "
                             "(ver o esquema em .claude/rules/todos.md)")
        concluido = t.secao == SECAO_CONCLUIDO
        for item in t.itens:
            onde = f"linha {item.linha + 1} ({t.secao})"
            if item.placeholder:
                continue
            if concluido:
                if not DATA_ISO.search(item.campos.get("data", "")):
                    erros.append(f"{onde}: item concluído sem data AAAA-MM-DD")
                continue
            if not item.status:
                erros.append(f"{onde}: sem status do vocabulário ({' '.join(STATUS)}) — «{item.titulo[:60]}»")
            elif item.status == "✅":
                regra = ("a linha sai e o registro é o commit" if camada == "dev"
                         else f"mover para ## {SECAO_CONCLUIDO} com a data")
                erros.append(f"{onde}: item ✅ fora de {SECAO_CONCLUIDO} — {regra} — «{item.titulo[:60]}»")
            if "prioridade" in item.campos and item.prioridade not in PRIORIDADES:
                erros.append(f"{onde}: prioridade «{item.prioridade}» fora de {'/'.join(PRIORIDADES)}")
    return erros


# ── escrita ──────────────────────────────────────────────────────────────────

def _celula(texto: str) -> str:
    return texto.replace("|", "/").replace("\n", " ").strip()


def _linha(valores: list[str]) -> str:
    return "| " + " | ".join(_celula(v) for v in valores) + " |"


def _tabela_da_secao(doc: Documento, secao: str) -> Tabela:
    for t in doc.tabelas:
        if t.secao == secao and t.campos:
            return t
    raise KeyError(f"seção «{secao}» sem tabela em {doc.relativo}")


def _texto(linhas: list[str], original: str) -> str:
    return "\n".join(linhas) + ("\n" if original.endswith("\n") else "")


def mudar_campo(doc: Documento, item_id: str, campo: str, valor: str) -> str:
    item = doc.item(item_id)
    tabela = _tabela_da_secao(doc, item.secao)
    if campo not in tabela.campos:
        raise KeyError(f"a seção «{item.secao}» não tem coluna {campo}")
    cel = list(item.bruto)
    cel[tabela.campos.index(campo)] = valor
    linhas = list(doc.linhas)
    linhas[item.linha] = _linha(cel)
    return _texto(linhas, doc.texto)


def mudar_status(doc: Documento, item_id: str, valor: str) -> str:
    if not status_de(valor):
        raise ValueError(f"status «{valor}» sem símbolo do vocabulário")
    return mudar_campo(doc, item_id, "status", valor)


def mudar_prioridade(doc: Documento, item_id: str, valor: str) -> str:
    if valor not in PRIORIDADES:
        raise ValueError(f"prioridade «{valor}» fora de {'/'.join(PRIORIDADES)}")
    return mudar_campo(doc, item_id, "prioridade", valor)


def adicionar(doc: Documento, secao: str, valores: dict[str, str]) -> str:
    """Acrescenta uma linha no fim da tabela da seção. `valores` usa os campos canônicos."""
    tabela = _tabela_da_secao(doc, secao)
    if not valores.get("titulo"):
        raise ValueError("item sem título")
    linhas = list(doc.linhas)
    nova = _linha([valores.get(c, "") for c in tabela.campos])
    fim = tabela.fim
    # Linha-placeholder "*(nenhum pendente...)*" sai quando entra o primeiro item real.
    if tabela.itens and all(i.placeholder for i in tabela.itens):
        for i in sorted((i.linha for i in tabela.itens), reverse=True):
            del linhas[i]
        fim = tabela.inicio + 1
    linhas.insert(fim + 1, nova)
    return _texto(linhas, doc.texto)


def concluir(doc: Documento, item_id: str, data: str) -> str:
    """Regra de baixa da camada: Pesquisa e Criativo movem para ## Concluído com a data;
    Desenvolvimento tira a linha (o registro é o commit)."""
    if not DATA_ISO.fullmatch(data):
        raise ValueError("data no formato AAAA-MM-DD")
    item = doc.item(item_id)
    linhas = list(doc.linhas)
    del linhas[item.linha]
    if camada_de(doc) != "dev":
        alvo = _tabela_da_secao(doc, SECAO_CONCLUIDO)
        pos = alvo.fim if alvo.fim < item.linha else alvo.fim - 1
        linhas.insert(pos + 1, _linha([item.bruto[0], data]))
    return _texto(linhas, doc.texto)


def gravar(caminho: Path | str, texto: str, hash_esperado: str) -> None:
    """Grava só se o arquivo ainda é o que foi lido (escrita otimista)."""
    caminho = Path(caminho)
    if not caminho.is_absolute():
        caminho = ROOT / caminho
    bruto = caminho.read_bytes() if caminho.exists() else b""
    atual = bruto.decode("utf-8").replace("\r\n", "\n")
    if hash_texto(atual) != hash_esperado:
        raise Conflito(f"{caminho.name} mudou desde a leitura — recarregue antes de gravar")
    antes = validar(analisar(atual, caminho))
    depois = validar(analisar(texto, caminho))
    if len(depois) > len(antes):
        raise ValueError("a gravação deixaria o TODO malformado: " + "; ".join(depois[:3]))
    # Mantém o fim de linha que o arquivo já tinha (autocrlf=true faz worktree nascer em CRLF).
    caminho.write_text(texto, encoding="utf-8", newline="\r\n" if b"\r\n" in bruto else "\n")
