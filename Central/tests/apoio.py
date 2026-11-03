"""Apoio dos testes: repositório git temporário e um agente falso que segue um roteiro."""
from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
import threading
import time
import warnings
from pathlib import Path

from central import config

warnings.filterwarnings("ignore", category=DeprecationWarning)

TODO_CRIATIVO = """# TODO

## Pendências

### Lendas

| Item | Arquivo | Prioridade | Status |
|------|---------|-----------|--------|
| Ficha: Bruxas | [`c.md`](c.md) | Alta | ❌ Não iniciado |
| Ficha: Dragão | [`c.md`](c.md) | Média | ❌ Não iniciado |

### Ideias

| Item | Arquivo | Prioridade | Status |
|------|---------|-----------|--------|
| Primeiras ideias | [`p.md`](p.md) | Baixa | ❌ Não iniciado |

---

## Concluído

| Item | Data |
|------|------|
| Bootstrap | 2026-04-25 |
"""


def git(cwd, *args):
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, encoding="utf-8",
                          env=config.ambiente())


def repo_temporario() -> Path:
    raiz = Path(tempfile.mkdtemp(prefix="central-teste-"))
    git(raiz, "init", "-q", "-b", "main")
    git(raiz, "config", "user.email", "teste@central")
    git(raiz, "config", "user.name", "Teste")
    git(raiz, "config", "core.autocrlf", "false")
    (raiz / "Design/Criativo").mkdir(parents=True)
    (raiz / "Design/Criativo/TODO.md").write_text(TODO_CRIATIVO, encoding="utf-8", newline="\n")
    (raiz / "LEIA.md").write_text("projeto de teste\n", encoding="utf-8")
    git(raiz, "add", "-A")
    git(raiz, "commit", "-q", "-m", "inicial")
    return raiz


def apagar(raiz: Path) -> None:
    shutil.rmtree(raiz, ignore_errors=True)


def esperar(condicao, limite: float = 20.0) -> bool:
    fim = time.time() + limite
    while time.time() < fim:
        if condicao():
            return True
        time.sleep(0.05)
    return False


BLOCO = '\n\n```resultado\n{"itens": [{"titulo": "x", "situacao": "feito", "resumo": "ok"}], "commit": "docs: teste"}\n```'


class SessaoFalsa:
    """Mesmo contrato do SessaoAgente; cada `enviar` executa o próximo passo do roteiro."""
    roteiro: list = []
    criadas: list = []

    def __init__(self, cwd, agente, contrato, nome, ao_evento, retomar=None, exe=None):
        self.cwd, self.agente, self.contrato, self.nome = Path(cwd), agente, contrato, nome
        self.ao_evento, self.retomar = ao_evento, retomar
        self._vivo = False
        self.recebidas: list[str] = []
        self.respostas: list[tuple] = []
        self.passos = list(SessaoFalsa.roteiro)
        self.ao_permitir = None
        SessaoFalsa.criadas.append(self)

    def iniciar(self):
        self._vivo = True
        self.ao_evento({"type": "system", "subtype": "init", "session_id": "sessao-falsa", "cwd": str(self.cwd)})

    @property
    def vivo(self):
        return self._vivo

    def texto(self, t):
        self.ao_evento({"type": "assistant", "message": {"content": [{"type": "text", "text": t}]}})

    def fim(self):
        self.ao_evento({"type": "result", "subtype": "success", "duration_ms": 10})

    def enviar(self, texto):
        self.recebidas.append(texto)
        passo = self.passos.pop(0) if self.passos else (lambda s: (s.texto("nada a fazer" + BLOCO), s.fim()))
        threading.Thread(target=passo, args=(self,), daemon=True).start()

    def responder_permissao(self, request_id, permitir, entrada=None, mensagem=""):
        self.respostas.append((request_id, permitir))
        if self.ao_permitir:
            acao, self.ao_permitir = self.ao_permitir, None
            threading.Thread(target=acao, args=(self, permitir), daemon=True).start()

    def interromper(self):
        self.fim()

    def encerrar(self, espera=0):
        if self._vivo:
            self._vivo = False
            self.ao_evento({"type": "_fim", "codigo": 0, "stderr": []})


def pedir_permissao(sessao, request_id="p1", comando="py script.py --x"):
    sessao.ao_evento({"type": "control_request", "request_id": request_id,
                      "request": {"subtype": "can_use_tool", "tool_name": "Bash",
                                  "input": {"command": comando}, "description": "rodar"}})


PY = sys.executable
