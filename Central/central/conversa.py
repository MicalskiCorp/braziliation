"""Eventos do stream-json → entradas do chat; e o bloco de resultado que fecha uma execução."""
from __future__ import annotations

import json
import re

RESULTADO = re.compile(r"```resultado\s*\n(.*?)```", re.DOTALL)

CONTRATO = """\
Você está rodando dentro da Central do Braziliation (ADR-012) — execução {id}, fila «{fila}».
O responsável acompanha pelo chat da Central e valida tudo antes do commit.

1. Trabalhe só nos itens pedidos. Siga o seu Passo 0 e o seu Passo Final, as skills e as regras
   de sempre (inclusive a baixa no TODO e o handoff para a camada seguinte, quando couber).
2. Precisou de decisão, informação ou aprovação do responsável? Pergunte em texto claro e
   ENCERRE o turno — ele responde pelo chat. A ferramenta AskUserQuestion não existe aqui.
3. Não faça commit nem push, e não mexa em branch, rebase, stash ou worktree. A Central mostra o
   diff ao responsável; o commit sai da validação e o push é sempre manual.
4. Quando quiser mostrar uma imagem (concept art, folha de miniaturas), cite o caminho do arquivo
   relativo à raiz do projeto — a Central exibe a imagem no chat.
5. Quando terminar TODOS os itens — ou não houver mais nada a fazer sem o responsável —, encerre
   a mensagem final com este bloco, e só então:

```resultado
{{"itens": [{{"titulo": "…", "situacao": "feito | precisa-decisao | bloqueado", "resumo": "…"}}],
 "commit": "tipo(escopo): mensagem no padrão do projeto, sem acento, com corpo e Co-Authored-By"}}
```

Sem esse bloco a Central entende que você está esperando o responsável.
"""


def resumo_ferramenta(nome: str, entrada: dict) -> str:
    entrada = entrada or {}
    for chave in ("command", "file_path", "notebook_path", "path", "pattern", "skill", "query", "url",
                  "description", "prompt"):
        if entrada.get(chave):
            valor = str(entrada[chave])
            return valor if len(valor) <= 240 else valor[:240] + "…"
    texto = json.dumps(entrada, ensure_ascii=False)
    return texto if len(texto) <= 240 else texto[:240] + "…"


def _texto_resultado(conteudo) -> str:
    if isinstance(conteudo, str):
        return conteudo
    if isinstance(conteudo, list):
        return " ".join(c.get("text", "") for c in conteudo if isinstance(c, dict))
    return str(conteudo)


def normalizar(ev: dict) -> list[dict]:
    """Um evento bruto vira zero ou mais entradas de chat."""
    tipo = ev.get("type")
    if tipo == "assistant":
        saida = []
        for bloco in ev.get("message", {}).get("content", []):
            if bloco.get("type") == "text" and bloco.get("text", "").strip():
                saida.append({"tipo": "agente", "texto": bloco["text"]})
            elif bloco.get("type") == "tool_use":
                saida.append({"tipo": "ferramenta", "nome": bloco.get("name", "?"),
                              "resumo": resumo_ferramenta(bloco.get("name", ""), bloco.get("input", {}))})
        return saida
    if tipo == "user":
        saida = []
        conteudo = ev.get("message", {}).get("content", [])
        for bloco in conteudo if isinstance(conteudo, list) else []:
            if isinstance(bloco, dict) and bloco.get("type") == "tool_result" and bloco.get("is_error"):
                texto = _texto_resultado(bloco.get("content", ""))
                saida.append({"tipo": "erro_ferramenta", "texto": texto[:600]})
        return saida
    if tipo == "control_request" and ev.get("request", {}).get("subtype") == "can_use_tool":
        req = ev["request"]
        return [{"tipo": "permissao", "request_id": ev.get("request_id", ""), "ferramenta": req.get("tool_name", "?"),
                 "resumo": resumo_ferramenta(req.get("tool_name", ""), req.get("input", {})),
                 "descricao": req.get("description", ""), "entrada": req.get("input", {})}]
    if tipo == "result":
        return [{"tipo": "fim_turno", "erro": ev.get("is_error", False) or ev.get("subtype") != "success",
                 "duracao_s": round((ev.get("duration_ms") or 0) / 1000)}]
    if tipo == "system" and ev.get("subtype") == "init":
        return [{"tipo": "nota", "texto": f"Sessão do agente aberta em {ev.get('cwd', '?')}."}]
    return []


def extrair_resultado(texto: str) -> dict | None:
    blocos = RESULTADO.findall(texto or "")
    if not blocos:
        return None
    try:
        dado = json.loads(blocos[-1])
    except ValueError:
        return {"itens": [], "commit": "", "erro": "bloco de resultado com JSON inválido", "bruto": blocos[-1]}
    if not isinstance(dado, dict):
        return None
    dado.setdefault("itens", [])
    dado.setdefault("commit", "")
    return dado


def sem_bloco(texto: str) -> str:
    """O texto do agente sem o bloco de resultado (ele aparece formatado na validação)."""
    return RESULTADO.sub("", texto or "").rstrip()
