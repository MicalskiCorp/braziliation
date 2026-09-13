"""
Parte mecânica da skill gerir-todo: listar pendências e varrer lacunas sem o agente
precisar ler todos os arquivos da camada.

A varredura criativa lia catálogo, pool, índices de cidade, personagens e arcos — dezenas
de KB — para produzir uma lista de poucas linhas. Aqui o código faz a leitura e o agente
recebe só a lista; o que exige julgamento (se entra no TODO, com que prioridade) continua
com ele.

Uso:
  py .claude/skills/gerir-todo/todo.py listar {pesquisa|criativo|dev}
  py .claude/skills/gerir-todo/todo.py varredura {criativo|pesquisa}
"""
import re
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TODOS = {
    "pesquisa": ROOT / "Design/Pesquisa/TODO.md",
    "criativo": ROOT / "Design/Criativo/TODO.md",
    "dev": ROOT / "Desenvolvimento/Docs/TODO.md",
}
CRIATIVO = ROOT / "Design/Criativo"
ABERTO = ("❌", "📋", "🔨", "⏸")
MARCADORES = [r"\{TODO\}", r"\*\(a definir\)\*", r"\*\(Escrever aqui\)\*", r"\*\(nenhum"]


def ler(p: Path) -> str:
    return p.read_text(encoding="utf-8") if p.exists() else ""


def chave(texto: str) -> str:
    """Normaliza nome para comparação: sem acento, sem espaço/pontuação, minúsculo."""
    t = unicodedata.normalize("NFKD", texto)
    return re.sub(r"[^a-z0-9]", "", "".join(c for c in t if not unicodedata.combining(c)).lower())


def limpo(celula: str) -> str:
    """Tira link, crase e ênfase de uma célula de tabela."""
    return re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", celula).replace("`", "").replace("*", "").strip()


def linhas_de_tabela(texto: str):
    """(seção, células) de cada linha de dados de tabela, pulando cabeçalho e separador."""
    secao, bloco = "", []
    for linha in texto.splitlines() + [""]:
        if linha.startswith("#"):
            secao = linha.lstrip("#").strip()
        if linha.startswith("|"):
            bloco.append(linha)
            continue
        if len(bloco) > 2:
            for l in bloco[2:]:
                yield secao, [c.strip() for c in l.strip().strip("|").split("|")]
        bloco = []


def status(celulas) -> str:
    for c in celulas:
        for s in ABERTO + ("✅",):
            if s in c:
                return s
    return ""


def listar(camada: str) -> None:
    texto = ler(TODOS[camada])
    por_secao = {}
    for secao, cel in linhas_de_tabela(texto):
        s = status(cel)
        if "Concluído" in secao or s not in ABERTO:
            continue
        alta = "Alta" in cel
        por_secao.setdefault(secao, []).append((s, alta, limpo(cel[0])))
    total = sum(len(v) for v in por_secao.values())
    print(f"{TODOS[camada].relative_to(ROOT).as_posix()} — {total} pendência(s) aberta(s)")
    for secao, itens in por_secao.items():
        contagem = " ".join(f"{s}{sum(1 for i in itens if i[0] == s)}" for s in ABERTO if any(i[0] == s for i in itens))
        altas = [i for i in itens if i[1]]
        print(f"\n## {secao} — {len(itens)} ({contagem}) · Alta: {len(altas)}")
        for s, _, nome in altas:
            print(f"   {s} {nome[:100]}")


def varredura_criativo() -> None:
    todo = ler(TODOS["criativo"])
    no_todo = lambda *nomes: any(n and n in todo for n in nomes)
    catalogo_txt = ler(CRIATIVO / "Lendas/catalogo.md")
    lendas = [limpo(c[0]) for _, c in linhas_de_tabela(catalogo_txt)]
    cita_lenda = lambda texto: any(chave(l) and chave(l) in chave(texto) for l in lendas)
    achados = []

    for arq in sorted(CRIATIVO.rglob("*.md")):
        if arq.name == "TODO.md":
            continue
        n = sum(len(re.findall(p, ler(arq))) for p in MARCADORES)
        if n:
            rel = arq.relative_to(CRIATIVO).as_posix()
            # index.md de cidade/estado é citado pelo nome da pasta; o resto, pelo nome do arquivo.
            citado = arq.parent.name if arq.name == "index.md" else arq.name
            achados.append(("Marcador aberto", f"{rel} ({n})", no_todo(citado)))

    for _, c in linhas_de_tabela(catalogo_txt):
        if "❌" in " ".join(c[1:]):
            achados.append(("Lenda não mapeada", limpo(c[0]), no_todo(limpo(c[0]))))

    for secao, c in linhas_de_tabela(ler(CRIATIVO / "Ideias/pool.md")):
        if secao == "Ideias" and "💡" in " ".join(c):  # a legenda de status também tem 💡
            achados.append(("Ideia 💡 Nova parada", limpo(c[1]) if len(c) > 1 else limpo(c[0]), False))

    for idx in sorted(CRIATIVO.glob("Estados/*/cidades/index.md")):
        for _, c in linhas_de_tabela(ler(idx)):
            if "📋" in " ".join(c):
                nome = limpo(c[0]).rstrip("/")
                achados.append(("Cidade em rascunho", f"{nome} ({idx.parts[-3]})", no_todo(nome)))

    for _, c in linhas_de_tabela(ler(CRIATIVO / "Historia/arcos.md")):
        if len(c) >= 5 and not cita_lenda(c[-1]):
            achados.append(("Arco sem lenda do catálogo", limpo(c[1]), no_todo(limpo(c[1]))))

    conceitos = todo.split("Concept Art Pendente", 1)[-1].split("\n## ", 1)[0]
    for _, c in linhas_de_tabela(ler(CRIATIVO / "Historia/personagens/index.md")):
        nome = limpo(c[0])
        if len(c) >= 3 and not cita_lenda(c[2]):
            achados.append(("Personagem sem lenda do catálogo", nome, no_todo(nome)))
        m = re.search(r"\(([^)]+\.md)\)", c[0])
        ficha = CRIATIVO / "Historia/personagens" / m.group(1) if m else None
        slug = re.sub(r"[^a-z0-9]+", "-", unicodedata.normalize("NFKD", nome).encode("ascii", "ignore").decode().lower()).strip("-")
        aprovado = (ROOT / "Design/ArteConceitual/Personagens" / slug / "concept.md").exists()
        if ficha and "Aparência" in ler(ficha) and not aprovado and nome not in conceitos:
            achados.append(("Personagem com Aparência sem concept art", nome, False))

    print(f"Varredura criativa — {len(achados)} achado(s); 'no TODO' = já citado em Design/Criativo/TODO.md")
    for tipo in dict.fromkeys(a[0] for a in achados):
        print(f"\n## {tipo}")
        for _, item, citado in (a for a in achados if a[0] == tipo):
            print(f"   {'no TODO ' if citado else 'NOVO    '} {item}")


def varredura_pesquisa() -> None:
    cobertura = chave(ler(ROOT / "Design/Pesquisa/index.md"))
    todo = chave(ler(TODOS["pesquisa"]))
    estados = [limpo(c[0]).rstrip("/") for _, c in linhas_de_tabela(ler(CRIATIVO / "Estados/index.md"))]
    sem = [e for e in estados if chave(e) not in cobertura]
    print(f"Varredura de pesquisa — {len(sem)} estado(s) do Criativo sem cobertura em Design/Pesquisa/index.md")
    for e in sem:
        print(f"   {'no TODO ' if chave(e) in todo else 'NOVO    '} {e}")


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if len(sys.argv) != 3:
        print(__doc__)
        return 2
    op, camada = sys.argv[1], sys.argv[2]
    if op == "listar" and camada in TODOS:
        listar(camada)
    elif op == "varredura" and camada == "criativo":
        varredura_criativo()
    elif op == "varredura" and camada == "pesquisa":
        varredura_pesquisa()
    elif op == "varredura" and camada == "dev":
        print("Varredura de Desenvolvimento = dotnet test (DocsConsistencyTests, TokenBudgetTests, ConventionGuardTests).")
    else:
        print(__doc__)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
