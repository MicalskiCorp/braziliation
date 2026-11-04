"""Uso de tokens de uma execução, lido do `bruto.jsonl` (o stream-json que o agente escreveu).

O que pesa é o contexto relido: cada requisição ao modelo manda a conversa inteira de novo (quase
toda do cache, mais barata, mas conta no limite do plano). Por isso o painel mostra requisições e
tamanho do contexto, não só o total — medido em 2026-11-04, as 5 execuções de Unity/UI somavam 82%
dos tokens lidos das 15 primeiras, e o contexto delas chegava a 270 mil tokens (ADR-015).

Formato confirmado na 2.1.277 e na 2.1.318:
- cada bloco de uma resposta chega como um evento `assistant` com o mesmo `message.id` e o mesmo
  `usage` — uma requisição é um id, não um evento; o `output_tokens` desses eventos é parcial;
- evento com `parent_tool_use_id` é de subagente: fica fora da curva do contexto principal;
- o `result` de cada turno traz o `usage` do turno (exato, com saída e pensamento) e o
  `total_cost_usd` ACUMULADO do processo — somar os `result` conta o custo várias vezes; uma
  retomada (`--resume`) continua a conta da sessão;
- `system`/`compact_boundary` marca uma compactação, com `compact_metadata.pre_tokens`.
"""
from __future__ import annotations

import json
from pathlib import Path

from . import conversa

CH_POR_TOKEN = 3.5          # estimativa para resultados de ferramenta (o stream não diz o tamanho em tokens)
MOD = "braziliation-economia"

_cache: dict[str, tuple[int, int, dict]] = {}


def _texto(conteudo) -> str:
    if isinstance(conteudo, str):
        return conteudo
    if isinstance(conteudo, list):
        return "".join(c.get("text", "") for c in conteudo if isinstance(c, dict))
    return ""


def analisar(linhas) -> dict:
    """Resumo de uso a partir das linhas do stream-json. Pura: os testes chamam direto."""
    vistos: set[str] = set()
    contexto: list[int] = []
    por_mensagem = {"entrada": 0, "cache_lido": 0, "cache_escrito": 0}
    turnos = {"entrada": 0, "cache_lido": 0, "cache_escrito": 0, "saida": 0, "pensamento": 0}
    n_turnos = 0
    custo_fechado, custo_atual = 0.0, 0.0
    compactacoes: list[dict] = []
    chamadas: dict[str, tuple[str, str]] = {}
    resultados: list[tuple[int, int, str, str]] = []   # (requisição em que entrou, chars, ferramenta, resumo)
    plugins: list[str] = []
    versao = modelo = ""
    for bruta in linhas:
        try:
            ev = json.loads(bruta)
        except (ValueError, TypeError):
            continue
        if not isinstance(ev, dict):
            continue
        tipo = ev.get("type")
        if tipo == "system":
            sub = ev.get("subtype")
            if sub == "init":
                plugins = [p.get("name", "") for p in ev.get("plugins") or [] if isinstance(p, dict)]
                versao = ev.get("claude_code_version", versao)
                modelo = ev.get("model", modelo)
            elif sub == "compact_boundary":
                meta = ev.get("compact_metadata") or {}
                compactacoes.append({"gatilho": meta.get("trigger", ""), "antes": meta.get("pre_tokens") or 0,
                                     "requisicao": len(contexto)})
            continue
        if ev.get("parent_tool_use_id"):
            continue
        if tipo == "assistant":
            msg = ev.get("message") or {}
            for bloco in msg.get("content") or []:
                if isinstance(bloco, dict) and bloco.get("type") == "tool_use":
                    nome = bloco.get("name", "?")
                    chamadas[bloco.get("id", "")] = (nome, conversa.resumo_ferramenta(nome, bloco.get("input", {})))
            mid, uso = msg.get("id"), msg.get("usage")
            if mid and uso and mid not in vistos:
                vistos.add(mid)
                e, cl, ce = (uso.get("input_tokens") or 0, uso.get("cache_read_input_tokens") or 0,
                             uso.get("cache_creation_input_tokens") or 0)
                contexto.append(e + cl + ce)
                por_mensagem["entrada"] += e
                por_mensagem["cache_lido"] += cl
                por_mensagem["cache_escrito"] += ce
        elif tipo == "user":
            conteudo = (ev.get("message") or {}).get("content")
            for bloco in conteudo if isinstance(conteudo, list) else []:
                if isinstance(bloco, dict) and bloco.get("type") == "tool_result":
                    nome, resumo = chamadas.get(bloco.get("tool_use_id", ""), ("?", ""))
                    resultados.append((len(contexto), len(_texto(bloco.get("content"))), nome, resumo))
        elif tipo == "result":
            n_turnos += 1
            uso = ev.get("usage") or {}
            turnos["entrada"] += uso.get("input_tokens") or 0
            turnos["cache_lido"] += uso.get("cache_read_input_tokens") or 0
            turnos["cache_escrito"] += uso.get("cache_creation_input_tokens") or 0
            turnos["saida"] += uso.get("output_tokens") or 0
            turnos["pensamento"] += (uso.get("output_tokens_details") or {}).get("thinking_tokens") or 0
            custo = ev.get("total_cost_usd")
            if isinstance(custo, (int, float)):
                if custo < custo_atual:        # processo novo que não continuou a conta
                    custo_fechado += custo_atual
                custo_atual = float(custo)

    # Turno em andamento ainda não tem `result`: o que passou dele vem das mensagens.
    base = turnos if n_turnos and turnos["cache_lido"] + turnos["cache_escrito"] >= (
        por_mensagem["cache_lido"] + por_mensagem["cache_escrito"]) else por_mensagem
    lidos = base["entrada"] + base["cache_lido"] + base["cache_escrito"]
    n_req = len(contexto)
    maiores = sorted(
        ({"ferramenta": nome, "resumo": resumo, "tokens": round(ch / CH_POR_TOKEN),
          "relido": round(ch / CH_POR_TOKEN * max(n_req - idx, 0))}
         for idx, ch, nome, resumo in resultados),
        key=lambda r: r["relido"], reverse=True)[:5]
    return {
        "requisicoes": n_req,
        "contexto_inicial": contexto[0] if contexto else 0,
        "contexto_max": max(contexto) if contexto else 0,
        "contexto_medio": round(sum(contexto) / n_req) if n_req else 0,
        "lidos": lidos,
        "cache_lido": base["cache_lido"],
        "cache_escrito": base["cache_escrito"],
        "saida": turnos["saida"],
        "pensamento": turnos["pensamento"],
        "turnos": n_turnos,
        "custo_usd": round(custo_fechado + custo_atual, 2),
        "compactacoes": compactacoes,
        "maiores": maiores,
        "versao": versao,
        "modelo": modelo,
        "mod_carregado": MOD in plugins,
    }


def resumo(pasta: Path) -> dict | None:
    """Resumo da execução guardada em `pasta`; None se o agente ainda não escreveu nada."""
    bruto = Path(pasta) / "bruto.jsonl"
    try:
        st = bruto.stat()
    except OSError:
        return None
    chave = str(bruto)
    guardado = _cache.get(chave)
    if guardado and guardado[0] == st.st_size and guardado[1] == st.st_mtime_ns:
        return guardado[2]
    with bruto.open(encoding="utf-8", errors="replace") as f:
        dado = analisar(f)
    if not dado["requisicoes"] and not dado["turnos"]:
        return None
    _cache[chave] = (st.st_size, st.st_mtime_ns, dado)
    return dado


def agrupar(linhas: list[tuple]) -> list[dict]:
    """Médias por fila, separando execuções com e sem janela de compactação (o antes e depois)."""
    grupos: dict[tuple, dict] = {}
    for ex, r in linhas:
        janela = (ex.economia or {}).get("janela") or 0
        g = grupos.setdefault((ex.fila_nome, bool(janela)), {
            "fila": ex.fila_nome, "fila_id": ex.fila_id, "janela": janela, "n": 0, "lidos": 0,
            "requisicoes": 0, "contexto_max": 0, "custo_usd": 0.0, "compactacoes": 0})
        g["n"] += 1
        g["lidos"] += r["lidos"]
        g["requisicoes"] += r["requisicoes"]
        g["contexto_max"] += r["contexto_max"]
        g["custo_usd"] += r["custo_usd"]
        g["compactacoes"] += len(r["compactacoes"])
    saida = []
    for g in grupos.values():
        n = g["n"]
        saida.append({**g, "lidos_medio": g["lidos"] // n, "requisicoes_medio": g["requisicoes"] // n,
                      "contexto_max_medio": g["contexto_max"] // n, "custo_medio": round(g["custo_usd"] / n, 2),
                      "custo_usd": round(g["custo_usd"], 2)})
    return sorted(saida, key=lambda g: -g["lidos"])


def fmt(n: int | float) -> str:
    """25,3 M · 153 mil · 950 — como o painel escreve tokens."""
    n = n or 0
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f} M".replace(".", ",")
    if n >= 1_000:
        return f"{round(n / 1_000)} mil"
    return str(int(n))
